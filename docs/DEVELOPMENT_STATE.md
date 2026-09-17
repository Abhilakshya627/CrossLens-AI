# CrossLens AI Development State

## Current phase

**Phase 0 complete - awaiting human approval.** The repository audit, synopsis
review, and architecture baseline are complete. No application implementation
has begun.

## Completed work

- Read the repository README and the complete 18-page synopsis
  (`docs/synopsisssss.pdf`).
- Confirmed the repository has no source code, package/dependency manifest,
  test suite, or prior architecture documents.
- Created the architectural memory documents:
  - `docs/ARCHITECTURE.md`
  - `docs/MODULE_MAP.md`
  - `docs/DEVELOPMENT_STATE.md`

## Current implementation state

| Area | Status |
| --- | --- |
| Shared contracts | Proposed only; no code yet |
| Infrastructure/configuration | Proposed only; no code or dependency installed |
| M1-M10 | Not started |
| Frontend | Not started |
| Data stores and local AI | Not provisioned or selected |
| Public programmatic interfaces | None implemented |

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

## Verification performed

- Repository structure and README inspected.
- Synopsis text extracted and reviewed in full.
- A visual PDF-render attempt was made but the available Poppler renderer failed
  to resolve a path and the bundled Python runtime lacks PyMuPDF. The text
  extraction was successful; no PDF artifact was produced or altered.
- No automated tests exist to execute at this phase, and no dependencies were
  added.

## Known limitations and risks

- Hardware capability could not be reliably identified by the current probe;
  local model selection awaits a representative workload benchmark.
- Data retention, access control, encryption, reviewed policy/rule ownership,
  and domain-vocabulary governance are not yet specified.
- The integration footprint of four local supporting services needs compose
  profiles and adapter-level testing.
- The architecture documents are proposals, not validated runtime behaviour.

## Next gated step

On approval, begin **Phase 1: Shared Contracts + Infrastructure Foundation**.
It will first define the stable contract layout, configuration schema, structured
logging, dependency injection/composition root, ports, and minimal development
infrastructure; it will not begin M1 until Phase 1 has been reported and
approved.

## Pending decisions requiring human input before broad implementation

1. Confirm the intended privacy/retention and authentication posture for source
   materials, especially whether the initial development uses synthetic-only
   claim bundles.
2. Confirm the initial reviewed mock-policy/rule-pack format and responsible
   reviewer/owner.
3. Provide or approve the local deployment hardware target before committing to
   an OCR/VLM/LLM/embedding model stack.
