from typing import Any

from code_quality_system.quality_model import CodeQualityModel

#!/usr/bin/env python3
"""
Code Quality Fixer - Comprehensive Linting and Fixing Tool
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main() -> None:
    """Main function for the code quality fixer"""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive Code Quality Fixer")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze files without fixing",
    )
    parser.add_argument("--fix", action="store_true", help="Fix all issues")
    parser.add_argument(
        "--directories",
        nargs="+",
        default=["src", "tests", "scripts", ".cursor"],
        help="Directories to process",
    )
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    model = CodeQualityModel()

    if args.analyze:
        print("🔍 Analyzing code quality...")
        results = analyze_all_files(model, args.directories, args.verbose)
    elif args.fix:
        print("🔧 Fixing code quality issues...")
        results = fix_all_files(model, args.directories, args.verbose)
    else:
        print("🔍 Analyzing and fixing code quality...")
        results = analyze_and_fix_all_files(model, args.directories, args.verbose)

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"📄 Results saved to {args.output}")
    else:
        print_summary(results)


def analyze_all_files(
    model: CodeQualityModel,
    directories: list[str],
    verbose: bool,
) -> dict[str, Any]:
    """Analyze all files for linting issues"""
    results = {
        "total_files": 0,
        "total_issues": 0,
        "issues_by_type": {},
        "files_with_issues": [],
    }

    for directory in directories:
        if Path(directory).exists():
            for py_file in Path(directory).rglob("*.py"):
                results["total_files"] += 1

                if verbose:
                    print(f"Analyzing {py_file}...")

                analysis = model.analyze_file(py_file)
                results["total_issues"] += analysis["total_issues"]

                if analysis["total_issues"] > 0:
                    results["files_with_issues"].append(analysis)

                    # Count issues by type
                    for issue in analysis["issues"]:
                        issue_code = issue.get("code", "UNKNOWN")
                        results["issues_by_type"][issue_code] = (
                            results["issues_by_type"].get(issue_code, 0) + 1
                        )

    return results


def fix_all_files(
    model: CodeQualityModel,
    directories: list[str],
    verbose: bool,
) -> dict[str, Any]:
    """Fix all files"""
    return model.fix_all_files(directories)


def analyze_and_fix_all_files(
    model: CodeQualityModel,
    directories: list[str],
    verbose: bool,
) -> dict[str, Any]:
    """Analyze, fix, and re-analyze all files"""
    print("🔍 Initial analysis...")
    before_results = analyze_all_files(model, directories, verbose)

    print("🔧 Applying fixes...")
    fix_results = model.fix_all_files(directories)

    print("🔍 Post-fix analysis...")
    after_results = analyze_all_files(model, directories, verbose)

    return {
        "before": before_results,
        "fixes": fix_results,
        "after": after_results,
        "improvement": {
            "issues_reduced": before_results["total_issues"]
            - after_results["total_issues"],
            "reduction_percentage": (
                (before_results["total_issues"] - after_results["total_issues"])
                / max(before_results["total_issues"], 1)
            )
            * 100,
        },
    }


def print_summary(results: dict[str, Any]) -> None:
    """Print a summary of the results"""
    if "improvement" in results:
        # Combined analysis and fix
        before = results["before"]
        after = results["after"]
        improvement = results["improvement"]

        print("\n" + "=" * 60)
        print("📊 CODE QUALITY ANALYSIS & FIX SUMMARY")
        print("=" * 60)

        print(f"\n📁 Files processed: {before['total_files']}")
        print(f"🔍 Issues before: {before['total_issues']}")
        print(f"🔧 Issues after: {after['total_issues']}")
        print(f"📈 Issues reduced: {improvement['issues_reduced']}")
        print(f"📊 Reduction: {improvement['reduction_percentage']:.1f}%")

        if before["issues_by_type"]:
            print("\n📋 Issues by type (before):")
            for issue_type, count in sorted(before["issues_by_type"].items()):
                print(f"  {issue_type}: {count}")

        if after["issues_by_type"]:
            print("\n📋 Issues by type (after):")
            for issue_type, count in sorted(after["issues_by_type"].items()):
                print(f"  {issue_type}: {count}")

        if improvement["issues_reduced"] > 0:
            print(f"\n✅ SUCCESS: Reduced {improvement['issues_reduced']} issues!")
        else:
            print("\n⚠️  No issues were reduced.")

    else:
        # Single analysis or fix
        if "total_issues" in results:
            # Analysis only
            print("\n📊 ANALYSIS SUMMARY")
            print(f"Files processed: {results['total_files']}")
            print(f"Total issues: {results['total_issues']}")

            if results["issues_by_type"]:
                print("\nIssues by type:")
                for issue_type, count in sorted(results["issues_by_type"].items()):
                    print(f"  {issue_type}: {count}")
        else:
            # Fix only
            print("\n🔧 FIX SUMMARY")
            print(f"Files processed: {results['total_files']}")
            print(f"Files fixed: {results['files_fixed']}")
            print(f"Issues before: {results['total_issues_before']}")
            print(f"Issues after: {results['total_issues_after']}")


if __name__ == "__main__":
    main()
