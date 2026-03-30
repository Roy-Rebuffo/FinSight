def test_register_user(client):
    """Un usuario nuevo puede registrarse correctamente."""
    response = client.post("/api/auth/register", json={
        "email": "nuevo@test.com",
        "password": "password123",
        "full_name": "Nuevo Usuario",
        "currency": "EUR",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo@test.com"
    assert data["full_name"] == "Nuevo Usuario"
    assert data["currency"] == "EUR"
    assert "id" in data
    # Verificamos que NO se devuelve la password hasheada
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_email(client, registered_user):
    """No se puede registrar dos usuarios con el mismo email."""
    response = client.post("/api/auth/register", json={
        "email": "test@finsight.com",  # mismo email que registered_user
        "password": "otrapassword123",
        "full_name": "Otro Usuario",
        "currency": "USD",
    })
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_login_success(client, registered_user):
    """Un usuario registrado puede hacer login correctamente."""
    response = client.post("/api/auth/login", data={
        "username": "test@finsight.com",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # El token JWT tiene 3 partes separadas por puntos
    assert len(data["access_token"].split(".")) == 3


def test_login_wrong_password(client, registered_user):
    """Login con password incorrecta devuelve 401."""
    response = client.post("/api/auth/login", data={
        "username": "test@finsight.com",
        "password": "passwordincorrecta",
    })
    assert response.status_code == 401


def test_get_me(client, auth_headers):
    """Un usuario autenticado puede obtener sus propios datos."""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@finsight.com"
    assert data["full_name"] == "Test User"


def test_get_me_without_token(client):
    """Sin token no se puede acceder a endpoints protegidos."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401