#!/usr/bin/env python3
"""
🚀 BEAST MODE INCREMENTAL IMPROVEMENT SYSTEM
==========================================
Implements incremental compliance improvement with feedback loops.
"""

import os
import sys
import json
import ast
from datetime import datetime
from pathlib import Path


class BeastModeIncrementalImprovementSystem:
    """Incremental improvement system with feedback loops"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.target_compliance = 95.0
        self.improvement_cycles = 0
        self.max_cycles = 10
        self.improvement_threshold = 0.5  # Stop when improvement < 0.5%

    def run_incremental_improvement(self):
        """Run incremental improvement process with feedback loops"""
        print("🚀 BEAST MODE INCREMENTAL IMPROVEMENT SYSTEM")
        print("=" * 60)
        print("🔄 Iterative improvement with feedback loops and learning")
        print(f"🎯 Target Compliance: {self.target_compliance}%")
        print()

        # Get initial compliance
        initial_compliance = self.get_compliance()
        print(f"📊 Initial Compliance: {initial_compliance:.1f}%")

        if initial_compliance >= self.target_compliance:
            print("🎉 TARGET ALREADY ACHIEVED!")
            return True

        improvement_achieved = False
        cycle_results = []

        while self.improvement_cycles < self.max_cycles and not improvement_achieved:
            self.improvement_cycles += 1

            print(f"🔄 IMPROVEMENT CYCLE {self.improvement_cycles}")
            print("=" * 30)

            # Cycle 1: Analyze current state
            current_compliance = self.get_compliance()
            error_analysis = self.analyze_errors_for_cycle()

            print(f"📊 Current Compliance: {current_compliance:.1f}%")
            print(f"🔍 Errors to Address: {len(error_analysis['prioritized_errors'])}")

            # Cycle 2: Apply targeted improvements
            improvements_applied = self.apply_targeted_improvements(error_analysis)

            # Cycle 3: Measure and validate
            new_compliance = self.get_compliance()
            improvement = new_compliance - current_compliance

            print(f"📈 New Compliance: {new_compliance:.1f}%")
            print(f"📈 Improvement: +{improvement:.1f}%")
            print(f"✅ Improvements Applied: {improvements_applied}")

            # Cycle 4: Learn and adapt
            learning_insights = self.learn_from_cycle(improvements_applied, improvement)

            cycle_result = {
                "cycle": self.improvement_cycles,
                "initial_compliance": current_compliance,
                "final_compliance": new_compliance,
                "improvement": improvement,
                "improvements_applied": improvements_applied,
                "learning_insights": learning_insights,
            }

            cycle_results.append(cycle_result)

            # Check convergence
            if new_compliance >= self.target_compliance:
                improvement_achieved = True
                print("🎉 TARGET COMPLIANCE ACHIEVED!")
                break

            # Check if improvement is too small
            if improvement < self.improvement_threshold:
                print("⚠️  Improvement below threshold - stopping cycles")
                break

            print()

        # Generate final results
        self.generate_improvement_report(cycle_results, initial_compliance)

        return improvement_achieved

    def analyze_errors_for_cycle(self):
        """Analyze errors for current improvement cycle"""
        errors = []

        for py_file in self.project_root.rglob("src/**/*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                errors.append(
                    {
                        "file": str(py_file),
                        "line": e.lineno,
                        "message": e.msg,
                        "type": "syntax_error",
                        "priority": self.calculate_error_priority(e.msg, str(py_file)),
                    }
                )

        # Prioritize errors by impact and fixability
        prioritized_errors = sorted(errors, key=lambda x: x["priority"], reverse=True)

        return {
            "total_errors": len(errors),
            "prioritized_errors": prioritized_errors[:50],  # Focus on top 50
            "high_priority_errors": [
                e for e in prioritized_errors if e["priority"] >= 8
            ][:20],
            "medium_priority_errors": [
                e for e in prioritized_errors if 5 <= e["priority"] < 8
            ][:20],
            "low_priority_errors": [e for e in prioritized_errors if e["priority"] < 5][
                :10
            ],
        }

    def calculate_error_priority(self, error_msg, file_path):
        """Calculate priority score for error"""
        priority = 0

        # File importance
        if "core" in file_path:
            priority += 3
        if "interface" in file_path:
            priority += 3
        if "registry" in file_path:
            priority += 3
        if "main" in file_path or "__init__.py" in file_path:
            priority += 2

        # Error type
        error_msg_lower = error_msg.lower()
        if "expected an indented block" in error_msg_lower:
            priority += 3  # Easy to fix
        elif "invalid syntax" in error_msg_lower:
            priority += 1  # Hard to fix
        elif "unindent" in error_msg_lower:
            priority += 2  # Medium difficulty
        elif "unexpected indent" in error_msg_lower:
            priority += 2  # Medium difficulty

        return min(priority, 10)

    def apply_targeted_improvements(self, error_analysis):
        """Apply targeted improvements based on error analysis"""
        improvements_applied = 0

        # Focus on high-priority errors first
        for error in error_analysis["high_priority_errors"]:
            if self.apply_focused_fix(error):
                improvements_applied += 1
                print(f"      ✅ High-priority fix: {os.path.basename(error['file'])}")

        # Then medium-priority errors
        for error in error_analysis["medium_priority_errors"]:
            if self.apply_focused_fix(error):
                improvements_applied += 1
                print(
                    f"      ✅ Medium-priority fix: {os.path.basename(error['file'])}"
                )

        return improvements_applied

    def apply_focused_fix(self, error):
        """Apply focused fix to a single error"""
        try:
            file_path = error["file"]
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            error_msg = error["message"].lower()

            # Apply specific fixes based on error type
            if "expected an indented block" in error_msg:
                fixed_content = self.fix_indented_block(content, error)
            elif "invalid syntax" in error_msg:
                fixed_content = self.fix_invalid_syntax(content, error)
            elif "unindent" in error_msg:
                fixed_content = self.fix_unindent(content, error)
            elif "unexpected indent" in error_msg:
                fixed_content = self.fix_unexpected_indent(content, error)
            else:
                return False

            # Validate fix
            if self.validate_fix(content, fixed_content):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                return True

        except Exception as e:
            pass

        return False

    def fix_indented_block(self, content, error):
        """Fix expected indented block error"""
        lines = content.split("\n")
        error_line = error["line"] - 1 if error["line"] else 0

        if error_line < len(lines):
            line = lines[error_line]
            if line.strip().endswith(":"):
                indent = len(line) - len(line.lstrip()) + 4
                lines.insert(error_line + 1, " " * indent + "pass")

        return "\n".join(lines)

    def fix_invalid_syntax(self, content, error):
        """Fix invalid syntax error"""
        # Apply common syntax fixes
        fixes = [
            (r"::+", ":"),
            (r"(\w)([=+\-*/])(\w)", r"\1 \2 \3"),
            (r",(\w)", r", \1"),
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)

        return content

    def fix_unindent(self, content, error):
        """Fix unindent mismatch error"""
        lines = content.split("\n")
        error_line = error["line"] - 1 if error["line"] else 0

        if error_line < len(lines):
            # Find proper indentation
            proper_indent = 0
            for i in range(error_line - 1, -1, -1):
                if lines[i].strip() and not lines[i].startswith("#"):
                    proper_indent = len(lines[i]) - len(lines[i].lstrip())
                    break

            if lines[error_line].strip():
                lines[error_line] = " " * proper_indent + lines[error_line].lstrip()

        return "\n".join(lines)

    def fix_unexpected_indent(self, content, error):
        """Fix unexpected indent error"""
        lines = content.split("\n")
        error_line = error["line"] - 1 if error["line"] else 0

        if error_line < len(lines):
            # Find proper indentation
            proper_indent = 0
            for i in range(error_line - 1, -1, -1):
                if lines[i].strip() and not lines[i].startswith("#"):
                    proper_indent = len(lines[i]) - len(lines[i].lstrip())
                    break

            lines[error_line] = " " * proper_indent + lines[error_line].lstrip()

        return "\n".join(lines)

    def validate_fix(self, original_content, fixed_content):
        """Validate that fix is correct"""
        try:
            # Check if fixed content parses correctly
            ast.parse(fixed_content)

            # Check that fix doesn't make excessive changes
            if len(fixed_content) > len(original_content) * 1.5:
                return False

            return True

        except SyntaxError:
            return False

    def learn_from_cycle(self, improvements_applied, improvement):
        """Learn from improvement cycle results"""
        insights = {
            "cycle_number": self.improvement_cycles,
            "improvements_applied": improvements_applied,
            "improvement_achieved": improvement,
            "effectiveness_rating": (
                "high"
                if improvement > 2.0
                else "medium" if improvement > 0.5 else "low"
            ),
            "lessons_learned": [],
        }

        # Learn from results
        if improvement > 2.0:
            insights["lessons_learned"].append("High-impact fixes were effective")
        elif improvement > 0.5:
            insights["lessons_learned"].append("Moderate improvement achieved")
        else:
            insights["lessons_learned"].append(
                "Low improvement - need different strategy"
            )

        if improvements_applied > 10:
            insights["lessons_learned"].append("High fix application rate")
        elif improvements_applied > 5:
            insights["lessons_learned"].append("Moderate fix application rate")
        else:
            insights["lessons_learned"].append(
                "Low fix application rate - need refinement"
            )

        return insights

    def generate_improvement_report(self, cycle_results, initial_compliance):
        """Generate comprehensive improvement report"""
        print("\n📊 INCREMENTAL IMPROVEMENT REPORT")
        print("=" * 40)

        if cycle_results:
            final_compliance = cycle_results[-1]["final_compliance"]
            total_improvement = final_compliance - initial_compliance

            print(f"📈 Initial Compliance: {initial_compliance:.1f}%")
            print(f"📈 Final Compliance: {final_compliance:.1f}%")
            print(f"📈 Total Improvement: +{total_improvement:.1f}%")
            print(f"🔄 Cycles Completed: {len(cycle_results)}")

            total_improvements = sum(
                cycle["improvements_applied"] for cycle in cycle_results
            )
            print(f"✅ Total Improvements Applied: {total_improvements}")

            # Analyze cycle effectiveness
            effective_cycles = len([c for c in cycle_results if c["improvement"] > 0.5])
            print(f"🎯 Effective Cycles: {effective_cycles}/{len(cycle_results)}")

            if total_improvement >= 5.0:
                print("🏆 EXCELLENT IMPROVEMENT ACHIEVED!")
            elif total_improvement >= 2.0:
                print("✅ GOOD IMPROVEMENT ACHIEVED!")
            elif total_improvement >= 0.5:
                print("🟡 MODERATE IMPROVEMENT ACHIEVED!")
            else:
                print("🔴 MINIMAL IMPROVEMENT - NEEDS REFINEMENT")

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "initial_compliance": initial_compliance,
            "final_compliance": (
                cycle_results[-1]["final_compliance"]
                if cycle_results
                else initial_compliance
            ),
            "total_improvement": total_improvement if cycle_results else 0,
            "cycles_completed": len(cycle_results),
            "cycle_results": cycle_results,
            "target_achieved": (
                final_compliance >= self.target_compliance if cycle_results else False
            ),
        }

        os.makedirs(".beast_mode", exist_ok=True)
        with open(".beast_mode/incremental_improvement_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(
            f"💾 Detailed report saved to .beast_mode/incremental_improvement_report.json"
        )

    def get_compliance(self):
        """Get current compliance percentage"""
        total_files = 0
        valid_files = 0

        for py_file in self.project_root.rglob("src/**/*.py"):
            total_files += 1
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
                valid_files += 1
            except SyntaxError:
                pass

        return (valid_files / total_files * 100) if total_files > 0 else 0


if __name__ == "__main__":
    import re

    system = BeastModeIncrementalImprovementSystem()
    success = system.run_incremental_improvement()

    if success:
        print("\n🎉 INCREMENTAL IMPROVEMENT SUCCESSFUL!")
        sys.exit(0)
    else:
        print("\n🔄 INCREMENTAL IMPROVEMENT IN PROGRESS")
        sys.exit(1)
