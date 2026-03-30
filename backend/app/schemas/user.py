from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserCreate(BaseModel):
    """Datos necesarios para registrar un usuario nuevo."""
    email: EmailStr
    password: str
    full_name: str
    currency: str = "USD"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La password debe tener al menos 8 caracteres")
        return v

    @field_validator("currency")
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        return v.upper()


class UserRead(BaseModel):
    """Datos que devuelve la API sobre un usuario."""
    id: str
    email: str
    full_name: str
    currency: str
    is_active: bool
    created_at: datetime

    # model_config le dice a Pydantic que puede leer
    # atributos de objetos SQLAlchemy (no solo dicts)
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Datos para hacer login."""
    email: EmailStr
    password: str