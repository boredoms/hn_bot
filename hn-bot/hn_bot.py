import apis.hn_api as hn_api
import apis.tg_api as tg_api

import time
import asyncio

from dataclasses import dataclass
from typing import AsyncIterator, ClassVar

from queue import Queue

post_queue = Queue()

RATE_LIMIT = 3


@dataclass(frozen=True)
class BotConfig:
    token: str
    post_template: str
    rate_limit: int

    instance: ClassVar = None
    token_path: ClassVar[str] = "bot-token"

    @staticmethod
    def get_instance():
        if BotConfig.instance is None:
            BotConfig.instance = BotConfig(
                token=read_token(), post_template="", rate_limit=RATE_LIMIT
            )

        return BotConfig.instance


def format_post(item) -> str:
    template = "<b>{}</b>\n\n<i>Link: {}</i>\n\nKarma: {}, Comments: {}"

    return template.format(
        item["title"], item["url"], item["score"], item["descendants"]
    )


async def fetch_post(id: str) -> tuple[int, str] | None:
    item = hn_api.get_item(id)

    if item is None:
        print(f"fetching the post failed (id={id})")
        return None

    if "url" not in item:
        print(f"post {id} does not have a URL")
        return None

    return (item["id"], format_post(item))


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


def write_seen(seen: dict):
    with open("cache/seen.txt", "w") as f:
        for item_id, post_id in seen.items():
            f.write(f"{item_id},{post_id}\n")


def read_seen():
    seen = {}

    try:
        f = open("cache/seen.txt")
    except:
        return seen
    else:
        with f:
            for line in f.readlines():
                item_id, post_id = line.split(",")
                seen[int(item_id)] = int(post_id)

    return seen


def create_post(id: str) -> str | None:
    item = hn_api.get_item(id)

    if item is None:
        return None

    if "url" not in item:
        print(f"Post {id} does not have url")
        return None

    if item["score"] < 30:
        print(f"Item {id} score too low")
        return None

    title = item["title"]
    url = item["url"]
    score = item["score"]
    descendants = item["descendants"]

    post_text = f"<b>{title}</b>\n\n<i>Link: {url}</i>\n\nKarma: {score}, Comments: {descendants}"

    return post_text


async def main():
    print("Hello from hn-bot!")
    config = BotConfig.get_instance()

    # check if a cache exists

    seen = read_seen()

    print(seen)

    while True:
        top_posts = hn_api.get_topstories()

        if top_posts is None:
            print("Error getting top posts")
            return

        top_posts = top_posts[:3]

        posts = await asyncio.gather(
            *[fetch_post(id) for id in top_posts if id not in seen]
        )

        for id, post in filter(lambda x: x is not None, posts):
            response = tg_api.send_message(
                config.token, "@distraction_free_hacker_news", post
            )

            post_id = response["result"]["message_id"]

            seen[id] = post_id

            time.sleep(3)

        write_seen(seen)
        time.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
