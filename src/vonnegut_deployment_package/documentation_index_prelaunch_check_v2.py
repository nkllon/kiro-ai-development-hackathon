#!/usr/bin/env python3
"""
Prelaunch validation for Documentation Index Generator implementation.
Validates infrastructure readiness and system prerequisites.
Generated using proven spec-creation-dag-compliance patterns v2.0.
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

class DocumentationIndexPrelaunchValidator(ReflectiveModule):
    """Validates readiness for Documentation Index Generator implementation."""
    
    def __init__(self):
        super().__init__()
        self.validation_results = {}
        self.critical_failures = []
        self.warnings = []
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'validation_types': ['infrastructure', 'documentation_access', 'indexing_tools', 'beast_mode'],
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
            'name': 'DocumentationIndexPrelaunchValidator',
            'version': '2.0.0',
            'description': 'Validates readiness for Documentation Index Generator implementation',
            'dependencies': ['ReflectiveModule', 'DAGRegistry'],
            'workflow_control': 'spec-creation-dag-compliance-v2'
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
        print("🔍 Validating Documentation Index Generator Infrastructure Readiness...")
        
        # Core infrastructure validation
        self._validate_beast_mode_infrastructure()
        self._validate_documentation_access()
        self._validate_indexing_tools()
        self._validate_specification_structure()
        
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
            dag_registry.register_module('test_doc_task_1', dependencies=[])
            dag_registry.register_module('test_doc_task_2', dependencies=['test_doc_task_1'])
            dependencies = dag_registry.get_dependency_chain('test_doc_task_2')
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
    
    def _validate_documentation_access(self):
        """Validate documentation access and file system functionality."""
        print("\n📁 Validating Documentation Access...")
        
        # Check for documentation directories
        doc_paths = [
            Path('docs'),
            Path('.kiro/specs'),
            Path('README.md'),
            Path('CONTRIBUTING.md')
        ]
        
        accessible_docs = 0
        for doc_path in doc_paths:
            if doc_path.exists():
                accessible_docs += 1
                print(f"  ✅ Found: {doc_path}")
            else:
                print(f"  ⚠️  Missing: {doc_path}")
        
        if accessible_docs >= 2:
            self.validation_results['documentation_access'] = {
                'status': 'available',
                'details': f'{accessible_docs}/{len(doc_paths)} documentation sources found',
                'confidence': 0.8 + (accessible_docs / len(doc_paths)) * 0.2
            }
            print(f"  ✅ Documentation Access: {accessible_docs}/{len(doc_paths)} sources available")
        else:
            self.critical_failures.append("Insufficient documentation sources found")
            self.validation_results['documentation_access'] = {
                'status': 'insufficient',
                'details': f'Only {accessible_docs}/{len(doc_paths)} documentation sources found',
                'confidence': 0.3
            }
            print(f"  ❌ Documentation Access: Insufficient sources ({accessible_docs}/{len(doc_paths)})")
        
        # Check file system permissions
        try:
            test_file = Path('test_doc_access.tmp')
            test_file.write_text("test")
            test_file.unlink()
            
            self.validation_results['filesystem_access'] = {
                'status': 'available',
                'details': 'File system read/write access confirmed',
                'confidence': 0.95
            }
            print("  ✅ File System Access: READ/WRITE permissions confirmed")
        except Exception as e:
            self.critical_failures.append(f"File system access failed: {e}")
            self.validation_results['filesystem_access'] = {
                'status': 'failed',
                'details': str(e),
                'confidence': 0.0
            }
            print(f"  ❌ File System Access: FAILED - {e}")
    
    def _validate_indexing_tools(self):
        """Validate indexing tools and dependencies."""
        print("\n🔧 Validating Indexing Tools...")
        
        # Check Python and required modules
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
        
        # Check for text processing capabilities
        required_modules = ['pathlib', 'json', 'hashlib', 're']
        available_modules = 0
        
        for module_name in required_modules:
            try:
                __import__(module_name)
                available_modules += 1
                print(f"  ✅ Module: {module_name}")
            except ImportError:
                print(f"  ❌ Module: {module_name} (missing)")
        
        if available_modules == len(required_modules):
            self.validation_results['indexing_modules'] = {
                'status': 'available',
                'details': f'All {len(required_modules)} required modules available',
                'confidence': 0.95
            }
            print(f"  ✅ Indexing Modules: All {len(required_modules)} available")
        else:
            missing_count = len(required_modules) - available_modules
            self.critical_failures.append(f"{missing_count} required modules missing")
            self.validation_results['indexing_modules'] = {
                'status': 'incomplete',
                'details': f'{missing_count} modules missing',
                'confidence': 0.3
            }
            print(f"  ❌ Indexing Modules: {missing_count} missing")
    
    def _validate_specification_structure(self):
        """Validate specification directory structure."""
        print("\n📁 Validating Specification Structure...")
        
        spec_path = Path('.kiro/specs/documentation-index-generator')
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
        
        if any(result.get('status') == 'failed' for result in self.validation_results.values()):
            recommendations.append("Fix failed infrastructure components")
        
        if len(self.warnings) > 3:
            recommendations.append("Address warnings to improve implementation success rate")
        
        if not recommendations:
            recommendations.append("System is ready for Documentation Index Generator implementation")
        
        return recommendations

def main():
    """Main execution function."""
    print("🚀 Documentation Index Generator - Prelaunch Validation v2.0")
    print("=" * 70)
    
    try:
        validator = DocumentationIndexPrelaunchValidator()
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