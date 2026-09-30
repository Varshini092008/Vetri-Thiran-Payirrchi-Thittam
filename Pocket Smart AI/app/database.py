import os
import sqlite3
from contextlib import contextmanager

from .config import settings


def get_database_path() -> str:
    url = settings.database_url

    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "", 1)
    else:
        path = url

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    return path


@contextmanager
def get_db():
    connection = sqlite3.connect(
        get_database_path(),
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with get_db() as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner TEXT NOT NULL,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)