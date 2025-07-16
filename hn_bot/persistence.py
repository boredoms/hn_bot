import sqlite3


def connect() -> sqlite3.Connection:
    return sqlite3.connect("data/hn_bot.db")


# TODO: handle the return values
def create_database(connection: sqlite3.Connection) -> None:
    _ = connection.cursor().execute(
        "CREATE TABLE IF NOT EXISTS posts(hn_id INTEGER PRIMARY KEY, url TEXT, title TEXT, date INTEGER, score INTEGER, comments INTEGER, tg_id INTEGER)"
    )


def insert_post(item: dict[str, str | int], cursor: sqlite3.Cursor) -> None:
    _ = cursor.execute(
        "INSERT INTO posts VALUES(:id, :url, :title, :time, :score, :descendants, :tg_id)",
        item,
    )


def update_post(item: dict[str, str | int], cursor: sqlite3.Cursor) -> None:
    _ = cursor.execute(
        "UPDATE posts SET score = :score, comments = :descendants WHERE hn_id = :id",
        item,
    )


def get_post_karma(item: dict[str, str | int], cursor: sqlite3.Cursor) -> int:
    res = cursor.execute("SELECT score FROM posts WHERE hn_id = :id", item).fetchone()

    return res[0]


def get_post_comments(item: dict[str, str | int], cursor: sqlite3.Cursor) -> int:
    res = cursor.execute(
        "SELECT comments FROM posts WHERE hn_id = :id", item
    ).fetchone()

    return res[0]


def get_post_scores(
    item: dict[str, str | int], cursor: sqlite3.Cursor
) -> tuple[int, int]:
    res = cursor.execute(
        "SELECT score, comments FROM posts WHERE hn_id = :id", item
    ).fetchone()

    return res


# check if the post and its corresponding id already exists in the DB
def get_postid(id: int, cursor: sqlite3.Cursor) -> int | None:
    res = cursor.execute("SELECT tg_id FROM posts WHERE hn_id = ?", (id,)).fetchone()

    if res is None:
        return None
    else:
        return res[0]


def get_post(
    id: int, cursor: sqlite3.Cursor
) -> tuple[int, str, str, int, int, int, int] | None:
    res = cursor.execute("SELECT * from posts WHERE hn_id = ?", (id,)).fetchone()

    return res


def commit(db_connection: sqlite3.Connection):
    db_connection.commit()
