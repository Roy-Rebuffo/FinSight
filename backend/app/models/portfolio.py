from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Portfolio(TimestampMixin, Base):
    """
    Tabla: portfolios
    Un usuario puede tener varios portfolios (ej: 'Jubilación', 'Trading').
    """
    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    # ForeignKey crea la relación en la base de datos.
    # "users.id" significa: esta columna apunta a la columna 'id' de la tabla 'users'
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
    )

    # Ticker del índice de referencia para comparar rendimiento
    # Ej: "^GSPC" (S&P 500), "^IBEX" (IBEX 35)
    benchmark_ticker: Mapped[str] = mapped_column(
        String(20),
        default="^GSPC",
        nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="portfolios",
    )

    positions: Mapped[list["Position"]] = relationship(
        "Position",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

    snapshots: Mapped[list["Snapshot"]] = relationship(
        "Snapshot",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Portfolio {self.name} (user={self.user_id})>"