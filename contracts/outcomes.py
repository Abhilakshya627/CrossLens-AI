"""Contracts for evidence-cited findings and reviewer-facing actions."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from contracts.common import Confidence, ContractModel, EvidenceStatus, SourceCitation


class FindingStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    DEFERRED = "deferred"
    SUPERSEDED = "superseded"


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


class Finding(ContractModel):
    finding_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=512)
    summary: str = Field(min_length=1, max_length=8_000)
    evidence_status: EvidenceStatus
    status: FindingStatus = FindingStatus.OPEN
    verification_ids: tuple[str, ...] = ()
    reasoning_id: str | None = Field(default=None, max_length=128)
    source_references: tuple[SourceCitation, ...] = Field(min_length=1)
    uncertainty: tuple[str, ...] = ()
    confidence: Confidence | None = None


class Action(ContractModel):
    action_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    finding_id: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=4_000)
    status: ActionStatus = ActionStatus.PROPOSED
    source_references: tuple[SourceCitation, ...] = Field(min_length=1)

