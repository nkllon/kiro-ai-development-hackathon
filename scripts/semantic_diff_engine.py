#!/usr/bin/env python3
"""
Semantic Diff Engine - Model-Driven Change Detection

This engine detects semantic changes between glacier spores,
not just artifact-level differences. It understands the meaning
and impact of changes at a semantic level.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from glacier_spore_models import (
    Dimension,
    DimensionType,
    GlacierSpore,
    ModelVersion,
    SemanticDiff,
    SporeType,
)

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))


class SemanticDiffEngine:
    """
    Engine for detecting semantic differences between glacier spores

    This engine understands:
    1. Semantic meaning of changes, not just text differences
    2. Impact assessment of changes
    3. Relationship changes between spores
    4. Schema evolution and breaking changes
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Semantic change patterns and their impact scores
        self.semantic_patterns = {
            "field_addition": {
                "impact": 0.3,
                "description": "New semantic field added",
            },
            "field_removal": {"impact": 0.5, "description": "Semantic field removed"},
            "field_modification": {
                "impact": 0.4,
                "description": "Semantic field value changed",
            },
            "schema_evolution": {
                "impact": 0.6,
                "description": "Schema structure evolved",
            },
            "relationship_change": {
                "impact": 0.7,
                "description": "Semantic relationship changed",
            },
            "dimension_change": {
                "impact": 0.5,
                "description": "Dimensional context changed",
            },
            "breaking_change": {
                "impact": 0.9,
                "description": "Breaking semantic change",
            },
            "quality_improvement": {
                "impact": 0.2,
                "description": "Quality improvement",
            },
            "security_enhancement": {
                "impact": 0.4,
                "description": "Security enhancement",
            },
            "performance_optimization": {
                "impact": 0.3,
                "description": "Performance optimization",
            },
        }

    def diff_spores(self, old_spore: GlacierSpore, new_spore: GlacierSpore) -> list[SemanticDiff]:
        """
        Create semantic diffs between two spores

        This analyzes semantic meaning, not just artifact differences
        """
        diffs = []

        # Validate that we're comparing compatible spores
        if not self._are_compatible_spores(old_spore, new_spore):
            msg = "Cannot compare incompatible spore types"
            raise ValueError(msg)

        # Content semantic diffs
        content_diffs = self._diff_content_semantically(old_spore.content, new_spore.content)
        diffs.extend(content_diffs)

        # Schema semantic diffs
        schema_diffs = self._diff_schemas_semantically(old_spore.embedded_schema, new_spore.embedded_schema)
        diffs.extend(schema_diffs)

        # Dimension semantic diffs
        dimension_diffs = self._diff_dimensions_semantically(old_spore.dimensions, new_spore.dimensions)
        diffs.extend(dimension_diffs)

        # Relationship semantic diffs
        relationship_diffs = self._diff_relationships_semantically(old_spore, new_spore)
        diffs.extend(relationship_diffs)

        # Processing instruction diffs
        processing_diffs = self._diff_processing_semantically(old_spore, new_spore)
        diffs.extend(processing_diffs)

        # Add semantic context to all diffs
        for diff in diffs:
            diff.semantic_context = self._build_semantic_context(old_spore, new_spore, diff)

        return diffs

    def _are_compatible_spores(self, spore1: GlacierSpore, spore2: GlacierSpore) -> bool:
        """Check if spores are semantically compatible for comparison"""
        # Same type is required
        if spore1.spore_type != spore2.spore_type:
            return False

        # Similar schemas are preferred
        if spore1.embedded_schema.get("type") != spore2.embedded_schema.get("type"):
            self.logger.warning("Comparing spores with different schema types")

        return True

    def _diff_content_semantically(self, old_content: dict[str, Any], new_content: dict[str, Any]) -> list[SemanticDiff]:
        """Detect semantic changes in content"""
        diffs = []

        # Find added fields
        for key in new_content:
            if key not in old_content:
                diff = SemanticDiff(
                    field_path=f"content.{key}",
                    change_type="field_addition",
                    new_semantic_value=new_content[key],
                    impact_score=self._assess_field_impact(key, new_content[key], "addition"),
                    semantic_context={
                        "change_reason": "new_field",
                        "field_category": self._categorize_field(key),
                    },
                )
                diffs.append(diff)

        # Find removed fields
        for key in old_content:
            if key not in new_content:
                diff = SemanticDiff(
                    field_path=f"content.{key}",
                    change_type="field_removal",
                    old_semantic_value=old_content[key],
                    impact_score=self._assess_field_impact(key, old_content[key], "removal"),
                    semantic_context={
                        "change_reason": "removed_field",
                        "field_category": self._categorize_field(key),
                    },
                )
                diffs.append(diff)

        # Find modified fields
        for key in old_content:
            if key in new_content and old_content[key] != new_content[key]:
                diff = SemanticDiff(
                    field_path=f"content.{key}",
                    change_type="field_modification",
                    old_semantic_value=old_content[key],
                    new_semantic_value=new_content[key],
                    impact_score=self._assess_field_impact(key, new_content[key], "modification"),
                    semantic_context={
                        "change_reason": "value_change",
                        "field_category": self._categorize_field(key),
                        "change_magnitude": self._assess_change_magnitude(old_content[key], new_content[key]),
                    },
                )
                diffs.append(diff)

        return diffs

    def _diff_schemas_semantically(self, old_schema: dict[str, Any], new_schema: dict[str, Any]) -> list[SemanticDiff]:
        """Detect semantic changes in schemas"""
        diffs = []

        # Check for breaking schema changes
        if self._is_breaking_schema_change(old_schema, new_schema):
            diff = SemanticDiff(
                field_path="embedded_schema",
                change_type="breaking_change",
                old_semantic_value=old_schema,
                new_semantic_value=new_schema,
                impact_score=0.9,
                semantic_context={"change_reason": "breaking_schema_change"},
            )
            diffs.append(diff)

        # Check for schema evolution
        elif old_schema != new_schema:
            diff = SemanticDiff(
                field_path="embedded_schema",
                change_type="schema_evolution",
                old_semantic_value=old_schema,
                new_semantic_value=new_schema,
                impact_score=0.6,
                semantic_context={"change_reason": "schema_evolution"},
            )
            diffs.append(diff)

        return diffs

    def _diff_dimensions_semantically(self, old_dims: dict[str, Any], new_dims: dict[str, Any]) -> list[SemanticDiff]:
        """Detect semantic changes in dimensions"""
        diffs = []

        # Find added dimensions
        for key in new_dims:
            if key not in old_dims:
                diff = SemanticDiff(
                    field_path=f"dimensions.{key}",
                    change_type="dimension_change",
                    new_semantic_value=new_dims[key],
                    impact_score=0.5,
                    semantic_context={
                        "change_reason": "new_dimension",
                        "dimension_type": "added",
                    },
                )
                diffs.append(diff)

        # Find removed dimensions
        for key in old_dims:
            if key not in new_dims:
                diff = SemanticDiff(
                    field_path=f"dimensions.{key}",
                    change_type="dimension_change",
                    old_semantic_value=old_dims[key],
                    impact_score=0.5,
                    semantic_context={
                        "change_reason": "removed_dimension",
                        "dimension_type": "removed",
                    },
                )
                diffs.append(diff)

        # Find modified dimensions
        for key in old_dims:
            if key in new_dims and old_dims[key] != new_dims[key]:
                diff = SemanticDiff(
                    field_path=f"dimensions.{key}",
                    change_type="dimension_change",
                    old_semantic_value=old_dims[key],
                    new_semantic_value=new_dims[key],
                    impact_score=0.5,
                    semantic_context={
                        "change_reason": "dimension_value_change",
                        "dimension_type": "modified",
                    },
                )
                diffs.append(diff)

        return diffs

    def _diff_relationships_semantically(self, old_spore: GlacierSpore, new_spore: GlacierSpore) -> list[SemanticDiff]:
        """Detect semantic changes in relationships"""
        diffs = []

        # Check parent relationship changes
        if old_spore.parent_spore_id != new_spore.parent_spore_id:
            diff = SemanticDiff(
                field_path="parent_spore_id",
                change_type="relationship_change",
                old_semantic_value=old_spore.parent_spore_id,
                new_semantic_value=new_spore.parent_spore_id,
                impact_score=0.7,
                semantic_context={"change_reason": "parent_relationship_change"},
            )
            diffs.append(diff)

        # Check child relationship changes
        if set(old_spore.child_spore_ids) != set(new_spore.child_spore_ids):
            diff = SemanticDiff(
                field_path="child_spore_ids",
                change_type="relationship_change",
                old_semantic_value=old_spore.child_spore_ids,
                new_semantic_value=new_spore.child_spore_ids,
                impact_score=0.6,
                semantic_context={"change_reason": "child_relationship_change"},
            )
            diffs.append(diff)

        # Check related spore changes
        if set(old_spore.related_spore_ids) != set(new_spore.related_spore_ids):
            diff = SemanticDiff(
                field_path="related_spore_ids",
                change_type="relationship_change",
                old_semantic_value=old_spore.related_spore_ids,
                new_semantic_value=new_spore.related_spore_ids,
                impact_score=0.5,
                semantic_context={"change_reason": "related_relationship_change"},
            )
            diffs.append(diff)

        return diffs

    def _diff_processing_semantically(self, old_spore: GlacierSpore, new_spore: GlacierSpore) -> list[SemanticDiff]:
        """Detect semantic changes in processing instructions"""
        diffs = []

        # Check processing trigger changes
        if set(old_spore.processing_triggers) != set(new_spore.processing_triggers):
            diff = SemanticDiff(
                field_path="processing_triggers",
                change_type="field_modification",
                old_semantic_value=old_spore.processing_triggers,
                new_semantic_value=new_spore.processing_triggers,
                impact_score=0.4,
                semantic_context={"change_reason": "processing_trigger_change"},
            )
            diffs.append(diff)

        # Check processor requirement changes
        if old_spore.processor_requirements != new_spore.processor_requirements:
            diff = SemanticDiff(
                field_path="processor_requirements",
                change_type="field_modification",
                old_semantic_value=old_spore.processor_requirements,
                new_semantic_value=new_spore.processor_requirements,
                impact_score=0.4,
                semantic_context={"change_reason": "processor_requirement_change"},
            )
            diffs.append(diff)

        return diffs

    def _assess_field_impact(self, field_name: str, value: Any, change_type: str) -> float:
        """Assess the semantic impact of a field change"""
        base_impact = self.semantic_patterns.get(change_type, {}).get("impact", 0.5)

        # Adjust based on field importance
        if field_name in ["repo_name", "language", "quality_score"]:
            base_impact *= 1.2  # Important fields have higher impact

        # Adjust based on value type
        if isinstance(value, (dict, list)):
            base_impact *= 1.1  # Complex values have higher impact

        return min(base_impact, 1.0)

    def _categorize_field(self, field_name: str) -> str:
        """Categorize a field semantically"""
        if "name" in field_name:
            return "identifier"
        if "score" in field_name or "quality" in field_name:
            return "quality_metric"
        if "type" in field_name:
            return "classification"
        if "url" in field_name or "path" in field_name:
            return "location"
        if "time" in field_name or "date" in field_name:
            return "temporal"
        return "general"

    def _assess_change_magnitude(self, old_value: Any, new_value: Any) -> str:
        """Assess the magnitude of a value change"""
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            change_ratio = abs(new_value - old_value) / max(abs(old_value), 1)
            if change_ratio > 0.5:
                return "major"
            if change_ratio > 0.1:
                return "moderate"
            return "minor"
        if old_value != new_value:
            return "moderate"
        return "none"

    def _is_breaking_schema_change(self, old_schema: dict[str, Any], new_schema: dict[str, Any]) -> bool:
        """Check if a schema change is breaking"""
        # Check for required field removal
        old_required = old_schema.get("required", [])
        new_required = new_schema.get("required", [])

        removed_required = set(old_required) - set(new_required)
        if removed_required:
            return True

        # Check for type changes in existing fields
        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})

        for field_name in old_props:
            if field_name in new_props:
                old_type = old_props[field_name].get("type")
                new_type = new_props[field_name].get("type")

                if old_type != new_type:
                    # Some type changes are breaking
                    if old_type == "string" and new_type in ["integer", "number"]:
                        return True
                    if old_type in ["integer", "number"] and new_type == "string":
                        return True

        return False

    def _build_semantic_context(self, old_spore: GlacierSpore, new_spore: GlacierSpore, diff: SemanticDiff) -> dict[str, Any]:
        """Build semantic context for a diff"""
        context = {
            "spore_type": old_spore.spore_type.value,
            "change_timestamp": datetime.now(timezone.utc).isoformat(),
            "old_spore_id": old_spore.spore_id,
            "new_spore_id": new_spore.spore_id,
            "field_category": self._categorize_field(diff.field_path.split(".")[-1]),
            "semantic_impact": ("high" if diff.impact_score > 0.7 else "medium" if diff.impact_score > 0.4 else "low"),
        }

        # Add existing context if present
        if diff.semantic_context:
            context.update(diff.semantic_context)

        return context

    def analyze_semantic_impact(self, diffs: list[SemanticDiff]) -> dict[str, Any]:
        """Analyze the overall semantic impact of changes"""
        if not diffs:
            return {
                "total_impact": 0.0,
                "breaking_changes": 0,
                "high_impact_changes": 0,
                "medium_impact_changes": 0,
                "low_impact_changes": 0,
                "change_categories": {},
                "recommendations": [],
            }

        # Calculate impact metrics
        total_impact = sum(diff.impact_score for diff in diffs)
        breaking_changes = len([d for d in diffs if d.is_breaking_change])
        high_impact = len([d for d in diffs if d.impact_score > 0.7])
        medium_impact = len([d for d in diffs if 0.4 < d.impact_score <= 0.7])
        low_impact = len([d for d in diffs if d.impact_score <= 0.4])

        # Categorize changes
        change_categories = {}
        for diff in diffs:
            category = diff.semantic_context.get("field_category", "unknown")
            change_categories[category] = change_categories.get(category, 0) + 1

        # Generate recommendations
        recommendations = []
        if breaking_changes > 0:
            recommendations.append("Review breaking changes before deployment")
        if high_impact > 0:
            recommendations.append("High impact changes detected - consider staged rollout")
        if total_impact > 2.0:
            recommendations.append("High cumulative impact - consider feature flagging")

        return {
            "total_impact": total_impact,
            "breaking_changes": breaking_changes,
            "high_impact_changes": high_impact,
            "medium_impact_changes": medium_impact,
            "low_impact_changes": low_impact,
            "change_categories": change_categories,
            "recommendations": recommendations,
        }


