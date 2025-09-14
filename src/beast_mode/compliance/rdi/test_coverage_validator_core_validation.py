"""
Test Coverage Validator Core Validation

This module was extracted from test_coverage_validator_core.py
as part of RM-DDD compliance refactoring.
"""

import re
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity
from ...utils.path_normalizer import safe_relative_to
from src.rm_ddd.core.health import ModuleHealth


def validate(self, target: str) -> List[ComplianceIssue]:
    """
        Validate test coverage for the given target.
        
        Args:
            target: Path to analyze (file or directory)
            
        Returns:
            List of compliance issues found
        """
    target_path = Path(target) if isinstance(target, str) else target
    if self.coverage_cache is None:
        self.coverage_cache = self._generate_coverage_report(target_path)
    coverage_result = self._analyze_coverage()
    return coverage_result.issues

def _has_corresponding_test_file(self, src_file: Path, test_files: List[Path]) -> bool:
    """
        Check if a source file has a corresponding test file.
        
        Args:
            src_file: Source file to check
            test_files: List of test files
            
        Returns:
            True if corresponding test file exists
        """
    src_name = src_file.stem
    for test_file in test_files:
        test_name = test_file.stem
        if src_name in test_name or test_name.replace('test_', '') == src_name or test_name == f'test_{src_name}':
            return True
    return False

def _find_test_files(self, target_path: Path) -> List[TestFile]:
    """
        Find and analyze all test files.
        
        Args:
            target_path: Path to search for test files
            
        Returns:
            List of test files with metadata
        """
    test_files = []
    test_patterns = ['**/test_*.py', '**/tests.py', '**/*_test.py']
    found_files = []
    for pattern in test_patterns:
        found_files.extend(self.repository_path.glob(pattern))
    for test_file in found_files:
        try:
            test_functions = self._extract_test_functions(test_file)
            test_type = self._determine_test_type(test_file)
            test_files.append(TestFile(file_path=str(test_file), test_functions=test_functions, test_type=test_type, coverage_percentage=0.0, lines_covered=0, lines_total=0, missing_lines=[]))
        except Exception as e:
            print(f'Error analyzing test file {test_file}: {e}')
    return test_files

def _extract_test_functions(self, test_file: Path) -> List[str]:
    """
        Extract test function names from a test file.
        
        Args:
            test_file: Path to the test file
            
        Returns:
            List of test function names
        """
    test_functions = []
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        test_matches = re.findall('def\\s+(test_\\w+)', content)
        test_functions.extend(test_matches)
        class_matches = re.findall('class\\s+(Test\\w+)', content)
        for class_name in class_matches:
            class_pattern = f'class\\s+{class_name}.*?(?=class|\\Z)'
            class_match = re.search(class_pattern, content, re.DOTALL)
            if class_match:
                class_content = class_match.group(0)
                method_matches = re.findall('def\\s+(test_\\w+)', class_content)
                test_functions.extend([f'{class_name}.{method}' for method in method_matches])
    except Exception as e:
        print(f'Error extracting test functions from {test_file}: {e}')
    return test_functions

def _determine_test_type(self, test_file: Path) -> TestType:
    """
        Determine the type of test based on file path and content.
        
        Args:
            test_file: Path to the test file
            
        Returns:
            Test type classification
        """
    file_path_str = str(test_file).lower()
    if 'integration' in file_path_str:
        return TestType.INTEGRATION
    elif 'functional' in file_path_str:
        return TestType.FUNCTIONAL
    elif 'system' in file_path_str:
        return TestType.SYSTEM
    else:
        return TestType.UNIT

def _identify_failing_tests(self, target_path: Path) -> List[FailingTest]:
    """
        Identify failing tests by running the test suite.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            List of failing tests with details
        """
    failing_tests = []
    try:
        result = subprocess.run(['python', '-m', 'pytest', '--tb=short', '--json-report', '--json-report-file=test_report.json', str(target_path / 'tests') if (target_path / 'tests').exists() else 'tests'], capture_output=True, text=True, cwd=self.repository_path, timeout=300)
        report_path = self.repository_path / 'test_report.json'
        if report_path.exists():
            with open(report_path, 'r') as f:
                test_report = json.load(f)
            for test in test_report.get('tests', []):
                if test.get('outcome') == 'failed':
                    failing_tests.append(FailingTest(test_name=test.get('nodeid', ''), test_file=test.get('file', ''), error_message=test.get('call', {}).get('longrepr', ''), error_type='test_failure', stack_trace=test.get('call', {}).get('longrepr', ''), requirements_covered=[]))
            report_path.unlink()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f'Test execution failed: {e}')
        for test_name in self.known_failing_tests:
            failing_tests.append(FailingTest(test_name=test_name, test_file=f'tests/{test_name}.py', error_message='Known failing test from Phase 2', error_type='known_failure', stack_trace=None, requirements_covered=[]))
    return failing_tests

def _find_missing_test_files(self, target_path: Path) -> List[str]:
    """
        Find source files that don't have corresponding test files.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            List of source files missing test coverage
        """
    missing_test_files = []
    src_files = list(self.repository_path.glob('src/**/*.py'))
    test_files = list(self.repository_path.glob('tests/**/*.py'))
    for src_file in src_files:
        if src_file.name == '__init__.py':
            continue
        if not self._has_corresponding_test_file(src_file, test_files):
            relative_path = safe_relative_to(src_file, self.repository_path)
            if relative_path is not None:
                missing_test_files.append(str(relative_path))
    return missing_test_files

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

