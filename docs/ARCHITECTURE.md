# CrossLens AI Architecture

## Status and scope

This is the Phase 0 architecture baseline for CrossLens AI. It preserves the
synopsis' bounded vehicle-claim prototype while generalising the product into a
domain-independent Evidence Intelligence platform. No application code, runtime
dependency, database schema, or module directory is created by this phase.

The central architectural rule is that a source, an extracted observation, a
normalised claim, retrieval relevance, a verification outcome, and AI reasoning
are different objects with different evidential weight. A finding must make its
supporting path inspectable all the way to the versioned source fragment.

## Repository audit and requirements carried forward

At Phase 0, the repository contains only `README.md` and
`docs/synopsisssss.pdf`. The README identifies CrossLens as an assistant for
source review and consistency checking; it contains no implementation or
dependency manifest. The synopsis is the authoritative initial research scope:

- The demonstrator is a vehicle-claim bundle: claim and policy documents,
  amendments, an itemised repair estimate, and vehicle photographs.
- Digital and scanned documents must retain text, tables, page locations,
  bounding boxes, extraction warnings, and the original files. Spreadsheet
  lineage must similarly retain sheet and cell/range coordinates.
- Visual output is an *observation* of visible parts, apparent conditions, and
  visibility limitations. It cannot establish hidden damage, causation, or a
  required repair.
- Versioned mock-policy context, including amendments and definitions, must be
  selected before reviewed rules evaluate identifiers, dates, arithmetic,
  deductions, limits, and evidence links.
- A check has three materially distinct outcomes: satisfied/supported,
  contradicted, or insufficient evidence. Missing evidence is never silently
  treated as a contradiction.
- Findings need source-linked explanations, correction and reprocessing paths,
  and a human reviewer who remains responsible for final decisions. Autonomous
  settlement, definitive fraud detection, and market-price inference are out of
  scope.
- Evaluation is part of the deliverable: held-out annotated bundles, explicit
  synthetic labels and split hygiene, text-only RAG and direct multimodal
  prompting baselines, and ablations of evidence linking and coded checks.
  Extraction quality, precision/recall, citation correctness, appropriate
  deferral, latency, memory, and reviewer effort are measured rather than
  assumed.

The master brief expands the delivery scope, not these evidence principles.
Insurance-specific mappings and reviewed checks therefore live in M10; the core
uses generic entities, facts, observations, claims, events, conditions,
measurements, evidence, verifications, findings, actions, and source fragments.

## System shape

CrossLens starts as a modular monolith with independently testable modules and
one composition boundary. FastAPI endpoints and Celery tasks invoke module
*public ports*; modules exchange versioned Pydantic contracts and never import
another module's internal implementation. Database drivers, Cypher, Chroma
calls, model SDKs, and file-system paths remain in infrastructure adapters.

```text
React/Vite client
        | explicit HTTP schemas
FastAPI composition layer ---- Celery/Redis job dispatcher
        |                         |
        +----- module public ports and contracts -----+
 M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M7 -> M8 -> M9
                    ^                         ^
                    +------ M10 domain adapters -------+
        |
 relational port | graph port | vector port | file/object port | AI provider ports
        |               |            |               |                 |
 PostgreSQL       Neo4j       ChromaDB       local object store    local runtimes
```

The diagram depicts allowed data flow, not direct implementation imports. M6
may ask M5 for an `EvidenceBundle`, M7 reasons only over the compact bundle and
verification results, and M9 records corrections/audit events that cause a
new, traceable downstream run rather than mutation of historical evidence.

## Core model and provenance

### Identity and versioning

`Workspace` owns logical `Document` records. A new upload of the same logical
document creates a new immutable `DocumentVersion`, linked to a preserved
`SourceAsset` with cryptographic hash, MIME type, storage locator, and ingest
metadata. `SourceFragment` is the atomic citeable unit: it belongs to a version
and may identify a PDF page/bounding box, heading/paragraph/table, spreadsheet
sheet/cell/range/formula, or image region.

Normalised assertions and graph relationships retain their source-fragment
references, confidence, creation actor/processor, timestamp, status, schema
version, and processing-run/version context. Corrections create a new assertion
or superseding relationship and an audit event; they do not overwrite the prior
assertion. Derived items record `DERIVED_FROM` / `EVIDENCED_BY` paths.

### Database-independent evidence graph

The application graph exposes only these operations through `EvidenceGraphPort`:
`create_node`, `update_node`, `create_relationship`, `update_relationship`,
`get_node`, `get_neighbors`, `traverse`, `query_subgraph`, `get_provenance`, and
`get_source_references`. Node and edge validation occurs at this boundary;
Neo4j Cypher is an adapter concern.

Initial node labels are `Workspace`, `Document`, `DocumentVersion`,
`SourceAsset`, `SourceFragment`, `Entity`, `Fact`, `Observation`, `Event`,
`Claim`, `Condition`, `Measurement`, `Evidence`, `Verification`, `Finding`,
`Action`, and `AuditEvent`. Every graph node has an opaque ID, node type,
workspace ID, lifecycle status, contract version, and provenance fields.

