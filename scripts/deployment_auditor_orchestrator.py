#!/usr/bin/env python3
"""
Deployment Data Auditor Orchestrator

Comprehensive orchestration system for DAG execution with Beast Mode integration,
Redis coordination, and systematic execution management.
"""

import os
import sys
import json
import subprocess
import time
import redis
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path for Beast Mode integration
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from rm_ddd.core.unified_reflective_module import ReflectiveModule
    BEAST_MODE_AVAILABLE = True
except ImportError:
    BEAST_MODE_AVAILABLE = False
    class ReflectiveModule:
        def __init__(self):
            pass

@dataclass
class ExecutionResult:
    """Result of task execution."""
    task_id: str
    success: bool
    duration: float
    output: str
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DeploymentAuditorOrchestrator(ReflectiveModule if BEAST_MODE_AVAILABLE else object):
    """Orchestrate DAG execution with Beast Mode integration and Redis coordination."""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        if BEAST_MODE_AVAILABLE:
            super().__init__()
            self.register_metric("orchestration_tasks_executed", "counter", "Total tasks executed")
            self.register_metric("orchestration_tasks_failed", "counter", "Total tasks failed")
            self.register_metric("orchestration_execution_time", "histogram", "Task execution time")
            self.register_metric("orchestration_parallel_efficiency", "gauge", "Parallel execution efficiency")
    
    # Beast Mode ReflectiveModule implementation
    def get_capabilities(self) -> Dict[str, Any]:
        """Get orchestrator capabilities."""
        return {
            "name": "DeploymentAuditorOrchestrator",
            "version": "1.0.0",
            "capabilities": ["dag_orchestration", "parallel_execution", "redis_coordination", "task_management"]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status."""
        return {
            "status": "healthy",
            "redis_connected": self.redis_client is not None,
            "execution_id": self.execution_id,
            "beast_mode_available": BEAST_MODE_AVAILABLE
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "deployment_auditor_orchestrator",
            "module_type": "orchestration_system",
            "beast_mode_integration": BEAST_MODE_AVAILABLE,
            "redis_integration": self.redis_client is not None
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "sequential_execution",
            "parallel_disabled": True
        }
        
        self.redis_client = None
        self.execution_id = f"deployment_auditor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # DAG structure with dependencies
        self.dag_structure = {
            # Foundation Layer - No dependencies
            "foundation": {
                "tasks": ["1.1", "1.2", "1.3", "6.1", "6.2", "6.3", "9.1", "9.2", "9.3"],
                "dependencies": [],
                "estimated_hours": 4.0
            },
            # Core Layer - Depends on foundation
            "core": {
                "tasks": ["2.1", "2.2", "2.3", "3.1", "3.2", "3.3"],
                "dependencies": ["foundation"],
                "estimated_hours": 4.0
            },
            # Integration Layer - Depends on core
            "integration": {
                "tasks": ["4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "5.4"],
                "dependencies": ["core"],
                "estimated_hours": 4.0
            },
            # Optimization Layer - Depends on integration
            "optimization": {
                "tasks": ["7.1", "7.2", "7.3", "8.1", "8.2", "8.3"],
                "dependencies": ["integration"],
                "estimated_hours": 4.0
            },
            # Validation Layer - Depends on optimization
            "validation": {
                "tasks": ["10.1", "10.2", "10.3", "10.4"],
                "dependencies": ["optimization"],
                "estimated_hours": 5.0
            }
        }
        
        # Task-level dependencies
        self.task_dependencies = {
            "1.3": ["1.1", "1.2"],
            "6.2": ["6.1"],
            "6.3": ["6.1", "6.2"],
            "9.1": ["1.2"],
            "9.2": ["1.2"],
            "9.3": ["9.1", "9.2"],
            "2.1": ["1.2", "6.1"],
            "2.2": ["1.2", "6.1"],
            "2.3": ["2.1", "2.2"],
            "3.1": ["1.2", "6.1"],
            "3.2": ["3.1"],
            "3.3": ["3.1", "3.2"],
            "4.1": ["3.2"],
            "4.2": ["3.2"],
            "4.3": ["4.1", "4.2"],
            "4.4": ["4.1", "4.2", "4.3"],
            "5.1": ["3.2"],
            "5.2": ["5.1"],
            "5.3": ["1.2", "5.1"],
            "5.4": ["5.1", "5.2", "5.3"],
            "7.1": ["1.2", "5.3"],
            "7.2": ["2.1", "7.1"],
            "7.3": ["7.1", "7.2"],
            "8.1": ["4.3", "5.2"],
            "8.2": ["8.1"],
            "8.3": ["8.1", "8.2"],
            "10.1": ["4.3", "5.2", "8.2"],
            "10.2": ["9.2", "10.1"],
            "10.3": ["10.1", "10.2"],
            "10.4": ["10.2", "10.3"]
        }
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True,
                socket_timeout=5
            )
            self.redis_client.ping()
            print(f"✅ Redis connection established: {redis_host}:{redis_port}")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("   Continuing without Redis coordination")
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
    def _log_execution_event(self, event_type: str, data: Dict[str, Any]):
        """Log execution events to Redis and local storage."""
        event = {
            "execution_id": self.execution_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        # Log to Redis if available
        if self.redis_client:
            try:
                self.redis_client.lpush(
                    f"deployment_auditor:execution:{self.execution_id}:events",
                    json.dumps(event)
                )
                self.redis_client.expire(
                    f"deployment_auditor:execution:{self.execution_id}:events",
                    86400  # 24 hours
                )
            except Exception as e:
                print(f"⚠️  Redis logging failed: {e}")
        
        # Log to local file
        log_file = Path(f"logs/orchestration_{self.execution_id}.log")
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def _check_task_dependencies(self, task_id: str) -> bool:
        """Check if all dependencies for a task are satisfied."""
        dependencies = self.task_dependencies.get(task_id, [])
        
        for dep_id in dependencies:
            completion_file = Path(f".task-{dep_id}-complete")
            if not completion_file.exists():
                return False
        
        return True
    
    def _execute_task(self, task_id: str) -> ExecutionResult:
        """Execute a single task."""
        script_name = f"execute_task_{task_id.replace('.', '_')}.py"
        script_path = Path("scripts") / script_name
        
        if not script_path.exists():
            return ExecutionResult(
                task_id=task_id,
                success=False,
                duration=0.0,
                output="",
                error=f"Script not found: {script_path}"
            )
        
        started_at = datetime.now()
        
        try:
            # Execute the task script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            success = result.returncode == 0
            
            execution_result = ExecutionResult(
                task_id=task_id,
                success=success,
                duration=duration,
                output=result.stdout,
                error=result.stderr if not success else None,
                started_at=started_at,
                completed_at=completed_at
            )
            
            # Log execution event
            self._log_execution_event("task_completed", {
                "task_id": task_id,
                "success": success,
                "duration": duration,
                "error": execution_result.error
            })
            
            # Update Beast Mode metrics
            if BEAST_MODE_AVAILABLE:
                self.increment_metric("orchestration_tasks_executed")
                if not success:
                    self.increment_metric("orchestration_tasks_failed")
                self.observe_metric("orchestration_execution_time", duration)
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                task_id=task_id,
                success=False,
                duration=3600.0,
                output="",
                error="Task execution timed out after 1 hour"
            )
        except Exception as e:
            return ExecutionResult(
                task_id=task_id,
                success=False,
                duration=0.0,
                output="",
                error=f"Execution error: {str(e)}"
            )
    
    def _execute_parallel_group(self, group_name: str, task_ids: List[str], max_workers: int = 4) -> List[ExecutionResult]:
        """Execute a group of tasks in parallel."""
        print(f"\n🚀 Starting parallel group: {group_name}")
        print(f"   Tasks: {', '.join(task_ids)}")
        print(f"   Max workers: {max_workers}")
        
        group_start_time = datetime.now()
        results = []
        
        # Filter tasks that are ready to execute (dependencies satisfied)
        ready_tasks = []
        waiting_tasks = []
        
        for task_id in task_ids:
            if self._check_task_dependencies(task_id):
                ready_tasks.append(task_id)
            else:
                waiting_tasks.append(task_id)
        
        if waiting_tasks:
            print(f"   ⏳ Waiting for dependencies: {', '.join(waiting_tasks)}")
        
        # Execute ready tasks in parallel
        if ready_tasks:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all ready tasks
                future_to_task = {
                    executor.submit(self._execute_task, task_id): task_id 
                    for task_id in ready_tasks
                }
                
                # Process completed tasks
                for future in as_completed(future_to_task):
                    task_id = future_to_task[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        if result.success:
                            print(f"   ✅ {task_id}: Completed ({result.duration:.1f}s)")
                        else:
                            print(f"   ❌ {task_id}: Failed - {result.error}")
                            
                    except Exception as e:
                        print(f"   ❌ {task_id}: Exception - {str(e)}")
                        results.append(ExecutionResult(
                            task_id=task_id,
                            success=False,
                            duration=0.0,
                            output="",
                            error=f"Future exception: {str(e)}"
                        ))
        
        # Handle waiting tasks (execute sequentially after dependencies are met)
        for task_id in waiting_tasks:
            # Wait for dependencies with timeout
            max_wait_time = 3600  # 1 hour
            wait_start = datetime.now()
            
            while not self._check_task_dependencies(task_id):
                if (datetime.now() - wait_start).total_seconds() > max_wait_time:
                    print(f"   ❌ {task_id}: Dependency timeout")
                    results.append(ExecutionResult(
                        task_id=task_id,
                        success=False,
                        duration=0.0,
                        output="",
                        error="Dependency timeout - dependencies not satisfied within 1 hour"
                    ))
                    break
                
                time.sleep(10)  # Check every 10 seconds
            else:
                # Dependencies satisfied, execute task
                result = self._execute_task(task_id)
                results.append(result)
                
                if result.success:
                    print(f"   ✅ {task_id}: Completed ({result.duration:.1f}s)")
                else:
                    print(f"   ❌ {task_id}: Failed - {result.error}")
        
        group_duration = (datetime.now() - group_start_time).total_seconds()
        successful_tasks = sum(1 for r in results if r.success)
        
        print(f"   📊 Group {group_name} completed: {successful_tasks}/{len(task_ids)} tasks successful ({group_duration:.1f}s)")
        
        # Calculate parallel efficiency
        if BEAST_MODE_AVAILABLE and results:
            total_task_time = sum(r.duration for r in results)
            efficiency = (total_task_time / group_duration) if group_duration > 0 else 0
            self.observe_metric("orchestration_parallel_efficiency", efficiency)
        
        return results
    
    def execute_dag(self, max_workers: int = 4, continue_on_failure: bool = False) -> Dict[str, Any]:
        """Execute the complete DAG with parallel optimization."""
        print(f"🚀 Starting Deployment Data Auditor DAG Execution")
        print(f"   Execution ID: {self.execution_id}")
        print(f"   Max workers per group: {max_workers}")
        print(f"   Continue on failure: {continue_on_failure}")
        print("=" * 60)
        
        execution_start_time = datetime.now()
        all_results = []
        
        # Log execution start
        self._log_execution_event("execution_started", {
            "max_workers": max_workers,
            "continue_on_failure": continue_on_failure,
            "total_groups": len(self.dag_structure)
        })
        
        # Execute each parallel group in sequence
        for group_name, group_config in self.dag_structure.items():
            group_start_time = datetime.now()
            
            # Check group dependencies
            for dep_group in group_config["dependencies"]:
                # Verify all tasks in dependency group are complete
                dep_tasks = self.dag_structure[dep_group]["tasks"]
                incomplete_deps = []
                
                for dep_task in dep_tasks:
                    completion_file = Path(f".task-{dep_task}-complete")
                    if not completion_file.exists():
                        incomplete_deps.append(dep_task)
                
                if incomplete_deps:
                    error_msg = f"Group {group_name} cannot start - incomplete dependencies in {dep_group}: {', '.join(incomplete_deps)}"
                    print(f"❌ {error_msg}")
                    
                    if not continue_on_failure:
                        return {
                            "success": False,
                            "error": error_msg,
                            "execution_time": (datetime.now() - execution_start_time).total_seconds(),
                            "results": all_results
                        }
            
            # Execute the parallel group
            group_results = self._execute_parallel_group(
                group_name, 
                group_config["tasks"], 
                max_workers
            )
            
            all_results.extend(group_results)
            
            # Check for failures
            failed_tasks = [r for r in group_results if not r.success]
            if failed_tasks and not continue_on_failure:
                error_msg = f"Group {group_name} failed - {len(failed_tasks)} tasks failed"
                print(f"❌ {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - execution_start_time).total_seconds(),
                    "results": all_results,
                    "failed_tasks": [r.task_id for r in failed_tasks]
                }
            
            group_duration = (datetime.now() - group_start_time).total_seconds()
            print(f"✅ Group {group_name} completed in {group_duration:.1f}s")
        
        execution_duration = (datetime.now() - execution_start_time).total_seconds()
        successful_tasks = sum(1 for r in all_results if r.success)
        total_tasks = len(all_results)
        
        # Log execution completion
        self._log_execution_event("execution_completed", {
            "success": successful_tasks == total_tasks,
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": total_tasks - successful_tasks,
            "execution_time": execution_duration
        })
        
        print("\n" + "=" * 60)
        print(f"🎉 DAG Execution Completed!")
        print(f"   Total time: {execution_duration:.1f}s ({execution_duration/3600:.1f}h)")
        print(f"   Tasks: {successful_tasks}/{total_tasks} successful")
        
        if successful_tasks < total_tasks:
            failed_count = total_tasks - successful_tasks
            print(f"   ⚠️  {failed_count} tasks failed")
        
        return {
            "success": successful_tasks == total_tasks,
            "execution_time": execution_duration,
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": total_tasks - successful_tasks,
            "results": all_results,
            "execution_id": self.execution_id
        }
    
    def generate_execution_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive execution report."""
        report_content = [
            "# Deployment Data Auditor - DAG Execution Report",
            f"**Execution ID:** {self.execution_id}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            f"- **Total Execution Time:** {results['execution_time']:.1f} seconds ({results['execution_time']/3600:.1f} hours)",
            f"- **Tasks Executed:** {results['total_tasks']}",
            f"- **Successful Tasks:** {results['successful_tasks']}",
            f"- **Failed Tasks:** {results['failed_tasks']}",
            f"- **Success Rate:** {(results['successful_tasks']/results['total_tasks']*100):.1f}%",
            "",
        ]
        
        if results['failed_tasks'] > 0:
            report_content.extend([
                "## Failed Tasks",
                ""
            ])
            
            for result in results['results']:
                if not result.success:
                    report_content.extend([
                        f"### Task {result.task_id}",
                        f"- **Error:** {result.error}",
                        f"- **Duration:** {result.duration:.1f}s",
                        f"- **Output:** ```{result.output}```",
                        ""
                    ])
        
        # Group results by parallel group
        report_content.extend([
            "## Execution by Parallel Group",
            ""
        ])
        
        for group_name, group_config in self.dag_structure.items():
            group_results = [r for r in results['results'] if r.task_id in group_config['tasks']]
            successful = sum(1 for r in group_results if r.success)
            total = len(group_results)
            avg_duration = sum(r.duration for r in group_results) / len(group_results) if group_results else 0
            
            report_content.extend([
                f"### {group_name.title()} Layer",
                f"- **Tasks:** {total}",
                f"- **Successful:** {successful}",
                f"- **Average Duration:** {avg_duration:.1f}s",
                ""
            ])
            
            for result in group_results:
                status = "✅" if result.success else "❌"
                report_content.append(f"  {status} {result.task_id}: {result.duration:.1f}s")
            
            report_content.append("")
        
        return '\n'.join(report_content)

def main():
    """Main orchestration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Auditor DAG Orchestrator')
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--max-workers', type=int, default=4, help='Max parallel workers per group')
    parser.add_argument('--continue-on-failure', action='store_true', help='Continue execution even if tasks fail')
    parser.add_argument('--dry-run', action='store_true', help='Show execution plan without running')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = DeploymentAuditorOrchestrator(
        redis_host=args.redis_host,
        redis_port=args.redis_port
    )
    
    if args.dry_run:
        print("🔍 DAG Execution Plan (Dry Run)")
        print("=" * 40)
        
        for group_name, group_config in orchestrator.dag_structure.items():
            print(f"\n📋 {group_name.title()} Layer:")
            print(f"   Dependencies: {group_config['dependencies'] or 'None'}")
            print(f"   Tasks: {', '.join(group_config['tasks'])}")
            print(f"   Estimated time: {group_config['estimated_hours']} hours")
        
        total_estimated = sum(g['estimated_hours'] for g in orchestrator.dag_structure.values())
        print(f"\n⏱️  Total estimated time: {total_estimated} hours (parallel execution)")
        return
    
    # Execute DAG
    results = orchestrator.execute_dag(
        max_workers=args.max_workers,
        continue_on_failure=args.continue_on_failure
    )
    
    # Generate and save report
    report = orchestrator.generate_execution_report(results)
    report_file = f"deployment_auditor_execution_report_{orchestrator.execution_id}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Execution report saved: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)

if __name__ == "__main__":
    main()