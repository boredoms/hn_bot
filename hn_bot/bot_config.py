import sqlite3
import tomllib
from dataclasses import dataclass
from typing import ClassVar

import httpx

import hn_bot.persistence
import hn_bot.rate_limiter


# class to hold the configuration of the entire bot
#
# since the entire app is single threaded async, this means we save a lot of time running buildup
# and teardown code for http clients and database connections
#
# this class is immutable, as we don't want to dynamically change the config
@dataclass(frozen=True)
class BotConfig:
    # config for the telegram API interaction
    tg_api_token: str
    tg_channel_name: str
    tg_api_rate_limiter: hn_bot.rate_limiter.RateLimiter
    post_template: str

    # config for the database interaction
    db_connection: sqlite3.Connection
    db_cursor: sqlite3.Cursor

    # the async html client to use
    async_http_client: httpx.AsyncClient

    # time between fetching new posts
    sleep_time: int

    # minimum amount of karma and posts of an item to be posted to the channel
    hn_min_karma: int
    hn_min_comments: int

    @staticmethod
    def read_from_file(config_path: str, secrets_path: str):
        config = None
        secrets = None

        with open(config_path, "rb") as f:
            pyproject = tomllib.load(f)
            config = pyproject["hn_bot"]

        with open(secrets_path, "rb") as f:
            secrets = tomllib.load(f)

        connection = hn_bot.persistence.connect()
        cursor = connection.cursor()

        hn_bot.persistence.create_database(connection)

        return BotConfig(
            tg_api_token=secrets["tg_api_token"],
            tg_channel_name=config["tg_channel_name"],
            tg_api_rate_limiter=hn_bot.rate_limiter.RateLimiter(
                1, config["tg_api_rate"]
            ),
            post_template=config["post_template"],
            db_connection=connection,
            db_cursor=cursor,
            async_http_client=httpx.AsyncClient(),
            sleep_time=config["sleep_time"],
            hn_min_karma=config["hn_min_karma"],
            hn_min_comments=config["hn_min_comments"],
        )
