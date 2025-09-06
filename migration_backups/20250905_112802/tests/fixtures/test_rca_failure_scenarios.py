"""
Test Fixtures with Synthetic and Real Failure Scenarios - Task 11
Provides comprehensive test fixtures for RCA integration testing
Requirements: All requirements - Test fixtures for validation
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from src.beast_mode.testing.rca_integration import TestFailureData


@dataclass
class FailureScenario:
    """Container for a complete failure scenario"""
    name: str
    description: str
    failures: List[TestFailureData]
    expected_groupings: int
    expected_priority_order: List[str]
    expected_categories: List[str]
    context: Dict[str, Any]


class RCAFailureScenarioFixtures:
    """Comprehensive failure scenario fixtures for RCA testing"""
    
    @pytest.fixture
    def synthetic_import_error_scenario(self):
        """Synthetic scenario: Multiple import errors in related modules"""
        base_time = datetime.now()
        
        failures = [
            TestFailureData(
                test_name="test_pandas_import",
                test_file="tests/test_data_analysis.py",
                failure_type="error",
                error_message="ImportError: No module named 'pandas'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_data_analysis.py\", line 3, in test_pandas_import\n    import pandas as pd\nImportError: No module named 'pandas'",
                test_function="test_pandas_import",
                test_class="TestDataAnalysis",
                failure_timestamp=base_time,
                test_context={"test_type": "unit", "category": "data_analysis", "priority": "high"},
                pytest_node_id="tests/test_data_analysis.py::TestDataAnalysis::test_pandas_import"
            ),
            TestFailureData(
                test_name="test_numpy_import",
                test_file="tests/test_data_analysis.py",
                failure_type="error",
                error_message="ImportError: No module named 'numpy'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_data_analysis.py\", line 8, in test_numpy_import\n    import numpy as np\nImportError: No module named 'numpy'",
                test_function="test_numpy_import",
                test_class="TestDataAnalysis",
                failure_timestamp=base_time - timedelta(minutes=1),
                test_context={"test_type": "unit", "category": "data_analysis", "priority": "high"},
                pytest_node_id="tests/test_data_analysis.py::TestDataAnalysis::test_numpy_import"
            ),
            TestFailureData(
                test_name="test_matplotlib_import",
                test_file="tests/test_visualization.py",
                failure_type="error",
                error_message="ImportError: No module named 'matplotlib'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_visualization.py\", line 5, in test_matplotlib_import\n    import matplotlib.pyplot as plt\nImportError: No module named 'matplotlib'",
                test_function="test_matplotlib_import",
                test_class="TestVisualization",
                failure_timestamp=base_time - timedelta(minutes=2),
                test_context={"test_type": "unit", "category": "visualization", "priority": "medium"},
                pytest_node_id="tests/test_visualization.py::TestVisualization::test_matplotlib_import"
            )
        ]
        
        return FailureScenario(
            name="synthetic_import_error_scenario",
            description="Multiple related import errors for data science dependencies",
            failures=failures,
            expected_groupings=2,  # data_analysis and visualization groups
            expected_priority_order=["test_pandas_import", "test_numpy_import", "test_matplotlib_import"],
            expected_categories=["DEPENDENCY_ISSUE"],
            context={
                "scenario_type": "synthetic",
                "root_cause": "missing_dependencies",
                "fix_suggestion": "pip install pandas numpy matplotlib"
            }
        )
        
    @pytest.fixture
    def synthetic_configuration_error_scenario(self):
        """Synthetic scenario: Configuration file and environment issues"""
        base_time = datetime.now()
        
        failures = [
            TestFailureData(
                test_name="test_config_file_loading",
                test_file="tests/test_config.py",
                failure_type="error",
                error_message="FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_config.py\", line 10, in test_config_file_loading\n    with open('config.yaml', 'r') as f:\nFileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'",
                test_function="test_config_file_loading",
                test_class="TestConfig",
                failure_timestamp=base_time,
                test_context={"test_type": "integration", "category": "configuration", "priority": "critical"},
                pytest_node_id="tests/test_config.py::TestConfig::test_config_file_loading"
            ),
            TestFailureData(
                test_name="test_environment_variables",
                test_file="tests/test_config.py",
                failure_type="error",
                error_message="KeyError: 'DATABASE_URL'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_config.py\", line 20, in test_environment_variables\n    db_url = os.environ['DATABASE_URL']\nKeyError: 'DATABASE_URL'",
                test_function="test_environment_variables",
                test_class="TestConfig",
                failure_timestamp=base_time - timedelta(minutes=1),
                test_context={"test_type": "integration", "category": "configuration", "priority": "critical"},
                pytest_node_id="tests/test_config.py::TestConfig::test_environment_variables"
            ),
            TestFailureData(
                test_name="test_secrets_file",
                test_file="tests/test_security.py",
                failure_type="error",
                error_message="PermissionError: [Errno 13] Permission denied: '/etc/secrets/api_key'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_security.py\", line 15, in test_secrets_file\n    with open('/etc/secrets/api_key', 'r') as f:\nPermissionError: [Errno 13] Permission denied: '/etc/secrets/api_key'",
                test_function="test_secrets_file",
                test_class="TestSecurity",
                failure_timestamp=base_time - timedelta(minutes=2),
                test_context={"test_type": "integration", "category": "security", "priority": "critical"},
                pytest_node_id="tests/test_security.py::TestSecurity::test_secrets_file"
            )
        ]
        
        return FailureScenario(
            name="synthetic_configuration_error_scenario",
            description="Configuration and environment setup failures",
            failures=failures,
            expected_groupings=2,  # configuration and security groups
            expected_priority_order=["test_config_file_loading", "test_environment_variables", "test_secrets_file"],
            expected_categories=["CONFIGURATION_ERROR", "PERMISSION_ISSUE"],
            context={
                "scenario_type": "synthetic",
                "root_cause": "missing_configuration",
                "fix_suggestion": "Create config files and set environment variables"
            }
        )
        
    @pytest.fixture
    def synthetic_network_connectivity_scenario(self):
        """Synthetic scenario: Network and service connectivity issues"""
        base_time = datetime.now()
        
        failures = [
            TestFailureData(
                test_name="test_api_connection",
                test_file="tests/test_api.py",
                failure_type="error",
                error_message="ConnectionError: HTTPSConnectionPool(host='api.example.com', port=443): Max retries exceeded",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_api.py\", line 25, in test_api_connection\n    response = requests.get('https://api.example.com/health')\nConnectionError: HTTPSConnectionPool(host='api.example.com', port=443): Max retries exceeded",
                test_function="test_api_connection",
                test_class="TestAPI",
                failure_timestamp=base_time,
                test_context={"test_type": "integration", "category": "api", "priority": "high"},
                pytest_node_id="tests/test_api.py::TestAPI::test_api_connection"
            ),
            TestFailureData(
                test_name="test_database_connection",
                test_file="tests/test_database.py",
                failure_type="error",
                error_message="psycopg2.OperationalError: could not connect to server: Connection refused",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_database.py\", line 30, in test_database_connection\n    conn = psycopg2.connect(DATABASE_URL)\npsycopg2.OperationalError: could not connect to server: Connection refused",
                test_function="test_database_connection",
                test_class="TestDatabase",
                failure_timestamp=base_time - timedelta(minutes=1),
                test_context={"test_type": "integration", "category": "database", "priority": "critical"},
                pytest_node_id="tests/test_database.py::TestDatabase::test_database_connection"
            ),
            TestFailureData(
                test_name="test_redis_connection",
                test_file="tests/test_cache.py",
                failure_type="error",
                error_message="redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_cache.py\", line 20, in test_redis_connection\n    r = redis.Redis(host='localhost', port=6379)\nredis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.",
                test_function="test_redis_connection",
                test_class="TestCache",
                failure_timestamp=base_time - timedelta(minutes=2),
                test_context={"test_type": "integration", "category": "cache", "priority": "medium"},
                pytest_node_id="tests/test_cache.py::TestCache::test_redis_connection"
            )
        ]
        
        return FailureScenario(
            name="synthetic_network_connectivity_scenario",
            description="Network connectivity and service availability failures",
            failures=failures,
            expected_groupings=3,  # api, database, cache groups
            expected_priority_order=["test_database_connection", "test_api_connection", "test_redis_connection"],
            expected_categories=["NETWORK_CONNECTIVITY"],
            context={
                "scenario_type": "synthetic",
                "root_cause": "service_unavailability",
                "fix_suggestion": "Start required services and check network connectivity"
            }
        )
        
    @pytest.fixture
    def real_django_test_failure_scenario(self):
        """Real scenario: Django application test failures"""
        base_time = datetime.now()
        
        failures = [
            TestFailureData(
                test_name="test_user_model_creation",
                test_file="tests/test_models.py",
                failure_type="error",
                error_message="django.db.utils.OperationalError: no such table: auth_user",
                stack_trace="Traceback (most recent call last):\n  File \"/usr/local/lib/python3.9/site-packages/django/db/backends/sqlite3/base.py\", line 423, in execute\n    return Database.execute(self, query, params)\nsqlite3.OperationalError: no such table: auth_user\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"tests/test_models.py\", line 15, in test_user_model_creation\n    user = User.objects.create_user('testuser', 'test@example.com', 'password')\ndjango.db.utils.OperationalError: no such table: auth_user",
                test_function="test_user_model_creation",
                test_class="TestUserModel",
                failure_timestamp=base_time,
                test_context={"test_type": "integration", "framework": "django", "category": "database", "priority": "critical"},
                pytest_node_id="tests/test_models.py::TestUserModel::test_user_model_creation"
            ),
            TestFailureData(
                test_name="test_view_response",
                test_file="tests/test_views.py",
                failure_type="assertion",
                error_message="AssertionError: 500 != 200 : Expected successful response, got server error",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_views.py\", line 25, in test_view_response\n    self.assertEqual(response.status_code, 200, \"Expected successful response, got server error\")\nAssertionError: 500 != 200 : Expected successful response, got server error",
                test_function="test_view_response",
                test_class="TestViews",
                failure_timestamp=base_time - timedelta(minutes=1),
                test_context={"test_type": "integration", "framework": "django", "category": "views", "priority": "high"},
                pytest_node_id="tests/test_views.py::TestViews::test_view_response"
            ),
            TestFailureData(
                test_name="test_template_rendering",
                test_file="tests/test_templates.py",
                failure_type="error",
                error_message="django.template.TemplateDoesNotExist: base.html",
                stack_trace="Traceback (most recent call last):\n  File \"/usr/local/lib/python3.9/site-packages/django/template/loader.py\", line 19, in get_template\n    return engine.get_template(template_name)\n  File \"/usr/local/lib/python3.9/site-packages/django/template/backends/django.py\", line 34, in get_template\n    return Template(self.engine.get_template(template_name), self)\n  File \"/usr/local/lib/python3.9/site-packages/django/template/engine.py\", line 143, in get_template\n    template, origin = self.find_template(template_name)\n  File \"/usr/local/lib/python3.9/site-packages/django/template/engine.py\", line 125, in find_template\n    template = loader.get_template(name, skip=skip)\n  File \"/usr/local/lib/python3.9/site-packages/django/template/loaders/filesystem.py\", line 30, in get_template\n    contents, origin = self.get_contents(origin)\n  File \"/usr/local/lib/python3.9/site-packages/django/template/loaders/base.py\", line 26, in get_contents\n    data = f.read()\ndjango.template.TemplateDoesNotExist: base.html",
                test_function="test_template_rendering",
                test_class="TestTemplates",
                failure_timestamp=base_time - timedelta(minutes=2),
                test_context={"test_type": "integration", "framework": "django", "category": "templates", "priority": "medium"},
                pytest_node_id="tests/test_templates.py::TestTemplates::test_template_rendering"
            )
        ]
        
        return FailureScenario(
            name="real_django_test_failure_scenario",
            description="Real Django application test failures",
            failures=failures,
            expected_groupings=3,  # models, views, templates groups
            expected_priority_order=["test_user_model_creation", "test_view_response", "test_template_rendering"],
            expected_categories=["CONFIGURATION_ERROR", "UNKNOWN"],
            context={
                "scenario_type": "real",
                "framework": "django",
                "root_cause": "missing_migrations_and_templates",
                "fix_suggestion": "Run migrations and create template files"
            }
        )
        
    @pytest.fixture
    def real_fastapi_test_failure_scenario(self):
        """Real scenario: FastAPI application test failures"""
        base_time = datetime.now()
        
        failures = [
            TestFailureData(
                test_name="test_api_endpoint_authentication",
                test_file="tests/test_api_endpoints.py",
                failure_type="assertion",
                error_message="AssertionError: 401 != 200 : Authentication failed for protected endpoint",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_api_endpoints.py\", line 35, in test_api_endpoint_authentication\n    assert response.status_code == 200, \"Authentication failed for protected endpoint\"\nAssertionError: 401 != 200 : Authentication failed for protected endpoint",
                test_function="test_api_endpoint_authentication",
                test_class="TestAPIEndpoints",
                failure_timestamp=base_time,
                test_context={"test_type": "integration", "framework": "fastapi", "category": "authentication", "priority": "critical"},
                pytest_node_id="tests/test_api_endpoints.py::TestAPIEndpoints::test_api_endpoint_authentication"
            ),
            TestFailureData(
                test_name="test_database_session",
                test_file="tests/test_database.py",
                failure_type="error",
                error_message="sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users",
                stack_trace="Traceback (most recent call last):\n  File \"/usr/local/lib/python3.9/site-packages/sqlalchemy/engine/base.py\", line 1900, in _execute_context\n    self.dialect.do_execute(\n  File \"/usr/local/lib/python3.9/site-packages/sqlalchemy/engine/default.py\", line 736, in do_execute\n    cursor.execute(statement, parameters)\nsqlite3.OperationalError: no such table: users\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"tests/test_database.py\", line 20, in test_database_session\n    result = session.execute(select(User)).scalars().all()\nsqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users",
                test_function="test_database_session",
                test_class="TestDatabase",
                failure_timestamp=base_time - timedelta(minutes=1),
                test_context={"test_type": "integration", "framework": "fastapi", "category": "database", "priority": "critical"},
                pytest_node_id="tests/test_database.py::TestDatabase::test_database_session"
            ),
            TestFailureData(
                test_name="test_pydantic_validation",
                test_file="tests/test_models.py",
                failure_type="error",
                error_message="pydantic.ValidationError: 1 validation error for UserCreate\nemail\n  field required (type=value_error.missing)",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_models.py\", line 30, in test_pydantic_validation\n    user_data = UserCreate(name=\"Test User\")\npydantic.ValidationError: 1 validation error for UserCreate\nemail\n  field required (type=value_error.missing)",
                test_function="test_pydantic_validation",
                test_class="TestModels",
                failure_timestamp=base_time - timedelta(minutes=2),
                test_context={"test_type": "unit", "framework": "fastapi", "category": "validation", "priority": "medium"},
                pytest_node_id="tests/test_models.py::TestModels::test_pydantic_validation"
            )
        ]
        
        return FailureScenario(
            name="real_fastapi_test_failure_scenario",
            description="Real FastAPI application test failures",
            failures=failures,
            expected_groupings=3,  # authentication, database, validation groups
            expected_priority_order=["test_api_endpoint_authentication", "test_database_session", "test_pydantic_validation"],
            expected_categories=["UNKNOWN", "CONFIGURATION_ERROR"],
            context={
                "scenario_type": "real",
                "framework": "fastapi",
                "root_cause": "missing_database_setup_and_auth_config",
                "fix_suggestion": "Set up database tables and configure authentication"
            }
        )
        
    @pytest.fixture
    def real_data_science_pipeline_scenario(self):
        """Real scenario: Data science pipeline test failures"""
        base_time = datetime.now()
        
        failures = [
            TestFailureData(
                test_name="test_data_loading",
                test_file="tests/test_data_pipeline.py",
                failure_type="error",
                error_message="FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/dataset.csv'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_data_pipeline.py\", line 15, in test_data_loading\n    df = pd.read_csv('data/raw/dataset.csv')\n  File \"/usr/local/lib/python3.9/site-packages/pandas/io/parsers/readers.py\", line 912, in read_csv\n    return _read(filepath_or_buffer, kwds)\n  File \"/usr/local/lib/python3.9/site-packages/pandas/io/parsers/readers.py\", line 577, in _read\n    parser = TextFileReader(filepath_or_buffer, **kwds)\n  File \"/usr/local/lib/python3.9/site-packages/pandas/io/parsers/readers.py\", line 1407, in __init__\n    self._engine = self._make_engine(f, self.engine)\n  File \"/usr/local/lib/python3.9/site-packages/pandas/io/parsers/readers.py\", line 1661, in _make_engine\n    self.handles = get_handle(\n  File \"/usr/local/lib/python3.9/site-packages/pandas/io/common.py\", line 859, in get_handle\n    handle = open(\nFileNotFoundError: [Errno 2] No such file or directory: 'data/raw/dataset.csv'",
                test_function="test_data_loading",
                test_class="TestDataPipeline",
                failure_timestamp=base_time,
                test_context={"test_type": "integration", "category": "data_pipeline", "priority": "critical"},
                pytest_node_id="tests/test_data_pipeline.py::TestDataPipeline::test_data_loading"
            ),
            TestFailureData(
                test_name="test_model_training",
                test_file="tests/test_ml_model.py",
                failure_type="error",
                error_message="ValueError: Input contains NaN, infinity or a value too large for dtype('float64').",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_ml_model.py\", line 25, in test_model_training\n    model.fit(X_train, y_train)\n  File \"/usr/local/lib/python3.9/site-packages/sklearn/linear_model/_base.py\", line 648, in fit\n    X, y = self._validate_data(\n  File \"/usr/local/lib/python3.9/site-packages/sklearn/base.py\", line 581, in _validate_data\n    X, y = check_X_y(X, y, accept_sparse=accept_sparse,\n  File \"/usr/local/lib/python3.9/site-packages/sklearn/utils/validation.py\", line 1074, in check_X_y\n    X = check_array(\n  File \"/usr/local/lib/python3.9/site-packages/sklearn/utils/validation.py\", line 856, in check_array\n    _assert_all_finite(array, allow_nan=force_all_finite == 'allow-nan')\n  File \"/usr/local/lib/python3.9/site-packages/sklearn/utils/validation.py\", line 103, in _assert_all_finite\n    raise ValueError(\nValueError: Input contains NaN, infinity or a value too large for dtype('float64').",
                test_function="test_model_training",
                test_class="TestMLModel",
                failure_timestamp=base_time - timedelta(minutes=1),
                test_context={"test_type": "integration", "category": "machine_learning", "priority": "high"},
                pytest_node_id="tests/test_ml_model.py::TestMLModel::test_model_training"
            ),
            TestFailureData(
                test_name="test_feature_engineering",
                test_file="tests/test_features.py",
                failure_type="error",
                error_message="KeyError: 'target_column'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_features.py\", line 20, in test_feature_engineering\n    target = df['target_column']\n  File \"/usr/local/lib/python3.9/site-packages/pandas/core/frame.py\", line 3505, in __getitem__\n    indexer = self.columns.get_loc(key)\n  File \"/usr/local/lib/python3.9/site-packages/pandas/core/indexes/base.py\", line 3623, in get_loc\n    raise KeyError(key) from err\nKeyError: 'target_column'",
                test_function="test_feature_engineering",
                test_class="TestFeatures",
                failure_timestamp=base_time - timedelta(minutes=2),
                test_context={"test_type": "unit", "category": "feature_engineering", "priority": "medium"},
                pytest_node_id="tests/test_features.py::TestFeatures::test_feature_engineering"
            )
        ]
        
        return FailureScenario(
            name="real_data_science_pipeline_scenario",
            description="Real data science pipeline test failures",
            failures=failures,
            expected_groupings=3,  # data_pipeline, machine_learning, feature_engineering groups
            expected_priority_order=["test_data_loading", "test_model_training", "test_feature_engineering"],
            expected_categories=["CONFIGURATION_ERROR", "UNKNOWN"],
            context={
                "scenario_type": "real",
                "domain": "data_science",
                "root_cause": "missing_data_and_preprocessing_issues",
                "fix_suggestion": "Provide test data files and handle missing values"
            }
        )
        
    @pytest.fixture
    def complex_mixed_failure_scenario(self):
        """Complex scenario: Mixed failure types across different systems"""
        base_time = datetime.now()
        
        failures = [
            # Infrastructure failure
            TestFailureData(
                test_name="test_docker_container_startup",
                test_file="tests/test_infrastructure.py",
                failure_type="infrastructure",
                error_message="docker.errors.APIError: 500 Server Error: Internal Server Error (\"driver failed programming external connectivity on endpoint test_db (abc123): Error starting userland proxy: listen tcp 0.0.0.0:5432: bind: address already in use\")",
                stack_trace="Docker container startup failure",
                test_function="test_docker_container_startup",
                test_class="TestInfrastructure",
                failure_timestamp=base_time,
                test_context={"test_type": "infrastructure", "service": "docker", "priority": "critical"},
                pytest_node_id="tests/test_infrastructure.py::TestInfrastructure::test_docker_container_startup"
            ),
            # Dependency failure
            TestFailureData(
                test_name="test_redis_dependency",
                test_file="tests/test_cache.py",
                failure_type="error",
                error_message="ImportError: No module named 'redis'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_cache.py\", line 3, in <module>\n    import redis\nImportError: No module named 'redis'",
                test_function="test_redis_dependency",
                test_class="TestCache",
                failure_timestamp=base_time - timedelta(minutes=1),
                test_context={"test_type": "unit", "category": "cache", "priority": "high"},
                pytest_node_id="tests/test_cache.py::TestCache::test_redis_dependency"
            ),
            # Configuration failure
            TestFailureData(
                test_name="test_environment_config",
                test_file="tests/test_config.py",
                failure_type="error",
                error_message="KeyError: 'REDIS_URL'",
                stack_trace="Traceback (most recent call last):\n  File \"tests/test_config.py\", line 15, in test_environment_config\n    redis_url = os.environ['REDIS_URL']\nKeyError: 'REDIS_URL'",
                test_function="test_environment_config",
                test_class="TestConfig",
                failure_timestamp=base_time - timedelta(minutes=2),
                test_context={"test_type": "integration", "category": "configuration", "priority": "high"},
                pytest_node_id="tests/test_config.py::TestConfig::test_environment_config"
            ),
            # Network failure
            TestFailureData(
                test_name="test_external_api_call",
                test_file="tests/test_external.py",
                failure_type="error",
                error_message="requests.exceptions.ConnectionError: HTTPSConnectionPool(host='external-api.com', port=443): Max retries exceeded with url: /api/v1/data (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f8b8c0d5f40>: Failed to establish a new connection: [Errno 111] Connection refused'))",
                stack_trace="Network connection failure to external API",
                test_function="test_external_api_call",
                test_class="TestExternal",
                failure_timestamp=base_time - timedelta(minutes=3),
                test_context={"test_type": "integration", "category": "external_api", "priority": "medium"},
                pytest_node_id="tests/test_external.py::TestExternal::test_external_api_call"
            ),
            # Business logic failure
            TestFailureData(
                test_name="test_business_logic",
                test_file="tests/test_business.py",
                failure_type="assertion",
                error_message="AssertionError: Expected total_amount to be 150.0, got 120.0",
                stack_trace="def test_business_logic():\n    result = calculate_total_with_discount(100, 0.2)\n>   assert result == 150.0, \"Expected total_amount to be 150.0, got 120.0\"\nE   AssertionError: Expected total_amount to be 150.0, got 120.0",
                test_function="test_business_logic",
                test_class="TestBusiness",
                failure_timestamp=base_time - timedelta(minutes=4),
                test_context={"test_type": "unit", "category": "business_logic", "priority": "low"},
                pytest_node_id="tests/test_business.py::TestBusiness::test_business_logic"
            )
        ]
        
        return FailureScenario(
            name="complex_mixed_failure_scenario",
            description="Complex mixed failure types across different systems",
            failures=failures,
            expected_groupings=5,  # Each failure in different group
            expected_priority_order=["test_docker_container_startup", "test_redis_dependency", "test_environment_config", "test_external_api_call", "test_business_logic"],
            expected_categories=["RESOURCE_EXHAUSTION", "DEPENDENCY_ISSUE", "CONFIGURATION_ERROR", "NETWORK_CONNECTIVITY", "UNKNOWN"],
            context={
                "scenario_type": "complex",
                "complexity": "high",
                "root_cause": "multiple_system_failures",
                "fix_suggestion": "Address infrastructure, dependencies, and configuration issues systematically"
            }
        )
        
    @pytest.fixture
    def all_failure_scenarios(self, synthetic_import_error_scenario, synthetic_configuration_error_scenario,
                             synthetic_network_connectivity_scenario, real_django_test_failure_scenario,
                             real_fastapi_test_failure_scenario, real_data_science_pipeline_scenario,
                             complex_mixed_failure_scenario):
        """All failure scenarios combined for comprehensive testing"""
        return [
            synthetic_import_error_scenario,
            synthetic_configuration_error_scenario,
            synthetic_network_connectivity_scenario,
            real_django_test_failure_scenario,
            real_fastapi_test_failure_scenario,
            real_data_science_pipeline_scenario,
            complex_mixed_failure_scenario
        ]
        
    @pytest.fixture
    def performance_stress_scenario(self):
        """Large scenario for performance and stress testing"""
        base_time = datetime.now()
        failures = []
        
        # Generate 200 diverse failures for stress testing
        failure_types = ["error", "assertion", "timeout"]
        error_templates = [
            "ImportError: No module named 'module_{}'",
            "FileNotFoundError: [Errno 2] No such file or directory: 'file_{}.txt'",
            "AssertionError: Expected {}, got {}",
            "ConnectionError: Failed to connect to service_{}",
            "PermissionError: [Errno 13] Permission denied: '/path/to/resource_{}'",
            "ValueError: Invalid value for parameter_{}: {}",
            "TypeError: unsupported operand type(s) for +: '{}' and '{}'",
            "KeyError: 'missing_key_{}'",
            "AttributeError: '{}' object has no attribute 'method_{}'"
        ]
        
        for i in range(200):
            failure_type = failure_types[i % 3]
            error_template = error_templates[i % len(error_templates)]
            
            if "Expected {}, got {}" in error_template:
                error_message = error_template.format(i + 10, i)
            elif "{}" in error_template:
                error_message = error_template.format(i)
            else:
                error_message = error_template
                
            failures.append(TestFailureData(
                test_name=f"test_stress_{i}",
                test_file=f"tests/test_module_{i % 20}.py",  # Group into 20 files
                failure_type=failure_type,
                error_message=error_message,
                stack_trace=f"Stack trace for stress test {i}\n" * (i % 3 + 1),
                test_function=f"test_stress_{i}",
                test_class=f"TestStress{i % 10}" if i % 2 == 0 else None,
                failure_timestamp=base_time - timedelta(minutes=i % 60),
                test_context={
                    "test_type": "stress",
                    "batch": i // 50,
                    "complexity": i % 5,
                    "priority": ["low", "medium", "high", "critical"][i % 4]
                },
                pytest_node_id=f"tests/test_module_{i % 20}.py::TestStress{i % 10}::test_stress_{i}"
            ))
            
        return FailureScenario(
            name="performance_stress_scenario",
            description="Large-scale scenario for performance and stress testing",
            failures=failures,
            expected_groupings=20,  # Based on file grouping
            expected_priority_order=[],  # Too many to specify
            expected_categories=["DEPENDENCY_ISSUE", "CONFIGURATION_ERROR", "UNKNOWN", "NETWORK_CONNECTIVITY", "PERMISSION_ISSUE"],
            context={
                "scenario_type": "stress",
                "size": "large",
                "purpose": "performance_testing"
            }
        )


# Utility functions for working with scenarios

def create_temporary_test_files(scenario: FailureScenario, temp_dir: str) -> List[str]:
    """Create temporary test files based on scenario failures"""
    created_files = []
    
    for failure in scenario.failures:
        if failure.test_file and failure.test_file != "Makefile":
            file_path = Path(temp_dir) / failure.test_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a simple test file that would produce the failure
            test_content = f'''"""
