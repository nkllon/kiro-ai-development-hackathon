#!/usr/bin/env python3
"""
Model Conformance Check Script

This script checks that all Python files conform to their extracted models.
It ensures that the round-trip process maintains model compliance.

Usage:
    python scripts/check_model_conformance.py <python_file>
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.round_trip_engineering import EnhancedReverseEngineer

    ENHANCED_REVERSE_ENGINEER_AVAILABLE = True
except ImportError:
    ENHANCED_REVERSE_ENGINEER_AVAILABLE = False
    print("⚠️  Enhanced reverse engineer not available")


class ModelConformanceChecker:
    """Checks model conformance for Python files"""

    def __init__(self):
        self.reverse_engineer = None
        if ENHANCED_REVERSE_ENGINEER_AVAILABLE:
            self.reverse_engineer = EnhancedReverseEngineer()

    def check_model_conformance(self, file_path: str) -> dict:
        """Check if a Python file conforms to its extracted model"""
        print(f"🔍 Checking model conformance for: {file_path}")

        if not self.reverse_engineer:
            return {
                "success": False,
                "error": "No reverse engineer available",
                "file": file_path,
            }

        try:
            # Extract model from current file
            print("  📥 Extracting current model...")
            current_model = self.reverse_engineer.reverse_engineer_file(file_path)

            if not current_model:
                return {
                    "success": False,
                    "error": "Failed to extract model from current file",
                    "file": file_path,
                }

            # Check model structure and completeness
            print("  🔍 Analyzing model structure...")
            conformance_result = self.analyze_model_conformance(current_model)

            return {
                "success": True,
                "file": file_path,
                "model_components": len(current_model.get("components", {})),
                "model_lines": current_model.get("total_lines", 0),
                "imports": len(current_model.get("imports", [])),
                "conformance": conformance_result,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "file": file_path}

    def analyze_model_conformance(self, model: dict) -> dict:
        """Analyze model conformance and completeness"""
        components = model.get("components", {})
        imports = model.get("imports", [])
        used_names = model.get("used_names", [])

        # Check component completeness
        component_analysis = {}
        for class_name, class_info in components.items():
            methods = class_info.get("methods", [])
            implemented_methods = [m for m in methods if m.get("implementation_status") == "implemented"]

            component_analysis[class_name] = {
                "total_methods": len(methods),
                "implemented_methods": len(implemented_methods),
                "implementation_ratio": (len(implemented_methods) / len(methods) if methods else 0),
                "has_body_content": all(m.get("body") and len(m.get("body", [])) > 0 for m in implemented_methods),
            }

        # Check import completeness
        import_analysis = {
            "total_imports": len(imports),
            "import_types": self.categorize_imports(imports),
            "used_names_coverage": len(used_names) if used_names else 0,
        }

        # Check overall model quality
        model_quality = {
            "has_components": len(components) > 0,
            "has_imports": len(imports) > 0,
            "has_used_names": len(used_names) > 0,
            "components_complete": (all(analysis["implementation_ratio"] > 0.8 for analysis in component_analysis.values()) if component_analysis else False),
        }

        return {
            "components": component_analysis,
            "imports": import_analysis,
            "quality": model_quality,
            "overall_score": self.calculate_conformance_score(component_analysis, import_analysis, model_quality),
        }

    def categorize_imports(self, imports: list[str]) -> dict[str, int]:
        """Categorize imports by type"""
        categories = {"standard_library": 0, "third_party": 0, "local": 0, "unknown": 0}

        for imp in imports:
            if imp.startswith(
                (
                    "from typing import",
                    "import os",
                    "import sys",
                    "from pathlib import",
                    "import pathlib",
                )
            ):
                categories["standard_library"] += 1
            elif imp.startswith(("from base_expert import", "import base_expert")):
                categories["local"] += 1
            elif imp.startswith(("from ", "import ")):
                categories["third_party"] += 1
            else:
                categories["unknown"] += 1

        return categories

    def calculate_conformance_score(self, components: dict, imports: dict, quality: dict) -> float:
        """Calculate overall conformance score (0.0 to 1.0)"""
        scores = []

        # Component completeness score
        if components:
            component_scores = [analysis["implementation_ratio"] for analysis in components.values()]
            scores.append(sum(component_scores) / len(component_scores))
        else:
            scores.append(0.0)

        # Import completeness score
        if imports["total_imports"] > 0:
            scores.append(1.0)  # Has imports
        else:
            scores.append(0.0)

        # Quality indicators score
        quality_scores = [
            1.0 if quality["has_components"] else 0.0,
            1.0 if quality["has_imports"] else 0.0,
            1.0 if quality["components_complete"] else 0.0,
        ]
        scores.append(sum(quality_scores) / len(quality_scores))

        return sum(scores) / len(scores)


def main():
    """Main entry point"""
    # Handle pre-commit mode
    if len(sys.argv) > 1 and sys.argv[1] == "--pre-commit":
        # Pre-commit mode: process all staged Python files
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
                capture_output=True,
                text=True,
                check=True,
            )
            python_files = [f for f in result.stdout.strip().split("\n") if f.endswith(".py") and f]

            if not python_files:
                print("✅ No Python files to check")
                sys.exit(0)

            checker = ModelConformanceChecker()
            all_success = True

            for file_path in python_files:
                if os.path.exists(file_path):
                    print(f"🔍 Checking model conformance for: {file_path}")
                    result = checker.check_model_conformance(file_path)
                    if result["success"]:
                        print(f"✅ Model conformance passed for: {file_path}")
                    else:
                        print(f"❌ Model conformance failed for: {file_path}")
                        all_success = False

            sys.exit(0 if all_success else 1)
        except subprocess.CalledProcessError:
            print("⚠️  Could not determine staged files, skipping model conformance check")
            sys.exit(0)
    elif len(sys.argv) != 2:
        print("Usage: python scripts/check_model_conformance.py <python_file>")
        print("       python scripts/check_model_conformance.py --pre-commit")
        sys.exit(1)
    else:
        file_path = sys.argv[1]

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        if not file_path.endswith(".py"):
            print(f"❌ Not a Python file: {file_path}")
            sys.exit(1)

        # Check model conformance
        checker = ModelConformanceChecker()
        result = checker.check_model_conformance(file_path)

        if result["success"]:
            print(f"✅ Model conformance check PASSED for {file_path}")
            print(f"   📦 Model components: {result['model_components']}")
            print(f"   📏 Model lines: {result['model_lines']}")
            print(f"   📥 Imports: {result['imports']}")

            # Show conformance details
            conformance = result["conformance"]
            overall_score = conformance["overall_score"]

            print(f"   🎯 Overall conformance score: {overall_score:.2%}")

            # Component analysis
            for class_name, analysis in conformance["components"].items():
                print(f"   🏗️  {class_name}: {analysis['implemented_methods']}/{analysis['total_methods']} methods implemented")

            # Import analysis
            import_cats = conformance["imports"]["import_types"]
            print("   📥 Import breakdown:")
            for category, count in import_cats.items():
                if count > 0:
                    print(f"      {category}: {count}")

            # Quality indicators
            quality = conformance["quality"]
            if quality["components_complete"]:
                print("   ✅ All components are complete")
            else:
                print("   ⚠️  Some components are incomplete")

            # Exit with success
            sys.exit(0)
        else:
            print(f"❌ Model conformance check FAILED for {file_path}")
            print(f"   🚨 Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
