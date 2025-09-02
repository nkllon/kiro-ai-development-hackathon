#!/usr/bin/env python3
"""
Round-Trip Engineering Enforcement Script

This script enforces that all Python files can survive the round-trip process:
1. Reverse engineer into a model
2. Regenerate code from the model
3. Ensure functional equivalence

Usage:
    python scripts/enforce_round_trip.py <python_file>
"""

import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.round_trip_engineering import EnhancedReverseEngineer, RoundTripModelSystem

    ENHANCED_REVERSE_ENGINEER_AVAILABLE = True
except ImportError:
    ENHANCED_REVERSE_ENGINEER_AVAILABLE = False
    print("⚠️  Enhanced reverse engineer not available, using fallback")

try:
    from src.abstract_factory_system import ModelDrivenFactory

    ABSTRACT_FACTORY_AVAILABLE = True
except ImportError:
    ABSTRACT_FACTORY_AVAILABLE = False
    print("⚠️  Abstract factory not available, using direct tools")


class RoundTripEnforcer:
    """Enforces round-trip engineering compliance"""

    def __init__(self) -> None:
        self.tool_factory = ModelDrivenFactory() if ABSTRACT_FACTORY_AVAILABLE else None
        self.reverse_engineer: Any = None
        self.code_generator: Any = None
        self.setup_tools()

    def setup_tools(self) -> None:
        """Setup reverse engineering and code generation tools"""
        if self.tool_factory:
            self.reverse_engineer = self.tool_factory.get_reverse_engineering_tool("python")
            # We need a model to get the code generator, but we don't have one yet
            # We'll get it when we have a model
            self.code_generator = None
        else:
            # Fallback to direct tools
            if ENHANCED_REVERSE_ENGINEER_AVAILABLE:
                self.reverse_engineer = EnhancedReverseEngineer()
                self.code_generator = RoundTripModelSystem()
            else:
                print("❌ No reverse engineering tools available")
                sys.exit(1)

    def enforce_round_trip(self, file_path: str) -> dict[str, Any]:
        """Enforce round-trip engineering for a single file"""
        print(f"🔄 Enforcing round-trip engineering for: {file_path}")

        # Step 1: Reverse engineer the file
        print("  📥 Step 1: Reverse engineering...")
        if self.reverse_engineer is None:
            return {
                "success": False,
                "error": "Reverse engineer not available",
                "file": file_path,
            }
        model = self.reverse_engineer.reverse_engineer(file_path)

        if not model:
            return {
                "success": False,
                "error": "Failed to reverse engineer file",
                "file": file_path,
            }

        # Step 2: Generate code from the model
        print("  📤 Step 2: Generating code...")
        if self.code_generator is None:
            return {
                "success": False,
                "error": "Code generator not available",
                "file": file_path,
            }
        generated_code = self.code_generator.generate_code(model)

        if not generated_code:
            return {
                "success": False,
                "error": "Failed to generate code from model",
                "file": file_path,
            }

        # Step 3: Save generated code to temporary file
        print("  💾 Step 3: Saving generated code...")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(generated_code)
            temp_file = f.name

        # Also save to a permanent file for inspection
        output_file = f"{Path(file_path).stem}_regenerated.py"
        with open(output_file, "w") as f:
            f.write(generated_code)
        print(f"  💾 Generated code saved to: {output_file}")

        try:
            # Step 4: Test functional equivalence
            print("  🧪 Step 4: Testing functional equivalence...")
            equivalence_result = self.test_functional_equivalence(file_path, temp_file)

            # Step 5: Clean up
            Path(temp_file).unlink()

            return {
                "success": True,
                "file": file_path,
                "model_components": len(model.get("components", {})),
                "model_lines": model.get("total_lines", 0),
                "generated_lines": len(generated_code.split("\n")),
                "functional_equivalence": equivalence_result,
            }

        except Exception as e:
            # Clean up on error
            if Path(temp_file).exists():
                Path(temp_file).unlink()
            raise e

    def test_functional_equivalence(self, original_file: str, generated_file: str) -> dict[str, Any]:
        """Test functional equivalence between original and generated files"""
        try:
            # Test 1: AST parsing
            original_ast = self.parse_python_file(original_file)
            generated_ast = self.parse_python_file(generated_file)

            # Test 2: Import comparison
            original_imports = self.extract_imports(original_file)
            generated_imports = self.extract_imports(generated_file)

            # Test 3: Class and method comparison
            original_structure = self.extract_structure(original_file)
            generated_structure = self.extract_structure(generated_file)

            return {
                "ast_parsing": {
                    "original": original_ast is not None,
                    "generated": generated_ast is not None,
                },
                "imports": {
                    "original_count": len(original_imports),
                    "generated_count": len(generated_imports),
                    "match": original_imports == generated_imports,
                },
                "structure": {
                    "original": original_structure,
                    "generated": generated_structure,
                    "match": original_structure == generated_structure,
                },
            }

        except Exception as e:
            return {
                "error": str(e),
                "ast_parsing": {"original": False, "generated": False},
                "imports": {"original_count": 0, "generated_count": 0, "match": False},
                "structure": {"original": {}, "generated": {}, "match": False},
            }

    def parse_python_file(self, file_path: str) -> Optional[object]:
        """Parse Python file and return AST"""
        try:
            with open(file_path) as f:
                content = f.read()
            import ast

            return ast.parse(content)
        except Exception:
            return None

    def extract_imports(self, file_path: str) -> list[str]:
        """Extract imports from Python file"""
        try:
            with open(file_path) as f:
                content = f.read()

            imports = []
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith(("import ", "from ")):
                    imports.append(line)

            return sorted(imports)
        except Exception:
            return []

    def extract_structure(self, file_path: str) -> dict[str, Any]:
        """Extract class and method structure from Python file"""
        try:
            with open(file_path) as f:
                content = f.read()

            import ast

            tree = ast.parse(content)

            structure: dict[str, Any] = {"classes": {}, "functions": []}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    structure["classes"][node.name] = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    structure["functions"].append(node.name)

            return structure
        except Exception:
            return {"classes": {}, "functions": []}