Test file for {failure.test_name}
This file is created for RCA integration testing
"""

import pytest

class {failure.test_class or "TestGenerated"}:
    def {failure.test_function}(self):
        """Test that demonstrates the failure scenario"""
        # This test is designed to fail with: {failure.error_message}
        assert False, "Synthetic test failure for RCA testing"
'''
            
            file_path.write_text(test_content)
            created_files.append(str(file_path))
            
    return created_files


def save_scenario_to_json(scenario: FailureScenario, file_path: str):
    """Save a failure scenario to JSON file for persistence"""
    scenario_data = {
        "name": scenario.name,
        "description": scenario.description,
        "expected_groupings": scenario.expected_groupings,
        "expected_priority_order": scenario.expected_priority_order,
        "expected_categories": scenario.expected_categories,
        "context": scenario.context,
        "failures": [
            {
                "test_name": f.test_name,
                "test_file": f.test_file,
                "failure_type": f.failure_type,
                "error_message": f.error_message,
                "stack_trace": f.stack_trace,
                "test_function": f.test_function,
                "test_class": f.test_class,
                "failure_timestamp": f.failure_timestamp.isoformat(),
                "test_context": f.test_context,
                "pytest_node_id": f.pytest_node_id
            }
            for f in scenario.failures
        ]
    }
    
    with open(file_path, 'w') as f:
        json.dump(scenario_data, f, indent=2)


def load_scenario_from_json(file_path: str) -> FailureScenario:
    """Load a failure scenario from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    failures = [
        TestFailureData(
            test_name=f["test_name"],
            test_file=f["test_file"],
            failure_type=f["failure_type"],
            error_message=f["error_message"],
            stack_trace=f["stack_trace"],
            test_function=f["test_function"],
            test_class=f["test_class"],
            failure_timestamp=datetime.fromisoformat(f["failure_timestamp"]),
            test_context=f["test_context"],
            pytest_node_id=f["pytest_node_id"]
        )
        for f in data["failures"]
    ]
    
    return FailureScenario(
        name=data["name"],
        description=data["description"],
        failures=failures,
        expected_groupings=data["expected_groupings"],
        expected_priority_order=data["expected_priority_order"],
        expected_categories=data["expected_categories"],
        context=data["context"]
    )