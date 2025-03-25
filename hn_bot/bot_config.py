from dataclasses import dataclass
import sqlite3
from typing import ClassVar
import hn_bot
from hn_bot.rate_limiter import RateLimiter
import httpx
import tomllib


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
    tg_api_token: str
    tg_channel_name: str
    tg_api_rate_limiter: RateLimiter
    post_template: str
    db_connection: sqlite3.Connection
    db_cursor: sqlite3.Cursor
    async_http_client: httpx.AsyncClient

    instance: ClassVar = None
    token_path: ClassVar[str] = "bot-token"

    sleep_time: int

    hn_min_karma: int
    hn_min_comments: int

    @staticmethod
    def get():
        if BotConfig.instance is None:
            config = None
            secrets = None

            with open("pyproject.toml", "rb") as f:
                pyproject = tomllib.load(f)
                config = pyproject["hn_bot"]

            with open("secrets.toml", "rb") as f:
                secrets = tomllib.load(f)

            connection = hn_bot.persistence.connect()
            cursor = connection.cursor()

            BotConfig.instance = BotConfig(
                tg_api_token=secrets["tg_api_token"],
                tg_channel_name=config["tg_channel_name"],
                tg_api_rate_limiter=RateLimiter(1, config["tg_api_rate"]),
                post_template=config["post_template"],
                db_connection=connection,
                db_cursor=cursor,
                async_http_client=httpx.AsyncClient(),
                sleep_time=config["sleep_time"],
                hn_min_karma=config["hn_min_karma"],
                hn_min_comments=config["hn_min_comments"],
            )

            # when initializing the config instance, we want to create the table if it does not exist
            hn_bot.persistence.create_database(BotConfig.instance.db_connection)

        return BotConfig.instance
