#!/usr/bin/env python3
"""
DAG Task Failure Investigator
Comprehensive investigation of Task ID 2 failure and status inconsistency
"""

import sys
import os
import json
import redis
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import glob

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, GracefulDegradationResult


class DAGTaskFailureInvestigator(ReflectiveModule):
    """Comprehensive investigator for DAG task execution failures"""
    
    def __init__(self):
        super().__init__()
        self.task_id = 2
        self.task_name = "Data Loading Test"
        self.investigation_results = {}
        
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "dag_task_failure_investigator",
            "name": "DAG Task Failure Investigator",
            "version": "1.0.0",
            "description": "Investigates DAG task execution failures and status inconsistencies"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        return ModuleHealth(
            module_id="dag_task_failure_investigator",
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
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
        """Connect to Redis for investigation"""
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
    
    def investigate_redis_execution_history(self, r: redis.Redis) -> Dict[str, Any]:
        """Investigate Redis for any traces of Task ID 2 execution"""
        print("🔍 Investigating Redis execution history...")
        
        results = {
            "task_keys": [],
            "execution_keys": [],
            "dag_keys": [],
            "error_keys": [],
            "beast_mode_keys": [],
            "historical_data": {}
        }
        
        # Check for task-related keys
        patterns_to_check = [
            f"*task*{self.task_id}*",
            f"*execution*{self.task_id}*",
            f"*dag*{self.task_id}*",
            "*error*",
            "*failed*",
            "*exception*",
            "beast_mode:*",
            "execution:*",
            "dag:*"
        ]
        
        for pattern in patterns_to_check:
            try:
                keys = r.keys(pattern)
                if keys:
                    print(f"  📋 Pattern '{pattern}': {len(keys)} keys found")
                    
                    for key in keys:
                        try:
                            key_type = r.type(key)
                            
                            if key_type == 'string':
                                value = r.get(key)
                                try:
                                    data = json.loads(value)
                                    if isinstance(data, dict) and ('task_id' in data or 'id' in data):
                                        task_id_in_data = data.get('task_id', data.get('id'))
                                        if str(task_id_in_data) == str(self.task_id):
                                            results["historical_data"][key] = data
                                            print(f"    🎯 FOUND Task {self.task_id} data in {key}")
                                except json.JSONDecodeError:
                                    if str(self.task_id) in str(value):
                                        results["historical_data"][key] = value
                                        print(f"    🎯 FOUND Task {self.task_id} reference in {key}")
                            
                            elif key_type == 'hash':
                                hash_data = r.hgetall(key)
                                if any(str(self.task_id) in str(v) for v in hash_data.values()):
                                    results["historical_data"][key] = hash_data
                                    print(f"    🎯 FOUND Task {self.task_id} in hash {key}")
                            
                            # Categorize keys
                            if 'task' in key.lower():
                                results["task_keys"].append(key)
                            elif 'execution' in key.lower():
                                results["execution_keys"].append(key)
                            elif 'dag' in key.lower():
                                results["dag_keys"].append(key)
                            elif any(word in key.lower() for word in ['error', 'failed', 'exception']):
                                results["error_keys"].append(key)
                            elif 'beast_mode' in key.lower():
                                results["beast_mode_keys"].append(key)
                                
                        except Exception as e:
                            print(f"    ⚠️  Error reading key {key}: {e}")
                            
            except Exception as e:
                print(f"  ❌ Error checking pattern {pattern}: {e}")
        
        return results
    
    def investigate_cms_task_details(self, token: str) -> Dict[str, Any]:
        """Get detailed information about Task ID 2 from CMS"""
        print("🔍 Investigating CMS task details...")
        
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Get specific task details
            response = requests.get(
                f"http://localhost:8055/items/tasks/{self.task_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                task_data = response.json().get('data', {})
                print(f"  📋 Task {self.task_id} details:")
                print(f"    Title: {task_data.get('title', 'N/A')}")
                print(f"    Status: {task_data.get('status', 'N/A')}")
                print(f"    Created: {task_data.get('created_at', 'N/A')}")
                print(f"    Updated: {task_data.get('updated_at', 'N/A')}")
                print(f"    Description: {task_data.get('description', 'N/A')}")
                
                return {
                    "task_found": True,
                    "task_data": task_data,
                    "status_history": self._get_task_status_history(headers, self.task_id)
                }
            else:
                print(f"  ❌ Failed to get task details: {response.status_code}")
                return {"task_found": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"  ❌ Error getting task details: {e}")
            return {"task_found": False, "error": str(e)}
    
    def _get_task_status_history(self, headers: Dict[str, str], task_id: int) -> List[Dict]:
        """Try to get task status update history"""
        try:
            # Check for task history or audit logs
            response = requests.get(
                "http://localhost:8055/activity",
                headers=headers,
                params={
                    "filter[collection][_eq]": "tasks",
                    "filter[item][_eq]": str(task_id),
                    "sort": "-timestamp",
                    "limit": 50
                },
                timeout=30
            )
            
            if response.status_code == 200:
                activities = response.json().get('data', [])
                print(f"    📊 Found {len(activities)} activity records for task {task_id}")
                return activities
            else:
                print(f"    ⚠️  No activity history available")
                return []
                
        except Exception as e:
            print(f"    ⚠️  Error getting task history: {e}")
            return []
    
    def investigate_log_files(self) -> Dict[str, Any]:
        """Search for log files that might contain Task ID 2 execution traces"""
        print("🔍 Investigating log files...")
        
        results = {
            "log_files_found": [],
            "task_references": [],
            "error_traces": []
        }
        
        # Common log file locations
        log_patterns = [
            "*.log",
            "logs/*.log",
            ".kiro/execution-logs/*.log",
            ".kiro/execution-logs/*.out",
            ".kiro/execution-logs/*.err",
            "dag_execution_*.log",
            "execution_*.log",
            "task_*.log",
            "observatory*.log",
            "beast_mode*.log"
        ]
        
        for pattern in log_patterns:
            try:
                log_files = glob.glob(pattern, recursive=True)
                for log_file in log_files:
                    if os.path.exists(log_file):
                        results["log_files_found"].append(log_file)
                        
                        # Search for Task ID 2 references
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if str(self.task_id) in content or self.task_name in content:
                                    results["task_references"].append({
                                        "file": log_file,
                                        "size": os.path.getsize(log_file),
                                        "modified": datetime.fromtimestamp(os.path.getmtime(log_file)).isoformat()
                                    })
                                    print(f"  🎯 FOUND Task {self.task_id} reference in {log_file}")
                                    
                                    # Look for error patterns around task references
                                    lines = content.split('\n')
                                    for i, line in enumerate(lines):
                                        if str(self.task_id) in line or self.task_name in line:
                                            # Get context around the reference
                                            start = max(0, i - 3)
                                            end = min(len(lines), i + 4)
                                            context = lines[start:end]
                                            
                                            if any(word in line.lower() for word in ['error', 'failed', 'exception', 'traceback']):
                                                results["error_traces"].append({
                                                    "file": log_file,
                                                    "line_number": i + 1,
                                                    "context": context
                                                })
                                                print(f"    ❌ ERROR trace found at line {i + 1}")
                        except Exception as e:
                            print(f"    ⚠️  Error reading {log_file}: {e}")
                            
            except Exception as e:
                print(f"  ⚠️  Error checking pattern {pattern}: {e}")
        
        print(f"  📊 Scanned {len(results['log_files_found'])} log files")
        print(f"  🎯 Found {len(results['task_references'])} files with task references")
        print(f"  ❌ Found {len(results['error_traces'])} error traces")
        
        return results
    
    def investigate_dag_orchestration_context(self) -> Dict[str, Any]:
        """Investigate DAG orchestration context and execution history"""
        print("🔍 Investigating DAG orchestration context...")
        
        results = {
            "dag_files_found": [],
            "execution_reports": [],
            "constellation_status": {}
        }
        
        # Look for DAG execution reports and status files
        dag_patterns = [
            "DAG_ORCHESTRATION_*.json",
            "CONFIGURABLE_LLM_DAG_EXECUTION_REPORT_*.json",
            "KIRO_DAG_EXECUTION_REPORT_*.json",
            "dag_execution_report_*.json",
            "system_architecture_dag_status_*.json",
            ".kiro/execution-status.json",
            ".kiro/task-registry.json",
            ".kiro/constellation-execution-config.json"
        ]
        
        for pattern in dag_patterns:
            try:
                files = glob.glob(pattern, recursive=True)
                for file_path in files:
                    if os.path.exists(file_path):
                        results["dag_files_found"].append(file_path)
                        
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                
                                # Check if this file contains information about our task
                                if self._contains_task_reference(data, self.task_id):
                                    results["execution_reports"].append({
                                        "file": file_path,
                                        "data": data,
                                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                                    })
                                    print(f"  🎯 FOUND Task {self.task_id} in DAG report: {file_path}")
                                    
                        except Exception as e:
                            print(f"    ⚠️  Error reading {file_path}: {e}")
                            
            except Exception as e:
                print(f"  ⚠️  Error checking pattern {pattern}: {e}")
        
        # Check constellation orchestrator status
        try:
            if os.path.exists(".kiro/execution-status.json"):
                with open(".kiro/execution-status.json", 'r') as f:
                    results["constellation_status"] = json.load(f)
                    print(f"  📊 Found constellation execution status")
        except Exception as e:
            print(f"  ⚠️  Error reading constellation status: {e}")
        
        return results
    
    def _contains_task_reference(self, data: Any, task_id: int) -> bool:
        """Recursively check if data contains reference to task ID"""
        if isinstance(data, dict):
            for key, value in data.items():
                if str(task_id) in str(key) or str(task_id) in str(value):
                    return True
                if isinstance(value, (dict, list)):
                    if self._contains_task_reference(value, task_id):
                        return True
        elif isinstance(data, list):
            for item in data:
                if str(task_id) in str(item):
                    return True
                if isinstance(item, (dict, list)):
                    if self._contains_task_reference(item, task_id):
                        return True
        return False
    
    def analyze_system_state_reconciliation(self) -> Dict[str, Any]:
        """Analyze expected vs actual system state for the task"""
        print("🔍 Analyzing system state reconciliation...")
        
        results = {
            "expected_outcomes": [],
            "actual_state": {},
            "data_verification": {},
            "resource_check": {}
        }
        
        # Based on task description "Test loading repository data into Directus collections"
        # Check if repository data was actually loaded
        
        try:
            token = self.authenticate_with_directus()
            if token:
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                # Check collections that might have been populated
                response = requests.get(
                    "http://localhost:8055/collections",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    collections = response.json().get('data', [])
                    results["actual_state"]["collections_count"] = len(collections)
                    
                    # Check for repository-related collections
                    repo_collections = [c for c in collections if 'repo' in c.get('collection', '').lower()]
                    results["actual_state"]["repository_collections"] = repo_collections
                    
                    print(f"  📊 Found {len(collections)} total collections")
                    print(f"  📊 Found {len(repo_collections)} repository-related collections")
                    
                    # Check if collections have data
                    for collection in repo_collections:
                        collection_name = collection.get('collection')
                        try:
                            items_response = requests.get(
                                f"http://localhost:8055/items/{collection_name}",
                                headers=headers,
                                params={"limit": 1},
                                timeout=10
                            )
                            
                            if items_response.status_code == 200:
                                items_data = items_response.json()
                                item_count = len(items_data.get('data', []))
                                results["data_verification"][collection_name] = {
                                    "has_data": item_count > 0,
                                    "sample_count": item_count
                                }
                                print(f"    📋 Collection {collection_name}: {item_count} items")
                                
                        except Exception as e:
                            print(f"    ⚠️  Error checking collection {collection_name}: {e}")
                            
        except Exception as e:
            print(f"  ❌ Error analyzing system state: {e}")
        
        return results
    
    def generate_root_cause_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive root cause analysis"""
        print("\n🔍 GENERATING ROOT CAUSE ANALYSIS")
        print("=" * 60)
        
        # Collect all investigation data
        r = self.connect_to_redis()
        token = self.authenticate_with_directus()
        
        analysis = {
            "investigation_timestamp": datetime.now(timezone.utc).isoformat(),
            "task_details": {
                "task_id": self.task_id,
                "task_name": self.task_name,
                "current_status": "in_progress"
            },
            "findings": {},
            "root_cause": "",
            "timeline": [],
            "recovery_plan": [],
            "prevention_measures": []
        }
        
        if r:
            analysis["findings"]["redis_investigation"] = self.investigate_redis_execution_history(r)
        
        if token:
            analysis["findings"]["cms_investigation"] = self.investigate_cms_task_details(token)
        
        analysis["findings"]["log_investigation"] = self.investigate_log_files()
        analysis["findings"]["dag_investigation"] = self.investigate_dag_orchestration_context()
        analysis["findings"]["system_state"] = self.analyze_system_state_reconciliation()
        
        # Analyze findings to determine root cause
        redis_data = analysis["findings"].get("redis_investigation", {})
        cms_data = analysis["findings"].get("cms_investigation", {})
        log_data = analysis["findings"].get("log_investigation", {})
        dag_data = analysis["findings"].get("dag_investigation", {})
        
        # Determine root cause based on evidence
        if not redis_data.get("historical_data"):
            if not log_data.get("task_references"):
                analysis["root_cause"] = "NEVER_EXECUTED: Task was never actually started or executed"
                analysis["timeline"].append("Task status set to 'in_progress' but execution never began")
            else:
                analysis["root_cause"] = "EXECUTION_FAILED: Task started but failed without status update"
                analysis["timeline"].append("Task execution attempted but failed")
        else:
            analysis["root_cause"] = "STATUS_SYNC_FAILURE: Task completed but status not synchronized"
            analysis["timeline"].append("Task executed but status update mechanism failed")
        
        # Generate recovery plan
        analysis["recovery_plan"] = [
            "1. Update CMS task status to 'failed' to reflect actual state",
            "2. Clear any zombie processes or locks related to Task ID 2",
            "3. Verify system state and clean up any partial data",
            "4. Implement proper status synchronization mechanism",
            "5. Add monitoring to detect similar issues in the future"
        ]
        
        # Generate prevention measures
        analysis["prevention_measures"] = [
            "Implement heartbeat mechanism for running tasks",
            "Add automatic status timeout for stuck 'in_progress' tasks",
            "Create comprehensive execution logging",
            "Implement status synchronization validation",
            "Add monitoring alerts for status inconsistencies"
        ]
        
        return analysis
    
    def create_recovery_script(self, analysis: Dict[str, Any]) -> str:
        """Create executable recovery script"""
        script_content = f'''#!/usr/bin/env python3
"""
Task ID {self.task_id} Recovery Script
Generated: {datetime.now(timezone.utc).isoformat()}
Root Cause: {analysis.get("root_cause", "Unknown")}
"""

import requests
import json
from datetime import datetime, timezone

def authenticate_with_directus():
    """Authenticate with Directus CMS"""
    try:
        auth_data = {{
            "email": "admin@example.com",
            "password": "d1r3ctu5"
        }}
        
        response = requests.post(
            "http://localhost:8055/auth/login",
            json=auth_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {{}}).get('access_token')
        return None
    except Exception as e:
        print(f"❌ Authentication failed: {{e}}")
        return None

def update_task_status():
    """Update Task ID {self.task_id} status to failed"""
    token = authenticate_with_directus()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    headers = {{
        'Authorization': f'Bearer {{token}}',
        'Content-Type': 'application/json'
    }}
    
    update_data = {{
        "status": "failed",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Status corrected by recovery script - task execution failed"
    }}
    
    try:
        response = requests.patch(
            f"http://localhost:8055/items/tasks/{self.task_id}",
            headers=headers,
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Task {self.task_id} status updated to 'failed'")
            return True
        else:
            print(f"❌ Failed to update task status: {{response.status_code}}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating task status: {{e}}")
        return False

def validate_recovery():
    """Validate that recovery was successful"""
    token = authenticate_with_directus()
    if not token:
        return False
    
    headers = {{
        'Authorization': f'Bearer {{token}}',
        'Content-Type': 'application/json'
    }}
    
    try:
        response = requests.get(
            f"http://localhost:8055/items/tasks/{self.task_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            task_data = response.json().get('data', {{}})
            current_status = task_data.get('status')
            print(f"📊 Current task status: {{current_status}}")
            return current_status == 'failed'
        else:
            print(f"❌ Failed to validate recovery: {{response.status_code}}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating recovery: {{e}}")
        return False

if __name__ == "__main__":
    print("🔧 Starting Task ID {self.task_id} recovery...")
    
    if update_task_status():
        if validate_recovery():
            print("✅ Recovery completed successfully")
        else:
            print("❌ Recovery validation failed")
    else:
        print("❌ Recovery failed")
'''
        
        return script_content
    
    def run_investigation(self) -> Dict[str, Any]:
        """Run complete investigation and generate report"""
        print("🚨 STARTING DAG TASK FAILURE INVESTIGATION")
        print("=" * 80)
        print(f"Task ID: {self.task_id}")
        print(f"Task Name: {self.task_name}")
        print(f"Investigation Time: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        
        # Generate comprehensive analysis
        analysis = self.generate_root_cause_analysis()
        
        # Create recovery script
        recovery_script = self.create_recovery_script(analysis)
        
        # Save investigation report
        report_file = f"dag_task_{self.task_id}_failure_investigation_report.json"
        with open(report_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save recovery script
        recovery_file = f"recover_task_{self.task_id}.py"
        with open(recovery_file, 'w') as f:
            f.write(recovery_script)
        
        # Make recovery script executable
        os.chmod(recovery_file, 0o755)
        
        print("\n🎯 INVESTIGATION SUMMARY")
        print("=" * 60)
        print(f"Root Cause: {analysis['root_cause']}")
        print(f"Report Saved: {report_file}")
        print(f"Recovery Script: {recovery_file}")
        
        print("\n📋 RECOVERY PLAN:")
        for i, step in enumerate(analysis['recovery_plan'], 1):
            print(f"  {i}. {step}")
        
        print("\n🛡️  PREVENTION MEASURES:")
        for i, measure in enumerate(analysis['prevention_measures'], 1):
            print(f"  {i}. {measure}")
        
        print("\n🔧 IMMEDIATE ACTION:")
        print(f"  Run: python {recovery_file}")
        
        return analysis


def main():
    investigator = DAGTaskFailureInvestigator()
    analysis = investigator.run_investigation()
    return analysis


if __name__ == "__main__":
    main()