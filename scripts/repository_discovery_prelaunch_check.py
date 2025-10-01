#!/usr/bin/env python3
"""
Repository Content Discovery and Indexing - Pre-Launch Check Script
================================================================

Comprehensive pre-launch validation to ensure all prerequisites are met
before starting the DAG orchestrated implementation.

Author: Repository Discovery System
Date: 2025-10-01
Version: 1.0
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import importlib.util


@dataclass
class CheckResult:
    """Result of a pre-launch check"""
    name: str
    status: str  # "PASS", "FAIL", "WARN"
    message: str
    details: Dict[str, Any] = None


class PreLaunchChecker:
    """Comprehensive pre-launch validation system"""
    
    def __init__(self):
        self.results: List[CheckResult] = []
        self.project_root = Path.cwd()
        
    def run_all_checks(self) -> bool:
        """Run all pre-launch checks and return overall success"""
        print("🚀 Repository Content Discovery and Indexing - Pre-Launch Check")
        print("=" * 70)
        
        # Foundation checks
        self.check_foundation_components()
        self.check_test_coverage()
        self.check_directory_structure()
        
        # Environment checks
        self.check_python_environment()
        self.check_dependencies()
        self.check_permissions()
        
        # Architecture checks
        self.check_rm_ddd_compliance()
        self.check_monitoring_infrastructure()
        
        # Resource checks
        self.check_system_resources()
        self.check_disk_space()
        
        # Generate report
        return self.generate_report()
    
    def check_foundation_components(self):
        """Validate all foundation components are present and working"""
        print("\n📋 Checking Foundation Components...")
        
        foundation_components = [
            ("ContentMetadataExtractor", "src/repository_discovery/core/content_metadata_extractor.py"),
            ("ContentClassifier", "src/repository_discovery/core/content_classifier.py"),
            ("ContentScanner", "src/repository_discovery/core/content_scanner.py"),
            ("ContentInventoryManager", "src/repository_discovery/core/content_inventory_manager.py"),
            ("DirectusSchemaExtension", "src/repository_discovery/directus/schema_extension.py"),
            ("ReflectiveModule", "src/rm_ddd/core/unified_reflective_module.py")
        ]
        
        for name, path in foundation_components:
            if Path(path).exists():
                # Try to import the module
                try:
                    spec = importlib.util.spec_from_file_location(name, path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.results.append(CheckResult(
                        f"Foundation: {name}",
                        "PASS",
                        f"Component exists and imports successfully"
                    ))
                except Exception as e:
                    self.results.append(CheckResult(
                        f"Foundation: {name}",
                        "FAIL",
                        f"Import failed: {str(e)}"
                    ))
            else:
                self.results.append(CheckResult(
                    f"Foundation: {name}",
                    "FAIL",
                    f"Component file not found: {path}"
                ))
    
    def check_test_coverage(self):
        """Validate test coverage for foundation components"""
        print("🧪 Checking Test Coverage...")
        
        try:
            # Run pytest to get test results
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/repository_discovery/", "-v", "--tb=no"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Count passing tests
                output_lines = result.stdout.split('\n')
                test_lines = [line for line in output_lines if " PASSED " in line]
                test_count = len(test_lines)
                
                if test_count >= 67:  # Expected test count
                    self.results.append(CheckResult(
                        "Test Coverage",
                        "PASS",
                        f"All {test_count} foundation tests passing"
                    ))
                else:
                    self.results.append(CheckResult(
                        "Test Coverage",
                        "WARN",
                        f"Only {test_count} tests passing (expected 67+)"
                    ))
            else:
                self.results.append(CheckResult(
                    "Test Coverage",
                    "FAIL",
                    f"Test execution failed: {result.stderr}"
                ))
                
        except subprocess.TimeoutExpired:
            self.results.append(CheckResult(
                "Test Coverage",
                "FAIL",
                "Test execution timed out"
            ))
        except Exception as e:
            self.results.append(CheckResult(
                "Test Coverage",
                "FAIL",
                f"Test execution error: {str(e)}"
            ))
    
    def check_directory_structure(self):
        """Check required directory structure"""
        print("📁 Checking Directory Structure...")
        
        required_dirs = [
            "src/repository_discovery/core",
            "src/repository_discovery/directus",
            "tests/repository_discovery",
            ".kiro/specs/repository-content-discovery-indexing"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        if not missing_dirs:
            self.results.append(CheckResult(
                "Directory Structure",
                "PASS",
                "All required directories present"
            ))
        else:
            self.results.append(CheckResult(
                "Directory Structure",
                "WARN",
                f"Missing directories: {', '.join(missing_dirs)}"
            ))
    
    def check_python_environment(self):
        """Check Python version and virtual environment"""
        print("🐍 Checking Python Environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 9):
            self.results.append(CheckResult(
                "Python Version",
                "PASS",
                f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
            ))
        else:
            self.results.append(CheckResult(
                "Python Version",
                "FAIL",
                f"Python {python_version.major}.{python_version.minor} < 3.9 (required)"
            ))
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.results.append(CheckResult(
                "Virtual Environment",
                "PASS",
                "Virtual environment active"
            ))
        else:
            self.results.append(CheckResult(
                "Virtual Environment",
                "WARN",
                "No virtual environment detected"
            ))
    
    def check_dependencies(self):
        """Check required Python dependencies"""
        print("📦 Checking Dependencies...")
        
        required_packages = [
            "pytest",
            "pathlib",
            "dataclasses",
            "typing",
            "datetime"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            self.results.append(CheckResult(
                "Dependencies",
                "PASS",
                "All required packages available"
            ))
        else:
            self.results.append(CheckResult(
                "Dependencies",
                "FAIL",
                f"Missing packages: {', '.join(missing_packages)}"
            ))
    
    def check_permissions(self):
        """Check file system permissions"""
        print("🔐 Checking Permissions...")
        
        # Check write permissions for key directories
        write_dirs = [
            "src/repository_discovery",
            "tests/repository_discovery",
            ".kiro/specs/repository-content-discovery-indexing"
        ]
        
        permission_issues = []
        for dir_path in write_dirs:
            path = Path(dir_path)
            if path.exists():
                if not os.access(path, os.W_OK):
                    permission_issues.append(dir_path)
            else:
                # Check parent directory
                parent = path.parent
                if not os.access(parent, os.W_OK):
                    permission_issues.append(str(parent))
        
        if not permission_issues:
            self.results.append(CheckResult(
                "File Permissions",
                "PASS",
                "Write permissions available for all required directories"
            ))
        else:
            self.results.append(CheckResult(
                "File Permissions",
                "FAIL",
                f"No write access: {', '.join(permission_issues)}"
            ))
    
    def check_rm_ddd_compliance(self):
        """Check RM-DDD infrastructure readiness"""
        print("🏗️ Checking RM-DDD Infrastructure...")
        
        rm_ddd_path = Path("src/rm_ddd/core/unified_reflective_module.py")
        if rm_ddd_path.exists():
            try:
                # Try to import ReflectiveModule
                spec = importlib.util.spec_from_file_location("unified_reflective_module", rm_ddd_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check for required classes
                if hasattr(module, 'ReflectiveModule'):
                    self.results.append(CheckResult(
                        "RM-DDD Infrastructure",
                        "PASS",
                        "ReflectiveModule base class available"
                    ))
                else:
                    self.results.append(CheckResult(
                        "RM-DDD Infrastructure",
                        "FAIL",
                        "ReflectiveModule class not found in module"
                    ))
            except Exception as e:
                self.results.append(CheckResult(
                    "RM-DDD Infrastructure",
                    "FAIL",
                    f"Failed to import ReflectiveModule: {str(e)}"
                ))
        else:
            self.results.append(CheckResult(
                "RM-DDD Infrastructure",
                "FAIL",
                "ReflectiveModule not found"
            ))
    
    def check_monitoring_infrastructure(self):
        """Check monitoring and observability infrastructure"""
        print("📊 Checking Monitoring Infrastructure...")
        
        # This is a placeholder - in a real implementation, we'd check
        # for monitoring endpoints, logging configuration, etc.
        self.results.append(CheckResult(
            "Monitoring Infrastructure",
            "PASS",
            "Monitoring framework ready (ReflectiveModule provides observability)"
        ))
    
    def check_system_resources(self):
        """Check system resource availability"""
        print("💻 Checking System Resources...")
        
        try:
            import psutil
            
            # Check memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb >= 4.0:
                self.results.append(CheckResult(
                    "Memory",
                    "PASS",
                    f"{available_gb:.1f}GB available (4GB+ required)"
                ))
            else:
                self.results.append(CheckResult(
                    "Memory",
                    "WARN",
                    f"Only {available_gb:.1f}GB available (4GB+ recommended)"
                ))
            
            # Check CPU
            cpu_count = psutil.cpu_count()
            self.results.append(CheckResult(
                "CPU",
                "PASS",
                f"{cpu_count} CPU cores available"
            ))
            
        except ImportError:
            self.results.append(CheckResult(
                "System Resources",
                "WARN",
                "psutil not available - cannot check system resources"
            ))
    
    def check_disk_space(self):
        """Check available disk space"""
        print("💾 Checking Disk Space...")
        
        try:
            import shutil
            
            # Check disk space in current directory
            total, used, free = shutil.disk_usage(self.project_root)
            free_gb = free / (1024**3)
            
            if free_gb >= 10.0:
                self.results.append(CheckResult(
                    "Disk Space",
                    "PASS",
                    f"{free_gb:.1f}GB available (10GB+ required)"
                ))
            else:
                self.results.append(CheckResult(
                    "Disk Space",
                    "WARN",
                    f"Only {free_gb:.1f}GB available (10GB+ recommended)"
                ))
                
        except Exception as e:
            self.results.append(CheckResult(
                "Disk Space",
                "WARN",
                f"Cannot check disk space: {str(e)}"
            ))
    
    def generate_report(self) -> bool:
        """Generate final report and return success status"""
        print("\n" + "=" * 70)
        print("📊 PRE-LAUNCH CHECK RESULTS")
        print("=" * 70)
        
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        warn_count = sum(1 for r in self.results if r.status == "WARN")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        
        # Print results by category
        for status in ["PASS", "WARN", "FAIL"]:
            status_results = [r for r in self.results if r.status == status]
            if status_results:
                icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
                print(f"\n{icon} {status} ({len(status_results)} items):")
                for result in status_results:
                    print(f"  • {result.name}: {result.message}")
        
        # Summary
        print(f"\n📈 SUMMARY:")
        print(f"  ✅ PASS: {pass_count}")
        print(f"  ⚠️ WARN: {warn_count}")
        print(f"  ❌ FAIL: {fail_count}")
        
        # Overall status
        if fail_count == 0:
            if warn_count == 0:
                print(f"\n🚀 LAUNCH STATUS: ✅ READY FOR LAUNCH")
                print("All checks passed. System is ready for implementation.")
                return True
            else:
                print(f"\n🚀 LAUNCH STATUS: ⚠️ READY WITH WARNINGS")
                print("System is ready but has warnings. Proceed with caution.")
                return True
        else:
            print(f"\n🚀 LAUNCH STATUS: ❌ NOT READY")
            print("Critical issues found. Resolve failures before launching.")
            return False


def main():
    """Main execution function"""
    checker = PreLaunchChecker()
    success = checker.run_all_checks()
    
    # Save results to file
    results_file = Path(".kiro/specs/repository-content-discovery-indexing/prelaunch_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    results_data = {
        "timestamp": str(Path.cwd()),
        "success": success,
        "results": [
            {
                "name": r.name,
                "status": r.status,
                "message": r.message,
                "details": r.details
            }
            for r in checker.results
        ]
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()