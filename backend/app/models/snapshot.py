from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, ForeignKey, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Snapshot(TimestampMixin, Base):
    """
    Tabla: snapshots
    Foto del estado del portfolio en un momento concreto.
    Permite construir gráficas históricas sin recalcular cada vez.
    """
    __tablename__ = "snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )

    portfolio_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Valor total del portfolio en este momento
    total_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # Sharpe ratio calculado en este momento
    sharpe_ratio: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), nullable=True
    )

    # JSON con el desglose por activo: {"AAPL": 0.45, "MSFT": 0.30, ...}
    allocation: Mapped[dict] = mapped_column(JSON, nullable=True)

    # JSON con métricas adicionales calculadas
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True)

    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="snapshots"
    )


class AgentSession(TimestampMixin, Base):
    """
    Tabla: agent_sessions
    Guarda el estado de la conversación con el agente LangGraph por usuario.
    En la Fase 4 esto se complementa con PostgresSaver para el estado interno.
    """
    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # thread_id es el identificador que usa LangGraph para
    # recuperar el estado de una conversación específica
    thread_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=generate_uuid,
    )

    title: Mapped[str] = mapped_column(
        String(200), nullable=True
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="agent_sessions"
    )

    def __repr__(self) -> str:
        return f"<AgentSession thread={self.thread_id}>"