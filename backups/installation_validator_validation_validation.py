"""
Installation Validator Validation Validation

This module was extracted from installation_validator_validation.py
as part of RM-DDD compliance refactoring.
"""

import logging
import sys
import tempfile
import shutil
import venv
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
import os
from ..models import ValidationResult
import time
import tomllib
import importlib.util
import tomli as tomllib
import time
import tomllib
import importlib.util
import tomli as tomllib

def validate_installation_setup(self) -> InstallationReport:
    """
        Perform comprehensive installation and setup validation.
        
        Returns:
            Detailed installation validation report
        """
    self.logger.info('Starting installation and setup validation')
    try:
        import time
        start_time = time.time()
        all_issues = []
        self.logger.info('Validating configuration files')
        config_analysis = self._validate_configuration_files()
        all_issues.extend(config_analysis['issues'])
        self.logger.info('Validating dependencies')
        dependency_analysis = self._validate_dependencies()
        all_issues.extend(dependency_analysis['issues'])
        self.logger.info('Validating setup instructions')
        setup_analysis = self._validate_setup_instructions()
        all_issues.extend(setup_analysis['issues'])
        self.logger.info('Validating installation documentation')
        doc_analysis = self._validate_documentation()
        all_issues.extend(doc_analysis['issues'])
        self.logger.info('Testing installation process')
        installation_analysis = self._test_installation_process()
        all_issues.extend(installation_analysis['issues'])
        end_time = time.time()
        installation_time = end_time - start_time
        requirements_score = config_analysis['score']
        dependency_score = dependency_analysis['score']
        setup_score = setup_analysis['score']
        documentation_score = doc_analysis['score']
        environment_score = installation_analysis['score']
        overall_score = requirements_score * 0.25 + dependency_score * 0.25 + setup_score * 0.2 + documentation_score * 0.15 + environment_score * 0.15
        critical_issues = [i for i in all_issues if i.severity == 'critical']
        major_issues = [i for i in all_issues if i.severity == 'major']
        minor_issues = [i for i in all_issues if i.severity == 'minor']
        success_rate = max(0, 100 - len(critical_issues) * 30 - len(major_issues) * 10 - len(minor_issues) * 2)
        recommendations = self._generate_recommendations(all_issues, {'requirements': requirements_score, 'dependency': dependency_score, 'setup': setup_score, 'documentation': documentation_score, 'environment': environment_score})
        report = InstallationReport(overall_score=overall_score, requirements_score=requirements_score, dependency_score=dependency_score, setup_score=setup_score, documentation_score=documentation_score, environment_score=environment_score, total_issues=len(all_issues), critical_issues=len(critical_issues), major_issues=len(major_issues), minor_issues=len(minor_issues), issues=all_issues, recommendations=recommendations, installation_time=installation_time, success_rate=success_rate)
        self.logger.info(f'Installation validation complete. Overall score: {overall_score:.1f}')
        return report
    except Exception as e:
        self.logger.error(f'Installation validation failed: {e}')
        return self._create_error_report(f'Validation failed: {e}')

def validate_installation_reliability(self, num_tests: int=3) -> ValidationResult:
    """
        Test installation reliability across multiple attempts.
        
        Args:
            num_tests: Number of installation attempts to test
            
        Returns:
            Validation result with reliability assessment
        """
    self.logger.info(f'Testing installation reliability with {num_tests} attempts')
    successful_installs = 0
    issues = []
    recommendations = []
    for attempt in range(num_tests):
        try:
            self.logger.info(f'Installation attempt {attempt + 1}/{num_tests}')
            with tempfile.TemporaryDirectory() as temp_dir:
                test_result = self._test_single_installation(Path(temp_dir))
                if test_result['success']:
                    successful_installs += 1
                else:
                    issues.extend(test_result['issues'])
        except Exception as e:
            issues.append(f'Installation attempt {attempt + 1} failed: {e}')
    success_rate = successful_installs / num_tests * 100
    if success_rate < 80:
        issues.append(f'Installation reliability too low: {success_rate:.1f}%')
        recommendations.append('Improve installation process reliability')
    if success_rate < 50:
        recommendations.append('Critical: Fix installation process - more than half of attempts fail')
    return ValidationResult(is_valid=success_rate >= 80, score=success_rate, issues=issues, recommendations=recommendations)

def _validate_configuration_files(self) -> Dict[str, Any]:
    """Validate presence and quality of configuration files."""
    issues = []
    score = 100
    config_files_found = []
    for config_file in self.config_files:
        if (self.project_path / config_file).exists():
            config_files_found.append(config_file)
    if not config_files_found:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='critical', message='No dependency configuration files found', suggestion='Add requirements.txt, pyproject.toml, or setup.py'))
        score = 0
    else:
        for config_file in config_files_found:
            file_path = self.project_path / config_file
            file_issues = self._validate_config_file(file_path)
            issues.extend(file_issues)
            if file_issues:
                score -= len(file_issues) * 10
    return {'score': max(0, score), 'issues': issues}

