from fastapi import FastAPI

app = FastAPI(
    title="FinSight API",
    description="AI-powered portfolio analyst",
    version="0.1.0",
)

@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está viva."""
    return {"status": "ok", "service": "finsight-api"}