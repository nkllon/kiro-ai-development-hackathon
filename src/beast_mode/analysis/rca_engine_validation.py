"""
Rca Engine Validation

This module was extracted from rca_engine.py
as part of RM-DDD compliance refactoring.
"""

import os
import subprocess
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
import shutil

def validate_root_cause_addressed(self, fix: SystematicFix, original_failure: Failure) -> ValidationResult:
    """
        Validate fixes address root cause, not just symptoms (R7.4)
        Required by R7.4: Validate fixes address root cause, not just symptoms
        """
    try:
        self.logger.info(f'Validating systematic fix: {fix.fix_id}')
        validation_evidence = []
        symptoms_resolved = []
        remaining_issues = []
        for criteria in fix.validation_criteria:
            try:
                validation_result = self._execute_validation_criteria(criteria, original_failure)
                validation_evidence.append(f"Criteria '{criteria}': {validation_result['status']}")
                if validation_result['status'] == 'passed':
                    symptoms_resolved.extend(validation_result.get('resolved_symptoms', []))
                else:
                    remaining_issues.extend(validation_result.get('remaining_issues', []))
            except Exception as e:
                validation_evidence.append(f"Criteria '{criteria}': failed - {e}")
                remaining_issues.append(f'Validation failed: {e}')
        fix_successful = len(remaining_issues) == 0
        root_cause_addressed = fix_successful and len(symptoms_resolved) > 0
        confidence_score = len(symptoms_resolved) / max(1, len(symptoms_resolved) + len(remaining_issues))
        return ValidationResult(fix_successful=fix_successful, root_cause_addressed=root_cause_addressed, symptoms_resolved=symptoms_resolved, remaining_issues=remaining_issues, validation_evidence=validation_evidence, confidence_score=confidence_score)
    except Exception as e:
        self.logger.error(f'Fix validation failed: {e}')
        return ValidationResult(fix_successful=False, root_cause_addressed=False, symptoms_resolved=[], remaining_issues=[f'Validation error: {e}'], validation_evidence=[f'Validation failed: {e}'], confidence_score=0.0)

def analyze_test_failure_categorization(self, failure: Failure) -> Dict[str, Any]:
    """
        Categorize test failures (pytest, make, infrastructure) - Requirement 5.1, 5.2, 5.3
        """
    try:
        self.logger.info(f'Categorizing test failure: {failure.failure_id}')
        categorization = {'primary_category': 'unknown', 'subcategory': 'unknown', 'confidence': 0.0, 'analysis_details': {}}
        if self._is_pytest_failure(failure):
            categorization.update({'primary_category': 'pytest_failure', 'subcategory': self._get_pytest_subcategory(failure), 'confidence': 0.9, 'analysis_details': self._analyze_pytest_details(failure)})
        elif self._is_make_failure(failure):
            categorization.update({'primary_category': 'make_target_failure', 'subcategory': self._get_make_subcategory(failure), 'confidence': 0.8, 'analysis_details': self._analyze_make_details(failure)})
        elif self._is_infrastructure_failure(failure):
            categorization.update({'primary_category': 'infrastructure_failure', 'subcategory': self._get_infrastructure_subcategory(failure), 'confidence': 0.7, 'analysis_details': self._analyze_infrastructure_details(failure)})
        elif failure.component.startswith('test:') or 'test' in failure.component.lower() or (failure.context and 'test_file' in failure.context):
            categorization.update({'primary_category': 'test_environment_failure', 'subcategory': 'unknown_test_failure', 'confidence': 0.5, 'analysis_details': {'error': 'Could not categorize test failure specifically'}})
        self.logger.info(f"Test failure categorized as: {categorization['primary_category']}/{categorization['subcategory']}")
        return categorization
    except Exception as e:
        self.logger.error(f'Test failure categorization failed: {e}')
        return {'primary_category': 'unknown', 'subcategory': 'categorization_error', 'confidence': 0.0, 'analysis_details': {'error': str(e)}}

