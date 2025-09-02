#!/usr/bin/env python3
"""
Subproject Scrubber - Automatically fix linting issues across all subprojects

This tool iterates through all subprojects in the OpenFlow-Playground workspace
and applies consistent linting fixes to ensure all code meets quality standards.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class SubprojectScrubber:
    """Automatically scrub all subprojects for linting issues"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.subprojects = []
        self.results = {}

    def discover_subprojects(self) -> list[Path]:
        """Find all subprojects with their own .git directories"""
        subproject_paths = []

        for git_dir in self.workspace_root.rglob(".git"):
            if git_dir.is_dir() and git_dir.parent != self.workspace_root:
                subproject_path = git_dir.parent
                if subproject_path.name not in [".git", "node_modules", "__pycache__"]:
                    subproject_paths.append(subproject_path)

        # Sort by name for consistent processing
        subproject_paths.sort(key=lambda p: p.name)
        self.subprojects = subproject_paths
        return subproject_paths

    def _deploy_ruff_config(self, subproject_path: Path) -> None:
        """Deploy universal Ruff config to subproject"""
        template_path = self.workspace_root / "scripts" / "subproject_ruff_template.toml"
        target_path = subproject_path / ".ruff.toml"

        if template_path.exists():
            try:
                import shutil

                shutil.copy2(template_path, target_path)
                print(f"   📋 Deployed universal Ruff config")
            except Exception as e:
                print(f"   ⚠️  Failed to deploy Ruff config: {e}")
        else:
            print(f"   ⚠️  Ruff template not found at {template_path}")

    def scrub_subproject(self, subproject_path: Path) -> dict[str, Any]:
        """Scrub a single subproject for linting issues"""
        print(f"\n🔧 Scrubbing subproject: {subproject_path.name}")

        result = {
            "name": subproject_path.name,
            "path": str(subproject_path),
            "status": "unknown",
            "ruff_issues_before": 0,
            "ruff_issues_after": 0,
            "black_formatted": False,
            "git_status": "unknown",
            "errors": [],
        }

        try:
            # Check if it's a Python project
            pyproject_toml = subproject_path / "pyproject.toml"
            if not pyproject_toml.exists():
                result["status"] = "skipped"
                result["errors"].append("No pyproject.toml found - not a Python project")
                return result

            # Deploy universal Ruff config to subproject
            self._deploy_ruff_config(subproject_path)

            # Check initial ruff status
            ruff_result = self._run_ruff_check(subproject_path)
            if ruff_result["success"]:
                result["ruff_issues_before"] = ruff_result["issue_count"]
            else:
                result["errors"].append(f"Ruff check failed: {ruff_result['error']}")

            # Run black formatting
            black_result = self._run_black(subproject_path)
            if black_result["success"]:
                result["black_formatted"] = True
                print("   ✅ Black formatting completed")
            else:
                result["errors"].append(f"Black formatting failed: {black_result['error']}")

            # Run ruff with auto-fix
            ruff_fix_result = self._run_ruff_fix(subproject_path)
            if ruff_fix_result["success"]:
                print("   ✅ Ruff auto-fix completed")
            else:
                result["errors"].append(f"Ruff auto-fix failed: {ruff_fix_result['error']}")

            # Check final ruff status
            final_ruff_result = self._run_ruff_check(subproject_path)
            if final_ruff_result["success"]:
                result["ruff_issues_after"] = final_ruff_result["issue_count"]
                print(f"   📊 Issues: {result['ruff_issues_before']} → {result['ruff_issues_after']}")
            else:
                result["errors"].append(f"Final ruff check failed: {final_ruff_result['error']}")

            # Check git status
            git_result = self._check_git_status(subproject_path)
            result["git_status"] = git_result["status"]

            # Determine overall status
            if result["ruff_issues_after"] == 0:
                result["status"] = "clean"
            elif result["ruff_issues_after"] < result["ruff_issues_before"]:
                result["status"] = "improved"
            else:
                result["status"] = "unchanged"

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Unexpected error: {str(e)}")

        return result

    def _run_ruff_check(self, subproject_path: Path) -> dict[str, Any]:
        """Run ruff check on a subproject"""
        try:
            result = subprocess.run(
                ["python3", "-m", "ruff", "check", ".", "--output-format=concise"],
                capture_output=True,
                text=True,
                cwd=subproject_path,
                timeout=60,
            )

            if result.returncode == 0:
                return {"success": True, "issue_count": 0}
            # Parse issue count from output
            lines = result.stdout.strip().split("\n")
            issue_count = len([line for line in lines if ":" in line and not line.startswith("warning:")])
            return {"success": True, "issue_count": issue_count}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_black(self, subproject_path: Path) -> dict[str, Any]:
        """Run black formatting on a subproject"""
        try:
            result = subprocess.run(
                ["python3", "-m", "black", "."],
                capture_output=True,
                text=True,
                cwd=subproject_path,
                timeout=60,
            )

            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_ruff_fix(self, subproject_path: Path) -> dict[str, Any]:
        """Run ruff with auto-fix on a subproject"""
        try:
            result = subprocess.run(
                ["python3", "-m", "ruff", "check", ".", "--fix"],
                capture_output=True,
                text=True,
                cwd=subproject_path,
                timeout=60,
            )

            return {
                "success": True,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_git_status(self, subproject_path: Path) -> dict[str, Any]:
        """Check git status of a subproject"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=subproject_path,
                timeout=30,
            )

            if result.returncode == 0:
                changes = result.stdout.strip().split("\n")
                if not changes or changes == [""]:
                    return {"status": "clean", "changes": 0}
                return {"status": "dirty", "changes": len(changes)}
            return {"status": "error", "error": result.stderr}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def scrub_all(self) -> dict[str, Any]:
        """Scrub all discovered subprojects"""
        print(f"🚀 Starting subproject scrubbing for {self.workspace_root}")

        # Discover subprojects
        subprojects = self.discover_subprojects()
        print(f"📁 Found {len(subprojects)} subprojects")

        # Scrub each subproject
        for subproject_path in subprojects:
            result = self.scrub_subproject(subproject_path)
            self.results[subproject_path.name] = result

        return self.results

    def print_summary(self) -> None:
        """Print a summary of all scrubbing results"""
        print(f"\n{'=' * 60}")
        print(f"📊 SUBPROJECT SCRUBBING SUMMARY")
        print(f"{'=' * 60}")

        total_issues_before = sum(r["ruff_issues_before"] for r in self.results.values())
        total_issues_after = sum(r["ruff_issues_after"] for r in self.results.values())
        total_improvement = total_issues_before - total_issues_after

        print(
            f"📈 Overall Improvement: {total_issues_before} → {total_issues_after} issues ( \
    -{total_improvement})"
        )
        print(f"🎯 Subprojects Processed: {len(self.results)}")

        # Group by status
        status_counts = {}
        for result in self.results.values():
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        print(f"\n📋 Status Breakdown:")
        for status, count in status_counts.items():
            print(f"   {status.capitalize()}: {count}")

        print(f"\n🔍 Detailed Results:")
        for name, result in self.results.items():
            status_emoji = {
                "clean": "✅",
                "improved": "🔄",
                "unchanged": "⚠️",
                "skipped": "⏭️",
                "error": "❌",
            }.get(result["status"], "❓")

            print(f"   {status_emoji} {name}: {result['ruff_issues_before']} → {result['ruff_issues_after']} issues")

            if result["errors"]:
                for error in result["errors"]:
                    print(f"      ❌ {error}")

        # Save results to file
        output_file = self.workspace_root / "subproject_scrubbing_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n💾 Detailed results saved to: {output_file}")


def main():
    """Main function"""
    workspace_root = Path.cwd()

    # Check if we're in the right directory
    if not (workspace_root / ".git").exists():
        print("❌ Error: Not in a git repository root")
        print("   Please run this script from the OpenFlow-Playground root directory")
        sys.exit(1)

    # Create and run the scrubber
    scrubber = SubprojectScrubber(workspace_root)
    results = scrubber.scrub_all()
    scrubber.print_summary()

    # Exit with error code if any subprojects failed
    error_count = sum(1 for r in results.values() if r["status"] == "error")
    if error_count > 0:
        print(f"\n⚠️  {error_count} subprojects encountered errors")
        sys.exit(1)
    else:
        print(f"\n🎉 All subprojects processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
