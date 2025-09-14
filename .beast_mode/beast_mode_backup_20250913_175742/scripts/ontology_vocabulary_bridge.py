#!/usr/bin/env python3
"""
Ontology Vocabulary Bridge for OpenFlow-Playground.

This script bridges the ontology framework with OpenFlow-Playground to solve
vocabulary alignment between reverse engineering and code generation domains.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the ontology framework to the path
ontology_framework_path = Path(__file__).parent.parent / "subprojects" / "ontology-framework" / "src"
sys.path.insert(0, str(ontology_framework_path))

try:
    from ontology_framework.openflow_integration import OpenFlowIntegration
except ImportError as e:
    print(f"❌ Failed to import ontology framework: {e}")
    print("Make sure the ontology-framework subproject is properly cloned")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OntologyVocabularyBridge:
    """
    Bridge between OpenFlow-Playground and the ontology framework.

    This class provides vocabulary alignment capabilities using the sophisticated
    ontology framework rather than simple Python class mappings.
    """

    def __init__(self):
        """Initialize the ontology vocabulary bridge."""
        try:
            # Initialize the ontology integration
            ontology_path = Path(__file__).parent.parent / "subprojects" / "ontology-framework" / "models"
            self.integration = OpenFlowIntegration(str(ontology_path))
            logger.info("✅ Ontology vocabulary bridge initialized successfully")

            # Get ontology summary
            summary = self.integration.get_ontology_summary()
            logger.info(f"📊 Loaded ontology with {summary.get('classes', 0)} classes")

        except Exception as e:
            logger.error(f"❌ Failed to initialize ontology bridge: {e}")
            raise

    def analyze_vocabulary_mismatch(self, reverse_engineering_data: Any, code_generation_data: Any) -> Dict[str, Any]:
        """
        Analyze vocabulary mismatch using ontological validation.

        Args:
            reverse_engineering_data: Data from reverse engineering domain
            code_generation_data: Data from code generation domain

        Returns:
            Comprehensive analysis of vocabulary alignment
        """
        try:
            logger.info("🔍 Analyzing vocabulary mismatch using ontology framework...")

            # Use the ontology framework for validation
            validation_result = self.integration.validate_vocabulary_alignment(reverse_engineering_data, code_generation_data)

            logger.info(f"📋 Vocabulary analysis completed. Valid: {validation_result['valid']}")

            return validation_result

        except Exception as e:
            logger.error(f"❌ Vocabulary analysis failed: {e}")
            return {"valid": False, "error": str(e), "analysis_timestamp": "failed"}

    def resolve_vocabulary_mismatch(self, reverse_engineering_data: Any, target_format: str = "dict") -> Any:
        """
        Resolve vocabulary mismatch by transforming data to target format.

        Args:
            reverse_engineering_data: Data from reverse engineering domain
            target_format: Target format ("dict" or "list")

        Returns:
            Transformed data in target format
        """
        try:
            logger.info(f"🔄 Resolving vocabulary mismatch to {target_format} format...")

            # Determine transformation type
            if target_format == "dict" and isinstance(reverse_engineering_data, list):
                transformation_type = "list_to_dict"
            elif target_format == "list" and isinstance(reverse_engineering_data, dict):
                transformation_type = "dict_to_list"
            else:
                logger.warning(f"⚠️ No transformation needed for {type(reverse_engineering_data)} to {target_format}")
                return reverse_engineering_data

            # Apply transformation using ontology framework
            transformed_data = self.integration.apply_transformation(reverse_engineering_data, transformation_type)

            logger.info(f"✅ Transformation successful: {type(reverse_engineering_data)} -> {type(transformed_data)}")

            return transformed_data

        except Exception as e:
            logger.error(f"❌ Vocabulary mismatch resolution failed: {e}")
            raise

    def validate_transformation(self, original_data: Any, transformed_data: Any, target_format: str) -> Dict[str, Any]:
        """
        Validate that transformation was successful and maintains data integrity.

        Args:
            original_data: Original data before transformation
            transformed_data: Data after transformation
            target_format: Expected target format

        Returns:
            Validation results
        """
        try:
            logger.info("🔍 Validating transformation integrity...")

            validation_result = {
                "valid": True,
                "format_correct": False,
                "data_integrity": False,
                "component_count_preserved": False,
                "method_count_preserved": False,
                "issues": [],
            }

            # Check format correctness
            if target_format == "dict" and isinstance(transformed_data, dict):
                validation_result["format_correct"] = True
            elif target_format == "list" and isinstance(transformed_data, list):
                validation_result["format_correct"] = True
            else:
                validation_result["format_correct"] = False
                validation_result["issues"].append(f"Expected {target_format}, got {type(transformed_data).__name__}")

            # Check data integrity
            if isinstance(original_data, list) and isinstance(transformed_data, dict):
                # List to dict transformation
                original_count = len(original_data)
                transformed_count = len(transformed_data)
                validation_result["component_count_preserved"] = original_count == transformed_count

                if not validation_result["component_count_preserved"]:
                    validation_result["issues"].append(f"Component count mismatch: {original_count} -> {transformed_count}")

                # Check that all components have names
                missing_names = []
                for i, item in enumerate(original_data):
                    if not isinstance(item, dict) or "name" not in item:
                        missing_names.append(f"Item {i}")

                if missing_names:
                    validation_result["issues"].append(f"Missing names: {missing_names}")

            elif isinstance(original_data, dict) and isinstance(transformed_data, list):
                # Dict to list transformation
                original_count = len(original_data)
                transformed_count = len(transformed_data)
                validation_result["component_count_preserved"] = original_count == transformed_count

                if not validation_result["component_count_preserved"]:
                    validation_result["issues"].append(f"Component count mismatch: {original_count} -> {transformed_count}")

            # Overall validation
            validation_result["valid"] = validation_result["format_correct"] and validation_result["component_count_preserved"] and len(validation_result["issues"]) == 0

            if validation_result["valid"]:
                logger.info("✅ Transformation validation passed")
            else:
                logger.warning(f"⚠️ Transformation validation failed: {validation_result['issues']}")

            return validation_result

        except Exception as e:
            logger.error(f"❌ Transformation validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "issues": [f"Validation error: {e}"],
            }

    def get_ontology_insights(self) -> Dict[str, Any]:
        """
        Get insights from the ontology about vocabulary alignment.

        Returns:
            Ontology insights and recommendations
        """
        try:
            logger.info("🔍 Gathering ontology insights...")

            # Get ontology summary
            summary = self.integration.get_ontology_summary()

            insights = {
                "ontology_summary": summary,
                "vocabulary_alignment_rules": [
                    "Reverse engineering components use list format",
                    "Code generation components expect dict format",
                    "Transformation preserves component names as keys",
                    "Methods are nested within components",
                    "All transformations maintain data integrity",
                ],
                "recommended_workflow": [
                    "1. Extract models using reverse engineering (list format)",
                    "2. Validate vocabulary alignment using ontology",
                    "3. Transform to code generation format (dict format)",
                    "4. Validate transformation integrity",
                    "5. Generate code using transformed models",
                ],
                "validation_approach": "Ontological validation using SHACL shapes and SPARQL queries",
                "transformation_approach": "Rule-based transformations with integrity validation",
            }

            return insights

        except Exception as e:
            logger.error(f"❌ Failed to get ontology insights: {e}")
            return {"error": str(e)}


def main():
    """Main function to demonstrate the ontology vocabulary bridge."""

    print("🌉 OpenFlow-Playground Ontology Vocabulary Bridge")
    print("=" * 60)

    try:
        # Initialize the bridge
        bridge = OntologyVocabularyBridge()

        # Get ontology insights
        print("\n🔍 Getting ontology insights...")
        insights = bridge.get_ontology_insights()
        print(f"📊 Ontology Summary: {json.dumps(insights['ontology_summary'], indent=2)}")

        print("\n📋 Vocabulary Alignment Rules:")
        for rule in insights["vocabulary_alignment_rules"]:
            print(f"  • {rule}")

        print("\n🔄 Recommended Workflow:")
        for step in insights["recommended_workflow"]:
            print(f"  {step}")

        # Test with sample data
        print("\n🧪 Testing with sample data...")

        # Sample reverse engineering data (list format)
        sample_re_data = [
            {
                "name": "TestComponent",
                "type": "class",
                "description": "A test component",
                "methods": [{"name": "test_method", "type": "method", "return_type": "str"}],
            }
        ]

        # Sample code generation data (dict format)
        sample_cg_data = {
            "TestComponent": {
                "name": "TestComponent",
                "type": "class",
                "description": "A test component",
                "methods": {
                    "test_method": {
                        "name": "test_method",
                        "type": "method",
                        "return_type": "str",
                    }
                },
            }
        }

        # Analyze vocabulary mismatch
        print("\n🔍 Analyzing vocabulary mismatch...")
        analysis = bridge.analyze_vocabulary_mismatch(sample_re_data, sample_cg_data)

        if analysis["valid"]:
            print("✅ Vocabulary alignment is valid!")
        else:
            print("⚠️ Vocabulary alignment issues detected:")
            for mismatch in analysis.get("vocabulary_mismatches", []):
                print(f"  - {mismatch['description']}")

        # Test transformation
        print("\n🔄 Testing transformation...")
        transformed = bridge.resolve_vocabulary_mismatch(sample_re_data, "dict")

        # Validate transformation
        validation = bridge.validate_transformation(sample_re_data, transformed, "dict")

        if validation["valid"]:
            print("✅ Transformation and validation successful!")
        else:
            print("⚠️ Transformation validation failed:")
            for issue in validation.get("issues", []):
                print(f"  - {issue}")

        print("\n🎉 Ontology vocabulary bridge test completed successfully!")

    except Exception as e:
        print(f"❌ Bridge test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
