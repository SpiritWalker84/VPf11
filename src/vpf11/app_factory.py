"""Фабрика Flask-приложения."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask, abort, send_file

from vpf11.api.blueprint import create_api_blueprint
from vpf11.config import load_settings
from vpf11.database import Database, init_schema
from vpf11.repositories.users import UserRepository
from vpf11.services.active_users import ActiveUsersTracker
from vpf11.services.passwords import PasswordHasher


def create_app() -> Flask:
    """
    Собирает приложение: конфиг, схема БД, сервисы, маршруты.

    Returns:
        Настроенный экземпляр Flask.
    """
    settings = load_settings()
    os.makedirs(os.path.dirname(settings.database_path) or ".", exist_ok=True)

    db = Database(settings.database_path)
    with db.connect() as conn:
        init_schema(conn)

    user_repo = UserRepository(db)
    password_hasher = PasswordHasher()
    active = ActiveUsersTracker()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.flask_secret_key
    app.register_blueprint(
        create_api_blueprint(user_repo, password_hasher, active),
    )

    openapi_path = Path(__file__).resolve().parent.parent.parent / "openapi.yaml"

    @app.get("/openapi.yaml")
    def openapi_yaml() -> Any:
        """Отдаёт актуальную спецификацию из корня проекта (в образе — /app/openapi.yaml)."""
        if not openapi_path.is_file():
            abort(404)
        return send_file(openapi_path, mimetype="application/yaml")

    return app
