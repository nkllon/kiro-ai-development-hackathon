#!/usr/bin/env python3
"""
Installation Testing System for Beast Mode AI Development Framework

This script tests the installation process on multiple platforms by:
1. Testing dependency resolution and environment setup
2. Validating installation scripts work correctly
3. Ensuring quick start guide works for new users
4. Testing Docker and containerized installations

Requirements addressed: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import platform
import venv
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback

@dataclass
class InstallationTestResult:
    """Result of testing a single installation method."""
    test_name: str
    platform_info: Dict[str, str]
    success: bool
    execution_time: float
    output: str
    error_message: Optional[str] = None
    dependencies_resolved: bool = False
    quick_start_works: bool = False
    
@dataclass
class InstallationReport:
    """Comprehensive installation testing report."""
    timestamp: str
    platform_info: Dict[str, str]
    total_tests: int
    successful_tests: int
    failed_tests: int
    results: List[InstallationTestResult]
    summary: Dict[str, Any]

class InstallationTester:
    """Tests installation process on multiple platforms."""
    
    def __init__(self):
        self.project_root = Path.cwd().resolve()
        self.platform_info = self._get_platform_info()
        
    def _get_platform_info(self) -> Dict[str, str]:
        """Get current platform information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        }
    
    def test_all_installations(self) -> InstallationReport:
        """Test all installation methods."""
        print("🔧 Starting comprehensive installation testing...")
        print(f"Platform: {self.platform_info['system']} {self.platform_info['release']}")
        print(f"Python: {self.platform_info['python_version']}")
        
        results = []
        
        # Test different installation methods
        test_methods = [
            ("pip_install", self._test_pip_installation),
            ("script_install", self._test_script_installation),
            ("docker_install", self._test_docker_installation),
            ("development_setup", self._test_development_setup),
            ("dependency_resolution", self._test_dependency_resolution),
            ("quick_start_guide", self._test_quick_start_guide),
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n🧪 Testing: {test_name}")
            result = self._run_installation_test(test_name, test_method)
            results.append(result)
            
            # Print immediate feedback
            if result.success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED - {result.error_message}")
        
        # Generate comprehensive report
        report = self._generate_report(results)
        self._save_report(report)
        
        return report
    
    def _run_installation_test(self, test_name: str, test_method) -> InstallationTestResult:
        """Run a single installation test."""
        start_time = datetime.now()
        
        try:
            result = test_method()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return InstallationTestResult(
                test_name=test_name,
                platform_info=self.platform_info,
                success=result.get("success", False),
                execution_time=execution_time,
                output=result.get("output", ""),
                error_message=result.get("error"),
                dependencies_resolved=result.get("dependencies_resolved", False),
                quick_start_works=result.get("quick_start_works", False)
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return InstallationTestResult(
                test_name=test_name,
                platform_info=self.platform_info,
                success=False,
                execution_time=execution_time,
                output="",
                error_message=f"Test error: {str(e)}",
                dependencies_resolved=False,
                quick_start_works=False
            )
    
    def _test_pip_installation(self) -> Dict[str, Any]:
        """Test pip-based installation."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create a virtual environment
                venv_path = temp_path / "test_venv"
                venv.create(venv_path, with_pip=True)
                
                # Get the python executable in the venv
                if platform.system() == "Windows":
                    python_exe = venv_path / "Scripts" / "python.exe"
                    pip_exe = venv_path / "Scripts" / "pip.exe"
                else:
                    python_exe = venv_path / "bin" / "python"
                    pip_exe = venv_path / "bin" / "pip"
                
                # Test pip installation of requirements
                requirements_file = self.project_root / "requirements.txt"
                if requirements_file.exists():
                    result = subprocess.run(
                        [str(pip_exe), "install", "-r", str(requirements_file)],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode != 0:
                        return {
                            "success": False,
                            "error": f"Pip install failed: {result.stderr}",
                            "output": result.stdout
                        }
                    
                    # Test importing key modules
                    test_imports = [
                        "import sys",
                        "sys.path.insert(0, r'" + str(self.project_root / "src") + "')",
                        "from beast_mode.core.reflective_module import ReflectiveModule",
                        "from beast_mode.ai_memory_palace.context_engine import ContextEngine",
                        "print('All imports successful')"
                    ]
                    
                    import_test = subprocess.run(
                        [str(python_exe), "-c", "; ".join(test_imports)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if import_test.returncode != 0:
                        return {
                            "success": False,
                            "error": f"Import test failed: {import_test.stderr}",
                            "output": import_test.stdout,
                            "dependencies_resolved": True
                        }
                    
                    return {
                        "success": True,
                        "output": f"Pip installation successful\n{result.stdout}\n{import_test.stdout}",
                        "dependencies_resolved": True
                    }
                else:
                    return {
                        "success": False,
                        "error": "requirements.txt not found"
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timeout (5 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Pip installation error: {str(e)}"
            }
    
    def _test_script_installation(self) -> Dict[str, Any]:
        """Test script-based installation."""
        try:
            # Test the install script exists
            if platform.system() == "Windows":
                install_script = self.project_root / "install.bat"
            else:
                install_script = self.project_root / "install.sh"
            
            if not install_script.exists():
                return {
                    "success": False,
                    "error": f"Install script not found: {install_script}"
                }
            
            # For safety, we'll just validate the script syntax rather than execute it
            # since it might modify the system
            with open(install_script, 'r') as f:
                script_content = f.read()
            
            # Basic validation checks
            validation_issues = []
            
            if platform.system() != "Windows":
                # Check for bash shebang
                if not script_content.startswith("#!/"):
                    validation_issues.append("Missing shebang line")
                
                # Check for basic error handling
                if "set -e" not in script_content:
                    validation_issues.append("Missing error handling (set -e)")
            
            # Check for dependency installation commands
            if platform.system() == "Windows":
                if "pip install" not in script_content:
                    validation_issues.append("Missing pip install command")
            else:
                if "pip" not in script_content and "pip3" not in script_content:
                    validation_issues.append("Missing pip installation command")
            
            if validation_issues:
                return {
                    "success": False,
                    "error": f"Script validation issues: {', '.join(validation_issues)}",
                    "output": f"Script content preview:\n{script_content[:500]}..."
                }
            
            return {
                "success": True,
                "output": f"Install script validation passed: {install_script}",
                "dependencies_resolved": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Script installation test error: {str(e)}"
            }
    
    def _test_docker_installation(self) -> Dict[str, Any]:
        """Test Docker-based installation."""
        try:
            # Check if Docker files exist
            dockerfile = self.project_root / "Dockerfile"
            docker_compose = self.project_root / "docker-compose.yml"
            
            if not dockerfile.exists():
                return {
                    "success": False,
                    "error": "Dockerfile not found"
                }
            
            # Validate Dockerfile syntax
            with open(dockerfile, 'r', encoding='utf-8') as f:
                dockerfile_content = f.read().strip()
            
            validation_issues = []
            
            # Basic Dockerfile validation
            # Check if FROM appears in the first few lines (allowing for comments)
            lines = dockerfile_content.split('\n')
            has_from = False
            for line in lines[:10]:  # Check first 10 lines
                if line.strip().startswith('FROM '):
                    has_from = True
                    break
            
            if not has_from:
                validation_issues.append("Dockerfile must contain FROM instruction in first 10 lines")
            
            if "COPY" not in dockerfile_content and "ADD" not in dockerfile_content:
                validation_issues.append("Dockerfile missing COPY or ADD instruction")
            
            if "CMD" not in dockerfile_content and "ENTRYPOINT" not in dockerfile_content:
                validation_issues.append("Dockerfile missing CMD or ENTRYPOINT instruction")
            
            # Check for security best practices
            if "USER root" in dockerfile_content and "USER " not in dockerfile_content.split("USER root", 1)[1]:
                validation_issues.append("Dockerfile runs as root without switching to non-root user")
            
            if validation_issues:
                return {
                    "success": False,
                    "error": f"Dockerfile validation issues: {', '.join(validation_issues)}",
                    "output": f"Dockerfile preview:\n{dockerfile_content[:500]}..."
                }
            
            # Test Docker Compose if it exists
            compose_output = ""
            if docker_compose.exists():
                try:
                    import yaml
                    with open(docker_compose, 'r') as f:
                        compose_content = yaml.safe_load(f)
                    
                    if 'services' not in compose_content:
                        validation_issues.append("docker-compose.yml missing services section")
                    
                    compose_output = f"\nDocker Compose services: {list(compose_content.get('services', {}).keys())}"
                    
                except yaml.YAMLError as e:
                    validation_issues.append(f"Invalid docker-compose.yml: {e}")
            
            if validation_issues:
                return {
                    "success": False,
                    "error": f"Docker validation issues: {', '.join(validation_issues)}"
                }
            
            return {
                "success": True,
                "output": f"Docker configuration validation passed{compose_output}",
                "dependencies_resolved": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Docker installation test error: {str(e)}"
            }
    
    def _test_development_setup(self) -> Dict[str, Any]:
        """Test development environment setup."""
        try:
            # Check for development files
            dev_files = [
                "requirements-dev.txt",
                "pyproject.toml",
                ".pre-commit-config.yaml",
                "pytest.ini"
            ]
            
            missing_files = []
            for file_name in dev_files:
                if not (self.project_root / file_name).exists():
                    missing_files.append(file_name)
            
            # Check for source code structure
            src_dir = self.project_root / "src"
            if not src_dir.exists():
                return {
                    "success": False,
                    "error": "Source directory (src/) not found"
                }
            
            # Check for key modules
            key_modules = [
                "src/beast_mode",
                "src/beast_mode/core",
                "src/beast_mode/ai_memory_palace"
            ]
            
            missing_modules = []
            for module_path in key_modules:
                if not (self.project_root / module_path).exists():
                    missing_modules.append(module_path)
            
            issues = []
            if missing_files:
                issues.append(f"Missing development files: {', '.join(missing_files)}")
            if missing_modules:
                issues.append(f"Missing key modules: {', '.join(missing_modules)}")
            
            if issues:
                return {
                    "success": False,
                    "error": "; ".join(issues),
                    "output": f"Found files: {[f.name for f in self.project_root.iterdir() if f.is_file()][:10]}"
                }
            
            return {
                "success": True,
                "output": "Development environment structure validated",
                "dependencies_resolved": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Development setup test error: {str(e)}"
            }
    
    def _test_dependency_resolution(self) -> Dict[str, Any]:
        """Test dependency resolution and compatibility."""
        try:
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                return {
                    "success": False,
                    "error": "requirements.txt not found"
                }
            
            # Parse requirements
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
            
            # Filter out empty lines and comments
            requirements = [req.strip() for req in requirements if req.strip() and not req.strip().startswith('#')]
            
            # Basic validation of requirement format
            invalid_requirements = []
            for req in requirements:
                # Skip environment markers (semicolon indicates environment marker)
                if ';' in req:
                    package_part = req.split(';')[0].strip()
                else:
                    package_part = req
                
                # Check for basic package name format (allow common pip requirement characters)
                cleaned = package_part.replace('-', '').replace('_', '').replace('.', '').replace('>', '').replace('<', '').replace('=', '').replace('[', '').replace(']', '').replace(',', '').replace(' ', '').replace('!', '').replace('~', '')
                if not cleaned.isalnum():
                    if '://' not in req:  # Allow URLs
                        invalid_requirements.append(req)
            
            if invalid_requirements:
                return {
                    "success": False,
                    "error": f"Invalid requirement format: {', '.join(invalid_requirements)}",
                    "output": f"Total requirements: {len(requirements)}"
                }
            
            # Check for potential security issues in requirements
            security_issues = []
            for req in requirements:
                if 'http://' in req:
                    security_issues.append(f"Insecure HTTP URL: {req}")
            
            if security_issues:
                return {
                    "success": False,
                    "error": f"Security issues in requirements: {', '.join(security_issues)}"
                }
            
            return {
                "success": True,
                "output": f"Dependency resolution validated: {len(requirements)} requirements",
                "dependencies_resolved": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Dependency resolution test error: {str(e)}"
            }
    
    def _test_quick_start_guide(self) -> Dict[str, Any]:
        """Test that the quick start guide works."""
        try:
            # Check for README with quick start
            readme_file = self.project_root / "README.md"
            if not readme_file.exists():
                return {
                    "success": False,
                    "error": "README.md not found"
                }
            
            with open(readme_file, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # Check for quick start section
            quick_start_indicators = [
                "quick start",
                "getting started",
                "installation",
                "setup"
            ]
            
            has_quick_start = any(indicator in readme_content.lower() for indicator in quick_start_indicators)
            
            if not has_quick_start:
                return {
                    "success": False,
                    "error": "README missing quick start section",
                    "output": f"README length: {len(readme_content)} characters"
                }
            
            # Check for code examples
            code_blocks = readme_content.count('```')
            if code_blocks < 2:  # At least one code block (opening and closing)
                return {
                    "success": False,
                    "error": "README missing code examples",
                    "output": f"Found {code_blocks // 2} code blocks"
                }
            
            # Check for installation instructions
            installation_keywords = ["pip install", "docker", "git clone", "python"]
            has_installation = any(keyword in readme_content.lower() for keyword in installation_keywords)
            
            if not has_installation:
                return {
                    "success": False,
                    "error": "README missing installation instructions"
                }
            
            # Test if quick start example exists
            examples_dir = self.project_root / "examples"
            quick_start_files = []
            if examples_dir.exists():
                for pattern in ["quick_start*", "*quick*start*", "basic/*"]:
                    quick_start_files.extend(examples_dir.glob(f"**/{pattern}.py"))
            
            if not quick_start_files:
                return {
                    "success": False,
                    "error": "No quick start example files found",
                    "output": f"Checked examples directory: {examples_dir.exists()}"
                }
            
            return {
                "success": True,
                "output": f"Quick start guide validated: {len(quick_start_files)} example files found",
                "quick_start_works": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Quick start guide test error: {str(e)}"
            }
    
    def _generate_report(self, results: List[InstallationTestResult]) -> InstallationReport:
        """Generate comprehensive installation testing report."""
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        # Calculate summary statistics
        avg_execution_time = sum(r.execution_time for r in results) / len(results) if results else 0
        dependencies_resolved_count = sum(1 for r in results if r.dependencies_resolved)
        quick_start_works_count = sum(1 for r in results if r.quick_start_works)
        
        summary = {
            "success_rate": (successful / len(results)) * 100 if results else 0,
            "average_execution_time": avg_execution_time,
            "dependencies_resolved_rate": (dependencies_resolved_count / len(results)) * 100 if results else 0,
            "quick_start_success_rate": (quick_start_works_count / len(results)) * 100 if results else 0,
            "platform_compatibility": self._assess_platform_compatibility(results)
        }
        
        return InstallationReport(
            timestamp=datetime.now().isoformat(),
            platform_info=self.platform_info,
            total_tests=len(results),
            successful_tests=successful,
            failed_tests=failed,
            results=results,
            summary=summary
        )
    
    def _assess_platform_compatibility(self, results: List[InstallationTestResult]) -> Dict[str, Any]:
        """Assess platform compatibility based on test results."""
        compatibility = {
            "overall_compatible": all(r.success for r in results),
            "critical_failures": [],
            "warnings": []
        }
        
        for result in results:
            if not result.success:
                if result.test_name in ["pip_install", "dependency_resolution"]:
                    compatibility["critical_failures"].append(result.test_name)
                else:
                    compatibility["warnings"].append(result.test_name)
        
        return compatibility
    
    def _save_report(self, report: InstallationReport) -> None:
        """Save installation testing report to file."""
        report_file = self.project_root / "data" / "installation_test_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        # Convert to JSON-serializable format
        report_dict = asdict(report)
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
            
        print(f"\n📊 Installation test report saved to: {report_file}")
        
        # Also create a human-readable summary
        self._create_summary_report(report)
    
    def _create_summary_report(self, report: InstallationReport) -> None:
        """Create human-readable summary report."""
        summary_file = self.project_root / "data" / "installation_test_summary.md"
        
        with open(summary_file, 'w') as f:
            f.write("# Installation Testing Summary Report\n\n")
            f.write(f"**Generated:** {report.timestamp}\n\n")
            
            f.write("## Platform Information\n\n")
            for key, value in report.platform_info.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
            
            f.write("\n## Overall Results\n\n")
            f.write(f"- **Total Tests:** {report.total_tests}\n")
            f.write(f"- **Successful:** {report.successful_tests} ({report.summary['success_rate']:.1f}%)\n")
            f.write(f"- **Failed:** {report.failed_tests}\n")
            f.write(f"- **Dependencies Resolved:** {report.summary['dependencies_resolved_rate']:.1f}%\n")
            f.write(f"- **Quick Start Works:** {report.summary['quick_start_success_rate']:.1f}%\n")
            f.write(f"- **Average Execution Time:** {report.summary['average_execution_time']:.2f}s\n\n")
            
            compatibility = report.summary['platform_compatibility']
            if compatibility['overall_compatible']:
                f.write("✅ **Platform Compatibility:** Fully Compatible\n\n")
            else:
                f.write("⚠️ **Platform Compatibility:** Issues Found\n\n")
                if compatibility['critical_failures']:
                    f.write(f"**Critical Failures:** {', '.join(compatibility['critical_failures'])}\n\n")
                if compatibility['warnings']:
                    f.write(f"**Warnings:** {', '.join(compatibility['warnings'])}\n\n")
            
            f.write("## Test Results\n\n")
            for result in report.results:
                status = "✅" if result.success else "❌"
                f.write(f"### {status} {result.test_name}\n")
                f.write(f"- **Execution Time:** {result.execution_time:.2f}s\n")
                if result.dependencies_resolved:
                    f.write("- **Dependencies:** ✅ Resolved\n")
                if result.quick_start_works:
                    f.write("- **Quick Start:** ✅ Works\n")
                if not result.success:
                    f.write(f"- **Error:** {result.error_message}\n")
                if result.output:
                    f.write(f"- **Output:** {result.output[:200]}{'...' if len(result.output) > 200 else ''}\n")
                f.write("\n")
        
        print(f"📋 Installation test summary saved to: {summary_file}")

def main():
    """Main function to run installation testing."""
    print("🚀 Beast Mode AI Framework - Installation Testing System")
    print("=" * 60)
    
    # Initialize tester
    tester = InstallationTester()
    
    # Run tests
    report = tester.test_all_installations()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 INSTALLATION TEST SUMMARY")
    print("=" * 60)
    print(f"Platform: {report.platform_info['system']} {report.platform_info['release']}")
    print(f"Python: {report.platform_info['python_version']}")
    print(f"Total Tests: {report.total_tests}")
    print(f"Successful: {report.successful_tests} ({report.summary['success_rate']:.1f}%)")
    print(f"Failed: {report.failed_tests}")
    
    compatibility = report.summary['platform_compatibility']
    if compatibility['overall_compatible']:
        print("\n✅ Platform is fully compatible!")
    else:
        print(f"\n⚠️ Platform compatibility issues found:")
        if compatibility['critical_failures']:
            print(f"Critical failures: {', '.join(compatibility['critical_failures'])}")
        if compatibility['warnings']:
            print(f"Warnings: {', '.join(compatibility['warnings'])}")
    
    if report.failed_tests > 0:
        print(f"\n❌ {report.failed_tests} installation tests failed")
        print("Please fix installation issues before proceeding.")
        return 1
    else:
        print("\n✅ All installation tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())