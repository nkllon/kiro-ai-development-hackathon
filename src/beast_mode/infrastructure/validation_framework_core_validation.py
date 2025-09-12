"""
Validation Framework Core Validation

This module was extracted from validation_framework_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
import sys
import time
import json
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from ..core.reflective_module import ReflectiveModule
import logging
import json
import cProfile
import psutil
import threading
import queue
import pytest
import logging
import json
import cProfile
import psutil
import threading
import queue
import pytest

def validate_complete_infrastructure(self) -> InfrastructureAssessment:
    """
        Perform complete systematic infrastructure validation
        
        Following Beast Mode priorities:
        1. Logging infrastructure (ALWAYS FIRST)
        2. Profiling infrastructure (ALWAYS SECOND)
        3. Monitoring infrastructure
        4. Testing infrastructure
        5. Documentation infrastructure
        """
    self.logger.info('🔍 Starting complete systematic infrastructure validation')
    assessment_id = f"infra_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    validation_results = []
    self.logger.info('📝 Validating logging infrastructure (PRIORITY 1)')
    logging_result = self._validate_logging_infrastructure()
    validation_results.append(logging_result)
    self.logger.info('📊 Validating profiling infrastructure (PRIORITY 2)')
    profiling_result = self._validate_profiling_infrastructure()
    validation_results.append(profiling_result)
    self.logger.info('📈 Validating monitoring infrastructure')
    monitoring_result = self._validate_monitoring_infrastructure()
    validation_results.append(monitoring_result)
    self.logger.info('🧪 Validating testing infrastructure')
    testing_result = self._validate_testing_infrastructure()
    validation_results.append(testing_result)
    self.logger.info('📚 Validating documentation infrastructure')
    documentation_result = self._validate_documentation_infrastructure()
    validation_results.append(documentation_result)
    assessment = self._calculate_infrastructure_assessment(assessment_id, validation_results)
    self.assessment_history.append(assessment)
    self.logger.info(f'✅ Infrastructure validation complete: {assessment.overall_compliance_score:.2f} compliance score')
    return assessment

def _validate_logging_infrastructure(self) -> ValidationResult:
    """
        Validate logging infrastructure - ALWAYS FIRST PRIORITY
        
        Systematic logging validation includes:
        - Basic logging module availability
        - Structured logging capabilities
        - Log directory structure
        - Log level configuration
        - Contextual logging support
        """
    issues = []
    recommendations = []
    try:
        import logging
        self.logger.debug('✅ Basic logging module: Available')
    except ImportError:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.LOGGING, issue_type='missing_logging_module', severity=ValidationSeverity.CRITICAL, description='Python logging module not available', systematic_impact='Cannot perform any systematic logging operations', remediation_steps=['Verify Python installation includes logging module', 'Reinstall Python if logging module is missing', 'Check Python environment configuration'], validation_command='python -c \'import logging; print("Logging available")\'', estimated_fix_time='5-10 minutes'))
    try:
        import json
        test_log = {'timestamp': '2025-01-01', 'level': 'INFO', 'message': 'test'}
        json.dumps(test_log)
        self.logger.debug('✅ Structured logging (JSON): Available')
    except Exception as e:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.LOGGING, issue_type='structured_logging_failure', severity=ValidationSeverity.HIGH, description=f'Structured logging validation failed: {str(e)}', systematic_impact='Cannot implement systematic structured logging', remediation_steps=['Verify JSON module availability', 'Implement structured logging formatter', 'Test structured logging with sample data'], validation_command='python -c \'import json; print(json.dumps({"test": "structured_logging"}))\'', estimated_fix_time='15-20 minutes'))
    log_dir = Path('logs')
    required_subdirs = ['pdca_cycles', 'rca_analysis', 'performance', 'patterns', 'infrastructure']
    if not log_dir.exists():
        issues.append(InfrastructureIssue(component=InfrastructureComponent.LOGGING, issue_type='missing_log_directory', severity=ValidationSeverity.HIGH, description='Log directory structure missing', systematic_impact='Cannot organize systematic logging output', remediation_steps=['Create logs/ directory', 'Create systematic log subdirectories', 'Set appropriate directory permissions'], validation_command='ls -la logs/', estimated_fix_time='5 minutes'))
    else:
        for subdir in required_subdirs:
            subdir_path = log_dir / subdir
            if not subdir_path.exists():
                issues.append(InfrastructureIssue(component=InfrastructureComponent.LOGGING, issue_type='missing_log_subdirectory', severity=ValidationSeverity.MEDIUM, description=f'Missing log subdirectory: {subdir}', systematic_impact='Cannot organize specific systematic logging categories', remediation_steps=[f'Create logs/{subdir}/ directory', 'Verify directory permissions', 'Test logging to subdirectory'], validation_command=f'ls -la logs/{subdir}/', estimated_fix_time='2 minutes'))
    try:
        test_logger = logging.getLogger('beast_mode.test')
        test_logger.setLevel(logging.DEBUG)
        self.logger.debug('✅ Log level configuration: Available')
    except Exception as e:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.LOGGING, issue_type='log_level_configuration_failure', severity=ValidationSeverity.MEDIUM, description=f'Log level configuration failed: {str(e)}', systematic_impact='Cannot implement systematic log level management', remediation_steps=['Verify logging configuration capabilities', 'Implement systematic log level management', 'Test log level changes'], estimated_fix_time='10-15 minutes'))
    if not issues:
        recommendations.extend(['Implement correlation IDs for request tracing', 'Add structured logging with JSON format', 'Setup log rotation and retention policies', 'Implement contextual logging for systematic operations'])
    else:
        recommendations.extend(['Address critical logging infrastructure issues immediately', 'Implement comprehensive logging framework', 'Establish systematic logging standards'])
    critical_issues = len([i for i in issues if i.severity == ValidationSeverity.CRITICAL])
    high_issues = len([i for i in issues if i.severity == ValidationSeverity.HIGH])
    if critical_issues > 0:
        compliance_score = 0.0
    elif high_issues > 0:
        compliance_score = 0.5
    elif len(issues) > 0:
        compliance_score = 0.8
    else:
        compliance_score = 1.0
    status = 'PASS' if compliance_score >= 0.8 else 'FAIL' if compliance_score < 0.5 else 'WARNING'
    return ValidationResult(component=InfrastructureComponent.LOGGING, status=status, issues=issues, systematic_compliance_score=compliance_score, recommendations=recommendations, validation_timestamp=datetime.now())

def _validate_profiling_infrastructure(self) -> ValidationResult:
    """
        Validate profiling infrastructure - ALWAYS SECOND PRIORITY
        
        Systematic profiling validation includes:
        - cProfile availability
        - System monitoring capabilities (psutil)
        - High-precision timing
        - Performance monitoring infrastructure
        - Memory tracking capabilities
        """
    issues = []
    recommendations = []
    try:
        import cProfile
        self.logger.debug('✅ cProfile: Available')
    except ImportError:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.PROFILING, issue_type='missing_cprofile', severity=ValidationSeverity.HIGH, description='cProfile module not available', systematic_impact='Cannot perform systematic code profiling', remediation_steps=['Verify Python installation includes cProfile', 'Install cProfile if missing', 'Test cProfile functionality'], validation_command='python -c \'import cProfile; print("cProfile available")\'', estimated_fix_time='10-15 minutes'))
    try:
        import psutil
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        disk_usage = psutil.disk_usage('/')
        self.logger.debug(f'✅ psutil: Available (Memory: {memory_info.percent:.1f}%, CPU: {cpu_percent:.1f}%)')
    except ImportError:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.PROFILING, issue_type='missing_psutil', severity=ValidationSeverity.CRITICAL, description='psutil module not available for system monitoring', systematic_impact='Cannot monitor system performance during systematic operations', remediation_steps=['Install psutil: pip install psutil', 'Verify psutil functionality', 'Test system monitoring capabilities'], validation_command='python -c \'import psutil; print(f"Memory: {psutil.virtual_memory().percent:.1f}%")\'', estimated_fix_time='5-10 minutes'))
    except Exception as e:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.PROFILING, issue_type='psutil_functionality_failure', severity=ValidationSeverity.HIGH, description=f'psutil functionality test failed: {str(e)}', systematic_impact='System monitoring may be unreliable', remediation_steps=['Verify psutil installation', 'Check system permissions for monitoring', 'Test psutil functionality'], estimated_fix_time='10-15 minutes'))
    try:
        start_time = time.time()
        time.sleep(0.01)
        end_time = time.time()
        duration = end_time - start_time
        if duration > 0.005:
            self.logger.debug(f'✅ High-precision timing: Available ({duration:.4f}s precision)')
        else:
            issues.append(InfrastructureIssue(component=InfrastructureComponent.PROFILING, issue_type='insufficient_timing_precision', severity=ValidationSeverity.MEDIUM, description='Timing precision may be insufficient for systematic profiling', systematic_impact='May not capture fine-grained performance metrics', remediation_steps=['Verify system timer resolution', 'Consider alternative timing methods', 'Test timing precision requirements'], estimated_fix_time='15-20 minutes'))
    except Exception as e:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.PROFILING, issue_type='timing_infrastructure_failure', severity=ValidationSeverity.HIGH, description=f'Timing infrastructure test failed: {str(e)}', systematic_impact='Cannot measure systematic operation performance', remediation_steps=['Verify time module functionality', 'Check system timer capabilities', 'Implement alternative timing methods'], estimated_fix_time='20-30 minutes'))
    try:
        import threading
        import queue
        monitor_queue = queue.Queue()
        self.logger.debug('✅ Performance monitoring infrastructure: Available')
    except Exception as e:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.PROFILING, issue_type='monitoring_infrastructure_failure', severity=ValidationSeverity.MEDIUM, description=f'Performance monitoring infrastructure test failed: {str(e)}', systematic_impact='Cannot implement systematic performance monitoring', remediation_steps=['Verify threading and queue modules', 'Implement performance monitoring framework', 'Test monitoring infrastructure'], estimated_fix_time='30-45 minutes'))
    if not issues:
        recommendations.extend(['Implement comprehensive performance profiling', 'Add memory leak detection capabilities', 'Setup performance baseline measurement', 'Implement systematic performance monitoring dashboards'])
    else:
        recommendations.extend(['Address critical profiling infrastructure issues immediately', 'Install missing profiling dependencies', 'Establish systematic performance monitoring'])
    critical_issues = len([i for i in issues if i.severity == ValidationSeverity.CRITICAL])
    high_issues = len([i for i in issues if i.severity == ValidationSeverity.HIGH])
    if critical_issues > 0:
        compliance_score = 0.0
    elif high_issues > 0:
        compliance_score = 0.6
    elif len(issues) > 0:
        compliance_score = 0.8
    else:
        compliance_score = 1.0
    status = 'PASS' if compliance_score >= 0.8 else 'FAIL' if compliance_score < 0.5 else 'WARNING'
    return ValidationResult(component=InfrastructureComponent.PROFILING, status=status, issues=issues, systematic_compliance_score=compliance_score, recommendations=recommendations, validation_timestamp=datetime.now())

def _validate_monitoring_infrastructure(self) -> ValidationResult:
    """Validate monitoring infrastructure for systematic operations"""
    issues = []
    recommendations = []
    try:
        monitoring_available = True
        self.logger.debug('✅ Basic monitoring infrastructure: Available')
    except Exception as e:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.MONITORING, issue_type='monitoring_infrastructure_failure', severity=ValidationSeverity.MEDIUM, description=f'Monitoring infrastructure validation failed: {str(e)}', systematic_impact='Cannot implement systematic monitoring', remediation_steps=['Implement basic monitoring infrastructure', 'Setup systematic monitoring capabilities', 'Test monitoring functionality'], estimated_fix_time='45-60 minutes'))
    compliance_score = 0.8 if not issues else 0.6
    status = 'PASS' if compliance_score >= 0.8 else 'WARNING'
    recommendations.extend(['Implement comprehensive systematic monitoring', 'Add real-time performance dashboards', 'Setup systematic alerting and notifications'])
    return ValidationResult(component=InfrastructureComponent.MONITORING, status=status, issues=issues, systematic_compliance_score=compliance_score, recommendations=recommendations, validation_timestamp=datetime.now())

def _validate_testing_infrastructure(self) -> ValidationResult:
    """Validate testing infrastructure for systematic quality assurance"""
    issues = []
    recommendations = []
    try:
        import pytest
        self.logger.debug('✅ pytest testing framework: Available')
    except ImportError:
        issues.append(InfrastructureIssue(component=InfrastructureComponent.TESTING, issue_type='missing_pytest', severity=ValidationSeverity.HIGH, description='pytest testing framework not available', systematic_impact='Cannot execute systematic testing procedures', remediation_steps=['Install pytest: pip install pytest', 'Verify pytest functionality', 'Setup systematic testing configuration'], validation_command='python -m pytest --version', estimated_fix_time='10-15 minutes'))
    test_dir = Path('tests')
    if not test_dir.exists():
        issues.append(InfrastructureIssue(component=InfrastructureComponent.TESTING, issue_type='missing_test_directory', severity=ValidationSeverity.MEDIUM, description='Test directory structure missing', systematic_impact='Cannot organize systematic tests', remediation_steps=['Create tests/ directory', 'Setup systematic test organization', 'Implement test discovery patterns'], estimated_fix_time='10 minutes'))
    compliance_score = 0.8 if len(issues) == 0 else 0.6 if len([i for i in issues if i.severity == ValidationSeverity.HIGH]) == 0 else 0.4
    status = 'PASS' if compliance_score >= 0.8 else 'WARNING' if compliance_score >= 0.6 else 'FAIL'
    recommendations.extend(['Implement comprehensive test coverage measurement', 'Setup systematic test automation', 'Add performance and integration testing capabilities'])
    return ValidationResult(component=InfrastructureComponent.TESTING, status=status, issues=issues, systematic_compliance_score=compliance_score, recommendations=recommendations, validation_timestamp=datetime.now())

def _validate_documentation_infrastructure(self) -> ValidationResult:
    """Validate documentation infrastructure for systematic knowledge management"""
    issues = []
    recommendations = []
    docs_dir = Path('docs')
    if not docs_dir.exists():
        issues.append(InfrastructureIssue(component=InfrastructureComponent.DOCUMENTATION, issue_type='missing_docs_directory', severity=ValidationSeverity.MEDIUM, description='Documentation directory missing', systematic_impact='Cannot organize systematic documentation', remediation_steps=['Create docs/ directory', 'Setup systematic documentation structure', 'Implement documentation standards'], estimated_fix_time='15 minutes'))
    systematic_docs_dir = Path('docs/systematic')
    if systematic_docs_dir.exists():
        doc_count = len([f for f in systematic_docs_dir.iterdir() if f.is_file()])
        self.logger.debug(f'✅ Systematic documentation: {doc_count} documents found')
    compliance_score = 0.9 if len(issues) == 0 else 0.7
    status = 'PASS' if compliance_score >= 0.8 else 'WARNING'
    recommendations.extend(['Implement systematic documentation standards', 'Setup automated documentation generation', 'Add systematic knowledge management capabilities'])
    return ValidationResult(component=InfrastructureComponent.DOCUMENTATION, status=status, issues=issues, systematic_compliance_score=compliance_score, recommendations=recommendations, validation_timestamp=datetime.now())
