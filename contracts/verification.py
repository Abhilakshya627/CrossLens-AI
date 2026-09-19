"""Contracts for deterministic, versioned checks over an EvidenceBundle."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from contracts.common import ContractModel, SourceCitation
from contracts.retrieval import EvidenceBundle


class VerificationStatus(StrEnum):
    SATISFIED = "satisfied"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NOT_APPLICABLE = "not_applicable"
    FAILED = "failed"


class RuleReference(ContractModel):
    rule_id: str = Field(min_length=1, max_length=128)
    rule_version: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=2_000)


class VerificationRequest(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    evidence_bundle: EvidenceBundle
    rule_references: tuple[RuleReference, ...] = Field(min_length=1)


class VerificationCheck(ContractModel):
    check_id: str = Field(min_length=1, max_length=128)
    rule_reference: RuleReference
    status: VerificationStatus
    explanation: str = Field(min_length=1, max_length=4_000)
    source_references: tuple[SourceCitation, ...] = ()
    missing_evidence: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence_semantics(self) -> "VerificationCheck":
        if self.status in {VerificationStatus.SATISFIED, VerificationStatus.CONTRADICTED}:
            if not self.source_references:
                raise ValueError("satisfied and contradicted checks require source references")
        if self.status is VerificationStatus.INSUFFICIENT_EVIDENCE and not self.missing_evidence:
            raise ValueError("insufficient evidence checks must name missing evidence")
        return self


class VerificationResult(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    verification_id: str = Field(min_length=1, max_length=128)
    checks: tuple[VerificationCheck, ...] = Field(min_length=1)

