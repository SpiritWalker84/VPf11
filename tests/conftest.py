"""Фикстуры pytest."""

from __future__ import annotations

import os

import pytest

# Импорт приложения только после выставления DATABASE_PATH


@pytest.fixture()
def app(tmp_path):
    """Flask-приложение на временной SQLite."""
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_PATH"] = str(db_path)
    os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")

    from vpf11.app_factory import create_app

    application = create_app()
    application.config.update(TESTING=True)
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
