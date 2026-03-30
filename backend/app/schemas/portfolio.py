from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    benchmark_ticker: str = "^GSPC"


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    benchmark_ticker: Optional[str] = None


class PortfolioRead(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    benchmark_ticker: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}