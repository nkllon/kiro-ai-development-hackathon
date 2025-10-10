#!/usr/bin/env python3
"""
Constellation Execution Monitor
Real-time monitoring and progress tracking for constellation elaboration
"""

import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability


class ConstellationMonitor(ReflectiveModule):
    """Real-time monitor for constellation elaboration execution"""
    
    def __init__(self, update_interval: int = 5):
        super().__init__()
        self.update_interval = update_interval
        self.status_file = Path(".kiro/execution-status.json")
        self.logs_dir = Path(".kiro/execution-logs")
        self.monitoring_active = False
        
        self.logger = logging.getLogger("ConstellationMonitor")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "constellation_monitor",
            "name": "Constellation Execution Monitor",
            "version": "1.0.0",
            "description": "Real-time monitoring and progress tracking for constellation elaboration",
            "update_interval": self.update_interval
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.CORE_FUNCTIONALITY
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        return ModuleHealth(
            module_id="constellation_monitor",
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(timezone.utc),
            uptime_seconds=(datetime.now(timezone.utc) - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def load_execution_status(self) -> Optional[Dict]:
        """Load current execution status"""
        if not self.status_file.exists():
            return None
        
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load execution status: {e}")
            return None
    
    def calculate_progress_metrics(self, status: Dict) -> Dict[str, Any]:
        """Calculate progress metrics from status"""
        if not status or "prompts" not in status:
            return {}
        
        prompts = status["prompts"]
        total_tasks = len(prompts)
        
        # Count tasks by status
        completed = sum(1 for p in prompts.values() if p["status"] == "completed")
        failed = sum(1 for p in prompts.values() if p["status"] == "failed")
        running = sum(1 for p in prompts.values() if p["status"] == "running")
        pending = sum(1 for p in prompts.values() if p["status"] == "pending")
        
        # Calculate completion percentage
        completion_percent = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate estimated time remaining
        completed_tasks = [p for p in prompts.values() if p["status"] == "completed" and p.get("duration_min")]
        avg_duration = 0
        if completed_tasks:
            total_duration = sum(p["duration_min"] for p in completed_tasks)
            avg_duration = total_duration / len(completed_tasks)
        
        remaining_tasks = pending + running
        estimated_remaining_minutes = remaining_tasks * avg_duration if avg_duration > 0 else 0
        
        # Calculate total elapsed time
        started_at = status.get("started_at")
        elapsed_minutes = 0
        if started_at:
            try:
                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                elapsed_minutes = (datetime.now(timezone.utc) - start_time).total_seconds() / 60
            except Exception:
                pass
        
        # Calculate success rate
        finished_tasks = completed + failed
        success_rate = (completed / finished_tasks * 100) if finished_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "completion_percent": completion_percent,
            "success_rate": success_rate,
            "avg_task_duration_minutes": avg_duration,
            "estimated_remaining_minutes": estimated_remaining_minutes,
            "elapsed_minutes": elapsed_minutes
        }
    
    def analyze_phase_progress(self, status: Dict) -> Dict[str, Dict]:
        """Analyze progress by execution phase"""
        if not status or "prompts" not in status:
            return {}
        
        phases = {
            "Phase 1: Discovery": {"total": 0, "completed": 0, "failed": 0, "running": 0, "pending": 0},
            "Phase 2: Requirements": {"total": 0, "completed": 0, "failed": 0, "running": 0, "pending": 0},
            "Phase 3: Design": {"total": 0, "completed": 0, "failed": 0, "running": 0, "pending": 0},
            "Phase 4: Tasks": {"total": 0, "completed": 0, "failed": 0, "running": 0, "pending": 0},
            "Phase 5: Consolidation": {"total": 0, "completed": 0, "failed": 0, "running": 0, "pending": 0}
        }
        
        for task_name, task_data in status["prompts"].items():
            if task_name.startswith("phase-1"):
                phase = "Phase 1: Discovery"
            elif task_name.startswith("phase-2"):
                phase = "Phase 2: Requirements"
            elif task_name.startswith("phase-3"):
                phase = "Phase 3: Design"
            elif task_name.startswith("phase-4"):
                phase = "Phase 4: Tasks"
            elif task_name.startswith("phase-5"):
                phase = "Phase 5: Consolidation"
            else:
                continue
            
            phases[phase]["total"] += 1
            task_status = task_data["status"]
            if task_status in phases[phase]:
                phases[phase][task_status] += 1
        
        # Calculate completion percentages
        for phase_name, phase_data in phases.items():
            total = phase_data["total"]
            completed = phase_data["completed"]
            phase_data["completion_percent"] = (completed / total * 100) if total > 0 else 0
        
        return phases
    
    def get_active_tasks(self, status: Dict) -> List[Dict]:
        """Get currently running tasks with details"""
        if not status or "prompts" not in status:
            return []
        
        active_tasks = []
        for task_name, task_data in status["prompts"].items():
            if task_data["status"] == "running":
                started_at = task_data.get("started_at")
                duration_so_far = 0
                
                if started_at:
                    try:
                        start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                        duration_so_far = (datetime.now(timezone.utc) - start_time).total_seconds() / 60
                    except Exception:
                        pass
                
                active_tasks.append({
                    "task_name": task_name,
                    "agent_id": task_data.get("agent_id", "unknown"),
                    "started_at": started_at,
                    "duration_minutes": duration_so_far,
                    "estimated_minutes": task_data.get("estimated_minutes", 0)
                })
        
        return sorted(active_tasks, key=lambda x: x["duration_minutes"], reverse=True)
    
    def get_recent_completions(self, status: Dict, limit: int = 5) -> List[Dict]:
        """Get recently completed tasks"""
        if not status or "prompts" not in status:
            return []
        
        completed_tasks = []
        for task_name, task_data in status["prompts"].items():
            if task_data["status"] in ["completed", "failed"]:
                completed_at = task_data.get("completed_at")
                if completed_at:
                    completed_tasks.append({
                        "task_name": task_name,
                        "status": task_data["status"],
                        "completed_at": completed_at,
                        "duration_minutes": task_data.get("duration_min", 0),
                        "error": task_data.get("error")
                    })
        
        # Sort by completion time (most recent first)
        completed_tasks.sort(key=lambda x: x["completed_at"], reverse=True)
        return completed_tasks[:limit]
    
    def print_status_dashboard(self, status: Dict):
        """Print comprehensive status dashboard"""
        if not status:
            print("❌ No execution status available")
            return
        
        # Clear screen (works on most terminals)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header
        print("🌟 CONSTELLATION ELABORATION MONITOR")
        print("=" * 80)
        print(f"📊 Execution ID: {status.get('execution_id', 'Unknown')}")
        print(f"🕐 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Max Agents: {status.get('max_agents', 'Unknown')}")
        print()
        
        # Progress metrics
        metrics = self.calculate_progress_metrics(status)
        if metrics:
            print("📈 OVERALL PROGRESS")
            print("-" * 40)
            print(f"✅ Completed: {metrics['completed']}/{metrics['total_tasks']} ({metrics['completion_percent']:.1f}%)")
            print(f"❌ Failed: {metrics['failed']}")
            print(f"🔄 Running: {metrics['running']}")
            print(f"⏳ Pending: {metrics['pending']}")
            print(f"📊 Success Rate: {metrics['success_rate']:.1f}%")
            
            if metrics['elapsed_minutes'] > 0:
                print(f"⏱️  Elapsed: {metrics['elapsed_minutes']:.1f} minutes ({metrics['elapsed_minutes']/60:.1f} hours)")
            
            if metrics['estimated_remaining_minutes'] > 0:
                print(f"⏰ Est. Remaining: {metrics['estimated_remaining_minutes']:.1f} minutes ({metrics['estimated_remaining_minutes']/60:.1f} hours)")
            
            # Progress bar
            progress_width = 50
            filled_width = int(progress_width * metrics['completion_percent'] / 100)
            progress_bar = "█" * filled_width + "░" * (progress_width - filled_width)
            print(f"📊 Progress: [{progress_bar}] {metrics['completion_percent']:.1f}%")
            print()
        
        # Phase analysis
        phases = self.analyze_phase_progress(status)
        if phases:
            print("🎭 PHASE PROGRESS")
            print("-" * 40)
            for phase_name, phase_data in phases.items():
                if phase_data["total"] > 0:
                    completion = phase_data["completion_percent"]
                    status_icon = "✅" if completion == 100 else "🔄" if phase_data["running"] > 0 else "⏳"
                    print(f"{status_icon} {phase_name}: {phase_data['completed']}/{phase_data['total']} ({completion:.0f}%)")
            print()
        
        # Active tasks
        active_tasks = self.get_active_tasks(status)
        if active_tasks:
            print("🔄 ACTIVE TASKS")
            print("-" * 40)
            for task in active_tasks[:5]:  # Show top 5
                duration = task["duration_minutes"]
                estimated = task.get("estimated_minutes", 0)
                progress_indicator = ""
                if estimated > 0:
                    task_progress = min(100, (duration / estimated) * 100)
                    progress_indicator = f" ({task_progress:.0f}%)"
                
                print(f"🤖 {task['agent_id']}: {task['task_name']}")
                print(f"   ⏱️  Running for {duration:.1f}min{progress_indicator}")
            
            if len(active_tasks) > 5:
                print(f"   ... and {len(active_tasks) - 5} more")
            print()
        
        # Recent completions
        recent = self.get_recent_completions(status)
        if recent:
            print("📋 RECENT COMPLETIONS")
            print("-" * 40)
            for task in recent:
                status_icon = "✅" if task["status"] == "completed" else "❌"
                duration = task["duration_minutes"]
                print(f"{status_icon} {task['task_name']} ({duration:.1f}min)")
                if task["status"] == "failed" and task.get("error"):
                    error_preview = task["error"][:60] + "..." if len(task["error"]) > 60 else task["error"]
                    print(f"   💥 Error: {error_preview}")
            print()
        
        # System status
        execution_status = status.get("status", "unknown")
        status_icon = {
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "interrupted": "⏸️"
        }.get(execution_status, "❓")
        
        print("🖥️  SYSTEM STATUS")
        print("-" * 40)
        print(f"{status_icon} Execution Status: {execution_status.upper()}")
        
        if execution_status == "running":
            print("🔄 Monitoring active - Press Ctrl+C to stop monitoring")
        elif execution_status == "completed":
            print("🎉 Execution completed successfully!")
        elif execution_status == "failed":
            print("💥 Execution failed - check logs for details")
        elif execution_status == "interrupted":
            print("⏸️  Execution was interrupted - can be resumed")
    
    async def monitor_execution(self, continuous: bool = True):
        """Monitor execution with real-time updates"""
        print("🚀 Starting Constellation Execution Monitor")
        print(f"📊 Update interval: {self.update_interval} seconds")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        self.monitoring_active = True
        
        try:
            while self.monitoring_active:
                status = self.load_execution_status()
                
                if status:
                    self.print_status_dashboard(status)
                    
                    # Check if execution is complete
                    execution_status = status.get("status", "unknown")
                    if execution_status in ["completed", "failed"] and not continuous:
                        print(f"\n🏁 Execution {execution_status}. Monitoring stopped.")
                        break
                else:
                    print("⏳ Waiting for execution to start...")
                    print("   (No status file found)")
                
                if continuous:
                    await asyncio.sleep(self.update_interval)
                else:
                    break
        
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.monitoring_active = False
        
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
            self.monitoring_active = False
    
    def setup_monitoring(self):
        """Setup monitoring infrastructure"""
        print("🔧 Setting up monitoring infrastructure...")
        
        # Create monitoring directories
        monitoring_dirs = [
            Path(".kiro/monitoring"),
            Path("logs/constellation-monitoring")
        ]
        
        for directory in monitoring_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  📁 Created: {directory}")
        
        # Create monitoring configuration
        config = {
            "monitoring": {
                "update_interval_seconds": self.update_interval,
                "dashboard_enabled": True,
                "log_level": "INFO",
                "metrics_collection": True
            },
            "alerts": {
                "task_timeout_minutes": 120,
                "high_failure_rate_percent": 20,
                "low_progress_rate_tasks_per_hour": 2
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        config_file = Path(".kiro/monitoring-config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"  📄 Created: {config_file}")
        print("✅ Monitoring setup complete")
    
    def validate_monitoring(self):
        """Validate monitoring system"""
        print("🔍 Validating monitoring system...")
        
        issues = []
        
        # Check status file accessibility
        if not self.status_file.parent.exists():
            issues.append(f"Status directory missing: {self.status_file.parent}")
        
        # Check logs directory
        if not self.logs_dir.exists():
            issues.append(f"Logs directory missing: {self.logs_dir}")
        
        # Test status file read/write
        try:
            test_status = {
                "test": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            test_file = self.status_file.parent / "monitor-test.json"
            with open(test_file, 'w') as f:
                json.dump(test_status, f)
            
            with open(test_file, 'r') as f:
                loaded_status = json.load(f)
            
            if loaded_status.get("test") != True:
                issues.append("Status file read/write test failed")
            
            # Cleanup test file
            test_file.unlink()
            
        except Exception as e:
            issues.append(f"Status file access error: {e}")
        
        if issues:
            print("❌ Monitoring validation failed:")
            for issue in issues:
                print(f"  • {issue}")
            return False
        else:
            print("✅ Monitoring validation passed")
            return True


async def main():
    parser = argparse.ArgumentParser(description="Constellation Execution Monitor")
    parser.add_argument("--setup", action="store_true", 
                       help="Setup monitoring infrastructure")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate monitoring system")
    parser.add_argument("--once", action="store_true", 
                       help="Show status once and exit")
    parser.add_argument("--interval", type=int, default=5,
                       help="Update interval in seconds (default: 5)")
    
    args = parser.parse_args()
    
    monitor = ConstellationMonitor(update_interval=args.interval)
    
    if args.setup:
        monitor.setup_monitoring()
    elif args.validate:
        valid = monitor.validate_monitoring()
        sys.exit(0 if valid else 1)
    else:
        await monitor.monitor_execution(continuous=not args.once)


if __name__ == "__main__":
    asyncio.run(main())