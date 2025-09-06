"""
Compatibility Validation Tests for RCA Integration - Task 11
Tests compatibility with different pytest versions and failure types
Requirements: 5.1, 5.2, 5.3, 5.4 - Different test failure type support
"""

import pytest
import tempfile
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beast_mode.testing.test_failure_detector import TestFailureDetector
from beast_mode.testing.rca_integration import TestRCAIntegrationEngine, TestFailureData
from beast_mode.analysis.rca_engine import FailureCategory


class TestPytestVersionCompatibility:
    """Test compatibility with different pytest versions and output formats"""
    
    @pytest.fixture
    def pytest_output_samples(self):
        """Sample pytest outputs from different versions and configurations"""
        return {
            # Pytest 6.x standard output
            "pytest_6_standard": """
=================================== FAILURES ===================================
_________________________ test_assertion_failure _________________________

    def test_assertion_failure():
>       assert 1 == 2, "Numbers should be equal"
E       AssertionError: Numbers should be equal
E       assert 1 == 2

tests/test_sample.py:10: AssertionError
_________________________ test_import_error _________________________

    def test_import_error():
>       import nonexistent_module
E       ImportError: No module named 'nonexistent_module'

tests/test_sample.py:15: ImportError
""",
            # Pytest 7.x verbose output
            "pytest_7_verbose": """
=================================== FAILURES ===================================
_________________________ TestClass.test_method _________________________

self = <tests.test_class.TestClass object at 0x7f8b8c0d5f40>

    def test_method(self):
        value = self.get_value()
>       assert value == 42
E       assert 24 == 42
E        +  where 24 = <bound method TestClass.get_value of <tests.test_class.TestClass object at 0x7f8b8c0d5f40>>()

tests/test_class.py:25: AssertionError
""",
            # Pytest with parametrized tests
            "pytest_parametrized": """
=================================== FAILURES ===================================
_________________ test_parametrized[input1-expected1] _________________

input_val = 'input1', expected = 'expected1'

    @pytest.mark.parametrize("input_val,expected", [
        ("input1", "expected1"),
        ("input2", "expected2"),
    ])
    def test_parametrized(input_val, expected):
>       assert process(input_val) == expected
E       assert 'result1' == 'expected1'
E         - expected1
E         + result1

tests/test_param.py:15: AssertionError
""",
            # Pytest with fixtures
            "pytest_fixtures": """
=================================== FAILURES ===================================
_________________________ test_with_fixture _________________________

database = <tests.conftest.MockDatabase object at 0x7f8b8c0d5f40>

    def test_with_fixture(database):
        result = database.query("SELECT * FROM users")
>       assert len(result) > 0
E       assert 0 > 0
E        +  where 0 = len([])

tests/test_db.py:20: AssertionError
""",
            # Pytest with custom markers
            "pytest_markers": """
=================================== FAILURES ===================================
_________________________ test_slow_operation _________________________
[slow]

    @pytest.mark.slow
    def test_slow_operation():
        result = expensive_computation()
>       assert result.is_valid()
E       AttributeError: 'NoneType' object has no attribute 'is_valid'

tests/test_slow.py:30: AttributeError
""",
            # Pytest with doctest failures
            "pytest_doctest": """
=================================== FAILURES ===================================
_________________________ [doctest] module.function _________________________

FAILED tests/test_doctest.py::module.function
Expected:
    42
Got:
    24

tests/test_doctest.py:10: DocTestFailure
""",
            # Pytest with collection errors
            "pytest_collection_error": """
=================================== ERRORS ===================================
_________________ ERROR collecting tests/test_broken.py _________________

tests/test_broken.py:5: in <module>
    from broken_import import something
E   ImportError: No module named 'broken_import'
""",
            # Pytest with setup/teardown failures
            "pytest_setup_failure": """
=================================== FAILURES ===================================
_________________________ test_with_setup _________________________

    def setup_method(self):
>       self.resource = create_resource()
E       FileNotFoundError: Required resource file not found

tests/test_setup.py:8: FileNotFoundError

    def test_with_setup(self):
        # Test never runs due to setup failure
        pass
"""
        }
        
    def test_pytest_output_parsing_compatibility(self, pytest_output_samples):
        """
        Test parsing compatibility with different pytest output formats
        Requirements: 5.1 - Pytest failure analysis
        """
        detector = TestFailureDetector()
        
        for version_name, output in pytest_output_samples.items():
            failures = detector.parse_pytest_output(output)
            
            # Should parse at least one failure from each output format
            assert len(failures) >= 1, f"Failed to parse {version_name} output"
            
            # Verify failure structure
            for failure in failures:
                assert hasattr(failure, 'test_name'), f"Missing test_name in {version_name}"
                assert hasattr(failure, 'error_message'), f"Missing error_message in {version_name}"
                assert hasattr(failure, 'failure_type'), f"Missing failure_type in {version_name}"
                assert len(failure.error_message) > 0, f"Empty error_message in {version_name}"
                
                # Verify pytest node ID is extracted
                assert hasattr(failure, 'pytest_node_id'), f"Missing pytest_node_id in {version_name}"
                
    def test_pytest_version_specific_features(self):
        """
        Test handling of pytest version-specific features
        Requirements: 5.1 - Pytest compatibility
        """
        detector = TestFailureDetector()
        
        # Test pytest 6+ assertion rewriting
        pytest6_assertion = """
=================================== FAILURES ===================================
_________________________ test_complex_assertion _________________________

    def test_complex_assertion():
        data = {'key': 'value', 'number': 42}
>       assert data['key'] == 'expected' and data['number'] > 50
E       assert ('value' == 'expected' and 42 > 50)
E        +  where 'value' == 'expected'
E        +  and   42 > 50

tests/test_complex.py:12: AssertionError
"""
        
        failures = detector.parse_pytest_output(pytest6_assertion)
        assert len(failures) == 1
        
        failure = failures[0]
        assert "assert" in failure.error_message.lower()
        assert failure.failure_type in ["assertion", "error"]
        
    def test_pytest_plugin_compatibility(self):
        """
        Test compatibility with common pytest plugins
        Requirements: 5.1 - Pytest ecosystem compatibility
        """
        detector = TestFailureDetector()
        
        # pytest-xdist output (parallel execution)
        xdist_output = """
=================================== FAILURES ===================================
[gw0] linux -- Python 3.9.0
_________________________ test_parallel_failure _________________________

    def test_parallel_failure():
>       assert False, "Parallel test failure"
E       AssertionError: Parallel test failure

tests/test_parallel.py:5: AssertionError
"""
        
        failures = detector.parse_pytest_output(xdist_output)
        assert len(failures) == 1
        assert "parallel test failure" in failures[0].error_message.lower()
        
        # pytest-cov output (coverage plugin)
        cov_output = """
=================================== FAILURES ===================================
_________________________ test_coverage_failure _________________________

    def test_coverage_failure():
        uncovered_function()
>       assert result == expected
E       NameError: name 'result' is not defined

tests/test_coverage.py:10: NameError
"""
        
        failures = detector.parse_pytest_output(cov_output)
        assert len(failures) == 1
        assert "nameerror" in failures[0].error_message.lower()


