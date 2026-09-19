"""Database-independent Evidence Graph contracts and query shapes."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from contracts.common import Confidence, ContractModel, Provenance, SourceCitation, TypedAttribute


class GraphNodeType(StrEnum):
    WORKSPACE = "workspace"
    DOCUMENT = "document"
    DOCUMENT_VERSION = "document_version"
    SOURCE_ASSET = "source_asset"
    SOURCE_FRAGMENT = "source_fragment"
    ENTITY = "entity"
    FACT = "fact"
    OBSERVATION = "observation"
    EVENT = "event"
    CLAIM = "claim"
    CONDITION = "condition"
    MEASUREMENT = "measurement"
    EVIDENCE = "evidence"
    VERIFICATION = "verification"
    FINDING = "finding"
    ACTION = "action"
    AUDIT_EVENT = "audit_event"


class RelationshipType(StrEnum):
    CONTAINS = "contains"
    HAS_PAGE = "has_page"
    HAS_SECTION = "has_section"
    HAS_TABLE = "has_table"
    HAS_CELL = "has_cell"
    HAS_IMAGE = "has_image"
    HAS_FRAGMENT = "has_fragment"
    REFERS_TO = "refers_to"
    DESCRIBES = "describes"
    MENTIONS = "mentions"
    ALIAS_OF = "alias_of"
    SAME_AS = "same_as"
    SUPPORTED_BY = "supported_by"
    EVIDENCED_BY = "evidenced_by"
    DERIVED_FROM = "derived_from"
    OBSERVED_IN = "observed_in"
    CITED_BY = "cited_by"
    INVOLVES = "involves"
    OWNS = "owns"
    BELONGS_TO = "belongs_to"
    APPLIES_TO = "applies_to"
    GOVERNS = "governs"
    REQUIRES = "requires"
    EXCLUDES = "excludes"
    CAUSES = "causes"
    OCCURRED_AT = "occurred_at"
    OCCURRED_ON = "occurred_on"
    VERIFIES = "verifies"
    CONTRADICTS = "contradicts"
    CONFIRMS = "confirms"
    DEPENDS_ON = "depends_on"
    REQUIRES_EVIDENCE = "requires_evidence"
    RESULTS_IN = "results_in"
    RECOMMENDS = "recommends"
    REQUIRES_ACTION = "requires_action"
    RESOLVES = "resolves"


EVIDENCE_BEARING_RELATIONSHIPS = frozenset(
    {
        RelationshipType.SUPPORTED_BY,
        RelationshipType.EVIDENCED_BY,
        RelationshipType.DERIVED_FROM,
        RelationshipType.OBSERVED_IN,
        RelationshipType.CONTRADICTS,
        RelationshipType.CONFIRMS,
    }
)


class GraphNode(ContractModel):
    node_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    node_type: GraphNodeType
    status: str = Field(min_length=1, max_length=128)
    attributes: tuple[TypedAttribute, ...] = ()
    provenance: Provenance
    source_references: tuple[SourceCitation, ...] = ()
    version: int = Field(ge=1)


class GraphRelationship(ContractModel):
    relationship_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    relationship_type: RelationshipType
    source_node_id: str = Field(min_length=1, max_length=128)
    target_node_id: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=128)
    confidence: Confidence | None = None
    provenance: Provenance
    source_references: tuple[SourceCitation, ...] = ()
    version: int = Field(ge=1)

    @model_validator(mode="after")
    def require_sources_for_evidence_relationships(self) -> "GraphRelationship":
        if self.relationship_type in EVIDENCE_BEARING_RELATIONSHIPS and not self.source_references:
            raise ValueError("evidence-bearing relationships require source references")
        return self


class EvidenceGraphUpdate(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    nodes_to_create: tuple[GraphNode, ...] = ()
    nodes_to_update: tuple[GraphNode, ...] = ()
    relationships_to_create: tuple[GraphRelationship, ...] = ()
    relationships_to_update: tuple[GraphRelationship, ...] = ()


class GraphTraversalQuery(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    start_node_id: str = Field(min_length=1, max_length=128)
    relationship_types: tuple[RelationshipType, ...] = ()
    max_depth: int = Field(default=2, ge=1, le=6)
    max_nodes: int = Field(default=100, ge=1, le=500)


class ProvenancePath(ContractModel):
    node_ids: tuple[str, ...] = Field(min_length=1)
    relationship_ids: tuple[str, ...] = ()
    source_references: tuple[SourceCitation, ...] = Field(min_length=1)


class GraphQueryResult(ContractModel):
    nodes: tuple[GraphNode, ...]
    relationships: tuple[GraphRelationship, ...]
    provenance_paths: tuple[ProvenancePath, ...] = ()

