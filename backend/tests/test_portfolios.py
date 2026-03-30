def test_create_portfolio(client, auth_headers):
    """Un usuario autenticado puede crear un portfolio."""
    response = client.post("/api/portfolios", json={
        "name": "Mi Portfolio de Test",
        "description": "Portfolio para tests",
        "benchmark_ticker": "^GSPC",
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mi Portfolio de Test"
    assert data["benchmark_ticker"] == "^GSPC"
    assert "id" in data
    assert "user_id" in data


def test_get_portfolios_empty(client, auth_headers):
    """Un usuario nuevo no tiene portfolios."""
    response = client.get("/api/portfolios", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_portfolios(client, auth_headers):
    """Se pueden listar los portfolios del usuario."""
    # Crear dos portfolios
    client.post("/api/portfolios", json={
        "name": "Portfolio 1"
    }, headers=auth_headers)
    client.post("/api/portfolios", json={
        "name": "Portfolio 2"
    }, headers=auth_headers)

    response = client.get("/api/portfolios", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_portfolio_by_id(client, auth_headers):
    """Se puede obtener un portfolio específico por ID."""
    # Crear portfolio
    create_response = client.post("/api/portfolios", json={
        "name": "Portfolio Específico"
    }, headers=auth_headers)
    portfolio_id = create_response.json()["id"]

    # Obtenerlo por ID
    response = client.get(f"/api/portfolios/{portfolio_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Portfolio Específico"


def test_get_portfolio_not_found(client, auth_headers):
    """Obtener un portfolio inexistente devuelve 404."""
    response = client.get(
        "/api/portfolios/00000000-0000-0000-0000-000000000000",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_update_portfolio(client, auth_headers):
    """Se puede actualizar el nombre de un portfolio."""
    create_response = client.post("/api/portfolios", json={
        "name": "Nombre Original"
    }, headers=auth_headers)
    portfolio_id = create_response.json()["id"]

    response = client.put(f"/api/portfolios/{portfolio_id}", json={
        "name": "Nombre Actualizado"
    }, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Nombre Actualizado"


def test_delete_portfolio(client, auth_headers):
    """Se puede eliminar un portfolio."""
    create_response = client.post("/api/portfolios", json={
        "name": "Portfolio a Eliminar"
    }, headers=auth_headers)
    portfolio_id = create_response.json()["id"]

    # Eliminar
    response = client.delete(
        f"/api/portfolios/{portfolio_id}",
        headers=auth_headers
    )
    assert response.status_code == 204

    # Verificar que ya no existe
    response = client.get(
        f"/api/portfolios/{portfolio_id}",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_cannot_access_other_user_portfolio(client, db):
    """Un usuario no puede acceder al portfolio de otro usuario."""
    # Crear usuario 1 y su portfolio
    client.post("/api/auth/register", json={
        "email": "user1@test.com",
        "password": "password123",
        "full_name": "User 1",
        "currency": "USD",
    })
    login1 = client.post("/api/auth/login", data={
        "username": "user1@test.com",
        "password": "password123",
    })
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

    portfolio_response = client.post("/api/portfolios", json={
        "name": "Portfolio Privado"
    }, headers=headers1)
    portfolio_id = portfolio_response.json()["id"]

    # Crear usuario 2
    client.post("/api/auth/register", json={
        "email": "user2@test.com",
        "password": "password123",
        "full_name": "User 2",
        "currency": "USD",
    })
    login2 = client.post("/api/auth/login", data={
        "username": "user2@test.com",
        "password": "password123",
    })
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    # Usuario 2 intenta acceder al portfolio de Usuario 1
    response = client.get(
        f"/api/portfolios/{portfolio_id}",
        headers=headers2
    )
    assert response.status_code == 404