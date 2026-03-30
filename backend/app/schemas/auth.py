from pydantic import BaseModel


class Token(BaseModel):
    """Respuesta del endpoint de login."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos decodificados del JWT."""
    user_id: str