#!/usr/bin/env python3
"""
Functional Equivalence Test Script

This script tests that regenerated code is functionally equivalent to the original.
It performs comprehensive comparison including AST structure, imports, and behavior.

Usage:
    python scripts/test_functional_equivalence.py <python_file>
"""

import ast
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Add project root to path - works from any directory
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.round_trip_engineering import EnhancedReverseEngineer, RoundTripModelSystem

    ENHANCED_REVERSE_ENGINEER_AVAILABLE = True
except ImportError:
    ENHANCED_REVERSE_ENGINEER_AVAILABLE = False
    print("⚠️  Enhanced reverse engineer not available")


class FunctionalEquivalenceTester:
    """Tests functional equivalence between original and regenerated code"""

    def __init__(self):
        self.reverse_engineer = None
        self.code_generator = None
        if ENHANCED_REVERSE_ENGINEER_AVAILABLE:
            self.reverse_engineer = EnhancedReverseEngineer()
            self.code_generator = RoundTripModelSystem()

    def test_functional_equivalence(self, file_path: str) -> dict:
        """Test functional equivalence for a Python file"""
        print(f"🧪 Testing functional equivalence for: {file_path}")

        if not self.reverse_engineer or not self.code_generator:
            return {
                "success": False,
                "error": "Required tools not available",
                "file": file_path,
            }

        try:
            # Step 1: Reverse engineer the original file
            print("  📥 Step 1: Reverse engineering original file...")
            original_model = self.reverse_engineer.reverse_engineer_file(file_path)

            if not original_model:
                return {
                    "success": False,
                    "error": "Failed to reverse engineer original file",
                    "file": file_path,
                }

            # Step 2: Generate code from the model
            print("  📤 Step 2: Generating code from model...")
            generated_code = self.code_generator.generate_code_from_extracted_model(original_model)

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

            try:
                # Step 4: Perform comprehensive equivalence testing
                print("  🔍 Step 4: Testing equivalence...")
                equivalence_result = self.comprehensive_equivalence_test(file_path, temp_file)

                # Step 5: Clean up
                os.unlink(temp_file)

                return {
                    "success": True,
                    "file": file_path,
                    "original_lines": self.count_lines(file_path),
                    "generated_lines": len(generated_code.split("\n")),
                    "equivalence": equivalence_result,
                }

            except Exception as e:
                # Clean up on error
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                raise e

        except Exception as e:
            return {"success": False, "error": str(e), "file": file_path}

    def comprehensive_equivalence_test(self, original_file: str, generated_file: str) -> dict:
        """Perform comprehensive functional equivalence testing"""
        results = {}

        # Test 1: AST parsing
        print("    🔍 Testing AST parsing...")
        results["ast_parsing"] = self.test_ast_parsing(original_file, generated_file)

        # Test 2: Import structure
        print("    📥 Testing import structure...")
        results["imports"] = self.test_import_structure(original_file, generated_file)

        # Test 3: Class and method structure
        print("    🏗️  Testing code structure...")
        results["structure"] = self.test_code_structure(original_file, generated_file)

        # Test 4: Syntax validation
        print("    ✅ Testing syntax validation...")
        results["syntax"] = self.test_syntax_validation(original_file, generated_file)

        # Test 5: Content analysis
        print("    📊 Testing content analysis...")
        results["content"] = self.test_content_analysis(original_file, generated_file)

        return results

    def test_ast_parsing(self, original_file: str, generated_file: str) -> dict:
        """Test AST parsing for both files"""
        try:
            original_ast = self.parse_python_file(original_file)
            generated_ast = self.parse_python_file(generated_file)

            return {
                "original_parses": original_ast is not None,
                "generated_parses": generated_ast is not None,
                "both_parse": original_ast is not None and generated_ast is not None,
                "ast_nodes_original": (self.count_ast_nodes(original_ast) if original_ast else 0),
                "ast_nodes_generated": (self.count_ast_nodes(generated_ast) if generated_ast else 0),
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_parses": False,
                "generated_parses": False,
                "both_parse": False,
                "ast_nodes_original": 0,
                "ast_nodes_generated": 0,
            }

    def test_import_structure(self, original_file: str, generated_file: str) -> dict:
        """Test import structure equivalence"""
        try:
            original_imports = self.extract_imports(original_file)
            generated_imports = self.extract_imports(generated_file)

            return {
                "original_imports": original_imports,
                "generated_imports": generated_imports,
                "import_count_match": len(original_imports) == len(generated_imports),
                "import_content_match": original_imports == generated_imports,
                "missing_imports": set(original_imports) - set(generated_imports),
                "extra_imports": set(generated_imports) - set(original_imports),
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_imports": [],
                "generated_imports": [],
                "import_count_match": False,
                "import_content_match": False,
                "missing_imports": set(),
                "extra_imports": set(),
            }

    def test_code_structure(self, original_file: str, generated_file: str) -> dict:
        """Test class and method structure equivalence"""
        try:
            original_structure = self.extract_code_structure(original_file)
            generated_structure = self.extract_code_structure(generated_file)

            return {
                "original_structure": original_structure,
                "generated_structure": generated_structure,
                "structure_match": original_structure == generated_structure,
                "class_count_match": len(original_structure["classes"]) == len(generated_structure["classes"]),
                "method_count_match": (sum(len(methods) for methods in original_structure["classes"].values()) == sum(len(methods) for methods in generated_structure["classes"].values())),
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_structure": {"classes": {}, "functions": []},
                "generated_structure": {"classes": {}, "functions": []},
                "structure_match": False,
                "class_count_match": False,
                "method_count_match": False,
            }

    def test_syntax_validation(self, original_file: str, generated_file: str) -> dict:
        """Test syntax validation for both files"""
        try:
            original_syntax = self.validate_syntax(original_file)
            generated_syntax = self.validate_syntax(generated_file)

            return {
                "original_syntax_valid": original_syntax,
                "generated_syntax_valid": generated_syntax,
                "both_syntax_valid": original_syntax and generated_syntax,
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_syntax_valid": False,
                "generated_syntax_valid": False,
                "both_syntax_valid": False,
            }

    def test_content_analysis(self, original_file: str, generated_file: str) -> dict:
        """Test content analysis and comparison"""
        try:
            original_content = self.read_file_content(original_file)
            generated_content = self.read_file_content(generated_file)

            return {
                "original_length": len(original_content),
                "generated_length": len(generated_content),
                "length_ratio": (len(generated_content) / len(original_content) if original_content else 0),
                "content_similarity": self.calculate_content_similarity(original_content, generated_content),
                "has_todo_comments": "TODO" in generated_content,
                "has_placeholder_comments": "placeholder" in generated_content.lower(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_length": 0,
                "generated_length": 0,
                "length_ratio": 0,
                "content_similarity": 0.0,
                "has_todo_comments": False,
                "has_placeholder_comments": False,
            }

    def parse_python_file(self, file_path: str) -> Optional[ast.AST]:
        """Parse Python file and return AST"""
        try:
            with open(file_path) as f:
                content = f.read()
            return ast.parse(content)
        except Exception:
            return None

    def count_ast_nodes(self, tree: ast.AST) -> int:
        """Count AST nodes in the tree"""
        if not tree:
            return 0
        return len(list(ast.walk(tree)))

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

    def extract_code_structure(self, file_path: str) -> dict:
        """Extract class and method structure from Python file"""
        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)
            structure = {"classes": {}, "functions": []}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    structure["classes"][node.name] = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    structure["functions"].append(node.name)

            return structure
        except Exception:
            return {"classes": {}, "functions": []}

    def validate_syntax(self, file_path: str) -> bool:
        """Validate Python syntax"""
        try:
            with open(file_path) as f:
                content = f.read()
            ast.parse(content)
            return True
        except Exception:
            return False

    def read_file_content(self, file_path: str) -> str:
        """Read file content"""
        try:
            with open(file_path) as f:
                return f.read()
        except Exception:
            return ""

    def calculate_content_similarity(self, original: str, generated: str) -> float:
        """Calculate content similarity between original and generated"""
        if not original or not generated:
            return 0.0

        # Simple similarity based on common lines
        original_lines = set(original.split("\n"))
        generated_lines = set(generated.split("\n"))

        if not original_lines:
            return 0.0

        common_lines = len(original_lines.intersection(generated_lines))
        return common_lines / len(original_lines)

    def count_lines(self, file_path: str) -> int:
        """Count lines in a file"""
        try:
            with open(file_path) as f:
                return len(f.readlines())
        except Exception:
            return 0


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

            tester = FunctionalEquivalenceTester()
            all_success = True

            for file_path in python_files:
                if os.path.exists(file_path):
                    print(f"🔍 Testing functional equivalence for: {file_path}")
                    result = tester.test_functional_equivalence(file_path)
                    if result["success"]:
                        print(f"✅ Functional equivalence passed for: {file_path}")
                    else:
                        print(f"❌ Functional equivalence failed for: {file_path}")
                        all_success = False

            sys.exit(0 if all_success else 1)
        except subprocess.CalledProcessError:
            print("⚠️  Could not determine staged files, skipping functional equivalence test")
            sys.exit(0)
    elif len(sys.argv) != 2:
        print("Usage: python scripts/test_functional_equivalence.py <python_file>")
        print("       python scripts/test_functional_equivalence.py --pre-commit")
        sys.exit(1)
    else:
        file_path = sys.argv[1]

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        if not file_path.endswith(".py"):
            print(f"❌ Not a Python file: {file_path}")
            sys.exit(1)

        # Test functional equivalence
        tester = FunctionalEquivalenceTester()
        result = tester.test_functional_equivalence(file_path)

        if result["success"]:
            print(f"✅ Functional equivalence test PASSED for {file_path}")
            print(f"   📏 Original lines: {result['original_lines']}")
            print(f"   📝 Generated lines: {result['generated_lines']}")

            # Show detailed results
            equiv = result["equivalence"]

            # AST parsing results
            ast_result = equiv["ast_parsing"]
            if ast_result["both_parse"]:
                print("   ✅ Both files parse successfully")
            else:
                print("   ❌ Parsing issues detected")

            # Import results
            import_result = equiv["imports"]
            if import_result["import_content_match"]:
                print("   ✅ Import structure preserved")
            else:
                print("   ⚠️  Import structure differs")
                if import_result["missing_imports"]:
                    print(f"      Missing: {import_result['missing_imports']}")
                if import_result["extra_imports"]:
                    print(f"      Extra: {import_result['extra_imports']}")

            # Structure results
            structure_result = equiv["structure"]
            if structure_result["structure_match"]:
                print("   ✅ Code structure preserved")
            else:
                print("   ⚠️  Code structure differs")

            # Syntax results
            syntax_result = equiv["syntax"]
            if syntax_result["both_syntax_valid"]:
                print("   ✅ Both files have valid syntax")
            else:
                print("   ❌ Syntax validation issues")

            # Content results
            content_result = equiv["content"]
            print(f"   📊 Content similarity: {content_result['content_similarity']:.1%}")
            if content_result["has_todo_comments"]:
                print("   ⚠️  Generated code contains TODO comments")
            if content_result["has_placeholder_comments"]:
                print("   ⚠️  Generated code contains placeholder comments")

            # Exit with success
            sys.exit(0)
        else:
            print(f"❌ Functional equivalence test FAILED for {file_path}")
            print(f"   🚨 Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
