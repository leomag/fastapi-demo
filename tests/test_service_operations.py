import asyncio
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.enum import CurrencyEnum, OperationType
from app.schemas import OperationRequest, TransferCreateSchema
from app.service import operations as operations_service


def test_add_income_404_if_wallet_missing(monkeypatch, fake_db):
    user = SimpleNamespace(id=1)
    payload = OperationRequest(wallet_name="w", amount=Decimal("1"), description="x")
    monkeypatch.setattr(operations_service.wallets_repository, "is_wallet_exists", lambda db, uid, name: False)

    with pytest.raises(HTTPException) as e:
        operations_service.add_income(fake_db, user, payload)

    assert e.value.status_code == 404
    assert "not found" in e.value.detail
    assert fake_db.commits == 0


def test_add_income_creates_operation_and_commits(monkeypatch, fake_db):
    user = SimpleNamespace(id=1)
    payload = OperationRequest(wallet_name="w", amount=Decimal("5"), description="salary")

    monkeypatch.setattr(operations_service.wallets_repository, "is_wallet_exists", lambda db, uid, name: True)
    wallet = SimpleNamespace(id=10, currency=CurrencyEnum.USD)
    monkeypatch.setattr(operations_service.wallets_repository, "add_income", lambda db, uid, name, amount: wallet)

    created_at = datetime(2020, 1, 1)
    op = SimpleNamespace(
        id=99,
        wallet_id=10,
        type=OperationType.INCOME,
        amount=Decimal("5"),
        currency=CurrencyEnum.USD,
        category="salary",
        subcategory=None,
        created_at=created_at,
    )

    def _create_operation(**kwargs):
        assert kwargs["wallet_id"] == 10
        assert kwargs["type"] == OperationType.INCOME
        assert kwargs["amount"] == Decimal("5")
        assert kwargs["currency"] == CurrencyEnum.USD
        assert kwargs["category"] == "salary"
        return op

    monkeypatch.setattr(operations_service.operations_repository, "create_operation", _create_operation)

    result = operations_service.add_income(fake_db, user, payload)

    assert result.id == 99
    assert result.type == OperationType.INCOME
    assert fake_db.commits == 1


def test_add_expense_400_if_insufficient_funds(monkeypatch, fake_db):
    user = SimpleNamespace(id=1)
    payload = OperationRequest(wallet_name="w", amount=Decimal("10"), description="x")

    monkeypatch.setattr(operations_service.wallets_repository, "is_wallet_exists", lambda db, uid, name: True)
    monkeypatch.setattr(
        operations_service.wallets_repository,
        "get_wallet_balance_by_name",
        lambda db, uid, name: SimpleNamespace(balance=Decimal("3")),
    )

    with pytest.raises(HTTPException) as e:
        operations_service.add_expense(fake_db, user, payload)

    assert e.value.status_code == 400
    assert "Insufficient funds" in e.value.detail
    assert fake_db.commits == 0


def test_get_operations_list_validates_wallet_id(monkeypatch, fake_db):
    user = SimpleNamespace(id=1)
    monkeypatch.setattr(operations_service.wallets_repository, "get_wallet_by_id", lambda db, uid, wid: None)

    with pytest.raises(HTTPException) as e:
        operations_service.get_operations_list(fake_db, user, wallet_id=123)

    assert e.value.status_code == 404


def test_transfer_between_wallets_converts_currency(monkeypatch, fake_db):
    from_wallet = SimpleNamespace(id=1, balance=Decimal("100"), currency=CurrencyEnum.USD)
    to_wallet = SimpleNamespace(id=2, balance=Decimal("0"), currency=CurrencyEnum.RUB)
    monkeypatch.setattr(
        operations_service.wallets_repository,
        "get_wallet_by_id",
        lambda db, uid, wid: from_wallet if wid == 1 else to_wallet if wid == 2 else None,
    )

    async def _rate(base, target):
        assert base == CurrencyEnum.USD
        assert target == CurrencyEnum.RUB
        return Decimal("90")

    monkeypatch.setattr(operations_service, "get_exchange_rate", _rate)

    created_at = datetime(2020, 1, 1)
    created_op = SimpleNamespace(
        id=7,
        wallet_id=1,
        type=OperationType.TRANSFER,
        amount=Decimal("180"),  # 2 * 90
        currency=CurrencyEnum.RUB,
        category="перевод",
        subcategory=None,
        created_at=created_at,
    )
    monkeypatch.setattr(operations_service.operations_repository, "create_operation", lambda **kwargs: created_op)

    payload = TransferCreateSchema(from_wallet_id=1, to_wallet_id=2, amount=Decimal("2"))
    result = asyncio.run(operations_service.transfer_beetween_wallets(fake_db, user_id=1, payload=payload))

    assert from_wallet.balance == Decimal("98")
    assert to_wallet.balance == Decimal("180")
    assert result.id == 7
    assert fake_db.commits == 1
