#!/usr/bin/env python3
"""
Simple Ontology Vocabulary Bridge for OpenFlow-Playground.

This script provides vocabulary alignment between reverse engineering and code generation
domains using a simplified ontological approach.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleOntologyBridge:
    """
    Simple bridge for vocabulary alignment between domains.

    This class provides vocabulary alignment capabilities using a simplified
    ontological approach focused on the specific OpenFlow-Playground use case.
    """

    def __init__(self):
        """Initialize the simple ontology bridge."""
        logger.info("✅ Simple ontology vocabulary bridge initialized")

        # Define our vocabulary alignment ontology
        self.ontology = {
            "domains": {
                "reverse_engineering": {
                    "format": "list",
                    "structure": "array_of_components",
                    "component_representation": "list_item",
                },
                "code_generation": {
                    "format": "dict",
                    "structure": "keyed_by_name",
                    "component_representation": "dict_value",
                },
            },
            "transformations": {
                "list_to_dict": {
                    "source": "reverse_engineering",
                    "target": "code_generation",
                    "logic": "transform_list_to_dict",
                    "validation": "preserve_component_count_and_names",
                },
                "dict_to_list": {
                    "source": "code_generation",
                    "target": "reverse_engineering",
                    "logic": "transform_dict_to_list",
                    "validation": "preserve_component_count",
                },
            },
            "vocabulary_mapping": {
                "component": {
                    "reverse_engineering": "list_item",
                    "code_generation": "dict_value",
                    "required_fields": ["name", "type", "description"],
                },
                "method": {
                    "reverse_engineering": "nested_list",
                    "code_generation": "nested_dict",
                    "required_fields": ["name", "type", "return_type"],
                },
            },
        }

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
            logger.info("🔍 Analyzing vocabulary mismatch using ontology...")

            # Analyze the data structures
            re_analysis = self._analyze_data_structure(reverse_engineering_data, "reverse_engineering")
            cg_analysis = self._analyze_data_structure(code_generation_data, "code_generation")

            # Check for vocabulary mismatches
            mismatches = self._identify_vocabulary_mismatches(re_analysis, cg_analysis)

            # Generate transformation recommendations
            transformations = self._recommend_transformations(mismatches)

            return {
                "valid": len(mismatches) == 0,
                "reverse_engineering_analysis": re_analysis,
                "code_generation_analysis": cg_analysis,
                "vocabulary_mismatches": mismatches,
                "recommended_transformations": transformations,
                "ontology_used": "SimpleOntologyBridge",
            }

        except Exception as e:
            logger.error(f"❌ Vocabulary alignment validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "ontology_used": "SimpleOntologyBridge",
            }

    def _analyze_data_structure(self, data: Any, domain: str) -> Dict[str, Any]:
        """
        Analyze the structure of data from a specific domain.

        Args:
            data: The data to analyze
            domain: The domain name (reverse_engineering or code_generation)

        Returns:
            Analysis results
        """
        analysis = {
            "domain": domain,
            "data_type": type(data).__name__,
            "structure": self._get_structure_info(data),
            "components": self._extract_components(data),
            "methods": self._extract_methods(data),
            "vocabulary": self._extract_vocabulary(data),
        }

        return analysis

    def _get_structure_info(self, data: Any) -> Dict[str, Any]:
        """Get information about the data structure."""
        if isinstance(data, dict):
            return {
                "type": "dictionary",
                "keys": list(data.keys()),
                "depth": self._calculate_depth(data),
                "size": len(data),
            }
        elif isinstance(data, list):
            return {
                "type": "list",
                "length": len(data),
                "item_types": list(set(type(item).__name__ for item in data)),
                "depth": self._calculate_depth(data),
            }
        else:
            return {"type": type(data).__name__, "depth": 0, "size": 1}

    def _calculate_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of nested data structures."""
        if isinstance(data, (dict, list)) and data:
            if isinstance(data, dict):
                return max(self._calculate_depth(v, current_depth + 1) for v in data.values())
            else:  # list
                return max(self._calculate_depth(item, current_depth + 1) for item in data)
        return current_depth

    def _extract_components(self, data: Any) -> List[Dict[str, Any]]:
        """Extract component information from the data."""
        components = []

        if isinstance(data, dict):
            # Dictionary format - components are values
            for key, value in data.items():
                if isinstance(value, dict) and self._is_component(value):
                    components.append(
                        {
                            "name": key,
                            "type": value.get("type", "unknown"),
                            "description": value.get("description", ""),
                            "properties": list(value.keys()),
                        }
                    )
        elif isinstance(data, list):
            # List format - components are list items
            for item in data:
                if isinstance(item, dict) and self._is_component(item):
                    components.append(
                        {
                            "name": item.get("name", "unnamed"),
                            "type": item.get("type", "unknown"),
                            "description": item.get("description", ""),
                            "properties": list(item.keys()),
                        }
                    )

        return components

    def _is_component(self, item: Any) -> bool:
        """Check if an item represents a component."""
        if not isinstance(item, dict):
            return False

        # Check for component indicators
        component_indicators = ["name", "type", "description", "methods", "properties"]
        return any(indicator in item for indicator in component_indicators)

    def _extract_methods(self, data: Any) -> List[Dict[str, Any]]:
        """Extract method information from the data."""
        methods = []

        if isinstance(data, dict):
            # Look for methods in components
            for value in data.values():
                if isinstance(value, dict):
                    methods.extend(self._extract_methods_from_component(value))
        elif isinstance(data, list):
            # Look for methods in list items
            for item in data:
                if isinstance(item, dict):
                    methods.extend(self._extract_methods_from_component(item))

        return methods

    def _extract_methods_from_component(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract methods from a single component."""
        methods = []

        # Check if component has methods
        if "methods" in component:
            method_list = component["methods"]
            if isinstance(method_list, list):
                for method in method_list:
                    if isinstance(method, dict):
                        methods.append(
                            {
                                "name": method.get("name", "unnamed"),
                                "type": method.get("type", "unknown"),
                                "return_type": method.get("return_type", "unknown"),
                                "parameters": method.get("parameters", []),
                            }
                        )

        return methods

    def _extract_vocabulary(self, data: Any) -> Dict[str, Any]:
        """Extract vocabulary information from the data."""
        vocabulary = {"terms": set(), "data_types": set(), "structures": set()}

        def _extract_from_item(item: Any):
            if isinstance(item, dict):
                vocabulary["terms"].update(item.keys())
                vocabulary["structures"].add("dictionary")
                for value in item.values():
                    _extract_from_item(value)
            elif isinstance(item, list):
                vocabulary["structures"].add("list")
                for subitem in item:
                    _extract_from_item(subitem)
            else:
                vocabulary["data_types"].add(type(item).__name__)

        _extract_from_item(data)

        # Convert sets to lists for JSON serialization
        return {
            "terms": list(vocabulary["terms"]),
            "data_types": list(vocabulary["data_types"]),
            "structures": list(vocabulary["structures"]),
        }

    def _identify_vocabulary_mismatches(self, re_analysis: Dict[str, Any], cg_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify vocabulary mismatches between domains."""
        mismatches = []

        # Check structure mismatches
        re_structure = re_analysis["structure"]["type"]
        cg_structure = cg_analysis["structure"]["type"]

        if re_structure != cg_structure:
            mismatches.append(
                {
                    "type": "structure_mismatch",
                    "reverse_engineering": re_structure,
                    "code_generation": cg_structure,
                    "description": f"Reverse engineering uses {re_structure}, code generation expects {cg_structure}",
                    "severity": "HIGH",
                    "ontology_rule": "format_mismatch",
                }
            )

        # Check vocabulary term mismatches
        re_terms = set(re_analysis["vocabulary"]["terms"])
        cg_terms = set(cg_analysis["vocabulary"]["terms"])

        missing_in_cg = re_terms - cg_terms
        missing_in_re = cg_terms - re_terms

        if missing_in_cg:
            mismatches.append(
                {
                    "type": "missing_vocabulary",
                    "domain": "code_generation",
                    "missing_terms": list(missing_in_cg),
                    "description": f"Code generation domain missing terms: {missing_in_cg}",
                    "severity": "MEDIUM",
                    "ontology_rule": "vocabulary_incomplete",
                }
            )

        if missing_in_re:
            mismatches.append(
                {
                    "type": "missing_vocabulary",
                    "domain": "reverse_engineering",
                    "missing_terms": list(missing_in_re),
                    "description": f"Reverse engineering domain missing terms: {missing_in_re}",
                    "severity": "MEDIUM",
                    "ontology_rule": "vocabulary_incomplete",
                }
            )

        return mismatches

    def _recommend_transformations(self, mismatches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend transformations to resolve vocabulary mismatches."""
        transformations = []

        for mismatch in mismatches:
            if mismatch["type"] == "structure_mismatch":
                if mismatch["reverse_engineering"] == "list" and mismatch["code_generation"] == "dictionary":
                    transformations.append(
                        {
                            "type": "list_to_dict",
                            "description": "Transform list-based components to dictionary format",
                            "transformation_rule": "OpenFlowComponentTransformation",
                            "implementation": "Use transform_list_to_dict function",
                            "priority": "HIGH",
                            "ontology_rule": "list_to_dict_transformation",
                        }
                    )
                elif mismatch["reverse_engineering"] == "dictionary" and mismatch["code_generation"] == "list":
                    transformations.append(
                        {
                            "type": "dict_to_list",
                            "description": "Transform dictionary-based components to list format",
                            "transformation_rule": "OpenFlowMethodTransformation",
                            "implementation": "Use transform_dict_to_list function",
                            "priority": "HIGH",
                            "ontology_rule": "dict_to_list_transformation",
                        }
                    )

        return transformations

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

            # Apply transformation
            if transformation_type == "list_to_dict":
                transformed_data = self._transform_list_to_dict(reverse_engineering_data)
            elif transformation_type == "dict_to_list":
                transformed_data = self._transform_dict_to_list(reverse_engineering_data)
            else:
                raise ValueError(f"Unknown transformation type: {transformation_type}")

            logger.info(f"✅ Transformation successful: {type(reverse_engineering_data)} -> {type(transformed_data)}")

            return transformed_data

        except Exception as e:
            logger.error(f"❌ Vocabulary mismatch resolution failed: {e}")
            raise

    def _transform_list_to_dict(self, component_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform list of components to dictionary keyed by name."""
        if not isinstance(component_list, list):
            raise ValueError("Input must be a list")

        result = {}
        for component in component_list:
            if isinstance(component, dict) and "name" in component:
                result[component["name"]] = component
            else:
                raise ValueError("Each component must be a dict with 'name' field")

        return result

    def _transform_dict_to_list(self, component_dict: Dict[str, Any]) -> List[Any]:
        """Transform dictionary of components to list."""
        if not isinstance(component_dict, dict):
            raise ValueError("Input must be a dictionary")

        return list(component_dict.values())

    def get_ontology_insights(self) -> Dict[str, Any]:
        """
        Get insights from the ontology about vocabulary alignment.

        Returns:
            Ontology insights and recommendations
        """
        try:
            logger.info("🔍 Gathering ontology insights...")

            insights = {
                "ontology_summary": {
                    "type": "SimpleOntologyBridge",
                    "domains": len(self.ontology["domains"]),
                    "transformations": len(self.ontology["transformations"]),
                    "vocabulary_mappings": len(self.ontology["vocabulary_mapping"]),
                },
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
                "validation_approach": "Ontological validation using domain rules and structure analysis",
                "transformation_approach": "Rule-based transformations with integrity validation",
            }

            return insights

        except Exception as e:
            logger.error(f"❌ Failed to get ontology insights: {e}")
            return {"error": str(e)}


def main():
    """Main function to demonstrate the simple ontology vocabulary bridge."""

    print("🌉 OpenFlow-Playground Simple Ontology Vocabulary Bridge")
    print("=" * 60)

    try:
        # Initialize the bridge
        bridge = SimpleOntologyBridge()

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

        print("✅ Transformation successful!")
        print(f"📊 Original: {type(sample_re_data).__name__} with {len(sample_re_data)} items")
        print(f"📊 Transformed: {type(transformed).__name__} with {len(transformed)} keys")
        print(f"📊 Keys: {list(transformed.keys())}")

        print("\n🎉 Simple ontology vocabulary bridge test completed successfully!")

    except Exception as e:
        print(f"❌ Bridge test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
