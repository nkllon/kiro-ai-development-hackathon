#!/usr/bin/env python3
"""
Repository Setup and Installation - Prelaunch Validation
Validates infrastructure readiness using updated workflow control patterns.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    from src.rm_ddd.core.dag_registry import DAGRegistry
except ImportError as e:
    print(f"❌ Critical import failure: {e}")
    print("Ensure Beast Mode infrastructure is available")
    sys.exit(1)

class RepositorySetupPrelaunchValidator(ReflectiveModule):
    """Validates readiness for Repository Setup and Installation implementation."""
    
    def __init__(self):
        super().__init__()
        self.validation_results = {}
        self.critical_failures = []
        self.warnings = []
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'validation_types': ['infrastructure', 'repository_health', 'installation_readiness'],
            'readiness_assessment': True,
            'confidence_scoring': True,
            'remediation_guidance': True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            'status': 'healthy',
            'validation_results_count': len(self.validation_results),
            'critical_failures_count': len(self.critical_failures),
            'warnings_count': len(self.warnings)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'RepositorySetupPrelaunchValidator',
            'version': '1.0.0',
            'description': 'Validates readiness for Repository Setup and Installation implementation',
            'dependencies': ['ReflectiveModule', 'DAGRegistry']
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_validation'],
            'recommendation': 'Run with reduced validation scope'
        }
        
    def validate_infrastructure_readiness(self) -> Dict[str, Any]:
        """Comprehensive infrastructure readiness validation."""
        print("🔍 Validating Repository Setup Infrastructure Readiness...")
        
        # Core infrastructure validation
        self._validate_beast_mode_infrastructure()
        self._validate_repository_structure()
        self._validate_development_environment()
        self._validate_installation_prerequisites()
        self._validate_specification_completeness()
        
        return self._generate_readiness_report()
    
    def _validate_beast_mode_infrastructure(self):
        """Validate Beast Mode infrastructure availability."""
        print("\n📊 Validating Beast Mode Infrastructure...")
        
        # Test ReflectiveModule inheritance
        try:
            class TestModule(ReflectiveModule):
                def get_capabilities(self): return {'test': True}
                def get_health_status(self): return {'status': 'healthy'}
                def get_module_info(self): return {'name': 'TestModule'}
                def graceful_degradation(self, error): return {'degraded': True}
            
            test_module = TestModule()
            health = test_module.get_health_status()
            
            self.validation_results['reflective_module'] = {
                'status': 'available',
                'details': 'ReflectiveModule inheritance working with abstract methods',
                'confidence': 0.95
            }
            print("  ✅ ReflectiveModule inheritance: AVAILABLE")
        except Exception as e:
            self.critical_failures.append(f"ReflectiveModule inheritance failed: {e}")
            self.validation_results['reflective_module'] = {
                'status': 'failed',
                'details': str(e),
                'confidence': 0.0
            }
            print(f"  ❌ ReflectiveModule inheritance: FAILED - {e}")
        
        # Test DAG Registry availability
        try:
            dag_registry = DAGRegistry()
            dag_registry.register_module('test_task_1', dependencies=[])
            dag_registry.register_module('test_task_2', dependencies=['test_task_1'])
            dependencies = dag_registry.get_dependency_chain('test_task_2')
            stats = dag_registry.get_registry_stats()
            
            self.validation_results['dag_registry'] = {
                'status': 'available',
                'details': f'DAG Registry operational with {stats.get("total_modules", 0)} modules',
                'confidence': 0.98
            }
            print("  ✅ DAG Registry: AVAILABLE")
        except Exception as e:
            self.critical_failures.append(f"DAG Registry validation failed: {e}")
            self.validation_results['dag_registry'] = {
                'status': 'failed',
                'details': str(e),
                'confidence': 0.0
            }
            print(f"  ❌ DAG Registry: FAILED - {e}")
    
    def _validate_repository_structure(self):
        """Validate repository structure and specification completeness."""
        print("\n📁 Validating Repository Structure...")
        
        spec_path = Path('.kiro/specs/repository-setup-and-installation')
        required_files = ['requirements.md', 'design.md', 'tasks.md']
        
        if spec_path.exists():
            missing_files = []
            for file_name in required_files:
                file_path = spec_path / file_name
                if not file_path.exists():
                    missing_files.append(file_name)
            
            if not missing_files:
                self.validation_results['specification_structure'] = {
                    'status': 'complete',
                    'details': f'All {len(required_files)} specification files present',
                    'confidence': 0.95
                }
                print(f"  ✅ Specification Files: All {len(required_files)} present")
            else:
                self.warnings.append(f"Missing specification files: {missing_files}")
                self.validation_results['specification_structure'] = {
                    'status': 'incomplete',
                    'details': f'Missing files: {missing_files}',
                    'confidence': 0.5
                }
                print(f"  ⚠️  Specification Files: Missing {missing_files}")
        else:
            self.critical_failures.append("Specification directory not found")
            self.validation_results['specification_structure'] = {
                'status': 'missing',
                'details': 'Specification directory not found',
                'confidence': 0.0
            }
            print("  ❌ Specification Directory: NOT FOUND")
    
    def _validate_development_environment(self):
        """Validate development environment readiness."""
        print("\n💻 Validating Development Environment...")
        
        # Python version check
        python_version = sys.version_info
        if python_version >= (3, 9):
            self.validation_results['python_version'] = {
                'status': 'compatible',
                'details': f'Python {python_version.major}.{python_version.minor}.{python_version.micro}',
                'confidence': 0.95
            }
            print(f"  ✅ Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self.critical_failures.append(f"Python version {python_version.major}.{python_version.minor} < 3.9")
            self.validation_results['python_version'] = {
                'status': 'incompatible',
                'details': f'Python {python_version.major}.{python_version.minor} < 3.9 required',
                'confidence': 0.0
            }
            print(f"  ❌ Python Version: {python_version.major}.{python_version.minor} (requires 3.9+)")
        
        # Git availability check
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                git_version = result.stdout.strip()
                self.validation_results['git_availability'] = {
                    'status': 'available',
                    'details': git_version,
                    'confidence': 0.95
                }
                print(f"  ✅ Git: {git_version}")
            else:
                self.critical_failures.append("Git command failed")
                self.validation_results['git_availability'] = {
                    'status': 'failed',
                    'details': 'Git command execution failed',
                    'confidence': 0.0
                }
                print("  ❌ Git: Command execution failed")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.critical_failures.append(f"Git not available: {e}")
            self.validation_results['git_availability'] = {
                'status': 'missing',
                'details': str(e),
                'confidence': 0.0
            }
            print(f"  ❌ Git: NOT AVAILABLE - {e}")
    
    def _validate_installation_prerequisites(self):
        """Validate installation prerequisites and system readiness."""
        print("\n🔧 Validating Installation Prerequisites...")
        
        # Check for Makefile
        makefile_path = Path('Makefile')
        if makefile_path.exists():
            try:
                content = makefile_path.read_text()
                if 'install:' in content:
                    self.validation_results['makefile_install'] = {
                        'status': 'available',
                        'details': 'Makefile with install target found',
                        'confidence': 0.90
                    }
                    print("  ✅ Makefile install target: AVAILABLE")
                else:
                    self.warnings.append("Makefile exists but no install target found")
                    self.validation_results['makefile_install'] = {
                        'status': 'incomplete',
                        'details': 'Makefile exists but no install target',
                        'confidence': 0.3
                    }
                    print("  ⚠️  Makefile install target: MISSING")
            except Exception as e:
                self.warnings.append(f"Could not read Makefile: {e}")
                self.validation_results['makefile_install'] = {
                    'status': 'error',
                    'details': str(e),
                    'confidence': 0.0
                }
                print(f"  ❌ Makefile: READ ERROR - {e}")
        else:
            self.warnings.append("Makefile not found")
            self.validation_results['makefile_install'] = {
                'status': 'missing',
                'details': 'Makefile not found',
                'confidence': 0.0
            }
            print("  ⚠️  Makefile: NOT FOUND")
        
        # Check write permissions for key directories
        key_dirs = ['.kiro', 'src', 'scripts']
        permission_issues = []
        
        for dir_name in key_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                if not os.access(dir_path, os.W_OK):
                    permission_issues.append(dir_name)
            else:
                # Check if we can create the directory
                try:
                    test_dir = dir_path / 'test_write'
                    test_dir.mkdir(parents=True, exist_ok=True)
                    test_dir.rmdir()
                except Exception:
                    permission_issues.append(dir_name)
        
        if not permission_issues:
            self.validation_results['directory_permissions'] = {
                'status': 'adequate',
                'details': f'Write access confirmed for {len(key_dirs)} key directories',
                'confidence': 0.90
            }
            print(f"  ✅ Directory Permissions: Adequate for {len(key_dirs)} directories")
        else:
            self.warnings.append(f"Permission issues in directories: {permission_issues}")
            self.validation_results['directory_permissions'] = {
                'status': 'limited',
                'details': f'Permission issues: {permission_issues}',
                'confidence': 0.4
            }
            print(f"  ⚠️  Directory Permissions: Issues in {permission_issues}")
    
    def _validate_specification_completeness(self):
        """Validate specification completeness and task readiness."""
        print("\n📋 Validating Specification Completeness...")
        
        spec_path = Path('.kiro/specs/repository-setup-and-installation')
        
        if not spec_path.exists():
            self.critical_failures.append("Specification directory missing")
            return
        
        # Check tasks.md for implementation readiness
        tasks_file = spec_path / 'tasks.md'
        if tasks_file.exists():
            try:
                content = tasks_file.read_text()
                
                # Count total tasks and completed tasks
                total_tasks = content.count('- [ ]') + content.count('- [x]')
                completed_tasks = content.count('- [x]')
                
                if total_tasks > 0:
                    completion_rate = (completed_tasks / total_tasks) * 100
                    self.validation_results['task_completeness'] = {
                        'status': 'analyzed',
                        'details': f'{completed_tasks}/{total_tasks} tasks completed ({completion_rate:.1f}%)',
                        'confidence': 0.85,
                        'completion_rate': completion_rate
                    }
                    print(f"  📊 Task Analysis: {completed_tasks}/{total_tasks} completed ({completion_rate:.1f}%)")
                    
                    if completion_rate < 10:
                        print(f"  💡 Ready for implementation - most tasks are pending")
                    elif completion_rate > 90:
                        print(f"  🎉 Implementation nearly complete!")
                    else:
                        print(f"  🔄 Implementation in progress")
                else:
                    self.warnings.append("No tasks found in tasks.md")
                    self.validation_results['task_completeness'] = {
                        'status': 'empty',
                        'details': 'No tasks found in tasks.md',
                        'confidence': 0.2
                    }
                    print("  ⚠️  Task Analysis: No tasks found")
                    
            except Exception as e:
                self.warnings.append(f"Could not analyze tasks.md: {e}")
                self.validation_results['task_completeness'] = {
                    'status': 'error',
                    'details': str(e),
                    'confidence': 0.0
                }
                print(f"  ❌ Task Analysis: ERROR - {e}")
        else:
            self.warnings.append("tasks.md file not found")
            self.validation_results['task_completeness'] = {
                'status': 'missing',
                'details': 'tasks.md file not found',
                'confidence': 0.0
            }
            print("  ❌ Task Analysis: tasks.md NOT FOUND")
    
    def _generate_readiness_report(self) -> Dict[str, Any]:
        """Generate comprehensive readiness report."""
        print("\n📋 Generating Readiness Report...")
        
        # Calculate overall readiness score
        total_confidence = sum(result.get('confidence', 0) for result in self.validation_results.values())
        max_confidence = len(self.validation_results)
        overall_confidence = (total_confidence / max_confidence) if max_confidence > 0 else 0
        
        # Determine readiness status
        if len(self.critical_failures) == 0 and overall_confidence >= 0.8:
            readiness_status = "READY"
            readiness_color = "🟢"
        elif len(self.critical_failures) == 0 and overall_confidence >= 0.6:
            readiness_status = "READY_WITH_WARNINGS"
            readiness_color = "🟡"
        else:
            readiness_status = "NOT_READY"
            readiness_color = "🔴"
        
        report = {
            'overall_status': readiness_status,
            'confidence_score': overall_confidence,
            'critical_failures': self.critical_failures,
            'warnings': self.warnings,
            'validation_results': self.validation_results,
            'recommendations': self._generate_recommendations()
        }
        
        # Print summary
        print(f"\n{readiness_color} READINESS STATUS: {readiness_status}")
        print(f"📊 Confidence Score: {overall_confidence:.2f} ({overall_confidence*100:.1f}%)")
        
        if self.critical_failures:
            print(f"\n❌ Critical Failures ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"  • {failure}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        if self.critical_failures:
            recommendations.append("Resolve all critical failures before proceeding with implementation")
        
        if any(result.get('status') == 'missing' for result in self.validation_results.values()):
            recommendations.append("Install missing prerequisites and dependencies")
        
        task_result = self.validation_results.get('task_completeness', {})
        completion_rate = task_result.get('completion_rate', 0)
        if completion_rate < 10:
            recommendations.append("Ready to begin implementation - start with Phase 1 tasks")
        elif completion_rate > 90:
            recommendations.append("Implementation nearly complete - focus on final validation and testing")
        
        if len(self.warnings) > 3:
            recommendations.append("Address warnings to improve implementation success rate")
        
        if not recommendations:
            recommendations.append("System is ready for Repository Setup and Installation implementation")
        
        return recommendations

def main():
    """Main execution function."""
    print("🚀 Repository Setup and Installation - Prelaunch Validation")
    print("=" * 70)
    
    try:
        validator = RepositorySetupPrelaunchValidator()
        report = validator.validate_infrastructure_readiness()
        
        # Exit with appropriate code
        if report['overall_status'] == 'READY':
            print(f"\n✅ VALIDATION COMPLETE: System ready for implementation")
            sys.exit(0)
        elif report['overall_status'] == 'READY_WITH_WARNINGS':
            print(f"\n⚠️  VALIDATION COMPLETE: Ready with warnings - proceed with caution")
            sys.exit(0)
        else:
            print(f"\n❌ VALIDATION FAILED: Resolve critical issues before proceeding")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 VALIDATION ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()