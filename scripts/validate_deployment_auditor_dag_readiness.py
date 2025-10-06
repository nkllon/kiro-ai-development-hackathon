#!/usr/bin/env python3
"""
Deployment Auditor DAG Readiness Validator
==========================================

Validates that the deployment auditor DAG is ready for execution by checking
all prerequisites, dependencies, and system requirements.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple


class DeploymentAuditorDAGValidator:
    """
    Comprehensive validator for deployment auditor DAG execution readiness.
    """
    
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {},
            "recommendations": [],
            "blocking_issues": [],
            "warnings": []
        }
        
    def validate_file_structure(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate required file structure exists."""
        print("🔍 Validating File Structure...")
        
        required_files = [
            "src/deployment_auditor/core.py",
            "src/deployment_auditor/cli.py",
            "src/deployment_auditor/models.py", 
            "src/deployment_auditor/auditor.py",
            "src/deployment_auditor/api.py",
            "deployment-auditor-config.yml",
            "deployment_auditor_dag_specification.json"
        ]
        
        optional_files = [
            "src/deployment_auditor/__main__.py",
            "src/deployment_auditor/config.py",
            "tests/unit/deployment_auditor/"
        ]
        
        file_status = {}
        missing_required = []
        missing_optional = []
        
        for file_path in required_files:
            exists = Path(file_path).exists()
            file_status[file_path] = {"exists": exists, "required": True}
            if exists:
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} (REQUIRED)")
                missing_required.append(file_path)
        
        for file_path in optional_files:
            exists = Path(file_path).exists()
            file_status[file_path] = {"exists": exists, "required": False}
            if exists:
                print(f"   ✅ {file_path}")
            else:
                print(f"   ⚠️  {file_path} (optional)")
                missing_optional.append(file_path)
        
        success = len(missing_required) == 0
        
        result = {
            "success": success,
            "file_status": file_status,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "total_files_checked": len(required_files) + len(optional_files),
            "required_files_found": len(required_files) - len(missing_required)
        }
        
        if not success:
            self.validation_results["blocking_issues"].extend([
                f"Missing required file: {f}" for f in missing_required
            ])
        
        if missing_optional:
            self.validation_results["warnings"].extend([
                f"Missing optional file: {f}" for f in missing_optional
            ])
        
        return success, result
    
    def validate_python_environment(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate Python environment and imports."""
        print("\n🐍 Validating Python Environment...")
        
        # Check Python version
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            python_version = result.stdout.strip()
            print(f"   ✅ Python Version: {python_version}")
        except Exception as e:
            python_version = f"Error: {e}"
            print(f"   ❌ Python Version: {e}")
        
        # Test critical imports
        import_tests = [
            ("ReflectiveModule", "from src.rm_ddd.core.unified_reflective_module import ReflectiveModule"),
            ("DeploymentAuditor", "from src.deployment_auditor.core import DeploymentAuditor"),
            ("DAG Orchestration", "from src.dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine")
        ]
        
        import_results = {}
        failed_imports = []
        
        for name, import_statement in import_tests:
            try:
                exec(import_statement)
                import_results[name] = {"success": True, "error": None}
                print(f"   ✅ {name}: Import successful")
            except Exception as e:
                import_results[name] = {"success": False, "error": str(e)}
                print(f"   ❌ {name}: Import failed - {e}")
                failed_imports.append(name)
        
        success = len(failed_imports) == 0
        
        result = {
            "success": success,
            "python_version": python_version,
            "import_results": import_results,
            "failed_imports": failed_imports
        }
        
        if failed_imports:
            self.validation_results["blocking_issues"].extend([
                f"Failed import: {name}" for name in failed_imports
            ])
        
        return success, result
    
    def validate_dag_specification(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate DAG specification file."""
        print("\n📋 Validating DAG Specification...")
        
        spec_file = Path("deployment_auditor_dag_specification.json")
        
        if not spec_file.exists():
            print("   ❌ DAG specification file not found")
            self.validation_results["blocking_issues"].append("DAG specification file missing")
            return False, {"success": False, "error": "Specification file not found"}
        
        try:
            with open(spec_file, 'r') as f:
                dag_spec = json.load(f)
            
            print("   ✅ DAG specification file loaded successfully")
            
            # Validate required fields
            required_fields = ["dag_id", "tasks", "parallel_execution_groups"]
            missing_fields = []
            
            for field in required_fields:
                if field not in dag_spec:
                    missing_fields.append(field)
                    print(f"   ❌ Missing required field: {field}")
                else:
                    print(f"   ✅ Required field present: {field}")
            
            # Validate task structure
            tasks = dag_spec.get("tasks", [])
            task_validation = self._validate_task_definitions(tasks)
            
            success = len(missing_fields) == 0 and task_validation["valid"]
            
            result = {
                "success": success,
                "dag_spec": dag_spec,
                "missing_fields": missing_fields,
                "task_count": len(tasks),
                "task_validation": task_validation
            }
            
            if missing_fields:
                self.validation_results["blocking_issues"].extend([
                    f"Missing DAG field: {field}" for field in missing_fields
                ])
            
            return success, result
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON in DAG specification: {e}")
            self.validation_results["blocking_issues"].append(f"Invalid DAG specification JSON: {e}")
            return False, {"success": False, "error": f"JSON decode error: {e}"}
        except Exception as e:
            print(f"   ❌ Error loading DAG specification: {e}")
            self.validation_results["blocking_issues"].append(f"DAG specification error: {e}")
            return False, {"success": False, "error": str(e)}
    
    def _validate_task_definitions(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate individual task definitions."""
        print("   🔍 Validating task definitions...")
        
        required_task_fields = ["task_id", "dependencies", "estimated_duration_minutes"]
        task_issues = []
        valid_tasks = 0
        
        for i, task in enumerate(tasks):
            task_id = task.get("task_id", f"task_{i}")
            missing_fields = []
            
            for field in required_task_fields:
                if field not in task:
                    missing_fields.append(field)
            
            if missing_fields:
                issue = f"Task {task_id} missing fields: {missing_fields}"
                task_issues.append(issue)
                print(f"      ❌ {issue}")
            else:
                valid_tasks += 1
                print(f"      ✅ Task {task_id}: Valid")
        
        return {
            "valid": len(task_issues) == 0,
            "total_tasks": len(tasks),
            "valid_tasks": valid_tasks,
            "issues": task_issues
        }
    
    def validate_system_resources(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate system resources and dependencies."""
        print("\n💻 Validating System Resources...")
        
        # Check disk space
        try:
            result = subprocess.run(["df", "-h", "."], capture_output=True, text=True)
            disk_info = result.stdout.split('\n')[1] if result.returncode == 0 else "Unknown"
            print(f"   ✅ Disk Space: {disk_info}")
        except Exception as e:
            disk_info = f"Error: {e}"
            print(f"   ⚠️  Disk Space: {e}")
        
        # Check if Kiro CLI is available
        kiro_available = False
        try:
            result = subprocess.run(["which", "kiro"], capture_output=True, text=True)
            if result.returncode == 0:
                kiro_path = result.stdout.strip()
                kiro_available = True
                print(f"   ✅ Kiro CLI: Available at {kiro_path}")
            else:
                print("   ❌ Kiro CLI: Not found in PATH")
        except Exception as e:
            print(f"   ❌ Kiro CLI: Error checking - {e}")
        
        # Check log directory permissions
        log_dir = Path("logs")
        log_writable = False
        try:
            log_dir.mkdir(exist_ok=True)
            test_file = log_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            log_writable = True
            print("   ✅ Log Directory: Writable")
        except Exception as e:
            print(f"   ❌ Log Directory: Not writable - {e}")
        
        success = kiro_available and log_writable
        
        result = {
            "success": success,
            "disk_info": disk_info,
            "kiro_available": kiro_available,
            "log_writable": log_writable
        }
        
        if not kiro_available:
            self.validation_results["blocking_issues"].append("Kiro CLI not available")
        
        if not log_writable:
            self.validation_results["blocking_issues"].append("Log directory not writable")
        
        return success, result
    
    def validate_deployment_auditor_current_state(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate current state of deployment auditor system."""
        print("\n🔧 Validating Deployment Auditor Current State...")
        
        # Test basic import
        import_works = False
        try:
            exec("from src.deployment_auditor.core import DeploymentAuditor")
            import_works = True
            print("   ✅ DeploymentAuditor: Import successful")
        except Exception as e:
            print(f"   ❌ DeploymentAuditor: Import failed - {e}")
        
        # Test CLI module access
        cli_works = False
        try:
            result = subprocess.run([
                sys.executable, "-c", 
                "import sys; sys.path.insert(0, 'src'); import deployment_auditor"
            ], capture_output=True, text=True)
            if result.returncode == 0:
                cli_works = True
                print("   ✅ CLI Module: Import successful")
            else:
                print(f"   ❌ CLI Module: Import failed - {result.stderr}")
        except Exception as e:
            print(f"   ❌ CLI Module: Error testing - {e}")
        
        # Test scanner functionality
        scanner_works = False
        scanner_script = Path("scripts/deployment_auditor_scan.py")
        if scanner_script.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(scanner_script), "--help"
                ], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    scanner_works = True
                    print("   ✅ Scanner Script: Functional")
                else:
                    print(f"   ❌ Scanner Script: Failed - {result.stderr}")
            except Exception as e:
                print(f"   ❌ Scanner Script: Error testing - {e}")
        else:
            print("   ⚠️  Scanner Script: Not found")
        
        success = import_works  # Minimum requirement
        
        result = {
            "success": success,
            "import_works": import_works,
            "cli_works": cli_works,
            "scanner_works": scanner_works
        }
        
        if not import_works:
            self.validation_results["blocking_issues"].append("DeploymentAuditor import fails")
        
        if not cli_works:
            self.validation_results["warnings"].append("CLI module access issues")
        
        return success, result
    
    def generate_readiness_report(self) -> Dict[str, Any]:
        """Generate comprehensive readiness report."""
        print("\n📊 Generating Readiness Report...")
        
        # Run all validations
        validations = [
            ("file_structure", self.validate_file_structure()),
            ("python_environment", self.validate_python_environment()),
            ("dag_specification", self.validate_dag_specification()),
            ("system_resources", self.validate_system_resources()),
            ("deployment_auditor_state", self.validate_deployment_auditor_current_state())
        ]
        
        # Collect results
        all_passed = True
        for name, (success, details) in validations:
            self.validation_results["checks"][name] = {
                "success": success,
                "details": details
            }
            if not success:
                all_passed = False
        
        # Determine overall status
        if all_passed:
            self.validation_results["overall_status"] = "ready"
            print("\n🟢 OVERALL STATUS: READY FOR DAG EXECUTION")
        elif len(self.validation_results["blocking_issues"]) == 0:
            self.validation_results["overall_status"] = "ready_with_warnings"
            print("\n🟡 OVERALL STATUS: READY WITH WARNINGS")
        else:
            self.validation_results["overall_status"] = "not_ready"
            print("\n🔴 OVERALL STATUS: NOT READY FOR EXECUTION")
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Save report
        report_file = Path(f"deployment_auditor_dag_readiness_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"\n📄 Readiness report saved: {report_file}")
        
        return self.validation_results
    
    def _generate_recommendations(self):
        """Generate specific recommendations based on validation results."""
        recommendations = []
        
        # File structure recommendations
        file_check = self.validation_results["checks"].get("file_structure", {})
        if not file_check.get("success", False):
            missing_files = file_check.get("details", {}).get("missing_required", [])
            for file_path in missing_files:
                recommendations.append(f"Create missing file: {file_path}")
        
        # Python environment recommendations
        python_check = self.validation_results["checks"].get("python_environment", {})
        if not python_check.get("success", False):
            failed_imports = python_check.get("details", {}).get("failed_imports", [])
            for import_name in failed_imports:
                recommendations.append(f"Fix import issue: {import_name}")
        
        # System resources recommendations
        system_check = self.validation_results["checks"].get("system_resources", {})
        if not system_check.get("success", False):
            details = system_check.get("details", {})
            if not details.get("kiro_available", False):
                recommendations.append("Install or configure Kiro CLI in PATH")
            if not details.get("log_writable", False):
                recommendations.append("Fix log directory write permissions")
        
        # Deployment auditor recommendations
        auditor_check = self.validation_results["checks"].get("deployment_auditor_state", {})
        if auditor_check.get("success", False):
            details = auditor_check.get("details", {})
            if not details.get("cli_works", False):
                recommendations.append("Fix deployment auditor CLI module access")
        
        # General recommendations
        if len(self.validation_results["blocking_issues"]) > 0:
            recommendations.append("Resolve all blocking issues before attempting DAG execution")
        
        if len(self.validation_results["warnings"]) > 0:
            recommendations.append("Consider addressing warnings for optimal execution")
        
        self.validation_results["recommendations"] = recommendations


def main():
    """Main validation function."""
    print("🔍 DEPLOYMENT AUDITOR DAG READINESS VALIDATION")
    print("=" * 60)
    
    validator = DeploymentAuditorDAGValidator()
    report = validator.generate_readiness_report()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Blocking Issues: {len(report['blocking_issues'])}")
    print(f"Warnings: {len(report['warnings'])}")
    print(f"Recommendations: {len(report['recommendations'])}")
    
    if report["blocking_issues"]:
        print("\n🚫 BLOCKING ISSUES:")
        for issue in report["blocking_issues"]:
            print(f"   • {issue}")
    
    if report["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in report["warnings"]:
            print(f"   • {warning}")
    
    if report["recommendations"]:
        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")
    
    print("=" * 60)
    
    # Exit with appropriate code
    if report["overall_status"] == "ready":
        print("✅ DAG is ready for execution!")
        sys.exit(0)
    elif report["overall_status"] == "ready_with_warnings":
        print("⚠️  DAG is ready but has warnings")
        sys.exit(0)
    else:
        print("❌ DAG is not ready for execution")
        sys.exit(1)


if __name__ == "__main__":
    main()