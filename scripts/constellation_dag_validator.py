#!/usr/bin/env python3
"""
Constellation DAG Validator
Validates DAG structure and dependencies for constellation elaboration
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, deque
import logging

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability
from beast_mode.execution.dag_executor import DAGExecutor
from beast_mode.execution.task_registry import TaskRegistry


class ConstellationDAGValidator(ReflectiveModule):
    """Validates DAG structure for constellation elaboration"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ConstellationDAGValidator")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "constellation_dag_validator",
            "name": "Constellation DAG Validator",
            "version": "1.0.0",
            "description": "Validates DAG structure and dependencies for constellation elaboration"
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
            module_id="constellation_dag_validator",
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
    
    def load_constellation_tasks(self) -> Dict[str, Dict]:
        """Load constellation task definitions"""
        tasks = {}
        
        # Define constellation tasks with dependencies
        task_definitions = [
            # Phase 1: Discovery (all parallel)
            ("phase-1a-constellation-inventory", [], 150),
            ("phase-1b-stakeholder-landscape-mapping", [], 120),
            ("phase-1c-cms-dependency-discovery", [], 90),
            ("phase-1d-ontology-gap-analysis", [], 105),
            
            # Phase 2: Requirements (sequential layers)
            ("phase-2-bootstrap-requirements", ["phase-1a-constellation-inventory"], 180),
            ("phase-2-foundation-requirements", ["phase-2-bootstrap-requirements"], 240),
            ("phase-2-intelligence-requirements", ["phase-2-foundation-requirements"], 300),
            ("phase-2-application-requirements", ["phase-2-intelligence-requirements"], 180),
            
            # Phase 3: Design (parallel based on requirements)
            ("phase-3-bootstrap-designs", ["phase-2-bootstrap-requirements"], 150),
            ("phase-3-foundation-designs", ["phase-2-foundation-requirements"], 200),
            ("phase-3-intelligence-designs", ["phase-2-intelligence-requirements"], 250),
            ("phase-3-application-designs", ["phase-2-application-requirements"], 150),
            
            # Phase 4: Tasks (parallel based on designs)
            ("phase-4-bootstrap-tasks", ["phase-3-bootstrap-designs"], 120),
            ("phase-4-foundation-tasks", ["phase-3-foundation-designs"], 160),
            ("phase-4-intelligence-tasks", ["phase-3-intelligence-designs"], 200),
            ("phase-4-application-tasks", ["phase-3-application-designs"], 120),
            
            # Phase 5: Consolidation (sequential)
            ("phase-5a-cms-requirements-consolidation", 
             ["phase-2-bootstrap-requirements", "phase-2-foundation-requirements", 
              "phase-2-intelligence-requirements", "phase-2-application-requirements"], 180),
            ("phase-5b-cms-architecture-update", ["phase-5a-cms-requirements-consolidation"], 120),
            ("phase-5c-constellation-cms-mapping", ["phase-5b-cms-architecture-update"], 90),
            ("phase-5d-stakeholder-validation", ["phase-5c-constellation-cms-mapping"], 60),
        ]
        
        for task_id, dependencies, est_minutes in task_definitions:
            tasks[task_id] = {
                "dependencies": dependencies,
                "estimated_minutes": est_minutes,
                "prompt_file": f"{task_id}.md"
            }
        
        return tasks
    
    def validate_dag_structure(self, tasks: Dict[str, Dict]) -> Dict[str, any]:
        """Validate DAG structure for mathematical correctness"""
        print("🔍 Validating DAG Structure...")
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {},
            "analysis": {}
        }
        
        # 1. Check for missing dependencies
        print("  📋 Checking dependency references...")
        missing_deps = []
        for task_id, task_info in tasks.items():
            for dep in task_info["dependencies"]:
                if dep not in tasks:
                    missing_deps.append(f"Task '{task_id}' depends on non-existent task '{dep}'")
        
        if missing_deps:
            validation_result["valid"] = False
            validation_result["errors"].extend(missing_deps)
            print(f"    ❌ Found {len(missing_deps)} missing dependency references")
        else:
            print("    ✅ All dependency references valid")
        
        # 2. Detect circular dependencies using DFS
        print("  🔄 Checking for circular dependencies...")
        cycles = self._detect_cycles(tasks)
        
        if cycles:
            validation_result["valid"] = False
            for cycle in cycles:
                cycle_str = " → ".join(cycle + [cycle[0]])
                validation_result["errors"].append(f"Circular dependency detected: {cycle_str}")
            print(f"    ❌ Found {len(cycles)} circular dependencies")
        else:
            print("    ✅ No circular dependencies detected")
        
        # 3. Calculate execution levels and parallelization
        print("  📊 Analyzing execution levels...")
        levels = self._calculate_execution_levels(tasks)
        validation_result["analysis"]["execution_levels"] = levels
        
        max_parallel = max(len(tasks_in_level) for tasks_in_level in levels.values()) if levels else 0
        validation_result["statistics"]["max_parallelization"] = max_parallel
        validation_result["statistics"]["total_levels"] = len(levels)
        
        print(f"    📈 Execution levels: {len(levels)}")
        print(f"    🔀 Max parallelization: {max_parallel} tasks")
        
        # 4. Calculate critical path
        print("  🎯 Calculating critical path...")
        critical_path, critical_duration = self._calculate_critical_path(tasks)
        validation_result["analysis"]["critical_path"] = critical_path
        validation_result["statistics"]["critical_path_duration_minutes"] = critical_duration
        
        print(f"    ⏱️  Critical path duration: {critical_duration:.1f} minutes")
        print(f"    🛤️  Critical path: {' → '.join(critical_path)}")
        
        # 5. Calculate parallelization benefits
        print("  ⚡ Analyzing parallelization benefits...")
        sequential_duration = sum(task_info["estimated_minutes"] for task_info in tasks.values())
        parallel_duration = critical_duration
        time_savings = sequential_duration - parallel_duration
        efficiency_gain = (time_savings / sequential_duration) * 100 if sequential_duration > 0 else 0
        
        validation_result["statistics"]["sequential_duration_minutes"] = sequential_duration
        validation_result["statistics"]["parallel_duration_minutes"] = parallel_duration
        validation_result["statistics"]["time_savings_minutes"] = time_savings
        validation_result["statistics"]["efficiency_gain_percent"] = efficiency_gain
        
        print(f"    📏 Sequential execution: {sequential_duration:.1f} minutes ({sequential_duration/60:.1f} hours)")
        print(f"    ⚡ Parallel execution: {parallel_duration:.1f} minutes ({parallel_duration/60:.1f} hours)")
        print(f"    💰 Time savings: {time_savings:.1f} minutes ({efficiency_gain:.1f}% reduction)")
        
        # 6. Validate execution phases
        print("  🎭 Validating execution phases...")
        phase_analysis = self._analyze_phases(tasks, levels)
        validation_result["analysis"]["phases"] = phase_analysis
        
        for phase_name, phase_info in phase_analysis.items():
            print(f"    📋 {phase_name}: {phase_info['task_count']} tasks, {phase_info['duration_minutes']:.1f}min")
        
        # 7. Resource utilization analysis
        print("  📊 Analyzing resource utilization...")
        utilization = self._analyze_resource_utilization(tasks, levels)
        validation_result["analysis"]["resource_utilization"] = utilization
        
        avg_utilization = utilization["average_utilization_percent"]
        print(f"    📈 Average resource utilization: {avg_utilization:.1f}%")
        
        if avg_utilization < 50:
            validation_result["warnings"].append(
                f"Low resource utilization ({avg_utilization:.1f}%) - consider optimizing task dependencies"
            )
        
        return validation_result
    
    def _detect_cycles(self, tasks: Dict[str, Dict]) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        colors = {task_id: 0 for task_id in tasks}  # 0=white, 1=gray, 2=black
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            if colors[node] == 1:  # Gray - cycle detected
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return True
            
            if colors[node] == 2:  # Black - already processed
                return False
            
            colors[node] = 1  # Mark as gray
            
            for dep in tasks[node]["dependencies"]:
                if dep in tasks and dfs(dep, path + [node]):
                    return True
            
            colors[node] = 2  # Mark as black
            return False
        
        for task_id in tasks:
            if colors[task_id] == 0:
                dfs(task_id, [])
        
        return cycles
    
    def _calculate_execution_levels(self, tasks: Dict[str, Dict]) -> Dict[int, List[str]]:
        """Calculate execution levels using topological sort"""
        # Calculate in-degrees
        in_degree = {task_id: 0 for task_id in tasks}
        
        for task_info in tasks.values():
            for dep in task_info["dependencies"]:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Topological sort by levels
        levels = {}
        current_level = 0
        remaining_tasks = set(tasks.keys())
        
        while remaining_tasks:
            # Find tasks with no remaining dependencies
            ready_tasks = [
                task_id for task_id in remaining_tasks 
                if in_degree[task_id] == 0
            ]
            
            if not ready_tasks:
                # Circular dependency - should be caught earlier
                break
            
            levels[current_level] = ready_tasks
            
            # Remove ready tasks and update in-degrees
            for task_id in ready_tasks:
                remaining_tasks.remove(task_id)
                
                # Reduce in-degree for tasks that depend on this one
                for other_task_id, other_task_info in tasks.items():
                    if task_id in other_task_info["dependencies"]:
                        in_degree[other_task_id] -= 1
            
            current_level += 1
        
        return levels
    
    def _calculate_critical_path(self, tasks: Dict[str, Dict]) -> Tuple[List[str], float]:
        """Calculate critical path through the DAG"""
        # Calculate longest path to each task
        longest_paths = {}
        
        def calculate_longest_path(task_id: str) -> float:
            if task_id in longest_paths:
                return longest_paths[task_id]
            
            if task_id not in tasks:
                longest_paths[task_id] = 0
                return 0
            
            task_info = tasks[task_id]
            max_dep_path = 0
            
            for dep in task_info["dependencies"]:
                dep_path = calculate_longest_path(dep)
                max_dep_path = max(max_dep_path, dep_path)
            
            longest_path = max_dep_path + task_info["estimated_minutes"]
            longest_paths[task_id] = longest_path
            return longest_path
        
        # Calculate longest paths for all tasks
        for task_id in tasks:
            calculate_longest_path(task_id)
        
        # Find the task with the longest path (end of critical path)
        critical_end = max(longest_paths.items(), key=lambda x: x[1])
        critical_duration = critical_end[1]
        
        # Trace back the critical path
        critical_path = []
        current = critical_end[0]
        
        while current and current in tasks:
            critical_path.append(current)
            
            # Find the dependency that contributes to the longest path
            task_info = tasks[current]
            next_task = None
            max_path = 0
            
            for dep in task_info["dependencies"]:
                if dep in longest_paths and longest_paths[dep] > max_path:
                    max_path = longest_paths[dep]
                    next_task = dep
            
            current = next_task
        
        critical_path.reverse()
        return critical_path, critical_duration
    
    def _analyze_phases(self, tasks: Dict[str, Dict], levels: Dict[int, List[str]]) -> Dict[str, Dict]:
        """Analyze execution phases"""
        phases = {
            "Phase 1: Discovery": {"tasks": [], "duration_minutes": 0, "task_count": 0},
            "Phase 2: Requirements": {"tasks": [], "duration_minutes": 0, "task_count": 0},
            "Phase 3: Design": {"tasks": [], "duration_minutes": 0, "task_count": 0},
            "Phase 4: Tasks": {"tasks": [], "duration_minutes": 0, "task_count": 0},
            "Phase 5: Consolidation": {"tasks": [], "duration_minutes": 0, "task_count": 0}
        }
        
        for task_id, task_info in tasks.items():
            if task_id.startswith("phase-1"):
                phase = "Phase 1: Discovery"
            elif task_id.startswith("phase-2"):
                phase = "Phase 2: Requirements"
            elif task_id.startswith("phase-3"):
                phase = "Phase 3: Design"
            elif task_id.startswith("phase-4"):
                phase = "Phase 4: Tasks"
            elif task_id.startswith("phase-5"):
                phase = "Phase 5: Consolidation"
            else:
                continue
            
            phases[phase]["tasks"].append(task_id)
            phases[phase]["duration_minutes"] += task_info["estimated_minutes"]
            phases[phase]["task_count"] += 1
        
        return phases
    
    def _analyze_resource_utilization(self, tasks: Dict[str, Dict], levels: Dict[int, List[str]]) -> Dict[str, any]:
        """Analyze resource utilization across execution levels"""
        if not levels:
            return {"average_utilization_percent": 0, "level_utilization": []}
        
        max_parallel = max(len(tasks_in_level) for tasks_in_level in levels.values())
        level_utilization = []
        
        for level, tasks_in_level in levels.items():
            utilization = (len(tasks_in_level) / max_parallel) * 100 if max_parallel > 0 else 0
            level_utilization.append({
                "level": level,
                "tasks": len(tasks_in_level),
                "utilization_percent": utilization
            })
        
        avg_utilization = sum(lu["utilization_percent"] for lu in level_utilization) / len(level_utilization)
        
        return {
            "average_utilization_percent": avg_utilization,
            "max_parallel_tasks": max_parallel,
            "level_utilization": level_utilization
        }
    
    def validate_prompt_files(self, tasks: Dict[str, Dict]) -> Dict[str, any]:
        """Validate that prompt files exist for all tasks"""
        print("📁 Validating Prompt Files...")
        
        staging_dir = Path("prompts/staging")
        result = {
            "valid": True,
            "missing_files": [],
            "accessible_files": [],
            "file_sizes": {}
        }
        
        for task_id, task_info in tasks.items():
            prompt_file = staging_dir / task_info["prompt_file"]
            
            if not prompt_file.exists():
                result["valid"] = False
                result["missing_files"].append(task_info["prompt_file"])
                print(f"    ❌ Missing: {task_info['prompt_file']}")
            else:
                try:
                    file_size = prompt_file.stat().st_size
                    result["accessible_files"].append(task_info["prompt_file"])
                    result["file_sizes"][task_info["prompt_file"]] = file_size
                    
                    if file_size == 0:
                        result["valid"] = False
                        print(f"    ⚠️  Empty file: {task_info['prompt_file']}")
                    else:
                        print(f"    ✅ Found: {task_info['prompt_file']} ({file_size} bytes)")
                
                except Exception as e:
                    result["valid"] = False
                    result["missing_files"].append(task_info["prompt_file"])
                    print(f"    ❌ Error accessing {task_info['prompt_file']}: {e}")
        
        print(f"  📊 Summary: {len(result['accessible_files'])}/{len(tasks)} files accessible")
        
        return result
    
    def run_comprehensive_validation(self) -> Dict[str, any]:
        """Run comprehensive DAG validation"""
        print("🚀 Running Comprehensive DAG Validation")
        print("=" * 80)
        
        validation_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_valid": True,
            "components": {}
        }
        
        # Load tasks
        tasks = self.load_constellation_tasks()
        print(f"📋 Loaded {len(tasks)} constellation tasks")
        
        # Validate DAG structure
        dag_validation = self.validate_dag_structure(tasks)
        validation_results["components"]["dag_structure"] = dag_validation
        
        if not dag_validation["valid"]:
            validation_results["overall_valid"] = False
        
        # Validate prompt files
        file_validation = self.validate_prompt_files(tasks)
        validation_results["components"]["prompt_files"] = file_validation
        
        if not file_validation["valid"]:
            validation_results["overall_valid"] = False
        
        # Test with DAG Executor
        print("\n🔧 Testing with DAG Executor...")
        try:
            dag_executor = DAGExecutor(max_concurrent=10)
            
            # Add tasks to executor
            for task_id, task_info in tasks.items():
                dag_executor.add_task(
                    task_id=task_id,
                    dependencies=task_info["dependencies"]
                )
            
            # Validate with executor
            executor_validation = dag_executor.validate_dag()
            validation_results["components"]["dag_executor"] = executor_validation
            
            if not executor_validation["valid"]:
                validation_results["overall_valid"] = False
                print("    ❌ DAG Executor validation failed")
            else:
                print("    ✅ DAG Executor validation passed")
        
        except Exception as e:
            validation_results["components"]["dag_executor"] = {
                "valid": False,
                "errors": [f"DAG Executor test failed: {e}"]
            }
            validation_results["overall_valid"] = False
            print(f"    ❌ DAG Executor test failed: {e}")
        
        # Save validation results
        try:
            results_file = Path(".kiro/dag-validation-results.json")
            with open(results_file, 'w') as f:
                json.dump(validation_results, f, indent=2)
            print(f"\n💾 Validation results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save validation results: {e}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 DAG VALIDATION SUMMARY")
        print("=" * 80)
        
        if validation_results["overall_valid"]:
            print("✅ DAG VALIDATION PASSED")
            print("🚀 DAG is mathematically valid and ready for execution")
            
            # Print key statistics
            dag_stats = dag_validation.get("statistics", {})
            print(f"\n📈 Key Statistics:")
            print(f"   • Total tasks: {len(tasks)}")
            print(f"   • Execution levels: {dag_stats.get('total_levels', 'N/A')}")
            print(f"   • Max parallelization: {dag_stats.get('max_parallelization', 'N/A')} tasks")
            print(f"   • Critical path: {dag_stats.get('critical_path_duration_minutes', 0):.1f} minutes")
            print(f"   • Time savings: {dag_stats.get('efficiency_gain_percent', 0):.1f}% reduction")
        else:
            print("❌ DAG VALIDATION FAILED")
            print("🛑 Issues must be resolved before execution")
            
            # Print errors
            for component, result in validation_results["components"].items():
                if not result.get("valid", True):
                    print(f"\n❌ {component.replace('_', ' ').title()} Issues:")
                    for error in result.get("errors", []):
                        print(f"   • {error}")
        
        return validation_results


async def main():
    parser = argparse.ArgumentParser(description="Constellation DAG Validator")
    parser.add_argument("--comprehensive", action="store_true", 
                       help="Run comprehensive validation including file checks")
    
    args = parser.parse_args()
    
    validator = ConstellationDAGValidator()
    results = validator.run_comprehensive_validation()
    
    # Exit with appropriate code
    if not results["overall_valid"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())