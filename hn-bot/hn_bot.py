import apis.hn_api as hn_api
import apis.tg_api as tg_api

import time
import asyncio
import sqlite3

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
    db_connection: sqlite3.Connection

    instance: ClassVar = None
    token_path: ClassVar[str] = "bot-token"

    @staticmethod
    def get():
        if BotConfig.instance is None:
            BotConfig.instance = BotConfig(
                token=read_token(),
                post_template="",
                rate_limit=RATE_LIMIT,
                db_connection=sqlite3.connect("hn_bot.db"),
            )

            # when initializing the config instance, we want to craete the table if it does not exist, as connect might create a new table
            cursor = BotConfig.instance.db_connection.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS posts(hn_id INTEGER PRIMARY KEY, url TEXT, title TEXT, date INTEGER, score INTEGER, comments INTEGER, tg_id INTEGER)"
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

    insert_item(item)

    return (item["id"], format_post(item))


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


def insert_item(item):
    print(f"inserting {item}")

    cursor = BotConfig.get().db_connection.cursor()

    cursor.execute(
        "INSERT INTO posts VALUES(:id, :url, :title, :time, :score, :descendants, 0)",
        item,
    )


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


async def main():
    print("Hello from hn-bot!")
    config = BotConfig.get()

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
