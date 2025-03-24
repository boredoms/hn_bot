from dataclasses import dataclass
import sqlite3
from typing import AsyncIterator, ClassVar
import persistence as p

RATE_LIMIT = 3


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


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
                db_connection=p.connect(),
            )

            # when initializing the config instance, we want to create the table if it does not exist
            p.create_database(BotConfig.instance.db_connection)

        return BotConfig.instance
