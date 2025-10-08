#!/usr/bin/env python3
"""
Beast Mode Comprehensive Test Runner

This script implements systematic testing with:
- PDCA loops for continuous improvement
- RCA (Root Cause Analysis) for failure investigation
- RDI (Requirements-Design-Implementation) traceability
- Pattern-based error analysis with enhanced logging
- Comprehensive profiling and monitoring

Usage:
    python run_beast_mode_comprehensive_tests.py [test_path] [--coverage] [--rca] [--profile]
"""

import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.beast_mode.testing.beast_mode_test_orchestrator import (
    BeastModeTestOrchestrator,
    TestPhase,
    TestFailurePattern,
)


def setup_logging_directory():
    """Setup logging directory structure"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create subdirectories for different log types
    (log_dir / "pdca_cycles").mkdir(exist_ok=True)
    (log_dir / "rca_analysis").mkdir(exist_ok=True)
    (log_dir / "performance").mkdir(exist_ok=True)
    (log_dir / "patterns").mkdir(exist_ok=True)

    return log_dir


def create_test_requirements() -> List[str]:
    """Define comprehensive test requirements for RDI tracing"""
    return [
        "REQ-001: Beast Mode core functionality must be testable",
        "REQ-002: DAG orchestration models must validate correctly",
        "REQ-003: Visual diagram validation must process formats",
        "REQ-004: RCA integration must detect failure patterns",
        "REQ-005: PDCA loops must drive continuous improvement",
        "REQ-006: Logging must provide comprehensive traceability",
        "REQ-007: Profiling must capture performance metrics",
        "REQ-008: Error patterns must be systematically analyzed",
        "REQ-009: Test coverage must exceed 80% for core modules",
        "REQ-010: Test execution must complete within time limits",
    ]


def run_comprehensive_test_suite(
    test_paths: List[str],
    enable_coverage: bool = True,
    enable_rca: bool = True,
    enable_profiling: bool = True,
) -> Dict[str, Any]:
    """
    Run comprehensive test suite with Beast Mode orchestration
    """
    print("🐺 Beast Mode Comprehensive Test Suite")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 Test Paths: {', '.join(test_paths)}")
    print(f"📊 Coverage: {'Enabled' if enable_coverage else 'Disabled'}")
    print(f"🔬 RCA: {'Enabled' if enable_rca else 'Disabled'}")
    print(f"📈 Profiling: {'Enabled' if enable_profiling else 'Disabled'}")
    print("=" * 60)

    # Setup logging
    log_dir = setup_logging_directory()

    # Initialize Beast Mode Test Orchestrator
    orchestrator = BeastModeTestOrchestrator("comprehensive_test_orchestrator")
    orchestrator.config.update(
        {
            "enable_profiling": enable_profiling,
            "enable_rca": enable_rca,
            "enable_rdi_tracing": True,
            "log_level": "DEBUG",
        }
    )

    # Define test requirements for RDI tracing
    requirements = create_test_requirements()

    # Results tracking
    overall_results = {
        "start_time": datetime.now().isoformat(),
        "test_paths": test_paths,
        "pdca_cycles": [],
        "total_tests_run": 0,
        "total_passed": 0,
        "total_failed": 0,
        "failure_patterns": {},
        "performance_metrics": {},
        "rca_analyses": [],
        "improvements_implemented": [],
    }

    try:
        # Execute tests for each path with PDCA cycles
        for i, test_path in enumerate(test_paths):
            print(f"\n🎯 Starting PDCA Cycle {i+1}/{len(test_paths)}: {test_path}")
            print("-" * 50)

            # Start PDCA cycle
            cycle_id = orchestrator.start_pdca_cycle(test_path, requirements)
            print(f"📋 PLAN Phase: Cycle {cycle_id} initialized")

            try:
                # DO Phase: Execute tests
                print("🚀 DO Phase: Executing tests...")
                test_result = orchestrator.execute_test_suite(
                    test_path, coverage=enable_coverage, timeout=300
                )

                print(
                    f"✅ Test execution completed: Exit code {test_result['exit_code']}"
                )
                if test_result.get("coverage", 0) > 0:
                    print(f"📊 Coverage: {test_result['coverage']:.1f}%")

                # Update overall results
                overall_results["total_tests_run"] += 1
                if test_result["exit_code"] == 0:
                    overall_results["total_passed"] += 1
                else:
                    overall_results["total_failed"] += 1

                # CHECK Phase: Analyze results
                print("🔍 CHECK Phase: Analyzing results...")
                check_results = orchestrator.check_test_results()

                success_criteria_met = check_results["success_criteria_met"]
                print(
                    f"📈 Success Criteria: {'✅ Met' if success_criteria_met else '❌ Not Met'}"
                )

                # Display failure pattern analysis
                pattern_analysis = check_results.get("failure_pattern_analysis", {})
                if pattern_analysis.get("pattern_frequency"):
                    print("🔍 Failure Patterns Detected:")
                    for pattern, count in pattern_analysis["pattern_frequency"].items():
                        print(f"  • {pattern}: {count} occurrences")
                        overall_results["failure_patterns"][pattern] = (
                            overall_results["failure_patterns"].get(pattern, 0) + count
                        )

                # Display performance analysis
                perf_analysis = check_results.get("performance_analysis", {})
                if perf_analysis:
                    print("📊 Performance Analysis:")
                    exec_analysis = perf_analysis.get("execution_time_analysis", {})
                    if exec_analysis:
                        print(
                            f"  • Duration: {exec_analysis.get('duration_seconds', 0):.2f}s"
                        )
                        print(
                            f"  • Rating: {exec_analysis.get('performance_rating', 'unknown')}"
                        )

                    resource_analysis = perf_analysis.get("resource_usage_analysis", {})
                    if resource_analysis:
                        print(
                            f"  • Memory: {resource_analysis.get('memory_mb', 0):.1f} MB"
                        )
                        print(
                            f"  • CPU: {resource_analysis.get('cpu_percent', 0):.1f}%"
                        )

                # ACT Phase: Implement improvements
                print("⚡ ACT Phase: Implementing improvements...")
                actions_taken = orchestrator.act_on_results(check_results)

                if actions_taken:
                    print("🔧 Improvements Implemented:")
                    for action in actions_taken:
                        print(f"  • {action}")
                        overall_results["improvements_implemented"].append(action)
                else:
                    print("✅ No improvements needed - system performing optimally")

                # Store PDCA cycle results
                cycle_results = {
                    "cycle_id": cycle_id,
                    "test_path": test_path,
                    "success": success_criteria_met,
                    "actions_taken": actions_taken,
                    "performance": perf_analysis,
                    "patterns": pattern_analysis,
                }
                overall_results["pdca_cycles"].append(cycle_results)

                print(f"✅ PDCA Cycle {i+1} completed successfully")

            except Exception as e:
                print(f"❌ PDCA Cycle {i+1} failed: {str(e)}")
                overall_results["total_failed"] += 1

                # Still try to complete the cycle for learning
                try:
                    check_results = orchestrator.check_test_results()
                    actions_taken = orchestrator.act_on_results(check_results)
                    overall_results["improvements_implemented"].extend(actions_taken)
                except:
                    pass

                # Record failure for analysis
                failure_info = {
                    "cycle_id": cycle_id,
                    "test_path": test_path,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
                overall_results["pdca_cycles"].append(failure_info)

        # Final analysis and reporting
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST ANALYSIS")
        print("=" * 60)

        # Overall statistics
        total_tests = overall_results["total_tests_run"]
        passed_tests = overall_results["total_passed"]
        failed_tests = overall_results["total_failed"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"📈 Overall Results:")
        print(f"  • Total Tests: {total_tests}")
        print(f"  • Passed: {passed_tests}")
        print(f"  • Failed: {failed_tests}")
        print(f"  • Success Rate: {success_rate:.1f}%")

        # PDCA cycle analysis
        successful_cycles = len(
            [c for c in overall_results["pdca_cycles"] if c.get("success", False)]
        )
        print(f"\n🔄 PDCA Cycle Analysis:")
        print(f"  • Total Cycles: {len(overall_results['pdca_cycles'])}")
        print(f"  • Successful Cycles: {successful_cycles}")
        print(
            f"  • Cycle Success Rate: {(successful_cycles / len(overall_results['pdca_cycles']) * 100) if overall_results['pdca_cycles'] else 0:.1f}%"
        )

        # Failure pattern summary
        if overall_results["failure_patterns"]:
            print(f"\n🔍 Failure Pattern Summary:")
            sorted_patterns = sorted(
                overall_results["failure_patterns"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for pattern, count in sorted_patterns[:5]:  # Top 5 patterns
                print(f"  • {pattern}: {count} occurrences")

        # Improvements summary
        if overall_results["improvements_implemented"]:
            print(f"\n⚡ Improvements Implemented:")
            unique_improvements = list(set(overall_results["improvements_implemented"]))
            for improvement in unique_improvements[:5]:  # Top 5 improvements
                print(f"  • {improvement}")

        # Health check
        health_indicators = orchestrator.get_health_indicators()
        print(f"\n🏥 System Health:")
        print(f"  • Orchestrator Status: {orchestrator.get_module_status()}")
        print(f"  • Total Metrics Collected: {health_indicators['total_test_metrics']}")
        print(
            f"  • Patterns Detected: {health_indicators['failure_patterns_detected']}"
        )
        print(f"  • RCA Engine: {health_indicators['rca_engine_status']}")

        # Save comprehensive results
        overall_results["end_time"] = datetime.now().isoformat()
        overall_results["duration_seconds"] = (
            datetime.now() - datetime.fromisoformat(overall_results["start_time"])
        ).total_seconds()
        overall_results["health_indicators"] = health_indicators

        # Write results to file
        results_file = (
            log_dir
            / f"comprehensive_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(results_file, "w") as f:
            json.dump(overall_results, f, indent=2, default=str)

        print(f"\n📄 Detailed results saved to: {results_file}")

        # Final Beast Mode assessment
        beast_mode_score = calculate_beast_mode_score(overall_results)
        print(f"\n🐺 Beast Mode Score: {beast_mode_score:.2f}/10.00")
        print_beast_mode_assessment(beast_mode_score)

        return overall_results

    except Exception as e:
        print(f"\n❌ Comprehensive test suite failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"error": str(e), "status": "failed"}


def calculate_beast_mode_score(results: Dict[str, Any]) -> float:
    """Calculate Beast Mode effectiveness score"""
    score = 0.0
    max_score = 10.0

    # Success rate (30% of score)
    total_tests = results["total_tests_run"]
    if total_tests > 0:
        success_rate = results["total_passed"] / total_tests
        score += success_rate * 3.0

    # PDCA cycle effectiveness (25% of score)
    cycles = results["pdca_cycles"]
    if cycles:
        successful_cycles = len([c for c in cycles if c.get("success", False)])
        cycle_success_rate = successful_cycles / len(cycles)
        score += cycle_success_rate * 2.5

    # Improvement implementation (20% of score)
    improvements = len(set(results["improvements_implemented"]))
    score += min(improvements / 5.0, 1.0) * 2.0  # Max 2 points for 5+ improvements

    # Pattern detection and analysis (15% of score)
    patterns_detected = len(results["failure_patterns"])
    score += min(patterns_detected / 3.0, 1.0) * 1.5  # Max 1.5 points for 3+ patterns

    # System health (10% of score)
    health_indicators = results.get("health_indicators", {})
    if health_indicators.get("rca_engine_status") == "active":
        score += 0.5
    if health_indicators.get("total_test_metrics", 0) > 0:
        score += 0.5

    return min(score, max_score)


def print_beast_mode_assessment(score: float):
    """Print Beast Mode assessment based on score"""
    if score >= 9.0:
        print("🏆 BEAST MODE MASTERY: Systematic excellence achieved!")
        print("   • PDCA cycles driving continuous improvement")
        print("   • RCA providing deep failure insights")
        print("   • RDI traceability ensuring quality")
        print("   • Pattern analysis preventing future issues")
    elif score >= 7.0:
        print("🥇 BEAST MODE PROFICIENCY: Strong systematic approach!")
        print("   • Good PDCA cycle implementation")
        print("   • Effective failure analysis")
        print("   • Solid improvement implementation")
    elif score >= 5.0:
        print("🥈 BEAST MODE DEVELOPING: Good foundation with room for growth")
        print("   • Basic systematic principles applied")
        print("   • Some improvement opportunities identified")
    else:
        print("🥉 BEAST MODE EMERGING: Focus on systematic fundamentals")
        print("   • Strengthen PDCA cycle implementation")
        print("   • Enhance RCA and pattern analysis")
        print("   • Improve systematic approach consistency")


def main():
    """Main entry point for Beast Mode comprehensive testing"""
    parser = argparse.ArgumentParser(
        description="Beast Mode Comprehensive Test Runner with RCA and RDI tracing"
    )
    parser.add_argument(
        "test_paths",
        nargs="*",
        default=[
            "tests/test_dag_models_simple.py",
            "tests/test_core_models.py",
            "tests/test_format_router.py",
            "tests/test_beast_mode_core.py",
        ],
        help="Test paths to execute (default: core test suite)",
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Disable coverage analysis"
    )
    parser.add_argument("--no-rca", action="store_true", help="Disable RCA analysis")
    parser.add_argument(
        "--no-profiling", action="store_true", help="Disable performance profiling"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Run quick test suite (core tests only)"
    )

    args = parser.parse_args()

    # Adjust test paths for quick mode
    if args.quick:
        test_paths = ["tests/test_dag_models_simple.py", "tests/test_core_models.py"]
    else:
        test_paths = args.test_paths

    # Run comprehensive test suite
    results = run_comprehensive_test_suite(
        test_paths=test_paths,
        enable_coverage=not args.no_coverage,
        enable_rca=not args.no_rca,
        enable_profiling=not args.no_profiling,
    )

    # Exit with appropriate code
    if results.get("error"):
        sys.exit(1)
    elif results.get("total_failed", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