Supported relationships include source structure (`CONTAINS`, `HAS_PAGE`,
`HAS_SECTION`, `HAS_TABLE`, `HAS_CELL`, `HAS_IMAGE`, `HAS_FRAGMENT`), semantic
links (`REFERS_TO`, `DESCRIBES`, `MENTIONS`, `ALIAS_OF`, `SAME_AS`), evidence
links (`SUPPORTED_BY`, `EVIDENCED_BY`, `DERIVED_FROM`, `OBSERVED_IN`,
`CITED_BY`), generic/domain links (`INVOLVES`, `OWNS`, `BELONGS_TO`,
`APPLIES_TO`, `GOVERNS`, `REQUIRES`, `EXCLUDES`, `CAUSES`, `OCCURRED_AT`,
`OCCURRED_ON`), verification links (`VERIFIES`, `CONTRADICTS`, `CONFIRMS`,
`DEPENDS_ON`, `REQUIRES_EVIDENCE`), and decision links (`RESULTS_IN`,
`RECOMMENDS`, `REQUIRES_ACTION`, `RESOLVES`).

Every edge has an opaque relationship ID, edge type, source and target IDs,
confidence, source references/provenance, status, creator, timestamp, and
version. Confidence is not proof; a relationship cannot be marked supported
without its evidence references. Ambiguous entity matches remain candidates,
not `SAME_AS` assertions.

## Contracts and ports

`contracts/` will own stable Pydantic DTOs, enums, error/result envelopes, and
versioned port protocols. Stable cross-module data must never be an untyped
dictionary. Proposed groups are:

| Contract group | Primary contracts |
| --- | --- |
| ingestion | `Document`, `DocumentVersion`, `SourceAsset`, `DocumentIngestionRequest`, `DocumentIngestionResult`, `ProcessingJob` |
| extraction | `ExtractionRequest`, `ExtractionResult`, `SourceFragment`, `ExtractedTable`, `ExtractedObservation`, `ExtractionWarning` |
| knowledge | `NormalizedKnowledge`, `Entity`, `Fact`, `Observation`, `Claim`, `Event`, `Condition`, `Measurement`, `EntityResolutionCandidate` |
| graph | `GraphNode`, `GraphRelationship`, `EvidenceGraphUpdate`, `GraphQuery`, `ProvenancePath`, `EvidenceGraphPort` |
| retrieval | `RetrievalRequest`, `RetrievalResult`, `EvidenceBundle`, `VectorStorePort`, `RetrievalStatus` |
| verification | `VerificationRequest`, `VerificationResult`, `VerificationCheck`, `VerificationStatus`, `RuleReference` |
| reasoning | `ReasoningRequest`, `ReasoningResult`, `LLMProvider`, `VLMProvider`, `EmbeddingProvider` |
| outcomes and audit | `Finding`, `Action`, `ReviewCorrection`, `AuditEvent`, `SourceCitation` |
| storage and jobs | `RelationalStore`, `GraphStore`, `VectorStore`, `FileStore`, `JobEvent`, `JobStatus` |

Contract versions are explicit and backward-compatible changes are additive.
Breaking fields require a new contract version and an adapter at the public
boundary. IDs, enums for evidence/verification status, timestamps, and source
citations are typed rather than embedded in prose.

## Storage architecture

- PostgreSQL, behind `RelationalStore`, holds workspaces, document/version and
  job metadata, idempotency keys, configuration references, audit indexes, and
  user/review metadata when authentication is added.
- Neo4j, behind `GraphStore`, persists the provenance-aware evidence graph and
  executes storage-specific traversal. Application modules do not contain
  Cypher.
- ChromaDB, behind `VectorStore`, holds embeddings keyed to immutable
  fragment/assertion/version IDs and metadata filters. Similarity only means
  potentially relevant; its output must be graph- and rule-qualified.
- A configurable `FileStore` preserves original uploads and derived, non-source
  artifacts (for example rendered pages) in local development. Its locator is
  opaque to contracts, enabling S3-compatible storage later.

The synopsis proposed pgvector/full-text search; the current master brief
selects ChromaDB and Neo4j. PostgreSQL full-text is an optional keyword adapter
for Phase 6, while ChromaDB is the vector-store abstraction. Either may change
without changing M5's retrieval contract.

## Local AI architecture

Provider protocols separate capability from vendor/runtime:

- `EmbeddingProvider.embed(texts, model_config)` supports local sentence
  transformers or an Ollama-compatible embedding adapter.
- `LLMProvider.generate_structured(request)` receives only a cited
  `EvidenceBundle` plus verification results and returns schema-validated
  reasoning, uncertainty, and citations.
- `VLMProvider.observe_image(request)` returns structured observations,
  confidence, region references when available, and visibility limitations.

