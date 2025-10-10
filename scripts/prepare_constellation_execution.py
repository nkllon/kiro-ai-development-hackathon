#!/usr/bin/env python3
"""
Constellation Execution Preparation Script
Validates infrastructure and prepares environment for DAG execution
"""

import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import redis
import logging

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability
from beast_mode.execution.dag_executor import DAGExecutor
from beast_mode.execution.task_registry import TaskRegistry


class ConstellationPreparator(ReflectiveModule):
    """Prepares and validates constellation execution environment"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ConstellationPreparator")
        self.validation_results = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "constellation_preparator",
            "name": "Constellation Execution Preparator",
            "version": "1.0.0",
            "description": "Validates infrastructure and prepares environment for DAG execution"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        return ModuleHealth(
            module_id="constellation_preparator",
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
    
    def validate_beast_mode_components(self) -> Dict[str, Any]:
        """Validate Beast Mode infrastructure components"""
        print("🔍 Validating Beast Mode Components...")
        
        results = {
            "dag_executor": {"status": "unknown", "details": {}},
            "task_registry": {"status": "unknown", "details": {}},
            "reflective_module": {"status": "unknown", "details": {}}
        }
        
        try:
            # Test DAG Executor
            dag_executor = DAGExecutor(max_concurrent=2)
            health = dag_executor.get_health_status()
            results["dag_executor"] = {
                "status": "healthy" if health.status == ModuleStatus.HEALTHY else "warning",
                "details": {
                    "health_score": health.health_score,
                    "issues": health.issues,
                    "capabilities": [cap.value for cap in dag_executor.get_capabilities()]
                }
            }
            print("  ✅ DAG Executor: Healthy")
            
        except Exception as e:
            results["dag_executor"] = {
                "status": "error",
                "details": {"error": str(e)}
            }
            print(f"  ❌ DAG Executor: {e}")
        
        try:
            # Test Task Registry
            task_registry = TaskRegistry()
            health = task_registry.get_health_status()
            results["task_registry"] = {
                "status": "healthy" if health.status == ModuleStatus.HEALTHY else "warning",
                "details": {
                    "health_score": health.health_score,
                    "issues": health.issues,
                    "total_tasks": len(task_registry.tasks)
                }
            }
            print("  ✅ Task Registry: Healthy")
            
        except Exception as e:
            results["task_registry"] = {
                "status": "error",
                "details": {"error": str(e)}
            }
            print(f"  ❌ Task Registry: {e}")
        
        # Test ReflectiveModule pattern
        try:
            test_module = ReflectiveModule()
            health = test_module.get_health_status()
            results["reflective_module"] = {
                "status": "healthy",
                "details": {
                    "health_score": health.health_score,
                    "module_info": test_module.get_module_info()
                }
            }
            print("  ✅ ReflectiveModule Pattern: Healthy")
            
        except Exception as e:
            results["reflective_module"] = {
                "status": "error",
                "details": {"error": str(e)}
            }
            print(f"  ❌ ReflectiveModule Pattern: {e}")
        
        return results
    
    def validate_redis_connectivity(self) -> Dict[str, Any]:
        """Validate Redis connectivity and execution tracking"""
        print("🔍 Validating Redis Connectivity...")
        
        result = {
            "status": "unknown",
            "details": {}
        }
        
        try:
            # Try to connect to Redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Test basic operations
            test_key = f"constellation_test_{int(time.time())}"
            r.set(test_key, "test_value", ex=60)  # Expire in 60 seconds
            retrieved_value = r.get(test_key)
            
            if retrieved_value == "test_value":
                # Test execution tracking patterns
                execution_id = f"test_execution_{int(time.time())}"
                r.hset(f"execution:{execution_id}", mapping={
                    "status": "testing",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "test": "true"
                })
                
                # Retrieve and validate
                execution_data = r.hgetall(f"execution:{execution_id}")
                
                if execution_data and execution_data.get("status") == "testing":
                    result = {
                        "status": "healthy",
                        "details": {
                            "connection": "successful",
                            "basic_operations": "working",
                            "execution_tracking": "working",
                            "test_key": test_key,
                            "test_execution": execution_id
                        }
                    }
                    print("  ✅ Redis: Healthy (connection and execution tracking working)")
                else:
                    result = {
                        "status": "warning",
                        "details": {
                            "connection": "successful",
                            "basic_operations": "working",
                            "execution_tracking": "failed",
                            "error": "Could not retrieve execution data"
                        }
                    }
                    print("  ⚠️  Redis: Warning (execution tracking issues)")
                
                # Cleanup test data
                r.delete(test_key)
                r.delete(f"execution:{execution_id}")
                
            else:
                result = {
                    "status": "error",
                    "details": {
                        "connection": "successful",
                        "basic_operations": "failed",
                        "error": "Could not retrieve test value"
                    }
                }
                print("  ❌ Redis: Error (basic operations failed)")
        
        except redis.ConnectionError as e:
            result = {
                "status": "error",
                "details": {
                    "connection": "failed",
                    "error": f"Connection error: {e}"
                }
            }
            print(f"  ❌ Redis: Connection failed - {e}")
        
        except Exception as e:
            result = {
                "status": "error",
                "details": {
                    "connection": "unknown",
                    "error": f"Unexpected error: {e}"
                }
            }
            print(f"  ❌ Redis: Unexpected error - {e}")
        
        return result
    
    def validate_claude_cli(self) -> Dict[str, Any]:
        """Validate Claude CLI integration"""
        print("🔍 Validating Claude CLI Integration...")
        
        result = {
            "status": "unknown",
            "details": {}
        }
        
        try:
            # Check if Claude CLI is available
            process = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if process.returncode == 0:
                version_info = process.stdout.strip()
                
                # Test basic functionality with a simple prompt
                test_prompt = "Please respond with exactly: 'Claude CLI test successful'"
                test_process = subprocess.run(
                    ['claude'],
                    input=test_prompt,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if test_process.returncode == 0:
                    response = test_process.stdout.strip()
                    
                    result = {
                        "status": "healthy",
                        "details": {
                            "version": version_info,
                            "basic_functionality": "working",
                            "test_response": response[:100] + "..." if len(response) > 100 else response
                        }
                    }
                    print(f"  ✅ Claude CLI: Healthy ({version_info})")
                else:
                    result = {
                        "status": "warning",
                        "details": {
                            "version": version_info,
                            "basic_functionality": "failed",
                            "error": test_process.stderr.strip()
                        }
                    }
                    print(f"  ⚠️  Claude CLI: Warning (basic functionality issues)")
            else:
                result = {
                    "status": "error",
                    "details": {
                        "availability": "not_found",
                        "error": process.stderr.strip()
                    }
                }
                print("  ❌ Claude CLI: Not found or not working")
        
        except subprocess.TimeoutExpired:
            result = {
                "status": "error",
                "details": {
                    "availability": "timeout",
                    "error": "Command timed out"
                }
            }
            print("  ❌ Claude CLI: Timeout during validation")
        
        except FileNotFoundError:
            result = {
                "status": "error",
                "details": {
                    "availability": "not_installed",
                    "error": "Claude CLI not found in PATH"
                }
            }
            print("  ❌ Claude CLI: Not installed or not in PATH")
        
        except Exception as e:
            result = {
                "status": "error",
                "details": {
                    "availability": "unknown",
                    "error": f"Unexpected error: {e}"
                }
            }
            print(f"  ❌ Claude CLI: Unexpected error - {e}")
        
        return result
    
    def validate_staging_prompts(self) -> Dict[str, Any]:
        """Validate staging prompts accessibility and integrity"""
        print("🔍 Validating Staging Prompts...")
        
        staging_dir = Path("prompts/staging")
        
        result = {
            "status": "unknown",
            "details": {
                "total_prompts": 0,
                "accessible_prompts": 0,
                "missing_prompts": [],
                "invalid_prompts": [],
                "prompt_categories": {}
            }
        }
        
        try:
            if not staging_dir.exists():
                result = {
                    "status": "error",
                    "details": {
                        "error": f"Staging directory not found: {staging_dir}"
                    }
                }
                print(f"  ❌ Staging Directory: Not found ({staging_dir})")
                return result
            
            # Get all markdown files
            prompt_files = list(staging_dir.glob("*.md"))
            result["details"]["total_prompts"] = len(prompt_files)
            
            accessible_count = 0
            categories = {}
            
            for prompt_file in prompt_files:
                try:
                    # Check if file is readable
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic validation - check if file has content
                    if len(content.strip()) > 0:
                        accessible_count += 1
                        
                        # Categorize by filename pattern
                        filename = prompt_file.name
                        if filename.startswith("phase-1"):
                            category = "Phase 1: Discovery"
                        elif filename.startswith("phase-2"):
                            category = "Phase 2: Requirements"
                        elif filename.startswith("phase-3"):
                            category = "Phase 3: Design"
                        elif filename.startswith("phase-4"):
                            category = "Phase 4: Tasks"
                        elif filename.startswith("phase-5"):
                            category = "Phase 5: Consolidation"
                        else:
                            category = "Other"
                        
                        if category not in categories:
                            categories[category] = 0
                        categories[category] += 1
                    else:
                        result["details"]["invalid_prompts"].append(filename)
                
                except Exception as e:
                    result["details"]["missing_prompts"].append({
                        "file": prompt_file.name,
                        "error": str(e)
                    })
            
            result["details"]["accessible_prompts"] = accessible_count
            result["details"]["prompt_categories"] = categories
            
            # Determine status
            if accessible_count == len(prompt_files) and len(result["details"]["invalid_prompts"]) == 0:
                result["status"] = "healthy"
                print(f"  ✅ Staging Prompts: Healthy ({accessible_count} prompts accessible)")
            elif accessible_count > 0:
                result["status"] = "warning"
                print(f"  ⚠️  Staging Prompts: Warning ({accessible_count}/{len(prompt_files)} accessible)")
            else:
                result["status"] = "error"
                print("  ❌ Staging Prompts: No accessible prompts found")
            
            # Print category breakdown
            for category, count in categories.items():
                print(f"    - {category}: {count} prompts")
        
        except Exception as e:
            result = {
                "status": "error",
                "details": {
                    "error": f"Unexpected error during validation: {e}"
                }
            }
            print(f"  ❌ Staging Prompts: Unexpected error - {e}")
        
        return result
    
    def prepare_execution_environment(self) -> Dict[str, Any]:
        """Prepare directories and configuration files"""
        print("🔧 Preparing Execution Environment...")
        
        result = {
            "status": "unknown",
            "details": {
                "directories_created": [],
                "files_created": [],
                "errors": []
            }
        }
        
        try:
            # Create necessary directories
            directories = [
                Path(".kiro"),
                Path(".kiro/execution-logs"),
                Path(".kiro/execution-status"),
                Path("logs/constellation-execution"),
                Path("reports/constellation-execution")
            ]
            
            for directory in directories:
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    result["details"]["directories_created"].append(str(directory))
                    print(f"  📁 Created directory: {directory}")
                except Exception as e:
                    result["details"]["errors"].append(f"Failed to create {directory}: {e}")
                    print(f"  ❌ Failed to create directory {directory}: {e}")
            
            # Create configuration files
            config_files = {
                ".kiro/constellation-config.json": {
                    "execution_settings": {
                        "max_concurrent_agents": 10,
                        "default_timeout_minutes": 60,
                        "retry_attempts": 3,
                        "log_level": "INFO"
                    },
                    "monitoring": {
                        "progress_update_interval_seconds": 5,
                        "health_check_interval_seconds": 30,
                        "metrics_collection": True
                    },
                    "paths": {
                        "staging_prompts": "prompts/staging",
                        "execution_logs": ".kiro/execution-logs",
                        "status_file": ".kiro/execution-status.json",
                        "reports": "reports/constellation-execution"
                    }
                },
                ".kiro/execution-metadata.json": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "version": "1.0.0",
                    "infrastructure_validated": False,
                    "ready_for_execution": False,
                    "last_validation": None
                }
            }
            
            for file_path, content in config_files.items():
                try:
                    with open(file_path, 'w') as f:
                        json.dump(content, f, indent=2)
                    result["details"]["files_created"].append(file_path)
                    print(f"  📄 Created config file: {file_path}")
                except Exception as e:
                    result["details"]["errors"].append(f"Failed to create {file_path}: {e}")
                    print(f"  ❌ Failed to create config file {file_path}: {e}")
            
            # Determine status
            if len(result["details"]["errors"]) == 0:
                result["status"] = "healthy"
                print("  ✅ Execution Environment: Prepared successfully")
            else:
                result["status"] = "warning"
                print(f"  ⚠️  Execution Environment: Prepared with {len(result['details']['errors'])} errors")
        
        except Exception as e:
            result = {
                "status": "error",
                "details": {
                    "error": f"Unexpected error during preparation: {e}"
                }
            }
            print(f"  ❌ Execution Environment: Unexpected error - {e}")
        
        return result
    
    def register_constellation_tasks(self) -> Dict[str, Any]:
        """Register all constellation tasks in the task registry"""
        print("📝 Registering Constellation Tasks...")
        
        result = {
            "status": "unknown",
            "details": {
                "tasks_registered": 0,
                "registration_errors": [],
                "task_categories": {}
            }
        }
        
        try:
            task_registry = TaskRegistry()
            
            # Define constellation tasks with dependencies and estimates
            constellation_tasks = [
                # Phase 1: Discovery (parallel)
                ("phase-1a-constellation-inventory", [], 150, "Phase 1: Discovery"),
                ("phase-1b-stakeholder-landscape-mapping", [], 120, "Phase 1: Discovery"),
                ("phase-1c-cms-dependency-discovery", [], 90, "Phase 1: Discovery"),
                ("phase-1d-ontology-gap-analysis", [], 105, "Phase 1: Discovery"),
                
                # Phase 2: Requirements (sequential layers)
                ("phase-2-bootstrap-requirements", ["phase-1a-constellation-inventory"], 180, "Phase 2: Requirements"),
                ("phase-2-foundation-requirements", ["phase-2-bootstrap-requirements"], 240, "Phase 2: Requirements"),
                ("phase-2-intelligence-requirements", ["phase-2-foundation-requirements"], 300, "Phase 2: Requirements"),
                ("phase-2-application-requirements", ["phase-2-intelligence-requirements"], 180, "Phase 2: Requirements"),
                
                # Phase 3: Design (parallel based on requirements)
                ("phase-3-bootstrap-designs", ["phase-2-bootstrap-requirements"], 150, "Phase 3: Design"),
                ("phase-3-foundation-designs", ["phase-2-foundation-requirements"], 200, "Phase 3: Design"),
                ("phase-3-intelligence-designs", ["phase-2-intelligence-requirements"], 250, "Phase 3: Design"),
                ("phase-3-application-designs", ["phase-2-application-requirements"], 150, "Phase 3: Design"),
                
                # Phase 4: Tasks (parallel based on designs)
                ("phase-4-bootstrap-tasks", ["phase-3-bootstrap-designs"], 120, "Phase 4: Tasks"),
                ("phase-4-foundation-tasks", ["phase-3-foundation-designs"], 160, "Phase 4: Tasks"),
                ("phase-4-intelligence-tasks", ["phase-3-intelligence-designs"], 200, "Phase 4: Tasks"),
                ("phase-4-application-tasks", ["phase-3-application-designs"], 120, "Phase 4: Tasks"),
                
                # Phase 5: Consolidation (sequential)
                ("phase-5a-cms-requirements-consolidation", 
                 ["phase-2-bootstrap-requirements", "phase-2-foundation-requirements", 
                  "phase-2-intelligence-requirements", "phase-2-application-requirements"], 180, "Phase 5: Consolidation"),
                ("phase-5b-cms-architecture-update", ["phase-5a-cms-requirements-consolidation"], 120, "Phase 5: Consolidation"),
                ("phase-5c-constellation-cms-mapping", ["phase-5b-cms-architecture-update"], 90, "Phase 5: Consolidation"),
                ("phase-5d-stakeholder-validation", ["phase-5c-constellation-cms-mapping"], 60, "Phase 5: Consolidation"),
            ]
            
            registered_count = 0
            categories = {}
            
            for task_id, dependencies, est_minutes, category in constellation_tasks:
                try:
                    task_registry.register_task(
                        task_id=task_id,
                        name=task_id.replace("-", " ").title(),
                        description=f"Constellation elaboration task: {task_id}",
                        dependencies=dependencies,
                        estimated_duration_minutes=est_minutes,
                        category=category,
                        tags=["constellation", "elaboration", category.lower().replace(" ", "_")]
                    )
                    
                    registered_count += 1
                    
                    if category not in categories:
                        categories[category] = 0
                    categories[category] += 1
                    
                    print(f"  ✅ Registered: {task_id} ({est_minutes}min, deps: {len(dependencies)})")
                
                except Exception as e:
                    result["details"]["registration_errors"].append({
                        "task_id": task_id,
                        "error": str(e)
                    })
                    print(f"  ❌ Failed to register {task_id}: {e}")
            
            result["details"]["tasks_registered"] = registered_count
            result["details"]["task_categories"] = categories
            
            # Determine status
            if len(result["details"]["registration_errors"]) == 0:
                result["status"] = "healthy"
                print(f"  ✅ Task Registration: {registered_count} tasks registered successfully")
            else:
                result["status"] = "warning"
                print(f"  ⚠️  Task Registration: {registered_count} tasks registered with {len(result['details']['registration_errors'])} errors")
            
            # Print category summary
            for category, count in categories.items():
                print(f"    - {category}: {count} tasks")
        
        except Exception as e:
            result = {
                "status": "error",
                "details": {
                    "error": f"Unexpected error during task registration: {e}"
                }
            }
            print(f"  ❌ Task Registration: Unexpected error - {e}")
        
        return result
    
    def run_comprehensive_validation(self, final_check: bool = False) -> Dict[str, Any]:
        """Run comprehensive validation of all components"""
        print("🚀 Running Comprehensive Infrastructure Validation")
        print("=" * 80)
        
        validation_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "final_check": final_check,
            "overall_status": "unknown",
            "components": {}
        }
        
        # Run all validations
        validation_results["components"]["beast_mode"] = self.validate_beast_mode_components()
        validation_results["components"]["redis"] = self.validate_redis_connectivity()
        validation_results["components"]["claude_cli"] = self.validate_claude_cli()
        validation_results["components"]["staging_prompts"] = self.validate_staging_prompts()
        validation_results["components"]["environment"] = self.prepare_execution_environment()
        validation_results["components"]["task_registry"] = self.register_constellation_tasks()
        
        # Determine overall status
        component_statuses = [comp.get("status", "error") for comp in validation_results["components"].values()]
        
        if all(status == "healthy" for status in component_statuses):
            validation_results["overall_status"] = "healthy"
            ready_for_execution = True
        elif any(status == "error" for status in component_statuses):
            validation_results["overall_status"] = "error"
            ready_for_execution = False
        else:
            validation_results["overall_status"] = "warning"
            ready_for_execution = not final_check  # Allow execution if not final check
        
        # Update metadata
        try:
            metadata_file = Path(".kiro/execution-metadata.json")
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            metadata.update({
                "infrastructure_validated": True,
                "ready_for_execution": ready_for_execution,
                "last_validation": validation_results["timestamp"],
                "validation_results": validation_results
            })
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        except Exception as e:
            print(f"⚠️  Warning: Could not update metadata file: {e}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 VALIDATION SUMMARY")
        print("=" * 80)
        
        for component, result in validation_results["components"].items():
            status_icon = {
                "healthy": "✅",
                "warning": "⚠️ ",
                "error": "❌",
                "unknown": "❓"
            }.get(result["status"], "❓")
            
            print(f"{status_icon} {component.replace('_', ' ').title()}: {result['status'].upper()}")
        
        print(f"\n🎯 Overall Status: {validation_results['overall_status'].upper()}")
        print(f"🚀 Ready for Execution: {'YES' if ready_for_execution else 'NO'}")
        
        if ready_for_execution:
            print("\n✨ All systems validated! Ready to launch constellation elaboration.")
            print("   Run: python scripts/constellation_orchestrator.py 10")
        else:
            print("\n⚠️  Issues detected. Please resolve before execution:")
            for component, result in validation_results["components"].items():
                if result["status"] in ["error", "warning"]:
                    print(f"   - {component}: {result.get('details', {}).get('error', 'See details above')}")
        
        return validation_results


async def main():
    parser = argparse.ArgumentParser(description="Constellation Execution Preparation")
    parser.add_argument("--final-check", action="store_true", 
                       help="Run final pre-execution validation")
    
    args = parser.parse_args()
    
    preparator = ConstellationPreparator()
    results = preparator.run_comprehensive_validation(final_check=args.final_check)
    
    # Exit with appropriate code
    if results["overall_status"] == "error":
        sys.exit(1)
    elif results["overall_status"] == "warning" and args.final_check:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())