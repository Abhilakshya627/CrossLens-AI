from __future__ import annotations

import pytest
from pydantic import ValidationError

from contracts.common import ActorType, Confidence, Provenance, SourceCitation, SourceLocation
from contracts.graph import GraphRelationship, RelationshipType
from contracts.knowledge import AssertionKind, Observation
from contracts.outcomes import Finding
from contracts.verification import RuleReference, VerificationCheck, VerificationStatus


def citation() -> SourceCitation:
    return SourceCitation(
        workspace_id="workspace-1",
        document_id="document-1",
        document_version_id="version-1",
        source_fragment_id="fragment-1",
        location=SourceLocation(page_number=1),
        excerpt="Visible damage is limited to the photographed area.",
    )


def provenance() -> Provenance:
    return Provenance(created_by="test-worker", actor_type=ActorType.WORKER)


def test_source_citation_requires_a_location_anchor() -> None:
    with pytest.raises(ValidationError, match="citeable source location"):
        SourceCitation(
            workspace_id="workspace-1",
            document_id="document-1",
            document_version_id="version-1",
            source_fragment_id="fragment-1",
            location=SourceLocation(),
        )


def test_observation_cannot_be_retyped_as_a_fact() -> None:
    with pytest.raises(ValidationError):
        Observation(
            assertion_id="observation-1",
            workspace_id="workspace-1",
            statement="Visible scratch on front bumper.",
            citations=(citation(),),
            kind=AssertionKind.FACT,
        )


def test_evidence_relationship_requires_a_source_reference() -> None:
    with pytest.raises(ValidationError, match="require source references"):
        GraphRelationship(
            relationship_id="relationship-1",
            workspace_id="workspace-1",
            relationship_type=RelationshipType.SUPPORTED_BY,
            source_node_id="claim-1",
            target_node_id="observation-1",
            status="active",
            confidence=Confidence(score=0.8, method="reviewed-rule"),
            provenance=provenance(),
            version=1,
        )


def test_insufficient_evidence_is_not_a_contradiction() -> None:
    with pytest.raises(ValidationError, match="must name missing evidence"):
        VerificationCheck(
            check_id="check-1",
            rule_reference=RuleReference(
                rule_id="rule-1", rule_version="1.0", description="Requires photograph."
            ),
            status=VerificationStatus.INSUFFICIENT_EVIDENCE,
            explanation="No image shows the relevant vehicle component.",
        )


def test_finding_cannot_exist_without_a_source_reference() -> None:
    with pytest.raises(ValidationError):
        Finding(
            finding_id="finding-1",
            workspace_id="workspace-1",
            title="Unsupported repair item",
            summary="The source bundle lacks evidence for the listed item.",
            evidence_status="insufficient_evidence",
        )