def _validate_config_file(self, file_path: Path) -> List[InstallationIssue]:
    """Validate a specific configuration file."""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if file_path.name == 'requirements.txt':
            issues.extend(self._validate_requirements_txt(file_path, content))
        elif file_path.name == 'pyproject.toml':
            issues.extend(self._validate_pyproject_toml(file_path, content))
        elif file_path.name == 'setup.py':
            issues.extend(self._validate_setup_py(file_path, content))
    except Exception as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message=f'Cannot read {file_path.name}: {e}', file_path=str(file_path), suggestion='Fix file encoding or permissions'))
    return issues

def _validate_requirements_txt(self, file_path: Path, content: str) -> List[InstallationIssue]:
    """Validate requirements.txt file."""
    issues = []
    lines = content.strip().split('\n')
    if not lines or (len(lines) == 1 and (not lines[0].strip())):
        issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='major', message='requirements.txt is empty', file_path=str(file_path), suggestion='Add required dependencies to requirements.txt'))
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '==' not in line and '>=' not in line and ('~=' not in line):
            issues.append(InstallationIssue(issue_type=InstallationIssueType.DEPENDENCY_CONFLICT, severity='minor', message=f"Dependency '{line}' not version-pinned", file_path=str(file_path), suggestion='Consider pinning versions for reproducible builds'))
        if not re.match('^[a-zA-Z0-9_-]+', line.split('=')[0].split('>')[0].split('<')[0]):
            issues.append(InstallationIssue(issue_type=InstallationIssueType.DEPENDENCY_CONFLICT, severity='major', message=f'Invalid package name format: {line}', file_path=str(file_path), suggestion='Use valid Python package names'))
    return issues

def _validate_pyproject_toml(self, file_path: Path, content: str) -> List[InstallationIssue]:
    """Validate pyproject.toml file."""
    issues = []
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='minor', message='Cannot validate pyproject.toml - TOML parser not available', file_path=str(file_path), suggestion='Install tomli or use Python 3.11+'))
            return issues
    try:
        data = tomllib.loads(content)
        if 'project' not in data and 'tool' not in data:
            issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='major', message='pyproject.toml missing project or tool sections', file_path=str(file_path), suggestion='Add [project] section with dependencies'))
        if 'project' in data:
            project = data['project']
            if 'dependencies' not in project and 'requires' not in project:
                issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='minor', message='No dependencies specified in pyproject.toml', file_path=str(file_path), suggestion='Add dependencies list if project has requirements'))
    except Exception as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message=f'Invalid pyproject.toml format: {e}', file_path=str(file_path), suggestion='Fix TOML syntax errors'))
    return issues

def _validate_setup_py(self, file_path: Path, content: str) -> List[InstallationIssue]:
    """Validate setup.py file."""
    issues = []
    if 'setup(' not in content:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message='setup.py missing setup() call', file_path=str(file_path), suggestion='Add proper setup() function call'))
    if 'install_requires' not in content:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='minor', message='setup.py missing install_requires', file_path=str(file_path), suggestion='Add install_requires list if project has dependencies'))
    return issues

def _validate_dependencies(self) -> Dict[str, Any]:
    """Validate dependency specifications and conflicts."""
    issues = []
    score = 100
    requirements_file = self.project_path / 'requirements.txt'
    if requirements_file.exists():
        try:
            content = requirements_file.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip() and (not line.startswith('#'))]
            packages = {}
            for line in lines:
                if any((op in line for op in ['==', '>=', '<=', '>', '<', '~='])):
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('~=')[0].strip()
                    if package_name in packages:
                        issues.append(InstallationIssue(issue_type=InstallationIssueType.DEPENDENCY_CONFLICT, severity='major', message=f'Duplicate package specification: {package_name}', suggestion='Remove duplicate package specifications'))
                        score -= 20
                    packages[package_name] = line
            for line in lines:
                if any((char in line for char in ['!', '@', '#', '$', '%', '^', '&', '*'])):
                    issues.append(InstallationIssue(issue_type=InstallationIssueType.DEPENDENCY_CONFLICT, severity='major', message=f'Invalid package specification: {line}', suggestion='Fix package name and version specification'))
                    score -= 15
        except Exception as e:
            issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='minor', message=f'Could not parse requirements.txt: {e}', suggestion='Fix requirements.txt syntax'))
            score -= 10
    return {'score': max(0, score), 'issues': issues}

