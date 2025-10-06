#!/usr/bin/env python3
"""
System Architecture DAG Monitoring Script
========================================

Monitors the progress of the DAG orchestrated parallel execution
of the System Architecture Wiring Diagram implementation.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class SystemArchitectureDAGMonitor:
    """Monitors DAG execution progress for System Architecture implementation."""
    
    def __init__(self):
        self.log_base_dir = Path("logs/system-architecture-dag")
        self.spec_path = Path(".kiro/specs/system-architecture-wiring-diagram")
        
    def get_latest_execution(self) -> str:
        """Get the latest execution timestamp."""
        if not self.log_base_dir.exists():
            return None
            
        execution_dirs = [d for d in self.log_base_dir.iterdir() if d.is_dir()]
        if not execution_dirs:
            return None
            
        # Sort by timestamp (directory name)
        latest_dir = sorted(execution_dirs, key=lambda x: x.name)[-1]
        return latest_dir.name
    
    def check_task_status(self, execution_id: str) -> Dict[str, Any]:
        """Check the status of all tasks in the execution."""
        execution_dir = self.log_base_dir / execution_id
        
        if not execution_dir.exists():
            return {"error": f"Execution directory not found: {execution_dir}"}
        
        # Define expected tasks
        expected_tasks = [
            "1.1_project_structure_setup",
            "1.2_observatory_websocket_integration", 
            "1.3_service_discovery_scanner",
            "1.4_cloudflare_tunnel_discovery",
            "1.5_makefile_analysis_system",
            "1.6_network_topology_discovery"
        ]
        
        task_status = {}
        
        for task_id in expected_tasks:
            log_file = execution_dir / f"{task_id}-{execution_id}.log"
            
            if log_file.exists():
                # Check log file size and modification time
                stat = log_file.stat()
                task_status[task_id] = {
                    "log_exists": True,
                    "log_size_bytes": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "status": "in_progress" if stat.st_size > 0 else "launched"
                }
                
                # Try to read last few lines to check for completion
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            last_lines = ''.join(lines[-5:]).lower()
                            if any(keyword in last_lines for keyword in ['completed', 'finished', 'done', 'success']):
                                task_status[task_id]["status"] = "completed"
                            elif any(keyword in last_lines for keyword in ['error', 'failed', 'exception']):
                                task_status[task_id]["status"] = "failed"
                except Exception as e:
                    task_status[task_id]["read_error"] = str(e)
            else:
                task_status[task_id] = {
                    "log_exists": False,
                    "status": "not_started"
                }
        
        return task_status
    
    def check_spec_task_completion(self) -> Dict[str, Any]:
        """Check task completion status in the spec tasks.md file."""
        tasks_file = self.spec_path / "tasks.md"
        
        if not tasks_file.exists():
            return {"error": f"Tasks file not found: {tasks_file}"}
        
        try:
            with open(tasks_file, 'r') as f:
                content = f.read()
            
            # Count completed tasks (marked with [x])
            completed_phase1 = content.count("- [x] 1.")
            total_phase1 = content.count("- [ ] 1.") + completed_phase1
            
            completed_phase2 = content.count("- [x] 2.")
            total_phase2 = content.count("- [ ] 2.") + completed_phase2
            
            return {
                "phase1": {
                    "completed": completed_phase1,
                    "total": total_phase1,
                    "completion_rate": completed_phase1 / total_phase1 if total_phase1 > 0 else 0
                },
                "phase2": {
                    "completed": completed_phase2,
                    "total": total_phase2,
                    "completion_rate": completed_phase2 / total_phase2 if total_phase2 > 0 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to read tasks file: {e}"}
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        latest_execution = self.get_latest_execution()
        
        if not latest_execution:
            return {
                "status": "no_execution_found",
                "message": "No DAG execution found. Run system_architecture_dag_orchestration_plan.py to start."
            }
        
        # Get task status from logs
        task_status = self.check_task_status(latest_execution)
        
        # Get spec completion status
        spec_status = self.check_spec_task_completion()
        
        # Calculate overall progress
        if isinstance(task_status, dict) and "error" not in task_status:
            total_tasks = len(task_status)
            completed_tasks = sum(1 for status in task_status.values() if status.get("status") == "completed")
            in_progress_tasks = sum(1 for status in task_status.values() if status.get("status") == "in_progress")
            failed_tasks = sum(1 for status in task_status.values() if status.get("status") == "failed")
            
            overall_progress = completed_tasks / total_tasks if total_tasks > 0 else 0
        else:
            total_tasks = completed_tasks = in_progress_tasks = failed_tasks = 0
            overall_progress = 0
        
        return {
            "execution_id": latest_execution,
            "timestamp": datetime.now().isoformat(),
            "overall_progress": overall_progress,
            "task_summary": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "failed": failed_tasks,
                "not_started": total_tasks - completed_tasks - in_progress_tasks - failed_tasks
            },
            "task_details": task_status,
            "spec_status": spec_status,
            "log_directory": str(self.log_base_dir / latest_execution),
            "next_actions": self._get_next_actions(task_status, spec_status)
        }
    
    def _get_next_actions(self, task_status: Dict, spec_status: Dict) -> List[str]:
        """Determine next actions based on current status."""
        actions = []
        
        if isinstance(task_status, dict) and "error" not in task_status:
            completed_tasks = [task for task, status in task_status.items() if status.get("status") == "completed"]
            failed_tasks = [task for task, status in task_status.items() if status.get("status") == "failed"]
            in_progress_tasks = [task for task, status in task_status.items() if status.get("status") == "in_progress"]
            
            if failed_tasks:
                actions.append(f"Investigate and retry failed tasks: {', '.join(failed_tasks)}")
            
            if in_progress_tasks:
                actions.append(f"Monitor in-progress tasks: {', '.join(in_progress_tasks)}")
            
            if len(completed_tasks) == len(task_status):
                actions.append("Phase 1 complete! Ready to launch Phase 2: Relationship Analysis Engine")
            elif len(completed_tasks) >= len(task_status) * 0.8:
                actions.append("Phase 1 nearly complete. Prepare for Phase 2 launch.")
        
        # Check spec status
        if isinstance(spec_status, dict) and "error" not in spec_status:
            phase1_completion = spec_status.get("phase1", {}).get("completion_rate", 0)
            if phase1_completion >= 1.0:
                actions.append("Update spec tasks.md to mark remaining Phase 1 tasks as complete")
        
        if not actions:
            actions.append("Continue monitoring DAG execution progress")
        
        return actions
    
    def print_status_report(self):
        """Print formatted status report."""
        report = self.generate_status_report()
        
        print("🐺 SYSTEM ARCHITECTURE DAG MONITORING REPORT 🐺")
        print("=" * 60)
        print(f"Execution ID: {report.get('execution_id', 'N/A')}")
        print(f"Timestamp: {report.get('timestamp', 'N/A')}")
        print(f"Overall Progress: {report.get('overall_progress', 0):.1%}")
        print()
        
        # Task Summary
        summary = report.get('task_summary', {})
        print("📊 TASK SUMMARY")
        print("-" * 30)
        print(f"Total Tasks: {summary.get('total', 0)}")
        print(f"✅ Completed: {summary.get('completed', 0)}")
        print(f"🔄 In Progress: {summary.get('in_progress', 0)}")
        print(f"❌ Failed: {summary.get('failed', 0)}")
        print(f"⏳ Not Started: {summary.get('not_started', 0)}")
        print()
        
        # Task Details
        task_details = report.get('task_details', {})
        if isinstance(task_details, dict) and "error" not in task_details:
            print("📋 TASK DETAILS")
            print("-" * 30)
            for task_id, status in task_details.items():
                status_emoji = {
                    "completed": "✅",
                    "in_progress": "🔄", 
                    "failed": "❌",
                    "launched": "🚀",
                    "not_started": "⏳"
                }.get(status.get("status", "unknown"), "❓")
                
                print(f"{status_emoji} {task_id}: {status.get('status', 'unknown')}")
                if status.get('log_size_bytes', 0) > 0:
                    print(f"    Log size: {status.get('log_size_bytes', 0)} bytes")
                    print(f"    Last modified: {status.get('last_modified', 'N/A')}")
            print()
        
        # Spec Status
        spec_status = report.get('spec_status', {})
        if isinstance(spec_status, dict) and "error" not in spec_status:
            print("📄 SPEC COMPLETION STATUS")
            print("-" * 30)
            phase1 = spec_status.get('phase1', {})
            phase2 = spec_status.get('phase2', {})
            print(f"Phase 1: {phase1.get('completed', 0)}/{phase1.get('total', 0)} ({phase1.get('completion_rate', 0):.1%})")
            print(f"Phase 2: {phase2.get('completed', 0)}/{phase2.get('total', 0)} ({phase2.get('completion_rate', 0):.1%})")
            print()
        
        # Next Actions
        next_actions = report.get('next_actions', [])
        if next_actions:
            print("🎯 NEXT ACTIONS")
            print("-" * 30)
            for i, action in enumerate(next_actions, 1):
                print(f"{i}. {action}")
            print()
        
        # Log Directory
        log_dir = report.get('log_directory')
        if log_dir:
            print(f"📁 Log Directory: {log_dir}")
            print("💡 Use 'tail -f <log_file>' to monitor individual task progress")
        
        print("=" * 60)
    
    def save_status_report(self, output_file: str = None):
        """Save status report to JSON file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = f"system_architecture_dag_status_{timestamp}.json"
        
        report = self.generate_status_report()
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Status report saved to: {output_file}")
        except Exception as e:
            print(f"❌ Failed to save status report: {e}")


def main():
    """Main monitoring function."""
    monitor = SystemArchitectureDAGMonitor()
    
    # Print status report
    monitor.print_status_report()
    
    # Save status report
    monitor.save_status_report()


if __name__ == "__main__":
    main()