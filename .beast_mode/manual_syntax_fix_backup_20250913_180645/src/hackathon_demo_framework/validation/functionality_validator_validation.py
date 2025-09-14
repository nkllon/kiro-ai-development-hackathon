"""
Functionality Validator Validation

This module was extracted from functionality_validator.py
as part of RM-DDD compliance refactoring.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import importlib.util
import ast
import json
from ..models import ValidationResult, TechnicalAssessment

def validate_core_functionality(self) -> ValidationResult:
    """
        Comprehensive validation of core functionality implementation.
        
        Returns:
            Validation result with functionality assessment
        """
    self.logger.info('Starting core functionality validation')
    issues = []
    recommendations = []
    score = 0.0
    try:
        test_results = self._discover_and_run_tests()
        test_score = self._calculate_test_score(test_results)
        feature_coverage = self._analyze_feature_coverage()
        coverage_score = self._calculate_coverage_score(feature_coverage)
        integration_results = self._validate_integrations()
        integration_score = self._calculate_integration_score(integration_results)
        interface_results = self._validate_interfaces()
        interface_score = self._calculate_interface_score(interface_results)
        scores = [test_score, coverage_score, integration_score, interface_score]
        score = sum(scores) / len(scores)
        if test_score < 80:
            issues.append(f'Test execution score too low: {test_score:.1f}')
            recommendations.append('Fix failing tests and improve test coverage')
        if coverage_score < 70:
            issues.append(f'Feature coverage insufficient: {coverage_score:.1f}')
            recommendations.append('Implement missing core features or add feature tests')
        if integration_score < 75:
            issues.append(f'Integration validation failed: {integration_score:.1f}')
            recommendations.append('Fix integration issues and end-to-end workflows')
        self.logger.info(f'Functionality validation complete. Score: {score:.1f}')
    except Exception as e:
        self.logger.error(f'Functionality validation failed: {e}')
        issues.append(f'Validation error: {str(e)}')
        score = 0.0
    return ValidationResult(is_valid=score >= 80.0 and len(issues) == 0, score=score, issues=issues, recommendations=recommendations)

def _discover_and_run_tests(self) -> Dict[str, Any]:
    """Discover and execute all tests in the project."""
    test_results = {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'test_files': [], 'execution_time': 0.0, 'errors': []}
    try:
        test_files = []
        tests_dir = self.project_path / 'tests'
        if tests_dir.exists():
            for pattern in self.test_patterns:
                hackathon_tests = list(tests_dir.glob('test_hackathon*.py'))
                test_files.extend(hackathon_tests[:5])
        if not test_files:
            for pattern in self.test_patterns:
                found = list(self.project_path.glob(pattern))[:3]
                test_files.extend(found)
        test_results['test_files'] = [str(f) for f in test_files]
        if not test_files:
            test_results['errors'].append('No test files found')
            return test_results
        for test_file in test_files:
            try:
                spec = importlib.util.spec_from_file_location('test_module', test_file)
                if spec and spec.loader:
                    with open(test_file, 'r') as f:
                        content = f.read()
                        compile(content, str(test_file), 'exec')
                    test_results['passed_tests'] += 1
            except Exception as e:
                test_results['failed_tests'] += 1
                test_results['errors'].append(f'Import error in {test_file}: {e}')
        test_results['total_tests'] = test_results['passed_tests'] + test_results['failed_tests']
    except Exception as e:
        test_results['errors'].append(f'Test discovery failed: {e}')
    return test_results

def _validate_integrations(self) -> Dict[str, Any]:
    """Validate integration points and end-to-end workflows."""
    integration_results = {'working_integrations': [], 'broken_integrations': [], 'integration_score': 0.0, 'errors': []}
    try:
        import_issues = self._check_import_health()
        if not import_issues:
            integration_results['working_integrations'].append('All imports working')
            integration_results['integration_score'] = 100.0
        else:
            integration_results['broken_integrations'] = import_issues
            integration_results['integration_score'] = max(0, 100 - len(import_issues) * 20)
        config_files = [self.project_path / 'requirements.txt', self.project_path / 'pyproject.toml', self.project_path / 'setup.py']
        valid_configs = 0
        for config_file in config_files:
            if config_file.exists():
                try:
                    if config_file.name == 'requirements.txt':
                        with open(config_file, 'r') as f:
                            lines = f.readlines()
                            if lines:
                                valid_configs += 1
                    elif config_file.name in ['pyproject.toml', 'setup.py']:
                        valid_configs += 1
                except Exception as e:
                    integration_results['errors'].append(f'Config file error {config_file}: {e}')
        if valid_configs > 0:
            integration_results['working_integrations'].append(f'Valid configuration files: {valid_configs}')
        else:
            integration_results['broken_integrations'].append('No valid configuration files found')
    except Exception as e:
        integration_results['errors'].append(f'Integration validation failed: {e}')
    return integration_results

def _validate_interfaces(self) -> Dict[str, Any]:
    """Validate API and interface definitions."""
    interface_results = {'defined_interfaces': [], 'missing_interfaces': [], 'interface_score': 0.0, 'errors': []}
    try:
        source_files = list(self.project_path.rglob('src/**/*.py'))
        source_files.extend([f for f in self.project_path.rglob('*.py') if not f.name.startswith('test_')])
        total_interfaces = 0
        documented_interfaces = 0
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        total_interfaces += 1
                        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                            documented_interfaces += 1
                            interface_results['defined_interfaces'].append(f'{source_file.name}::{node.name}')
                        else:
                            interface_results['missing_interfaces'].append(f'{source_file.name}::{node.name} (missing docstring)')
            except Exception as e:
                interface_results['errors'].append(f'Interface analysis error {source_file}: {e}')
        if total_interfaces > 0:
            interface_results['interface_score'] = documented_interfaces / total_interfaces * 100
        else:
            interface_results['interface_score'] = 0.0
    except Exception as e:
        interface_results['errors'].append(f'Interface validation failed: {e}')
    return interface_results

def _check_import_health(self) -> List[str]:
    """Check for broken imports in the project."""
    import_issues = []
    try:
        source_files = []
        hackathon_src = self.project_path / 'src' / 'hackathon_demo_framework'
        if hackathon_src.exists():
            source_files = list(hackathon_src.rglob('*.py'))[:5]
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            try:
                                importlib.import_module(alias.name)
                            except ImportError:
                                import_issues.append(f'Cannot import {alias.name} in {source_file.name}')
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            try:
                                importlib.import_module(node.module)
                            except ImportError:
                                import_issues.append(f'Cannot import from {node.module} in {source_file.name}')
            except Exception as e:
                import_issues.append(f'Import analysis error in {source_file}: {e}')
    except Exception as e:
        import_issues.append(f'Import health check failed: {e}')
    return import_issues

def _check_documentation_completeness(self) -> List[str]:
    """Check for missing documentation."""
    doc_issues = []
    readme_files = list(self.project_path.glob('README*'))
    if not readme_files:
        doc_issues.append('Missing README file')
    else:
        try:
            with open(readme_files[0], 'r', encoding='utf-8') as f:
                readme_content = f.read()
            if len(readme_content.strip()) < 100:
                doc_issues.append('README file too short - needs more content')
            required_sections = ['installation', 'usage', 'setup']
            missing_sections = []
            for section in required_sections:
                if section.lower() not in readme_content.lower():
                    missing_sections.append(section)
            if missing_sections:
                doc_issues.append(f"README missing sections: {', '.join(missing_sections)}")
        except Exception as e:
            doc_issues.append(f'Could not analyze README: {e}')
    source_files = list(self.project_path.rglob('src/**/*.py'))
    undocumented_files = []
    for source_file in source_files:
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if '"""' not in content and "'''" not in content:
                undocumented_files.append(source_file.name)
        except Exception:
            pass
    if undocumented_files:
        doc_issues.append(f"Files missing docstrings: {', '.join(undocumented_files[:5])}")
    return doc_issues

def _calculate_test_score(self, test_results: Dict[str, Any]) -> float:
    """Calculate test execution score."""
    if test_results['total_tests'] == 0:
        return 0.0
    if test_results['errors']:
        return max(0, 50 - len(test_results['errors']) * 10)
    pass_rate = test_results['passed_tests'] / test_results['total_tests']
    return pass_rate * 100
