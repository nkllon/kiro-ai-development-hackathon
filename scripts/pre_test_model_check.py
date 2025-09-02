#!/usr/bin/env python3
"""
Pre-test model consultation hook.
This script MUST be run before any testing to ensure model-driven approach.
"""

import json
import sys

# import subprocess  # REMOVED - replaced with secure_execute
from pathlib import Path
from typing import Any

from src.secure_shell_service.secure_executor import secure_execute


def load_project_model() -> dict[str, Any]:
    """Load the project model registry."""
    model_path = Path("project_model_registry.json")
    if not model_path.exists():
        print("❌ ERROR: project_model_registry.json not found!")
        print("   This is the single source of truth for tool orchestration.")
        sys.exit(1)

    with open(model_path) as f:
        data = json.load(f)
        assert isinstance(
            data,
            dict,
        ), "project_model_registry.json must be a JSON object"
        return data


def check_testing_domain(model: Any) -> Any:
    """Check the testing domain requirements."""
    testing_domain = model.get("domains", {}).get("testing", {})

    print("🔍 Checking testing domain requirements...")
    print(f"   Linter: {testing_domain.get('linter', 'NOT SET')}")
    print(f"   Formatter: {testing_domain.get('formatter', 'NOT SET')}")
    print(f"   Validator: {testing_domain.get('validator', 'NOT SET')}")
    print(f"   Type Checker: {testing_domain.get('type_checker', 'NOT SET')}")

    requirements = testing_domain.get("requirements", [])
    print(f"   Requirements: {len(requirements)} found")
    for req in requirements:
        print(f"     - {req}")

    return testing_domain


def run_model_driven_tests(model: Any, testing_domain: Any) -> None:
    """Run tests according to the model-driven approach."""
    print("\n🚀 Running model-driven tests...")

    # Step 1: Lint with flake8
    if testing_domain.get("linter") == "flake8":
        print("   Step 1: Running flake8 linting...")
        result = secure_execute(
            [
                "python",
                "-m",
                "flake8",
                "tests/",
                "--select=F401,E302,E305,W291,W292",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"   ⚠️  Linting issues found:\n{result.stdout}")
        else:
            print("   ✅ Linting passed")

    # Step 2: Format with black
    if testing_domain.get("formatter") == "black":
        print("   Step 2: Running black formatting...")
        result = secure_execute(
            ["python", "-m", "black", "tests/", "--check"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"   ⚠️  Formatting issues found:\n{result.stdout}")
        else:
            print("   ✅ Formatting passed")

    # Step 3: Type check with mypy
    if testing_domain.get("type_checker") == "mypy":
        print("   Step 3: Running mypy type checking...")
        result = secure_execute(
            ["python", "-m", "mypy", "tests/"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"   ⚠️  Type checking issues found:\n{result.stdout}")
        else:
            print("   ✅ Type checking passed")

    # Step 4: Run pytest
    if testing_domain.get("validator") == "pytest":
        print("   Step 4: Running pytest validation...")
        result = secure_execute(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )
        print(f"   📊 Test results:\n{result.stdout}")
        if result.stderr:
            print(f"   ⚠️  Test errors:\n{result.stderr}")


def main() -> None:
    """Main function - enforce model-driven testing."""
    print("🧪 MODEL-DRIVEN TESTING ENFORCEMENT")
    print("=" * 50)

    # Step 1: Load the model (MANDATORY)
    model = load_project_model()
    print("✅ Project model loaded successfully")

    # Step 2: Check testing domain
    testing_domain = check_testing_domain(model)

    # Step 3: Run model-driven tests
    run_model_driven_tests(model, testing_domain)

    print("\n🎯 Model-driven testing complete!")
    print("   Remember: Always consult project_model_registry.json first!")


if __name__ == "__main__":
    main()
