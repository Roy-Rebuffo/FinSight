from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# OAuth2PasswordBearer extrae el token del header Authorization: Bearer <token>
# tokenUrl indica dónde está el endpoint de login (para Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependencia que extrae y valida el usuario del JWT.

    Uso en cualquier endpoint protegido:
        @router.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user

    FastAPI ejecuta esta función automáticamente antes del endpoint.
    Si el token es inválido, devuelve 401 automáticamente.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return user