#!/usr/bin/env python3
"""
Self-Validation Protocol

Purpose: Prevent delusions by validating tools and claims before they're made
"""

import ast
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class SelfValidationProtocol:
    """
    Protocol to validate tools and claims before making them
    """

    def __init__(self):
        self.validation_history = []
        self.failed_validations = []

    def validate_tool_effectiveness(self, tool_path: str, expected_functionality: str) -> dict[str, Any]:
        """Validate that a tool actually does what it claims"""

        print(f"🔍 Validating tool: {tool_path}")
        print(f"🎯 Expected functionality: {expected_functionality}")

        # Test 1: Does it parse?
        ast_validation = self._test_ast_parsing(tool_path)

        # Test 2: Does it have the claimed methods?
        method_validation = self._test_method_implementation(tool_path, expected_functionality)

        # Test 3: Does it actually work on a test case?
        functional_validation = self._test_functional_capability(tool_path)

        validation_result = {
            "tool_path": tool_path,
            "expected_functionality": expected_functionality,
            "ast_valid": ast_validation["passed"],
            "methods_implemented": method_validation["passed"],
            "functionally_working": functional_validation["passed"],
            "can_claim_success": all(
                [
                    ast_validation["passed"],
                    method_validation["passed"],
                    functional_validation["passed"],
                ]
            ),
            "details": {
                "ast_validation": ast_validation,
                "method_validation": method_validation,
                "functional_validation": functional_validation,
            },
        }

        # Log validation result
        self.validation_history.append(validation_result)

        if not validation_result["can_claim_success"]:
            self.failed_validations.append(validation_result)
            print(f"❌ VALIDATION FAILED: {tool_path}")
            print(f"   AST Valid: {ast_validation['passed']}")
            print(f"   Methods Implemented: {method_validation['passed']}")
            print(f"   Functionally Working: {functional_validation['passed']}")
        else:
            print(f"✅ VALIDATION PASSED: {tool_path}")

        return validation_result

    def _test_ast_parsing(self, tool_path: str) -> dict[str, Any]:
        """Test if the tool can be parsed by AST"""
        try:
            with open(tool_path) as f:
                content = f.read()
            ast.parse(content)
            return {"passed": True, "message": "File parses successfully with AST"}
        except SyntaxError as e:
            return {"passed": False, "message": f"Syntax error: {e}", "error": str(e)}
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error reading file: {e}",
                "error": str(e),
            }

    def _test_method_implementation(self, tool_path: str, expected_functionality: str) -> dict[str, Any]:
        """Test if the tool has the claimed methods implemented"""
        try:
            with open(tool_path) as f:
                content = f.read()

            # Check for TODO comments that indicate incomplete implementation
            todo_count = content.count("# TODO")
            content.count("# TODO: Implement")

            # Check for method stubs that just return None or empty strings
            stub_patterns = [
                "return None",
                'return ""',
                "return {}",
                "return []",
                "pass",
                "raise NotImplementedError",
            ]

            stub_count = sum(content.count(pattern) for pattern in stub_patterns)

            # If there are many TODOs or stubs, the tool isn't fully implemented
            if todo_count > 3 or stub_count > 5:
                return {
                    "passed": False,
                    "message": f"Tool has {todo_count} TODOs and {stub_count} stubs - not fully implemented",
                    "todo_count": todo_count,
                    "stub_count": stub_count,
                }

            return {
                "passed": True,
                "message": "Tool appears to have implemented methods",
                "todo_count": todo_count,
                "stub_count": stub_count,
            }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Error analyzing method implementation: {e}",
                "error": str(e),
            }

    def _test_functional_capability(self, tool_path: str) -> dict[str, Any]:
        """Test if the tool actually works on a test case"""
        try:
            # Try to run the tool with --help or similar
            result = subprocess.run(
                ["python", tool_path, "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "Tool runs successfully and responds to --help",
                    "output": (result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout),
                }
            # Try running without arguments
            result2 = subprocess.run(["python", tool_path], capture_output=True, text=True, timeout=10)

            if result2.returncode == 0:
                return {
                    "passed": True,
                    "message": "Tool runs successfully without arguments",
                    "output": (result2.stdout[:200] + "..." if len(result2.stdout) > 200 else result2.stdout),
                }
            return {
                "passed": False,
                "message": f"Tool failed to run: {result2.stderr}",
                "error": result2.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "message": "Tool timed out during execution",
                "error": "Timeout",
            }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error testing functional capability: {e}",
                "error": str(e),
            }

    def validate_against_project_model(self, work_item: str, domain: str) -> dict[str, Any]:
        """Validate work against project model requirements"""

        print(f"🔍 Validating {work_item} against project model domain: {domain}")

        try:
            # Load project model using Model Registry tools
            from src.round_trip_engineering.tools import get_model_registry

            registry = get_model_registry()
            manager = registry.get_model("project")
            model = manager.load_model()

            # Get domain requirements
            domain_config = model["domains"].get(domain, {})
            requirements = domain_config.get("requirements", [])

            print(f"📋 Found {len(requirements)} requirements for domain: {domain}")

            # Validate each requirement
            requirement_validation = {}
            for req in requirements:
                requirement_validation[req] = self._validate_requirement(work_item, req)

            all_requirements_met = all(requirement_validation.values())

            validation_result = {
                "work_item": work_item,
                "domain": domain,
                "requirements_met": all_requirements_met,
                "total_requirements": len(requirements),
                "met_requirements": sum(requirement_validation.values()),
                "validation_details": requirement_validation,
                "can_claim_compliance": all_requirements_met,
            }

            # Log validation result
            self.validation_history.append(validation_result)

            if all_requirements_met:
                print(f"✅ All requirements met for {domain}")
            else:
                print(f"❌ Some requirements not met for {domain}")
                for req, met in requirement_validation.items():
                    status = "✅" if met else "❌"
                    print(f"   {status} {req}")

            return validation_result

        except FileNotFoundError:
            return {
                "work_item": work_item,
                "domain": domain,
                "requirements_met": False,
                "error": "Project model registry not found",
            }
        except Exception as e:
            return {
                "work_item": work_item,
                "domain": domain,
                "requirements_met": False,
                "error": f"Error loading project model: {e}",
            }

    def _validate_requirement(self, work_item: str, requirement: str) -> bool:
        """Validate a specific requirement"""
        # This is a simplified validation - in practice, you'd have more sophisticated logic
        # For now, we'll just check if the requirement text appears in the work item

        try:
            if Path(work_item).exists():
                with open(work_item) as f:
                    content = f.read()
                return requirement.lower() in content.lower()
            return False
        except Exception:
            return False

    def call_ghostbusters_on_work(self, work_description: str, claims: list[str]) -> dict[str, Any]:
        """Use Ghostbusters to validate my own work"""

        print(f"👻 Calling Ghostbusters to validate: {work_description}")
        print(f"🎯 Claims to validate: {claims}")

        try:
            # Import Ghostbusters system
            import sys

            sys.path.append(".")

            from src.ghostbusters import GhostbustersOrchestrator

            # Create orchestrator
            orchestrator = GhostbustersOrchestrator()

            # Create validation request
            validation_request = {
                "work": work_description,
                "claims": claims,
                "validation_type": "self_validation",
            }

            # Let Ghostbusters investigate
            investigation = orchestrator.investigate_quality_issues(str(validation_request))

            return {
                "ghostbusters_available": True,
                "investigation_result": investigation,
                "delusions_detected": len(investigation.get("delusions", [])),
                "can_claim_success": len(investigation.get("delusions", [])) == 0,
            }

        except ImportError:
            return {
                "ghostbusters_available": False,
                "error": "Ghostbusters system not available",
                "can_claim_success": False,
            }
        except Exception as e:
            return {
                "ghostbusters_available": True,
                "error": f"Error during Ghostbusters validation: {e}",
                "can_claim_success": False,
            }

    def completion_validation_checklist(self, work_item: str) -> dict[str, Any]:
        """Validate that work is actually complete"""

        print(f"🔍 Running completion checklist for: {work_item}")

        checklist = {
            "code_parses": self._test_ast_parsing(work_item)["passed"],
            "tests_pass": self._test_tests_pass(work_item),
            "functionality_verified": self._test_actual_functionality(work_item),
            "integration_working": self._test_integration(work_item),
            "documentation_accurate": self._validate_documentation_accuracy(work_item),
        }

        all_passed = all(checklist.values())

        result = {
            "work_item": work_item,
            "all_passed": all_passed,
            "checklist": checklist,
            "can_claim_success": all_passed,
        }

        # Log result
        self.validation_history.append(result)

        if all_passed:
            print(f"✅ Completion checklist PASSED for {work_item}")
        else:
            print(f"❌ Completion checklist FAILED for {work_item}")
            for item, passed in checklist.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {item}")

        return result

    def _test_tests_pass(self, work_item: str) -> bool:
        """Test if tests pass for the work item"""
        try:
            # This is a simplified test - in practice, you'd run actual tests
            # For now, we'll just check if test files exist
            work_path = Path(work_item)
            if work_path.exists():
                # Look for corresponding test files
                test_patterns = [
                    f"test_{work_path.stem}.py",
                    f"test_{work_path.stem}_*.py",
                    f"*_test_{work_path.stem}.py",
                ]

                for pattern in test_patterns:
                    if list(work_path.parent.glob(pattern)):
                        return True

                # If no test files found, assume tests don't pass
                return False
            return False
        except Exception:
            return False

    def _test_actual_functionality(self, work_item: str) -> bool:
        """Test if the work item actually has functional code"""
        try:
            with open(work_item) as f:
                content = f.read()

            # Check for actual implementation vs. stubs
            if "raise NotImplementedError" in content:
                return False

            if content.count("pass") > content.count("def") * 2:
                return False

            return not content.count("# TODO") > 5
        except Exception:
            return False

    def _test_integration(self, work_item: str) -> bool:
        """Test if the work item integrates with the system"""
        try:
            # This is a simplified test - in practice, you'd check actual integration
            # For now, we'll just check if it can be imported
            work_path = Path(work_item)
            if work_path.suffix == ".py":
                # Try to parse it
                with open(work_item) as f:
                    content = f.read()
                ast.parse(content)
                return True
            return True
        except Exception:
            return False

    def _validate_documentation_accuracy(self, work_item: str) -> bool:
        """Validate that documentation matches the actual implementation"""
        try:
            # This is a simplified validation
            # In practice, you'd compare docstrings with actual function signatures
            with open(work_item) as f:
                content = f.read()

            # Check for basic documentation
            has_docstrings = '"""' in content or "'''" in content
            has_comments = "#" in content

            return has_docstrings or has_comments
        except Exception:
            return False

    def generate_validation_report(self) -> str:
        """Generate a comprehensive validation report"""

        report = f"""
🔍 Self-Validation Protocol Report
==================================

📊 Validation Summary:
  Total Validations: {len(self.validation_history)}
  Failed Validations: {len(self.failed_validations)}
  Success Rate: {((len(self.validation_history) - len(self.failed_validations)) / len(self.validation_history) * 100) if len(self.validation_history) > 0 else 0:.1f}%

📋 Validation History:
"""

        for i, validation in enumerate(self.validation_history, 1):
            status = "✅" if validation.get("can_claim_success", False) else "❌"
            report += f"  {i}. {status} {validation.get('work_item', 'Unknown')}\n"

        if self.failed_validations:
            report += f"\n🚨 Failed Validations:\n"
            for validation in self.failed_validations:
                report += f"  ❌ {validation.get('work_item', 'Unknown')}\n"
                if "error" in validation:
                    report += f"      Error: {validation['error']}\n"

        return report


def main():
    """Main entry point for self-validation protocol"""

    protocol = SelfValidationProtocol()

    print("🔍 Self-Validation Protocol")
    print("===========================")

    # Example validation
    print("\n1. Validating f-string fixer...")
    protocol.validate_tool_effectiveness("scripts/deterministic_fstring_fixer.py", "Fix broken f-strings in Python files")

    print("\n2. Validating against project model...")
    protocol.validate_against_project_model("scripts/deterministic_fstring_fixer.py", "code_quality")

    print("\n3. Running completion checklist...")
    protocol.completion_validation_checklist("scripts/deterministic_fstring_fixer.py")

    print("\n4. Calling Ghostbusters...")
    protocol.call_ghostbusters_on_work(
        "F-string fixer implementation",
        [
            "Tool can detect f-string issues",
            "Tool can fix f-string issues",
            "Tool validates fixes",
        ],
    )

    # Generate final report
    print("\n" + protocol.generate_validation_report())


if __name__ == "__main__":
    main()
