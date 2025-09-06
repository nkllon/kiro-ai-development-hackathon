#!/usr/bin/env python3
"""
Headless Execution Monitoring Dashboard

Real-time monitoring of background spec execution with progress tracking,
resource utilization, and intervention capabilities.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from beast_mode.billing.gcp_integration import GCPBillingMonitor
    BILLING_AVAILABLE = True
except ImportError:
    BILLING_AVAILABLE = False


class ExecutionMonitor:
    """Real-time monitoring for headless spec execution"""
    
    def __init__(self):
        self.execution_dir = Path('headless_execution')
        self.execution_dir.mkdir(exist_ok=True)
        
        # Initialize billing monitor if available
        self.billing_monitor = None
        if BILLING_AVAILABLE:
            try:
                self.billing_monitor = GCPBillingMonitor({})
            except Exception as e:
                print(f"⚠️  Billing monitor unavailable: {e}")
    
    def find_active_executions(self) -> List[Dict[str, Any]]:
        """Find all active execution plans"""
        executions = []
        
        for plan_file in self.execution_dir.glob("*_plan.json"):
            try:
                with open(plan_file) as f:
                    execution_data = json.load(f)
                
                # Convert string dates back to datetime for processing
                if execution_data.get('status') in ['running', 'paused']:
                    executions.append(execution_data)
                    
            except Exception as e:
                print(f"⚠️  Error reading {plan_file}: {e}")
        
        return executions
    
    def get_execution_metrics(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate execution metrics"""
        tasks = execution_data.get('tasks', [])
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        failed_tasks = len([t for t in tasks if t.get('status') == 'failed'])
        running_tasks = len([t for t in tasks if t.get('status') == 'running'])
        pending_tasks = len([t for t in tasks if t.get('status') == 'pending'])
        
        progress_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate estimated completion
        estimated_completion = self._estimate_completion(execution_data)
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'running_tasks': running_tasks,
            'pending_tasks': pending_tasks,
            'progress_percent': progress_percent,
            'estimated_completion': estimated_completion,
            'parallel_tracks': execution_data.get('parallel_tracks', 1),
            'critical_path_progress': self._calculate_critical_path_progress(execution_data)
        }
    
    def _estimate_completion(self, execution_data: Dict[str, Any]) -> Optional[str]:
        """Estimate completion time"""
        tasks = execution_data.get('tasks', [])
        
        # Find completed tasks with timing data
        completed_with_timing = []
        for task in tasks:
            if (task.get('status') == 'completed' and 
                task.get('started_at') and task.get('completed_at')):
                
                try:
                    started = datetime.fromisoformat(task['started_at'].replace('Z', '+00:00'))
                    completed = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                    duration = (completed - started).total_seconds()
                    completed_with_timing.append(duration)
                except:
                    continue
        
        if not completed_with_timing:
            return None
        
        # Calculate average task duration
        avg_duration = sum(completed_with_timing) / len(completed_with_timing)
        
        # Estimate remaining time
        remaining_tasks = len([t for t in tasks if t.get('status') in ['pending', 'running']])
        parallel_tracks = execution_data.get('parallel_tracks', 1)
        
        estimated_seconds = (remaining_tasks * avg_duration) / parallel_tracks
        completion_time = datetime.now() + timedelta(seconds=estimated_seconds)
        
        return completion_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def _calculate_critical_path_progress(self, execution_data: Dict[str, Any]) -> float:
        """Calculate progress along critical path"""
        critical_path = execution_data.get('critical_path', [])
        if not critical_path:
            return 0.0
        
        tasks = execution_data.get('tasks', [])
        
        # Find tasks on critical path
        critical_tasks = []
        for spec_name in critical_path:
            spec_tasks = [t for t in tasks if t.get('spec_name') == spec_name]
            critical_tasks.extend(spec_tasks)
        
        if not critical_tasks:
            return 0.0
        
        completed_critical = len([t for t in critical_tasks if t.get('status') == 'completed'])
        return (completed_critical / len(critical_tasks)) * 100
    
    async def get_cost_metrics(self) -> Dict[str, Any]:
        """Get current cost metrics if billing is available"""
        if not self.billing_monitor:
            return {
                'total_cost': 0.0,
                'hourly_rate': 0.0,
                'execution_cost': 0.0,
                'available': False
            }
        
        try:
            billing_metrics = await self.billing_monitor.collect_billing_metrics()
            return {
                'total_cost': billing_metrics.total_cost_usd,
                'hourly_rate': billing_metrics.hourly_burn_rate,
                'execution_cost': billing_metrics.daily_cost_usd,
                'available': True,
                'cost_breakdown': billing_metrics.cost_breakdown
            }
        except Exception as e:
            return {
                'total_cost': 0.0,
                'hourly_rate': 0.0,
                'execution_cost': 0.0,
                'available': False,
                'error': str(e)
            }
    
    def display_dashboard(self, executions: List[Dict[str, Any]], cost_metrics: Dict[str, Any]):
        """Display real-time monitoring dashboard"""
        
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🎯 ═══════════════════════════════════════════════════════════")
        print("   BEAST MODE HEADLESS EXECUTION MONITOR")
        print("   \"Autonomous Development with Full Visibility\"")
        print("═══════════════════════════════════════════════════════════")
        print()
        
        if not executions:
            print("📋 No active executions found")
            print("   Run 'python scripts/launch_headless_execution.py' to start")
            return
        
        # Display each active execution
        for i, execution_data in enumerate(executions):
            metrics = self.get_execution_metrics(execution_data)
            
            print(f"🚀 EXECUTION #{i+1}: {execution_data.get('plan_id', 'Unknown')}")
            print(f"   📊 Progress: {metrics['progress_percent']:.1f}% ({metrics['completed_tasks']}/{metrics['total_tasks']} tasks)")
            print(f"   🔄 Running: {metrics['running_tasks']} | ⏳ Pending: {metrics['pending_tasks']} | ❌ Failed: {metrics['failed_tasks']}")
            print(f"   🔀 Parallel Tracks: {metrics['parallel_tracks']}")
            print(f"   🎯 Critical Path: {metrics['critical_path_progress']:.1f}%")
            
            if metrics['estimated_completion']:
                print(f"   ⏰ Est. Completion: {metrics['estimated_completion']}")
            
            # Show recent task activity
            tasks = execution_data.get('tasks', [])
            recent_completed = [t for t in tasks if t.get('status') == 'completed'][-3:]
            if recent_completed:
                print(f"   ✅ Recent Completions:")
                for task in recent_completed:
                    print(f"      • {task.get('task_name', 'Unknown task')}")
            
            running_tasks = [t for t in tasks if t.get('status') == 'running']
            if running_tasks:
                print(f"   ⚡ Currently Running:")
                for task in running_tasks[:3]:  # Show first 3
                    print(f"      • {task.get('task_name', 'Unknown task')}")
            
            print()
        
        # Display cost metrics
        print("💰 COST MONITORING:")
        if cost_metrics['available']:
            print(f"   💸 Total Cost: ${cost_metrics['total_cost']:.4f}")
            print(f"   🔥 Burn Rate: ${cost_metrics['hourly_rate']:.4f}/hour")
            print(f"   🎯 Execution Cost: ${cost_metrics['execution_cost']:.4f}")
            
            if 'cost_breakdown' in cost_metrics:
                print(f"   📊 Breakdown:")
                for service, cost in cost_metrics['cost_breakdown'].items():
                    print(f"      • {service}: ${cost:.4f}")
        else:
            print("   ⚠️  Cost monitoring unavailable")
            if 'error' in cost_metrics:
                print(f"      Error: {cost_metrics['error']}")
        
        print()
        
        # Display system status
        print("🖥️  SYSTEM STATUS:")
        print(f"   ⏰ Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   📁 Execution Dir: {self.execution_dir}")
        print(f"   🔧 Billing Monitor: {'✅ Available' if BILLING_AVAILABLE else '❌ Unavailable'}")
        
        print()
        print("Press Ctrl+C to exit monitoring")
    
    async def monitor_loop(self, refresh_interval: int = 5):
        """Main monitoring loop"""
        
        try:
            while True:
                # Get current executions
                executions = self.find_active_executions()
                
                # Get cost metrics
                cost_metrics = await self.get_cost_metrics()
                
                # Display dashboard
                self.display_dashboard(executions, cost_metrics)
                
                # Wait for next refresh
                await asyncio.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
    
    def show_execution_details(self, execution_id: str):
        """Show detailed information about a specific execution"""
        
        plan_file = self.execution_dir / f"{execution_id}_plan.json"
        
        if not plan_file.exists():
            print(f"❌ Execution {execution_id} not found")
            return
        
        try:
            with open(plan_file) as f:
                execution_data = json.load(f)
            
            print(f"📋 EXECUTION DETAILS: {execution_id}")
            print("=" * 60)
            
            # Basic info
            print(f"Status: {execution_data.get('status', 'Unknown')}")
            print(f"Created: {execution_data.get('created_at', 'Unknown')}")
            print(f"Total Specs: {execution_data.get('total_specs', 0)}")
            print(f"Total Tasks: {execution_data.get('total_tasks', 0)}")
            print(f"Estimated Duration: {execution_data.get('estimated_duration_hours', 0):.1f} hours")
            print()
            
            # Task breakdown by spec
            tasks = execution_data.get('tasks', [])
            specs = {}
            
            for task in tasks:
                spec_name = task.get('spec_name', 'Unknown')
                if spec_name not in specs:
                    specs[spec_name] = {'total': 0, 'completed': 0, 'failed': 0, 'running': 0}
                
                specs[spec_name]['total'] += 1
                status = task.get('status', 'pending')
                if status in specs[spec_name]:
                    specs[spec_name][status] += 1
            
            print("📊 PROGRESS BY SPEC:")
            for spec_name, counts in specs.items():
                progress = (counts['completed'] / counts['total']) * 100 if counts['total'] > 0 else 0
                print(f"   {spec_name}: {progress:.1f}% ({counts['completed']}/{counts['total']})")
                if counts['failed'] > 0:
                    print(f"      ❌ {counts['failed']} failed")
                if counts['running'] > 0:
                    print(f"      ⚡ {counts['running']} running")
            
            print()
            
            # Failed tasks
            failed_tasks = [t for t in tasks if t.get('status') == 'failed']
            if failed_tasks:
                print("❌ FAILED TASKS:")
                for task in failed_tasks:
                    print(f"   • {task.get('task_name', 'Unknown')}")
                    if task.get('error_message'):
                        print(f"     Error: {task['error_message']}")
                print()
            
        except Exception as e:
            print(f"❌ Error reading execution details: {e}")


async def main():
    """Main entry point for monitoring"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        monitor = ExecutionMonitor()
        
        if command == "details" and len(sys.argv) > 2:
            execution_id = sys.argv[2]
            monitor.show_execution_details(execution_id)
        elif command == "list":
            executions = monitor.find_active_executions()
            if executions:
                print("📋 Active Executions:")
                for execution in executions:
                    print(f"   • {execution.get('plan_id', 'Unknown')} - {execution.get('status', 'Unknown')}")
            else:
                print("📋 No active executions found")
        else:
            print("Usage: python scripts/monitor_headless_execution.py [list|details <execution_id>]")
    else:
        # Start real-time monitoring
        print("🎯 Starting Beast Mode Headless Execution Monitor...")
        print("   Real-time monitoring with 5-second refresh")
        print("   Press Ctrl+C to exit")
        print()
        
        monitor = ExecutionMonitor()
        await monitor.monitor_loop()


if __name__ == "__main__":
    asyncio.run(main())