def generate_test_specific_systematic_fixes(self, root_causes: List[RootCause]) -> List[SystematicFix]:
    """
        Generate test-specific systematic fixes - Requirements 4.3, 5.1, 5.2, 5.3, 5.4
        """
    test_specific_fixes = []
    for root_cause in root_causes:
        try:
            if root_cause.cause_type in [RootCauseType.TEST_IMPORT_ERROR, RootCauseType.TEST_ASSERTION_FAILURE, RootCauseType.TEST_FIXTURE_ERROR, RootCauseType.TEST_TIMEOUT, RootCauseType.TEST_SETUP_ERROR]:
                fix = self._generate_pytest_specific_fix(root_cause)
                test_specific_fixes.append(fix)
            elif root_cause.cause_type in [RootCauseType.MAKEFILE_ERROR, RootCauseType.BUILD_DEPENDENCY_ERROR]:
                fix = self._generate_makefile_specific_fix(root_cause)
                test_specific_fixes.append(fix)
            elif root_cause.cause_type == RootCauseType.INFRASTRUCTURE_ERROR:
                fix = self._generate_infrastructure_specific_fix(root_cause)
                test_specific_fixes.append(fix)
            self.logger.info(f'Generated test-specific fix for {root_cause.cause_type}')
        except Exception as e:
            self.logger.error(f'Failed to generate test-specific fix for {root_cause.cause_type}: {e}')
    return test_specific_fixes

def add_test_specific_patterns_to_library(self, failure: Failure, root_causes: List[RootCause], fixes: List[SystematicFix]) -> List[PreventionPattern]:
    """
        Add test-specific patterns to pattern library - Requirements 4.4, 5.1, 5.2, 5.3, 5.4
        """
    test_patterns = []
    for root_cause, fix in zip(root_causes, fixes):
        try:
            pattern = self._create_test_specific_pattern(failure, root_cause, fix)
            test_patterns.append(pattern)
            self._add_test_pattern_to_library(pattern)
            self.logger.info(f'Added test-specific pattern: {pattern.pattern_name}')
        except Exception as e:
            self.logger.error(f'Failed to add test-specific pattern: {e}')
    return test_patterns

def _analyze_test_specific_factors(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test-specific factors for comprehensive analysis"""
    test_analysis = {}
    try:
        is_test_failure = failure.component.startswith('test:') or 'test' in failure.component.lower() or failure.category in [FailureCategory.PYTEST_FAILURE, FailureCategory.MAKE_TARGET_FAILURE, FailureCategory.INFRASTRUCTURE_FAILURE, FailureCategory.TEST_ENVIRONMENT_FAILURE] or self._is_pytest_failure(failure) or self._is_make_failure(failure) or self._is_infrastructure_failure(failure)
        if is_test_failure:
            test_analysis['is_test_failure'] = True
            test_analysis['test_categorization'] = self.analyze_test_failure_categorization(failure)
            if failure.context and 'test_file' in failure.context:
                test_analysis['test_file'] = failure.context['test_file']
                test_analysis['test_function'] = failure.context.get('test_function', 'unknown')
                test_analysis['pytest_node_id'] = failure.context.get('pytest_node_id', 'unknown')
            test_analysis['test_environment'] = self._analyze_test_environment(failure)
        else:
            test_analysis['is_test_failure'] = False
            test_analysis['reason'] = 'Not identified as test-related failure'
    except Exception as e:
        test_analysis['analysis_error'] = str(e)
    return test_analysis

def _analyze_pytest_failures(self, failure: Failure) -> Dict[str, Any]:
    """Analyze pytest-specific failures - Requirement 5.1"""
    pytest_analysis = {}
    try:
        if self._is_pytest_failure(failure):
            pytest_analysis['python_issues'] = self._analyze_python_issues(failure)
            pytest_analysis['import_analysis'] = self._analyze_import_issues(failure)
            pytest_analysis['dependency_analysis'] = self._analyze_test_dependencies(failure)
            pytest_analysis['syntax_analysis'] = self._analyze_syntax_issues(failure)
            pytest_analysis['test_structure'] = self._analyze_test_structure(failure)
            pytest_analysis['analysis_confidence'] = 0.9
        else:
            pytest_analysis['applicable'] = False
            pytest_analysis['reason'] = 'Not a pytest failure'
    except Exception as e:
        pytest_analysis['analysis_error'] = str(e)
    return pytest_analysis

def _verify_pattern_match(self, failure: Failure, pattern: PreventionPattern) -> bool:
    """Verify if failure matches existing pattern"""
    failure_signature = self._generate_failure_signature(failure)
    return failure.component in pattern.failure_signature and failure.category.value in pattern.failure_signature

def _is_pytest_failure(self, failure: Failure) -> bool:
    """Check if failure is pytest-related"""
    return 'pytest' in failure.error_message.lower() or 'test_' in failure.component or failure.context.get('pytest_node_id') is not None or ('ImportError' in failure.error_message) or ('AssertionError' in failure.error_message)

def _get_pytest_subcategory(self, failure: Failure) -> str:
    """Get pytest failure subcategory"""
    if 'ImportError' in failure.error_message:
        return 'import_error'
    elif 'AssertionError' in failure.error_message:
        return 'assertion_failure'
    elif 'fixture' in failure.error_message.lower():
        return 'fixture_error'
    elif 'timeout' in failure.error_message.lower():
        return 'timeout'
    else:
        return 'general_pytest_error'

def _analyze_pytest_details(self, failure: Failure) -> Dict[str, Any]:
    """Analyze pytest failure details"""
    return {'error_type': self._get_pytest_subcategory(failure), 'has_stack_trace': failure.stack_trace is not None, 'test_context_available': bool(failure.context.get('test_file')), 'pytest_node_available': bool(failure.context.get('pytest_node_id'))}

def _analyze_test_environment(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test environment factors"""
    env_analysis = {}
    try:
        env_analysis['python_available'] = subprocess.run(['python3', '--version'], capture_output=True).returncode == 0
        env_analysis['pytest_available'] = subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True).returncode == 0
        env_analysis['venv_active'] = 'VIRTUAL_ENV' in os.environ
        env_analysis['tests_dir_exists'] = Path('tests').exists()
        env_analysis['conftest_exists'] = Path('tests/conftest.py').exists()
    except Exception as e:
        env_analysis['analysis_error'] = str(e)
    return env_analysis

