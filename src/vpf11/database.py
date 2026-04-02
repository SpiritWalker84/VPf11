"""Инициализация схемы SQLite и фабрика соединений."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Generator


def init_schema(conn: sqlite3.Connection) -> None:
    """
    Создаёт таблицы при отсутствии.

    Args:
        conn: Открытое соединение с БД.
    """
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '[]'
        );
        CREATE TABLE IF NOT EXISTS user_credentials (
            user_id INTEGER PRIMARY KEY,
            password_hash BLOB NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()


class Database:
    """
    Обёртка над путём к БД: соединение на запрос через контекстный менеджер.

    Не использует глобальное соединение — каждый with connect() получает своё.
    """

    def __init__(self, path: str) -> None:
        self._path = path

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
