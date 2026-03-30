from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional


class PositionCreate(BaseModel):
    ticker: str
    asset_type: str = "stock"
    quantity: Decimal
    avg_cost: Decimal

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper()

    @field_validator("asset_type")
    @classmethod
    def valid_asset_type(cls, v: str) -> str:
        valid = ["stock", "etf", "crypto", "bond"]
        if v not in valid:
            raise ValueError(f"asset_type debe ser uno de: {valid}")
        return v


class TransactionCreate(BaseModel):
    type: str
    quantity: Decimal
    price: Decimal
    notes: Optional[str] = None
    executed_at: datetime

    @field_validator("type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in ["buy", "sell"]:
            raise ValueError("type debe ser 'buy' o 'sell'")
        return v


class PositionRead(BaseModel):
    id: str
    portfolio_id: str
    ticker: str
    asset_type: str
    quantity: Decimal
    avg_cost: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionRead(BaseModel):
    id: str
    position_id: str
    type: str
    quantity: Decimal
    price: Decimal
    total_value: Decimal
    notes: Optional[str]
    executed_at: datetime

    model_config = {"from_attributes": True}