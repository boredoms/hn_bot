from dataclasses import dataclass
import sqlite3
from typing import ClassVar
import hn_bot
from hn_bot.rate_limiter import RateLimiter
import httpx


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


# global singleton to hold the configuration of the entire bot
# making it a singleton ensures that we only have one active database connection/async_http_client
#
# since the entire app is single threaded async, this means we save a lot of time running buildup
# and teardown code for http clients and database connections
#
# this class is immutable, preventing the usual problem of entagling global state
@dataclass(frozen=True)
class BotConfig:
    token: str
    post_template: str
    tg_api_rate_limiter: RateLimiter
    db_connection: sqlite3.Connection
    db_cursor: sqlite3.Cursor
    async_http_client: httpx.AsyncClient

    instance: ClassVar = None
    token_path: ClassVar[str] = "bot-token"

    sleep_time: int

    @staticmethod
    def get():
        if BotConfig.instance is None:
            connection = hn_bot.persistence.connect()
            cursor = connection.cursor()

            BotConfig.instance = BotConfig(
                token=read_token(),
                post_template="",
                tg_api_rate_limiter=RateLimiter(1, 3),
                db_connection=connection,
                db_cursor=cursor,
                async_http_client=httpx.AsyncClient(),
                sleep_time=10,
            )

            # when initializing the config instance, we want to create the table if it does not exist
            hn_bot.persistence.create_database(BotConfig.instance.db_connection)

        return BotConfig.instance
