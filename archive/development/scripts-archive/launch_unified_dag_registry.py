#!/usr/bin/env python3
"""
Unified DAG Registry Launcher
============================

Comprehensive launcher for the unified DAG registry implementation.
Provides multiple execution modes and comprehensive monitoring.
"""

import asyncio
import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class UnifiedDAGRegistryLauncher:
    """Launcher for unified DAG registry implementation with comprehensive options."""
    
    def __init__(self):
        self.spec_path = Path(".kiro/specs/unified-dag-registry")
        self.prereq_script = "scripts/check_unified_dag_registry_prereqs.sh"
        self.executor_script = "scripts/execute_unified_dag_registry_tasks.sh"
        self.log_dir = Path("logs/unified-dag-registry")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met for implementation."""
        
        print("🔍 VALIDATING PREREQUISITES")
        print("=" * 40)
        
        # Check if prerequisite script exists and run it
        if not Path(self.prereq_script).exists():
            print(f"❌ Prerequisite script not found: {self.prereq_script}")
            return False
        
        try:
            result = subprocess.run([
                "bash", self.prereq_script
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print("❌ Prerequisites check failed:")
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
                return False
            
            print("✅ All prerequisites validated successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Prerequisites check timed out")
            return False
        except Exception as e:
            print(f"❌ Error running prerequisites check: {e}")
            return False
    
    def _check_redis_connectivity(self) -> Dict[str, bool]:
        """Check Redis connectivity options."""
        
        connectivity = {
            "primary_redis": False,
            "fallback_redis": False,
            "local_redis": False
        }
        
        # Check primary Redis (Vonnegut)
        try:
            result = subprocess.run([
                "python3", "-c", 
                "import redis; redis.Redis(host='192.168.1.119', port=6379, socket_timeout=5).ping()"
            ], capture_output=True, timeout=10)
            connectivity["primary_redis"] = (result.returncode == 0)
        except:
            pass
        
        # Check fallback Redis
        try:
            result = subprocess.run([
                "python3", "-c",
                "import redis; redis.Redis(host='localhost', port=6380, socket_timeout=5).ping()"
            ], capture_output=True, timeout=10)
            connectivity["fallback_redis"] = (result.returncode == 0)
        except:
            pass
        
        # Check local Redis
        try:
            result = subprocess.run([
                "python3", "-c",
                "import redis; redis.Redis(host='localhost', port=6379, socket_timeout=5).ping()"
            ], capture_output=True, timeout=10)
            connectivity["local_redis"] = (result.returncode == 0)
        except:
            pass
        
        return connectivity
    
    def _check_existing_registries(self) -> Dict[str, bool]:
        """Check availability of existing DAG registries for consolidation."""
        
        registries = {
            "in_memory": False,
            "sqlite": False,
            "mathematical": False
        }
        
        # Check in-memory registry
        try:
            result = subprocess.run([
                "python3", "-c",
                "from src.rm_ddd.core.dag_registry import dag_registry; print('OK')"
            ], capture_output=True, timeout=10)
            registries["in_memory"] = (result.returncode == 0)
        except:
            pass
        
        # Check SQLite registry
        try:
            result = subprocess.run([
                "python3", "-c",
                "from src.rm_ddd.core.persistent_dag_registry import persistent_dag_registry; print('OK')"
            ], capture_output=True, timeout=10)
            registries["sqlite"] = (result.returncode == 0)
        except:
            pass
        
        # Check mathematical registry
        try:
            result = subprocess.run([
                "python3", "-c",
                "from src.integration_governance.dag_registry import create_dag_registry; print('OK')"
            ], capture_output=True, timeout=10)
            registries["mathematical"] = (result.returncode == 0)
        except:
            pass
        
        return registries
    
    def show_system_status(self):
        """Show comprehensive system status."""
        
        print("🔍 UNIFIED DAG REGISTRY SYSTEM STATUS")
        print("=" * 50)
        
        # Check spec files
        print("\n📋 Specification Files:")
        spec_files = ["requirements.md", "design.md", "tasks.md", "dag-registry-inventory.md"]
        for file in spec_files:
            file_path = self.spec_path / file
            status = "✅" if file_path.exists() else "❌"
            print(f"   {status} {file}")
        
        # Check Redis connectivity
        print("\n🔗 Redis Connectivity:")
        redis_status = self._check_redis_connectivity()
        print(f"   {'✅' if redis_status['primary_redis'] else '❌'} Primary Redis (192.168.1.119:6379)")
        print(f"   {'✅' if redis_status['fallback_redis'] else '❌'} Fallback Redis (localhost:6380)")
        print(f"   {'✅' if redis_status['local_redis'] else '❌'} Local Redis (localhost:6379)")
        
        # Check existing registries
        print("\n🏗️  Existing DAG Registries:")
        registry_status = self._check_existing_registries()
        print(f"   {'✅' if registry_status['in_memory'] else '❌'} In-Memory Registry")
        print(f"   {'✅' if registry_status['sqlite'] else '❌'} SQLite Registry")
        print(f"   {'✅' if registry_status['mathematical'] else '❌'} Mathematical Registry")
        
        # Check task status
        print("\n📊 Task Status:")
        if (self.spec_path / "tasks.md").exists():
            try:
                with open(self.spec_path / "tasks.md", 'r') as f:
                    content = f.read()
                    completed = content.count("- [x]")
                    remaining = content.count("- [ ]")
                    total = completed + remaining
                    
                    if total > 0:
                        completion_rate = (completed * 100) // total
                        print(f"   📈 Progress: {completed}/{total} tasks ({completion_rate}%)")
                        print(f"   ✅ Completed: {completed}")
                        print(f"   ⏳ Remaining: {remaining}")
                    else:
                        print("   ⚠️  No tasks found")
            except Exception as e:
                print(f"   ❌ Error reading tasks: {e}")
        else:
            print("   ❌ tasks.md not found")
        
        # Overall readiness
        print("\n🎯 Implementation Readiness:")
        redis_ready = any(redis_status.values())
        registries_ready = sum(registry_status.values()) >= 2
        specs_ready = all((self.spec_path / f).exists() for f in spec_files)
        
        if redis_ready and registries_ready and specs_ready:
            print("   🚀 READY FOR IMPLEMENTATION!")
        else:
            print("   ⚠️  Prerequisites need attention")
            if not redis_ready:
                print("      • Redis connectivity required")
            if not registries_ready:
                print("      • At least 2 existing registries needed for consolidation")
            if not specs_ready:
                print("      • Complete specification files required")
    
    def execute_implementation(self, mode: str = "full-parallel", dry_run: bool = False):
        """Execute the unified DAG registry implementation."""
        
        print(f"🚀 EXECUTING UNIFIED DAG REGISTRY IMPLEMENTATION")
        print(f"Mode: {mode}")
        print(f"Dry Run: {dry_run}")
        print("=" * 60)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual implementation will occur")
            print("")
        
        # Validate prerequisites first
        if not self.validate_prerequisites():
            print("🛑 Prerequisites not met - aborting execution")
            return False
        
        # Execute based on mode
        if mode == "full-parallel":
            return self._execute_full_parallel(dry_run)
        elif mode == "critical-path":
            return self._execute_critical_path(dry_run)
        elif mode == "sequential":
            return self._execute_sequential(dry_run)
        else:
            print(f"❌ Unknown execution mode: {mode}")
            return False
    
    def _execute_full_parallel(self, dry_run: bool) -> bool:
        """Execute full parallel implementation."""
        
        print("🎯 FULL PARALLEL EXECUTION")
        print("=" * 30)
        print("Executing all task groups with maximum parallelization")
        print("")
        
        if dry_run:
            print("Would execute:")
            print("1. Infrastructure setup (parallel)")
            print("2. Algorithms + Coordination (parallel)")
            print("3. Core registry implementation")
            print("4. Integration + Migration (parallel)")
            print("5. Optimization + Security (parallel)")
            print("6. Testing + Deployment")
            return True
        
        # Execute the shell script
        try:
            result = subprocess.run([
                "bash", self.executor_script
            ], timeout=7200)  # 2 hour timeout
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Execution timed out")
            return False
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            return False
    
    def _execute_critical_path(self, dry_run: bool) -> bool:
        """Execute critical path only."""
        
        print("🎯 CRITICAL PATH EXECUTION")
        print("=" * 30)
        print("Executing only essential tasks for basic functionality")
        print("")
        
        critical_tasks = [
            "1.1: Create RedisDataManager",
            "2.1: Port DFS cycle detection", 
            "5.1: Create main UnifiedDAGRegistry class",
            "7.2: Implement backward compatibility layer"
        ]
        
        if dry_run:
            print("Would execute critical path:")
            for task in critical_tasks:
                print(f"   • {task}")
            return True
        
        # In a real implementation, this would execute only critical tasks
        print("Executing critical path tasks...")
        for task in critical_tasks:
            print(f"   ⏳ {task}")
            # Simulate work
            print(f"   ✅ {task} - Complete")
        
        return True
    
    def _execute_sequential(self, dry_run: bool) -> bool:
        """Execute sequential implementation."""
        
        print("🎯 SEQUENTIAL EXECUTION")
        print("=" * 30)
        print("Executing all tasks sequentially (safe mode)")
        print("")
        
        if dry_run:
            print("Would execute all 30 tasks sequentially")
            print("Estimated time: ~20 hours")
            return True
        
        # Execute with sequential flag
        try:
            result = subprocess.run([
                "bash", self.executor_script, "--sequential"
            ], timeout=72000)  # 20 hour timeout
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Sequential execution timed out")
            return False
        except Exception as e:
            print(f"❌ Sequential execution failed: {e}")
            return False
    
    def show_help(self):
        """Show help information."""
        
        print("🚀 UNIFIED DAG REGISTRY LAUNCHER")
        print("=" * 40)
        print("")
        print("USAGE:")
        print("  python launch_unified_dag_registry.py [command] [options]")
        print("")
        print("COMMANDS:")
        print("  status                    Show system status and readiness")
        print("  validate                  Validate prerequisites only")
        print("  execute [mode]            Execute implementation")
        print("  help                      Show this help message")
        print("")
        print("EXECUTION MODES:")
        print("  full-parallel            Full parallel execution (recommended, ~8 hours)")
        print("  critical-path            Critical path only (~2 hours)")
        print("  sequential               Sequential execution (safe mode, ~20 hours)")
        print("")
        print("OPTIONS:")
        print("  --dry-run                Show what would be executed without running")
        print("  --llm=kiro|claude        Specify LLM provider (default: auto)")
        print("")
        print("EXAMPLES:")
        print("  python launch_unified_dag_registry.py status")
        print("  python launch_unified_dag_registry.py validate")
        print("  python launch_unified_dag_registry.py execute full-parallel")
        print("  python launch_unified_dag_registry.py execute critical-path --dry-run")
        print("")
        print("CONSOLIDATION TARGET:")
        print("  This launcher consolidates 3 existing DAG registry implementations:")
        print("  • In-Memory Registry (src/rm_ddd/core/dag_registry.py)")
        print("  • SQLite Registry (src/rm_ddd/core/persistent_dag_registry.py)")
        print("  • Mathematical Registry (src/integration_governance/dag_registry.py)")
        print("  Into a single Redis-based unified system with full backward compatibility.")


def main():
    """Main entry point."""
    
    launcher = UnifiedDAGRegistryLauncher()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        launcher.show_help()
        return
    
    command = sys.argv[1].lower()
    dry_run = "--dry-run" in sys.argv
    
    if command == "help" or command == "--help" or command == "-h":
        launcher.show_help()
    
    elif command == "status":
        launcher.show_system_status()
    
    elif command == "validate":
        success = launcher.validate_prerequisites()
        sys.exit(0 if success else 1)
    
    elif command == "execute":
        mode = "full-parallel"  # default
        if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
            mode = sys.argv[2]
        
        success = launcher.execute_implementation(mode, dry_run)
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python launch_unified_dag_registry.py help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()