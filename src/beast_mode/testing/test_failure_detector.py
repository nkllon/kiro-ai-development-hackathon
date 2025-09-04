"""
Beast Mode Framework - Test Failure Detection Infrastructure
Implements test failure detection and parsing for automatic RCA triggering
Requirements: 1.1, 1.3, 5.1, 5.2, 5.3
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


class TestFailureDetector(ReflectiveModule):
    """
    Detects and parses test failures from pytest execution
    Provides comprehensive failure information for RCA analysis
    """
    
    def __init__(self):
        super().__init__("test_failure_detector")
        
        # Detection metrics
        self.total_test_runs_monitored = 0
        self.total_failures_detected = 0
        self.parsing_success_rate = 0.0
        
        # Configuration
        self.pytest_output_patterns = {
            'failure_header': r'^FAILURES\s*$',
            'test_failure_start': r'^_{20,}\s+(.+?)\s+_{20,}$',
            'test_node_id': r'^(.+?)::\s*(.+?)(?:\s+FAILED)?$',
            'error_line': r'^E\s+(.+)$',
            'traceback_line': r'^>\s+(.+)$',
            'assertion_error': r'^>?\s*assert\s+(.+)$',
            'import_error': r'ImportError:\s*(.+)$',
            'file_not_found': r'FileNotFoundError:\s*(.+)$'
        }
        
        self._update_health_indicator(
            "test_failure_detection_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "Test failure detector ready for pytest monitoring"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "test_runs_monitored": self.total_test_runs_monitored,
            "failures_detected": self.total_failures_detected,
            "parsing_success_rate": self.parsing_success_rate,
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for test failure detection capability"""
        return not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {
            "detection_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "runs_monitored": self.total_test_runs_monitored,
                "failures_detected": self.total_failures_detected
            },
            "parsing_performance": {
                "status": "healthy" if self.parsing_success_rate > 0.8 else "degraded",
                "success_rate": self.parsing_success_rate,
                "pattern_matching": "operational"
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Test failure detection and parsing"""
        return "test_failure_detection_and_parsing"
        
    def monitor_test_execution(self, test_command: str, working_dir: str = ".") -> List[TestFailureData]:
        """
        Monitor pytest execution and capture failure information
        Requirements: 1.1 - Automatic test failure detection
        """
        self.total_test_runs_monitored += 1
        
        try:
            self.logger.info(f"Monitoring test execution: {test_command}")
            
            # Execute pytest with JSON output for structured parsing
            json_output_file = f"/tmp/pytest_output_{int(datetime.now().timestamp())}.json"
            
            # Run pytest with both human-readable and JSON output
            cmd_parts = test_command.split()
            if '--json-report' not in cmd_parts:
                cmd_parts.extend(['--json-report', f'--json-report-file={json_output_file}'])
                
            # Also capture stdout/stderr for fallback parsing
            result = subprocess.run(
                cmd_parts,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            failures = []
            
            # Try JSON parsing first (more reliable)
            if os.path.exists(json_output_file):
                try:
                    failures = self._parse_json_output(json_output_file)
                    self.logger.info(f"Parsed {len(failures)} failures from JSON output")
                except Exception as e:
                    self.logger.warning(f"JSON parsing failed: {e}, falling back to text parsing")
                finally:
                    # Clean up temp file
                    try:
                        os.remove(json_output_file)
                    except:
                        pass
                        
            # Fallback to text parsing if JSON failed or unavailable
            if not failures and result.returncode != 0:
                failures = self.parse_pytest_output(result.stdout + result.stderr)
                self.logger.info(f"Parsed {len(failures)} failures from text output")
                
            self.total_failures_detected += len(failures)
            
            # Update parsing success rate
            if self.total_test_runs_monitored > 0:
                self.parsing_success_rate = (
                    (self.parsing_success_rate * (self.total_test_runs_monitored - 1) + 
                     (1.0 if failures or result.returncode == 0 else 0.0)) / 
                    self.total_test_runs_monitored
                )
                
            return failures
            
        except subprocess.TimeoutExpired:
            self.logger.error("Test execution timeout - creating timeout failure")
            return [self._create_timeout_failure(test_command)]
        except Exception as e:
            self.logger.error(f"Test monitoring failed: {e}")
            return [self._create_monitoring_failure(test_command, str(e))]
            
    def parse_pytest_output(self, output: str) -> List[TestFailureData]:
        """
        Parse pytest text output to extract failure information
        Requirements: 1.3, 5.1 - Extract stack traces, error messages, and context
        """
        try:
            failures = []
            lines = output.split('\n')
            
            # Find the FAILURES section
            in_failures_section = False
            current_failure = None
            current_traceback = []
            current_error_lines = []
            
            for i, line in enumerate(lines):
                # Check if we're entering the failures section
                if re.match(self.pytest_output_patterns['failure_header'], line):
                    in_failures_section = True
                    continue
                    
                if not in_failures_section:
                    continue
                    
                # Check for test failure start
                failure_match = re.match(self.pytest_output_patterns['test_failure_start'], line)
                if failure_match:
                    # Save previous failure if exists
                    if current_failure:
                        failure_data = self._create_failure_data(
                            current_failure, current_traceback, current_error_lines
                        )
                        if failure_data:
                            failures.append(failure_data)
                            
                    # Start new failure
                    current_failure = failure_match.group(1).strip()
                    current_traceback = []
                    current_error_lines = []
                    continue
                    
                # Collect error lines and traceback
                if current_failure:
                    if line.startswith('E '):
                        current_error_lines.append(line[2:].strip())
                    elif line.startswith('>'):
                        current_traceback.append(line[1:].strip())
                    elif line.strip() and not line.startswith('_'):
                        # Additional context lines
                        current_traceback.append(line.strip())
                        
            # Handle last failure
            if current_failure:
                failure_data = self._create_failure_data(
                    current_failure, current_traceback, current_error_lines
                )
                if failure_data:
                    failures.append(failure_data)
                    
            self.logger.info(f"Parsed {len(failures)} failures from pytest output")
            return failures
            
        except Exception as e:
            self.logger.error(f"Pytest output parsing failed: {e}")
            return []
            
    def extract_failure_context(self, failure_info: dict) -> Dict[str, Any]:
        """
        Extract comprehensive context from failure information
        Requirements: 5.2, 5.3 - Comprehensive failure context extraction
        """
        try:
            context = {
                "timestamp": datetime.now().isoformat(),
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "environment_variables": {},
                "pytest_version": self._get_pytest_version()
            }
            
            # Extract relevant environment variables
            relevant_env_vars = [
                'PYTHONPATH', 'PATH', 'VIRTUAL_ENV', 'PYTEST_CURRENT_TEST',
                'CI', 'GITHUB_ACTIONS', 'RCA_ON_FAILURE', 'RCA_TIMEOUT'
            ]
            
            for var in relevant_env_vars:
                if var in os.environ:
                    context["environment_variables"][var] = os.environ[var]
                    
            # Add failure-specific context from failure_info
            if isinstance(failure_info, dict):
                context.update(failure_info)
                
            return context
            
        except Exception as e:
            self.logger.error(f"Context extraction failed: {e}")
            return {"extraction_error": str(e)}
            
    def create_failure_object(self, test_name: str, error_info: dict) -> TestFailureData:
        """
        Create TestFailure object from parsed information
        Requirements: 5.1 - Create comprehensive failure information
        """
        try:
            # Parse test name to extract components
            test_file, test_function, test_class = self._parse_test_name(test_name)
            
            # Determine failure type
            failure_type = self._determine_failure_type(error_info.get('error_message', ''))
            
            # Extract context
            context = self.extract_failure_context(error_info)
            
            return TestFailureData(
                test_name=test_name,
                test_file=test_file,
                failure_type=failure_type,
                error_message=error_info.get('error_message', 'Unknown error'),
                stack_trace=error_info.get('stack_trace', ''),
                test_function=test_function,
                test_class=test_class,
                failure_timestamp=datetime.now(),
                test_context=context,
                pytest_node_id=test_name
            )
            
        except Exception as e:
            self.logger.error(f"Failure object creation failed: {e}")
            # Return minimal failure object
            return TestFailureData(
                test_name=test_name,
                test_file="unknown",
                failure_type="creation_error",
                error_message=f"Failed to create failure object: {e}",
                stack_trace="",
                test_function="unknown",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={"creation_error": str(e)},
                pytest_node_id=test_name
            )
            
    # Private helper methods
    
    def _parse_json_output(self, json_file: str) -> List[TestFailureData]:
        """Parse pytest JSON output for failure information"""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            failures = []
            
            # Extract failed tests from JSON report
            if 'tests' in data:
                for test in data['tests']:
                    if test.get('outcome') in ['failed', 'error']:
                        failure_data = self._create_failure_from_json(test)
                        if failure_data:
                            failures.append(failure_data)
                            
            return failures
            
        except Exception as e:
            self.logger.error(f"JSON output parsing failed: {e}")
            return []
            
    def _create_failure_from_json(self, test_data: dict) -> Optional[TestFailureData]:
        """Create failure data from JSON test information"""
        try:
            node_id = test_data.get('nodeid', 'unknown')
            test_file, test_function, test_class = self._parse_test_name(node_id)
            
            # Extract error information
            call_info = test_data.get('call', {})
            error_message = call_info.get('longrepr', 'Unknown error')
            
            # Extract stack trace if available
            stack_trace = ""
            if 'traceback' in call_info:
                stack_trace = '\n'.join([
                    entry.get('line', '') for entry in call_info['traceback']
                ])
                
            failure_type = self._determine_failure_type(error_message)
            
            return TestFailureData(
                test_name=node_id,
                test_file=test_file,
                failure_type=failure_type,
                error_message=error_message,
                stack_trace=stack_trace,
                test_function=test_function,
                test_class=test_class,
                failure_timestamp=datetime.now(),
                test_context={"json_source": True, "duration": test_data.get('duration', 0)},
                pytest_node_id=node_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create failure from JSON: {e}")
            return None
            
    def _create_failure_data(self, test_name: str, traceback: List[str], error_lines: List[str]) -> Optional[TestFailureData]:
        """Create failure data from parsed text output"""
        try:
            if not error_lines and not traceback:
                return None
                
            test_file, test_function, test_class = self._parse_test_name(test_name)
            
            error_message = ' '.join(error_lines) if error_lines else 'Unknown error'
            stack_trace = '\n'.join(traceback) if traceback else ''
            
            failure_type = self._determine_failure_type(error_message)
            
            return TestFailureData(
                test_name=test_name,
                test_file=test_file,
                failure_type=failure_type,
                error_message=error_message,
                stack_trace=stack_trace,
                test_function=test_function,
                test_class=test_class,
                failure_timestamp=datetime.now(),
                test_context={"text_source": True},
                pytest_node_id=test_name
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create failure data: {e}")
            return None
            
    def _parse_test_name(self, test_name: str) -> Tuple[str, str, Optional[str]]:
        """Parse pytest node ID to extract file, function, and class"""
        try:
            # Format: path/to/file.py::TestClass::test_method or path/to/file.py::test_function
            parts = test_name.split('::')
            
            test_file = parts[0] if parts else 'unknown'
            test_function = 'unknown'
            test_class = None
            
            if len(parts) >= 2:
                if len(parts) == 2:
                    # file.py::test_function
                    test_function = parts[1]
                elif len(parts) == 3:
                    # file.py::TestClass::test_method
                    test_class = parts[1]
                    test_function = parts[2]
                    
            return test_file, test_function, test_class
            
        except Exception as e:
            self.logger.error(f"Test name parsing failed: {e}")
            return 'unknown', 'unknown', None
            
    def _determine_failure_type(self, error_message: str) -> str:
        """Determine failure type from error message"""
        error_lower = error_message.lower()
        
        if 'assertionerror' in error_lower or 'assert' in error_lower:
            return 'assertion'
        elif 'importerror' in error_lower or 'modulenotfounderror' in error_lower:
            return 'import'
        elif 'filenotfounderror' in error_lower:
            return 'file_not_found'
        elif 'permissionerror' in error_lower:
            return 'permission'
        elif 'timeout' in error_lower:
            return 'timeout'
        elif 'connectionerror' in error_lower or 'network' in error_lower:
            return 'network'
        elif 'memoryerror' in error_lower:
            return 'memory'
        else:
            return 'error'
            
    def _get_pytest_version(self) -> str:
        """Get pytest version for context"""
        try:
            result = subprocess.run(['python3', '-m', 'pytest', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except:
            return 'unknown'
            
    def _create_timeout_failure(self, test_command: str) -> TestFailureData:
        """Create failure object for test execution timeout"""
        return TestFailureData(
            test_name="test_execution_timeout",
            test_file="timeout",
            failure_type="timeout",
            error_message=f"Test execution timeout: {test_command}",
            stack_trace="Test execution exceeded 5 minute timeout",
            test_function="timeout",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={"timeout": True, "command": test_command},
            pytest_node_id="timeout::execution"
        )
        
    def _create_monitoring_failure(self, test_command: str, error: str) -> TestFailureData:
        """Create failure object for monitoring errors"""
        return TestFailureData(
            test_name="test_monitoring_error",
            test_file="monitoring",
            failure_type="monitoring_error",
            error_message=f"Test monitoring failed: {error}",
            stack_trace=f"Command: {test_command}\nError: {error}",
            test_function="monitoring",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={"monitoring_error": True, "command": test_command},
            pytest_node_id="monitoring::error"
        )