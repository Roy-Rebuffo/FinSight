from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Position(TimestampMixin, Base):
    """
    Tabla: positions
    Una posición es la tenencia de un activo concreto dentro de un portfolio.
    Ej: '10 acciones de AAPL en el portfolio Jubilación'
    """
    __tablename__ = "positions"

    # Restricción a nivel de base de datos: no puede haber dos posiciones
    # con el mismo ticker en el mismo portfolio
    __table_args__ = (
        UniqueConstraint("portfolio_id", "ticker", name="uq_portfolio_ticker"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )

    portfolio_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        # Ej: "AAPL", "MSFT", "BTC-USD"
    )

    # Tipo de activo para categorización
    asset_type: Mapped[str] = mapped_column(
        String(20),
        default="stock",
        nullable=False,
        # Valores posibles: "stock", "etf", "crypto", "bond"
    )

    # Numeric(precision, scale) para dinero: evita errores de punto flotante
    # precision=18: hasta 18 dígitos en total
    # scale=8: hasta 8 decimales (necesario para crypto)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 8),
        nullable=False,
    )

    # Precio promedio de compra (se recalcula con cada transacción)
    avg_cost: Mapped[Decimal] = mapped_column(
        Numeric(18, 8),
        nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="positions"
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="position",
        cascade="all, delete-orphan",
        # Ordena las transacciones por fecha al cargarlas
        order_by="Transaction.executed_at",
    )

    def __repr__(self) -> str:
        return f"<Position {self.ticker} qty={self.quantity}>"


class Transaction(TimestampMixin, Base):
    """
    Tabla: transactions
    Cada compra o venta de un activo queda registrada aquí.
    El historial completo permite recalcular el avg_cost en cualquier momento.
    """
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )

    position_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("positions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "buy" o "sell"
    type: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    # Precio total de la operación (quantity * price)
    # Lo guardamos para evitar recalcularlo constantemente
    total_value: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    from datetime import datetime
    from sqlalchemy import DateTime
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    position: Mapped["Position"] = relationship(
        "Position", back_populates="transactions"
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.type} {self.quantity} @ {self.price}>"