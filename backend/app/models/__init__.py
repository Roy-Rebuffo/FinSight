# Importar todos los modelos aquí tiene dos propósitos:
# 1. SQLAlchemy registra las tablas en Base.metadata
# 2. Alembic encuentra los modelos al generar migraciones automáticas

from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.position import Position, Transaction
from app.models.snapshot import Snapshot, AgentSession

__all__ = [
    "User",
    "Portfolio",
    "Position",
    "Transaction",
    "Snapshot",
    "AgentSession",
]