def _analyze_test_dependencies(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test-specific dependency issues"""
    dep_analysis = {}
    try:
        dep_analysis['requirements_exists'] = Path('requirements.txt').exists()
        dep_analysis['pyproject_exists'] = Path('pyproject.toml').exists()
        dep_analysis['setup_py_exists'] = Path('setup.py').exists()
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        dep_analysis['pip_list_available'] = result.returncode == 0
    except Exception as e:
        dep_analysis['analysis_error'] = str(e)
    return dep_analysis

def _analyze_test_structure(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test structure issues"""
    structure_analysis = {}
    if failure.context and 'test_file' in failure.context:
        test_file = failure.context['test_file']
        structure_analysis['test_file_exists'] = Path(test_file).exists()
        structure_analysis['test_file_path'] = test_file
        structure_analysis['follows_naming_convention'] = test_file.startswith('test_') or test_file.endswith('_test.py')
    return structure_analysis

def _identify_test_specific_root_causes(self, failure: Failure, analysis: ComprehensiveAnalysisResult) -> List[RootCause]:
    """Identify test-specific root causes"""
    test_root_causes = []
    if self._is_pytest_failure(failure):
        if 'ImportError' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.TEST_IMPORT_ERROR, description='Test import error - missing or broken test dependencies', evidence=['ImportError in test execution', failure.error_message], confidence_score=0.9, impact_severity='high', affected_components=[failure.component]))
        if 'AssertionError' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.TEST_ASSERTION_FAILURE, description='Test assertion failure - test logic or implementation issue', evidence=['AssertionError in test execution', failure.error_message], confidence_score=0.8, impact_severity='medium', affected_components=[failure.component]))
        if 'fixture' in failure.error_message.lower():
            test_root_causes.append(RootCause(cause_type=RootCauseType.TEST_FIXTURE_ERROR, description='Test fixture error - fixture setup or teardown issue', evidence=['Fixture error in test execution', failure.error_message], confidence_score=0.8, impact_severity='medium', affected_components=[failure.component]))
    elif self._is_make_failure(failure):
        if 'No rule to make target' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.MAKEFILE_ERROR, description='Makefile target missing - build system configuration issue', evidence=['Missing make target', failure.error_message], confidence_score=0.9, impact_severity='high', affected_components=['makefile', 'build_system']))
        if 'missing separator' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.MAKEFILE_ERROR, description='Makefile syntax error - incorrect tab/space formatting', evidence=['Makefile syntax error', failure.error_message], confidence_score=0.9, impact_severity='medium', affected_components=['makefile']))
    elif self._is_infrastructure_failure(failure):
        if 'PermissionError' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.INFRASTRUCTURE_ERROR, description='Infrastructure permission error - system access issue', evidence=['Permission error in system operation', failure.error_message], confidence_score=0.8, impact_severity='high', affected_components=['system', 'infrastructure']))
    return test_root_causes

