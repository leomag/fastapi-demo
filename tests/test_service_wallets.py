import asyncio
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.enum import CurrencyEnum
from app.schemas import CreateWalletRequest
from app.service import wallets as wallets_service


def test_create_wallet_raises_if_exists(monkeypatch, fake_db):
    current_user = SimpleNamespace(id=1)
    payload = CreateWalletRequest(name="main", initial_balance=Decimal("10"), currency=CurrencyEnum.RUB)

    monkeypatch.setattr(wallets_service.wallets_repository, "is_wallet_exists", lambda db, uid, name: True)

    with pytest.raises(HTTPException) as e:
        wallets_service.create_wallet(fake_db, current_user, payload)

    assert e.value.status_code == 400
    assert "already exists" in e.value.detail
    assert fake_db.commits == 0


def test_create_wallet_commits_and_returns_schema(monkeypatch, fake_db):
    current_user = SimpleNamespace(id=1)
    payload = CreateWalletRequest(name="main", initial_balance=Decimal("10"), currency=CurrencyEnum.USD)

    monkeypatch.setattr(wallets_service.wallets_repository, "is_wallet_exists", lambda db, uid, name: False)

    created = SimpleNamespace(id=10, name="main", balance=Decimal("10"), currency=CurrencyEnum.USD)
    monkeypatch.setattr(
        wallets_service.wallets_repository,
        "create_wallet",
        lambda db, uid, name, initial_balance, currency: created,
    )

    result = wallets_service.create_wallet(fake_db, current_user, payload)

    assert result.id == 10
    assert result.name == "main"
    assert result.balance == Decimal("10")
    assert result.currency == CurrencyEnum.USD
    assert fake_db.commits == 1


def test_get_all_wallets_maps_to_schemas(monkeypatch, fake_db):
    current_user = SimpleNamespace(id=1)
    wallets = [
        SimpleNamespace(id=1, name="w1", balance=Decimal("1"), currency=CurrencyEnum.RUB),
        SimpleNamespace(id=2, name="w2", balance=Decimal("2"), currency=CurrencyEnum.USD),
    ]
    monkeypatch.setattr(wallets_service.wallets_repository, "get_all_wallets", lambda db, uid: wallets)

    result = wallets_service.get_all_wallets(fake_db, current_user)

    assert [w.id for w in result] == [1, 2]
    assert [w.name for w in result] == ["w1", "w2"]


def test_get_total_balance_all_rub(monkeypatch, fake_db):
    current_user = SimpleNamespace(id=1)
    wallets = [
        SimpleNamespace(id=1, name="w1", balance=Decimal("100"), currency=CurrencyEnum.RUB),
        SimpleNamespace(id=2, name="w2", balance=Decimal("10"), currency=CurrencyEnum.RUB),
    ]
    monkeypatch.setattr(wallets_service.wallets_repository, "get_all_wallets", lambda db, uid: wallets)

    result = asyncio.run(wallets_service.get_total_balance(fake_db, current_user))

    assert result.total_balance == Decimal("110")


def test_get_total_balance_converts_non_rub(monkeypatch, fake_db):
    current_user = SimpleNamespace(id=1)
    wallets = [
        SimpleNamespace(id=1, name="rub", balance=Decimal("100"), currency=CurrencyEnum.RUB),
        SimpleNamespace(id=2, name="usd", balance=Decimal("2"), currency=CurrencyEnum.USD),
    ]
    monkeypatch.setattr(wallets_service.wallets_repository, "get_all_wallets", lambda db, uid: wallets)

    async def _rate(base, target):
        assert base == CurrencyEnum.USD
        assert target == CurrencyEnum.RUB
        return Decimal("90")

    monkeypatch.setattr(wallets_service.exchange_service, "get_exchange_rate", _rate)

    result = asyncio.run(wallets_service.get_total_balance(fake_db, current_user))

    assert result.total_balance == Decimal("280")