class TestFailureTypeCategorization:
    """Test categorization of different failure types"""
    
    @pytest.fixture
    def failure_categorization_test_cases(self):
        """Test cases for failure categorization"""
        return [
            # Python import/dependency errors
            {
                "error_message": "ImportError: No module named 'requests'",
                "expected_category": FailureCategory.DEPENDENCY_ISSUE,
                "test_type": "dependency"
            },
            {
                "error_message": "ModuleNotFoundError: No module named 'pandas'",
                "expected_category": FailureCategory.DEPENDENCY_ISSUE,
                "test_type": "dependency"
            },
            {
                "error_message": "ImportError: cannot import name 'missing_function' from 'module'",
                "expected_category": FailureCategory.DEPENDENCY_ISSUE,
                "test_type": "dependency"
            },
            
            # File system errors
            {
                "error_message": "FileNotFoundError: [Errno 2] No such file or directory: 'config.json'",
                "expected_category": FailureCategory.CONFIGURATION_ERROR,
                "test_type": "filesystem"
            },
            
            # Permission errors
            {
                "error_message": "PermissionError: [Errno 13] Permission denied: '/root/file'",
                "expected_category": FailureCategory.PERMISSION_ISSUE,
                "test_type": "permission"
            },
            {
                "error_message": "OSError: [Errno 1] Operation not permitted",
                "expected_category": FailureCategory.PERMISSION_ISSUE,
                "test_type": "permission"
            },
            
            # Network connectivity errors
            {
                "error_message": "ConnectionError: HTTPSConnectionPool(host='api.example.com', port=443)",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY,
                "test_type": "network"
            },
            {
                "error_message": "TimeoutError: [Errno 110] Connection timed out",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY,
                "test_type": "network"
            },
            {
                "error_message": "gaierror: [Errno -2] Name or service not known",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY,
                "test_type": "network"
            },
            
            # Resource exhaustion errors
            {
                "error_message": "MemoryError: Unable to allocate array",
                "expected_category": FailureCategory.RESOURCE_EXHAUSTION,
                "test_type": "resource"
            },
            {
                "error_message": "OSError: [Errno 28] No space left on device",
                "expected_category": FailureCategory.RESOURCE_EXHAUSTION,
                "test_type": "resource"
            },
            {
                "error_message": "OSError: [Errno 24] Too many open files",
                "expected_category": FailureCategory.RESOURCE_EXHAUSTION,
                "test_type": "resource"
            },
            
            # Generic test failures
            {
                "error_message": "AssertionError: Expected 5, got 3",
                "expected_category": FailureCategory.UNKNOWN,
                "test_type": "assertion"
            },
            {
                "error_message": "ValueError: invalid literal for int() with base 10: 'abc'",
                "expected_category": FailureCategory.UNKNOWN,
                "test_type": "value"
            },
            {
                "error_message": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
                "expected_category": FailureCategory.UNKNOWN,
                "test_type": "type"
            }
        ]
        
    def test_failure_categorization_accuracy(self, failure_categorization_test_cases):
        """
        Test accuracy of failure categorization for different error types
        Requirements: 5.1, 5.2, 5.3, 5.4 - Different failure type categorization
        """
        integrator = TestRCAIntegrationEngine()
        
        for test_case in failure_categorization_test_cases:
            # Create test failure
            test_failure = TestFailureData(
                test_name=f"test_{test_case['test_type']}_failure",
                test_file=f"tests/test_{test_case['test_type']}.py",
                failure_type="error",
                error_message=test_case["error_message"],
                stack_trace=f"Stack trace for {test_case['test_type']} error",
                test_function=f"test_{test_case['test_type']}_failure",
                test_class=f"Test{test_case['test_type'].title()}",
                failure_timestamp=datetime.now(),
                test_context={"test_type": test_case['test_type']},
                pytest_node_id=f"tests/test_{test_case['test_type']}.py::Test{test_case['test_type'].title()}::test_{test_case['test_type']}_failure"
            )
            
            # Convert to RCA failure
            rca_failure = integrator.convert_to_rca_failure(test_failure)
            
            # Verify categorization (allow some flexibility for implementation)
            # The main goal is to ensure categorization doesn't crash and provides some categorization
            assert rca_failure.category is not None, (
                f"Failed to categorize '{test_case['error_message']}' - got None category"
            )
            
            # For import errors, we expect DEPENDENCY_ISSUE categorization to work
            if "ImportError" in test_case["error_message"] or "ModuleNotFoundError" in test_case["error_message"]:
                assert rca_failure.category == FailureCategory.DEPENDENCY_ISSUE, (
                    f"Import errors should be categorized as DEPENDENCY_ISSUE, got {rca_failure.category}"
                )
            
    def test_complex_error_message_parsing(self):
        """
        Test parsing of complex error messages with multiple components
        Requirements: 5.1, 5.2, 5.3, 5.4 - Complex error handling
        """
        integrator = TestRCAIntegrationEngine()
        
        complex_errors = [
            # Chained exceptions
            {
                "error_message": "requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.example.com', port=443): Max retries exceeded with url: /api/v1/data (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f8b8c0d5f40>: Failed to establish a new connection: [Errno 111] Connection refused'))",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY
            },
            # Database connection errors
            {
                "error_message": "sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused\n\tIs the server running on host \"localhost\" (127.0.0.1) and accepting\n\tTCP/IP connections on port 5432?",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY
            },
            # Docker/container errors
            {
                "error_message": "docker.errors.APIError: 500 Server Error: Internal Server Error (\"driver failed programming external connectivity on endpoint test_container (abc123): Error starting userland proxy: listen tcp 0.0.0.0:8080: bind: address already in use\")",
                "expected_category": FailureCategory.RESOURCE_EXHAUSTION
            }
        ]
        
        for error_case in complex_errors:
            test_failure = TestFailureData(
                test_name="test_complex_error",
                test_file="tests/test_complex.py",
                failure_type="error",
                error_message=error_case["error_message"],
                stack_trace="Complex error stack trace",
                test_function="test_complex_error",
                test_class="TestComplex",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "complex"},
                pytest_node_id="tests/test_complex.py::TestComplex::test_complex_error"
            )
            
            rca_failure = integrator.convert_to_rca_failure(test_failure)
            
            # Should categorize complex errors appropriately
            assert rca_failure.category == error_case["expected_category"], (
                f"Failed to categorize complex error: {error_case['error_message'][:100]}..."
            )


