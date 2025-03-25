import hn_bot.apis.async_apis.hn_api as hn_api
import hn_bot.apis.async_apis.tg_api as tg_api
import hn_bot.persistence as p
from hn_bot.bot_config import BotConfig

import asyncio


def format_post(item) -> str:
    return BotConfig.get().post_template.format(
        item["title"], item["url"], item["score"], item["descendants"]
    )


async def fetch_post(id: str) -> dict | None:
    item = await hn_api.get_item(id)

    if item is None:
        print(f"fetching the post failed (id={id})")
        return None

    if "url" not in item:
        print(f"post {id} does not have a URL")
        return None

    return item


async def make_or_edit_post(post: dict):
    config = BotConfig.get()

    # either none or tuple (hn_id, url, title, date, score, comments, tg_id)
    post_data = p.get_post(post["id"])

    if post_data is not None:
        # check if there is a difference to the current text in the channel
        score = post_data[4]
        comments = post_data[5]

        if post["score"] == score and post["descendants"] == comments:
            return

    message_body = format_post(post)

    await config.tg_api_rate_limiter.wait()

    if post_data is None:
        response = await tg_api.send_message(
            config.tg_api_token, "@distraction_free_hacker_news", message_body
        )
        tg_id = response["result"]["message_id"]
        post["tg_id"] = tg_id

        p.insert_post(post)
    else:
        await tg_api.edit_message_text(
            config.tg_api_token,
            "@distraction_free_hacker_news",
            str(post_data[6]),
            message_body,
        )
        p.update_post(post)


async def main():
    print("Hello from hn-bot!")

    while True:
        top_posts = await hn_api.get_topstories()

        if top_posts is None:
            print("Error getting top posts")
            return

        top_posts = top_posts[:10]

        posts = await asyncio.gather(*[fetch_post(id) for id in top_posts])

        # insert the posts that are going to be made
        BotConfig.get().db_connection.commit()

        for post in posts:
            if post is None:
                continue

            if (
                post["score"] < BotConfig.get().hn_min_karma
                or post["descendants"] < BotConfig.get().hn_min_comments
            ):
                continue

            asyncio.create_task(make_or_edit_post(post))

        p.commit()
        await asyncio.sleep(BotConfig.get().sleep_time)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Committing unsaved changes to DB")
        p.commit()
