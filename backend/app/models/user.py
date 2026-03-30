from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class User(TimestampMixin, Base):
    """
    Tabla: users
    Representa un usuario registrado en FinSight.
    """
    __tablename__ = "users"

    # Mapped[str] le dice a SQLAlchemy Y a Python que este campo es un string.
    # Es la sintaxis moderna de SQLAlchemy 2.0 con type hints completos.
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,    # No puede haber dos usuarios con el mismo email
        nullable=False,
        index=True,     # Crea un índice en esta columna para búsquedas rápidas
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        # NUNCA guardamos la password en texto plano, siempre el hash bcrypt
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
        # ISO 4217: USD, EUR, GBP, etc.
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────
    # 'relationship' le dice a SQLAlchemy cómo navegar entre tablas.
    # Cuando accedes a user.portfolios, SQLAlchemy hace el JOIN automático.
    portfolios: Mapped[list["Portfolio"]] = relationship(
        "Portfolio",
        back_populates="user",
        # cascade: si borras un usuario, se borran sus portfolios también
        cascade="all, delete-orphan",
    )

    agent_sessions: Mapped[list["AgentSession"]] = relationship(
        "AgentSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"