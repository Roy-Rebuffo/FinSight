from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import verify_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Código que se ejecuta al arrancar y al apagar la aplicación.
    'lifespan' reemplaza los eventos @app.on_event (deprecados en FastAPI 0.115)
    """
    # ── Startup ──
    print("Arrancando FinSight API...")

    # Verificar conexión a la base de datos
    if verify_database_connection():
        print("PostgreSQL: conexión OK")
    else:
        print("PostgreSQL: ERROR de conexión — revisa DATABASE_URL")

    yield  # La aplicación corre aquí

    # ── Shutdown ──
    print("Apagando FinSight API...")


app = FastAPI(
    title="FinSight API",
    description="AI-powered portfolio analyst — FastAPI · LangGraph · PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — permite que el frontend React (localhost:3000) llame a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend en desarrollo
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está viva."""
    return {
        "status": "ok",
        "service": "finsight-api",
        "version": "0.1.0",
    }