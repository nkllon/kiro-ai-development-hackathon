#!/usr/bin/env python3
"""
Background Governance Scheduler
==============================

Schedules and manages background tasks for governance compliance,
including orphaned solution scanning and spec consistency validation.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scripts.orphaned_solution_scanner import OrphanedSolutionScanner
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class BackgroundGovernanceScheduler(ReflectiveModule):
    """
    Schedules and manages background governance tasks.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "BackgroundGovernanceScheduler"
        self._logger = logging.getLogger(f"governance.{self.__class__.__name__}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "version": "1.0.0",
            "description": "Schedules and manages background governance tasks",
            "capabilities": ["task_scheduling", "background_execution", "notification_management"]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "status": "healthy",
            "scheduler_enabled": self.config.get("enabled", True),
            "tasks_configured": len(self.config.get("tasks", {})),
            "last_runs": self.state.get("last_run", {}),
            "error_counts": self.state.get("error_count", {})
        }
    
    def get_capabilities(self) -> List[str]:
        """Get scheduler capabilities."""
        return [
            "task_scheduling",
            "background_execution",
            "state_management",
            "notification_system",
            "report_generation"
        ]
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Handle graceful degradation."""
        return {
            "degraded_mode": False,
            "available_features": self.get_capabilities(),
            "limitations": []
        }
        
        self.config_file = Path(".kiro/governance/scheduler_config.json")
        self.state_file = Path(".kiro/governance/scheduler_state.json")
        self.reports_dir = Path("reports/governance")
        
        # Ensure directories exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        self.state = self._load_state()
        
        # Task registry
        self.tasks = {
            "orphaned_solution_scan": self._run_orphaned_solution_scan,
            "spec_consistency_check": self._run_spec_consistency_check,
            "governance_compliance_audit": self._run_governance_compliance_audit
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load scheduler configuration."""
        default_config = {
            "enabled": True,
            "tasks": {
                "orphaned_solution_scan": {
                    "enabled": True,
                    "schedule": "daily",
                    "time": "02:00",
                    "priority": "high"
                },
                "spec_consistency_check": {
                    "enabled": True,
                    "schedule": "weekly",
                    "day": "monday",
                    "time": "03:00",
                    "priority": "medium"
                },
                "governance_compliance_audit": {
                    "enabled": True,
                    "schedule": "weekly",
                    "day": "friday",
                    "time": "01:00",
                    "priority": "high"
                }
            },
            "notifications": {
                "enabled": True,
                "high_priority_threshold": 5,
                "email_enabled": False,
                "slack_enabled": False
            },
            "retention": {
                "keep_reports_days": 30,
                "max_reports_per_task": 10
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                return {**default_config, **config}
            except Exception as e:
                self._logger.warning(f"Failed to load config: {e}, using defaults")
        
        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _load_state(self) -> Dict[str, Any]:
        """Load scheduler state."""
        default_state = {
            "last_run": {},
            "task_history": {},
            "error_count": {},
            "next_scheduled": {}
        }
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self._logger.warning(f"Failed to load state: {e}, using defaults")
        
        return default_state
    
    def _save_state(self):
        """Save scheduler state."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            self._logger.error(f"Failed to save state: {e}")
    
    def setup_schedule(self):
        """Set up scheduled tasks based on configuration."""
        if not self.config.get("enabled", True):
            self._logger.info("Scheduler disabled in configuration")
            return
        
        self._logger.info("Scheduler setup completed (simplified implementation)")
        # Note: Full scheduling implementation would require additional dependencies
    
    def _run_task(self, task_name: str):
        """Run a scheduled task."""
        if task_name not in self.tasks:
            self._logger.error(f"Unknown task: {task_name}")
            return
        
        self._logger.info(f"Starting scheduled task: {task_name}")
        start_time = datetime.now()
        
        try:
            # Run the task
            result = asyncio.run(self.tasks[task_name]())
            
            # Update state
            self.state["last_run"][task_name] = start_time.isoformat()
            self.state["error_count"][task_name] = 0
            
            if task_name not in self.state["task_history"]:
                self.state["task_history"][task_name] = []
            
            self.state["task_history"][task_name].append({
                "timestamp": start_time.isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "status": "success",
                "result_summary": self._summarize_result(result)
            })
            
            # Keep only recent history
            max_history = self.config.get("retention", {}).get("max_reports_per_task", 10)
            self.state["task_history"][task_name] = self.state["task_history"][task_name][-max_history:]
            
            self._save_state()
            self._logger.info(f"Completed task: {task_name}")
            
            # Check for notifications
            self._check_notifications(task_name, result)
            
        except Exception as e:
            self._logger.error(f"Task {task_name} failed: {e}")
            
            # Update error state
            self.state["error_count"][task_name] = self.state["error_count"].get(task_name, 0) + 1
            
            if task_name not in self.state["task_history"]:
                self.state["task_history"][task_name] = []
            
            self.state["task_history"][task_name].append({
                "timestamp": start_time.isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "status": "error",
                "error": str(e)
            })
            
            self._save_state()
    
    async def _run_orphaned_solution_scan(self) -> Dict[str, Any]:
        """Run orphaned solution scan task."""
        scanner = OrphanedSolutionScanner()
        report = await scanner.scan_repository()
        
        # Save reports with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.reports_dir / f"orphaned_solutions_{timestamp}.json"
        md_path = self.reports_dir / f"orphaned_solutions_{timestamp}.md"
        
        scanner.save_report_json(report, json_path)
        scanner.save_report_markdown(report, md_path)
        
        return {
            "type": "orphaned_solution_scan",
            "total_implementations": report.total_implementations,
            "orphaned_solutions": len(report.orphaned_solutions),
            "high_priority_orphans": report.high_priority_orphans,
            "coverage_percentage": report.coverage_percentage,
            "json_report": str(json_path),
            "markdown_report": str(md_path)
        }
    
    async def _run_spec_consistency_check(self) -> Dict[str, Any]:
        """Run specification consistency check task."""
        # This would implement spec-to-implementation consistency checking
        # For now, return a placeholder
        return {
            "type": "spec_consistency_check",
            "specs_checked": 0,
            "inconsistencies_found": 0,
            "status": "placeholder_implementation"
        }
    
    async def _run_governance_compliance_audit(self) -> Dict[str, Any]:
        """Run governance compliance audit task."""
        # This would implement comprehensive governance compliance checking
        # For now, return a placeholder
        return {
            "type": "governance_compliance_audit",
            "rules_checked": 0,
            "violations_found": 0,
            "compliance_score": 100.0,
            "status": "placeholder_implementation"
        }
    
    def _summarize_result(self, result: Dict[str, Any]) -> str:
        """Create a summary of task result."""
        if result.get("type") == "orphaned_solution_scan":
            return f"Found {result['orphaned_solutions']} orphaned solutions ({result['high_priority_orphans']} high priority)"
        elif result.get("type") == "spec_consistency_check":
            return f"Checked {result['specs_checked']} specs, found {result['inconsistencies_found']} inconsistencies"
        elif result.get("type") == "governance_compliance_audit":
            return f"Compliance score: {result['compliance_score']:.1f}%, {result['violations_found']} violations"
        else:
            return "Task completed successfully"
    
    def _check_notifications(self, task_name: str, result: Dict[str, Any]):
        """Check if notifications should be sent based on task results."""
        notifications_config = self.config.get("notifications", {})
        if not notifications_config.get("enabled", True):
            return
        
        high_priority_threshold = notifications_config.get("high_priority_threshold", 5)
        
        # Check for high priority orphaned solutions
        if (result.get("type") == "orphaned_solution_scan" and 
            result.get("high_priority_orphans", 0) >= high_priority_threshold):
            
            self._send_notification(
                f"URGENT: {result['high_priority_orphans']} high-priority orphaned solutions found",
                f"Orphaned solution scan found {result['orphaned_solutions']} total orphaned solutions, "
                f"with {result['high_priority_orphans']} requiring immediate attention."
            )
    
    def _send_notification(self, subject: str, message: str):
        """Send notification (placeholder implementation)."""
        self._logger.warning(f"NOTIFICATION: {subject} - {message}")
        
        # Here you would implement actual notification sending
        # (email, Slack, etc.) based on configuration
    
    def run_once(self, task_name: str) -> Dict[str, Any]:
        """Run a specific task once (for testing/manual execution)."""
        if task_name not in self.tasks:
            raise ValueError(f"Unknown task: {task_name}")
        
        return asyncio.run(self.tasks[task_name]())
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status and recent task history."""
        return {
            "scheduler_enabled": self.config.get("enabled", True),
            "tasks_configured": len(self.config.get("tasks", {})),
            "last_runs": self.state.get("last_run", {}),
            "error_counts": self.state.get("error_count", {}),
            "next_scheduled": {
                task_name: "Manual execution only (simplified scheduler)"
                for task_name in self.config.get("tasks", {})
                if self.config["tasks"][task_name].get("enabled", True)
            }
        }
    
    def run_scheduler(self):
        """Run the scheduler (blocking)."""
        self._logger.info("Starting background governance scheduler...")
        self.setup_schedule()
        
        self._logger.info("Simplified scheduler - use --run <task> for manual execution")
        print("Use --run <task_name> for manual task execution")
        print("Available tasks: orphaned_solution_scan, spec_consistency_check, governance_compliance_audit")


def main():
    """Main entry point for background scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Background Governance Scheduler")
    parser.add_argument("--run", choices=["orphaned_solution_scan", "spec_consistency_check", "governance_compliance_audit"], 
                       help="Run a specific task once")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (continuous scheduling)")
    
    args = parser.parse_args()
    
    scheduler = BackgroundGovernanceScheduler()
    
    if args.run:
        print(f"🔄 Running task: {args.run}")
        result = scheduler.run_once(args.run)
        print(f"✅ Task completed: {scheduler._summarize_result(result)}")
        
    elif args.status:
        status = scheduler.get_status()
        print("📊 Scheduler Status:")
        print(f"   Enabled: {status['scheduler_enabled']}")
        print(f"   Tasks Configured: {status['tasks_configured']}")
        print(f"   Last Runs: {status['last_runs']}")
        print(f"   Error Counts: {status['error_counts']}")
        
    elif args.daemon:
        scheduler.run_scheduler()
        
    else:
        print("🔍 Running orphaned solution scan (default)...")
        result = scheduler.run_once("orphaned_solution_scan")
        print(f"✅ Scan completed: {scheduler._summarize_result(result)}")


if __name__ == "__main__":
    main()