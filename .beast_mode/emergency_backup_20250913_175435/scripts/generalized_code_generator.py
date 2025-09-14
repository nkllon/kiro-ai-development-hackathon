#!/usr/bin/env python3
"""
Generalized Code Generator
Model-driven workflow: JSON model → Python generator → auto-format → test → fix model → regenerate code

Core Principle: NEVER patch generated code - always fix the model and regenerate
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class GenerationResult:
    """Result of a code generation iteration"""

    iteration: int
    success: bool
    model_file: str
    output_file: str
    validation_results: dict[str, Any]
    test_results: dict[str, Any]
    errors: list[str]
    warnings: list[str]


class ModelLoader:
    """Load and validate JSON models"""

    @staticmethod
    def load_model(model_file: str) -> dict[str, Any]:
        """Load a JSON model file"""
        try:
            with open(model_file) as f:
                model = json.load(f)
            print(f"✅ Loaded model: {model_file}")
            return model
        except Exception as e:
            msg = f"Failed to load model {model_file}: {e}"
            raise ValueError(msg)

    @staticmethod
    def validate_model(model: dict[str, Any]) -> bool:
        """Validate model structure and completeness"""
        required_fields = ["system_name", "description", "purpose", "components"]

        for field in required_fields:
            if field not in model:
                print(f"❌ Missing required field: {field}")
                return False

        print("✅ Model validation passed")
        return True


class CodeGenerator:
    """Generate Python code from validated models"""

    def generate_code(self, model: dict[str, Any]) -> str:
        """Generate Python code from the model"""
        print("🔧 Generating Python code from model...")

        # Generate imports
        imports = self._generate_imports(model)

        # Generate classes
        classes = self._generate_classes(model)

        # Generate main function
        main_function = self._generate_main_function(model)

        # Combine all parts
        code = f'''#!/usr/bin/env python3
"""
{model.get("system_name", "Generated System")}
{model.get("description", "Generated from JSON model")}