def _validate_setup_instructions(self) -> Dict[str, Any]:
    """Validate setup instructions in documentation."""
    issues = []
    score = 100
    doc_files_found = []
    for doc_file in self.doc_files:
        if (self.project_path / doc_file).exists():
            doc_files_found.append(self.project_path / doc_file)
    if not doc_files_found:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message='No installation documentation found', suggestion='Add README.md with installation instructions'))
        score = 30
    else:
        for doc_file in doc_files_found:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                sections_found = 0
                for section in self.required_sections:
                    if section in content:
                        sections_found += 1
                if sections_found == 0:
                    issues.append(InstallationIssue(issue_type=InstallationIssueType.SETUP_INSTRUCTIONS, severity='major', message=f'No installation instructions in {doc_file.name}', file_path=str(doc_file), suggestion='Add installation/setup section to documentation'))
                    score -= 20
                elif sections_found < 2:
                    issues.append(InstallationIssue(issue_type=InstallationIssueType.SETUP_INSTRUCTIONS, severity='minor', message=f'Limited installation instructions in {doc_file.name}', file_path=str(doc_file), suggestion='Expand installation instructions with more detail'))
                    score -= 10
                if '```' not in content and '`' not in content:
                    issues.append(InstallationIssue(issue_type=InstallationIssueType.SETUP_INSTRUCTIONS, severity='minor', message=f'No code examples in {doc_file.name}', file_path=str(doc_file), suggestion='Add code examples for installation commands'))
                    score -= 5
            except Exception as e:
                issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='minor', message=f'Cannot read {doc_file.name}: {e}', file_path=str(doc_file), suggestion='Fix file encoding or permissions'))
                score -= 5
    return {'score': max(0, score), 'issues': issues}

def _validate_documentation(self) -> Dict[str, Any]:
    """Validate installation documentation quality."""
    issues = []
    score = 100
    readme_path = None
    for readme_name in ['README.md', 'README.rst', 'README.txt']:
        if (self.project_path / readme_name).exists():
            readme_path = self.project_path / readme_name
            break
    if not readme_path:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='critical', message='No README file found', suggestion='Add README.md with project description and setup instructions'))
        score = 0
    else:
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if len(content.strip()) < 100:
                issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message='README too short', file_path=str(readme_path), suggestion='Expand README with detailed project information'))
                score -= 30
            essential_sections = ['installation', 'usage', 'setup']
            missing_sections = []
            for section in essential_sections:
                if section not in content.lower():
                    missing_sections.append(section)
            if missing_sections:
                issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message=f"README missing sections: {', '.join(missing_sections)}", file_path=str(readme_path), suggestion='Add missing sections to README'))
                score -= len(missing_sections) * 15
        except Exception as e:
            issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message=f'Cannot read README: {e}', file_path=str(readme_path), suggestion='Fix README file encoding or permissions'))
            score -= 20
    return {'score': max(0, score), 'issues': issues}

def _test_installation_process(self) -> Dict[str, Any]:
    """Test the actual installation process in a clean environment."""
    issues = []
    score = 100
    try:
        if (self.project_path / 'src').exists():
            import importlib.util
            init_file = self.project_path / 'src' / '__init__.py'
            if init_file.exists():
                spec = importlib.util.spec_from_file_location('test_module', init_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
    except ImportError as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message=f'Import test failed: {e}', suggestion='Fix import issues or missing dependencies'))
        score -= 30
    except Exception as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='minor', message=f'Installation test error: {e}', suggestion='Review project structure and dependencies'))
        score -= 10
    return {'score': max(0, score), 'issues': issues}

def _test_single_installation(self, temp_dir: Path) -> Dict[str, Any]:
    """Test a single installation attempt in a temporary directory."""
    try:
        project_copy = temp_dir / 'project'
        shutil.copytree(self.project_path, project_copy, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'venv', 'env', '.venv'))
        venv_path = temp_dir / 'venv'
        venv.create(venv_path, with_pip=True)
        if sys.platform == 'win32':
            pip_path = venv_path / 'Scripts' / 'pip'
        else:
            pip_path = venv_path / 'bin' / 'pip'
        if (project_copy / 'requirements.txt').exists():
            try:
                content = (project_copy / 'requirements.txt').read_text()
                lines = [line.strip() for line in content.split('\n') if line.strip() and (not line.startswith('#'))]
                for line in lines:
                    if any((char in line for char in ['!', '@', '#', '$', '%', '^', '&', '*'])):
                        return {'success': False, 'issues': [f'Invalid requirement: {line}']}
            except Exception as e:
                return {'success': False, 'issues': [f'Could not parse requirements: {e}']}
        return {'success': True, 'issues': []}
    except Exception as e:
        return {'success': False, 'issues': [f'Installation test failed: {e}']}
