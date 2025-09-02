#!/usr/bin/env python3
"""
Glacier Spore Models - Pydantic-Driven Architecture

The models ARE the code. Everything is defined through Pydantic models
with semantic validation, automatic serialization, and model-driven behavior.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, computed_field, model_validator, validator
from pydantic.json import pydantic_encoder


class SporeType(str, Enum):
    """Types of glacier spores - semantic classification"""

    DISCOVERY = "discovery"  # Repository discovery
    ANALYSIS = "analysis"  # Code analysis
    METRIC = "metric"  # Quality/metrics
    PATTERN = "pattern"  # Detected patterns
    RELATIONSHIP = "relationship"  # Relationship data
    TRIGGER = "trigger"  # Processing trigger
    EVENT = "event"  # System events
    DIMENSION = "dimension"  # Dimension definition
    SCHEMA = "schema"  # Schema definition
    PROCESSOR = "processor"  # Processor definition


class DimensionType(str, Enum):
    """Types of dimensions - semantic classification"""

    TEMPORAL = "temporal"  # Time-based
    SPATIAL = "spatial"  # Location-based
    SEMANTIC = "semantic"  # Meaning-based
    STRUCTURAL = "structural"  # Code structure
    QUALITY = "quality"  # Quality metrics
    SECURITY = "security"  # Security aspects
    PERFORMANCE = "performance"  # Performance metrics
    DEPENDENCY = "dependency"  # Dependencies
    ARCHITECTURE = "architecture"  # Architecture patterns
    TECHNOLOGY = "technology"  # Technology stack


class SyncStrategy(str, Enum):
    """Synchronization strategies - semantic behavior"""

    LAST_UPDATE_WINS = "last_update_wins"
    MERGE_CONFLICTS = "merge_conflicts"
    MANUAL_RESOLUTION = "manual_resolution"
    TIMESTAMP_BASED = "timestamp_based"
    VERSION_BASED = "version_based"


class ConflictResolution(str, Enum):
    """Conflict resolution methods - semantic behavior"""

    ACCEPT_LOCAL = "accept_local"
    ACCEPT_REMOTE = "accept_remote"
    MERGE = "merge"
    MANUAL = "manual"
    REJECT = "reject"


class ModelVersion(BaseModel):
    """Model version metadata - semantic versioning"""

    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_hash: str = Field(..., description="SHA256 hash of model content")
    parent_version_id: Optional[str] = Field(None, description="Parent version for lineage")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(default="system", description="Who created this version")

    # Change metadata - semantic tracking
    change_count: int = Field(default=0, ge=0, description="Number of semantic changes")
    change_types: set[str] = Field(default_factory=set, description="Types of semantic changes")

    # Synchronization metadata - semantic state
    sync_status: str = Field(default="pending", description="Current sync state")
    last_sync: Optional[datetime] = Field(None, description="Last synchronization time")
    conflicts: list[str] = Field(default_factory=list, description="Semantic conflicts found")

    # Computed fields - derived from model state
    @computed_field
    @property
    def is_current(self) -> bool:
        """Is this the current version?"""
        return self.sync_status == "current"

    @computed_field
    @property
    def has_conflicts(self) -> bool:
        """Are there unresolved conflicts?"""
        return len(self.conflicts) > 0

    @computed_field
    @property
    def change_summary(self) -> str:
        """Human-readable change summary"""
        if self.change_count == 0:
            return "No changes"
        types_str = ", ".join(sorted(self.change_types))
        return f"{self.change_count} changes: {types_str}"

    # Validation - semantic rules
    @validator("model_hash")
    def validate_model_hash(self, v):
        """Validate model hash format"""
        if not v or len(v) != 64:  # SHA256 is 64 hex chars
            msg = "Model hash must be a valid SHA256 hash"
            raise ValueError(msg)
        return v

    @validator("change_types")
    def validate_change_types(self, v):
        """Validate change types are semantic"""
        semantic_types = {
            "spore_created",
            "spore_updated",
            "spore_deleted",
            "dimension_added",
            "dimension_modified",
            "dimension_removed",
            "relationship_changed",
            "schema_evolved",
            "quality_improved",
        }
        invalid_types = v - semantic_types
        if invalid_types:
            msg = f"Invalid change types: {invalid_types}"
            raise ValueError(msg)
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True


class Dimension(BaseModel):
    """A dimension in the glacier spore system - semantic definition"""

    dimension_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dimension_type: DimensionType = Field(..., description="Semantic type of dimension")
    name: str = Field(..., min_length=1, description="Human-readable dimension name")
    description: str = Field(..., min_length=1, description="Semantic description")

    # Dimensional properties - semantic constraints
    cardinality: Optional[int] = Field(None, ge=0, description="Number of distinct semantic values")
    range_min: Optional[Union[int, float, str]] = Field(None, description="Minimum semantic value")
    range_max: Optional[Union[int, float, str]] = Field(None, description="Maximum semantic value")
    unit: Optional[str] = Field(None, description="Semantic unit of measurement")

    # Metadata - semantic context
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: set[str] = Field(default_factory=set, description="Semantic tags")

    # Relationships - semantic connections
    parent_dimension_id: Optional[str] = Field(None, description="Parent dimension for hierarchy")
    child_dimension_ids: list[str] = Field(default_factory=list, description="Child dimensions")

    # Usage tracking - semantic usage patterns
    usage_count: int = Field(default=0, ge=0, description="Number of semantic usages")
    last_used: Optional[datetime] = Field(None, description="Last semantic usage")

    # Computed fields - derived semantic properties
    @computed_field
    @property
    def is_leaf(self) -> bool:
        """Is this a leaf dimension (no children)?"""
        return len(self.child_dimension_ids) == 0

    @computed_field
    @property
    def is_root(self) -> bool:
        """Is this a root dimension (no parent)?"""
        return self.parent_dimension_id is None

    @computed_field
    @property
    def semantic_complexity(self) -> float:
        """Semantic complexity score based on properties"""
        complexity = 0.0

        if self.cardinality:
            complexity += min(self.cardinality / 100, 1.0)

        if self.range_min is not None and self.range_max is not None:
            if isinstance(self.range_min, (int, float)) and isinstance(self.range_max, (int, float)):
                range_size = abs(self.range_max - self.range_min)
                complexity += min(range_size / 1000, 1.0)

        if self.unit:
            complexity += 0.2

        complexity += len(self.tags) * 0.1

        return min(complexity, 1.0)

    # Validation - semantic rules
    @validator("name")
    def validate_name(self, v):
        """Validate dimension name is semantic"""
        if not v.replace("_", "").replace("-", "").isalnum():
            msg = "Dimension name must be alphanumeric with underscores or hyphens"
            raise ValueError(msg)
        return v

    @validator("range_min", "range_max")
    def validate_range(self, v, values):
        """Validate range constraints are semantically valid"""
        if "range_min" in values and "range_max" in values:
            min_val = values["range_min"]
            max_val = values["range_max"]
            if min_val is not None and max_val is not None:
                if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
                    if min_val >= max_val:
                        msg = "Range min must be less than range max"
                        raise ValueError(msg)
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True


class SemanticDiff(BaseModel):
    """Semantic difference between two states - not artifact diffs"""

    diff_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    field_path: str = Field(..., description="Semantic path to changed field")
    change_type: str = Field(..., description="Type of semantic change")

    # Semantic change details
    old_semantic_value: Optional[Any] = Field(None, description="Previous semantic meaning")
    new_semantic_value: Optional[Any] = Field(None, description="New semantic meaning")

    # Semantic context
    semantic_context: dict[str, Any] = Field(default_factory=dict, description="Semantic context")
    impact_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Semantic impact score")

    # Metadata
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in semantic change")

    # Computed fields
    @computed_field
    @property
    def is_breaking_change(self) -> bool:
        """Is this a breaking semantic change?"""
        return self.impact_score > 0.7

    @computed_field
    @property
    def semantic_summary(self) -> str:
        """Human-readable semantic change summary"""
        return f"{self.change_type} at {self.field_path}: {self.impact_score:.2f} impact"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True


class GlacierSpore(BaseModel):
    """A glacier spore - self-describing message with embedded semantic schemata"""

    # Core identification
    spore_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    spore_type: SporeType = Field(..., description="Semantic type of spore")
    content_hash: str = Field(..., description="SHA256 hash of semantic content")

    # Self-describing schemata - semantic definitions
    embedded_schema: dict[str, Any] = Field(..., description="Schema that describes this spore semantically")
    content_schema: dict[str, Any] = Field(..., description="Schema for semantic content")

    # Content and data - semantic payload
    content: dict[str, Any] = Field(..., description="Semantic content payload")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Semantic metadata")

    # Dimensional vectors - semantic dimensions
    dimensions: dict[str, Any] = Field(default_factory=dict, description="Semantic dimension values")
    dimension_refs: list[str] = Field(default_factory=list, description="Referenced semantic dimensions")

    # Processing instructions - semantic behavior
    processing_triggers: list[str] = Field(default_factory=list, description="Semantic processing triggers")
    processor_requirements: dict[str, Any] = Field(default_factory=dict, description="Semantic processor requirements")

    # Relationships - semantic connections
    parent_spore_id: Optional[str] = Field(None, description="Parent spore for semantic hierarchy")
    child_spore_ids: list[str] = Field(default_factory=list, description="Child spores")
    related_spore_ids: list[str] = Field(default_factory=list, description="Semantically related spores")

    # Temporal metadata - semantic timing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(None, description="Semantic expiration time")
    last_processed: Optional[datetime] = Field(None, description="Last semantic processing")

    # Processing state - semantic state
    processed: bool = Field(default=False, description="Semantic processing status")
    processing_errors: list[str] = Field(default_factory=list, description="Semantic processing errors")
    processing_history: list[dict[str, Any]] = Field(default_factory=list, description="Semantic processing history")

    # Integrity and validation - semantic integrity
    validation_checksum: Optional[str] = Field(None, description="Semantic validation checksum")
    signature: Optional[str] = Field(None, description="Semantic signature")

    # Computed fields - derived semantic properties
    @computed_field
    @property
    def semantic_complexity(self) -> float:
        """Semantic complexity based on content and relationships"""
        complexity = 0.0

        # Content complexity
        if isinstance(self.content, dict):
            complexity += len(self.content) * 0.1

        # Relationship complexity
        complexity += len(self.child_spore_ids) * 0.2
        complexity += len(self.related_spore_ids) * 0.1

        # Dimension complexity
        complexity += len(self.dimensions) * 0.15

        return min(complexity, 1.0)

    @computed_field
    @property
    def semantic_health_score(self) -> float:
        """Semantic health score based on various factors"""
        health = 1.0

        # Processing errors reduce health
        health -= len(self.processing_errors) * 0.1

        # Missing required fields reduce health
        if not self.content:
            health -= 0.3

        if not self.embedded_schema:
            health -= 0.2

        # Expired spores have reduced health
        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            health -= 0.5

        return max(health, 0.0)

    @computed_field
    @property
    def semantic_summary(self) -> str:
        """Human-readable semantic summary"""
        return f"{self.spore_type.value} spore: {self.semantic_complexity:.2f} complexity, {self.semantic_health_score:.2f} health"

    # Methods - semantic behavior
    def get_dimension_value(self, dimension_name: str) -> Optional[Any]:
        """Get semantic value for a specific dimension"""
        return self.dimensions.get(dimension_name)

    def set_dimension_value(self, dimension_name: str, value: Any):
        """Set semantic value for a specific dimension"""
        self.dimensions[dimension_name] = value

    def add_processing_trigger(self, trigger_id: str):
        """Add a semantic processing trigger"""
        if trigger_id not in self.processing_triggers:
            self.processing_triggers.append(trigger_id)

    def validate_semantic_integrity(self) -> bool:
        """Validate semantic integrity of the spore"""
        # Check content hash
        content_str = json.dumps(self.content, sort_keys=True, default=pydantic_encoder)
        calculated_hash = hashlib.sha256(content_str.encode()).hexdigest()

        if calculated_hash != self.content_hash:
            return False

        # Check validation checksum if present
        if self.validation_checksum:
            # Additional semantic validation logic here
            pass

        return True

    def create_semantic_diff(self, other: "GlacierSpore") -> list[SemanticDiff]:
        """Create semantic diffs between this spore and another"""
        diffs = []

        # Compare content semantically
        for key in set(self.content.keys()) | set(other.content.keys()):
            if key not in self.content:
                # Key added
                diff = SemanticDiff(
                    field_path=f"content.{key}",
                    change_type="semantic_addition",
                    new_semantic_value=other.content[key],
                    impact_score=0.3,
                )
                diffs.append(diff)
            elif key not in other.content:
                # Key removed
                diff = SemanticDiff(
                    field_path=f"content.{key}",
                    change_type="semantic_removal",
                    old_semantic_value=self.content[key],
                    impact_score=0.5,
                )
                diffs.append(diff)
            elif self.content[key] != other.content[key]:
                # Value changed
                diff = SemanticDiff(
                    field_path=f"content.{key}",
                    change_type="semantic_modification",
                    old_semantic_value=self.content[key],
                    new_semantic_value=other.content[key],
                    impact_score=0.4,
                )
                diffs.append(diff)

        return diffs

    # Validation - semantic rules
    @validator("content_hash")
    def validate_content_hash(self, v):
        """Validate content hash format"""
        if not v or len(v) != 64:
            msg = "Content hash must be a valid SHA256 hash"
            raise ValueError(msg)
        return v

    @validator("embedded_schema")
    def validate_embedded_schema(self, v):
        """Validate embedded schema has required semantic fields"""
        if not isinstance(v, dict):
            msg = "Embedded schema must be a dictionary"
            raise ValueError(msg)

        required_fields = ["type", "version"]
        for field in required_fields:
            if field not in v:
                msg = f"Embedded schema missing required field: {field}"
                raise ValueError(msg)

        return v

    @model_validator(mode="after")
    def validate_semantic_consistency(self) -> "GlacierSpore":
        """Validate semantic consistency across the spore"""
        spore_type = self.spore_type
        content = self.content

        # Type-specific semantic validation
        if spore_type == SporeType.DISCOVERY:
            if "repo_name" not in content:
                msg = "Discovery spores must have repo_name in content"
                raise ValueError(msg)

        elif spore_type == SporeType.ANALYSIS:
            if "analysis_type" not in content:
                msg = "Analysis spores must have analysis_type in content"
                raise ValueError(msg)

        return self

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True
        arbitrary_types_allowed = True


class ChangeLog(BaseModel):
    """Log of semantic changes for model synchronization"""

    change_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    spore_id: str = Field(..., description="ID of affected spore")
    version_id: str = Field(..., description="Model version containing this change")
    change_type: str = Field(..., description="Type of semantic change")
    change_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Semantic change details
    field_name: Optional[str] = Field(None, description="Semantic field that changed")
    old_semantic_value: Optional[Any] = Field(None, description="Previous semantic value")
    new_semantic_value: Optional[Any] = Field(None, description="New semantic value")

    # Semantic metadata
    change_hash: str = Field(default="", description="Hash of semantic change")
    conflict_resolved: bool = Field(default=False, description="Semantic conflict resolution status")
    resolution_method: Optional[str] = Field(None, description="Method used to resolve semantic conflict")

    # Computed fields
    @computed_field
    @property
    def is_semantic_change(self) -> bool:
        """Is this a semantic change (not just artifact change)?"""
        semantic_types = {
            "semantic_addition",
            "semantic_removal",
            "semantic_modification",
            "semantic_relationship_change",
            "semantic_schema_evolution",
        }
        return self.change_type in semantic_types

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True


class SyncOperation(BaseModel):
    """Semantic synchronization operation"""

    sync_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str = Field(..., description="Type of sync operation")
    source_version_id: str = Field(..., description="Source model version")
    target_version_id: str = Field(..., description="Target model version")

    # Semantic operation details
    strategy: SyncStrategy = Field(..., description="Semantic sync strategy")
    conflict_resolution: ConflictResolution = Field(..., description="Semantic conflict resolution")

    # Status - semantic state
    status: str = Field(default="pending", description="Current semantic status")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(None, description="Completion time")

    # Results - semantic outcomes
    conflicts_found: int = Field(default=0, ge=0, description="Semantic conflicts found")
    conflicts_resolved: int = Field(default=0, ge=0, description="Semantic conflicts resolved")
    changes_applied: int = Field(default=0, ge=0, description="Semantic changes applied")
    errors: list[str] = Field(default_factory=list, description="Semantic errors")

    # Computed fields
    @computed_field
    @property
    def is_complete(self) -> bool:
        """Is the sync operation complete?"""
        return self.status in ["completed", "failed"]

    @computed_field
    @property
    def success_rate(self) -> float:
        """Success rate of semantic conflict resolution"""
        if self.conflicts_found == 0:
            return 1.0
        return self.conflicts_resolved / self.conflicts_found

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True


# Example usage and testing
def main():
    """Example usage of the Pydantic-driven glacier spore models"""

    print("🏔️ Glacier Spore Models - Pydantic-Driven Architecture")
    print("=" * 60)

    # Create a dimension
    quality_dimension = Dimension(
        dimension_type=DimensionType.QUALITY,
        name="code_quality_score",
        description="Semantic code quality assessment score",
        range_min=0.0,
        range_max=100.0,
        unit="percentage",
        tags={"quality", "assessment", "metrics"},
    )

    print(f"Created dimension: {quality_dimension.name}")
    print(f"Semantic complexity: {quality_dimension.semantic_complexity:.2f}")
    print(f"Is leaf: {quality_dimension.is_leaf}")
    print()

    # Create a model version
    model_version = ModelVersion(
        model_hash="a" * 64,  # Placeholder hash
        change_types={"spore_created", "dimension_added"},
        change_count=2,
    )

    print(f"Created model version: {model_version.version_id}")
    print(f"Change summary: {model_version.change_summary}")
    print(f"Has conflicts: {model_version.has_conflicts}")
    print()

    # Create a glacier spore
    spore = GlacierSpore(
        spore_type=SporeType.DISCOVERY,
        content_hash="b" * 64,  # Placeholder hash
        embedded_schema={
            "type": "discovery_spore",
            "version": "1.0.0",
            "properties": {
                "repo_name": {"type": "string"},
                "language": {"type": "string"},
            },
        },
        content_schema={
            "type": "object",
            "properties": {
                "repo_name": {"type": "string"},
                "language": {"type": "string"},
            },
        },
        content={"repo_name": "test-repo", "language": "Python"},
        dimensions={"code_quality_score": 85.0, "spore_type": "discovery"},
    )

    print(f"Created spore: {spore.spore_id}")
    print(f"Semantic complexity: {spore.semantic_complexity:.2f}")
    print(f"Semantic health: {spore.semantic_health_score:.2f}")
    print(f"Semantic summary: {spore.semantic_summary}")
    print()

    # Test semantic diff
    other_spore = GlacierSpore(
        spore_type=SporeType.DISCOVERY,
        content_hash="c" * 64,  # Placeholder hash
        embedded_schema=spore.embedded_schema,
        content_schema=spore.content_schema,
        content={
            "repo_name": "test-repo",
            "language": "Python",
            "new_field": "new_value",
        },
        dimensions=spore.dimensions,
    )

    diffs = spore.create_semantic_diff(other_spore)
    print(f"Semantic diffs found: {len(diffs)}")
    for diff in diffs:
        print(f"  - {diff.semantic_summary}")

    print(f"\n✅ Pydantic-driven glacier spore models demo completed!")


if __name__ == "__main__":
    main()
