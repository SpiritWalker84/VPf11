"""Репозиторий пользователей: параметризованный SQL, явные контракты ответа."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from vpf11.database import Database


class UserRepository:
    """Операции чтения/записи пользователей и хешей паролей."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def add_user(self, name: str, tags: list[str] | None = None) -> int:
        """
        Добавляет пользователя.

        Args:
            name: Имя (непустая строка валидируется на уровне HTTP).
            tags: Список тегов; по умолчанию пустой список (без мутации дефолта).

        Returns:
            Числовой id вставленной строки.
        """
        if tags is None:
            tags = []
        tags_copy = list(tags)
        tags_copy.append("new")
        payload = json.dumps(tags_copy, ensure_ascii=False)
        with self._db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, tags) VALUES (?, ?)",
                (name, payload),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Возвращает пользователя по id или None, если не найден."""
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT id, name, tags FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_public(row)

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        """Возвращает пользователя по имени или None, если не найден."""
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT id, name, tags FROM users WHERE name = ?",
                (name,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_public(row)

    def set_password_hash(self, user_id: int, password_hash: bytes) -> None:
        """Сохраняет или обновляет bcrypt-хеш пароля для пользователя."""
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO user_credentials (user_id, password_hash)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET password_hash = excluded.password_hash
                """,
                (user_id, password_hash),
            )
            conn.commit()

    @staticmethod
    def _row_to_public(row: sqlite3.Row) -> dict[str, Any]:
        raw_tags = row["tags"]
        try:
            tags = json.loads(raw_tags)
        except (json.JSONDecodeError, TypeError):
            tags = raw_tags
        return {"id": int(row["id"]), "name": row["name"], "tags": tags}
