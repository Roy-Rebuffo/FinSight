import pytest


@pytest.fixture
def portfolio(client, auth_headers):
    """Fixture que crea un portfolio de prueba."""
    response = client.post("/api/portfolios", json={
        "name": "Portfolio de Test"
    }, headers=auth_headers)
    return response.json()


def test_create_position(client, auth_headers, portfolio):
    """Se puede añadir una posición a un portfolio."""
    response = client.post(
        f"/api/portfolios/{portfolio['id']}/positions",
        json={
            "ticker": "AAPL",
            "asset_type": "stock",
            "quantity": "10",
            "avg_cost": "150.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["asset_type"] == "stock"
    assert float(data["quantity"]) == 10.0
    assert float(data["avg_cost"]) == 150.0


def test_ticker_is_uppercased(client, auth_headers, portfolio):
    """El ticker se convierte automáticamente a mayúsculas."""
    response = client.post(
        f"/api/portfolios/{portfolio['id']}/positions",
        json={
            "ticker": "aapl",  # minúsculas
            "asset_type": "stock",
            "quantity": "5",
            "avg_cost": "150.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["ticker"] == "AAPL"  # debe estar en mayúsculas


def test_duplicate_ticker_in_portfolio(client, auth_headers, portfolio):
    """No se puede añadir el mismo ticker dos veces al mismo portfolio."""
    position_data = {
        "ticker": "AAPL",
        "asset_type": "stock",
        "quantity": "10",
        "avg_cost": "150.00",
    }
    client.post(
        f"/api/portfolios/{portfolio['id']}/positions",
        json=position_data,
        headers=auth_headers,
    )
    # Segunda vez — debe fallar
    response = client.post(
        f"/api/portfolios/{portfolio['id']}/positions",
        json=position_data,
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_get_positions(client, auth_headers, portfolio):
    """Se pueden listar las posiciones de un portfolio."""
    # Añadir dos posiciones
    for ticker, price in [("AAPL", "150"), ("MSFT", "300")]:
        client.post(
            f"/api/portfolios/{portfolio['id']}/positions",
            json={
                "ticker": ticker,
                "asset_type": "stock",
                "quantity": "10",
                "avg_cost": price,
            },
            headers=auth_headers,
        )

    response = client.get(
        f"/api/portfolios/{portfolio['id']}/positions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_create_transaction_buy(client, auth_headers, portfolio):
    """Una compra actualiza la cantidad y el precio promedio."""
    # Crear posición inicial: 10 acciones a $100
    pos_response = client.post(
        f"/api/portfolios/{portfolio['id']}/positions",
        json={
            "ticker": "AAPL",
            "asset_type": "stock",
            "quantity": "10",
            "avg_cost": "100.00",
        },
        headers=auth_headers,
    )
    position_id = pos_response.json()["id"]

    # Comprar 10 más a $200 — el avg_cost debe ser $150
    response = client.post(
        f"/api/portfolios/{portfolio['id']}/positions/{position_id}/transactions",
        json={
            "type": "buy",
            "quantity": "10",
            "price": "200.00",
            "executed_at": "2024-01-15T10:00:00Z",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201

    # Verificar que el avg_cost se actualizó correctamente
    positions = client.get(
        f"/api/portfolios/{portfolio['id']}/positions",
        headers=auth_headers,
    ).json()

    aapl = next(p for p in positions if p["ticker"] == "AAPL")
    assert float(aapl["quantity"]) == 20.0
    assert float(aapl["avg_cost"]) == 150.0  # (10*100 + 10*200) / 20


def test_cannot_sell_more_than_owned(client, auth_headers, portfolio):
    """No se puede vender más cantidad de la que se tiene."""
    pos_response = client.post(
        f"/api/portfolios/{portfolio['id']}/positions",
        json={
            "ticker": "AAPL",
            "asset_type": "stock",
            "quantity": "10",
            "avg_cost": "150.00",
        },
        headers=auth_headers,
    )
    position_id = pos_response.json()["id"]

    response = client.post(
        f"/api/portfolios/{portfolio['id']}/positions/{position_id}/transactions",
        json={
            "type": "sell",
            "quantity": "999",  # más de lo que tenemos
            "price": "200.00",
            "executed_at": "2024-01-15T10:00:00Z",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400