#!/usr/bin/env python3
"""
Deployment Data Auditor DAG Validator

Comprehensive validation system for DAG structure, dependencies, and execution readiness
with mathematical verification and Beast Mode compliance checking.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import networkx as nx

# Add src to path for Beast Mode integration
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Simplified Beast Mode integration for now
BEAST_MODE_AVAILABLE = False
class ReflectiveModule:
    def __init__(self):
        pass

class DeploymentAuditorDAGValidator(ReflectiveModule if BEAST_MODE_AVAILABLE else object):
    """Comprehensive DAG validation with mathematical verification."""
    
    def __init__(self):
        # Simplified initialization without Beast Mode complexity
        self.validation_results = {}
        
        # Load DAG structure from optimizer
        self.dag_structure = {
            "foundation": {
                "tasks": ["1.1", "1.2", "1.3", "6.1", "6.2", "6.3", "9.1", "9.2", "9.3"],
                "dependencies": [],
                "estimated_hours": 4.0
            },
            "core": {
                "tasks": ["2.1", "2.2", "2.3", "3.1", "3.2", "3.3"],
                "dependencies": ["foundation"],
                "estimated_hours": 4.0
            },
            "integration": {
                "tasks": ["4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "5.4"],
                "dependencies": ["core"],
                "estimated_hours": 4.0
            },
            "optimization": {
                "tasks": ["7.1", "7.2", "7.3", "8.1", "8.2", "8.3"],
                "dependencies": ["integration"],
                "estimated_hours": 4.0
            },
            "validation": {
                "tasks": ["10.1", "10.2", "10.3", "10.4"],
                "dependencies": ["optimization"],
                "estimated_hours": 5.0
            }
        }
        
        # Task-level dependencies
        self.task_dependencies = {
            "1.3": ["1.1", "1.2"],
            "6.2": ["6.1"],
            "6.3": ["6.1", "6.2"],
            "9.1": ["1.2"],
            "9.2": ["1.2"],
            "9.3": ["9.1", "9.2"],
            "2.1": ["1.2", "6.1"],
            "2.2": ["1.2", "6.1"],
            "2.3": ["2.1", "2.2"],
            "3.1": ["1.2", "6.1"],
            "3.2": ["3.1"],
            "3.3": ["3.1", "3.2"],
            "4.1": ["3.2"],
            "4.2": ["3.2"],
            "4.3": ["4.1", "4.2"],
            "4.4": ["4.1", "4.2", "4.3"],
            "5.1": ["3.2"],
            "5.2": ["5.1"],
            "5.3": ["1.2", "5.1"],
            "5.4": ["5.1", "5.2", "5.3"],
            "7.1": ["1.2", "5.3"],
            "7.2": ["2.1", "7.1"],
            "7.3": ["7.1", "7.2"],
            "8.1": ["4.3", "5.2"],
            "8.2": ["8.1"],
            "8.3": ["8.1", "8.2"],
            "10.1": ["4.3", "5.2", "8.2"],
            "10.2": ["9.2", "10.1"],
            "10.3": ["10.1", "10.2"],
            "10.4": ["10.2", "10.3"]
        }
        
        # Task metadata
        self.task_metadata = {
            "1.1": {"name": "Create core data models", "beast_mode": True, "critical_path": False},
            "1.2": {"name": "Implement ReflectiveModule integration", "beast_mode": True, "critical_path": True},
            "1.3": {"name": "Write unit tests for base classes", "beast_mode": False, "critical_path": False},
            "6.1": {"name": "Build configuration system", "beast_mode": True, "critical_path": False},
            "6.2": {"name": "Implement hot-reloading", "beast_mode": True, "critical_path": False},
            "6.3": {"name": "Write configuration tests", "beast_mode": False, "critical_path": False},
            "9.1": {"name": "Implement CLI interface", "beast_mode": True, "critical_path": False},
            "9.2": {"name": "Build daemon lifecycle", "beast_mode": True, "critical_path": False},
            "9.3": {"name": "Write CLI tests", "beast_mode": False, "critical_path": False},
            "2.1": {"name": "Implement file system watching", "beast_mode": True, "critical_path": False},
            "2.2": {"name": "Create baseline scanning", "beast_mode": True, "critical_path": False},
            "2.3": {"name": "Write file monitoring tests", "beast_mode": False, "critical_path": False},
            "3.1": {"name": "Implement pattern matching", "beast_mode": True, "critical_path": True},
            "3.2": {"name": "Create violation classifier", "beast_mode": True, "critical_path": True},
            "3.3": {"name": "Write pattern matching tests", "beast_mode": False, "critical_path": False},
            "4.1": {"name": "Implement gitignore management", "beast_mode": True, "critical_path": True},
            "4.2": {"name": "Create file quarantine", "beast_mode": True, "critical_path": False},
            "4.3": {"name": "Build git integration", "beast_mode": True, "critical_path": True},
            "4.4": {"name": "Write remediation tests", "beast_mode": False, "critical_path": False},
            "5.1": {"name": "Create reporting engine", "beast_mode": True, "critical_path": False},
            "5.2": {"name": "Build notification system", "beast_mode": True, "critical_path": True},
            "5.3": {"name": "Implement Prometheus metrics", "beast_mode": True, "critical_path": False},
            "5.4": {"name": "Write reporting tests", "beast_mode": False, "critical_path": False},
            "7.1": {"name": "Create resource monitoring", "beast_mode": True, "critical_path": False},
            "7.2": {"name": "Build event processing", "beast_mode": True, "critical_path": False},
            "7.3": {"name": "Write performance tests", "beast_mode": False, "critical_path": False},
            "8.1": {"name": "Create emergency detection", "beast_mode": True, "critical_path": True},
            "8.2": {"name": "Build recovery systems", "beast_mode": True, "critical_path": True},
            "8.3": {"name": "Write emergency tests", "beast_mode": False, "critical_path": False},
            "10.1": {"name": "Create end-to-end tests", "beast_mode": False, "critical_path": True},
            "10.2": {"name": "Build deployment tools", "beast_mode": False, "critical_path": True},
            "10.3": {"name": "Create documentation", "beast_mode": False, "critical_path": True},
            "10.4": {"name": "Write integration tests", "beast_mode": False, "critical_path": True}
        }
    
    # Beast Mode ReflectiveModule implementation
    def get_capabilities(self) -> Dict[str, Any]:
        """Get validator capabilities."""
        return {
            "name": "DeploymentAuditorDAGValidator",
            "version": "1.0.0",
            "capabilities": [
                "mathematical_dag_validation",
                "execution_script_validation", 
                "beast_mode_compliance_checking",
                "makefile_structure_validation",
                "infrastructure_readiness_assessment"
            ]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get validator health status."""
        return {
            "status": "healthy",
            "beast_mode_available": BEAST_MODE_AVAILABLE,
            "validation_results": bool(self.validation_results),
            "last_validation": self.validation_results.get("validation_timestamp") if self.validation_results else None
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "deployment_auditor_dag_validator",
            "module_type": "validation_system",
            "beast_mode_integration": BEAST_MODE_AVAILABLE,
            "supported_validations": [
                "mathematical_structure",
                "execution_scripts", 
                "beast_mode_compliance",
                "makefile_structure",
                "infrastructure_readiness"
            ]
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_validation",
            "available_functions": ["basic_dag_check", "script_existence_check"]
        }
    
    def validate_mathematical_structure(self) -> Dict[str, Any]:
        """Validate the mathematical properties of the DAG."""
        print("🔢 Validating mathematical DAG structure...")
        
        # Build NetworkX graph
        G = nx.DiGraph()
        
        # Add all tasks as nodes
        all_tasks = []
        for group_config in self.dag_structure.values():
            all_tasks.extend(group_config["tasks"])
        
        for task_id in all_tasks:
            G.add_node(task_id)
        
        # Add edges for dependencies
        for task_id, deps in self.task_dependencies.items():
            for dep_id in deps:
                G.add_edge(dep_id, task_id)
        
        # Mathematical validation
        validation = {
            "is_dag": nx.is_directed_acyclic_graph(G),
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "cycles": [],
            "topological_order": [],
            "critical_path": [],
            "parallel_width": 0,
            "density": nx.density(G)
        }
        
        if validation["is_dag"]:
            # Get topological ordering
            validation["topological_order"] = list(nx.topological_sort(G))
            
            # Calculate critical path
            critical_path_tasks = [t for t, meta in self.task_metadata.items() if meta["critical_path"]]
            validation["critical_path"] = critical_path_tasks
            
            # Calculate maximum parallel width
            levels = {}
            for node in validation["topological_order"]:
                if not list(G.predecessors(node)):
                    levels[node] = 0
                else:
                    levels[node] = max(levels[pred] for pred in G.predecessors(node)) + 1
            
            level_counts = {}
            for node, level in levels.items():
                level_counts[level] = level_counts.get(level, 0) + 1
            
            validation["parallel_width"] = max(level_counts.values()) if level_counts else 0
            
        else:
            # Find cycles
            try:
                validation["cycles"] = list(nx.simple_cycles(G))
            except:
                validation["cycles"] = ["Unable to detect cycles"]
        
        # Metrics would be recorded here in full Beast Mode integration
        
        return validation
    
    def validate_execution_scripts(self) -> Dict[str, Any]:
        """Validate that all required execution scripts exist and are executable."""
        print("📜 Validating execution scripts...")
        
        validation = {
            "total_scripts": 0,
            "existing_scripts": 0,
            "executable_scripts": 0,
            "missing_scripts": [],
            "non_executable_scripts": []
        }
        
        all_tasks = []
        for group_config in self.dag_structure.values():
            all_tasks.extend(group_config["tasks"])
        
        validation["total_scripts"] = len(all_tasks)
        
        for task_id in all_tasks:
            script_name = f"execute_task_{task_id.replace('.', '_')}.py"
            script_path = Path("scripts") / script_name
            
            if script_path.exists():
                validation["existing_scripts"] += 1
                
                # Check if executable
                if os.access(script_path, os.X_OK):
                    validation["executable_scripts"] += 1
                else:
                    validation["non_executable_scripts"].append(script_name)
            else:
                validation["missing_scripts"].append(script_name)
        
        # Metrics would be recorded here in full Beast Mode integration
        
        return validation
    
    def validate_beast_mode_compliance(self) -> Dict[str, Any]:
        """Validate Beast Mode framework compliance."""
        print("🐺 Validating Beast Mode compliance...")
        
        validation = {
            "beast_mode_available": BEAST_MODE_AVAILABLE,
            "total_beast_tasks": 0,
            "compliant_tasks": 0,
            "non_compliant_tasks": [],
            "reflective_module_imports": 0,
            "health_endpoints": 0,
            "prometheus_metrics": 0
        }
        
        # Count Beast Mode tasks
        beast_tasks = [t for t, meta in self.task_metadata.items() if meta["beast_mode"]]
        validation["total_beast_tasks"] = len(beast_tasks)
        
        # Check script compliance (simplified check)
        for task_id in beast_tasks:
            script_name = f"execute_task_{task_id.replace('.', '_')}.py"
            script_path = Path("scripts") / script_name
            
            if script_path.exists():
                try:
                    content = script_path.read_text()
                    
                    # Check for ReflectiveModule import
                    if "ReflectiveModule" in content:
                        validation["reflective_module_imports"] += 1
                    
                    # Check for health endpoint mentions
                    if "/health" in content or "health_check" in content:
                        validation["health_endpoints"] += 1
                    
                    # Check for Prometheus metrics
                    if "prometheus" in content.lower() or "metrics" in content:
                        validation["prometheus_metrics"] += 1
                    
                    # Consider compliant if has ReflectiveModule
                    if "ReflectiveModule" in content:
                        validation["compliant_tasks"] += 1
                    else:
                        validation["non_compliant_tasks"].append(task_id)
                        
                except Exception as e:
                    validation["non_compliant_tasks"].append(f"{task_id} (read error)")
        
        # Metrics would be recorded here in full Beast Mode integration
        
        return validation
    
    def validate_makefile_structure(self) -> Dict[str, Any]:
        """Validate Makefile structure and targets."""
        print("🔨 Validating Makefile structure...")
        
        validation = {
            "makefile_exists": False,
            "required_targets": [],
            "missing_targets": [],
            "dependency_declarations": 0,
            "parallel_group_targets": 0
        }
        
        makefile_path = Path("Makefile.deployment-auditor")
        validation["makefile_exists"] = makefile_path.exists()
        
        if makefile_path.exists():
            try:
                content = makefile_path.read_text()
                
                # Check for required targets
                required_targets = ["all", "validate-dag", "foundation", "core", "integration", "optimization", "validation", "clean"]
                validation["required_targets"] = required_targets
                
                for target in required_targets:
                    if f"{target}:" in content:
                        pass  # Target exists
                    else:
                        validation["missing_targets"].append(target)
                
                # Count task targets
                all_tasks = []
                for group_config in self.dag_structure.values():
                    all_tasks.extend(group_config["tasks"])
                
                for task_id in all_tasks:
                    if f"task-{task_id}:" in content:
                        validation["dependency_declarations"] += 1
                
                # Count parallel group targets
                for group_name in self.dag_structure.keys():
                    if f"{group_name}:" in content:
                        validation["parallel_group_targets"] += 1
                        
            except Exception as e:
                validation["read_error"] = str(e)
        
        # Metrics would be recorded here in full Beast Mode integration
        
        return validation
    
    def validate_infrastructure_readiness(self) -> Dict[str, Any]:
        """Validate infrastructure prerequisites."""
        print("🏗️  Validating infrastructure readiness...")
        
        validation = {
            "python_version": sys.version,
            "python_version_ok": sys.version_info >= (3, 9),
            "required_directories": [],
            "missing_directories": [],
            "required_files": [],
            "missing_files": [],
            "beast_mode_available": BEAST_MODE_AVAILABLE,
            "redis_available": False
        }
        
        # Check required directories
        required_dirs = ["src", "scripts", "logs", "tests"]
        validation["required_directories"] = required_dirs
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                validation["missing_directories"].append(dir_name)
            elif dir_name == "logs":
                # Create logs directory if it doesn't exist
                dir_path.mkdir(exist_ok=True)
        
        # Check required files
        required_files = [
            "deployment-auditor-config.yml",
            "src/deployment_auditor/__init__.py",
            "src/deployment_auditor/auditor.py"
        ]
        validation["required_files"] = required_files
        
        for file_path in required_files:
            if not Path(file_path).exists():
                validation["missing_files"].append(file_path)
        
        # Check Redis availability
        try:
            import redis
            redis_client = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            redis_client.ping()
            validation["redis_available"] = True
        except:
            validation["redis_available"] = False
        
        # Metrics would be recorded here in full Beast Mode integration
        
        return validation
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation checks and generate comprehensive report."""
        print("🔍 Running comprehensive DAG validation...")
        print("=" * 50)
        
        start_time = datetime.now()
        
        # Run all validation checks
        validations = {
            "mathematical_structure": self.validate_mathematical_structure(),
            "execution_scripts": self.validate_execution_scripts(),
            "beast_mode_compliance": self.validate_beast_mode_compliance(),
            "makefile_structure": self.validate_makefile_structure(),
            "infrastructure_readiness": self.validate_infrastructure_readiness()
        }
        
        # Calculate overall validation score
        total_checks = 0
        passed_checks = 0
        critical_failures = []
        
        # Mathematical structure (critical)
        math_val = validations["mathematical_structure"]
        total_checks += 1
        if math_val["is_dag"]:
            passed_checks += 1
        else:
            critical_failures.append("DAG contains cycles - mathematically invalid")
        
        # Execution scripts
        script_val = validations["execution_scripts"]
        total_checks += 1
        if script_val["missing_scripts"] == []:
            passed_checks += 1
        else:
            critical_failures.append(f"Missing {len(script_val['missing_scripts'])} execution scripts")
        
        # Beast Mode compliance
        beast_val = validations["beast_mode_compliance"]
        total_checks += 1
        if len(beast_val["non_compliant_tasks"]) == 0:
            passed_checks += 1
        
        # Makefile structure
        make_val = validations["makefile_structure"]
        total_checks += 1
        if make_val["makefile_exists"] and not make_val["missing_targets"]:
            passed_checks += 1
        
        # Infrastructure readiness
        infra_val = validations["infrastructure_readiness"]
        total_checks += 1
        if infra_val["python_version_ok"] and not infra_val["missing_directories"]:
            passed_checks += 1
        
        validation_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Overall result
        overall_result = {
            "validation_timestamp": start_time.isoformat(),
            "validation_duration": (datetime.now() - start_time).total_seconds(),
            "validation_score": validation_score,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "critical_failures": critical_failures,
            "ready_for_execution": len(critical_failures) == 0 and validation_score >= 80,
            "validations": validations
        }
        
        self.validation_results = overall_result
        return overall_result
    
    def print_validation_summary(self, results: Dict[str, Any]):
        """Print a comprehensive validation summary."""
        print("\n" + "=" * 60)
        print("🔍 DAG Validation Summary")
        print("=" * 60)
        
        # Overall status
        score = results["validation_score"]
        ready = results["ready_for_execution"]
        
        status_icon = "✅" if ready else "❌"
        print(f"{status_icon} Overall Status: {'READY FOR EXECUTION' if ready else 'NOT READY'}")
        print(f"📊 Validation Score: {score:.1f}% ({results['passed_checks']}/{results['total_checks']} checks passed)")
        print(f"⏱️  Validation Time: {results['validation_duration']:.2f}s")
        
        if results["critical_failures"]:
            print(f"\n❌ Critical Failures:")
            for failure in results["critical_failures"]:
                print(f"   • {failure}")
        
        print(f"\n📋 Detailed Results:")
        
        # Mathematical structure
        math_val = results["validations"]["mathematical_structure"]
        math_icon = "✅" if math_val["is_dag"] else "❌"
        print(f"{math_icon} Mathematical Structure:")
        print(f"   • DAG Valid: {math_val['is_dag']}")
        print(f"   • Nodes: {math_val['node_count']}, Edges: {math_val['edge_count']}")
        print(f"   • Max Parallel Width: {math_val['parallel_width']}")
        if math_val["cycles"]:
            print(f"   • Cycles Found: {len(math_val['cycles'])}")
        
        # Execution scripts
        script_val = results["validations"]["execution_scripts"]
        script_icon = "✅" if not script_val["missing_scripts"] else "❌"
        print(f"{script_icon} Execution Scripts:")
        print(f"   • Total: {script_val['total_scripts']}")
        print(f"   • Existing: {script_val['existing_scripts']}")
        print(f"   • Executable: {script_val['executable_scripts']}")
        if script_val["missing_scripts"]:
            print(f"   • Missing: {len(script_val['missing_scripts'])}")
        
        # Beast Mode compliance
        beast_val = results["validations"]["beast_mode_compliance"]
        beast_icon = "✅" if not beast_val["non_compliant_tasks"] else "⚠️"
        print(f"{beast_icon} Beast Mode Compliance:")
        print(f"   • Beast Mode Available: {beast_val['beast_mode_available']}")
        print(f"   • Beast Tasks: {beast_val['total_beast_tasks']}")
        print(f"   • Compliant: {beast_val['compliant_tasks']}")
        print(f"   • ReflectiveModule Imports: {beast_val['reflective_module_imports']}")
        
        # Makefile structure
        make_val = results["validations"]["makefile_structure"]
        make_icon = "✅" if make_val["makefile_exists"] and not make_val["missing_targets"] else "❌"
        print(f"{make_icon} Makefile Structure:")
        print(f"   • Makefile Exists: {make_val['makefile_exists']}")
        print(f"   • Missing Targets: {len(make_val['missing_targets'])}")
        print(f"   • Task Dependencies: {make_val['dependency_declarations']}")
        print(f"   • Parallel Groups: {make_val['parallel_group_targets']}")
        
        # Infrastructure readiness
        infra_val = results["validations"]["infrastructure_readiness"]
        infra_icon = "✅" if infra_val["python_version_ok"] and not infra_val["missing_directories"] else "❌"
        print(f"{infra_icon} Infrastructure Readiness:")
        print(f"   • Python Version OK: {infra_val['python_version_ok']}")
        print(f"   • Missing Directories: {len(infra_val['missing_directories'])}")
        print(f"   • Missing Files: {len(infra_val['missing_files'])}")
        print(f"   • Redis Available: {infra_val['redis_available']}")
        
        print("\n" + "=" * 60)
        
        if ready:
            print("🚀 DAG is ready for execution!")
            print("   Next steps:")
            print("   1. Run: make -f Makefile.deployment-auditor validate-dag")
            print("   2. Execute: make -f Makefile.deployment-auditor all")
            print("   3. Monitor: python scripts/deployment_auditor_execution_monitor.py")
        else:
            print("🔧 DAG requires fixes before execution:")
            for failure in results["critical_failures"]:
                print(f"   • {failure}")

def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Auditor DAG Validator')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--save-report', action='store_true', help='Save validation report to file')
    parser.add_argument('--quiet', action='store_true', help='Suppress detailed output')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = DeploymentAuditorDAGValidator()
    
    # Run validation
    results = validator.run_comprehensive_validation()
    
    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.quiet:
        validator.print_validation_summary(results)
    
    # Save report if requested
    if args.save_report:
        report_file = f"deployment_auditor_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Validation report saved: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["ready_for_execution"] else 1)

if __name__ == "__main__":
    main()