Purpose: {model.get("purpose", "To be defined")}
Graph API Level: {model.get("graph_api_level", 1)}
Projection System: {model.get("projection_system", "default")}
"""

{imports}

{classes}

{main_function}

if __name__ == "__main__":
    main()
'''

        print("✅ Code generation completed")
        return code

    def _generate_imports(self, model: dict[str, Any]) -> str:
        """Generate minimal imports - let the model handle complexity"""
        # Simple, clean imports - no complex logic
        return ""

    def _generate_classes(self, model: dict[str, Any]) -> str:
        """Generate class definitions"""
        classes = []

        if "components" in model:
            for component_name, component_data in model["components"].items():
                if isinstance(component_data, dict):
                    class_code = self._generate_class(component_name, component_data)
                    classes.append(class_code)

        return "\n\n".join(classes)

    def _generate_class(self, class_name: str, class_data: dict[str, Any]) -> str:
        """Generate a single class"""
        # Convert snake_case to PascalCase
        class_name_pascal = "".join(word.capitalize() for word in class_name.split("_"))

        # Generate class definition
        class_def = f"class {class_name_pascal}:\n"

        # Add docstring
        if "responsibility" in class_data:
            class_def += f'    """{class_data["responsibility"]}"""\n\n'

        # Add methods
        if "methods" in class_data:
            for method in class_data["methods"]:
                method_code = self._generate_method(method)
                class_def += method_code + "\n"

        return class_def

    def _generate_method(self, method_def: str) -> str:
        """Generate clean, simple method definitions"""
        # Simple parsing - extract method name and signature
        if "(" in method_def and ")" in method_def:
            # Keep the full signature as-is for simplicity
            return f"""    def {method_def}:
        \"\"\"{method_def}\"\"\"
        # TODO: Implement {method_def}
        pass"""
        return f"""    def {method_def}(self):
        \"\"\"{method_def}\"\"\"
        # TODO: Implement {method_def}
        pass"""

    def _generate_main_function(self, model: dict[str, Any]) -> str:
        """Generate main function"""
        system_name = model.get("system_name", "Generated System")

        return f"""def main():
    \"\"\"Main entry point for {system_name}\"\"\"
    print("🚀 {system_name}")
    print("📝 Generated from JSON model")
    print("✅ Ready to use!")"""


class CodeWriter:
    """Write generated code to files"""

    @staticmethod
    def write_code(output_file: str, code: str) -> bool:
        """Write generated code to file"""
        try:
            # Create backup if file exists
            if Path(output_file).exists():
                CodeWriter.backup_existing_file(output_file)

            # Write new code
            with open(output_file, "w") as f:
                f.write(code)

            print(f"✅ Code written to: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to write code: {e}")
            return False

    @staticmethod
    def backup_existing_file(file_path: str) -> bool:
        """Create backup of existing file"""
        try:
            backup_path = f"{file_path}.backup"
            Path(file_path).rename(backup_path)
            print(f"📦 Created backup: {backup_path}")
            return True
        except Exception as e:
            print(f"⚠️  Failed to create backup: {e}")
            return False


class AutoFormatter:
    """Format generated code using deterministic tools"""

    @staticmethod
    def format_file(file_path: str) -> bool:
        """Format a Python file using all available formatters"""
        print(f"🎨 Formatting: {file_path}")

        success = True

        # Run Black
        if AutoFormatter.run_black(file_path):
            print("  ✅ Black formatting completed")
        else:
            print("  ❌ Black formatting failed")
            success = False

        # Run autopep8
        if AutoFormatter.run_autopep8(file_path):
            print("  ✅ autopep8 formatting completed")
        else:
            print("  ⚠️  autopep8 had issues")

        # Run ruff
        if AutoFormatter.run_ruff(file_path):
            print("  ✅ ruff auto-fixes completed")
        else:
            print("  ⚠️  ruff had issues")

        return success

    @staticmethod
    def run_black(file_path: str) -> bool:
        """Run Black formatter"""
        try:
            result = subprocess.run(
                ["uv", "run", "black", "--line-length=88", file_path],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def run_autopep8(file_path: str) -> bool:
        """Run autopep8 formatter"""
        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "autopep8",
                    "--in-place",
                    "--aggressive",
                    "--aggressive",
                    file_path,
                ],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def run_ruff(file_path: str) -> bool:
        """Run ruff auto-fixes"""
        try:
            result = subprocess.run(
                ["uv", "run", "ruff", "check", "--fix", file_path],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False


class CodeValidator:
    """Validate generated code for syntax and quality"""

    @staticmethod
    def validate_syntax(file_path: str) -> bool:
        """Validate Python syntax"""
        try:
            with open(file_path) as f:
                content = f.read()

            import ast

            ast.parse(content)
            print(f"✅ Syntax validation passed: {file_path}")
            return True

        except SyntaxError as e:
            print(f"❌ Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Validation error in {file_path}: {e}")
            return False

    @staticmethod
    def check_quality(file_path: str) -> dict[str, Any]:
        """Check overall code quality"""
        return {
            "syntax_valid": CodeValidator.validate_syntax(file_path),
            "file_exists": Path(file_path).exists(),
            "file_size": (Path(file_path).stat().st_size if Path(file_path).exists() else 0),
        }


class TestRunner:
    """Run tests on generated code"""

    @staticmethod
    def run_smoke_tests(file_path: str) -> bool:
        """Run basic smoke tests"""
        print(f"🧪 Running smoke tests: {file_path}")

        try:
            # Try to import the module
            result = subprocess.run(
                ["python", "-c", f"import ast; ast.parse(open('{file_path}').read())"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("  ✅ AST parsing test passed")
                return True
            print(f"  ❌ AST parsing test failed: {result.stderr}")
            return False

        except Exception as e:
            print(f"  ❌ Smoke test failed: {e}")
            return False


class WorkflowOrchestrator:
    """Orchestrate the complete model-driven workflow"""

    def __init__(self):
        self.model_loader = ModelLoader()
        self.code_generator = CodeGenerator()
        self.code_writer = CodeWriter()
        self.auto_formatter = AutoFormatter()
        self.code_validator = CodeValidator()
        self.test_runner = TestRunner()

    def run_full_workflow(self, model_file: str, output_file: str) -> GenerationResult:
        """Run the complete workflow once"""
        print("🚀 Starting full workflow...")

        try:
            # Step 1: Load and validate model
            model = self.model_loader.load_model(model_file)
            if not self.model_loader.validate_model(model):
                msg = "Model validation failed"
                raise ValueError(msg)

            # Step 2: Generate code
            code = self.code_generator.generate_code(model)

            # Step 3: Write code
            if not self.code_writer.write_code(output_file, code):
                msg = "Code writing failed"
                raise ValueError(msg)

            # Step 4: Auto-format
            if not self.auto_formatter.format_file(output_file):
                print("⚠️  Auto-formatting had issues")

            # Step 5: Validate code
            validation_results = self.code_validator.check_quality(output_file)

            # Step 6: Run tests
            test_results = self.test_runner.run_smoke_tests(output_file)

            # Determine success
            success = validation_results.get("syntax_valid", False) and validation_results.get("file_exists", False) and test_results

            return GenerationResult(
                iteration=1,
                success=success,
                model_file=model_file,
                output_file=output_file,
                validation_results=validation_results,
                test_results={"smoke_test": test_results},
                errors=[],
                warnings=[],
            )

        except Exception as e:
            return GenerationResult(
                iteration=1,
                success=False,
                model_file=model_file,
                output_file=output_file,
                validation_results={},
                test_results={},
                errors=[str(e)],
                warnings=[],
            )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generalized Code Generator - Model-driven workflow without patching")

    parser.add_argument("model_file", help="JSON model file")
    parser.add_argument("output_file", help="Output Python file")

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.model_file).exists():
        print(f"❌ Model file not found: {args.model_file}")
        sys.exit(1)

    # Create orchestrator and run workflow
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.run_full_workflow(args.model_file, args.output_file)

    if result.success:
        print("🎉 Workflow completed successfully!")
        sys.exit(0)
    else:
        print("❌ Workflow failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
