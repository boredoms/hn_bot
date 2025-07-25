import asyncio
import html
import logging
import logging.handlers

import hn_bot.apis.async_apis.hn_api as hn_api
import hn_bot.apis.async_apis.tg_api as tg_api
import hn_bot.persistence as p
from hn_bot.bot_config import BotConfig

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(
            "data/hn_bot.log", maxBytes=10_000_000, backupCount=3
        )
    ],
)

logger = logging.getLogger(__name__)


def format_post(item: dict[str, str | int], post_template: str) -> str:
    assert isinstance(item["title"], str)

    return post_template.format(
        html.escape(item["title"]), item["url"], item["score"], item["descendants"]
    )


async def fetch_post(id: str, config: BotConfig) -> dict[str, str | int] | None:
    logger.info(f"Fetching post {id}")

    if item := await hn_api.get_item(id, config.async_http_client):
        if "url" not in item:
            logger.info(f"item {id} has no url")
            return None

        return item
    else:
        return None


async def make_or_edit_post(post: dict[str, str | int], config: BotConfig):
    assert isinstance(post["id"], int)

    message_body = format_post(post, config.post_template)

    # either none or tuple (hn_id, url, title, date, score, comments, tg_id)
    if post_data := p.get_post(post["id"], config.db_cursor):
        # check if there is a difference to the current text in the channel
        score = post_data[4]
        comments = post_data[5]

        if post["score"] == score and post["descendants"] == comments:
            return

        _ = await tg_api.edit_message_text(
            config.tg_api_token,
            config.tg_channel_name,
            str(post_data[6]),
            message_body,
            config.async_http_client,
            config.tg_api_rate_limiter,
        )

        p.update_post(post, config.db_cursor)

    else:
        if response := await tg_api.send_message(
            config.tg_api_token,
            config.tg_channel_name,
            message_body,
            config.async_http_client,
            config.tg_api_rate_limiter,
        ):
            if "result" not in response:
                logger.warning(
                    f"unexpected response object for {post_data}: {response}"
                )
                return
            tg_id = response["result"]["message_id"]

            post["tg_id"] = tg_id

            p.insert_post(post, config.db_cursor)


async def main(config: BotConfig):
    logging.info("starting hn_bot")

    while True:
        logging.info("fetching top stories")
        if top_posts := await hn_api.get_topstories(config.async_http_client):
            posts = await asyncio.gather(*[fetch_post(id, config) for id in top_posts])

            for post in [x for x in posts if x is not None and x["type"] == "story"]:
                assert isinstance(post["score"], int)
                assert isinstance(post["descendants"], int)

                if (
                    post["score"] < config.hn_min_karma
                    or post["descendants"] < config.hn_min_comments
                ):
                    continue

                _ = asyncio.create_task(make_or_edit_post(post, config))

            p.commit(config.db_connection)
            await asyncio.sleep(config.sleep_time)

        # if there is a network error we want to retry later
        else:
            logging.error("fetching posts did not work, retrying later")
            await asyncio.sleep(config.sleep_time)

            continue


def run_bot():
    config = BotConfig.read_from_file("pyproject.toml", "config/secrets.toml")

    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        logging.info("committing unsaved changes to DB")

        # clean up the database
        p.commit(config.db_connection)

        config.db_cursor.close()
        config.db_connection.close()
