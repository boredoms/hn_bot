from dataclasses import dataclass
import sqlite3
from typing import ClassVar
import persistence as p
from rate_limiter import RateLimiter
import httpx


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


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

    @staticmethod
    def get():
        if BotConfig.instance is None:
            connection = p.connect()
            cursor = connection.cursor()

            BotConfig.instance = BotConfig(
                token=read_token(),
                post_template="",
                tg_api_rate_limiter=RateLimiter(1, 3000),
                db_connection=connection,
                db_cursor=cursor,
                async_http_client=httpx.AsyncClient(),
            )

            # when initializing the config instance, we want to create the table if it does not exist
            p.create_database(BotConfig.instance.db_connection)

        return BotConfig.instance
