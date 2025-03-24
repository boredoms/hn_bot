import apis.hn_api as hn_api
import apis.tg_api as tg_api
import persistence as p

import time
import asyncio

from bot_config import BotConfig

from dataclasses import dataclass
from typing import AsyncIterator, ClassVar

from queue import Queue

post_queue = Queue()


def format_post(item) -> str:
    template = "<b>{}</b>\n\n<i>Link: {}</i>\n\nKarma: {}, Comments: {}"

    return template.format(
        item["title"], item["url"], item["score"], item["descendants"]
    )


async def fetch_post(id: str) -> dict | None:
    item = hn_api.get_item(id)

    if item is None:
        print(f"fetching the post failed (id={id})")
        return None

    if "url" not in item:
        print(f"post {id} does not have a URL")
        return None

    return item


async def main():
    print("Hello from hn-bot!")
    config = BotConfig.get()

    while True:
        top_posts = hn_api.get_topstories()

        if top_posts is None:
            print("Error getting top posts")
            return

        top_posts = top_posts[:3]

        posts = await asyncio.gather(*[fetch_post(id) for id in top_posts])

        # insert the posts that are going to be made
        BotConfig.get().db_connection.commit()

        for post in posts:
            if post is None:
                continue

            if not p.already_posted(post["id"]):
                message_body = format_post(post)

                response = tg_api.send_message(
                    config.token, "@distraction_free_hacker_news", message_body
                )

                tg_id = response["result"]["message_id"]
                post["tg_id"] = tg_id

                p.insert_post(post)
            else:
                p.update_post(post)

            time.sleep(3)

        p.commit()
        time.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
