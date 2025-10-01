#!/usr/bin/env python3
"""
Generalized Pre-Launch Validator for Prepare Spec for Execution
==============================================================

Abstracts and generalizes the proven V2.0 prelaunch validation patterns from
documentation_index_prelaunch_check_v2.py and other V2 implementations.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.rm_ddd.core.dag_registry import DAGRegistry
from src.spec_framework.core.spec_analyzer import SpecAnalyzer, SpecificationData


class ValidationSeverity(Enum):
    """Validation result severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Individual validation result."""
    check_name: str
    severity: ValidationSeverity
    status: str  # "passed", "failed", "warning"
    message: str
    details: Optional[str] = None
    remediation: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class ValidationReport:
    """Complete validation report."""
    spec_name: str
    spec_path: Path
    overall_status: str  # "ready", "warnings", "failed"
    confidence_score: float = 0.0
    total_checks: int = 0
    passed_checks: int = 0
    warning_checks: int = 0
    failed_checks: int = 0
    critical_failures: int = 0
    validation_results: List[ValidationResult] = field(default_factory=list)
    execution_time: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PreLaunchValidator(ReflectiveModule):
    """Generalized pre-launch validation system based on proven V2 patterns."""
    
    def __init__(self):
        super().__init__()
        self.spec_analyzer = SpecAnalyzer()
        self.validation_cache: Dict[str, ValidationReport] = {}
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'validation_types': [
                'infrastructure', 'specification', 'dependencies', 
                'beast_mode', 'system_resources', 'permissions'
            ],
            'confidence_scoring': True,
            'remediation_guidance': True,
            'caching': True,
            'batch_validation': True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            'status': 'healthy',
            'cached_validations': len(self.validation_cache),
            'spec_analyzer_ready': True,
            'beast_mode_available': self._check_beast_mode_availability()
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'PreLaunchValidator',
            'version': '1.0.0',
            'description': 'Generalized pre-launch validation system',
            'dependencies': ['SpecAnalyzer', 'ReflectiveModule', 'DAGRegistry'],
            'workflow_control': 'prepare-spec-for-execution'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_validation'],
            'recommendation': 'Run with reduced validation scope'
        }
    
    def validate_specification_readiness(self, spec_path: str, 
                                       force_refresh: bool = False) -> ValidationReport:
        """Comprehensive specification readiness validation."""
        spec_path = Path(spec_path)
        cache_key = str(spec_path.absolute())
        
        # Check cache first
        if not force_refresh and cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        start_time = time.time()
        
        # Initialize report
        report = ValidationReport(
            spec_name=spec_path.name,
            spec_path=spec_path
        )
        
        print(f"🔍 Validating Specification Readiness: {spec_path.name}")
        print("=" * 60)
        
        # Run all validation checks
        self._validate_specification_structure(report)
        self._validate_beast_mode_infrastructure(report)
        self._validate_system_resources(report)
        self._validate_dependencies(report)
        self._validate_permissions(report)
        self._validate_dag_orchestration(report)
        
        # Calculate final scores and status
        self._calculate_validation_scores(report)
        self._generate_recommendations(report)
        
        report.execution_time = time.time() - start_time
        
        # Cache result
        self.validation_cache[cache_key] = report
        
        # Display summary
        self._display_validation_summary(report)
        
        return report
    
    def _validate_specification_structure(self, report: ValidationReport) -> None:
        """Validate specification file structure and completeness."""
        print("\n📋 Validating Specification Structure...")
        
        try:
            # Check for required files
            required_files = ['requirements.md', 'design.md', 'tasks.md']
            for file_name in required_files:
                file_path = report.spec_path / file_name
                
                if file_path.exists():
                    self._add_validation_result(report, 
                        f"spec_file_{file_name.replace('.', '_')}", 
                        ValidationSeverity.INFO, "passed",
                        f"✅ {file_name} exists"
                    )
                else:
                    self._add_validation_result(report,
                        f"spec_file_{file_name.replace('.', '_')}", 
                        ValidationSeverity.CRITICAL, "failed",
                        f"❌ {file_name} missing",
                        remediation=f"Create {file_name} file in specification directory"
                    )
            
            # Analyze specification content if files exist
            if all((report.spec_path / f).exists() for f in required_files):
                try:
                    spec_data = self.spec_analyzer.analyze_specification(str(report.spec_path))
                    
                    # Check completeness score
                    if spec_data.completeness_score >= 0.8:
                        self._add_validation_result(report,
                            "spec_completeness", ValidationSeverity.INFO, "passed",
                            f"✅ Specification completeness: {spec_data.completeness_score:.1%}"
                        )
                    elif spec_data.completeness_score >= 0.6:
                        self._add_validation_result(report,
                            "spec_completeness", ValidationSeverity.WARNING, "warning",
                            f"⚠️ Specification completeness: {spec_data.completeness_score:.1%}",
                            remediation="Consider adding missing requirements or task details"
                        )
                    else:
                        self._add_validation_result(report,
                            "spec_completeness", ValidationSeverity.ERROR, "failed",
                            f"❌ Low specification completeness: {spec_data.completeness_score:.1%}",
                            remediation="Specification needs significant improvement before execution"
                        )
                    
                    # Check for validation errors
                    if spec_data.validation_errors:
                        self._add_validation_result(report,
                            "spec_validation_errors", ValidationSeverity.WARNING, "warning",
                            f"⚠️ {len(spec_data.validation_errors)} validation issues found",
                            details="; ".join(spec_data.validation_errors[:3]),
                            remediation="Review and fix specification validation errors"
                        )
                    else:
                        self._add_validation_result(report,
                            "spec_validation_errors", ValidationSeverity.INFO, "passed",
                            "✅ No specification validation errors"
                        )
                    
                    # Store spec data for later use
                    report.metadata['spec_data'] = spec_data
                    
                except Exception as e:
                    self._add_validation_result(report,
                        "spec_analysis", ValidationSeverity.ERROR, "failed",
                        f"❌ Specification analysis failed: {str(e)}",
                        remediation="Check specification file format and content"
                    )
            
        except Exception as e:
            self._add_validation_result(report,
                "spec_structure", ValidationSeverity.CRITICAL, "failed",
                f"❌ Specification structure validation failed: {str(e)}"
            )
    
    def _validate_beast_mode_infrastructure(self, report: ValidationReport) -> None:
        """Validate Beast Mode infrastructure availability."""
        print("\n🐺 Validating Beast Mode Infrastructure...")
        
        try:
            # Test ReflectiveModule inheritance
            try:
                class TestModule(ReflectiveModule):
                    def get_capabilities(self): return {'test': True}
                    def get_health_status(self): return {'status': 'healthy'}
                    def get_module_info(self): return {'name': 'TestModule'}
                    def graceful_degradation(self, error): return {'degraded': True}
                
                test_module = TestModule()
                health = test_module.get_health_status()
                
                self._add_validation_result(report,
                    "reflective_module", ValidationSeverity.INFO, "passed",
                    "✅ ReflectiveModule inheritance working"
                )
                
            except Exception as e:
                self._add_validation_result(report,
                    "reflective_module", ValidationSeverity.CRITICAL, "failed",
                    f"❌ ReflectiveModule inheritance failed: {str(e)}",
                    remediation="Ensure Beast Mode infrastructure is properly installed"
                )
            
            # Test DAG Registry availability
            try:
                dag_registry = DAGRegistry()
                self._add_validation_result(report,
                    "dag_registry", ValidationSeverity.INFO, "passed",
                    "✅ DAG Registry available"
                )
            except Exception as e:
                self._add_validation_result(report,
                    "dag_registry", ValidationSeverity.ERROR, "failed",
                    f"❌ DAG Registry unavailable: {str(e)}",
                    remediation="Check DAG orchestration infrastructure"
                )
            
            # Test parallel execution engine
            try:
                from src.dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
                engine = ParallelExecutionEngine(max_workers=2)
                
                self._add_validation_result(report,
                    "parallel_execution_engine", ValidationSeverity.INFO, "passed",
                    "✅ Parallel Execution Engine available"
                )
            except Exception as e:
                self._add_validation_result(report,
                    "parallel_execution_engine", ValidationSeverity.ERROR, "failed",
                    f"❌ Parallel Execution Engine unavailable: {str(e)}",
                    remediation="Install DAG orchestration components"
                )
            
        except Exception as e:
            self._add_validation_result(report,
                "beast_mode_infrastructure", ValidationSeverity.CRITICAL, "failed",
                f"❌ Beast Mode infrastructure validation failed: {str(e)}"
            )
    
    def _validate_system_resources(self, report: ValidationReport) -> None:
        """Validate system resources and requirements."""
        print("\n💻 Validating System Resources...")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version >= (3, 9):
                self._add_validation_result(report,
                    "python_version", ValidationSeverity.INFO, "passed",
                    f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}"
                )
            else:
                self._add_validation_result(report,
                    "python_version", ValidationSeverity.ERROR, "failed",
                    f"❌ Python {python_version.major}.{python_version.minor} (requires 3.9+)",
                    remediation="Upgrade to Python 3.9 or higher"
                )
            
            # Check disk space
            try:
                import shutil
                total, used, free = shutil.disk_usage(report.spec_path)
                free_gb = free // (1024**3)
                
                if free_gb >= 5:
                    self._add_validation_result(report,
                        "disk_space", ValidationSeverity.INFO, "passed",
                        f"✅ Disk space: {free_gb}GB available"
                    )
                elif free_gb >= 1:
                    self._add_validation_result(report,
                        "disk_space", ValidationSeverity.WARNING, "warning",
                        f"⚠️ Low disk space: {free_gb}GB available",
                        remediation="Consider freeing up disk space"
                    )
                else:
                    self._add_validation_result(report,
                        "disk_space", ValidationSeverity.ERROR, "failed",
                        f"❌ Very low disk space: {free_gb}GB available",
                        remediation="Free up disk space before execution"
                    )
            except Exception as e:
                self._add_validation_result(report,
                    "disk_space", ValidationSeverity.WARNING, "warning",
                    f"⚠️ Could not check disk space: {str(e)}"
                )
            
            # Check memory (basic check)
            try:
                import psutil
                memory = psutil.virtual_memory()
                available_gb = memory.available // (1024**3)
                
                if available_gb >= 4:
                    self._add_validation_result(report,
                        "memory", ValidationSeverity.INFO, "passed",
                        f"✅ Available memory: {available_gb}GB"
                    )
                elif available_gb >= 2:
                    self._add_validation_result(report,
                        "memory", ValidationSeverity.WARNING, "warning",
                        f"⚠️ Limited memory: {available_gb}GB available",
                        remediation="Consider closing other applications"
                    )
                else:
                    self._add_validation_result(report,
                        "memory", ValidationSeverity.ERROR, "failed",
                        f"❌ Low memory: {available_gb}GB available",
                        remediation="Increase available memory before execution"
                    )
            except ImportError:
                self._add_validation_result(report,
                    "memory", ValidationSeverity.INFO, "passed",
                    "✅ Memory check skipped (psutil not available)"
                )
            except Exception as e:
                self._add_validation_result(report,
                    "memory", ValidationSeverity.WARNING, "warning",
                    f"⚠️ Could not check memory: {str(e)}"
                )
            
        except Exception as e:
            self._add_validation_result(report,
                "system_resources", ValidationSeverity.ERROR, "failed",
                f"❌ System resources validation failed: {str(e)}"
            )
    
    def _validate_dependencies(self, report: ValidationReport) -> None:
        """Validate required dependencies."""
        print("\n📦 Validating Dependencies...")
        
        # Core dependencies
        core_dependencies = [
            ('pathlib', 'pathlib'),
            ('typing', 'typing'),
            ('dataclasses', 'dataclasses'),
            ('json', 'json'),
            ('re', 're')
        ]
        
        # Optional dependencies
        optional_dependencies = [
            ('redis', 'redis'),
            ('psutil', 'psutil'),
            ('requests', 'requests')
        ]
        
        try:
            # Check core dependencies
            for dep_name, import_name in core_dependencies:
                try:
                    importlib.import_module(import_name)
                    self._add_validation_result(report,
                        f"dependency_{dep_name}", ValidationSeverity.INFO, "passed",
                        f"✅ {dep_name} available"
                    )
                except ImportError:
                    self._add_validation_result(report,
                        f"dependency_{dep_name}", ValidationSeverity.CRITICAL, "failed",
                        f"❌ {dep_name} missing",
                        remediation=f"Install {dep_name}: pip install {dep_name}"
                    )
            
            # Check optional dependencies
            for dep_name, import_name in optional_dependencies:
                try:
                    importlib.import_module(import_name)
                    self._add_validation_result(report,
                        f"optional_dependency_{dep_name}", ValidationSeverity.INFO, "passed",
                        f"✅ {dep_name} available (optional)"
                    )
                except ImportError:
                    self._add_validation_result(report,
                        f"optional_dependency_{dep_name}", ValidationSeverity.WARNING, "warning",
                        f"⚠️ {dep_name} not available (optional)",
                        remediation=f"Install for enhanced features: pip install {dep_name}"
                    )
            
        except Exception as e:
            self._add_validation_result(report,
                "dependencies", ValidationSeverity.ERROR, "failed",
                f"❌ Dependency validation failed: {str(e)}"
            )
    
    def _validate_permissions(self, report: ValidationReport) -> None:
        """Validate file and directory permissions."""
        print("\n🔐 Validating Permissions...")
        
        try:
            # Check read permissions on spec directory
            if os.access(report.spec_path, os.R_OK):
                self._add_validation_result(report,
                    "spec_read_permission", ValidationSeverity.INFO, "passed",
                    "✅ Specification directory readable"
                )
            else:
                self._add_validation_result(report,
                    "spec_read_permission", ValidationSeverity.CRITICAL, "failed",
                    "❌ Cannot read specification directory",
                    remediation="Check directory permissions"
                )
            
            # Check write permissions for output
            output_dir = report.spec_path.parent / "output"
            try:
                output_dir.mkdir(exist_ok=True)
                test_file = output_dir / "test_write.tmp"
                test_file.write_text("test")
                test_file.unlink()
                
                self._add_validation_result(report,
                    "output_write_permission", ValidationSeverity.INFO, "passed",
                    "✅ Output directory writable"
                )
            except Exception as e:
                self._add_validation_result(report,
                    "output_write_permission", ValidationSeverity.ERROR, "failed",
                    f"❌ Cannot write to output directory: {str(e)}",
                    remediation="Check write permissions or create output directory"
                )
            
        except Exception as e:
            self._add_validation_result(report,
                "permissions", ValidationSeverity.ERROR, "failed",
                f"❌ Permission validation failed: {str(e)}"
            )
    
    def _validate_dag_orchestration(self, report: ValidationReport) -> None:
        """Validate DAG orchestration capabilities."""
        print("\n🔄 Validating DAG Orchestration...")
        
        try:
            # Test task definition creation
            try:
                from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition
                
                def dummy_function():
                    return "test"
                
                test_task = TaskDefinition(
                    task_id="test_task",
                    name="Test Task",
                    execution_function=dummy_function
                )
                
                self._add_validation_result(report,
                    "task_definition", ValidationSeverity.INFO, "passed",
                    "✅ TaskDefinition creation working"
                )
                
            except Exception as e:
                self._add_validation_result(report,
                    "task_definition", ValidationSeverity.ERROR, "failed",
                    f"❌ TaskDefinition creation failed: {str(e)}",
                    remediation="Check DAG orchestration installation"
                )
            
            # Test execution tracking
            try:
                from src.execution_tracking.redis_execution_tracker import RedisExecutionTracker
                tracker = RedisExecutionTracker()
                
                self._add_validation_result(report,
                    "execution_tracking", ValidationSeverity.INFO, "passed",
                    "✅ Execution tracking available"
                )
                
            except Exception as e:
                self._add_validation_result(report,
                    "execution_tracking", ValidationSeverity.WARNING, "warning",
                    f"⚠️ Execution tracking limited: {str(e)}",
                    remediation="Install Redis for full execution tracking"
                )
            
        except Exception as e:
            self._add_validation_result(report,
                "dag_orchestration", ValidationSeverity.ERROR, "failed",
                f"❌ DAG orchestration validation failed: {str(e)}"
            )
    
    def _add_validation_result(self, report: ValidationReport, check_name: str, 
                              severity: ValidationSeverity, status: str, message: str,
                              details: Optional[str] = None, remediation: Optional[str] = None) -> None:
        """Add validation result to report."""
        result = ValidationResult(
            check_name=check_name,
            severity=severity,
            status=status,
            message=message,
            details=details,
            remediation=remediation
        )
        
        report.validation_results.append(result)
        report.total_checks += 1
        
        if status == "passed":
            report.passed_checks += 1
        elif status == "warning":
            report.warning_checks += 1
        elif status == "failed":
            report.failed_checks += 1
            if severity == ValidationSeverity.CRITICAL:
                report.critical_failures += 1
    
    def _calculate_validation_scores(self, report: ValidationReport) -> None:
        """Calculate validation scores and overall status."""
        if report.total_checks == 0:
            report.confidence_score = 0.0
            report.overall_status = "failed"
            return
        
        # Calculate confidence score
        passed_weight = 1.0
        warning_weight = 0.5
        failed_weight = 0.0
        
        weighted_score = (
            report.passed_checks * passed_weight +
            report.warning_checks * warning_weight +
            report.failed_checks * failed_weight
        )
        
        report.confidence_score = weighted_score / report.total_checks
        
        # Determine overall status
        if report.critical_failures > 0:
            report.overall_status = "failed"
        elif report.failed_checks > 0:
            report.overall_status = "failed"
        elif report.warning_checks > 0:
            report.overall_status = "warnings"
        else:
            report.overall_status = "ready"
    
    def _generate_recommendations(self, report: ValidationReport) -> None:
        """Generate recommendations based on validation results."""
        if report.overall_status == "ready":
            report.recommendations.append("✅ Specification is ready for execution")
            report.recommendations.append("🚀 You can proceed with launching the implementation")
        
        elif report.overall_status == "warnings":
            report.recommendations.append("⚠️ Specification has warnings but can proceed")
            report.recommendations.append("📋 Review warnings and consider addressing them")
            
            # Add specific remediation suggestions
            for result in report.validation_results:
                if result.status == "warning" and result.remediation:
                    report.recommendations.append(f"• {result.remediation}")
        
        else:  # failed
            report.recommendations.append("❌ Specification is not ready for execution")
            report.recommendations.append("🔧 Address critical issues before proceeding")
            
            # Add specific remediation suggestions
            for result in report.validation_results:
                if result.status == "failed" and result.remediation:
                    report.recommendations.append(f"• {result.remediation}")
    
    def _display_validation_summary(self, report: ValidationReport) -> None:
        """Display validation summary."""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"Specification: {report.spec_name}")
        print(f"Overall Status: {report.overall_status.upper()}")
        print(f"Confidence Score: {report.confidence_score:.1%}")
        print(f"Execution Time: {report.execution_time:.2f}s")
        
        print(f"\nResults: {report.passed_checks} passed, {report.warning_checks} warnings, {report.failed_checks} failed")
        
        if report.critical_failures > 0:
            print(f"❌ Critical Failures: {report.critical_failures}")
        
        print("\n📋 RECOMMENDATIONS:")
        for recommendation in report.recommendations:
            print(f"  {recommendation}")
        
        if report.overall_status == "ready":
            print("\n🎉 Ready to proceed with execution!")
        elif report.overall_status == "warnings":
            print("\n⚠️ Proceed with caution - review warnings")
        else:
            print("\n🛑 Do not proceed - fix critical issues first")
    
    def _check_beast_mode_availability(self) -> bool:
        """Check if Beast Mode infrastructure is available."""
        try:
            from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
            from src.rm_ddd.core.dag_registry import DAGRegistry
            return True
        except ImportError:
            return False


# Convenience functions
def validate_spec_readiness(spec_path: str, force_refresh: bool = False) -> ValidationReport:
    """Validate specification readiness for execution."""
    validator = PreLaunchValidator()
    return validator.validate_specification_readiness(spec_path, force_refresh)


def quick_validation_check(spec_path: str) -> bool:
    """Quick validation check - returns True if ready."""
    validator = PreLaunchValidator()
    report = validator.validate_specification_readiness(spec_path)
    return report.overall_status in ["ready", "warnings"]


def get_validation_confidence(spec_path: str) -> float:
    """Get validation confidence score (0.0 to 1.0)."""
    validator = PreLaunchValidator()
    report = validator.validate_specification_readiness(spec_path)
    return report.confidence_score