#!/usr/bin/env python3
"""
Deployment Data Auditor Execution Monitor

Real-time monitoring and progress tracking for DAG execution with Redis integration
and comprehensive status reporting.
"""

import os
import sys
import json
import time
import redis
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Add src to path for Beast Mode integration
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Simplified Beast Mode integration for now
BEAST_MODE_AVAILABLE = False
class ReflectiveModule:
    def __init__(self):
        pass

@dataclass
class TaskStatus:
    """Status information for a single task."""
    task_id: str
    name: str
    status: str  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    parallel_group: str = ""
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ExecutionProgress:
    """Overall execution progress information."""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    pending_tasks: int
    current_parallel_group: str
    estimated_completion: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None

class DeploymentAuditorExecutionMonitor(ReflectiveModule if BEAST_MODE_AVAILABLE else object):
    """Monitor and track DAG execution progress with Redis integration."""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        # Simplified initialization without Beast Mode complexity
        self.redis_client = None
        self.task_statuses: Dict[str, TaskStatus] = {}
        self.parallel_groups = {
            "foundation": ["1.1", "1.2", "1.3", "6.1", "6.2", "6.3", "9.1", "9.2", "9.3"],
            "core": ["2.1", "2.2", "2.3", "3.1", "3.2", "3.3"],
            "integration": ["4.1", "4.2", "4.3", "4.4", "4.5", "5.1", "5.2", "5.3", "5.4"],
            "optimization": ["7.1", "7.2", "7.3", "8.1", "8.2", "8.3"],
            "validation": ["10.1", "10.2", "10.3", "10.4"]
        }
        
        # Initialize Redis connection
        try:
            import redis
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
            print("   Continuing without Redis integration")
        
        self._initialize_task_statuses()
    
    # Beast Mode ReflectiveModule implementation
    def get_capabilities(self) -> Dict[str, Any]:
        """Get monitor capabilities."""
        return {
            "name": "DeploymentAuditorExecutionMonitor",
            "version": "1.0.0",
            "capabilities": ["task_monitoring", "progress_tracking", "redis_integration", "real_time_dashboard"]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get monitor health status."""
        return {
            "status": "healthy",
            "redis_connected": self.redis_client is not None,
            "tasks_tracked": len(self.task_statuses),
            "beast_mode_available": BEAST_MODE_AVAILABLE
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "deployment_auditor_execution_monitor",
            "module_type": "monitoring_system",
            "beast_mode_integration": BEAST_MODE_AVAILABLE,
            "redis_integration": self.redis_client is not None
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "local_monitoring_only",
            "redis_disabled": True
        }
        
        self.redis_client = None
        self.task_statuses: Dict[str, TaskStatus] = {}
        self.parallel_groups = {
            "foundation": ["1.1", "1.2", "1.3", "6.1", "6.2", "6.3", "9.1", "9.2", "9.3"],
            "core": ["2.1", "2.2", "2.3", "3.1", "3.2", "3.3"],
            "integration": ["4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "5.4"],
            "optimization": ["7.1", "7.2", "7.3", "8.1", "8.2", "8.3"],
            "validation": ["10.1", "10.2", "10.3", "10.4"]
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
            print("   Continuing without Redis integration")
        
        self._initialize_task_statuses()
        
    def _initialize_task_statuses(self):
        """Initialize task status tracking."""
        task_definitions = {
            # Foundation Layer
            "1.1": ("Create core data models", "foundation"),
            "1.2": ("Implement ReflectiveModule integration", "foundation"),
            "1.3": ("Write unit tests for base classes", "foundation"),
            "6.1": ("Build configuration system", "foundation"),
            "6.2": ("Implement hot-reloading", "foundation"),
            "6.3": ("Write configuration tests", "foundation"),
            "9.1": ("Implement CLI interface", "foundation"),
            "9.2": ("Build daemon lifecycle", "foundation"),
            "9.3": ("Write CLI tests", "foundation"),
            
            # Core Layer
            "2.1": ("Implement file system watching", "core"),
            "2.2": ("Create baseline scanning", "core"),
            "2.3": ("Write file monitoring tests", "core"),
            "3.1": ("Implement pattern matching", "core"),
            "3.2": ("Create violation classifier", "core"),
            "3.3": ("Write pattern matching tests", "core"),
            
            # Integration Layer
            "4.1": ("Implement gitignore management", "integration"),
            "4.2": ("Create file quarantine", "integration"),
            "4.3": ("Build git integration", "integration"),
            "4.4": ("Write remediation tests", "integration"),
            "5.1": ("Create reporting engine", "integration"),
            "5.2": ("Build notification system", "integration"),
            "5.3": ("Implement Prometheus metrics", "integration"),
            "5.4": ("Write reporting tests", "integration"),
            
            # Optimization Layer
            "7.1": ("Create resource monitoring", "optimization"),
            "7.2": ("Build event processing", "optimization"),
            "7.3": ("Write performance tests", "optimization"),
            "8.1": ("Create emergency detection", "optimization"),
            "8.2": ("Build recovery systems", "optimization"),
            "8.3": ("Write emergency tests", "optimization"),
            
            # Validation Layer
            "10.1": ("Create end-to-end tests", "validation"),
            "10.2": ("Build deployment tools", "validation"),
            "10.3": ("Create documentation", "validation"),
            "10.4": ("Write integration tests", "validation"),
        }
        
        for task_id, (name, group) in task_definitions.items():
            self.task_statuses[task_id] = TaskStatus(
                task_id=task_id,
                name=name,
                status="pending",
                parallel_group=group
            )
    
    def update_task_status(self, task_id: str, status: str, error_message: Optional[str] = None):
        """Update the status of a specific task."""
        if task_id not in self.task_statuses:
            print(f"⚠️  Unknown task ID: {task_id}")
            return
            
        task = self.task_statuses[task_id]
        old_status = task.status
        task.status = status
        
        now = datetime.now()
        
        if status == "running" and old_status == "pending":
            task.started_at = now
            print(f"🚀 Task {task_id} started: {task.name}")
            
        elif status == "completed" and old_status == "running":
            task.completed_at = now
            if task.started_at:
                task.duration = (now - task.started_at).total_seconds()
            print(f"✅ Task {task_id} completed: {task.name} ({task.duration:.1f}s)")
            
            # Metrics would be recorded here in full Beast Mode integration
                    
        elif status == "failed":
            task.completed_at = now
            task.error_message = error_message
            if task.started_at:
                task.duration = (now - task.started_at).total_seconds()
            print(f"❌ Task {task_id} failed: {task.name}")
            if error_message:
                print(f"   Error: {error_message}")
                
            # Metrics would be recorded here in full Beast Mode integration
        
        # Update Redis if available
        if self.redis_client:
            try:
                self.redis_client.hset(
                    f"deployment_auditor:task:{task_id}",
                    mapping={
                        "status": status,
                        "updated_at": now.isoformat(),
                        "duration": task.duration or 0,
                        "error": error_message or ""
                    }
                )
            except Exception as e:
                print(f"⚠️  Redis update failed: {e}")
    
    def scan_task_completion(self):
        """Scan for completed tasks by checking completion marker files."""
        for task_id in self.task_statuses:
            completion_file = Path(f".task-{task_id}-complete")
            task = self.task_statuses[task_id]
            
            if completion_file.exists() and task.status != "completed":
                # Check if there's a log file with execution details
                log_file = Path(f"logs/task_{task_id.replace('.', '_')}.log")
                error_message = None
                
                if log_file.exists():
                    try:
                        log_content = log_file.read_text()
                        if "ERROR" in log_content or "FAILED" in log_content:
                            # Extract error message
                            lines = log_content.split('\n')
                            error_lines = [line for line in lines if "ERROR" in line or "FAILED" in line]
                            if error_lines:
                                error_message = error_lines[-1]  # Get last error
                    except Exception:
                        pass
                
                if error_message:
                    self.update_task_status(task_id, "failed", error_message)
                else:
                    self.update_task_status(task_id, "completed")
    
    def get_execution_progress(self) -> ExecutionProgress:
        """Get current execution progress."""
        total_tasks = len(self.task_statuses)
        completed_tasks = sum(1 for t in self.task_statuses.values() if t.status == "completed")
        failed_tasks = sum(1 for t in self.task_statuses.values() if t.status == "failed")
        running_tasks = sum(1 for t in self.task_statuses.values() if t.status == "running")
        pending_tasks = total_tasks - completed_tasks - failed_tasks - running_tasks
        
        # Determine current parallel group
        current_group = "unknown"
        for group_name, task_ids in self.parallel_groups.items():
            group_tasks = [self.task_statuses[tid] for tid in task_ids if tid in self.task_statuses]
            if any(t.status == "running" for t in group_tasks):
                current_group = group_name
                break
            elif all(t.status in ["completed", "failed"] for t in group_tasks):
                continue
            else:
                current_group = group_name
                break
        
        return ExecutionProgress(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            running_tasks=running_tasks,
            pending_tasks=pending_tasks,
            current_parallel_group=current_group
        )
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        progress = self.get_execution_progress()
        
        # Group tasks by parallel group
        groups_status = {}
        for group_name, task_ids in self.parallel_groups.items():
            group_tasks = [self.task_statuses[tid] for tid in task_ids if tid in self.task_statuses]
            groups_status[group_name] = {
                "total": len(group_tasks),
                "completed": sum(1 for t in group_tasks if t.status == "completed"),
                "failed": sum(1 for t in group_tasks if t.status == "failed"),
                "running": sum(1 for t in group_tasks if t.status == "running"),
                "pending": sum(1 for t in group_tasks if t.status == "pending"),
                "tasks": [
                    {
                        "id": t.task_id,
                        "name": t.name,
                        "status": t.status,
                        "duration": t.duration,
                        "error": t.error_message
                    }
                    for t in group_tasks
                ]
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_progress": {
                "total_tasks": progress.total_tasks,
                "completed": progress.completed_tasks,
                "failed": progress.failed_tasks,
                "running": progress.running_tasks,
                "pending": progress.pending_tasks,
                "completion_percentage": (progress.completed_tasks / progress.total_tasks) * 100,
                "current_group": progress.current_parallel_group
            },
            "parallel_groups": groups_status,
            "failed_tasks": [
                {
                    "id": t.task_id,
                    "name": t.name,
                    "error": t.error_message,
                    "duration": t.duration
                }
                for t in self.task_statuses.values() if t.status == "failed"
            ]
        }
    
    def print_status_dashboard(self):
        """Print a real-time status dashboard."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔍 Deployment Data Auditor - DAG Execution Monitor")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        progress = self.get_execution_progress()
        completion_pct = (progress.completed_tasks / progress.total_tasks) * 100
        
        print(f"📊 Overall Progress: {progress.completed_tasks}/{progress.total_tasks} ({completion_pct:.1f}%)")
        print(f"🏃 Running: {progress.running_tasks} | ⏳ Pending: {progress.pending_tasks} | ❌ Failed: {progress.failed_tasks}")
        print(f"🎯 Current Group: {progress.current_parallel_group}")
        print()
        
        # Progress bar
        bar_width = 40
        filled = int(bar_width * completion_pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"[{bar}] {completion_pct:.1f}%")
        print()
        
        # Group status
        for group_name, task_ids in self.parallel_groups.items():
            group_tasks = [self.task_statuses[tid] for tid in task_ids if tid in self.task_statuses]
            completed = sum(1 for t in group_tasks if t.status == "completed")
            failed = sum(1 for t in group_tasks if t.status == "failed")
            running = sum(1 for t in group_tasks if t.status == "running")
            
            status_icon = "✅" if completed == len(group_tasks) else "🏃" if running > 0 else "⏳"
            print(f"{status_icon} {group_name.title()}: {completed}/{len(group_tasks)} completed")
            
            if failed > 0:
                print(f"   ❌ {failed} failed tasks")
        
        print()
        
        # Recent activity
        recent_tasks = sorted(
            [t for t in self.task_statuses.values() if t.completed_at],
            key=lambda x: x.completed_at or datetime.min,
            reverse=True
        )[:5]
        
        if recent_tasks:
            print("📋 Recent Activity:")
            for task in recent_tasks:
                status_icon = "✅" if task.status == "completed" else "❌"
                duration_str = f"({task.duration:.1f}s)" if task.duration else ""
                print(f"   {status_icon} {task.task_id}: {task.name} {duration_str}")
        
        print()
        print("Press Ctrl+C to stop monitoring")
    
    def monitor_execution(self, refresh_interval: int = 5):
        """Start real-time monitoring of DAG execution."""
        print("🚀 Starting DAG execution monitoring...")
        print(f"   Refresh interval: {refresh_interval} seconds")
        print(f"   Redis integration: {'✅ Enabled' if self.redis_client else '❌ Disabled'}")
        print()
        
        try:
            while True:
                self.scan_task_completion()
                self.print_status_dashboard()
                
                # Check if execution is complete
                progress = self.get_execution_progress()
                if progress.completed_tasks + progress.failed_tasks == progress.total_tasks:
                    print("\n🎉 DAG execution completed!")
                    if progress.failed_tasks > 0:
                        print(f"⚠️  {progress.failed_tasks} tasks failed - review logs for details")
                    break
                
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
            
        # Generate final report
        report = self.generate_status_report()
        report_file = f"deployment_auditor_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Final report saved: {report_file}")

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Auditor Execution Monitor')
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--refresh-interval', type=int, default=5, help='Refresh interval in seconds')
    parser.add_argument('--status-only', action='store_true', help='Show status once and exit')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = DeploymentAuditorExecutionMonitor(
        redis_host=args.redis_host,
        redis_port=args.redis_port
    )
    
    if args.status_only:
        monitor.scan_task_completion()
        report = monitor.generate_status_report()
        print(json.dumps(report, indent=2))
    else:
        monitor.monitor_execution(refresh_interval=args.refresh_interval)

if __name__ == "__main__":
    main()