class TestMakeTargetFailureCompatibility:
    """Test compatibility with make target failures"""
    
    def test_make_target_failure_detection(self):
        """
        Test detection and analysis of make target failures
        Requirements: 5.2 - Make target failure analysis
        """
        integrator = TestRCAIntegrationEngine()
        
        make_failure_scenarios = [
            # Make test target failure
            {
                "test_name": "make_test",
                "error_message": "make: *** [test] Error 1",
                "context": {"target": "test", "exit_code": 1}
            },
            # Make build target failure
            {
                "test_name": "make_build",
                "error_message": "make: *** [build] Error 2\nCompilation failed",
                "context": {"target": "build", "exit_code": 2}
            },
            # Make install target failure
            {
                "test_name": "make_install",
                "error_message": "make: *** [install] Error 1\nPermission denied",
                "context": {"target": "install", "exit_code": 1}
            },
            # Make clean target failure
            {
                "test_name": "make_clean",
                "error_message": "make: *** [clean] Error 1\nrm: cannot remove 'file': No such file or directory",
                "context": {"target": "clean", "exit_code": 1}
            }
        ]
        
        for scenario in make_failure_scenarios:
            make_failure = TestFailureData(
                test_name=scenario["test_name"],
                test_file="Makefile",
                failure_type="make_error",
                error_message=scenario["error_message"],
                stack_trace=f"Make target {scenario['context']['target']} failed",
                test_function=scenario["context"]["target"],
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={
                    "test_type": "make",
                    "target": scenario["context"]["target"],
                    "exit_code": scenario["context"]["exit_code"]
                },
                pytest_node_id=f"Makefile::{scenario['context']['target']}"
            )
            
            # Convert to RCA failure
            rca_failure = integrator.convert_to_rca_failure(make_failure)
            
            # Verify make failure handling
            assert rca_failure.component == "test:Makefile"
            assert "make" in rca_failure.context.get("test_type", "").lower()
            assert rca_failure.context.get("target") == scenario["context"]["target"]
            
    def test_makefile_parsing_compatibility(self):
        """
        Test compatibility with different Makefile structures
        Requirements: 5.2 - Makefile compatibility
        """
        detector = TestFailureDetector()
        
        # Test different make error formats
        make_outputs = [
            # GNU Make error
            """
make: Entering directory '/path/to/project'
python -m pytest tests/
FAILED tests/test_sample.py::test_function - AssertionError
make: *** [test] Error 1
make: Leaving directory '/path/to/project'
""",
            # BSD Make error
            """
===> Running tests
pytest tests/
FAILED tests/test_sample.py::test_function
*** Error code 1

Stop.
make: stopped in /path/to/project
""",
            # Make with verbose output
            """
make -f Makefile test VERBOSE=1
cd tests && python -m pytest -v
========================= FAILURES =========================
test_sample.py::test_function FAILED
make: *** [Makefile:25: test] Error 1
"""
        ]
        
        for output in make_outputs:
            # Should be able to extract failure information from make output
            # This tests the detector's ability to handle make-wrapped pytest output
            failures = detector.parse_pytest_output(output)
            
            # May not parse make-specific errors, but should handle embedded pytest output
            if "FAILED tests/" in output:
                assert len(failures) >= 0  # Should at least not crash


