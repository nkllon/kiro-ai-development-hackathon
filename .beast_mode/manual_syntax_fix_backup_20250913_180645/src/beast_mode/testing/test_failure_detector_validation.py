"""
Test Failure Detector Validation

This module was extracted from test_failure_detector.py
as part of RM-DDD compliance refactoring.
"""

import re
import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .rca_integration import TestFailureData
from .error_handler import RCAErrorHandler

def monitor_test_execution(self, test_command: str, working_dir: str='.') -> List[TestFailureData]:
    """
        Monitor pytest execution and capture failure information
        Requirements: 1.1 - Automatic test failure detection
        """
    self.total_test_runs_monitored += 1
    try:
        self.logger.info(f'Monitoring test execution: {test_command}')
        with self.error_handler.handle_rca_operation('monitor_test_execution', 'test_failure_detector'):
            json_output_file = f'/tmp/pytest_output_{int(datetime.now().timestamp())}.json'
        cmd_parts = test_command.split()
        if '--json-report' not in cmd_parts:
            cmd_parts.extend(['--json-report', f'--json-report-file={json_output_file}'])
        result = subprocess.run(cmd_parts, cwd=working_dir, capture_output=True, text=True, timeout=300)
        failures = []
        if os.path.exists(json_output_file):
            try:
                failures = self._parse_json_output(json_output_file)
                self.logger.info(f'Parsed {len(failures)} failures from JSON output')
                self.error_handler.monitor_component_health('json_parser', True, 100.0)
            except Exception as e:
                self.logger.warning(f'JSON parsing failed: {e}, falling back to text parsing')
                self.error_handler.monitor_component_health('json_parser', False, 1000.0)
            finally:
                try:
                    os.remove(json_output_file)
                except:
                    pass
        if not failures and result.returncode != 0:
            try:
                failures = self.parse_pytest_output(result.stdout + result.stderr)
                self.logger.info(f'Parsed {len(failures)} failures from text output')
                self.error_handler.monitor_component_health('text_parser', True, 200.0)
            except Exception as e:
                self.logger.error(f'Text parsing also failed: {e}')
                self.error_handler.monitor_component_health('text_parser', False, 2000.0)
                failures = [self._create_parsing_failure(test_command, str(e))]
        self.total_failures_detected += len(failures)
        if self.total_test_runs_monitored > 0:
            self.parsing_success_rate = (self.parsing_success_rate * (self.total_test_runs_monitored - 1) + (1.0 if failures or result.returncode == 0 else 0.0)) / self.total_test_runs_monitored
        return failures
    except subprocess.TimeoutExpired:
        self.logger.error('Test execution timeout - creating timeout failure')
        self.error_handler.monitor_component_health('test_execution', False, 300000.0)
        return [self._create_timeout_failure(test_command)]
    except Exception as e:
        self.logger.error(f'Test monitoring failed: {e}')
        self.error_handler.monitor_component_health('test_monitoring', False, 1000.0)
        return [self._create_monitoring_failure(test_command, str(e))]

def parse_pytest_output(self, output: str) -> List[TestFailureData]:
    """
        Parse pytest text output to extract failure information
        Requirements: 1.3, 5.1 - Extract stack traces, error messages, and context
        """
    try:
        failures = []
        lines = output.split('\n')
        in_failures_section = False
        current_failure = None
        current_traceback = []
        current_error_lines = []
        for i, line in enumerate(lines):
            if re.match(self.pytest_output_patterns['failure_header'], line):
                in_failures_section = True
                continue
            if not in_failures_section:
                continue
            failure_match = re.match(self.pytest_output_patterns['test_failure_start'], line)
            if failure_match:
                if current_failure:
                    failure_data = self._create_failure_data(current_failure, current_traceback, current_error_lines)
                    if failure_data:
                        failures.append(failure_data)
                current_failure = failure_match.group(1).strip()
                current_traceback = []
                current_error_lines = []
                continue
            if current_failure:
                if line.startswith('E '):
                    current_error_lines.append(line[2:].strip())
                elif line.startswith('>'):
                    current_traceback.append(line[1:].strip())
                elif line.strip() and (not line.startswith('_')):
                    current_traceback.append(line.strip())
        if current_failure:
            failure_data = self._create_failure_data(current_failure, current_traceback, current_error_lines)
            if failure_data:
                failures.append(failure_data)
        self.logger.info(f'Parsed {len(failures)} failures from pytest output')
        return failures
    except Exception as e:
        self.logger.error(f'Pytest output parsing failed: {e}')
        return []

def _parse_test_name(self, test_name: str) -> Tuple[str, str, Optional[str]]:
    """Parse pytest node ID to extract file, function, and class"""
    try:
        parts = test_name.split('::')
        test_file = parts[0] if parts else 'unknown'
        test_function = 'unknown'
        test_class = None
        if len(parts) >= 2:
            if len(parts) == 2:
                test_function = parts[1]
            elif len(parts) == 3:
                test_class = parts[1]
                test_function = parts[2]
        return (test_file, test_function, test_class)
    except Exception as e:
        self.logger.error(f'Test name parsing failed: {e}')
        return ('unknown', 'unknown', None)

def _get_pytest_version(self) -> str:
    """Get pytest version for context"""
    try:
        result = subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except:
        return 'unknown'
