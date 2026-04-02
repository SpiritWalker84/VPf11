"""Смоук-тесты HTTP API."""

from __future__ import annotations


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_create_and_get_user(client):
    r = client.post("/api/users", json={"name": "Alice", "tags": ["vip"]})
    assert r.status_code == 201
    body = r.get_json()
    uid = body["id"]

    g = client.get(f"/api/users/{uid}")
    assert g.status_code == 200
    data = g.get_json()
    assert data["name"] == "Alice"
    assert "vip" in data["tags"]
    assert "new" in data["tags"]


def test_get_unknown_user_404(client):
    r = client.get("/api/users/999999")
    assert r.status_code == 404


def test_lesson_route_alias_adducer(client):
    r = client.post("/adducer", json={"name": "Bob"})
    assert r.status_code == 201


def test_openapi_yaml_served(client):
    r = client.get("/openapi.yaml")
    assert r.status_code == 200
    assert b"openapi: 3.1.0" in r.data
    assert b"/api/users" in r.data
