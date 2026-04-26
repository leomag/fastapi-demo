from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum import OperationType
from app.models import User
from app.repository import operations as operations_repository
from app.repository import wallets as wallets_repository
from app.schemas import OperationRequest, OperationResponse, TransferCreateSchema
from app.service.exchange_service import get_exchange_rate


def add_income(db: Session, current_user: User, operation: OperationRequest) -> OperationResponse:
    if not wallets_repository.is_wallet_exists(db, current_user.id, operation.wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")
    wallet = wallets_repository.add_income(db, current_user.id, operation.wallet_name, operation.amount)
    operation = operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.INCOME,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.description,
        # subcategory = operation.subcategory,
        #  description = operation.description
    )
    db.commit()
    return OperationResponse.model_validate(operation)


def add_expense(db: Session, current_user: User, operation: OperationRequest) -> OperationResponse:
    if not wallets_repository.is_wallet_exists(db, current_user.id, operation.wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")
    wallet = wallets_repository.get_wallet_balance_by_name(db, current_user.id, operation.wallet_name)
    if wallet.balance < operation.amount:
        raise HTTPException(status_code=400, detail=f"Insufficient funds. Available: {wallet.balance}")
    wallet = wallets_repository.add_expense(db, current_user.id, operation.wallet_name, operation.amount)
    operation = operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.EXPENSE,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.description,
        # subcategory = operation.subcategory,
        # description = operation.description
    )
    db.commit()
    return OperationResponse.model_validate(operation)


def get_operations_list(
    db: Session,
    user: User,
    wallet_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[OperationResponse]:
    if wallet_id:
        wallet = wallets_repository.get_wallet_by_id(db, user.id, wallet_id)
        if not wallet:
            raise HTTPException(status_code=404, detail=f"Wallet '{wallet_id}' not found")

        wallets_ids = [wallet_id]
    else:
        wallets = wallets_repository.get_all_wallets(db, user.id)
        wallets_ids = [w.id for w in wallets]

    operations = operations_repository.get_operations_list(db, wallets_ids, date_from, date_to)

    result = []
    for operation in operations:
        result.append(OperationResponse.model_validate(operation))

    return result


async def transfer_beetween_wallets(db: Session, user_id: int, payload: TransferCreateSchema) -> OperationResponse:
    from_wallet = wallets_repository.get_wallet_by_id(db, user_id, payload.from_wallet_id)
    to_wallet = wallets_repository.get_wallet_by_id(db, user_id, payload.to_wallet_id)

    if not from_wallet or not to_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if from_wallet.balance < payload.amount:
        raise HTTPException(status_code=400, detail=f"Not enough money: {from_wallet.balance} {from_wallet.currency}")

    target_amount = payload.amount
    # exchange_rate = 1.0
    if from_wallet.currency != to_wallet.currency:
        exchange_rate = await get_exchange_rate(from_wallet.currency, to_wallet.currency)
        target_amount = payload.amount * exchange_rate

    # списываем со счета-отправителя
    from_wallet.balance = from_wallet.balance - payload.amount
    # зачисляем на счет-получателя
    to_wallet.balance = to_wallet.balance + target_amount

    operation = operations_repository.create_operation(
        db=db,
        wallet_id=from_wallet.id,
        type=OperationType.TRANSFER,
        amount=target_amount,
        currency=to_wallet.currency,
        category="перевод",
    )
    db.add(from_wallet)
    db.add(to_wallet)
    db.add(operation)
    db.commit()
    return OperationResponse.model_validate(operation)
