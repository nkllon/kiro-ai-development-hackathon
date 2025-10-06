#!/usr/bin/env python3
"""
Repository Refactoring Orchestrator

This script orchestrates the entire repository refactoring process:
1. Analysis - Identify files needing refactoring
2. Planning - Generate refactoring plans
3. Execution - Execute refactoring safely
4. Validation - Validate results
5. Reporting - Generate comprehensive reports

This extends the models.py refactoring approach to the entire repository.
"""

import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RepositoryRefactoringOrchestrator:
    """Orchestrates the complete repository refactoring process"""

    def __init__(self, src_dir: str = "src", max_files: Optional[int] = None):
        self.src_dir = Path(src_dir)
        self.max_files = max_files
        self.scripts_dir = Path("scripts")
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

        # Timestamps for tracking
        self.start_time = None
        self.end_time = None

    def run_complete_refactoring(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run the complete refactoring process"""
        self.start_time = datetime.now()

        logger.info("🚀 Starting Repository-Wide Refactoring Process")
        logger.info("=" * 60)

        results = {
            "phase1_analysis": None,
            "phase2_planning": None,
            "phase3_execution": None,
            "phase4_validation": None,
            "phase5_reporting": None,
            "overall_success": False,
            "total_duration": None,
        }

        try:
            # Phase 1: Analysis
            logger.info("📊 Phase 1: Repository Analysis")
            results["phase1_analysis"] = self._run_analysis_phase()

            # Phase 2: Planning
            logger.info("📋 Phase 2: Refactoring Planning")
            results["phase2_planning"] = self._run_planning_phase()

            # Phase 3: Execution
            logger.info("🔄 Phase 3: Refactoring Execution")
            results["phase3_execution"] = self._run_execution_phase(dry_run)

            # Phase 4: Validation
            logger.info("🔍 Phase 4: Validation")
            results["phase4_validation"] = self._run_validation_phase()

            # Phase 5: Reporting
            logger.info("📊 Phase 5: Final Reporting")
            results["phase5_reporting"] = self._run_reporting_phase()

            results["overall_success"] = True

        except Exception as e:
            logger.error(f"❌ Refactoring process failed: {e}")
            results["error"] = str(e)

        finally:
            self.end_time = datetime.now()
            if self.start_time:
                results["total_duration"] = str(self.end_time - self.start_time)

        return results

    def _run_analysis_phase(self) -> Dict[str, Any]:
        """Run repository analysis phase"""
        logger.info("  🔍 Analyzing repository structure...")

        try:
            # Run the analysis engine
            result = subprocess.run(
                ["python", str(self.scripts_dir / "repository_refactoring_engine.py")],
                capture_output=True,
                text=True,
                cwd=".",
            )

            if result.returncode == 0:
                logger.info("  ✅ Analysis completed successfully")

                # Load analysis results
                if os.path.exists("repository_analysis_report.json"):
                    with open("repository_analysis_report.json", "r") as f:
                        analysis_data = json.load(f)

                    # Print key metrics
                    summary = analysis_data.get("summary", {})
                    logger.info(f"    📊 Total files: {summary.get('total_files', 0)}")
                    logger.info(f"    📊 Large files: {summary.get('large_files', 0)}")
                    logger.info(
                        f"    📊 Compliance rate: {summary.get('compliance_rate', 0):.1f}%"
                    )

                    return {
                        "success": True,
                        "files_analyzed": summary.get("total_files", 0),
                        "large_files_found": summary.get("large_files", 0),
                        "compliance_rate": summary.get("compliance_rate", 0),
                    }
                else:
                    logger.warning("  ⚠️ Analysis report not found")
                    return {"success": False, "error": "Analysis report not generated"}
            else:
                logger.error(f"  ❌ Analysis failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"  ❌ Analysis phase error: {e}")
            return {"success": False, "error": str(e)}

    def _run_planning_phase(self) -> Dict[str, Any]:
        """Run refactoring planning phase"""
        logger.info("  📋 Generating refactoring plans...")

        try:
            # Check if plans already exist
            if os.path.exists("refactoring_plans.json"):
                with open("refactoring_plans.json", "r") as f:
                    plans_data = json.load(f)

                plan_count = len(plans_data)
                logger.info(f"  ✅ Found {plan_count} refactoring plans")

                # Filter by max_files if specified
                if self.max_files and plan_count > self.max_files:
                    logger.info(f"  🔄 Limiting to {self.max_files} plans")
                    plans_data = plans_data[: self.max_files]

                    # Save limited plans
                    with open("refactoring_plans.json", "w") as f:
                        json.dump(plans_data, f, indent=2)

                return {
                    "success": True,
                    "plans_generated": len(plans_data),
                    "plans_file": "refactoring_plans.json",
                }
            else:
                logger.error("  ❌ Refactoring plans not found")
                return {"success": False, "error": "Plans not generated"}

        except Exception as e:
            logger.error(f"  ❌ Planning phase error: {e}")
            return {"success": False, "error": str(e)}

    def _run_execution_phase(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run refactoring execution phase"""
        logger.info(f"  🔄 Executing refactoring plans (dry_run={dry_run})...")

        try:
            # Build execution command
            cmd = ["python", str(self.scripts_dir / "refactoring_executor.py")]
            cmd.extend(["--plans", "refactoring_plans.json"])

            if dry_run:
                cmd.append("--dry-run")

            if self.max_files:
                cmd.extend(["--max-files", str(self.max_files)])

            # Run execution
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            if result.returncode == 0:
                logger.info("  ✅ Execution completed successfully")

                # Load execution results
                if os.path.exists("refactoring_execution_report.json"):
                    with open("refactoring_execution_report.json", "r") as f:
                        execution_data = json.load(f)

                    successful = sum(
                        1 for r in execution_data if r.get("success", False)
                    )
                    total = len(execution_data)

                    logger.info(f"    📊 Plans executed: {total}")
                    logger.info(f"    📊 Successful: {successful}")
                    logger.info(f"    📊 Success rate: {(successful/total)*100:.1f}%")

                    return {
                        "success": True,
                        "plans_executed": total,
                        "successful_executions": successful,
                        "success_rate": (successful / total) * 100 if total > 0 else 0,
                        "dry_run": dry_run,
                    }
                else:
                    logger.warning("  ⚠️ Execution report not found")
                    return {"success": False, "error": "Execution report not generated"}
            else:
                logger.error(f"  ❌ Execution failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"  ❌ Execution phase error: {e}")
            return {"success": False, "error": str(e)}

    def _run_validation_phase(self) -> Dict[str, Any]:
        """Run validation phase"""
        logger.info("  🔍 Validating refactored modules...")

        try:
            # Check if execution report exists
            if not os.path.exists("refactoring_execution_report.json"):
                logger.warning("  ⚠️ No execution report found, skipping validation")
                return {"success": False, "error": "No execution report found"}

            # Run validation
            result = subprocess.run(
                [
                    "python",
                    str(self.scripts_dir / "refactoring_validator.py"),
                    "--execution-report",
                    "refactoring_execution_report.json",
                    "--output",
                    "validation_report.json",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            if result.returncode == 0:
                logger.info("  ✅ Validation completed successfully")

                # Load validation results
                if os.path.exists("validation_report.json"):
                    with open("validation_report.json", "r") as f:
                        validation_data = json.load(f)

                    summary = validation_data.get("summary", {})
                    logger.info(
                        f"    📊 Modules validated: {summary.get('total_modules', 0)}"
                    )
                    logger.info(
                        f"    📊 Success rate: {summary.get('success_rate', 0):.1f}%"
                    )
                    logger.info(
                        f"    📊 RM-DDD compliant: {summary.get('rm_ddd_compliant', 0)}"
                    )

                    return {
                        "success": True,
                        "modules_validated": summary.get("total_modules", 0),
                        "success_rate": summary.get("success_rate", 0),
                        "rm_ddd_compliant": summary.get("rm_ddd_compliant", 0),
                    }
                else:
                    logger.warning("  ⚠️ Validation report not found")
                    return {
                        "success": False,
                        "error": "Validation report not generated",
                    }
            else:
                logger.error(f"  ❌ Validation failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"  ❌ Validation phase error: {e}")
            return {"success": False, "error": str(e)}

    def _run_reporting_phase(self) -> Dict[str, Any]:
        """Run final reporting phase"""
        logger.info("  📊 Generating final reports...")

        try:
            # Generate comprehensive report
            final_report = {
                "refactoring_session": {
                    "start_time": (
                        self.start_time.isoformat() if self.start_time else None
                    ),
                    "end_time": self.end_time.isoformat() if self.end_time else None,
                    "duration": (
                        str(self.end_time - self.start_time)
                        if self.start_time and self.end_time
                        else None
                    ),
                    "max_files_limit": self.max_files,
                },
                "reports_generated": [],
            }

            # List all generated reports
            report_files = [
                "repository_analysis_report.json",
                "refactoring_plans.json",
                "refactoring_execution_report.json",
                "validation_report.json",
            ]

            for report_file in report_files:
                if os.path.exists(report_file):
                    final_report["reports_generated"].append(report_file)

                    # Copy to reports directory
                    shutil.copy2(report_file, self.reports_dir / report_file)

            # Save final report
            final_report_file = (
                self.reports_dir
                / f"refactoring_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(final_report_file, "w") as f:
                json.dump(final_report, f, indent=2)

            logger.info(f"  ✅ Final report saved: {final_report_file}")
            logger.info(f"  📁 All reports available in: {self.reports_dir}")

            return {
                "success": True,
                "final_report": str(final_report_file),
                "reports_generated": len(final_report["reports_generated"]),
            }

        except Exception as e:
            logger.error(f"  ❌ Reporting phase error: {e}")
            return {"success": False, "error": str(e)}


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orchestrate repository-wide refactoring"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform dry run without making changes"
    )
    parser.add_argument(
        "--max-files", type=int, help="Maximum number of files to refactor"
    )
    parser.add_argument("--src-dir", default="src", help="Source directory to refactor")

    args = parser.parse_args()

    print("🚀 Repository Refactoring Orchestrator")
    print("=" * 45)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")

    if args.max_files:
        print(f"📊 Limiting to {args.max_files} files")

    # Initialize orchestrator
    orchestrator = RepositoryRefactoringOrchestrator(
        src_dir=args.src_dir, max_files=args.max_files
    )

    # Run complete refactoring process
    results = orchestrator.run_complete_refactoring(dry_run=args.dry_run)

    # Print final summary
    print("\n" + "=" * 60)
    print("📊 REFACTORING SESSION SUMMARY")
    print("=" * 60)

    phases = [
        "phase1_analysis",
        "phase2_planning",
        "phase3_execution",
        "phase4_validation",
        "phase5_reporting",
    ]
    phase_names = ["Analysis", "Planning", "Execution", "Validation", "Reporting"]

    for phase, name in zip(phases, phase_names):
        result = results.get(phase, {})
        status = "✅" if result.get("success", False) else "❌"
        print(
            f"{status} {name}: {'Success' if result.get('success', False) else 'Failed'}"
        )

        if not result.get("success", False) and "error" in result:
            print(f"    Error: {result['error']}")

    print(f"\n⏱️  Total Duration: {results.get('total_duration', 'Unknown')}")
    print(
        f"🎯 Overall Success: {'✅ Yes' if results.get('overall_success', False) else '❌ No'}"
    )

    if args.dry_run:
        print("\n🔍 This was a dry run - no files were actually modified")
        print("   Run without --dry-run to execute actual refactoring")
    else:
        print(f"\n📁 Check the reports/ directory for detailed results")


if __name__ == "__main__":
    import shutil

    main()
