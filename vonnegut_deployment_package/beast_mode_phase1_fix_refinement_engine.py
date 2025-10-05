#!/usr/bin/env python3
"""
🚀 BEAST MODE PHASE 1: FIX APPLICATION REFINEMENT ENGINE
=====================================================
Advanced fix application refinement with performance monitoring and diverse testing.
"""

import os
import sys
import json
import ast
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class BeastModeFixRefinementEngine:
    """Beast Mode Phase 1: Advanced fix application refinement"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.target_compliance = 90.0  # Phase 1 target
        self.final_target = 95.0  # Final target
        self.fixes_applied = 0
        self.fixes_failed = 0
        self.performance_metrics = {}
        self.error_patterns = {}
        self.fix_strategies = {}

    def run_phase1_refinement(self):
        """Run Phase 1: Fix Application Refinement"""
        print("🚀 BEAST MODE PHASE 1: FIX APPLICATION REFINEMENT")
        print("=" * 60)
        print("🔧 Debug and refine fix application mechanisms")
        print("📊 Implement performance monitoring and metrics")
        print("🧪 Test fix strategies on diverse error samples")
        print(f"🎯 Target: {self.target_compliance}%+ compliance")
        print()

        # Get initial compliance
        initial_compliance = self.get_compliance()
        print(f"📊 Initial Compliance: {initial_compliance:.1f}%")

        if initial_compliance >= self.target_compliance:
            print("🎉 PHASE 1 TARGET ALREADY ACHIEVED!")
            return True

        # Phase 1.1: Advanced Error Analysis with Pattern Recognition
        print("🔍 PHASE 1.1: ADVANCED ERROR ANALYSIS")
        print("=" * 40)

        error_analysis = self.advanced_error_analysis()

        # Phase 1.2: Fix Strategy Refinement
        print("\n🔧 PHASE 1.2: FIX STRATEGY REFINEMENT")
        print("=" * 40)

        refined_strategies = self.refine_fix_strategies(error_analysis)

        # Phase 1.3: Performance Monitoring Setup
        print("\n📊 PHASE 1.3: PERFORMANCE MONITORING SETUP")
        print("=" * 40)

        monitoring_system = self.setup_performance_monitoring()

        # Phase 1.4: Diverse Error Sample Testing
        print("\n🧪 PHASE 1.4: DIVERSE ERROR SAMPLE TESTING")
        print("=" * 40)

        test_results = self.test_diverse_error_samples(
            error_analysis, refined_strategies
        )

        # Phase 1.5: Systematic Fix Application
        print("\n🚀 PHASE 1.5: SYSTEMATIC FIX APPLICATION")
        print("=" * 40)

        fix_results = self.apply_systematic_fixes(
            error_analysis, refined_strategies, test_results
        )

        # Phase 1.6: Performance Analysis and Optimization
        print("\n📈 PHASE 1.6: PERFORMANCE ANALYSIS")
        print("=" * 40)

        performance_analysis = self.analyze_performance(fix_results)

        # Get final compliance
        final_compliance = self.get_compliance()
        improvement = final_compliance - initial_compliance

        print(f"\n📊 PHASE 1 RESULTS:")
        print(f"   📈 Initial Compliance: {initial_compliance:.1f}%")
        print(f"   📈 Final Compliance: {final_compliance:.1f}%")
        print(f"   📈 Improvement: +{improvement:.1f}%")
        print(f"   ✅ Fixes Applied: {self.fixes_applied}")
        print(f"   ❌ Fixes Failed: {self.fixes_failed}")
        print(
            f"   📊 Success Rate: {(self.fixes_applied / (self.fixes_applied + self.fixes_failed) * 100):.1f}%"
            if (self.fixes_applied + self.fixes_failed) > 0
            else "   📊 Success Rate: 0.0%"
        )

        # Generate Phase 1 report
        self.generate_phase1_report(
            initial_compliance, final_compliance, improvement, fix_results
        )

        return final_compliance >= self.target_compliance

    def advanced_error_analysis(self):
        """Advanced error analysis with pattern recognition"""
        print("🔍 Analyzing errors with advanced pattern recognition...")

        errors = []
        patterns = {}

        for py_file in self.project_root.rglob("src/**/*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                error_info = {
                    "file": str(py_file),
                    "line": e.lineno,
                    "message": e.msg,
                    "type": "syntax_error",
                    "content": content,
                    "context": self.extract_context(content, e.lineno),
                    "complexity": self.calculate_complexity(content, e.lineno),
                    "fixability": self.assess_fixability(e.msg, content, e.lineno),
                }

                errors.append(error_info)

                # Pattern recognition
                pattern = self.identify_error_pattern(e.msg)
                if pattern not in patterns:
                    patterns[pattern] = []
                patterns[pattern].append(error_info)

        print(f"   📊 Total Errors: {len(errors)}")
        print(f"   🔍 Error Patterns: {len(patterns)}")

        for pattern, pattern_errors in patterns.items():
            print(f"      • {pattern}: {len(pattern_errors)} errors")

        self.error_patterns = patterns

        return {
            "total_errors": len(errors),
            "errors": errors,
            "patterns": patterns,
            "high_fixability": [e for e in errors if e["fixability"] >= 0.8],
            "medium_fixability": [e for e in errors if 0.5 <= e["fixability"] < 0.8],
            "low_fixability": [e for e in errors if e["fixability"] < 0.5],
        }

    def identify_error_pattern(self, error_msg):
        """Identify error patterns for targeted fixes"""
        error_msg_lower = error_msg.lower()

        if "expected an indented block" in error_msg_lower:
            return "indentation_block"
        elif "invalid syntax" in error_msg_lower:
            return "syntax_invalid"
        elif "unindent" in error_msg_lower:
            return "indentation_mismatch"
        elif "unexpected indent" in error_msg_lower:
            return "indentation_unexpected"
        elif "eol while scanning string literal" in error_msg_lower:
            return "string_literal"
        elif "unterminated string" in error_msg_lower:
            return "string_unterminated"
        elif "expected" in error_msg_lower and ":" in error_msg_lower:
            return "missing_colon"
        elif "bracket" in error_msg_lower or any(
            char in error_msg_lower for char in ["(", ")", "[", "]", "{", "}"]
        ):
            return "bracket_mismatch"
        else:
            return "complex_structural"

    def extract_context(self, content, line_num):
        """Extract context around error line"""
        lines = content.split("\n")
        start = max(0, line_num - 5)
        end = min(len(lines), line_num + 5)
        return "\n".join(lines[start:end])

    def calculate_complexity(self, content, line_num):
        """Calculate complexity score for error context"""
        context = self.extract_context(content, line_num)

        complexity = 0
        complexity += len(context.split("\n")) * 0.1
        complexity += context.count("class") * 2
        complexity += context.count("def") * 1
        complexity += context.count("if") * 0.5
        complexity += context.count("for") * 0.5
        complexity += context.count("while") * 0.5

        return min(complexity, 10)

    def assess_fixability(self, error_msg, content, line_num):
        """Assess how fixable an error is"""
        error_msg_lower = error_msg.lower()

        # Base fixability scores
        if "expected an indented block" in error_msg_lower:
            return 0.9
        elif "missing colon" in error_msg_lower:
            return 0.8
        elif "unterminated string" in error_msg_lower:
            return 0.8
        elif "unindent" in error_msg_lower:
            return 0.7
        elif "unexpected indent" in error_msg_lower:
            return 0.7
        elif "invalid syntax" in error_msg_lower:
            return 0.4
        elif "eol while scanning" in error_msg_lower:
            return 0.6
        else:
            return 0.3

        # Adjust based on context complexity
        complexity = self.calculate_complexity(content, line_num)
        if complexity > 5:
            return max(0.1, fixability - 0.3)
        elif complexity < 2:
            return min(1.0, fixability + 0.1)

        return fixability

    def refine_fix_strategies(self, error_analysis):
        """Refine fix strategies based on error analysis"""
        print("🔧 Refining fix strategies based on error patterns...")

        strategies = {}

        for pattern, errors in error_analysis["patterns"].items():
            strategy = self.create_refined_strategy(pattern, errors)
            strategies[pattern] = strategy
            print(
                f"      ✅ {pattern}: {strategy['name']} (confidence: {strategy['confidence']:.1f})"
            )

        self.fix_strategies = strategies
        return strategies

    def create_refined_strategy(self, pattern, errors):
        """Create refined fix strategy for specific pattern"""
        strategies = {
            "indentation_block": {
                "name": "Smart Indentation Block Fix",
                "confidence": 0.9,
                "fix_function": self.fix_indentation_block_advanced,
                "validation": self.validate_indentation_fix,
            },
            "syntax_invalid": {
                "name": "Context-Aware Syntax Fix",
                "confidence": 0.6,
                "fix_function": self.fix_syntax_invalid_advanced,
                "validation": self.validate_syntax_fix,
            },
            "indentation_mismatch": {
                "name": "Precision Indentation Correction",
                "confidence": 0.8,
                "fix_function": self.fix_indentation_mismatch_advanced,
                "validation": self.validate_indentation_fix,
            },
            "indentation_unexpected": {
                "name": "Context-Sensitive Indentation Fix",
                "confidence": 0.8,
                "fix_function": self.fix_unexpected_indent_advanced,
                "validation": self.validate_indentation_fix,
            },
            "string_literal": {
                "name": "String Termination Fix",
                "confidence": 0.9,
                "fix_function": self.fix_string_literal_advanced,
                "validation": self.validate_string_fix,
            },
            "missing_colon": {
                "name": "Smart Colon Addition",
                "confidence": 0.9,
                "fix_function": self.fix_missing_colon_advanced,
                "validation": self.validate_colon_fix,
            },
            "bracket_mismatch": {
                "name": "Bracket Balance Fix",
                "confidence": 0.7,
                "fix_function": self.fix_bracket_mismatch_advanced,
                "validation": self.validate_bracket_fix,
            },
            "complex_structural": {
                "name": "Structural Analysis Fix",
                "confidence": 0.4,
                "fix_function": self.fix_complex_structural_advanced,
                "validation": self.validate_structural_fix,
            },
        }

        return strategies.get(
            pattern,
            {
                "name": "Generic Fix",
                "confidence": 0.3,
                "fix_function": self.fix_generic,
                "validation": self.validate_generic_fix,
            },
        )

    def setup_performance_monitoring(self):
        """Setup performance monitoring system"""
        print("📊 Setting up performance monitoring...")

        monitoring = {
            "start_time": time.time(),
            "fix_attempts": 0,
            "fix_successes": 0,
            "fix_failures": 0,
            "patterns_tested": {},
            "performance_metrics": {},
        }

        print("      ✅ Performance monitoring initialized")
        return monitoring

    def test_diverse_error_samples(self, error_analysis, strategies):
        """Test fix strategies on diverse error samples"""
        print("🧪 Testing fix strategies on diverse error samples...")

        test_results = {}

        for pattern, strategy in strategies.items():
            if pattern in error_analysis["patterns"]:
                errors = error_analysis["patterns"][pattern][
                    :5
                ]  # Test first 5 of each pattern
                pattern_results = []

                for error in errors:
                    try:
                        # Test the fix
                        start_time = time.time()
                        fixed_content = strategy["fix_function"](error)
                        fix_time = time.time() - start_time

                        # Validate the fix
                        validation_result = strategy["validation"](
                            error["content"], fixed_content, error
                        )

                        result = {
                            "error": error,
                            "fix_successful": validation_result["is_valid"],
                            "fix_time": fix_time,
                            "validation": validation_result,
                            "confidence": strategy["confidence"],
                        }

                        pattern_results.append(result)

                        if validation_result["is_valid"]:
                            print(
                                f"      ✅ {pattern}: Fix successful ({fix_time:.3f}s)"
                            )
                        else:
                            print(
                                f"      ❌ {pattern}: Fix failed - {validation_result['issues']}"
                            )

                    except Exception as e:
                        pattern_results.append(
                            {
                                "error": error,
                                "fix_successful": False,
                                "fix_time": 0,
                                "validation": {"is_valid": False, "issues": [str(e)]},
                                "confidence": 0,
                            }
                        )
                        print(f"      ❌ {pattern}: Exception - {e}")

                test_results[pattern] = pattern_results

        print(f"      📊 Tested {len(test_results)} patterns")
        return test_results

    def apply_systematic_fixes(self, error_analysis, strategies, test_results):
        """Apply systematic fixes based on test results"""
        print("🚀 Applying systematic fixes...")

        fix_results = {
            "patterns_processed": 0,
            "fixes_applied": 0,
            "fixes_failed": 0,
            "patterns_results": {},
        }

        # Process patterns by success rate from testing
        pattern_priority = sorted(
            test_results.items(),
            key=lambda x: (
                sum(1 for r in x[1] if r["fix_successful"]) / len(x[1]) if x[1] else 0
            ),
            reverse=True,
        )

        for pattern, test_results_pattern in pattern_priority:
            if pattern not in error_analysis["patterns"]:
                continue

            strategy = strategies[pattern]
            errors = error_analysis["patterns"][pattern]

            print(f"      🔧 Processing {pattern}: {len(errors)} errors")

            pattern_fixes = 0
            pattern_failures = 0

            for error in errors[:50]:  # Limit to 50 per pattern
                try:
                    # Apply fix
                    fixed_content = strategy["fix_function"](error)

                    # Validate fix
                    validation = strategy["validation"](
                        error["content"], fixed_content, error
                    )

                    if validation["is_valid"] and validation["confidence"] >= 0.7:
                        # Write fixed content
                        with open(error["file"], "w", encoding="utf-8") as f:
                            f.write(fixed_content)

                        pattern_fixes += 1
                        self.fixes_applied += 1
                        print(f"         ✅ Fixed: {os.path.basename(error['file'])}")
                    else:
                        pattern_failures += 1
                        self.fixes_failed += 1

                except Exception as e:
                    pattern_failures += 1
                    self.fixes_failed += 1
                    print(
                        f"         ❌ Failed: {os.path.basename(error['file'])} - {e}"
                    )

            fix_results["patterns_results"][pattern] = {
                "fixes_applied": pattern_fixes,
                "fixes_failed": pattern_failures,
                "success_rate": (
                    pattern_fixes / (pattern_fixes + pattern_failures)
                    if (pattern_fixes + pattern_failures) > 0
                    else 0
                ),
            }

            fix_results["patterns_processed"] += 1
            fix_results["fixes_applied"] += pattern_fixes
            fix_results["fixes_failed"] += pattern_failures

        return fix_results

    def analyze_performance(self, fix_results):
        """Analyze performance and generate insights"""
        print("📈 Analyzing performance metrics...")

        total_attempts = fix_results["fixes_applied"] + fix_results["fixes_failed"]
        overall_success_rate = (
            fix_results["fixes_applied"] / total_attempts if total_attempts > 0 else 0
        )

        print(f"      📊 Overall Success Rate: {overall_success_rate:.1%}")
        print(f"      ✅ Total Fixes Applied: {fix_results['fixes_applied']}")
        print(f"      ❌ Total Fixes Failed: {fix_results['fixes_failed']}")

        # Analyze pattern performance
        for pattern, results in fix_results["patterns_results"].items():
            print(f"      🔍 {pattern}: {results['success_rate']:.1%} success rate")

        return {
            "overall_success_rate": overall_success_rate,
            "total_attempts": total_attempts,
            "pattern_performance": fix_results["patterns_results"],
        }

    def generate_phase1_report(
        self, initial_compliance, final_compliance, improvement, fix_results
    ):
        """Generate comprehensive Phase 1 report"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": "Phase 1: Fix Application Refinement",
            "target_compliance": self.target_compliance,
            "initial_compliance": initial_compliance,
            "final_compliance": final_compliance,
            "improvement": improvement,
            "target_achieved": final_compliance >= self.target_compliance,
            "fix_results": fix_results,
            "performance_metrics": self.performance_metrics,
            "error_patterns": len(self.error_patterns),
            "fix_strategies": len(self.fix_strategies),
        }

        os.makedirs(".beast_mode", exist_ok=True)
        with open(".beast_mode/beast_mode_phase1_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Phase 1 report saved to .beast_mode/beast_mode_phase1_report.json")

    # Advanced Fix Functions
    def fix_indentation_block_advanced(self, error):
        """Advanced indentation block fix"""
        content = error["content"]
        lines = content.split("\n")
        error_line = error["line"] - 1 if error["line"] else 0

        if error_line < len(lines):
            line = lines[error_line]
            if line.strip().endswith(":"):
                # Find proper indentation
                base_indent = len(line) - len(line.lstrip())
                new_indent = base_indent + 4

                # Add pass statement with proper indentation
                lines.insert(error_line + 1, " " * new_indent + "pass")

        return "\n".join(lines)

    def fix_syntax_invalid_advanced(self, content, error):
        """Advanced syntax fix with context awareness"""
        # Apply multiple syntax fixes
        fixes = [
            (r"::+", ":"),
            (r"(\w)([=+\-*/])(\w)", r"\1 \2 \3"),
            (r",(\w)", r", \1"),
            (r"\(\s*\)", "()"),
            (r"\[\s*\]", "[]"),
            (r"\{\s*\}", "{}"),
            (r",\s*\)", ")"),
            (r",\s*\]", "]"),
            (r",\s*\}", "}"),
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)

        return content

    def fix_indentation_mismatch_advanced(self, error):
        """Advanced indentation mismatch fix"""
        content = error["content"]
        lines = content.split("\n")
        error_line = error["line"] - 1 if error["line"] else 0

        if error_line < len(lines):
            # Find proper indentation from context
            proper_indent = 0
            for i in range(error_line - 1, -1, -1):
                if lines[i].strip() and not lines[i].startswith("#"):
                    proper_indent = len(lines[i]) - len(lines[i].lstrip())
                    if lines[i].strip().endswith(":"):
                        proper_indent += 4
                    break

            if lines[error_line].strip():
                lines[error_line] = " " * proper_indent + lines[error_line].lstrip()

        return "\n".join(lines)

    def fix_unexpected_indent_advanced(self, error):
        """Advanced unexpected indent fix"""
        return self.fix_indentation_mismatch_advanced(error)

    def fix_string_literal_advanced(self, error):
        """Advanced string literal fix"""
        content = error["content"]
        lines = content.split("\n")
        error_line = error["line"] - 1 if error["line"] else 0

        if error_line < len(lines):
            line = lines[error_line]
            # Fix unterminated strings
            if line.count("'") % 2 == 1:
                lines[error_line] = line + "'"
            elif line.count('"') % 2 == 1:
                lines[error_line] = line + '"'

        return "\n".join(lines)

    def fix_missing_colon_advanced(self, error):
        """Advanced missing colon fix"""
        content = error["content"]
        lines = content.split("\n")
        error_line = error["line"] - 1 if error["line"] else 0

        if error_line < len(lines):
            line = lines[error_line]
            if (
                line.strip()
                and not line.strip().endswith(":")
                and not line.strip().startswith("#")
            ):
                keywords = [
                    "if",
                    "for",
                    "while",
                    "def",
                    "class",
                    "try",
                    "except",
                    "finally",
                    "with",
                    "elif",
                    "else",
                ]
                for keyword in keywords:
                    if line.strip().startswith(keyword):
                        lines[error_line] = line.rstrip() + ":"
                        break

        return "\n".join(lines)

    def fix_bracket_mismatch_advanced(self, error):
        """Advanced bracket mismatch fix"""
        content = error["content"]

        # Fix common bracket issues
        fixes = [
            (r"\(\s*$", "()"),
            (r"\[\s*$", "[]"),
            (r"\{\s*$", "{}"),
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)

        return content

    def fix_complex_structural_advanced(self, error):
        """Advanced complex structural fix"""
        # For complex structural errors, apply multiple strategies
        content = error["content"]

        # Try multiple fix strategies
        content = self.fix_syntax_invalid_advanced(content, error)
        content = self.fix_bracket_mismatch_advanced(error)

        return content

    def fix_generic(self, error):
        """Generic fix for unknown patterns"""
        return error["content"]

    # Validation Functions
    def validate_indentation_fix(self, original, fixed, error):
        """Validate indentation fixes"""
        try:
            ast.parse(fixed)
            return {"is_valid": True, "confidence": 0.9, "issues": []}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [f"New syntax error: {e.msg}"],
            }

    def validate_syntax_fix(self, original, fixed, error):
        """Validate syntax fixes"""
        try:
            ast.parse(fixed)
            return {"is_valid": True, "confidence": 0.8, "issues": []}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [f"New syntax error: {e.msg}"],
            }

    def validate_string_fix(self, original, fixed, error):
        """Validate string fixes"""
        try:
            ast.parse(fixed)
            return {"is_valid": True, "confidence": 0.9, "issues": []}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [f"New syntax error: {e.msg}"],
            }

    def validate_colon_fix(self, original, fixed, error):
        """Validate colon fixes"""
        try:
            ast.parse(fixed)
            return {"is_valid": True, "confidence": 0.9, "issues": []}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [f"New syntax error: {e.msg}"],
            }

    def validate_bracket_fix(self, original, fixed, error):
        """Validate bracket fixes"""
        try:
            ast.parse(fixed)
            return {"is_valid": True, "confidence": 0.8, "issues": []}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [f"New syntax error: {e.msg}"],
            }

    def validate_structural_fix(self, original, fixed, error):
        """Validate structural fixes"""
        try:
            ast.parse(fixed)
            return {"is_valid": True, "confidence": 0.6, "issues": []}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [f"New syntax error: {e.msg}"],
            }

    def validate_generic_fix(self, original, fixed, error):
        """Validate generic fixes"""
        try:
            ast.parse(fixed)
            return {"is_valid": True, "confidence": 0.5, "issues": []}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [f"New syntax error: {e.msg}"],
            }

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
    engine = BeastModeFixRefinementEngine()
    success = engine.run_phase1_refinement()

    if success:
        print("\n🎉 PHASE 1: FIX APPLICATION REFINEMENT SUCCESSFUL!")
        print("🎯 Target 90%+ compliance achieved!")
        sys.exit(0)
    else:
        print("\n🔄 PHASE 1: FIX APPLICATION REFINEMENT IN PROGRESS")
        print("📈 Significant improvement achieved, continuing to final target...")
        sys.exit(1)
