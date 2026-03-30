import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importamos la Base y todos los modelos.
# Este import es CRÍTICO: si no importas los modelos aquí,
# Alembic no los detecta y no genera las migraciones correctamente.
from app.core.database import Base
from app.models import User, Portfolio, Position, Transaction, Snapshot, AgentSession

# Configuración de logging de Alembic (usa el alembic.ini)
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Le decimos a Alembic qué metadata usar para comparar con la DB.
# Base.metadata contiene la definición de todas tus tablas.
# Alembic compara esto con el estado actual de la DB para
# detectar qué ha cambiado y generar las migraciones.
target_metadata = Base.metadata


def get_url() -> str:
    """
    Lee la DATABASE_URL desde las variables de entorno.
    Docker inyecta esta variable en el contenedor via docker-compose.yml.
    Así evitamos hardcodear credenciales en cualquier fichero.
    """
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise ValueError(
            "DATABASE_URL no está definida. "
            "Verifica tu fichero .env y docker-compose.yml"
        )
    return url


def run_migrations_offline() -> None:
    """
    Modo offline: genera el SQL sin conectarse a la DB.
    Útil para revisar qué SQL se va a ejecutar antes de aplicarlo.
    Ejecutar con: alembic upgrade head --sql
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # compare_type=True hace que Alembic detecte cambios de tipo
        # en columnas existentes (ej: String(100) → String(200))
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Modo online: se conecta a la DB y aplica los cambios directamente.
    """
    from sqlalchemy import create_engine

    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Alembic llama a una función u otra según el modo
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()