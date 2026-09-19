# CrossLens AI Development State

## Current phase

**Phase 1 complete - awaiting human approval.** The repository audit and
architecture baseline are complete, and the shared contract/infrastructure
foundation is now implemented. M1 data ingestion has not begun.

## Completed work

- Read the repository README and the complete 18-page synopsis
  (`docs/synopsisssss.pdf`).
- Confirmed the repository has no source code, package/dependency manifest,
  test suite, or prior architecture documents.
- Created the architectural memory documents:
  - `docs/ARCHITECTURE.md`
  - `docs/MODULE_MAP.md`
  - `docs/DEVELOPMENT_STATE.md`
- Added versioned Pydantic contracts for ingestion, extraction, normalised
  knowledge, graph, retrieval, verification, reasoning, outcomes, audit, and
  system health.
- Added database-independent storage and provider protocols, environment
  settings, standard-library JSON logging, a health-only FastAPI composition
  root, and Celery bootstrap with no business tasks.
- Added Docker/Compose development definitions and eight foundation tests.

## Current implementation state

| Area | Status |
| --- | --- |
| Shared contracts | Implemented as versioned Pydantic DTOs and public protocols |
| Infrastructure/configuration | Implemented; storage/model adapters intentionally deferred |
| M1-M10 | Not started |
| Frontend | Not started |
| Data stores and local AI | Compose definitions/configuration only; not provisioned or selected |
| Public programmatic interfaces | Contract schemas, storage/provider ports, health API, and Celery factory |

## Architecture decisions recorded

- CrossLens is a modular monolith with a contract/port boundary, initially using
  FastAPI, Celery/Redis, PostgreSQL, Neo4j, ChromaDB, and a configurable local
  AI provider layer.
- The Evidence Graph is an application abstraction. Neo4j and ChromaDB calls
  are confined to infrastructure adapters.
- A `SourceFragment` is the citeable evidence unit; document versions and audit
  history are retained rather than overwritten.
- Evidence status distinguishes supported, contradicted, insufficient evidence,
  partial processing, and provider unavailability. Retrieval and model output
  never establish proof by themselves.
- Insurance remains the first evaluated adapter; generic graph/contracts remain
  domain independent. The synopsis' pgvector option is superseded by ChromaDB
  for vector storage under the current master brief, while PostgreSQL keyword
  search remains optional behind M5.
- Contract invariants reject source-free findings, source-free evidence links,
  unsupported observation-to-fact typing, and insufficient-evidence results
  that do not identify the missing material.
- Phase 1 declares only the needed foundation dependencies. The local Python
  environment already contained FastAPI, Pydantic, Pydantic Settings, Celery,
  Uvicorn, pytest, and HTTPX; the Redis client (`redis 8.1.0`) was added.

## Verification performed

- Repository structure and README inspected.
- Synopsis text extracted and reviewed in full.
- A visual PDF-render attempt was made but the available Poppler renderer failed
  to resolve a path and the bundled Python runtime lacks PyMuPDF. The text
  extraction was successful; no PDF artifact was produced or altered.
- `python -m pytest`: **8 passed**.
- `python -m compileall -q contracts infrastructure`: passed.
- All contract modules import successfully.
- `docker compose --env-file .env.example --profile app config --quiet`:
  passed.
- Docker image build could not run because Docker Desktop's Linux daemon is not
  running on this host. No image or container was created.

## Known limitations and risks

- No concrete storage, OCR, local-model, or AI-provider adapter exists yet;
  Phase 1 only defines their ports and configuration.
- Docker live integration cannot be verified until the local Docker daemon is
  started.
- Hardware capability could not be reliably identified by the current probe;
  local model selection awaits a representative workload benchmark.
- Data retention, access control, encryption, reviewed policy/rule ownership,
  and domain-vocabulary governance are not yet specified.
- The integration footprint of four local supporting services needs compose
  profiles and adapter-level testing.
- The architecture documents are proposals, not validated runtime behaviour.

## Next gated step

On approval, begin **Phase 2: M1 Data Ingestion**. It will implement only file
validation, MIME detection, hashing, versioned source registration, original
file preservation, idempotent processing-job creation, and status contracts;
it will not perform document understanding.

## Pending decisions requiring human input before broad implementation

1. Confirm the intended privacy/retention and authentication posture for source
   materials, especially whether the initial development uses synthetic-only
   claim bundles.
2. Confirm the initial reviewed mock-policy/rule-pack format and responsible
   reviewer/owner.
3. Provide or approve the local deployment hardware target before committing to
   an OCR/VLM/LLM/embedding model stack.
