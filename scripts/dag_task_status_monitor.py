#!/usr/bin/env python3
"""
DAG Task Status Monitor
Prevents status inconsistencies by monitoring task execution state
"""

import sys
import os
import json
import redis
import requests
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, GracefulDegradationResult


class DAGTaskStatusMonitor(ReflectiveModule):
    """Monitor for DAG task status inconsistencies and automatic recovery"""
    
    def __init__(self, check_interval: int = 300):  # 5 minutes default
        super().__init__()
        self.check_interval = check_interval
        self.max_in_progress_duration = 3600  # 1 hour timeout
        self.monitoring_active = True
        
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "dag_task_status_monitor",
            "name": "DAG Task Status Monitor",
            "version": "1.0.0",
            "description": "Monitors and prevents DAG task status inconsistencies",
            "check_interval": self.check_interval,
            "max_in_progress_duration": self.max_in_progress_duration
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.CORE_FUNCTIONALITY
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        issues = []
        if not self.monitoring_active:
            issues.append("Monitoring is not active")
        
        return ModuleHealth(
            module_id="dag_task_status_monitor",
            status=ModuleStatus.HEALTHY if not issues else ModuleStatus.WARNING,
            health_score=1.0 if not issues else 0.7,
            issues=issues,
            last_check=datetime.now(timezone.utc),
            uptime_seconds=(datetime.now(timezone.utc) - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation"""
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def connect_to_redis(self) -> Optional[redis.Redis]:
        """Connect to Redis for monitoring"""
        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD', os.getenv('BEAST_MODE_REDIS_PASSWORD', ''))
            
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password if redis_password else None,
                decode_responses=True
            )
            
            r.ping()
            return r
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return None
    
    def authenticate_with_directus(self) -> Optional[str]:
        """Authenticate with Directus CMS"""
        try:
            auth_data = {
                "email": "admin@example.com",
                "password": "d1r3ctu5"
            }
            
            response = requests.post(
                "http://localhost:8055/auth/login",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('data', {}).get('access_token')
                return token
            return None
            
        except Exception as e:
            print(f"❌ Directus authentication failed: {e}")
            return None
    
    def get_in_progress_tasks(self, token: str) -> List[Dict[str, Any]]:
        """Get all tasks with in_progress status from CMS"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                "http://localhost:8055/items/tasks",
                headers=headers,
                params={
                    "filter[status][_eq]": "in_progress",
                    "limit": -1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"❌ Failed to get in-progress tasks: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting in-progress tasks: {e}")
            return []
    
    def check_redis_execution_activity(self, r: redis.Redis, task_id: int) -> bool:
        """Check if task has any active execution in Redis"""
        patterns_to_check = [
            f"*task*{task_id}*",
            f"*execution*{task_id}*",
            f"*dag*{task_id}*"
        ]
        
        for pattern in patterns_to_check:
            try:
                keys = r.keys(pattern)
                for key in keys:
                    try:
                        key_type = r.type(key)
                        
                        if key_type == 'string':
                            value = r.get(key)
                            try:
                                data = json.loads(value)
                                if isinstance(data, dict):
                                    status = data.get('status', '').lower()
                                    if status in ['running', 'executing', 'in_progress']:
                                        return True
                            except json.JSONDecodeError:
                                pass
                        
                        elif key_type == 'hash':
                            hash_data = r.hgetall(key)
                            status = hash_data.get('status', '').lower()
                            if status in ['running', 'executing', 'in_progress']:
                                return True
                                
                    except Exception as e:
                        print(f"⚠️  Error checking key {key}: {e}")
                        
            except Exception as e:
                print(f"⚠️  Error checking pattern {pattern}: {e}")
        
        return False
    
    def is_task_stuck(self, task: Dict[str, Any]) -> bool:
        """Check if task has been in_progress for too long"""
        try:
            updated_at = task.get('updated_at')
            if not updated_at:
                return True  # No update time means potentially stuck
            
            # Parse the timestamp
            if isinstance(updated_at, str):
                # Handle various timestamp formats
                try:
                    if updated_at.endswith('Z'):
                        updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    elif '+' in updated_at or updated_at.endswith('UTC'):
                        updated_time = datetime.fromisoformat(updated_at.replace('UTC', '').strip())
                    else:
                        updated_time = datetime.fromisoformat(updated_at)
                        
                    # Ensure timezone awareness
                    if updated_time.tzinfo is None:
                        updated_time = updated_time.replace(tzinfo=timezone.utc)
                        
                except ValueError:
                    print(f"⚠️  Could not parse timestamp: {updated_at}")
                    return True
            else:
                return True
            
            # Check if task has been in_progress too long
            now = datetime.now(timezone.utc)
            duration = (now - updated_time).total_seconds()
            
            return duration > self.max_in_progress_duration
            
        except Exception as e:
            print(f"⚠️  Error checking if task is stuck: {e}")
            return True
    
    def mark_task_as_failed(self, token: str, task_id: int, reason: str) -> bool:
        """Mark a stuck task as failed"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            update_data = {
                "status": "failed",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "notes": f"Auto-failed by status monitor: {reason}"
            }
            
            response = requests.patch(
                f"http://localhost:8055/items/tasks/{task_id}",
                headers=headers,
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Task {task_id} marked as failed: {reason}")
                return True
            else:
                print(f"❌ Failed to update task {task_id}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error marking task {task_id} as failed: {e}")
            return False
    
    def check_and_fix_inconsistencies(self) -> Dict[str, Any]:
        """Check for and fix status inconsistencies"""
        print(f"🔍 Checking for DAG task status inconsistencies...")
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tasks_checked": 0,
            "inconsistencies_found": 0,
            "tasks_fixed": 0,
            "errors": []
        }
        
        # Connect to systems
        r = self.connect_to_redis()
        token = self.authenticate_with_directus()
        
        if not r or not token:
            error_msg = "Failed to connect to required systems"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            return results
        
        # Get in-progress tasks
        in_progress_tasks = self.get_in_progress_tasks(token)
        results["tasks_checked"] = len(in_progress_tasks)
        
        print(f"📊 Found {len(in_progress_tasks)} tasks with 'in_progress' status")
        
        for task in in_progress_tasks:
            task_id = task.get('id')
            task_title = task.get('title', 'Unknown')
            
            print(f"🔍 Checking Task {task_id}: {task_title}")
            
            # Check if task has active execution in Redis
            has_redis_activity = self.check_redis_execution_activity(r, task_id)
            
            # Check if task is stuck (too long in progress)
            is_stuck = self.is_task_stuck(task)
            
            if not has_redis_activity or is_stuck:
                results["inconsistencies_found"] += 1
                
                if not has_redis_activity and is_stuck:
                    reason = "No Redis activity and stuck for too long"
                elif not has_redis_activity:
                    reason = "No corresponding Redis execution activity"
                else:
                    reason = f"Stuck in progress for over {self.max_in_progress_duration/3600:.1f} hours"
                
                print(f"  ❌ INCONSISTENCY: {reason}")
                
                # Fix the inconsistency
                if self.mark_task_as_failed(token, task_id, reason):
                    results["tasks_fixed"] += 1
                else:
                    results["errors"].append(f"Failed to fix Task {task_id}")
            else:
                print(f"  ✅ Task {task_id} appears to be running normally")
        
        return results
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a single monitoring cycle"""
        print(f"🔄 Starting DAG task status monitoring cycle")
        print(f"⏰ Check interval: {self.check_interval} seconds")
        print(f"⏱️  Max in-progress duration: {self.max_in_progress_duration} seconds")
        print("=" * 60)
        
        results = self.check_and_fix_inconsistencies()
        
        print("\n📊 MONITORING CYCLE RESULTS:")
        print(f"  Tasks checked: {results['tasks_checked']}")
        print(f"  Inconsistencies found: {results['inconsistencies_found']}")
        print(f"  Tasks fixed: {results['tasks_fixed']}")
        
        if results['errors']:
            print(f"  Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"    - {error}")
        
        return results
    
    def start_continuous_monitoring(self):
        """Start continuous monitoring loop"""
        print("🚀 Starting continuous DAG task status monitoring...")
        print(f"⏰ Will check every {self.check_interval} seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while self.monitoring_active:
                results = self.run_monitoring_cycle()
                
                # Log results to file
                log_file = f"dag_task_status_monitoring_{datetime.now().strftime('%Y%m%d')}.log"
                with open(log_file, 'a') as f:
                    f.write(f"{json.dumps(results)}\n")
                
                print(f"\n⏳ Waiting {self.check_interval} seconds until next check...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.monitoring_active = False
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
            self.monitoring_active = False
    
    def run_single_check(self) -> Dict[str, Any]:
        """Run a single status check"""
        return self.run_monitoring_cycle()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="DAG Task Status Monitor")
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--timeout', type=int, default=3600,
                       help='Max in-progress duration in seconds (default: 3600)')
    
    args = parser.parse_args()
    
    monitor = DAGTaskStatusMonitor(check_interval=args.interval)
    monitor.max_in_progress_duration = args.timeout
    
    if args.continuous:
        monitor.start_continuous_monitoring()
    else:
        results = monitor.run_single_check()
        return results


if __name__ == "__main__":
    main()