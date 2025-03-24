import sqlite3
from bot_config import BotConfig


def connect():
    return sqlite3.connect("hn_bot.db")


def create_database(connection: sqlite3.Connection):
    connection.cursor().execute(
        "CREATE TABLE IF NOT EXISTS posts(hn_id INTEGER PRIMARY KEY, url TEXT, title TEXT, date INTEGER, score INTEGER, comments INTEGER, tg_id INTEGER)"
    )


def insert_post(item: dict):
    cursor = BotConfig.get().db_connection.cursor()

    cursor.execute(
        "INSERT INTO posts VALUES(:id, :url, :title, :time, :score, :descendants, :tg_id)",
        item,
    )


def update_post(item: dict):
    cursor = BotConfig.get().db_connection.cursor()

    cursor.execute(
        "UPDATE posts SET score = :score, comments = :comments WHERE hn_id = :id",
        item,
    )


# check if the post and its corresponding id already exists in the DB
def already_posted(id: int) -> bool:
    cursor = BotConfig.get().db_connection.cursor()
    res = cursor.execute("SELECT 1 FROM posts WHERE hn_id = ?", (id,)).fetchone()

    return res is not None


def commit():
    BotConfig.get().db_connection.commit()
