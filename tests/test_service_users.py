import pytest
from fastapi import HTTPException

from app.service import users as users_service


def test_create_user_raises_if_exists(monkeypatch, fake_db):
    monkeypatch.setattr(users_service.users_repository, "get_user", lambda db, login: object())

    with pytest.raises(HTTPException) as e:
        users_service.create_user(fake_db, "john")

    assert e.value.status_code == 400
    assert e.value.detail == "User already exists"
    assert fake_db.commits == 0


def test_create_user_commits_and_returns_schema(monkeypatch, fake_db):
    monkeypatch.setattr(users_service.users_repository, "get_user", lambda db, login: None)

    class _User:
        id = 123
        login = "john"

    monkeypatch.setattr(users_service.users_repository, "create_user", lambda db, login: _User())

    result = users_service.create_user(fake_db, "john")

    assert result.id == 123
    assert result.login == "john"
    assert fake_db.commits == 1
