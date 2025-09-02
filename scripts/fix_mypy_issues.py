#!/usr/bin/env python3
"""
Comprehensive Mypy Issue Fixer
"""

import re

# import subprocess  # REMOVED - replaced with secure_execute
from pathlib import Path
from typing import Any


def add_missing_type_annotations(file_path: Path) -> bool:
    """Add missing type annotations to a file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()

        lines: Any = content.split("\n")
        modified: bool = False

        # Add missing return type annotations
        for i, line in enumerate(lines):
            # Find function definitions without return types
            if re.match(r"^\s*def\s+\w+\s*\([^)]*\)\s*:\s*$", line):
                # Add -> None for functions without explicit return
                lines[i] = line.replace("):", ") -> None:")
                modified: bool = True

        # Add missing parameter type annotations
        for i, line in enumerate(lines):
            # Find function definitions with parameters
            match: Any = re.match(r"^\s*def\s+\w+\s*\(([^)]*)\)\s*", line)
            if match:
                params: Any = match.group(1)
                if params and not any(":" in param for param in params.split(",")):
                    # Add type annotations to parameters
                    new_params: list[Any] = []
                    for param in params.split(","):
                        param: Any = param.strip()
                        if param and ":" not in param:
                            # Infer type based on parameter name
                            param_name: Any = param.split("=")[0].strip()
                            param_type: Any = infer_parameter_type(param_name)
                            new_params.append(f"{param_name}: {param_type}")
                        else:
                            new_params.append(param)

                    new_param_str: Any = ", ".join(new_params)
                    lines[i] = line.replace(f"({params})", f"({new_param_str})")
                    modified: bool = True

        # Add missing variable type annotations
        for i, line in enumerate(lines):
            # Find variable assignments
            match: Any = re.match(r"^\s*(\w+)\s*=\s*(.+)$", line)
            if match:
                var_name: Any = match.group(1)
                var_value: Any = match.group(2)

                # Skip if already has type annotation
                if ":" in line:
                    continue

                # Infer type from value
                var_type: Any = infer_variable_type(var_value)
                if var_type:
                    lines[i] = f"{var_name}: {var_type} = {var_value}"
                    modified: bool = True

        # Add missing imports
        if modified:
            # Check if typing imports are needed
            typing_imports: list[Any] = []
            for line in lines:
                if any(
                    type_name in line
                    for type_name in [
                        "List[",
                        "Dict[",
                        "Tuple[",
                        "Optional[",
                        "Union[",
                        "Any",
                    ]
                ):
                    typing_imports: list[Any] = [
                        "from typing import List, Dict, Tuple, Optional, Union, Any",
                    ]
                    break

            if typing_imports:
                # Find where to insert imports
                for i, line in enumerate(lines):
                    if (
                        line.strip().startswith("import ")
                        or line.strip().startswith(
                            "from ",
                        )
                        or line.strip() == ""
                    ):
                        continue
                    # Insert imports here
                    for imp in reversed(typing_imports):
                        lines.insert(i, imp)
                    break

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def infer_parameter_type(param_name: str) -> str:
    """Infer parameter type based on name"""
    param_lower: Any = param_name.lower()

    if any(word in param_lower for word in ["file", "path", "name", "text", "content", "url", "string"]):
        return "str"
    if any(word in param_lower for word in ["count", "index", "size", "length", "number", "id"]):
        return "int"
    if any(word in param_lower for word in ["data", "items", "list", "array", "collection"]):
        return "List[Any]"
    if any(word in param_lower for word in ["config", "settings", "dict", "map", "params"]):
        return "Dict[str, Any]"
    if any(word in param_lower for word in ["flag", "enabled", "active", "is_", "has_"]):
        return "bool"
    if any(word in param_lower for word in ["func", "callback", "handler"]):
        return "Callable"

    return "Any"


def infer_variable_type(value: str) -> str:
    """Infer variable type from assignment value"""
    value: Any = value.strip()

    # String literals
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return "str"

    # Numeric literals
    if value.isdigit():
        return "int"
    if value.replace(".", "").replace("-", "").isdigit():
        return "float"

    # Boolean literals
    if value.lower() in ["true", "false"]:
        return "bool"

    # List literals
    if value.startswith("[") and value.endswith("]"):
        return "List[Any]"

    # Dict literals
    if value.startswith("{") and value.endswith("}"):
        return "Dict[str, Any]"

    # Tuple literals
    if value.startswith("(") and value.endswith(")"):
        return "Tuple[Any, ...]"

    # Function calls
    if "(" in value and ")" in value:
        return "Any"

    return "Any"


def fix_mypy_issues(directories: list[str] = None) -> dict[str, Any]:
    """Fix mypy issues in all files"""
    if directories is None:
        directories: list[Any] = ["src", "tests", "scripts", ".cursor"]

    results: Any = {"total_files": 0, "files_fixed": 0, "errors": []}

    for directory in directories:
        if Path(directory).exists():
            for py_file in Path(directory).rglob("*.py"):
                results["total_files"] += 1

                try:
                    if add_missing_type_annotations(py_file):
                        results["files_fixed"] += 1
                        print(f"Fixed: {py_file}")
                except Exception as e:
                    results["errors"].append(f"Error fixing {py_file}: {e}")

    return results


def main() -> None:
    """Main function"""
    print("🔧 Fixing mypy issues...")

    results: Any = fix_mypy_issues()

    print("\n📊 Results:")
    print(f"Files processed: {results['total_files']}")
    print(f"Files fixed: {results['files_fixed']}")

    if results["errors"]:
        print(f"Errors: {len(results['errors'])}")
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"  {error}")


if __name__ == "__main__":
    main()
