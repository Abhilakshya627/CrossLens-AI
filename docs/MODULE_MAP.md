# CrossLens AI Module Map

## Boundary rules

Each module owns its domain logic and infrastructure adapters. A module may
import `contracts` and another module's documented public port only; it may not
import a sibling's `application`, `domain`, `infrastructure`, or private parser/
repository implementation. The FastAPI/Celery composition layer wires adapters
to ports. `M10_Domain_Adapters` contributes mappings, vocabularies, rule
packages, and UI labels through contracts; core modules do not import
insurance-, finance-, or other domain-specific types.

Future module directories will contain a concise README, `__init__.py`, and
only necessary `api`, `application`, `domain`, `infrastructure`, and `tests`
subdirectories. This phase creates none of them.

## Module ownership and public outputs

| Module | Owns | Public inputs | Public outputs | Must not own |
| --- | --- | --- | --- | --- |
| M1_Data_Ingestion | upload validation, MIME/hash, document/version/source registration, preservation, job creation/status | upload request, workspace ID | `DocumentIngestionResult`, `DocumentVersion`, `SourceAsset`, `ProcessingJob` | document understanding or claims reasoning |
| M2_Multimodal_Extraction | PDF/DOCX/XLSX/CSV/TXT/image extraction, OCR routing, layout/table/cell/region locations, warnings | document version/source asset | `ExtractionResult`, `SourceFragment`, `ExtractedTable`, `ExtractedObservation` | declaring observations as facts or domain decisions |
| M3_Knowledge_Normalization | canonical records, aliases, unit/date/identifier normalisation, candidate entity resolution | extraction result, adapter vocabulary | `NormalizedKnowledge`, typed knowledge assertions/candidates | graph persistence, verification outcomes |
| M4_Evidence_Graph | application evidence graph validation, provenance traversal, graph updates | graph updates, graph queries | graph/provenance responses through `EvidenceGraphPort` | Neo4j-specific APIs in callers or LLM decisions |
| M5_Hybrid_Retrieval | metadata, keyword, vector, graph retrieval, ranking, compact evidence bundles | `RetrievalRequest`, graph/vector ports | `RetrievalResult`, `EvidenceBundle` | treating relevance as verification |
| M6_Verification | versioned deterministic checks, arithmetic/date/identifier/evidence sufficiency evaluation | verification request, evidence bundle, reviewed rule reference | `VerificationResult` | unreviewed legal/financial/insurance determinations or free-form LLM inference |
| M7_AI_Reasoning | evidence-constrained local-model prompt/response orchestration and structured grounding checks | reasoning request, evidence bundle, verification results | `ReasoningResult` | persistent truth, source-free answers, provider SDK leakage |
| M8_Insights_Actions | convert qualified results into findings, actions, and review recommendations | reasoning/verification results | `Finding`, `Action` | editing source evidence or final human decisions |
| M9_Human_Review_Audit | reviewer corrections, approvals/deferrals, audit history, targeted reprocessing request | correction/review request, affected IDs | `ReviewCorrection`, `AuditEvent`, reprocessing event | erasing historical evidence |
| M10_Domain_Adapters | versioned domain ontology/mappings, rule-pack registration, fixture/evaluation vocabulary | generic knowledge/evidence contracts | adapter and rule-pack contracts | generic graph/retrieval provider logic |

## Allowed communication map

```text
M1 --DocumentIngestionResult--> M2 --ExtractionResult--> M3
M3 --NormalizedKnowledge/EvidenceGraphUpdate--> M4
M4 --graph/provenance port--> M5 --EvidenceBundle--> M6
                                          |               |
                                          +--> M7 <-------+
                                                 |
                                    ReasoningResult / VerificationResult
                                                 v
                                                M8
                                                 v
                                                M9

M10 supplies versioned mapping/rule contracts to M3, M6, M8 and frontend labels.
contracts and infrastructure ports are shared foundations, not bypass channels.
```

M5 can use both M4's public graph port and a vector-store port. M6 can request
a fresh bundle from M5 but does not traverse a database itself. M7 can consume
M5/M6 contracts and provider ports, but cannot create graph facts. M8 always
attaches source citations supplied by upstream contracts. M9 emits correction
and reprocessing events through the composition layer rather than mutating M2-
M8 state directly.

## Shared packages

| Package | Responsibility |
| --- | --- |
| `contracts/` | Versioned Pydantic schemas, enums, error envelopes, provider/storage port protocols, and public module interfaces. |
| `infrastructure/` | Dependency-injection composition, configuration, logging, database/client adapters, file-store adapter, FastAPI/Celery bootstrap, and Docker support. It contains no cross-module business policy. |
| `Frontend/` | React/Vite/Tailwind typed client, views, source/provenance navigation, and UI-state logic only. |
| `docs/` | Architectural memory, phase state, module documentation, decision records, and evaluation protocol. |

## Processing and data ownership map

| Data item | Authoritative owner | Immutable/corrected behaviour |
| --- | --- | --- |
| Original asset and hash | M1 + `FileStore` | Preserve original asset; a changed upload becomes a new document version. |
| Fragment and extraction warning | M2 | Retain coordinates and processing-run provenance; re-extraction creates a new result/version. |
| Normalised assertion/candidate | M3 | Keep ambiguity as a candidate; correction supersedes rather than overwrites. |
| Graph node/relationship | M4 | Require typed provenance and relationship status/version. |
| Embedding/vector metadata | M5 adapter | Key to immutable fragment/assertion/version IDs; regenerate only for a new version/config. |
| Check outcome | M6 | Include rule version, evidence references, and status. |
| Finding/action | M8 | Link all evidence and verification dependencies. |
| Human decision/correction | M9 | Append an audit event and dispatch scoped reprocessing. |

## API resource boundary

FastAPI will expose contracts, rather than datastore entities, around:
`/workspaces`, `/documents`, `/uploads`, `/jobs`, `/search`, `/retrieval`,
`/graph`, `/verification`, `/findings`, `/actions`, `/review`, and `/audit`.
Authentication and authorization are intentionally uncommitted until a data
policy is selected. A future mobile or desktop client consumes the same API.
