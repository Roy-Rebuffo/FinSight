import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Base de datos SQLite en memoria para tests
# No necesita Docker ni PostgreSQL — es instantánea y se destruye al terminar
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)


@pytest.fixture(scope="function")
def db():
    """
    Fixture que crea una DB limpia para cada test.
    'scope=function' significa que se crea y destruye en cada test.
    Así cada test empieza con una DB vacía — sin interferencias.
    """
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db):
    """
    Fixture que crea un cliente HTTP de prueba.
    Sobreescribe la dependencia get_db para usar la DB de test.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """
    Fixture que registra un usuario de prueba.
    Reutilizable en todos los tests que necesiten un usuario.
    """
    response = client.post("/api/auth/register", json={
        "email": "test@finsight.com",
        "password": "testpass123",
        "full_name": "Test User",
        "currency": "USD",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(client, registered_user):
    """
    Fixture que hace login y devuelve los headers de autorización.
    Reutilizable en todos los tests que necesiten autenticación.
    """
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@finsight.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}