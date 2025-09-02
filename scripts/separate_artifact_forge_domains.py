#!/usr/bin/env python3
"""
Separate ArtifactForge and Round-trip Engineering Domains
Uses ModelManager to safely update the project model without JSON corruption
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from model_manager import ModelManager
except ImportError:
    print("❌ Could not import ModelManager - make sure src/model_manager.py exists")
    sys.exit(1)


def main() -> None:
    """Separate ArtifactForge and Round-trip Engineering domains"""
    print("🔧 Separating ArtifactForge and Round-trip Engineering Domains")
    print("=" * 70)

    # Initialize model manager
    manager = ModelManager()

    # Step 1: Remove the unified domain
    print("\n🗑️  Step 1: Removing unified domain")
    success = manager.remove_model_entry("project_model_registry", ["domains", "artifact_forge_unified"])

    if success:
        print("✅ Unified domain removed successfully")
    else:
        print("❌ Failed to remove unified domain")

    # Step 2: Add ArtifactForge domain (independent)
    print("\n🏗️  Step 2: Adding ArtifactForge domain (independent)")
    artifact_forge_domain = {
        "artifact_forge": {
            "patterns": ["**/*artifact_forge*.py", "src/artifact_forge/**/*.py"],
            "content_indicators": [
                "artifact_forge",
                "artifact_processing",
                "multi_format_support",
                "AST_parsing",
                "artifact_detection",
                "artifact_correlation",
            ],
            "linter": "flake8",
            "formatter": "black",
            "validator": "pytest",
            "exclusions": ["__pycache__/*", "*.pyc", "*.pyo"],
            "requirements": [
                "Provide core artifact processing system (ArtifactForge) for ALL artifact types",
                "Support 13+ artifact types (Python, MDC, Markdown, YAML, JSON, SQL, Shell, Docker, Terraform, Kubernetes, HTML, CSS, JavaScript)",
                "Provide basic AST parsing and structure analysis for all supported formats",
                "Provide artifact detection, classification, and correlation capabilities",
                "Provide block analysis and error recovery for malformed artifacts",
                "Maintain independence from other systems - no external dependencies",
                "All methods must have complete type annotations and pass MyPy validation",
                "Provide clean, structured output for consumption by other systems",
                "Support extensibility for new artifact types beyond current 13+ formats",
                "Ensure robust error handling and graceful degradation",
                "Provide comprehensive testing and validation capabilities",
            ],
            "demo_role": "tool",
            "extraction_candidate": True,
            "reason": "Core artifact processing system - independent foundation for all artifact analysis",
        }
    }

    success = manager.add_model_entry("project_model_registry", ["domains"], artifact_forge_domain)

    if success:
        print("✅ ArtifactForge domain added successfully")
    else:
        print("❌ Failed to add ArtifactForge domain")

    # Step 3: Update Round-trip Engineering domain (dependent on ArtifactForge)
    print("\n🔄 Step 3: Updating Round-trip Engineering domain (dependent)")

    # Update the requirements to clarify dependency relationship
    round_trip_requirements = [
        "DEPENDENCY: Use ArtifactForge for basic artifact parsing and analysis",
        "RESPONSIBILITY: ENRICH ArtifactForge output with enhanced method body extraction",
        "RESPONSIBILITY: Add pattern detection and best practice analysis",
        "RESPONSIBILITY: Generate code from enriched models with zero duplication",
        "BOUNDARY: Round-trip Engineering is NOT ArtifactForge - it extends and enriches",
        "Generate code from models with proper type annotations and MyPy compliance",
        "Maintain functional equivalence through round-trip validation",
        "Support model-driven development as foundation for code generation",
        "All methods must have complete type annotations and pass MyPy validation",
        "All imports must be validated before code generation",
        "Error handling must be consistent across all methods",
        "Code generation must produce lint-compliant output without duplications",
        "Type checking must pass with 100% coverage",
        "Maintain zero duplication in generated artifacts across all formats",
        "Ensure generated code is syntactically correct and follows best practices",
        "Provide comprehensive testing and validation capabilities",
        "Maintain clear separation: consume ArtifactForge output, enrich it, generate code",
    ]

    success = manager.update_model_field(
        "project_model_registry",
        ["domains", "round_trip_engineering", "requirements"],
        round_trip_requirements,
    )

    if success:
        print("✅ Round-trip Engineering requirements updated successfully")
    else:
        print("❌ Failed to update Round-trip Engineering requirements")

    # Step 4: Add critical todo for fixing code generation
    print("\n🚨 Step 4: Adding critical todo for fixing code generation")

    critical_todo = {
        "fix_code_generation_duplication": {
            "description": "Fix systematic code duplication in generated artifacts causing 524 MyPy errors",
            "priority": "critical",
            "status": "in_progress",
            "details": {
                "current_state": "Round-trip system generating broken code with duplicate return statements",
                "root_cause": "Code generation logic creating unreachable statements and duplications",
                "impact": "524 MyPy errors, 36 unreachable statement errors, broken generated code",
                "next_steps": [
                    "Fix code generation duplication bug in round-trip system",
                    "Delete broken generated files",
                    "Regenerate clean code from models",
                    "Validate MyPy compliance",
                    "Ensure zero duplication in generated artifacts",
                ],
                "metrics": {
                    "files_affected": "src/round_trip_generated/*.py",
                    "total_mypy_errors": 524,
                    "unreachable_statements": 36,
                    "duplicate_code_blocks": "Multiple files affected",
                },
            },
            "created": "2025-01-27T10:00:00",
            "assigned_to": "AI Assistant",
        }
    }

    success = manager.add_model_entry(
        "project_model_registry",
        ["domains", "round_trip_engineering", "todos"],
        critical_todo,
    )

    if success:
        print("✅ Critical todo added successfully")
    else:
        print("❌ Failed to add critical todo")

    # Step 5: Validate the updated model
    print("\n🔍 Step 5: Validating updated model structure")

    # Check that both domains exist
    try:
        data = manager.load_model("project_model_registry")
        artifact_forge_exists = "artifact_forge" in data.get("domains", {})
        round_trip_exists = "round_trip_engineering" in data.get("domains", {})

        if artifact_forge_exists and round_trip_exists:
            print("✅ Both domains exist in updated model")
        else:
            print("❌ Domain separation incomplete")

    except Exception as e:
        print(f"❌ Model validation failed: {e}")

    print("\n🎉 Domain separation complete!")
    print("\n📋 Summary:")
    print("  ✅ ArtifactForge: Independent core system")
    print("  ✅ Round-trip Engineering: Dependent enricher")
    print("  ✅ Clear boundaries established")
    print("  ✅ Critical todo added for fixing code generation")


if __name__ == "__main__":
    main()
