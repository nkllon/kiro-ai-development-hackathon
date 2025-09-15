#!/usr/bin/env python3
"""
Enhanced Interface Registry Validation Script
Validates all enhancements including:
- Method signature extraction accuracy
- File location tracking precision
- Domain vocabulary coverage
- Ubiquitous language indexing
- Registry integrity and performance
"""

import json
import os
from typing import Dict, List, Any
from collections import Counter


def load_enhanced_registry() -> Dict[str, Any]:
    """Load the enhanced interface registry."""
    try:
        with open(".beast_mode/enhanced_interface_registry.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Enhanced registry not found")
        return {}


def load_expanded_vocabulary() -> Dict[str, Any]:
    """Load the expanded domain vocabulary."""
    try:
        with open(".beast_mode/expanded_domain_vocabulary.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Expanded vocabulary not found")
        return {}


def validate_method_signatures(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate method signature extraction."""
    validation_results = {
        "total_interfaces": 0,
        "interfaces_with_methods": 0,
        "total_methods": 0,
        "methods_with_signatures": 0,
        "methods_with_docstrings": 0,
        "methods_with_type_annotations": 0,
        "signature_completeness": 0.0,
        "common_method_patterns": Counter(),
        "validation_errors": [],
    }

    for interface_id, interface_data in data.get("interfaces", {}).items():
        validation_results["total_interfaces"] += 1

        methods = interface_data.get("methods", [])
        if methods:
            validation_results["interfaces_with_methods"] += 1

        for method in methods:
            validation_results["total_methods"] += 1

            # Check method signature completeness
            has_name = bool(method.get("name"))
            has_parameters = "parameters" in method
            has_return_type = bool(method.get("return_type"))
            has_docstring = bool(method.get("docstring"))

            if has_name and has_parameters:
                validation_results["methods_with_signatures"] += 1

            if has_docstring:
                validation_results["methods_with_docstrings"] += 1

            if has_return_type:
                validation_results["methods_with_type_annotations"] += 1

            # Track common method patterns
            method_name = method.get("name", "")
            if method_name:
                validation_results["common_method_patterns"][method_name] += 1

    # Calculate completeness percentage
    if validation_results["total_methods"] > 0:
        validation_results["signature_completeness"] = round(
            validation_results["methods_with_signatures"]
            / validation_results["total_methods"]
            * 100,
            2,
        )

    return validation_results


def validate_file_tracking(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate file location tracking precision."""
    validation_results = {
        "total_interfaces": 0,
        "interfaces_with_precise_locations": 0,
        "location_precision_rate": 0.0,
        "file_path_accuracy": 0,
        "line_number_accuracy": 0,
        "end_line_accuracy": 0,
        "location_validation_errors": [],
    }

    for interface_id, interface_data in data.get("interfaces", {}).items():
        validation_results["total_interfaces"] += 1

        file_path = interface_data.get("file_path", "")
        line_number = interface_data.get("line_number", 0)
        end_line_number = interface_data.get("end_line_number", 0)

        # Validate file path exists
        if file_path and os.path.exists(file_path):
            validation_results["file_path_accuracy"] += 1
        else:
            validation_results["location_validation_errors"].append(
                f"File not found: {file_path}"
            )

        # Validate line numbers
        if line_number > 0:
            validation_results["line_number_accuracy"] += 1

        if end_line_number > 0 and end_line_number >= line_number:
            validation_results["end_line_accuracy"] += 1
            validation_results["interfaces_with_precise_locations"] += 1

    # Calculate precision rate
    if validation_results["total_interfaces"] > 0:
        validation_results["location_precision_rate"] = round(
            validation_results["interfaces_with_precise_locations"]
            / validation_results["total_interfaces"]
            * 100,
            2,
        )

    return validation_results


def validate_domain_vocabulary(
    registry_data: Dict[str, Any], vocabulary_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate domain vocabulary coverage and indexing."""
    validation_results = {
        "total_domain_terms": 0,
        "terms_used_in_interfaces": 0,
        "vocabulary_coverage_rate": 0.0,
        "ubiquitous_language_terms": 0,
        "ubiquitous_language_usage": 0,
        "ubiquitous_coverage_rate": 0.0,
        "semantic_relationships": 0,
        "vocabulary_validation_errors": [],
    }

    # Get vocabulary data
    domain_terms = set(vocabulary_data.get("domain_terms", []))
    ubiquitous_terms = set(vocabulary_data.get("ubiquitous_language", []))
    relationships = vocabulary_data.get("semantic_relationships", {})

    validation_results["total_domain_terms"] = len(domain_terms)
    validation_results["ubiquitous_language_terms"] = len(ubiquitous_terms)
    validation_results["semantic_relationships"] = len(relationships)

    # Check usage in interfaces
    used_domain_terms = set()
    used_ubiquitous_terms = set()

    for interface_id, interface_data in registry_data.get("interfaces", {}).items():
        interface_domain_terms = set(interface_data.get("domain_terms", []))
        interface_ubiquitous_terms = set(interface_data.get("ubiquitous_language", []))

        used_domain_terms.update(interface_domain_terms)
        used_ubiquitous_terms.update(interface_ubiquitous_terms)

    validation_results["terms_used_in_interfaces"] = len(used_domain_terms)
    validation_results["ubiquitous_language_usage"] = len(used_ubiquitous_terms)

    # Calculate coverage rates
    if validation_results["total_domain_terms"] > 0:
        validation_results["vocabulary_coverage_rate"] = round(
            validation_results["terms_used_in_interfaces"]
            / validation_results["total_domain_terms"]
            * 100,
            2,
        )

    if validation_results["ubiquitous_language_terms"] > 0:
        validation_results["ubiquitous_coverage_rate"] = round(
            validation_results["ubiquitous_language_usage"]
            / validation_results["ubiquitous_language_terms"]
            * 100,
            2,
        )

    return validation_results


def validate_registry_integrity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate overall registry integrity and consistency."""
    validation_results = {
        "total_interfaces": 0,
        "interfaces_with_metadata": 0,
        "compliance_scores_valid": 0,
        "average_compliance": 0.0,
        "interface_types_valid": 0,
        "registry_consistency_score": 0.0,
        "integrity_errors": [],
    }

    compliance_scores = []
    valid_interface_types = {
        "reflective_module",
        "domain_service",
        "api_interface",
        "data_model",
        "validation_rule",
        "configuration",
    }

    for interface_id, interface_data in data.get("interfaces", {}).items():
        validation_results["total_interfaces"] += 1

        # Check required metadata
        required_fields = [
            "interface_name",
            "interface_type",
            "file_path",
            "line_number",
        ]
        has_metadata = all(field in interface_data for field in required_fields)

        if has_metadata:
            validation_results["interfaces_with_metadata"] += 1

        # Validate compliance scores
        compliance_score = interface_data.get("compliance_score", 0)
        if isinstance(compliance_score, (int, float)) and 0 <= compliance_score <= 100:
            validation_results["compliance_scores_valid"] += 1
            compliance_scores.append(compliance_score)

        # Validate interface types
        interface_type = interface_data.get("interface_type", "")
        if interface_type in valid_interface_types:
            validation_results["interface_types_valid"] += 1
        else:
            validation_results["integrity_errors"].append(
                f"Invalid interface type: {interface_type}"
            )

    # Calculate average compliance
    if compliance_scores:
        validation_results["average_compliance"] = round(
            sum(compliance_scores) / len(compliance_scores), 2
        )

    # Calculate overall consistency score
    if validation_results["total_interfaces"] > 0:
        consistency_factors = [
            validation_results["interfaces_with_metadata"]
            / validation_results["total_interfaces"],
            validation_results["compliance_scores_valid"]
            / validation_results["total_interfaces"],
            validation_results["interface_types_valid"]
            / validation_results["total_interfaces"],
        ]
        validation_results["registry_consistency_score"] = round(
            sum(consistency_factors) / len(consistency_factors) * 100, 2
        )

    return validation_results


def generate_validation_report(
    registry_data: Dict[str, Any], vocabulary_data: Dict[str, Any]
) -> None:
    """Generate comprehensive validation report."""
    print("🔍 Enhanced Interface Registry Validation Report")
    print("=" * 60)

    # Method signature validation
    print("\n🔧 Method Signature Validation:")
    method_validation = validate_method_signatures(registry_data)
    print(f"   Total interfaces: {method_validation['total_interfaces']}")
    print(f"   Interfaces with methods: {method_validation['interfaces_with_methods']}")
    print(f"   Total methods: {method_validation['total_methods']}")
    print(f"   Methods with signatures: {method_validation['methods_with_signatures']}")
    print(f"   Methods with docstrings: {method_validation['methods_with_docstrings']}")
    print(
        f"   Methods with type annotations: {method_validation['methods_with_type_annotations']}"
    )
    print(f"   Signature completeness: {method_validation['signature_completeness']}%")

    print(f"\n   Most common method names:")
    for method_name, count in method_validation["common_method_patterns"].most_common(
        10
    ):
        print(f"     {method_name}: {count}")

    # File tracking validation
    print(f"\n📍 File Location Tracking Validation:")
    location_validation = validate_file_tracking(registry_data)
    print(f"   Total interfaces: {location_validation['total_interfaces']}")
    print(
        f"   Interfaces with precise locations: {location_validation['interfaces_with_precise_locations']}"
    )
    print(
        f"   Location precision rate: {location_validation['location_precision_rate']}%"
    )
    print(
        f"   File path accuracy: {location_validation['file_path_accuracy']}/{location_validation['total_interfaces']}"
    )
    print(
        f"   Line number accuracy: {location_validation['line_number_accuracy']}/{location_validation['total_interfaces']}"
    )
    print(
        f"   End line accuracy: {location_validation['end_line_accuracy']}/{location_validation['total_interfaces']}"
    )

    if location_validation["location_validation_errors"]:
        print(
            f"   Location errors: {len(location_validation['location_validation_errors'])}"
        )
        for error in location_validation["location_validation_errors"][:5]:
            print(f"     - {error}")

    # Domain vocabulary validation
    print(f"\n📚 Domain Vocabulary Validation:")
    vocabulary_validation = validate_domain_vocabulary(registry_data, vocabulary_data)
    print(f"   Total domain terms: {vocabulary_validation['total_domain_terms']}")
    print(
        f"   Terms used in interfaces: {vocabulary_validation['terms_used_in_interfaces']}"
    )
    print(
        f"   Domain vocabulary coverage: {vocabulary_validation['vocabulary_coverage_rate']}%"
    )
    print(
        f"   Ubiquitous language terms: {vocabulary_validation['ubiquitous_language_terms']}"
    )
    print(
        f"   Ubiquitous language usage: {vocabulary_validation['ubiquitous_language_usage']}"
    )
    print(
        f"   Ubiquitous language coverage: {vocabulary_validation['ubiquitous_coverage_rate']}%"
    )
    print(
        f"   Semantic relationships: {vocabulary_validation['semantic_relationships']}"
    )

    # Registry integrity validation
    print(f"\n✅ Registry Integrity Validation:")
    integrity_validation = validate_registry_integrity(registry_data)
    print(f"   Total interfaces: {integrity_validation['total_interfaces']}")
    print(
        f"   Interfaces with metadata: {integrity_validation['interfaces_with_metadata']}"
    )
    print(
        f"   Valid compliance scores: {integrity_validation['compliance_scores_valid']}"
    )
    print(f"   Average compliance: {integrity_validation['average_compliance']}%")
    print(f"   Valid interface types: {integrity_validation['interface_types_valid']}")
    print(
        f"   Registry consistency score: {integrity_validation['registry_consistency_score']}%"
    )

    if integrity_validation["integrity_errors"]:
        print(f"   Integrity errors: {len(integrity_validation['integrity_errors'])}")
        for error in integrity_validation["integrity_errors"][:5]:
            print(f"     - {error}")

    # Overall assessment
    print(f"\n🎯 Overall Enhancement Assessment:")

    enhancement_scores = {
        "Method Signatures": method_validation["signature_completeness"],
        "File Tracking": location_validation["location_precision_rate"],
        "Domain Vocabulary": vocabulary_validation["vocabulary_coverage_rate"],
        "Registry Integrity": integrity_validation["registry_consistency_score"],
    }

    overall_score = sum(enhancement_scores.values()) / len(enhancement_scores)

    print(
        f"   Method signature enhancement: {enhancement_scores['Method Signatures']}%"
    )
    print(f"   File location tracking: {enhancement_scores['File Tracking']}%")
    print(f"   Domain vocabulary coverage: {enhancement_scores['Domain Vocabulary']}%")
    print(f"   Registry integrity: {enhancement_scores['Registry Integrity']}%")
    print(f"   Overall enhancement score: {overall_score:.2f}%")

    # Enhancement status
    if overall_score >= 90:
        status = "🟢 EXCELLENT"
    elif overall_score >= 80:
        status = "🟡 GOOD"
    elif overall_score >= 70:
        status = "🟠 FAIR"
    else:
        status = "🔴 NEEDS IMPROVEMENT"

    print(f"\n📊 Enhancement Status: {status}")

    print(f"\n🎉 Enhanced Interface Registry Validation Complete!")


def main():
    """Main execution function."""
    print("🚀 Enhanced Interface Registry Validation")
    print("=" * 50)

    # Load data
    registry_data = load_enhanced_registry()
    vocabulary_data = load_expanded_vocabulary()

    if not registry_data:
        print("❌ Cannot validate: Enhanced registry not found")
        return

    if not vocabulary_data:
        print("❌ Cannot validate: Expanded vocabulary not found")
        return

    # Generate validation report
    generate_validation_report(registry_data, vocabulary_data)


if __name__ == "__main__":
    main()
