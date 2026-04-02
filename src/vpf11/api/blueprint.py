"""Маршруты REST API."""

from __future__ import annotations

import random
import threading
from http import HTTPStatus
from typing import Any

from flask import Blueprint, Response, jsonify, request

from vpf11.repositories.users import UserRepository
from vpf11.services.active_users import ActiveUsersTracker
from vpf11.services.passwords import PasswordHasher


def create_api_blueprint(
    users: UserRepository,
    passwords: PasswordHasher,
    active_tracker: ActiveUsersTracker,
) -> Blueprint:
    """
    Создаёт blueprint с замыканием на сервисы (явная композиция без глобалов).

    Совместимость с учебными путями: /adducer, /user/<uid>, /bg сохранены
    наряду с предпочтительными /api/* маршрутами.
    """
    bp = Blueprint("api", __name__)

    def _read_json_body() -> dict[str, Any] | None:
        if not request.is_json:
            return None
        return request.get_json(silent=True)

    @bp.post("/api/users")
    @bp.post("/adducer")
    def create_user() -> tuple[Response, int]:
        body = _read_json_body()
        if body is None:
            return jsonify({"error": "expected_json_object"}), HTTPStatus.BAD_REQUEST
        name = (body.get("name") or "").strip()
        if not name:
            return jsonify({"error": "name_required"}), HTTPStatus.BAD_REQUEST
        tags = body.get("tags")
        if tags is not None and not isinstance(tags, list):
            return jsonify({"error": "tags_must_be_list"}), HTTPStatus.BAD_REQUEST
        tag_list = [str(x) for x in tags] if isinstance(tags, list) else []
        user_id = users.add_user(name, tag_list)
        return jsonify({"id": user_id, "name": name}), HTTPStatus.CREATED

    @bp.get("/api/users/<int:user_id>")
    @bp.get("/user/<int:user_id>")
    def get_user(user_id: int) -> tuple[Response, int]:
        row = users.get_by_id(user_id)
        if row is None:
            return jsonify({"error": "not_found"}), HTTPStatus.NOT_FOUND
        return jsonify(row), HTTPStatus.OK

    @bp.get("/api/users/by-name")
    def get_user_by_name() -> tuple[Response, int]:
        name = (request.args.get("name") or "").strip()
        if not name:
            return jsonify({"error": "name_query_required"}), HTTPStatus.BAD_REQUEST
        row = users.get_by_name(name)
        if row is None:
            return jsonify({"error": "not_found"}), HTTPStatus.NOT_FOUND
        return jsonify(row), HTTPStatus.OK

    @bp.post("/api/users/<int:user_id>/credentials")
    def set_credentials(user_id: int) -> tuple[Response, int]:
        body = _read_json_body()
        if body is None:
            return jsonify({"error": "expected_json_object"}), HTTPStatus.BAD_REQUEST
        password = body.get("password")
        if not isinstance(password, str) or not password:
            return jsonify({"error": "password_required"}), HTTPStatus.BAD_REQUEST
        if users.get_by_id(user_id) is None:
            return jsonify({"error": "not_found"}), HTTPStatus.NOT_FOUND
        users.set_password_hash(user_id, passwords.hash_password(password))
        return jsonify({"ok": True}), HTTPStatus.OK

    @bp.post("/api/background-task")
    @bp.post("/bg")
    def background_demo() -> tuple[Response, int]:
        body = _read_json_body() or {}
        raw_id = body.get("id")
        try:
            uid = int(raw_id) if raw_id is not None else random.randint(1, 1000)
        except (TypeError, ValueError):
            uid = random.randint(1, 1000)

        def work() -> None:
            active_tracker.register(uid)

        threading.Thread(target=work, daemon=True).start()
        return jsonify(active_tracker.snapshot()), HTTPStatus.ACCEPTED

    @bp.get("/health")
    def health() -> tuple[Response, int]:
        return jsonify({"status": "ok"}), HTTPStatus.OK

    return bp
