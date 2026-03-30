import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class TimestampMixin:
    """
    Mixin que añade created_at y updated_at a cualquier modelo.
    En lugar de repetir estos campos en cada tabla, heredas este mixin.

    Uso:
        class Portfolio(TimestampMixin, Base):
            ...
        # Portfolio tendrá automáticamente created_at y updated_at
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        # default_factory se ejecuta en Python cuando creas el objeto
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        # onupdate se ejecuta automáticamente cada vez que
        # SQLAlchemy actualiza una fila de esta tabla
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


def generate_uuid() -> str:
    """Genera un UUID v4 como string. Lo usan todos los modelos como PK."""
    return str(uuid.uuid4())