The default target is local, configuration-driven inference (for example,
Ollama or Hugging Face adapters) with model, quantisation, endpoint, context,
and batch limits stored in configuration—not business code. An unsupported or
unavailable model produces a typed unavailable/partial-processing result and
does not fabricate a finding. Deterministic ingestion, extraction where no
model is needed, graph creation, retrieval, and verification remain usable
without paid API keys. Future cloud adapters implement the same protocols and
are optional.

The Phase 0 hardware probe did not yield reliable GPU or memory capability
details, so no model is selected now. Phase 1/3 must profile representative PDFs,
spreadsheets, and images against available CPU/RAM/VRAM, field/observation
quality, latency, licence, and reproducibility before committing a local model.

## Async processing and failure semantics

An upload endpoint validates and persists the source/version and creates an
idempotent `ProcessingJob`. It then dispatches a Celery workflow via Redis:

```text
queued -> ingest_registered -> extracting -> normalizing -> graph_updating
       -> embedding -> verifying -> reasoning -> findings_ready
                                \-> partial | failed | cancelled
```

Each task has an input version, correlation IDs (`workspace_id`, `document_id`,
`document_version_id`, `job_id`, optionally `source_fragment_id`), bounded
retry policy, structured logs, and a durable status event. Tasks publish only
contracts/events; no task reaches into another module's private repository.
Failures are surfaced with a typed error, safe retryability, and completed
artifact references. Downstream stages do not apply incomplete output as if it
were complete. Corrections create a targeted new job based on affected versions
and retain both the original and reprocessed evidence paths.

## Frontend architecture

The React/Vite/Tailwind client is an evidence-review client, not a business
logic host. Typed API client schemas support the following views:

- workspace and document upload/job-state view;
- document/source viewer with page, bounding-box, sheet/cell, or image-region
  citation deep links;
- evidence graph and evidence-neighbourhood visualisation;
- retrieval and verification view that distinguishes relevant, supported,
  contradicted, and insufficient evidence;
- finding/action queue with confidence, uncertainty, cited sources, and
  recommended reviewer action; and
- correction and audit timeline that displays the superseding processing run.

The frontend reads explicit FastAPI resources for workspaces, documents, jobs,
search/retrieval, graph/provenance, verification, findings/actions, review, and
audit. It never queries Neo4j, ChromaDB, or providers directly. Responsive and
loading/error/partial-result states are first-class UI requirements.

## Testing and evaluation strategy

Testing is introduced with each phase rather than deferred to the MVP:

- Unit tests cover pure parsing, normalisation, rule, mapping, and presentation
  transformations.
- Contract tests validate Pydantic compatibility, port conformance, result
  status semantics, and that modules consume public contracts only.
- Adapter integration tests use disposable PostgreSQL, Neo4j, ChromaDB, Redis,
  and worker environments where appropriate.
- End-to-end tests exercise source -> fragment -> assertion -> graph ->
  verification -> finding -> action provenance, including partial/failure and
  correction/reprocessing paths.
- Evaluation uses immutable, documented development/test splits; no related
  image/document leakage; synthetics are labelled; and baseline/ablation runs
  record model/configuration, rule version, source corpus version, latency, and
  resource use.

Core negative tests are mandatory: no source-free finding, no observation
silently promoted to fact, no missing-evidence result labelled contradiction,
no ambiguous entity merge, no vector hit marked verified, and no correction
that destroys historical traceability.

## Sequenced delivery

1. Phase 0: repository audit and this architecture baseline.
2. Phase 1: contracts, configuration, observability, port definitions, and
   development infrastructure foundation.
3. Phase 2: M1 data ingestion.
4. Phase 3: M2 multimodal extraction.
5. Phase 4: M3 knowledge normalisation.
6. Phase 5: M4 evidence graph.
7. Phase 6: M5 hybrid retrieval.
8. Phase 7: M6 deterministic verification.
9. Phase 8: M7 evidence-grounded AI reasoning.
10. Phase 9: M8 insights and actions.
11. Phase 10: M9 human review and audit.
12. Phase 11: M10 domain adapters.
13. Phase 12: frontend integration.
14. Phase 13: end-to-end MVP across one PDF, image, and XLSX plus insurance and
    finance fixtures.
15. Phase 14: evaluation, comparison, ablation, and optimisation.

Each phase ends with an implementation report, test results, known limitations,
risks, next phase, and an approval gate. Work must not advance automatically.

## Open decisions and risks

- The project must profile actual available GPU/RAM and choose reproducible,
  appropriately licensed local models before implementing model adapters.
- Retention, encryption, access control, and authentication policy for sensitive
  source material are not defined. They must be decided before non-synthetic or
  multi-user deployment.
- The initial policy/rule authoring format, domain vocabulary governance, and
  entity-resolution acceptance thresholds need reviewer ownership.
- Neo4j, ChromaDB, PostgreSQL, Redis, and local model runtimes increase local
  development footprint; compose profiles and isolated adapter tests will limit
  the burden.
- OCR/table/VLM quality must be measured on representative scans and images;
  extraction errors must remain warnings and inspectable candidates, never
  silent facts.
- Research claims are conditional on documented evaluation; the product must not
  present a determination as legal, financial, insurance, or fraud judgement.
