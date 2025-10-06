#!/usr/bin/env python3
"""
System Architecture DAG Launcher
================================

Comprehensive launcher for the system architecture wiring diagram DAG execution.
Provides multiple execution modes and comprehensive monitoring.
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class SystemArchitectureDAGLauncher:
    """Launcher for system architecture DAG execution with comprehensive options."""
    
    def __init__(self):
        self.config_file = Path("system_architecture_dag_tasks.json")
        self.validation_script = "validate_system_architecture_dag.py"
        self.executor_script = "configurable_llm_dag_executor.py"
        self.monitor_script = "monitor_system_architecture_dag.py"
    
    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met for DAG execution."""
        
        print("🔍 VALIDATING PREREQUISITES")
        print("=" * 40)
        
        # Check required files exist
        required_files = [
            self.config_file,
            self.validation_script,
            self.executor_script
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        print("✅ All required files present")
        
        # Validate DAG structure
        print("🔍 Validating DAG structure...")
        try:
            result = subprocess.run([
                sys.executable, self.validation_script
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print("❌ DAG validation failed:")
                print(result.stdout)
                print(result.stderr)
                return False
            
            print("✅ DAG structure is valid")
            
        except Exception as e:
            print(f"❌ Error validating DAG: {e}")
            return False
        
        # Check system constraints
        print("🔍 Checking system constraints...")
        constraints_met = self._check_system_constraints()
        
        if constraints_met:
            print("✅ All prerequisites validated successfully")
            return True
        else:
            print("⚠️  Some constraints not met - will use fallback modes")
            return True  # Still allow execution with fallbacks
    
    def _check_system_constraints(self) -> bool:
        """Check system constraints (Directus, Redis, Observatory)."""
        
        constraints = {
            "Directus CMS (localhost:8055)": self._check_directus(),
            "Redis Primary (192.168.1.119:6379)": self._check_redis_primary(),
            "Redis Fallback (localhost:6380)": self._check_redis_fallback(),
            "Observatory Server (localhost:8888)": self._check_observatory()
        }
        
        all_met = True
        for constraint, status in constraints.items():
            if status:
                print(f"   ✅ {constraint}")
            else:
                print(f"   ❌ {constraint} - will use fallback")
                all_met = False
        
        return all_met
    
    def _check_directus(self) -> bool:
        """Check if Directus CMS is available."""
        try:
            import requests
            response = requests.get("http://localhost:8055/server/ping", timeout=5)
            return response.text.strip() == "pong"
        except Exception:
            return False
    
    def _check_redis_primary(self) -> bool:
        """Check if Redis primary is available."""
        try:
            import redis
            r = redis.Redis(host='192.168.1.119', port=6379, socket_timeout=3)
            return r.ping()
        except Exception:
            return False
    
    def _check_redis_fallback(self) -> bool:
        """Check if Redis fallback is available."""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6380, socket_timeout=3)
            return r.ping()
        except Exception:
            return False
    
    def _check_observatory(self) -> bool:
        """Check if Observatory server is available."""
        try:
            import requests
            response = requests.get("http://localhost:8888/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def show_execution_options(self) -> None:
        """Display available execution options."""
        
        print("\n🚀 SYSTEM ARCHITECTURE DAG EXECUTION OPTIONS")
        print("=" * 50)
        
        print("1. 🔥 FULL PARALLEL EXECUTION (Recommended)")
        print("   Execute all tasks with maximum parallelization")
        print("   Estimated time: ~9.2 hours")
        print("   Command: python launch_system_architecture_dag.py --mode=full-parallel")
        
        print("\n2. 📋 SEQUENTIAL EXECUTION (Safe)")
        print("   Execute all tasks sequentially")
        print("   Estimated time: ~20.3 hours")
        print("   Command: python launch_system_architecture_dag.py --mode=sequential")
        
        print("\n3. 🎯 CRITICAL PATH ONLY")
        print("   Execute only critical path tasks")
        print("   Estimated time: ~6.5 hours")
        print("   Command: python launch_system_architecture_dag.py --mode=critical-path")
        
        print("\n4. 🧩 GROUP-BY-GROUP EXECUTION")
        print("   Execute specific task groups")
        print("   Available groups:")
        
        # Load config to show groups
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            for group_name, group_data in config.get("task_groups", {}).items():
                task_count = len(group_data.get("tasks", []))
                parallel = "parallel" if group_data.get("parallel_execution", False) else "sequential"
                print(f"     • {group_name}: {task_count} tasks ({parallel})")
        
        except Exception as e:
            print(f"     Error loading groups: {e}")
        
        print("   Command: python launch_system_architecture_dag.py --group=<group_name>")
        
        print("\n5. 🔍 DRY RUN")
        print("   Show what would be executed without running")
        print("   Command: python launch_system_architecture_dag.py --dry-run")
        
        print("\n6. 🛠️  CUSTOM EXECUTION")
        print("   Use configurable_llm_dag_executor.py directly with custom options")
    
    async def execute_full_parallel(self, llm_provider: Optional[str] = None) -> Dict[str, Any]:
        """Execute full DAG with maximum parallelization."""
        
        print("🔥 LAUNCHING FULL PARALLEL EXECUTION")
        print("=" * 40)
        
        cmd = [sys.executable, self.executor_script, "--mode=parallel"]
        if llm_provider:
            cmd.extend(["--llm", llm_provider])
        
        # Start monitoring in background if available
        monitor_process = None
        if Path(self.monitor_script).exists():
            try:
                monitor_process = subprocess.Popen([
                    sys.executable, self.monitor_script
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("📊 Started monitoring process")
            except Exception as e:
                print(f"⚠️  Could not start monitoring: {e}")
        
        try:
            # Execute DAG
            print(f"🚀 Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)  # 2 hour timeout
            
            print("📋 EXECUTION RESULTS:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️  STDERR:")
                print(result.stderr)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            print("❌ Execution timed out after 2 hours")
            return {"success": False, "error": "Timeout"}
            
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return {"success": False, "error": str(e)}
            
        finally:
            # Clean up monitoring process
            if monitor_process:
                try:
                    monitor_process.terminate()
                    monitor_process.wait(timeout=5)
                except Exception:
                    monitor_process.kill()
    
    async def execute_critical_path(self, llm_provider: Optional[str] = None) -> Dict[str, Any]:
        """Execute only critical path tasks."""
        
        print("🎯 LAUNCHING CRITICAL PATH EXECUTION")
        print("=" * 40)
        
        # Load critical path from config
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            critical_path = config.get("execution_matrix", {}).get("critical_path", [])
            print(f"Critical path: {' -> '.join(critical_path)}")
            
            # Create temporary config with only critical path tasks
            critical_tasks = []
            for group_name, group_data in config.get("task_groups", {}).items():
                for task in group_data.get("tasks", []):
                    if task["task_id"] in critical_path:
                        critical_tasks.append(task)
            
            # Execute critical tasks sequentially
            cmd = [sys.executable, self.executor_script, "--mode=sequential"]
            if llm_provider:
                cmd.extend(["--llm", llm_provider])
            
            print(f"🚀 Executing {len(critical_tasks)} critical path tasks")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            print("📋 CRITICAL PATH RESULTS:")
            print(result.stdout)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            print(f"❌ Critical path execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_group(self, group_name: str, llm_provider: Optional[str] = None) -> Dict[str, Any]:
        """Execute specific task group."""
        
        print(f"🧩 LAUNCHING GROUP EXECUTION: {group_name}")
        print("=" * 40)
        
        cmd = [sys.executable, self.executor_script, f"--tasks={group_name}"]
        if llm_provider:
            cmd.extend(["--llm", llm_provider])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            print(f"📋 GROUP '{group_name}' RESULTS:")
            print(result.stdout)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            print(f"❌ Group execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def dry_run(self) -> None:
        """Show what would be executed without running."""
        
        print("🔍 DRY RUN - EXECUTION PREVIEW")
        print("=" * 40)
        
        cmd = [sys.executable, self.executor_script, "--dry-run"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            print(result.stdout)
            
        except Exception as e:
            print(f"❌ Dry run error: {e}")


async def main():
    """Main launcher function."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="System Architecture DAG Launcher")
    parser.add_argument("--mode", choices=["full-parallel", "sequential", "critical-path"], 
                       help="Execution mode")
    parser.add_argument("--group", help="Execute specific task group")
    parser.add_argument("--llm", choices=["kiro", "claude", "llm", "openai"], 
                       help="LLM provider to use")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show execution plan without running")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Only validate prerequisites")
    
    args = parser.parse_args()
    
    launcher = SystemArchitectureDAGLauncher()
    
    # Always validate prerequisites first
    if not launcher.validate_prerequisites():
        print("❌ Prerequisites validation failed!")
        sys.exit(1)
    
    if args.validate_only:
        print("✅ Validation complete - system ready for execution")
        return
    
    # Show options if no specific mode requested
    if not any([args.mode, args.group, args.dry_run]):
        launcher.show_execution_options()
        return
    
    # Execute based on arguments
    if args.dry_run:
        launcher.dry_run()
    elif args.group:
        result = await launcher.execute_group(args.group, args.llm)
        if not result["success"]:
            sys.exit(1)
    elif args.mode == "full-parallel":
        result = await launcher.execute_full_parallel(args.llm)
        if not result["success"]:
            sys.exit(1)
    elif args.mode == "sequential":
        # Use executor directly for sequential mode
        cmd = [sys.executable, launcher.executor_script, "--mode=sequential"]
        if args.llm:
            cmd.extend(["--llm", args.llm])
        subprocess.run(cmd)
    elif args.mode == "critical-path":
        result = await launcher.execute_critical_path(args.llm)
        if not result["success"]:
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())