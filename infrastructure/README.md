# Infrastructure Foundation

## Purpose

`infrastructure/` owns application composition and adapters. It may implement
public protocols from `contracts/`, but must not contain M1-M10 business logic
or expose storage/model SDKs to those modules.

## Current public entry points

- `config.py`: environment-driven `Settings` with no hard-coded production
  credentials or provider model names.
- `logging.py`: standard-library JSON logging with an allowlist of correlation
  IDs and no source-content payload.
- `container.py`: the composition root and dependency registry.
- `api/app.py:create_app`: health-only FastAPI application with `GET /healthz`.
- `tasks/celery_app.py:create_celery_app`: configured Celery bootstrap; no
  business tasks are registered until their module phase.

## Local development

`compose.yaml` defines Redis, PostgreSQL, Neo4j, ChromaDB, and optional backend
and worker containers. It has no database or AI adapters yet, so starting those
services does not create evidence data. Copy `.env.example` to an untracked
`.env` before starting application-profile containers.

## Tests and limitations

Foundation tests cover settings wiring, the empty dependency registry, Celery
configuration without a broker connection, and the health endpoint. Docker
Compose configuration is validated in this phase. Image builds and live service
integration require a running Docker daemon and belong to the adapter phases.

