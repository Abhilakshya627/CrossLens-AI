"""Canonical, domain-neutral knowledge contracts with explicit evidence status."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field

from contracts.common import Confidence, ContractModel, EvidenceStatus, SourceCitation


class AssertionKind(StrEnum):
    FACT = "fact"
    OBSERVATION = "observation"
    CLAIM = "claim"
    EVENT = "event"
    CONDITION = "condition"
    MEASUREMENT = "measurement"


class Entity(ContractModel):
    entity_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    canonical_name: str = Field(min_length=1, max_length=512)
    entity_type: str = Field(min_length=1, max_length=128)
    aliases: tuple[str, ...] = ()
    citations: tuple[SourceCitation, ...] = ()


class KnowledgeAssertion(ContractModel):
    assertion_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    subject_entity_id: str | None = Field(default=None, max_length=128)
    statement: str = Field(min_length=1, max_length=8_000)
    status: EvidenceStatus = EvidenceStatus.UNASSESSED
    confidence: Confidence | None = None
    citations: tuple[SourceCitation, ...] = Field(min_length=1)


class Fact(KnowledgeAssertion):
    kind: Literal[AssertionKind.FACT] = AssertionKind.FACT


class Observation(KnowledgeAssertion):
    """A source-bound observation, never an automatically verified fact."""

    kind: Literal[AssertionKind.OBSERVATION] = AssertionKind.OBSERVATION
    visibility_limitations: tuple[str, ...] = ()


class Claim(KnowledgeAssertion):
    kind: Literal[AssertionKind.CLAIM] = AssertionKind.CLAIM


class Event(KnowledgeAssertion):
    kind: Literal[AssertionKind.EVENT] = AssertionKind.EVENT


class Condition(KnowledgeAssertion):
    kind: Literal[AssertionKind.CONDITION] = AssertionKind.CONDITION


class Measurement(KnowledgeAssertion):
    kind: Literal[AssertionKind.MEASUREMENT] = AssertionKind.MEASUREMENT
    value: str = Field(min_length=1, max_length=256)
    unit: str | None = Field(default=None, max_length=128)


class EntityResolutionCandidate(ContractModel):
    candidate_id: str = Field(min_length=1, max_length=128)
    source_entity_id: str = Field(min_length=1, max_length=128)
    target_entity_id: str = Field(min_length=1, max_length=128)
    confidence: Confidence
    is_accepted: bool = False
    citations: tuple[SourceCitation, ...] = Field(min_length=1)


class NormalizedKnowledge(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    entities: tuple[Entity, ...] = ()
    facts: tuple[Fact, ...] = ()
    observations: tuple[Observation, ...] = ()
    claims: tuple[Claim, ...] = ()
    events: tuple[Event, ...] = ()
    conditions: tuple[Condition, ...] = ()
    measurements: tuple[Measurement, ...] = ()
    resolution_candidates: tuple[EntityResolutionCandidate, ...] = ()

