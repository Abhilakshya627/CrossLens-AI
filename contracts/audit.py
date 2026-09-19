"""Append-only human-review and audit contracts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from contracts.common import ActorType, ContractModel, SourceCitation, utc_now


class ReviewDecision(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    DEFER = "defer"
    CORRECT = "correct"


class ReviewCorrection(ContractModel):
    correction_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    target_id: str = Field(min_length=1, max_length=128)
    superseding_id: str | None = Field(default=None, max_length=128)
    decision: ReviewDecision
    rationale: str = Field(min_length=1, max_length=4_000)
    reviewer_id: str = Field(min_length=1, max_length=128)
    source_references: tuple[SourceCitation, ...] = ()
    created_at: datetime = Field(default_factory=utc_now)


class AuditEvent(ContractModel):
    event_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=128)
    actor_id: str = Field(min_length=1, max_length=128)
    actor_type: ActorType
    affected_ids: tuple[str, ...] = Field(min_length=1)
    correction_id: str | None = Field(default=None, max_length=128)
    created_at: datetime = Field(default_factory=utc_now)