# Example usage
async def main():
    """Example usage of the semantic diff engine"""

    print("🔍 Semantic Diff Engine - Model-Driven Change Detection")
    print("=" * 60)

    # Create the diff engine
    engine = SemanticDiffEngine()

    # Create two spores with semantic differences
    old_spore = GlacierSpore(
        spore_type=SporeType.DISCOVERY,
        content_hash="a" * 64,  # Placeholder hash
        embedded_schema={
            "type": "discovery_spore",
            "version": "1.0.0",
            "properties": {
                "repo_name": {"type": "string"},
                "language": {"type": "string"},
            },
            "required": ["repo_name"],
        },
        content_schema={
            "type": "object",
            "properties": {
                "repo_name": {"type": "string"},
                "language": {"type": "string"},
            },
        },
        content={"repo_name": "old-repo", "language": "Python"},
        dimensions={"quality_score": 75.0, "spore_type": "discovery"},
        processing_triggers=["basic_analysis"],
        child_spore_ids=["child1", "child2"],
    )

    new_spore = GlacierSpore(
        spore_type=SporeType.DISCOVERY,
        content_hash="b" * 64,  # Placeholder hash
        embedded_schema={
            "type": "discovery_spore",
            "version": "1.1.0",
            "properties": {
                "repo_name": {"type": "string"},
                "language": {"type": "string"},
                "new_field": {"type": "string"},
            },
            "required": ["repo_name"],
        },
        content_schema={
            "type": "object",
            "properties": {
                "repo_name": {"type": "string"},
                "language": {"type": "string"},
                "new_field": {"type": "string"},
            },
        },
        content={
            "repo_name": "new-repo",
            "language": "Python",
            "new_field": "new_value",
        },
        dimensions={
            "quality_score": 85.0,
            "spore_type": "discovery",
            "new_dimension": "new_value",
        },
        processing_triggers=["basic_analysis", "advanced_analysis"],
        child_spore_ids=["child1", "child2", "child3"],
    )

    # Generate semantic diffs
    print("🔍 Analyzing semantic differences...")
    diffs = engine.diff_spores(old_spore, new_spore)

    print(f"Found {len(diffs)} semantic changes:")
    for i, diff in enumerate(diffs, 1):
        print(f"  {i}. {diff.semantic_summary}")
        print(f"     Path: {diff.field_path}")
        print(f"     Type: {diff.change_type}")
        print(f"     Impact: {diff.impact_score:.2f}")
        if diff.semantic_context:
            print(f"     Context: {diff.semantic_context.get('change_reason', 'N/A')}")
        print()

    # Analyze overall impact
    impact_analysis = engine.analyze_semantic_impact(diffs)

    print("📊 Semantic Impact Analysis:")
    print(f"  Total Impact: {impact_analysis['total_impact']:.2f}")
    print(f"  Breaking Changes: {impact_analysis['breaking_changes']}")
    print(f"  High Impact: {impact_analysis['high_impact_changes']}")
    print(f"  Medium Impact: {impact_analysis['medium_impact_changes']}")
    print(f"  Low Impact: {impact_analysis['low_impact_changes']}")
    print()

    print("🏷️  Change Categories:")
    for category, count in impact_analysis["change_categories"].items():
        print(f"  {category}: {count}")
    print()

    if impact_analysis["recommendations"]:
        print("💡 Recommendations:")
        for rec in impact_analysis["recommendations"]:
            print(f"  - {rec}")

    print(f"\n✅ Semantic diff analysis completed!")


if __name__ == "__main__":
    asyncio.run(main())