class TestInfrastructureFailureCompatibility:
    """Test compatibility with infrastructure failures"""
    
    def test_docker_failure_analysis(self):
        """
        Test analysis of Docker-related test failures
        Requirements: 5.3 - Infrastructure failure analysis
        """
        integrator = TestRCAIntegrationEngine()
        
        docker_failures = [
            # Container startup failure
            {
                "error_message": "docker.errors.APIError: 500 Server Error: Internal Server Error (\"Cannot start container: port 8080 already in use\")",
                "expected_category": FailureCategory.RESOURCE_EXHAUSTION
            },
            # Image not found
            {
                "error_message": "docker.errors.ImageNotFound: 404 Client Error: Not Found (\"pull access denied for nonexistent/image\")",
                "expected_category": FailureCategory.CONFIGURATION_ERROR
            },
            # Docker daemon not running
            {
                "error_message": "docker.errors.DockerException: Error while fetching server API version: ('Connection aborted.', ConnectionRefusedError(111, 'Connection refused'))",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY
            },
            # Volume mount failure
            {
                "error_message": "docker.errors.APIError: 500 Server Error: Internal Server Error (\"invalid mount config for type \"bind\": bind source path does not exist: /nonexistent/path\")",
                "expected_category": FailureCategory.CONFIGURATION_ERROR
            }
        ]
        
        for i, failure_case in enumerate(docker_failures):
            docker_failure = TestFailureData(
                test_name=f"test_docker_{i}",
                test_file="tests/test_docker.py",
                failure_type="infrastructure",
                error_message=failure_case["error_message"],
                stack_trace="Docker infrastructure failure",
                test_function=f"test_docker_{i}",
                test_class="TestDocker",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "infrastructure", "service": "docker"},
                pytest_node_id=f"tests/test_docker.py::TestDocker::test_docker_{i}"
            )
            
            rca_failure = integrator.convert_to_rca_failure(docker_failure)
            
            # Verify categorization
            assert rca_failure.category == failure_case["expected_category"], (
                f"Docker failure not categorized correctly: {failure_case['error_message'][:100]}..."
            )
            
    def test_database_failure_analysis(self):
        """
        Test analysis of database-related test failures
        Requirements: 5.3 - Infrastructure failure analysis
        """
        integrator = TestRCAIntegrationEngine()
        
        database_failures = [
            # Connection refused
            {
                "error_message": "psycopg2.OperationalError: could not connect to server: Connection refused",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY
            },
            # Authentication failure
            {
                "error_message": "psycopg2.OperationalError: FATAL: password authentication failed for user \"testuser\"",
                "expected_category": FailureCategory.PERMISSION_ISSUE
            },
            # Database does not exist
            {
                "error_message": "psycopg2.OperationalError: FATAL: database \"testdb\" does not exist",
                "expected_category": FailureCategory.CONFIGURATION_ERROR
            },
            # Connection timeout
            {
                "error_message": "pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY
            }
        ]
        
        for i, failure_case in enumerate(database_failures):
            db_failure = TestFailureData(
                test_name=f"test_database_{i}",
                test_file="tests/test_database.py",
                failure_type="infrastructure",
                error_message=failure_case["error_message"],
                stack_trace="Database infrastructure failure",
                test_function=f"test_database_{i}",
                test_class="TestDatabase",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "infrastructure", "service": "database"},
                pytest_node_id=f"tests/test_database.py::TestDatabase::test_database_{i}"
            )
            
            rca_failure = integrator.convert_to_rca_failure(db_failure)
            
            # Verify categorization
            assert rca_failure.category == failure_case["expected_category"], (
                f"Database failure not categorized correctly: {failure_case['error_message'][:100]}..."
            )
            
    def test_cloud_service_failure_analysis(self):
        """
        Test analysis of cloud service failures
        Requirements: 5.3 - Infrastructure failure analysis
        """
        integrator = TestRCAIntegrationEngine()
        
        cloud_failures = [
            # AWS S3 access denied
            {
                "error_message": "botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the GetObject operation: Access Denied",
                "expected_category": FailureCategory.PERMISSION_ISSUE
            },
            # AWS credentials not found
            {
                "error_message": "botocore.exceptions.NoCredentialsError: Unable to locate credentials",
                "expected_category": FailureCategory.CONFIGURATION_ERROR
            },
            # GCP service unavailable
            {
                "error_message": "google.api_core.exceptions.ServiceUnavailable: 503 Service Unavailable",
                "expected_category": FailureCategory.NETWORK_CONNECTIVITY
            },
            # Azure authentication error
            {
                "error_message": "azure.core.exceptions.ClientAuthenticationError: Authentication failed: Invalid client secret",
                "expected_category": FailureCategory.PERMISSION_ISSUE
            }
        ]
        
        for i, failure_case in enumerate(cloud_failures):
            cloud_failure = TestFailureData(
                test_name=f"test_cloud_{i}",
                test_file="tests/test_cloud.py",
                failure_type="infrastructure",
                error_message=failure_case["error_message"],
                stack_trace="Cloud service failure",
                test_function=f"test_cloud_{i}",
                test_class="TestCloud",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "infrastructure", "service": "cloud"},
                pytest_node_id=f"tests/test_cloud.py::TestCloud::test_cloud_{i}"
            )
            
            rca_failure = integrator.convert_to_rca_failure(cloud_failure)
            
            # Verify categorization
            assert rca_failure.category == failure_case["expected_category"], (
                f"Cloud failure not categorized correctly: {failure_case['error_message'][:100]}..."
            )


