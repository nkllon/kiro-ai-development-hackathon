#!/usr/bin/env python3
"""
Type Assertion Enforcer
Enforces proper type assertion patterns for Any -> Specific Type conversions
"""

import ast
import re
from pathlib import Path
from typing import Any


class TypeAssertionEnforcer:
    """Enforces proper type assertion patterns"""

    def __init__(self) -> None:
        self.patterns = {
            "json.load": {
                "any_type": "Any",
                "assert_type": "dict",
                "return_type": "Dict[str, Any]",
                "assert_message": "Must be JSON object",
            },
            "ast.parse": {
                "any_type": "Any",
                "assert_type": "ast.Module",
                "return_type": "ast.Module",
                "assert_message": "Must be valid Python module",
            },
            "requests.get().json": {
                "any_type": "Any",
                "assert_type": "dict",
                "return_type": "Dict[str, Any]",
                "assert_message": "API must return JSON object",
            },
        }

    def check_file(self, file_path: Path) -> dict[str, Any]:
        """Check a file for proper type assertions"""
        violations = []

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violations.extend(self._check_function(node, content))

        except Exception as e:
            violations.append(f"Parse error: {e}")

        return {
            "file": str(file_path),
            "violations": violations,
            "clean": len(violations) == 0,
        }

    def _check_function(self, func: ast.FunctionDef, content: str) -> list[str]:
        """Check a function for type assertion violations"""
        violations = []

        # Check return type annotation
        if func.returns is None:
            violations.append(f"Function '{func.name}' missing return type annotation")
            return violations

        # Look for json.load() patterns
        for pattern_name, pattern_info in self.patterns.items():
            if self._has_pattern(func, pattern_name):
                if not self._has_proper_assertion(func, pattern_info):
                    violations.append(
                        f"Function '{
                            func.name}' uses {pattern_name} but missing proper type assertion"
                    )

        return violations

    def _has_pattern(self, func: ast.FunctionDef, pattern: str) -> bool:
        """Check if function contains the pattern"""
        func_code = ast.unparse(func)
        return pattern in func_code

    def _has_proper_assertion(
        self,
        func: ast.FunctionDef,
        pattern_info: dict[str, str],
    ) -> bool:
        """Check if function has proper type assertion"""
        func_code = ast.unparse(func)

        # Look for assert isinstance pattern
        assert_pattern = f"assert isinstance(.*, {pattern_info['assert_type']})"
        return bool(re.search(assert_pattern, func_code))

    def enforce_patterns(self, directory: Path = Path()) -> dict[str, Any]:
        """Enforce type assertion patterns across directory"""
        results: dict[str, Any] = {
            "files_checked": 0,
            "files_with_violations": 0,
            "total_violations": 0,
            "violations": [],
        }

        for py_file in directory.rglob("*.py"):
            if "test" not in str(py_file):
                result = self.check_file(py_file)
                results["files_checked"] += 1

                if not result["clean"]:
                    results["files_with_violations"] += 1
                    results["total_violations"] += len(result["violations"])
                    results["violations"].append(result)

        return results


def main() -> None:
    """Main function to enforce type assertion patterns"""
    print("🔍 Type Assertion Pattern Enforcer")
    print("=" * 40)

    enforcer = TypeAssertionEnforcer()
    results = enforcer.enforce_patterns()

    print("📊 Results:")
    print(f"   Files checked: {results['files_checked']}")
    print(f"   Files with violations: {results['files_with_violations']}")
    print(f"   Total violations: {results['total_violations']}")

    if results["violations"]:
        print("\n❌ Violations found:")
        for violation in results["violations"]:
            print(f"   {violation['file']}:")
            for v in violation["violations"]:
                print(f"     - {v}")
    else:
        print("\n✅ All files follow type assertion patterns!")


if __name__ == "__main__":
    main()
