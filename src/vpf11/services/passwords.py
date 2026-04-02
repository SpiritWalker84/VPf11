"""Безопасное хеширование паролей (bcrypt)."""

from __future__ import annotations

import bcrypt


class PasswordHasher:
    """Обёртка над bcrypt: единая точка для хеширования и проверки."""

    def hash_password(self, password: str) -> bytes:
        """
        Возвращает bcrypt-хеш пароля.

        Args:
            password: Пароль в открытом виде (не логировать).
        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify(self, password: str, password_hash: bytes) -> bool:
        """Проверяет пароль против сохранённого хеша."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)
