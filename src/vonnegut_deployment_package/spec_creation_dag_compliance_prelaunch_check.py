#!/usr/bin/env python3
"""
Prelaunch validation for Spec Creation DAG Compliance implementation.
Validates infrastructure readiness and system prerequisites.
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

class SpecCreationDAGCompliancePrelaunchValidator(ReflectiveModule):
    """Validates readiness for Spec Creation DAG Compliance implementation."""
    
    def __init__(self):
        super().__init__()
        self.validation_results = {}
        self.critical_failures = []
        self.warnings = []
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'validation_types': ['infrastructure', 'dag_orchestration', 'beast_mode', 'development_environment'],
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
            'name': 'SpecCreationDAGCompliancePrelaunchValidator',
            'version': '1.0.0',
            'description': 'Validates readiness for Spec Creation DAG Compliance implementation',
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
        print("🔍 Validating Spec Creation DAG Compliance Infrastructure Readiness...")
        
        # Core infrastructure validation
        self._validate_beast_mode_infrastructure()
        self._validate_dag_orchestration_components()
        self._validate_development_environment()
        self._validate_specification_structure()
        self._validate_existing_patterns()
        
        return self._generate_readiness_report()
    
    def _validate_beast_mode_infrastructure(self):
        """Validate Beast Mode infrastructure availability."""
        print("\n📊 Validating Beast Mode Infrastructure...")
        
        # Test ReflectiveModule inheritance
        try:
            # Create a proper test module with required abstract methods
            class TestModule(ReflectiveModule):
                def get_capabilities(self): return {'test': True}
                def get_health_status(self): return {'status': 'healthy'}
                def get_module_info(self): return {'name': 'TestModule'}
                def graceful_degradation(self, error): return {'degraded': True}
            
            test_module = TestModule()
            # Test that it has the expected ReflectiveModule functionality
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
            # Test basic DAG operations using actual API
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
    
    def _validate_dag_orchestration_components(self):
        """Validate DAG orchestration infrastructure components."""
        print("\n🔄 Validating DAG Orchestration Components...")
        
        components = [
            ('ParallelExecutionEngine', 'src.dag_orchestration.execution.parallel_execution_engine'),
            ('InfrastructureValidator', 'src.dag_orchestration.core.infrastructure_validator'),
            ('DependencyAwareScheduler', 'src.dag_orchestration.execution.dependency_aware_scheduler'),
            ('DAGOrchestrator', 'src.dag_orchestration.core.dag_orchestrator')
        ]
        
        for component_name, module_path in components:
            try:
                spec = importlib.util.find_spec(module_path)
                if spec is not None:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    self.validation_results[f'dag_{component_name.lower()}'] = {
                        'status': 'available',
                        'details': f'{component_name} module accessible',
                        'confidence': 0.90
                    }
                    print(f"  ✅ {component_name}: AVAILABLE")
                else:
                    self.warnings.append(f"{component_name} module not found at {module_path}")
                    self.validation_results[f'dag_{component_name.lower()}'] = {
                        'status': 'missing',
                        'details': f'{component_name} module not found',
                        'confidence': 0.0
                    }
                    print(f"  ⚠️  {component_name}: MISSING")
            except Exception as e:
                self.warnings.append(f"{component_name} validation failed: {e}")
                self.validation_results[f'dag_{component_name.lower()}'] = {
                    'status': 'error',
                    'details': str(e),
                    'confidence': 0.0
                }
                print(f"  ❌ {component_name}: ERROR - {e}")
    
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
        
        # Required packages check
        required_packages = ['pathlib', 'typing', 'dataclasses', 'enum', 'datetime']
        missing_packages = []
        
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            self.validation_results['required_packages'] = {
                'status': 'available',
                'details': f'All {len(required_packages)} required packages available',
                'confidence': 0.95
            }
            print(f"  ✅ Required Packages: All {len(required_packages)} available")
        else:
            self.critical_failures.append(f"Missing packages: {missing_packages}")
            self.validation_results['required_packages'] = {
                'status': 'missing',
                'details': f'Missing packages: {missing_packages}',
                'confidence': 0.0
            }
            print(f"  ❌ Required Packages: Missing {missing_packages}")
    
    def _validate_specification_structure(self):
        """Validate specification directory structure."""
        print("\n📁 Validating Specification Structure...")
        
        spec_path = Path('.kiro/specs/spec-creation-dag-compliance')
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
    
    def _validate_existing_patterns(self):
        """Validate existing specification patterns for migration analysis."""
        print("\n🔍 Analyzing Existing Specification Patterns...")
        
        specs_dir = Path('.kiro/specs')
        if specs_dir.exists():
            spec_dirs = [d for d in specs_dir.iterdir() if d.is_dir()]
            
            # Analyze pattern compliance
            compliant_specs = 0
            non_compliant_specs = 0
            
            for spec_dir in spec_dirs:
                if spec_dir.name == 'spec-creation-dag-compliance':
                    continue  # Skip self
                
                # Skip system directories
                if spec_dir.name.startswith('.'):
                    continue
                
                # Check for ReflectiveModule patterns in design docs
                design_file = spec_dir / 'design.md'
                if design_file.exists():
                    try:
                        # Safe file reading with encoding handling
                        content = design_file.read_text(encoding='utf-8')
                        if 'ReflectiveModule' in content and 'ADR' in content:
                            compliant_specs += 1
                        else:
                            non_compliant_specs += 1
                    except UnicodeDecodeError:
                        # Skip files with encoding issues
                        self.warnings.append(f"Could not read {design_file} due to encoding issues")
                        non_compliant_specs += 1
                    except Exception as e:
                        self.warnings.append(f"Error reading {design_file}: {e}")
                        non_compliant_specs += 1
                else:
                    non_compliant_specs += 1
            
            total_specs = compliant_specs + non_compliant_specs
            compliance_rate = (compliant_specs / total_specs * 100) if total_specs > 0 else 0
            
            self.validation_results['existing_patterns'] = {
                'status': 'analyzed',
                'details': f'{compliant_specs}/{total_specs} specs compliant ({compliance_rate:.1f}%)',
                'confidence': 0.80,
                'migration_needed': non_compliant_specs
            }
            print(f"  📊 Pattern Analysis: {compliant_specs}/{total_specs} compliant ({compliance_rate:.1f}%)")
            
            if non_compliant_specs > 0:
                print(f"  ⚠️  Migration Required: {non_compliant_specs} specifications need updating")
        else:
            self.warnings.append("Specifications directory not found")
            self.validation_results['existing_patterns'] = {
                'status': 'missing',
                'details': 'Specifications directory not found',
                'confidence': 0.0
            }
            print("  ❌ Specifications Directory: NOT FOUND")
    
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
            recommendations.append("Install missing DAG orchestration components")
        
        migration_needed = self.validation_results.get('existing_patterns', {}).get('migration_needed', 0)
        if migration_needed > 0:
            recommendations.append(f"Plan migration for {migration_needed} non-compliant specifications")
        
        if len(self.warnings) > 3:
            recommendations.append("Address warnings to improve implementation success rate")
        
        if not recommendations:
            recommendations.append("System is ready for Spec Creation DAG Compliance implementation")
        
        return recommendations

def main():
    """Main execution function."""
    print("🚀 Spec Creation DAG Compliance - Prelaunch Validation")
    print("=" * 60)
    
    try:
        validator = SpecCreationDAGCompliancePrelaunchValidator()
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