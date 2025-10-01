#!/usr/bin/env python3
"""
Repository Setup and Installation - Pre-Launch Validation
========================================================

Validates system readiness for parallel DAG execution of repository setup tasks.
Ensures all prerequisites, dependencies, and infrastructure are in place.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepositorySetupPreLaunchChecker:
    """Pre-launch validation for repository setup DAG execution."""
    
    def __init__(self):
        self.repository_root = Path.cwd()
        self.spec_path = self.repository_root / ".kiro" / "specs" / "repository-setup-and-installation"
        self.validation_results = []
        self.critical_failures = []
        
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all pre-launch validation checks."""
        logger.info("🚀 Repository Setup Pre-Launch Validation Starting...")
        
        checks = [
            ("Specification Files", self.check_specification_files),
            ("Python Environment", self.check_python_environment),
            ("Git Repository", self.check_git_repository),
            ("Directory Structure", self.check_directory_structure),
            ("Dependencies", self.check_dependencies),
            ("Makefile System", self.check_makefile_system),
            ("Beast Mode Framework", self.check_beast_mode_framework),
            ("Test Infrastructure", self.check_test_infrastructure),
            ("Parallel Execution", self.check_parallel_execution_readiness),
            ("Resource Availability", self.check_resource_availability)
        ]
        
        results = {
            "overall_status": "unknown",
            "checks": {},
            "critical_failures": [],
            "warnings": [],
            "recommendations": []
        }
        
        for check_name, check_function in checks:
            logger.info(f"🔍 Running {check_name} validation...")
            try:
                check_result = check_function()
                results["checks"][check_name] = check_result
                
                if not check_result["passed"]:
                    if check_result.get("critical", False):
                        self.critical_failures.append(f"{check_name}: {check_result['message']}")
                    else:
                        results["warnings"].append(f"{check_name}: {check_result['message']}")
                        
            except Exception as e:
                error_msg = f"{check_name} validation failed: {str(e)}"
                logger.error(error_msg)
                self.critical_failures.append(error_msg)
                results["checks"][check_name] = {
                    "passed": False,
                    "critical": True,
                    "message": str(e)
                }
        
        # Determine overall status
        if self.critical_failures:
            results["overall_status"] = "FAILED"
            results["critical_failures"] = self.critical_failures
        elif results["warnings"]:
            results["overall_status"] = "WARNING"
        else:
            results["overall_status"] = "READY"
            
        # Add recommendations
        results["recommendations"] = self.generate_recommendations(results)
        
        return results
    
    def check_specification_files(self) -> Dict[str, Any]:
        """Validate specification files exist and are properly formatted."""
        required_files = ["requirements.md", "design.md", "tasks.md"]
        missing_files = []
        
        for file_name in required_files:
            file_path = self.spec_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)
            elif file_path.stat().st_size == 0:
                missing_files.append(f"{file_name} (empty)")
        
        if missing_files:
            return {
                "passed": False,
                "critical": True,
                "message": f"Missing specification files: {', '.join(missing_files)}",
                "details": {"missing_files": missing_files}
            }
        
        # Check tasks.md format
        tasks_content = (self.spec_path / "tasks.md").read_text()
        task_count = tasks_content.count("- [ ]")
        
        return {
            "passed": True,
            "message": f"All specification files present. Found {task_count} tasks.",
            "details": {"task_count": task_count}
        }
    
    def check_python_environment(self) -> Dict[str, Any]:
        """Validate Python environment and version."""
        try:
            python_version = sys.version_info
            if python_version < (3, 9):
                return {
                    "passed": False,
                    "critical": True,
                    "message": f"Python 3.9+ required, found {python_version.major}.{python_version.minor}"
                }
            
            # Check virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            
            return {
                "passed": True,
                "message": f"Python {python_version.major}.{python_version.minor}.{python_version.micro}, venv: {in_venv}",
                "details": {
                    "version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                    "virtual_env": in_venv
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "message": f"Python environment check failed: {str(e)}"
            }
    
    def check_git_repository(self) -> Dict[str, Any]:
        """Validate git repository status and configuration."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  capture_output=True, text=True, cwd=self.repository_root)
            if result.returncode != 0:
                return {
                    "passed": False,
                    "critical": True,
                    "message": "Not in a git repository"
                }
            
            # Check git status
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, cwd=self.repository_root)
            
            untracked_files = [line for line in result.stdout.split('\n') if line.startswith('??')]
            modified_files = [line for line in result.stdout.split('\n') if line and not line.startswith('??')]
            
            return {
                "passed": True,
                "message": f"Git repository ready. {len(untracked_files)} untracked, {len(modified_files)} modified files",
                "details": {
                    "untracked_count": len(untracked_files),
                    "modified_count": len(modified_files)
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "message": f"Git repository check failed: {str(e)}"
            }
    
    def check_directory_structure(self) -> Dict[str, Any]:
        """Validate required directory structure exists."""
        required_dirs = [
            ".kiro",
            ".kiro/specs",
            ".kiro/steering",
            "src",
            "tests",
            "scripts"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.repository_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            return {
                "passed": False,
                "critical": True,
                "message": f"Missing required directories: {', '.join(missing_dirs)}"
            }
        
        return {
            "passed": True,
            "message": "All required directories present"
        }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if required dependencies are available."""
        required_packages = [
            "pytest",
            "pathlib",
            "typing",
            "json",
            "subprocess"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            return {
                "passed": False,
                "critical": True,
                "message": f"Missing required packages: {', '.join(missing_packages)}"
            }
        
        return {
            "passed": True,
            "message": "All required dependencies available"
        }
    
    def check_makefile_system(self) -> Dict[str, Any]:
        """Validate Makefile system is functional."""
        makefile_path = self.repository_root / "Makefile"
        
        if not makefile_path.exists():
            return {
                "passed": False,
                "critical": True,
                "message": "Makefile not found"
            }
        
        try:
            # Test make help
            result = subprocess.run(["make", "help"], 
                                  capture_output=True, text=True, cwd=self.repository_root)
            
            if result.returncode != 0:
                return {
                    "passed": False,
                    "critical": False,
                    "message": "Makefile exists but 'make help' failed"
                }
            
            # Check for install target
            makefile_content = makefile_path.read_text()
            has_install = "install:" in makefile_content
            
            return {
                "passed": True,
                "message": f"Makefile functional, install target: {has_install}",
                "details": {"has_install_target": has_install}
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": False,
                "message": f"Makefile validation failed: {str(e)}"
            }
    
    def check_beast_mode_framework(self) -> Dict[str, Any]:
        """Check Beast Mode framework availability."""
        beast_mode_path = self.repository_root / "src" / "beast_mode"
        
        if not beast_mode_path.exists():
            return {
                "passed": False,
                "critical": False,
                "message": "Beast Mode framework not found in src/beast_mode"
            }
        
        # Check for ReflectiveModule
        core_path = beast_mode_path / "core"
        if core_path.exists():
            return {
                "passed": True,
                "message": "Beast Mode framework available"
            }
        
        return {
            "passed": False,
            "critical": False,
            "message": "Beast Mode framework incomplete (missing core)"
        }
    
    def check_test_infrastructure(self) -> Dict[str, Any]:
        """Validate test generation infrastructure."""
        test_generator_path = self.repository_root / "scripts" / "generate_missing_tests.py"
        
        if not test_generator_path.exists():
            return {
                "passed": False,
                "critical": False,
                "message": "Test generator script not found"
            }
        
        tests_dir = self.repository_root / "tests"
        if not tests_dir.exists():
            return {
                "passed": False,
                "critical": False,
                "message": "Tests directory not found"
            }
        
        return {
            "passed": True,
            "message": "Test infrastructure available"
        }
    
    def check_parallel_execution_readiness(self) -> Dict[str, Any]:
        """Check system readiness for parallel task execution."""
        try:
            import concurrent.futures
            import multiprocessing
            
            cpu_count = multiprocessing.cpu_count()
            
            # Test parallel execution capability
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(lambda: True) for _ in range(2)]
                results = [f.result() for f in futures]
            
            return {
                "passed": True,
                "message": f"Parallel execution ready, {cpu_count} CPUs available",
                "details": {"cpu_count": cpu_count}
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "message": f"Parallel execution check failed: {str(e)}"
            }
    
    def check_resource_availability(self) -> Dict[str, Any]:
        """Check system resource availability."""
        try:
            import shutil
            
            # Check disk space
            disk_usage = shutil.disk_usage(self.repository_root)
            free_gb = disk_usage.free / (1024**3)
            
            if free_gb < 1.0:
                return {
                    "passed": False,
                    "critical": True,
                    "message": f"Insufficient disk space: {free_gb:.1f}GB free"
                }
            
            return {
                "passed": True,
                "message": f"Resources available: {free_gb:.1f}GB free disk space",
                "details": {"free_disk_gb": free_gb}
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": False,
                "message": f"Resource check failed: {str(e)}"
            }
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if results["overall_status"] == "FAILED":
            recommendations.append("❌ CRITICAL: Fix all critical failures before launching")
            recommendations.append("📋 Review critical_failures list for specific issues")
        
        if results["overall_status"] == "WARNING":
            recommendations.append("⚠️  WARNING: Address warnings for optimal execution")
            recommendations.append("🚀 Launch possible but may encounter issues")
        
        if results["overall_status"] == "READY":
            recommendations.append("✅ READY: All systems go for parallel DAG execution")
            recommendations.append("🎯 Estimated execution time: 12-16 hours")
            recommendations.append("👥 Recommended workers: 3-4 parallel")
        
        # Specific recommendations based on checks
        checks = results.get("checks", {})
        
        if "Beast Mode Framework" in checks and not checks["Beast Mode Framework"]["passed"]:
            recommendations.append("🐺 Consider implementing ReflectiveModule pattern manually")
        
        if "Test Infrastructure" in checks and not checks["Test Infrastructure"]["passed"]:
            recommendations.append("🧪 Test generation will be manual without test generator")
        
        return recommendations
    
    def save_results(self, results: Dict[str, Any]) -> str:
        """Save validation results to file."""
        output_file = self.spec_path / "LAUNCH_READINESS.md"
        
        content = f"""# Repository Setup and Installation - Launch Readiness Report

## Overall Status: {results['overall_status']}

Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}

## Validation Summary

"""
        
        for check_name, check_result in results["checks"].items():
            status_icon = "✅" if check_result["passed"] else ("❌" if check_result.get("critical") else "⚠️")
            content += f"- {status_icon} **{check_name}**: {check_result['message']}\n"
        
        if results["critical_failures"]:
            content += "\n## Critical Failures\n\n"
            for failure in results["critical_failures"]:
                content += f"- ❌ {failure}\n"
        
        if results["warnings"]:
            content += "\n## Warnings\n\n"
            for warning in results["warnings"]:
                content += f"- ⚠️ {warning}\n"
        
        content += "\n## Recommendations\n\n"
        for recommendation in results["recommendations"]:
            content += f"- {recommendation}\n"
        
        content += f"""
## Next Steps

### If Status is READY ✅
```bash
# Launch parallel DAG execution
./scripts/repository_setup_background_launch.sh
```

### If Status is WARNING ⚠️
1. Review warnings above
2. Decide if acceptable risk
3. Launch with caution or fix issues first

### If Status is FAILED ❌
1. Fix all critical failures
2. Re-run pre-launch check
3. Do not launch until READY

## Technical Details

```json
{json.dumps(results, indent=2)}
```
"""
        
        output_file.write_text(content)
        return str(output_file)

def main():
    """Main execution function."""
    checker = RepositorySetupPreLaunchChecker()
    
    print("🚀 Repository Setup and Installation - Pre-Launch Validation")
    print("=" * 60)
    
    results = checker.run_comprehensive_check()
    
    # Save results
    output_file = checker.save_results(results)
    
    # Print summary
    print(f"\n📊 Validation Complete - Status: {results['overall_status']}")
    print(f"📄 Full report saved to: {output_file}")
    
    if results["overall_status"] == "READY":
        print("\n✅ SYSTEM READY FOR PARALLEL DAG EXECUTION")
        print("🚀 Run: ./scripts/repository_setup_background_launch.sh")
    elif results["overall_status"] == "WARNING":
        print("\n⚠️  SYSTEM HAS WARNINGS - REVIEW BEFORE LAUNCH")
        print("📋 Check warnings in the report above")
    else:
        print("\n❌ SYSTEM NOT READY - CRITICAL FAILURES DETECTED")
        print("🔧 Fix critical issues before attempting launch")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())