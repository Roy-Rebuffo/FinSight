from langchain_core.tools import tool
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.portfolio import Portfolio
from app.models.position import Position, Transaction
import yfinance as yf
import pandas as pd
from decimal import Decimal


def get_db_session() -> Session:
    """Crea una sesión de DB para usar dentro de las tools."""
    return SessionLocal()


@tool
def portfolio_tool(user_id: str, portfolio_id: str = "") -> str:
    """
    Consulta los datos del portfolio del usuario desde la base de datos.
    Devuelve posiciones, cantidades, precios promedio y valor actual.
    Usa esta herramienta cuando el usuario pregunta sobre su portfolio,
    sus posiciones, su inversión total o sus activos.
    """
    db = get_db_session()
    try:
        # Si no se especifica portfolio, busca todos los del usuario
        query = db.query(Portfolio).filter(Portfolio.user_id == user_id)
        if portfolio_id:
            query = query.filter(Portfolio.id == portfolio_id)

        portfolios = query.all()
        if not portfolios:
            return "El usuario no tiene portfolios creados."

        result = []
        for portfolio in portfolios:
            positions = db.query(Position).filter(
                Position.portfolio_id == portfolio.id
            ).all()

            portfolio_data = {
                "portfolio_name": portfolio.name,
                "portfolio_id": portfolio.id,
                "benchmark": portfolio.benchmark_ticker,
                "positions": []
            }

            for pos in positions:
                portfolio_data["positions"].append({
                    "ticker": pos.ticker,
                    "asset_type": pos.asset_type,
                    "quantity": float(pos.quantity),
                    "avg_cost": float(pos.avg_cost),
                    "total_invested": float(pos.quantity * pos.avg_cost),
                })

            result.append(portfolio_data)

        return str(result)
    finally:
        db.close()


@tool
def market_data_tool(tickers: str) -> str:
    """
    Obtiene datos de mercado en tiempo real para uno o varios tickers.
    Devuelve precio actual, variación diaria, volumen y info básica.
    Usa esta herramienta cuando el usuario pregunta por el precio actual
    de un activo, noticias recientes o datos de mercado.
    Parámetro tickers: string con tickers separados por comas. Ej: 'AAPL,MSFT,GOOGL'
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
        result = []

        for ticker_symbol in ticker_list:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            result.append({
                "ticker": ticker_symbol,
                "name": info.get("longName", ticker_symbol),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "day_change_pct": info.get("regularMarketChangePercent"),
                "market_cap": info.get("marketCap"),
                "sector": info.get("sector", "N/A"),
                "currency": info.get("currency", "USD"),
            })

        return str(result)
    except Exception as e:
        return f"Error obteniendo datos de mercado: {str(e)}"


@tool
def quant_tool(user_id: str, portfolio_id: str = "") -> str:
    """
    Calcula métricas cuantitativas del portfolio: Sharpe ratio,
    drawdown máximo, volatilidad anualizada y correlación entre activos.
    Usa esta herramienta cuando el usuario pregunta por el riesgo,
    rendimiento, Sharpe ratio o métricas cuantitativas del portfolio.
    """
    db = get_db_session()
    try:
        query = db.query(Portfolio).filter(Portfolio.user_id == user_id)
        if portfolio_id:
            query = query.filter(Portfolio.id == portfolio_id)

        portfolio = query.first()
        if not portfolio:
            return "No se encontró el portfolio."

        positions = db.query(Position).filter(
            Position.portfolio_id == portfolio.id
        ).all()

        if not positions:
            return "El portfolio no tiene posiciones para analizar."

        tickers = [p.ticker for p in positions]

        # Descarga histórico de 1 año para cada ticker
        data = yf.download(tickers, period="1y", auto_adjust=True, progress=False)

        if data.empty:
            return "No se pudieron obtener datos históricos."

        # Calcula retornos diarios
        if len(tickers) == 1:
            prices = data["Close"]
        else:
            prices = data["Close"]

        returns = prices.pct_change().dropna()

        # Sharpe ratio anualizado (asume tasa libre de riesgo = 0)
        sharpe = {}
        for ticker in tickers:
            if ticker in returns.columns if hasattr(returns, 'columns') else True:
                r = returns[ticker] if len(tickers) > 1 else returns
                sharpe[ticker] = round(
                    float(r.mean() / r.std() * (252 ** 0.5)), 3
                )

        # Drawdown máximo
        max_drawdown = {}
        for ticker in tickers:
            r = returns[ticker] if len(tickers) > 1 else returns
            cumulative = (1 + r).cumprod()
            rolling_max = cumulative.cummax()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown[ticker] = round(float(drawdown.min()), 3)

        return str({
            "portfolio": portfolio.name,
            "tickers_analyzed": tickers,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "period": "1 year",
        })

    except Exception as e:
        return f"Error calculando métricas: {str(e)}"
    finally:
        db.close()


# Lista de todas las tools disponibles para el agente
TOOLS = [portfolio_tool, market_data_tool, quant_tool]