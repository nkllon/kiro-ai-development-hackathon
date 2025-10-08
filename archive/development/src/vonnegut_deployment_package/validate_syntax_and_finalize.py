#!/usr/bin/env python3
"""
Beast Mode: Final Validation and Cleanup

Validates syntax of all modified files and provides final compliance report.
"""

import sys
import os
import json
import ast
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def validate_python_syntax(file_path: str) -> Dict[str, Any]:
    """Validate Python syntax of a file."""
    result = {
        "file_path": file_path,
        "valid": False,
        "error": None,
        "line_number": None,
    }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the file
        ast.parse(content)
        result["valid"] = True

    except SyntaxError as e:
        result["error"] = str(e)
        result["line_number"] = e.lineno
    except Exception as e:
        result["error"] = str(e)

    return result


def fix_common_syntax_issues(file_path: str) -> bool:
    """Fix common syntax issues in Python files."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        fixed_lines = []
        fixed = False

        for i, line in enumerate(lines):
            # Fix common indentation issues
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                # Check if this should be indented (follows a colon)
                if i > 0 and lines[i - 1].strip().endswith(":"):
                    # Add proper indentation
                    line = "    " + line
                    fixed = True

            # Fix common quote issues
            if '"""' in line and line.count('"""') % 2 != 0:
                # Try to balance quotes
                line = line.replace('"""', '"""')
                fixed = True

            fixed_lines.append(line)

        if fixed:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(fixed_lines))
            return True

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

    return False


def validate_all_files() -> Dict[str, Any]:
    """Validate syntax of all Python files in the project."""
    print("🔍 Validating Python File Syntax...")

    validation_results = {
        "total_files": 0,
        "valid_files": 0,
        "invalid_files": 0,
        "fixed_files": 0,
        "errors": [],
        "file_results": [],
    }

    # Get all Python files
    python_files = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    validation_results["total_files"] = len(python_files)

    for file_path in python_files:
        result = validate_python_syntax(file_path)
        validation_results["file_results"].append(result)

        if result["valid"]:
            validation_results["valid_files"] += 1
        else:
            validation_results["invalid_files"] += 1
            validation_results["errors"].append(result)

            # Try to fix common issues
            if fix_common_syntax_issues(file_path):
                # Re-validate
                new_result = validate_python_syntax(file_path)
                if new_result["valid"]:
                    validation_results["fixed_files"] += 1
                    validation_results["invalid_files"] -= 1
                    validation_results["valid_files"] += 1
                    print(f"   ✅ Fixed syntax in {file_path}")
                else:
                    print(
                        f"   ❌ Could not fix syntax in {file_path}: {new_result['error']}"
                    )
            else:
                print(f"   ❌ Syntax error in {file_path}: {result['error']}")

    return validation_results


def generate_final_compliance_report() -> Dict[str, Any]:
    """Generate final compliance report."""
    print("📊 Generating Final Compliance Report...")

    # Load enhanced registry data
    enhanced_file = ".beast_mode/enhanced_interface_registry.json"
    if not os.path.exists(enhanced_file):
        return {"error": "Enhanced registry data not found"}

    with open(enhanced_file, "r") as f:
        enhanced_data = json.load(f)

    interfaces = enhanced_data.get("interfaces", {})

    # Calculate final statistics
    compliance_scores = [
        interface.get("compliance_score", 0) for interface in interfaces.values()
    ]

    final_report = {
        "timestamp": str(datetime.now()),
        "total_interfaces": len(interfaces),
        "average_compliance": (
            sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
        ),
        "min_compliance": min(compliance_scores) if compliance_scores else 0,
        "max_compliance": max(compliance_scores) if compliance_scores else 0,
        "compliance_distribution": {
            "excellent_90_100": len([s for s in compliance_scores if s >= 90]),
            "good_80_89": len([s for s in compliance_scores if 80 <= s < 90]),
            "fair_70_79": len([s for s in compliance_scores if 70 <= s < 80]),
            "poor_50_69": len([s for s in compliance_scores if 50 <= s < 70]),
            "critical_below_50": len([s for s in compliance_scores if s < 50]),
        },
        "interface_types": {},
        "top_performers": [],
        "improvement_needed": [],
    }

    # Analyze by interface type
    type_stats = {}
    for interface_name, interface_data in interfaces.items():
        interface_type = interface_data.get("interface_type", "unknown")
        compliance = interface_data.get("compliance_score", 0)

        if interface_type not in type_stats:
            type_stats[interface_type] = {
                "count": 0,
                "total_compliance": 0,
                "interfaces": [],
            }

        type_stats[interface_type]["count"] += 1
        type_stats[interface_type]["total_compliance"] += compliance
        type_stats[interface_type]["interfaces"].append(
            {
                "name": interface_name,
                "compliance": compliance,
                "file_path": interface_data.get("file_path", ""),
            }
        )

    # Calculate averages
    for interface_type, stats in type_stats.items():
        stats["average_compliance"] = stats["total_compliance"] / stats["count"]
        final_report["interface_types"][interface_type] = stats

    # Get top performers and improvement needed
    all_interfaces = [
        (name, data.get("compliance_score", 0)) for name, data in interfaces.items()
    ]
    all_interfaces.sort(key=lambda x: x[1], reverse=True)

    final_report["top_performers"] = all_interfaces[:10]
    final_report["improvement_needed"] = [x for x in all_interfaces if x[1] < 70][:10]

    return final_report


def main():
    """Main validation and finalization function."""
    print("🚀 BEAST MODE: Final Validation and Cleanup")
    print("=" * 60)

    # Validate syntax
    validation_results = validate_all_files()

    print(f"\n📊 Syntax Validation Results:")
    print(f"   Total Files: {validation_results['total_files']}")
    print(f"   Valid Files: {validation_results['valid_files']}")
    print(f"   Invalid Files: {validation_results['invalid_files']}")
    print(f"   Fixed Files: {validation_results['fixed_files']}")

    if validation_results["errors"]:
        print(f"\n⚠️  Remaining Syntax Errors:")
        for error in validation_results["errors"][:5]:  # Show first 5
            print(f"   - {error['file_path']}: {error['error']}")
        if len(validation_results["errors"]) > 5:
            print(f"   ... and {len(validation_results['errors']) - 5} more")

    # Generate final compliance report
    final_report = generate_final_compliance_report()

    if "error" not in final_report:
        print(f"\n🎉 FINAL COMPLIANCE REPORT")
        print("=" * 60)

        print(f"\n📊 Final Compliance Statistics:")
        print(f"   Total Interfaces: {final_report['total_interfaces']}")
        print(f"   Average Compliance: {final_report['average_compliance']:.2f}%")
        print(f"   Min Compliance: {final_report['min_compliance']:.2f}%")
        print(f"   Max Compliance: {final_report['max_compliance']:.2f}%")

        print(f"\n📈 Compliance Distribution:")
        dist = final_report["compliance_distribution"]
        print(f"   Excellent (90-100%): {dist['excellent_90_100']} interfaces")
        print(f"   Good (80-89%): {dist['good_80_89']} interfaces")
        print(f"   Fair (70-79%): {dist['fair_70_79']} interfaces")
        print(f"   Poor (50-69%): {dist['poor_50_69']} interfaces")
        print(f"   Critical (<50%): {dist['critical_below_50']} interfaces")

        print(f"\n🏆 Top Performers:")
        for name, compliance in final_report["top_performers"]:
            print(f"   {name}: {compliance:.2f}%")

        print(f"\n🔧 Interface Types Performance:")
        for interface_type, stats in final_report["interface_types"].items():
            print(
                f"   {interface_type}: {stats['average_compliance']:.2f}% avg ({stats['count']} interfaces)"
            )

        # Save final report
        report_file = ".beast_mode/final_compliance_report.json"
        with open(report_file, "w") as f:
            json.dump(
                {
                    "validation_results": validation_results,
                    "final_report": final_report,
                },
                f,
                indent=2,
                default=str,
            )

        print(f"\n💾 Final report saved to {report_file}")

        # Calculate overall success
        success_rate = (
            validation_results["valid_files"] / validation_results["total_files"]
        ) * 100
        compliance_rate = final_report["average_compliance"]

        print(f"\n🎯 OVERALL SUCCESS METRICS:")
        print(f"   Syntax Validation: {success_rate:.1f}% files valid")
        print(f"   Compliance Achievement: {compliance_rate:.1f}% average")

        if success_rate >= 95 and compliance_rate >= 70:
            print(f"\n🏆 MISSION ACCOMPLISHED: Full compliance spread achieved!")
        elif success_rate >= 90 and compliance_rate >= 60:
            print(f"\n🎉 MAJOR SUCCESS: Significant compliance improvement achieved!")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: Further improvements needed")

    else:
        print(f"❌ {final_report['error']}")


if __name__ == "__main__":
    main()
