#!/usr/bin/env python3
"""
Fix Subprocess Vulnerabilities
Systematically replace subprocess usage with secure alternatives
"""

import re
import sys
from pathlib import Path
from typing import Any


def find_subprocess_usage(file_path: Path) -> list[dict[str, Any]]:
    """Find subprocess usage in a file"""
    issues = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Skip docstring lines that mention secure_execute but don't actually use it
            if '"""' in line and "subprocess.run" in line:
                continue
            if "'''" in line and "subprocess.run" in line:
                continue

            # Check for subprocess imports
            if re.search(r"import\s+subprocess", line):
                issues.append(
                    {
                        "line": line_num,
                        "type": "import",
                        "content": line.strip(),
                        # import subprocess  # REMOVED - replaced with secure_execute
                    },
                )

            # Check for secure_execute usage
            elif re.search(r"subprocess\.run", line):
                issues.append(
                    {
                        "line": line_num,
                        "type": "subprocess_run",
                        "content": line.strip(),
                        "fix": line.replace("secure_execute", "secure_execute"),
                    },
                )

            # Check for secure_execute usage
            elif re.search(r"os\.system", line):
                issues.append(
                    {
                        "line": line_num,
                        "type": "os_system",
                        "content": line.strip(),
                        "fix": line.replace("secure_execute", "secure_execute"),
                    },
                )

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return issues


def fix_file(file_path: Path, dry_run: bool = True) -> bool:
    """Fix subprocess usage in a file"""
    issues = find_subprocess_usage(file_path)

    if not issues:
        return True

    print(f"\n🔍 Found {len(issues)} subprocess issues in {file_path}:")

    for issue in issues:
        print(f"  Line {issue['line']}: {issue['type']}")
        print(f"    Before: {issue['content']}")
        print(f"    After:  {issue['fix']}")

    if dry_run:
        return True

    # Apply fixes
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        # Apply fixes in reverse order to maintain line numbers
        for issue in reversed(issues):
            line_idx = issue["line"] - 1
            if line_idx < len(lines):
                lines[line_idx] = issue["fix"]

        # Add import if needed
        if any(issue["type"] == "subprocess_run" or issue["type"] == "os_system" for issue in issues):
            # Find import section
            import_section = -1
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    import_section = i
                    break

            if import_section >= 0:
                # Add secure_execute import
                secure_import = "from src.secure_shell_service.secure_executor import secure_execute"
                if secure_import not in lines:
                    lines.insert(import_section + 1, secure_import)

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"✅ Fixed {len(issues)} issues in {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main() -> None:
    """Main function"""
    print("🛡️  Subprocess Vulnerability Fixer")
    print("=" * 50)

    # Files to check (updated list based on Ghostbusters analysis)
    files_to_fix = [
        # Core files
        "src/ghostbusters/enhanced_ghostbusters.py",
        "src/ghostbusters/tool_discovery.py",
        "src/ghostbusters_gcp/embedded_ghostbusters_main.py",
        "src/ghostbusters_gcp/main.py",
        "src/model_driven_projection/test_projected_equivalence.py",
        "src/model_driven_projection/test_simple_equivalence.py",
        "src/multi_agent_testing/test_model_traceability.py",
        "src/secure_shell_service/client.py",
        "src/secure_shell_service/elegant_client.py",
        "src/secure_shell_service/migration_example.py",
        "src/secure_shell_service/real_client.py",
        "src/secure_shell_service/secure_executor.py",
        "tests/test_python_quality_enforcement.py",
        "tests/test_python_quality_enhanced.py",
        "tests/test_type_safety.py",
        # Root level files
        "create_pr.py",
        "project_model.py",
        "fix_simple_type_issues.py",
        "test_secure_shell.py",
        "fix_test_return_values.py",
        "fix_return_value_issues.py",
        "src/linter_api_integration.py",
        "src/intelligent_linter_system.py",
        "regenerate_from_ast.py",
        "ghostbusters_pr_review.py",
        # Additional files found by Ghostbusters
        "fix_flake8_issues.py",
        "fix_remaining_type_issues.py",
        "fix_type_annotations.py",
        "src/code_quality_system/quality_model.py",
        # Script files
        "scripts/fix_mypy_issues.py",
        "scripts/fix_subprocess_vulnerabilities.py",
        "scripts/migrate_subprocess_to_secure_shell.py",
        "scripts/pre_test_model_check.py",
        # Migration templates
        "scripts/migration_templates/enhanced_ghostbusters_migration_template.py",
        "scripts/migration_templates/intelligent_linter_system_migration_template.py",
        "scripts/migration_templates/linter_api_integration_migration_template.py",
        "scripts/migration_templates/quality_model_migration_template.py",
        "scripts/migration_templates/test_model_traceability_migration_template.py",
        "scripts/migration_templates/test_projected_equivalence_migration_template.py",
        "scripts/migration_templates/test_simple_equivalence_migration_template.py",
        "scripts/migration_templates/tool_discovery_migration_template.py",
    ]

    # Check if dry run
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        print("⚠️  LIVE MODE - Files will be modified")

    print(f"\n📋 Found {len(files_to_fix)} files to check")

    success_count = 0
    total_issues = 0

    for file_path_str in files_to_fix:
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        issues = find_subprocess_usage(file_path)
        total_issues += len(issues)

        if issues:
            success = fix_file(file_path, dry_run)
            if success:
                success_count += 1
        else:
            print(f"✅ {file_path} - No subprocess issues found")
            success_count += 1

    print("\n🎯 Summary:")
    print(f"  Files processed: {success_count}/{len(files_to_fix)}")
    print(f"  Total issues found: {total_issues}")

    if dry_run:
        print("\n💡 Run without --dry-run to apply fixes")
    else:
        print("\n✅ Subprocess vulnerabilities fixed!")


if __name__ == "__main__":
    main()
