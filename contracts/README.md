# Shared Contracts

## Purpose

`contracts/` is the only shared vocabulary for CrossLens modules. It contains
immutable, versioned Pydantic DTOs and public infrastructure/provider ports.
It contains no database driver, model SDK, domain rule, or module-private logic.

## Public interface

- `common.py`: provenance, citations, confidence, lifecycle state, and typed
  attributes.
- `ingestion.py`, `extraction.py`, `knowledge.py`, `graph.py`, `retrieval.py`,
  `verification.py`, `reasoning.py`, `outcomes.py`, and `audit.py`: the public
  payloads named in the architecture.
- `ports.py`: graph, vector, relational, file-store, LLM, VLM, and embedding
  protocols implemented only by infrastructure adapters.
- `system.py`: system-level HTTP response schemas.

## Invariants

- Stable cross-module payloads cannot contain arbitrary metadata dictionaries.
- Evidence-bearing relationships, completed reasoning, and findings require
  citeable source fragments.
- Every citation must identify a concrete page, section, cell/range, bounding
  box, or image-region anchor.
- An observation has an observation type; it cannot be retyped as a fact.
- Insufficient-evidence checks must state the missing evidence.

## Dependencies and tests

The package depends on Pydantic only. Contract invariants are tested in
`tests/contracts/`; module-specific contract tests are added alongside the
corresponding module in later phases.
