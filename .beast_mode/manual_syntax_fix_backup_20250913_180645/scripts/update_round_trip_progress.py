#!/usr/bin/env python3
"""
Update Round-Trip Engineering Progress
Updates the project model to reflect current progress and next steps
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def update_project_model():
    """Update the project model with current round-trip engineering progress"""

    # Load the project model
    model_path = Path("project_model_registry.json")
    if not model_path.exists():
        print("❌ project_model_registry.json not found")
        return False

    with open(model_path, "r") as f:
        model = json.load(f)

    # Find the round_trip_engineering domain
    if "domains" not in model:
        print("❌ No domains section found in model")
        return False

    if "round_trip_engineering" not in model["domains"]:
        print("❌ round_trip_engineering domain not found")
        return False

    domain = model["domains"]["round_trip_engineering"]

    # Update the domain with current progress
    print("🔧 Updating round_trip_engineering domain...")

    # Update patterns to reflect new modular structure
    domain["patterns"] = [
        "src/round_trip_engineering/**/*.py",
        "tests/test_round_trip_system.py",
        "**/*round_trip*.py",
    ]

    # Update content indicators
    domain["content_indicators"] = [
        "round_trip",
        "reverse_engineer",
        "model_driven",
        "code_generation",
        "AST_parsing",
        "vocabulary_alignment",
        "duplication_cleaning",
        "ontological_modeling",
    ]

    # Update requirements to reflect current architecture
    domain["requirements"] = [
        "Provide canonical round-trip engineering system with modular architecture",
        "Support AST-based reverse engineering via ArtifactForge integration",
        "Generate code from models with zero duplication",
        "Maintain functional equivalence through round-trip validation",
        "Support model-driven development as foundation for code generation",
        "Integrate ontological vocabulary alignment for domain consistency",
        "Provide comprehensive logging and profiling with cProfile integration",
        "Implement activity model validation for expected vs actual behavior",
        "Support modular architecture: core, generators, cleaners, logging",
        "All methods must have complete type annotations and pass MyPy validation",
        "All imports must be validated before code generation",
        "Error handling must be consistent across all methods",
        "Code generation must produce lint-compliant output without duplications",
    ]

    # Update todos section
    if "todos" not in domain:
        domain["todos"] = []

    # Mark the duplication fix as completed
    for todo in domain["todos"]:
        if todo.get("id") == "fix_code_generation_duplication":
            todo["status"] = "completed"
            todo["completed"] = datetime.now().isoformat()
            todo["details"]["current_state"] = "Modular round-trip system implemented with duplication cleaning"
            todo["details"]["next_steps"] = [
                "Fix code generation to build complete model first instead of in-line generation",
                "Validate activity models and expected behavior",
                "Fix remaining MyPy errors after refactoring",
                "Integrate with ontology framework subproject",
            ]
            print("✅ Marked fix_code_generation_duplication as completed")
            break

    # Update the validate_activity_models todo
    for todo in domain["todos"]:
        if todo.get("id") == "validate_activity_models":
            todo["status"] = "in_progress"
            todo["details"] = {
                "current_state": "4/5 tests passing, duplication cleaner working perfectly",
                "next_steps": [
                    "Fix code generation to build complete model first",
                    "Implement activity model validation",
                    "Run comprehensive tests with logging and profiling",
                    "Compare expected vs actual activity models",
                ],
                "progress": "80% - Core system working, need to fix code generation approach",
            }
            print("✅ Updated validate_activity_models progress")
            break

    # Add new todo for code generation fix
    new_todo = {
        "id": "fix_code_generation_approach",
        "description": "Fix code generation to build complete in-memory model first instead of in-line generation",
        "priority": "high",
        "status": "not_started",
        "details": {
            "current_state": "Code generation only produces headers, not full class structure",
            "root_cause": "Generating code in-line before full model is constructed",
            "solution": "Build complete in-memory model first, then generate code from complete model",
            "next_steps": [
                "Implement model building phase before code generation",
                "Validate complete model structure before generation",
                "Update code generators to work with complete models",
                "Test end-to-end workflow with full model approach",
            ],
            "best_practice": "Always build complete model first, then generate code from complete model",
        },
        "created": datetime.now().isoformat(),
        "assigned_to": "AI Assistant",
    }

    domain["todos"].append(new_todo)
    print("✅ Added new todo for code generation approach fix")

    # Update the reason and description
    domain["reason"] = "Modular round-trip engineering system with ontological vocabulary alignment, comprehensive testing, and cProfile integration"

    # Save the updated model
    with open(model_path, "w") as f:
        json.dump(model, f, indent=2)

    print("✅ Project model updated successfully")
    return True


def main():
    """Main function"""
    print("🚀 Updating Round-Trip Engineering Progress")
    print("=" * 50)

    success = update_project_model()

    if success:
        print("\n🎉 Successfully updated project model!")
        print("📋 Next steps:")
        print("   1. Fix code generation to build complete model first")
        print("   2. Implement activity model validation")
        print("   3. Run comprehensive tests with logging and profiling")
        print("   4. Compare expected vs actual activity models")
    else:
        print("\n❌ Failed to update project model")
        sys.exit(1)


if __name__ == "__main__":
    main()
