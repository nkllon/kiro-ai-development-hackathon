#!/usr/bin/env python3
"""
MDC Projector - Uses parser and model to project changes to MDC files
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from scripts.mdc_parser import MDCParser


class MDCProjector:
    """Projects model-driven changes to MDC files"""

    def __init__(self, model_path: str = "project_model_registry.json"):
        self.parser = MDCParser()
        self.model = self._load_model(model_path)
        self.mdc_domain = self.model["domains"]["mdc_cursor_rules"]

    def _load_model(self, model_path: str) -> dict[str, Any]:
        """Load the project model"""
        with open(model_path) as f:
            return json.load(f)

    def get_mdc_constraints(self) -> dict[str, Any]:
        """Get MDC domain constraints from model"""
        return self.mdc_domain.get("constraints", {})

    def get_generation_rules(self) -> list[str]:
        """Get MDC generation rules from model"""
        return self.mdc_domain.get("constraints", {}).get("generation_rules", [])

    def validate_against_model(self, file_path: str) -> dict[str, Any]:
        """
        Validate MDC file against model constraints

        Returns:
            Dict with validation results and recommendations
        """
        try:
            yaml_data, content = self.parser.parse_mdc(file_path)

            results = {
                "valid": True,
                "issues": [],
                "recommendations": [],
                "yaml_data": yaml_data,
            }

            # Check alwaysApply behavior
            always_apply = yaml_data.get("alwaysApply")
            if always_apply is None:
                results["issues"].append("Missing 'alwaysApply' field")
                results["recommendations"].append("Add alwaysApply: true for universal rules, false for selective")
            elif not isinstance(always_apply, bool):
                results["issues"].append("'alwaysApply' must be boolean")
                results["recommendations"].append("Use true/false, not quoted strings")

            # Check globs based on alwaysApply
            if always_apply is False:
                if "globs" not in yaml_data:
                    results["issues"].append("'globs' required when alwaysApply: false")
                    results["recommendations"].append("Add globs field with file patterns")
                elif not yaml_data["globs"]:
                    results["issues"].append("'globs' cannot be empty when alwaysApply: false")
                    results["recommendations"].append("Specify file patterns like '*.py,*.js,*.ts'")

            # Check for model compliance
            if "globs" in yaml_data:
                globs = yaml_data["globs"]
                if isinstance(globs, str) and "," in globs:
                    # Cursor format - good
                    pass
                elif isinstance(globs, list):
                    # Standard YAML format - might need conversion
                    results["recommendations"].append("Consider converting to Cursor format: comma-separated string")
                else:
                    results["issues"].append("Invalid globs format")
                    results["recommendations"].append("Use comma-separated string or YAML list")

            # Check for required fields
            required_fields = ["description"]
            for field in required_fields:
                if field not in yaml_data:
                    results["issues"].append(f"Missing required field: {field}")

            if results["issues"]:
                results["valid"] = False

            return results

        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Parsing error: {e}"],
                "recommendations": ["Check file structure and delimiters"],
                "yaml_data": {},
            }

    def project_fixes(self, file_path: str) -> dict[str, Any]:
        """
        Project fixes based on model constraints

        Returns:
            Dict with projected fixes
        """
        validation = self.validate_against_model(file_path)

        if validation["valid"]:
            return {
                "needs_fixes": False,
                "message": "File is already compliant with model",
                "issues": [],
                "recommendations": [],
                "fixes": {},
            }

        yaml_data = validation["yaml_data"]
        fixes = {}

        # Fix alwaysApply if needed
        if "alwaysApply" in yaml_data and not isinstance(yaml_data["alwaysApply"], bool):
            if yaml_data["alwaysApply"] == "true":
                fixes["alwaysApply"] = True
            elif yaml_data["alwaysApply"] == "false":
                fixes["alwaysApply"] = False

        # Fix globs if needed
        if "globs" in yaml_data:
            globs = yaml_data["globs"]
            if isinstance(globs, list):
                # Convert YAML list to Cursor format
                fixes["globs"] = ",".join(globs)
            elif isinstance(globs, str) and globs.startswith("[") and globs.endswith("]"):
                # Handle string that looks like a list
                try:
                    # Simple list parsing
                    items = [item.strip().strip("\"'") for item in globs[1:-1].split(",")]
                    fixes["globs"] = ",".join(items)
                except Exception:
                    pass

        # Add missing required fields
        if "description" not in yaml_data:
            fixes["description"] = f"Rule for {Path(file_path).stem}"

        return {
            "needs_fixes": bool(fixes),
            "fixes": fixes,
            "issues": validation["issues"],
            "recommendations": validation["recommendations"],
        }


def main():
    """Test the MDC projector"""
    projector = MDCProjector()

    print("MDC Projector Test")
    print("==================")

    # Test constraints
    constraints = projector.get_mdc_constraints()
    print(f"Model constraints: {constraints}")

    # Test generation rules
    rules = projector.get_generation_rules()
    print(f"Generation rules: {rules}")

    # Test validation on a file
    test_file = ".cursor/rules/security.mdc"
    if Path(test_file).exists():
        print(f"\nTesting {test_file}:")
        validation = projector.validate_against_model(test_file)
        print(f"Valid: {validation['valid']}")
        if validation["issues"]:
            print(f"Issues: {validation['issues']}")
        if validation["recommendations"]:
            print(f"Recommendations: {validation['recommendations']}")

        # Test projection
        projection = projector.project_fixes(test_file)
        print(f"Needs fixes: {projection['needs_fixes']}")
        if projection.get("fixes"):
            print(f"Projected fixes: {projection['fixes']}")


if __name__ == "__main__":
    main()