def _generate_pytest_specific_fix(self, root_cause: RootCause) -> SystematicFix:
    """Generate pytest-specific systematic fix"""
    fix_id = f'fix_{root_cause.cause_type.value}_{int(time.time())}'
    if root_cause.cause_type == RootCauseType.TEST_IMPORT_ERROR:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description='Fix test import errors by resolving dependencies and Python path issues', implementation_steps=['Identify missing modules from error message', 'Check if modules are installed: pip list | grep <module>', 'Install missing dependencies: pip install <module>', 'Verify Python path includes necessary directories', 'Check for circular imports in test modules', 'Validate import statements in test files'], validation_criteria=['Import statements execute without errors', 'Test modules can be imported successfully', 'pytest --collect-only succeeds', 'No ImportError in test execution'], rollback_plan='Revert dependency installations and Python path changes', estimated_time_minutes=10)
    elif root_cause.cause_type == RootCauseType.TEST_ASSERTION_FAILURE:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description='Fix test assertion failures by analyzing test logic and expected behavior', implementation_steps=['Analyze assertion failure details from stack trace', 'Review test logic and expected vs actual values', 'Check if test data or fixtures are correct', 'Verify implementation matches test expectations', 'Update test assertions or fix implementation', 'Run specific test to validate fix'], validation_criteria=['Test assertions pass with correct values', 'Test logic matches implementation behavior', 'No assertion errors in test execution', 'Test provides meaningful validation'], rollback_plan='Revert test or implementation changes', estimated_time_minutes=15)
    elif root_cause.cause_type == RootCauseType.TEST_FIXTURE_ERROR:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description='Fix test fixture errors by resolving setup and teardown issues', implementation_steps=['Identify failing fixture from error message', 'Check fixture definition and scope', 'Verify fixture dependencies and parameters', 'Test fixture setup and teardown independently', 'Fix fixture implementation or dependencies', 'Validate fixture works with dependent tests'], validation_criteria=['Fixture setup completes without errors', 'Fixture provides expected test data/resources', 'Fixture teardown cleans up properly', 'Tests using fixture execute successfully'], rollback_plan='Revert fixture changes and restore original implementation', estimated_time_minutes=12)
    else:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description=f'Generic pytest fix for {root_cause.cause_type.value}', implementation_steps=[f'Analyze {root_cause.cause_type.value} systematically', 'Review pytest documentation for issue type', 'Implement appropriate fix', 'Validate fix resolves root cause'], validation_criteria=['Pytest error no longer occurs', 'Test execution completes successfully'], rollback_plan='Revert changes if fix fails', estimated_time_minutes=10)

def _create_test_specific_pattern(self, failure: Failure, root_cause: RootCause, fix: SystematicFix) -> PreventionPattern:
    """Create test-specific prevention pattern"""
    pattern_id = f'test_pattern_{root_cause.cause_type.value}_{int(time.time())}'
    failure_signature = self._generate_test_failure_signature(failure)
    pattern_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
    return PreventionPattern(pattern_id=pattern_id, pattern_name=f'Prevent {root_cause.cause_type.value} in {failure.component}', failure_signature=failure_signature, root_cause_pattern=root_cause.description, prevention_steps=[f'Monitor for {root_cause.cause_type.value} symptoms in tests', 'Implement automated test validation', 'Add pre-test environment checks', 'Create test-specific health monitoring'], detection_criteria=[f'Detect {root_cause.cause_type.value} patterns early', 'Monitor test execution for similar failures', 'Automated pattern matching for test failures'], automated_checks=[f'Automated check for {root_cause.cause_type.value} in tests', 'Continuous test environment monitoring', 'Preventive test validation'], pattern_hash=pattern_hash)

def _generate_test_failure_signature(self, failure: Failure) -> str:
    """Generate test-specific failure signature for pattern matching"""
    signature_parts = [failure.component, failure.category.value, failure.error_message[:100] if failure.error_message else '', failure.context.get('test_file', '') if failure.context else '', failure.context.get('failure_type', '') if failure.context else '', str(sorted(failure.context.keys())) if failure.context else '']
    return '|'.join(signature_parts)

def _add_test_pattern_to_library(self, pattern: PreventionPattern):
    """Add test-specific pattern to library with enhanced indexing"""
    self._add_pattern_to_library(pattern)
    self.logger.info(f'Added test-specific pattern to library: {pattern.pattern_id}')
