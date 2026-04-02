"""Загрузка настроек из окружения (без секретов в коде)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Настройки рантайма сервиса."""

    database_path: str
    flask_secret_key: str


def load_settings() -> Settings:
    """
    Читает переменные окружения.

    Returns:
        Объект настроек с путём к SQLite и секретным ключом Flask.
    """
    database_path = os.environ.get("DATABASE_PATH", "/data/app.db")
    secret = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-in-production")
    return Settings(database_path=database_path, flask_secret_key=secret)
