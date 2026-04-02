"""Точка входа для gunicorn: объект ``app``."""

from vpf11.app_factory import create_app

app = create_app()
