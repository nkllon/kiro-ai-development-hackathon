#!/usr/bin/env python3
"""
Migration script to replace subprocess calls with secure shell service
"""

import ast
from pathlib import Path
from typing import Any


class SubprocessMigrator:
    """Migrate subprocess calls to secure shell service"""

    def __init__(self):
        self.src_dir = Path("src")
        self.migration_results = []

    def find_subprocess_files(self) -> list[Path]:
        """Find all Python files with subprocess usage"""
        subprocess_files = []

        for py_file in self.src_dir.rglob("*.py"):
            try:
                # Check if file contains subprocess usage
                py_file.read_text()  # Read to check if file is accessible
                subprocess_files.append(py_file)
            except Exception as e:
                print(f"⚠️ Could not read {py_file}: {e}")

        return subprocess_files

    def analyze_subprocess_usage(self, file_path: Path) -> dict[str, Any]:
        """Analyze subprocess usage in a file"""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            subprocess_calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                        subprocess_calls.append(
                            {
                                "line": node.lineno,
                                "method": node.func.attr,
                                "args": self._extract_args(node),
                            },
                        )

            return {
                "file": str(file_path),
                "subprocess_calls": subprocess_calls,
                "total_calls": len(subprocess_calls),
            }

        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "subprocess_calls": [],
                "total_calls": 0,
            }

    def _extract_args(self, node: ast.Call) -> list[str]:
        """Extract arguments from subprocess call"""
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Constant):
                args.append(str(arg.value))
            elif isinstance(arg, ast.Str):
                args.append(arg.s)
            else:
                args.append(f"<{type(arg).__name__}>")
        return args

    def generate_migration_plan(self, analysis_results: list[dict[str, Any]]) -> str:
        """Generate migration plan"""
        plan = []
        plan.append("# Subprocess Migration Plan")
        plan.append("=" * 50)
        plan.append("")

        total_files = len(analysis_results)
        total_calls = sum(r.get("total_calls", 0) for r in analysis_results)

        plan.append("## Summary")
        plan.append(f"- Files to migrate: {total_files}")
        plan.append(f"- Subprocess calls to replace: {total_calls}")
        plan.append("")

        plan.append("## Migration Strategy")
        plan.append("1. Replace `secure_execute()` with `secure_execute()`")
        plan.append("2. Replace `subprocess.Popen()` with async secure shell calls")
        plan.append("3. Replace `secure_execute()` with secure shell service")
        plan.append("4. Add proper error handling and timeouts")
        plan.append("")

        plan.append("## Files to Migrate")
        for result in analysis_results:
            if result.get("total_calls", 0) > 0:
                plan.append(f"### {result['file']}")
                plan.append(f"- Calls: {result['total_calls']}")
                for call in result.get("subprocess_calls", []):
                    plan.append(
                        f"  - Line {call['line']}: {call['method']}({', '.join(call['args'])})",
                    )
                plan.append("")

        return "\n".join(plan)

    def create_migration_template(self, file_path: Path) -> str:
        """Create migration template for a file"""
        return f"""# Migration template for {file_path}

# Replace subprocess imports
# OLD:
# import subprocess  # REMOVED - replaced with secure_execute
# NEW:
from src.secure_shell_service.client import secure_execute
import asyncio

# Replace subprocess calls
# OLD:
# result = secure_execute(['ls', '-la'], capture_output=True, text=True)
# NEW:
# result = await secure_execute('ls -la', timeout=10)

# OLD:
# process = subprocess.Popen(['long_running_command'], stdout=subprocess.PIPE)
# NEW:
# result = await secure_execute('long_running_command', timeout=30)

# Add async wrapper if needed
async def main():
    result = await secure_execute('your_command_here', timeout=10)
    print(f"Success: {{result['success']}}")
    print(f"Output: {{result['output']}}")

if __name__ == "__main__":
    asyncio.run(main())
"""

    def run_migration_analysis(self) -> None:
        """Run full migration analysis"""
        print("🔍 Analyzing subprocess usage...")

        subprocess_files = self.find_subprocess_files()
        print(f"Found {len(subprocess_files)} files with subprocess usage")

        analysis_results = []
        for file_path in subprocess_files:
            result = self.analyze_subprocess_usage(file_path)
            analysis_results.append(result)
            if result.get("total_calls", 0) > 0:
                print(f"  📁 {file_path}: {result['total_calls']} calls")

        # Generate migration plan
        plan = self.generate_migration_plan(analysis_results)

        # Save migration plan
        plan_file = Path("docs/SUBPROCESS_MIGRATION_PLAN.md")
        plan_file.parent.mkdir(exist_ok=True)
        plan_file.write_text(plan)

        print(f"\n📋 Migration plan saved to: {plan_file}")
        print(f"📊 Total files to migrate: {len(subprocess_files)}")
        print(
            f"🔧 Total subprocess calls: {sum(r.get('total_calls', 0) for r in analysis_results)}",
        )

        # Create migration templates
        templates_dir = Path("scripts/migration_templates")
        templates_dir.mkdir(exist_ok=True)

        for result in analysis_results:
            if result.get("total_calls", 0) > 0:
                file_path = Path(result["file"])
                template = self.create_migration_template(file_path)
                template_file = templates_dir / f"{file_path.stem}_migration_template.py"
                template_file.write_text(template)
                print(f"  📝 Template created: {template_file}")

        self.migration_results = analysis_results


def main():
    """Main migration script"""
    print("🛡️ Subprocess to Secure Shell Migration Tool")
    print("=" * 50)

    migrator = SubprocessMigrator()
    migrator.run_migration_analysis()

    print("\n✅ Migration analysis complete!")
    print("📋 Check docs/SUBPROCESS_MIGRATION_PLAN.md for the full plan")
    print("📝 Check scripts/migration_templates/ for migration templates")


if __name__ == "__main__":
    main()
