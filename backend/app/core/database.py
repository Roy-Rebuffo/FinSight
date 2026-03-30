from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from langgraph.checkpoint.postgres import PostgresSaver


# ── Engine ────────────────────────────────────────────────────────────
# El engine es la conexión física a PostgreSQL.
# pool_pre_ping=True verifica que la conexión sigue viva antes de usarla.
# Esto evita errores si PostgreSQL se reinició mientras la app estaba corriendo.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # pool_size: conexiones simultáneas mantenidas abiertas
    pool_size=10,
    # max_overflow: conexiones extra permitidas si el pool está lleno
    max_overflow=20,
)


# ── Session factory ───────────────────────────────────────────────────
# SessionLocal es una "fábrica" de sesiones.
# Cada vez que llamas SessionLocal() obtienes una sesión nueva.
SessionLocal = sessionmaker(
    autocommit=False,   # Los cambios no se guardan hasta que hagas commit()
    autoflush=False,    # SQLAlchemy no envía SQL hasta que se lo pidas
    bind=engine,
)


# ── Base declarativa ──────────────────────────────────────────────────
# Todos tus modelos ORM heredarán de esta clase.
# SQLAlchemy usa esto para registrar qué tablas existen.
class Base(DeclarativeBase):
    pass


# ── Dependencia de FastAPI ─────────────────────────────────────────────
def get_db():
    """
    Generador que FastAPI usa como dependencia en los endpoints.

    Uso en un endpoint:
        @router.get("/portfolios")
        def get_portfolios(db: Session = Depends(get_db)):
            ...

    El 'yield' hace que FastAPI:
    1. Abra la sesión antes de ejecutar el endpoint
    2. Pase la sesión al endpoint
    3. Cierre la sesión después de enviar la respuesta
    4. Haga rollback automático si hay una excepción

    Esto garantiza que cada request tiene su propia sesión
    y que las sesiones siempre se cierran, incluso con errores.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Función de verificación ───────────────────────────────────────────
def verify_database_connection() -> bool:
    """
    Verifica que la conexión a PostgreSQL funciona.
    La usamos en el startup de FastAPI para fallar rápido
    si la base de datos no está disponible.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return False

# ── PostgresSaver para LangGraph ───────────────────────────────────────
# Esta clase permite a LangGraph guardar checkpoints en PostgreSQL.
def get_postgres_saver() -> PostgresSaver:
    """
    Crea un PostgresSaver para LangGraph.
    Usa la misma base de datos que SQLAlchemy pero en un
    esquema separado 'langgraph' para no mezclar tablas.

    PostgresSaver guarda el estado completo del grafo después
    de cada nodo, permitiendo reanudar conversaciones.
    """
    return PostgresSaver.from_conn_string(
        settings.DATABASE_URL.replace(
            "postgresql+psycopg2://",
            "postgresql://"
        )
    )


def init_langgraph_tables():
    """
    Crea las tablas que necesita LangGraph en PostgreSQL.
    Se llama una vez al arrancar la aplicación.
    Las tablas son: checkpoints, checkpoint_writes, checkpoint_migrations.
    """
    with get_postgres_saver() as saver:
        saver.setup()
    print("LangGraph: tablas inicializadas OK")