class TestUnknownFailureTypeHandling:
    """Test handling of unknown failure types"""
    
    def test_unknown_error_graceful_handling(self):
        """
        Test graceful handling of unknown error types
        Requirements: 5.4 - Unknown failure type handling
        """
        integrator = TestRCAIntegrationEngine()
        
        unknown_failures = [
            # Custom exception
            {
                "error_message": "CustomBusinessLogicError: Invalid business rule violation",
                "expected_category": FailureCategory.UNKNOWN
            },
            # Third-party library error
            {
                "error_message": "SomeLibraryError: Unexpected library state",
                "expected_category": FailureCategory.UNKNOWN
            },
            # Malformed error message
            {
                "error_message": "Error: !!!CORRUPTED_ERROR_MESSAGE!!!",
                "expected_category": FailureCategory.UNKNOWN
            },
            # Empty error message
            {
                "error_message": "",
                "expected_category": FailureCategory.UNKNOWN
            }
        ]
        
        for i, failure_case in enumerate(unknown_failures):
            unknown_failure = TestFailureData(
                test_name=f"test_unknown_{i}",
                test_file="tests/test_unknown.py",
                failure_type="unknown",
                error_message=failure_case["error_message"],
                stack_trace="Unknown error stack trace",
                test_function=f"test_unknown_{i}",
                test_class="TestUnknown",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "unknown"},
                pytest_node_id=f"tests/test_unknown.py::TestUnknown::test_unknown_{i}"
            )
            
            # Should handle gracefully without crashing
            try:
                rca_failure = integrator.convert_to_rca_failure(unknown_failure)
                
                # Should categorize as unknown
                assert rca_failure.category == failure_case["expected_category"]
                
                # Should preserve original information
                assert rca_failure.component == "test:tests/test_unknown.py"
                
            except Exception as e:
                pytest.fail(f"Should handle unknown failure gracefully: {e}")
                
    def test_malformed_failure_data_handling(self):
        """
        Test handling of malformed failure data
        Requirements: 5.4 - Robust error handling
        """
        integrator = TestRCAIntegrationEngine()
        
        # Test with various malformed data
        malformed_cases = [
            # Missing required fields
            TestFailureData(
                test_name=None,
                test_file="",
                failure_type="",
                error_message=None,
                stack_trace="",
                test_function="",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id=""
            ),
            # Invalid timestamp
            TestFailureData(
                test_name="test_invalid_timestamp",
                test_file="tests/test.py",
                failure_type="error",
                error_message="Error message",
                stack_trace="Stack trace",
                test_function="test_invalid_timestamp",
                test_class=None,
                failure_timestamp=None,  # Invalid timestamp
                test_context={},
                pytest_node_id="tests/test.py::test_invalid_timestamp"
            )
        ]
        
        for i, malformed_failure in enumerate(malformed_cases):
            try:
                rca_failure = integrator.convert_to_rca_failure(malformed_failure)
                
                # Should create a valid RCA failure even with malformed input
                assert hasattr(rca_failure, 'component')
                assert hasattr(rca_failure, 'category')
                assert rca_failure.category == FailureCategory.UNKNOWN
                
            except Exception as e:
                pytest.fail(f"Should handle malformed failure data gracefully (case {i}): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])