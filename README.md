# CrossLens AI

CrossLens AI is a provenance-aware Evidence Intelligence platform. It preserves
the bounded vehicle-insurance review research prototype while keeping its core
contracts and evidence graph domain independent.

## Current state

Phase 1 establishes shared Pydantic contracts, provider/storage ports,
environment configuration, JSON logging, a health-only FastAPI composition
root, Celery bootstrap, and local Docker Compose service definitions. No M1
ingestion or document-understanding behaviour exists yet.

Architecture and phase decisions are recorded in:

- `docs/ARCHITECTURE.md`
- `docs/MODULE_MAP.md`
- `docs/DEVELOPMENT_STATE.md`

## Local foundation

Use Python 3.13 or later, then install the declared project dependencies:

```powershell
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m pytest
uvicorn infrastructure.api.app:create_app --factory --reload
```

The health endpoint is available at `GET /healthz`. To start the local support
services after creating `.env`, use `docker compose up -d`; start the
health-only backend and empty worker bootstrap with `docker compose --profile
app up --build`.

Never commit `.env`, uploaded source material, local data volumes, or production
credentials.
