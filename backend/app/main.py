from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import verify_database_connection, init_langgraph_tables
from app.routers import auth_router, portfolios_router, positions_router
from app.routers.agent import router as agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Arrancando FinSight API...")
    if verify_database_connection():
        print("PostgreSQL: conexión OK")
    else:
        print("PostgreSQL: ERROR de conexión")

    # Inicializa las tablas de LangGraph (checkpoints, checkpoint_writes)
    try:
        init_langgraph_tables()
    except Exception as e:
        print(f"LangGraph setup warning: {e}")

    yield
    print("Apagando FinSight API...")


app = FastAPI(
    title="FinSight API",
    description="AI-powered portfolio analyst — FastAPI · LangGraph · PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(portfolios_router)
app.include_router(positions_router)
app.include_router(agent_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "finsight-api", "version": "0.1.0"}