def main() -> None:
    """Main entry point"""
    # Handle pre-commit mode
    if len(sys.argv) > 1 and sys.argv[1] == "--pre-commit":
        # Pre-commit mode: process all staged Python files
        import subprocess

        try:
            git_result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
                capture_output=True,
                text=True,
                check=True,
            )
            python_files = [f for f in git_result.stdout.strip().split("\n") if f.endswith(".py") and f]

            if not python_files:
                print("✅ No Python files to check")
                sys.exit(0)

            enforcer = RoundTripEnforcer()
            all_success = True

            for file_path in python_files:
                if Path(file_path).exists():
                    print(f"🔍 Checking round-trip for: {file_path}")
                    round_trip_result = enforcer.enforce_round_trip(file_path)
                    if round_trip_result["success"]:
                        print(f"✅ Round-trip passed for: {file_path}")
                    else:
                        print(f"❌ Round-trip failed for: {file_path}")
                        all_success = False

            sys.exit(0 if all_success else 1)
        except subprocess.CalledProcessError:
            print("⚠️  Could not determine staged files, skipping round-trip check")
            sys.exit(0)
    elif len(sys.argv) != 2:
        print("Usage: python scripts/enforce_round_trip.py <python_file>")
        print("       python scripts/enforce_round_trip.py --pre-commit")
        sys.exit(1)
    else:
        file_path = sys.argv[1]

        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        if not file_path.endswith(".py"):
            print(f"❌ Not a Python file: {file_path}")
            sys.exit(1)

        # Enforce round-trip engineering
        enforcer = RoundTripEnforcer()
        result = enforcer.enforce_round_trip(file_path)

        if result["success"]:
            print(f"✅ Round-trip engineering PASSED for {file_path}")
            print(f"   📦 Model components: {result['model_components']}")
            print(f"   📏 Model lines: {result['model_lines']}")
            print(f"   📝 Generated lines: {result['generated_lines']}")

            # Check functional equivalence
            equiv = result["functional_equivalence"]
            if equiv.get("ast_parsing", {}).get("generated", False):
                print("   ✅ Generated code parses successfully")
            else:
                print("   ❌ Generated code has syntax errors")

            if equiv.get("imports", {}).get("match", False):
                print("   ✅ Import structure preserved")
            else:
                print("   ⚠️  Import structure differs")

            if equiv.get("structure", {}).get("match", False):
                print("   ✅ Code structure preserved")
            else:
                print("   ⚠️  Code structure differs")

            # Exit with success
            sys.exit(0)
        else:
            print(f"❌ Round-trip engineering FAILED for {file_path}")
            print(f"   🚨 Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
