# FinSight — AI-Powered Portfolio Analyst

![CI](https://github.com/TU_USUARIO/finsight/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-19-61DAFB)
![LangGraph](https://img.shields.io/badge/LangGraph-1.1-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)

> A full-stack AI-powered portfolio analyst that queries your investments in real time, fetches live market data, and calculates quantitative risk metrics through a LangGraph agent with conversation memory persisted in PostgreSQL.

---

## Tech Stack

**Backend**
- **FastAPI** — Async REST API with automatic Swagger UI documentation
- **SQLAlchemy 2.0** — Modern ORM with full type hint support and connection pooling
- **Alembic** — Database schema migrations with version control
- **LangGraph** — Stateful AI agent with decision graph and tool routing
- **PostgresSaver** — Agent conversation state persisted in PostgreSQL
- **Celery + Redis** — Background task processing and caching layer

**Frontend**
- **React 19 + TypeScript** — Modern UI with static typing
- **Vite** — Ultra-fast bundler with instant hot-reload
- **TanStack Query** — Server state management with automatic caching
- **Recharts** — Interactive portfolio allocation charts
- **Zustand** — Lightweight global auth state management
- **Tailwind CSS** — Utility-first styling

**Infrastructure**
- **Docker Compose** — 6-service orchestration with healthchecks and startup order
- **PostgreSQL 16** — Relational database with 6 well-designed tables
- **Nginx** — Static file serving for the React build
- **GitHub Actions** — CI/CD pipeline running tests on every push

---

## Architecture
```
┌─────────────────┐     ┌──────────────────────────────────────┐
│   React + Vite  │────▶│           FastAPI (Uvicorn)           │
│   Nginx :3000   │     │              :8000                    │
└─────────────────┘     └──────┬───────────────┬───────────────┘
                               │               │
                    ┌──────────▼──┐    ┌───────▼────────┐
                    │ PostgreSQL  │    │     Redis       │
                    │    :5432    │    │     :6379       │
                    └─────────────┘    └────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   LangGraph Agent   │
                    │  portfolio_tool     │
                    │  market_data_tool   │
                    │  quant_tool         │
                    └─────────────────────┘
```

**Database Schema**
```
users (1) ──── (N) portfolios
portfolios (1) ── (N) positions
positions (1) ─── (N) transactions
portfolios (1) ── (N) snapshots
users (1) ──── (N) agent_sessions
```

---

## Getting Started

### Prerequisites
- Docker Desktop
- Git

### 1. Clone the repository
```bash
git clone https://github.com/TU_USUARIO/finsight.git
cd finsight
```

### 2. Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` with your values:
```bash
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=generate_with_python_secrets_token_hex_32
GROQ_API_KEY=gsk_your_groq_key  # Free at console.groq.com
```

### 3. Start the project
```bash
docker compose up --build -d
```

First run takes ~3 minutes to pull and build all images.

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

---

## Features

### JWT Authentication
- User registration and login with HS256-signed JWT tokens
- Protected routes via FastAPI dependency injection
- Session persistence on the frontend using Zustand with localStorage

### Portfolio Management
- Full CRUD for portfolios and positions
- Transaction recording with automatic weighted average cost calculation
- Interactive allocation pie chart built with Recharts

### LangGraph AI Agent
The agent automatically decides which tool to invoke based on the user's question:

| Tool | Activated when |
|------|---------------|
| `portfolio_tool` | Questions about positions and investments |
| `market_data_tool` | Questions about live prices and market data |
| `quant_tool` | Questions about risk, Sharpe ratio and quant metrics |

Conversation memory is persisted in PostgreSQL via `PostgresSaver`, enabling continuous multi-turn conversations across sessions.

---

## Running Tests
```bash
docker compose run --rm --no-deps api pytest tests/ -v
```

**20 tests** covering the full application cycle:
- **Auth**: registration, login, JWT tokens, protected routes
- **Portfolios**: CRUD operations, user data isolation
- **Positions**: transactions, weighted average cost calculation, validations

---

## Project Structure
```
finsight/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph graph and tool definitions
│   │   ├── core/           # Config, DB engine, security, dependencies
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── routers/        # FastAPI endpoint routers
│   │   └── schemas/        # Pydantic request/response schemas
│   ├── alembic/            # Database migration scripts
│   └── tests/              # pytest test suite
├── frontend/
│   └── src/
│       ├── api/            # HTTP clients per domain
│       ├── pages/          # React page components
│       ├── components/     # Shared UI components
│       ├── store/          # Zustand global state
│       └── types/          # TypeScript type definitions
├── docker-compose.yml
├── docker-compose.override.yml
└── .env.example
```

---

## Key Technical Decisions

**Why LangGraph over simple chains?** LangGraph models the agent as an explicit state graph, making tool routing deterministic and debuggable. Each node has a clear responsibility and the conversation state persists between requests via PostgresSaver.

**Why PostgreSQL for agent state?** Using a single database for both business data and agent checkpoints simplifies operations — one backup strategy, one monitoring setup, one connection string.

**Why Docker from day one?** Every service runs in isolation with defined healthchecks and startup order. Any developer can run the full stack with a single command regardless of their local environment.

---

## Author

**Roy Rebuffo** — [@Roy-Rebuffo](https://github.com/Roy-Rebuffo)

Built as a technical portfolio project demonstrating production-grade integration of generative AI with modern backend architecture.