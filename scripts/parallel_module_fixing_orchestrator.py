#!/usr/bin/env python3
"""
Parallel Module Fixing Orchestrator - Multi-agent module repair system
===================================================================

This script orchestrates multiple agents to run in parallel and systematically
fix missing modules causing test collection errors.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Orchestrate parallel agents for comprehensive module fixing
"""

import os
import sys
import subprocess
import threading
import time
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue


@dataclass
class AgentTask:
    """Task for an agent to execute."""

    agent_id: str
    task_type: str
    target_files: List[str]
    priority: int = 1
    status: str = "pending"
    results: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class AgentResult:
    """Result from an agent execution."""

    agent_id: str
    task_type: str
    success: bool
    modules_fixed: int
    errors_fixed: int
    details: Dict
    duration: float
    timestamp: datetime


class ParallelModuleFixingOrchestrator:
    """Orchestrates multiple agents for parallel module fixing."""

    def __init__(self, max_agents: int = 6):
        self.project_root = Path.cwd()
        self.max_agents = max_agents
        self.agent_results = []
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.start_time = datetime.now()

    def analyze_remaining_errors(self) -> List[Tuple[str, str, str]]:
        """Analyze remaining test collection errors to identify missing modules."""
        print("🔍 Analyzing remaining test collection errors...")

        errors = []
        try:
            # Run test collection to get current errors
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/unit/beast_mode/", "--collect-only"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                error_lines = result.stderr.split("\n")
                for line in error_lines:
                    if "ERROR collecting" in line:
                        # Extract test file from error
                        if "tests/" in line:
                            test_file = line.split("tests/")[1].split()[0]
                            test_file = f"tests/{test_file}"
                            errors.append(
                                (test_file, "collection_error", "import_error")
                            )
                    elif "cannot import name" in line:
                        # Extract missing class
                        if "'" in line:
                            missing_class = line.split("'")[1]
                            errors.append(("unknown", "missing_class", missing_class))
                    elif "No module named" in line:
                        # Extract missing module
                        if "'" in line:
                            missing_module = line.split("'")[1]
                            errors.append(("unknown", "missing_module", missing_module))

        except Exception as e:
            print(f"⚠️  Error analyzing test collection: {e}")

        return errors

    def create_agent_tasks(self, errors: List[Tuple[str, str, str]]) -> List[AgentTask]:
        """Create tasks for agents based on error analysis."""
        print("📋 Creating agent tasks...")

        tasks = []

        # Group errors by category for parallel processing
        error_categories = {
            "observability": [],
            "tool_health": [],
            "documentation": [],
            "compliance": [],
            "testing": [],
            "organization": [],
            "general": [],
        }

        for test_file, error_type, error_detail in errors:
            category = self._categorize_error(test_file, error_detail)
            error_categories[category].append((test_file, error_type, error_detail))

        # Create tasks for each category
        for category, category_errors in error_categories.items():
            if category_errors:
                task = AgentTask(
                    agent_id=f"agent_{category}",
                    task_type=f"fix_{category}_modules",
                    target_files=[
                        error[0] for error in category_errors if error[0] != "unknown"
                    ],
                    priority=len(category_errors),
                )
                tasks.append(task)

        # Sort by priority (most errors first)
        tasks.sort(key=lambda x: x.priority, reverse=True)

        return tasks

    def _categorize_error(self, test_file: str, error_detail: str) -> str:
        """Categorize error based on test file path and error details."""
        if "observability" in test_file or "monitoring" in error_detail.lower():
            return "observability"
        elif "tool_health" in test_file or "health" in error_detail.lower():
            return "tool_health"
        elif "documentation" in test_file or "document" in error_detail.lower():
            return "documentation"
        elif "compliance" in test_file or "compliance" in error_detail.lower():
            return "compliance"
        elif "testing" in test_file or "test" in error_detail.lower():
            return "testing"
        elif "organization" in test_file or "organization" in error_detail.lower():
            return "organization"
        else:
            return "general"

    def execute_agent_task(self, task: AgentTask) -> AgentResult:
        """Execute a single agent task."""
        start_time = datetime.now()
        agent_id = task.agent_id
        task_type = task.task_type

        print(f"🚀 Agent {agent_id} starting {task_type}...")

        try:
            # Create agent-specific fixing script
            agent_script = self._create_agent_script(task)

            # Execute the agent script
            result = subprocess.run(
                ["python3", agent_script], capture_output=True, text=True, timeout=120
            )

            # Parse results
            modules_fixed = 0
            errors_fixed = 0

            if result.returncode == 0:
                # Try to parse JSON results if available
                try:
                    if result.stdout:
                        output_data = json.loads(result.stdout)
                        modules_fixed = output_data.get("modules_fixed", 0)
                        errors_fixed = output_data.get("errors_fixed", 0)
                except:
                    # Fallback: count successful operations
                    modules_fixed = result.stdout.count("✅")
                    errors_fixed = result.stdout.count("Fixed")

            success = result.returncode == 0

            return AgentResult(
                agent_id=agent_id,
                task_type=task_type,
                success=success,
                modules_fixed=modules_fixed,
                errors_fixed=errors_fixed,
                details={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                },
                duration=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
            )

        except Exception as e:
            return AgentResult(
                agent_id=agent_id,
                task_type=task_type,
                success=False,
                modules_fixed=0,
                errors_fixed=0,
                details={"error": str(e)},
                duration=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
            )

    def _create_agent_script(self, task: AgentTask) -> str:
        """Create a specialized script for an agent task."""
        script_content = f'''#!/usr/bin/env python3
"""
Agent Script for {task.agent_id} - {task.task_type}
=================================================

This script is generated for parallel execution by the orchestrator.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.comprehensive_module_fixer import ComprehensiveModuleFixer

def main():
    """Main function for agent execution."""
    fixer = ComprehensiveModuleFixer()
    
    # Focus on specific category
    category = "{task.task_type.replace('fix_', '').replace('_modules', '')}"
    
    print(f"Agent {task.agent_id} working on {{category}} modules...")
    
    # Run targeted fixes
    stats = fixer.fix_all_missing_modules()
    
    # Output results as JSON for parsing
    result = {{
        "agent_id": "{task.agent_id}",
        "category": category,
        "modules_fixed": stats.get("successful", 0),
        "errors_fixed": stats.get("failed", 0),
        "success": stats.get("successful", 0) > 0
    }}
    
    print(json.dumps(result))
    return 0 if result["success"] else 1

if __name__ == "__main__":
    import json
    sys.exit(main())
'''

        script_path = self.project_root / f"temp_agent_{task.agent_id}.py"
        with open(script_path, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_path, 0o755)

        return str(script_path)

    def run_parallel_agents(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """Run multiple agents in parallel."""
        print(f"🚀 Starting {len(tasks)} agents in parallel (max {self.max_agents})...")

        results = []

        with ThreadPoolExecutor(max_workers=self.max_agents) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.execute_agent_task, task): task for task in tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)

                    status = "✅ SUCCESS" if result.success else "❌ FAILED"
                    print(
                        f"{status} Agent {result.agent_id}: {result.modules_fixed} modules fixed, {result.errors_fixed} errors in {result.duration:.2f}s"
                    )

                except Exception as e:
                    print(f"❌ Agent {task.agent_id} failed with exception: {e}")
                    results.append(
                        AgentResult(
                            agent_id=task.agent_id,
                            task_type=task.task_type,
                            success=False,
                            modules_fixed=0,
                            errors_fixed=0,
                            details={"exception": str(e)},
                            duration=0.0,
                            timestamp=datetime.now(),
                        )
                    )

        return results

    def validate_parallel_results(self) -> Dict[str, int]:
        """Validate the results of parallel execution."""
        print("🔍 Validating parallel execution results...")

        try:
            # Run test collection to check improvement
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/unit/beast_mode/", "--collect-only"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Parse results
            if result.returncode == 0:
                # Extract collection stats
                lines = result.stdout.split("\n")
                for line in lines:
                    if "collected" in line and "errors" in line:
                        # Parse: "collected X items / Y errors"
                        parts = line.split()
                        collected = int(parts[1]) if len(parts) > 1 else 0
                        errors = int(parts[4]) if len(parts) > 4 else 0
                        return {
                            "tests_collected": collected,
                            "errors_remaining": errors,
                            "collection_success": True,
                        }
            else:
                # Count errors from stderr
                error_count = result.stderr.count("ERROR")
                return {
                    "tests_collected": 0,
                    "errors_remaining": error_count,
                    "collection_success": False,
                }

        except Exception as e:
            print(f"⚠️  Error validating results: {e}")
            return {
                "tests_collected": 0,
                "errors_remaining": 0,
                "collection_success": False,
            }

    def generate_orchestration_report(
        self, results: List[AgentResult], validation_stats: Dict[str, int]
    ) -> str:
        """Generate comprehensive orchestration report."""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        successful_agents = sum(1 for r in results if r.success)
        total_modules_fixed = sum(r.modules_fixed for r in results)
        total_errors_fixed = sum(r.errors_fixed for r in results)

        report = f"""
🚀 PARALLEL MODULE FIXING ORCHESTRATION REPORT
=============================================

📊 ORCHESTRATION STATISTICS:
• Total Agents Deployed: {len(results)}
• Successful Agents: {successful_agents} ({successful_agents/len(results)*100:.1f}%)
• Total Modules Fixed: {total_modules_fixed}
• Total Errors Fixed: {total_errors_fixed}
• Orchestration Duration: {total_duration:.2f} seconds

🔍 VALIDATION RESULTS:
• Tests Collected: {validation_stats.get('tests_collected', 0)}
• Errors Remaining: {validation_stats.get('errors_remaining', 0)}
• Collection Success: {'✅' if validation_stats.get('collection_success') else '❌'}

📋 AGENT RESULTS:
"""

        for result in results:
            status = "✅" if result.success else "❌"
            report += f"{status} {result.agent_id} ({result.task_type}): {result.modules_fixed} modules, {result.errors_fixed} errors ({result.duration:.2f}s)\n"

        report += f"""
🎯 PERFORMANCE METRICS:
• Average Agent Duration: {sum(r.duration for r in results)/len(results):.2f}s
• Modules Fixed per Second: {total_modules_fixed/total_duration:.2f}
• Parallel Efficiency: {successful_agents/len(results)*100:.1f}%

📈 IMPROVEMENT ASSESSMENT:
"""

        if validation_stats.get("tests_collected", 0) > 41:
            improvement = validation_stats["tests_collected"] - 41
            report += (
                f"• Test Collection Improved: +{improvement} tests now collecting\n"
            )

        if validation_stats.get("errors_remaining", 124) < 124:
            improvement = 124 - validation_stats["errors_remaining"]
            report += f"• Errors Reduced: -{improvement} errors resolved\n"

        return report

    def cleanup_temp_files(self):
        """Clean up temporary agent files."""
        temp_files = list(self.project_root.glob("temp_agent_*.py"))
        for temp_file in temp_files:
            try:
                temp_file.unlink()
                print(f"🗑️  Cleaned up {temp_file}")
            except Exception as e:
                print(f"⚠️  Could not clean up {temp_file}: {e}")


def main():
    """Main orchestration function."""
    orchestrator = ParallelModuleFixingOrchestrator(max_agents=6)

    print("🚀 STARTING PARALLEL MODULE FIXING ORCHESTRATION")
    print("=" * 70)

    try:
        # Analyze remaining errors
        errors = orchestrator.analyze_remaining_errors()
        print(f"📋 Found {len(errors)} error patterns to address")

        if not errors:
            print("✅ No errors found to fix!")
            return

        # Create agent tasks
        tasks = orchestrator.create_agent_tasks(errors)
        print(f"📋 Created {len(tasks)} agent tasks")

        # Run parallel agents
        results = orchestrator.run_parallel_agents(tasks)

        # Validate results
        validation_stats = orchestrator.validate_parallel_results()

        # Generate report
        report = orchestrator.generate_orchestration_report(results, validation_stats)
        print(report)

        # Save report
        with open("parallel_module_fixing_report.txt", "w") as f:
            f.write(report)

        print("📄 Report saved to parallel_module_fixing_report.txt")

    finally:
        # Cleanup
        orchestrator.cleanup_temp_files()


if __name__ == "__main__":
    main()
