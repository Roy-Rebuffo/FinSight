from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.position import Position, Transaction
from app.schemas.position import (
    PositionCreate, PositionRead,
    TransactionCreate, TransactionRead
)

router = APIRouter(prefix="/api/portfolios", tags=["positions"])


def get_portfolio_or_404(
    portfolio_id: str,
    user_id: str,
    db: Session
) -> Portfolio:
    """Helper que busca un portfolio y lanza 404 si no existe."""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id,
    ).first()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio no encontrado",
        )
    return portfolio


@router.get("/{portfolio_id}/positions", response_model=List[PositionRead])
def get_positions(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve todas las posiciones de un portfolio."""
    get_portfolio_or_404(portfolio_id, current_user.id, db)
    return db.query(Position).filter(
        Position.portfolio_id == portfolio_id
    ).all()


@router.post("/{portfolio_id}/positions", response_model=PositionRead, status_code=201)
def create_position(
    portfolio_id: str,
    position_data: PositionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Añade una nueva posición al portfolio."""
    get_portfolio_or_404(portfolio_id, current_user.id, db)

    # Verificar que no existe ya una posición con ese ticker
    existing = db.query(Position).filter(
        Position.portfolio_id == portfolio_id,
        Position.ticker == position_data.ticker,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una posición para {position_data.ticker}",
        )

    position = Position(
        portfolio_id=portfolio_id,
        ticker=position_data.ticker,
        asset_type=position_data.asset_type,
        quantity=position_data.quantity,
        avg_cost=position_data.avg_cost,
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


@router.post(
    "/{portfolio_id}/positions/{position_id}/transactions",
    response_model=TransactionRead,
    status_code=201,
)
def create_transaction(
    portfolio_id: str,
    position_id: str,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registra una transacción (compra/venta) y actualiza
    la cantidad y el precio promedio de la posición automáticamente.
    """
    get_portfolio_or_404(portfolio_id, current_user.id, db)

    position = db.query(Position).filter(
        Position.id == position_id,
        Position.portfolio_id == portfolio_id,
    ).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posición no encontrada",
        )

    total_value = transaction_data.quantity * transaction_data.price

    transaction = Transaction(
        position_id=position_id,
        type=transaction_data.type,
        quantity=transaction_data.quantity,
        price=transaction_data.price,
        total_value=total_value,
        notes=transaction_data.notes,
        executed_at=transaction_data.executed_at,
    )

    # Actualizar cantidad y precio promedio según tipo de operación
    if transaction_data.type == "buy":
        # Precio promedio ponderado:
        # (qty_actual * avg_actual + qty_nueva * precio_nuevo) / qty_total
        total_qty = position.quantity + transaction_data.quantity
        position.avg_cost = (
            (position.quantity * position.avg_cost) +
            (transaction_data.quantity * transaction_data.price)
        ) / total_qty
        position.quantity = total_qty
    else:  # sell
        if transaction_data.quantity > position.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes vender más cantidad de la que tienes",
            )
        position.quantity -= transaction_data.quantity

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction