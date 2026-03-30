from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioRead

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])


@router.get("", response_model=List[PortfolioRead])
def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve todos los portfolios del usuario autenticado."""
    return db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).all()


@router.post("", response_model=PortfolioRead, status_code=201)
def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un nuevo portfolio para el usuario autenticado."""
    portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio_data.name,
        description=portfolio_data.description,
        benchmark_ticker=portfolio_data.benchmark_ticker,
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioRead)
def get_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve un portfolio específico verificando que pertenece al usuario."""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id,
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio no encontrado",
        )
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioRead)
def update_portfolio(
    portfolio_id: str,
    portfolio_data: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un portfolio existente."""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id,
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio no encontrado",
        )

    # Actualiza solo los campos que vienen en la request
    # model_dump(exclude_unset=True) devuelve solo los campos
    # que el usuario envió, ignorando los que no mandó
    update_data = portfolio_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)

    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}", status_code=204)
def delete_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un portfolio y todas sus posiciones (CASCADE)."""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id,
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio no encontrado",
        )

    db.delete(portfolio)
    db.commit()