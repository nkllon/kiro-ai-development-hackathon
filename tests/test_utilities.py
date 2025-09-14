"""
Comprehensive Test Utilities

This module provides utilities, fixtures, and helpers for comprehensive testing
across the entire Beast Mode framework.
"""

import pytest
import asyncio
import tempfile
import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.core.exceptions import BeastModeError
from beast_mode.core.reflective_module import ReflectiveModule, HealthStatus


@dataclass
class TestConfig:
    """Configuration for test execution."""
    timeout: int = 30
    retry_count: int = 3
    log_level: str = "INFO"
    cleanup_after: bool = True
    parallel_execution: bool = True
    coverage_threshold: float = 90.0


@dataclass
class TestResult:
    """Test execution result."""
    test_name: str
    success: bool
    duration: float
    error: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    coverage: Optional[float] = None


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_pdca_config() -> Dict[str, Any]:
        """Create a standard PDCA configuration for testing."""
        return {
            "objective": "test_implementation",
            "resources": {
                "developers": 2,
                "timeline": "1_week",
                "budget": 10000
            },
            "success_criteria": [
                "tests_pass",
                "coverage_90_percent",
                "performance_benchmarks_met"
            ],
            "validation_criteria": [
                "unit_tests_pass",
                "integration_tests_pass",
                "code_review_complete"
            ],
            "improvement_actions": [
                "optimize_performance",
                "enhance_documentation",
                "add_monitoring"
            ]
        }
    
    @staticmethod
    def create_model_metadata() -> Dict[str, Any]:
        """Create model metadata for testing."""
        return {
            "accuracy": 0.92,
            "training_data_size": 10000,
            "features": ["complexity", "size", "dependencies"],
            "model_type": "classification",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "performance_metrics": {
                "precision": 0.89,
                "recall": 0.91,
                "f1_score": 0.90
            }
        }
    
    @staticmethod
    def create_health_check_context() -> Dict[str, Any]:
        """Create health check context for testing."""
        return {
            "component_id": "test_component",
            "check_type": "comprehensive",
            "timeout": 5,
            "retry_count": 3,
            "dependencies": ["database", "cache", "api"],
            "expected_response_time": 100,  # ms
            "critical_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "disk_usage": 90
            }
        }
    
    @staticmethod
    def create_cli_command_args() -> Dict[str, Any]:
        """Create CLI command arguments for testing."""
        return {
            "command": "test",
            "subcommand": "run",
            "options": {
                "verbose": True,
                "json_output": False,
                "timeout": 30,
                "parallel": True
            },
            "arguments": ["test_file.py", "--coverage"]
        }


class MockSystemComponents:
    """Mock system components for testing."""
    
    def __init__(self):
        self.components = {}
        self.health_status = {}
        self.metrics = {}
    
    def register_component(self, component_id: str, 
                          health_func: Callable = None,
                          metrics_func: Callable = None) -> Dict[str, Any]:
        """Register a mock component."""
        component = {
            "component_id": component_id,
            "health_func": health_func or (lambda: True),
            "metrics_func": metrics_func or (lambda: {}),
            "status": "healthy",
            "last_check": datetime.now(),
            "check_count": 0
        }
        self.components[component_id] = component
        return component
    
    def check_health(self, component_id: str = None) -> Dict[str, Any]:
        """Check health of components."""
        if component_id:
            return self._check_single_component(component_id)
        else:
            return self._check_all_components()
    
    def _check_single_component(self, component_id: str) -> Dict[str, Any]:
        """Check health of a single component."""
        if component_id not in self.components:
            return {"status": "not_found", "error": f"Component {component_id} not found"}
        
        component = self.components[component_id]
        try:
            is_healthy = component["health_func"]()
            component["status"] = "healthy" if is_healthy else "unhealthy"
            component["last_check"] = datetime.now()
            component["check_count"] += 1
            
            return {
                "component_id": component_id,
                "status": component["status"],
                "last_check": component["last_check"],
                "check_count": component["check_count"]
            }
        except Exception as e:
            component["status"] = "error"
            component["last_error"] = str(e)
            return {
                "component_id": component_id,
                "status": "error",
                "error": str(e)
            }
    
    def _check_all_components(self) -> Dict[str, Any]:
        """Check health of all components."""
        results = {}
        healthy_count = 0
        total_count = len(self.components)
        
        for component_id in self.components:
            result = self._check_single_component(component_id)
            results[component_id] = result
            if result["status"] == "healthy":
                healthy_count += 1
        
        return {
            "overall_status": "healthy" if healthy_count == total_count else "degraded",
            "healthy_components": healthy_count,
            "total_components": total_count,
            "health_percentage": (healthy_count / total_count * 100) if total_count > 0 else 100,
            "components": results,
            "check_timestamp": datetime.now()
        }


class TestEnvironment:
    """Test environment management."""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.temp_dir = None
        self.original_cwd = None
        self.mock_components = MockSystemComponents()
        self.test_results = []
    
    def setup(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="beast_mode_test_")
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Register mock components
        self.mock_components.register_component("test_database", lambda: True)
        self.mock_components.register_component("test_api", lambda: True)
        self.mock_components.register_component("test_cache", lambda: True)
    
    def teardown(self):
        """Tear down test environment."""
        if self.config.cleanup_after and self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        if self.original_cwd:
            os.chdir(self.original_cwd)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file in the temp directory."""
        file_path = Path(self.temp_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    def create_test_config(self, config_data: Dict[str, Any]) -> Path:
        """Create a test configuration file."""
        config_path = Path(self.temp_dir) / "test_config.json"
        config_path.write_text(json.dumps(config_data, indent=2))
        return config_path
    
    def create_test_yaml(self, yaml_data: Dict[str, Any]) -> Path:
        """Create a test YAML file."""
        yaml_path = Path(self.temp_dir) / "test_config.yaml"
        yaml_path.write_text(yaml.dump(yaml_data, default_flow_style=False))
        return yaml_path


class PerformanceMonitor:
    """Monitor test performance and metrics."""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = datetime.now()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation not in self.start_times:
            return 0.0
        
        duration = (datetime.now() - self.start_times[operation]).total_seconds()
        self.metrics[operation] = duration
        return duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics."""
        return self.metrics.copy()
    
    def get_operation_metrics(self, operation: str) -> Optional[float]:
        """Get metrics for a specific operation."""
        return self.metrics.get(operation)


class TestCoverageTracker:
    """Track test coverage and generate reports."""
    
    def __init__(self):
        self.coverage_data = {}
        self.test_files = set()
        self.source_files = set()
    
    def add_test_file(self, test_file: str):
        """Add a test file to tracking."""
        self.test_files.add(test_file)
    
    def add_source_file(self, source_file: str):
        """Add a source file to tracking."""
        self.source_files.add(source_file)
    
    def record_coverage(self, module: str, coverage_percentage: float):
        """Record coverage for a module."""
        self.coverage_data[module] = coverage_percentage
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Generate coverage report."""
        total_modules = len(self.coverage_data)
        if total_modules == 0:
            return {"overall_coverage": 0.0, "modules": {}}
        
        total_coverage = sum(self.coverage_data.values())
        overall_coverage = total_coverage / total_modules
        
        return {
            "overall_coverage": overall_coverage,
            "total_modules": total_modules,
            "modules": self.coverage_data.copy(),
            "test_files": len(self.test_files),
            "source_files": len(self.source_files)
        }


# Pytest fixtures
@pytest.fixture
def test_config():
    """Provide test configuration."""
    return TestConfig()


@pytest.fixture
def test_environment(test_config):
    """Provide test environment."""
    env = TestEnvironment(test_config)
    env.setup()
    yield env
    env.teardown()


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory()


@pytest.fixture
def mock_components():
    """Provide mock system components."""
    return MockSystemComponents()


@pytest.fixture
def performance_monitor():
    """Provide performance monitor."""
    return PerformanceMonitor()


@pytest.fixture
def coverage_tracker():
    """Provide coverage tracker."""
    return TestCoverageTracker()


@pytest.fixture
def sample_pdca_config(test_data_factory):
    """Provide sample PDCA configuration."""
    return test_data_factory.create_pdca_config()


@pytest.fixture
def sample_model_metadata(test_data_factory):
    """Provide sample model metadata."""
    return test_data_factory.create_model_metadata()


@pytest.fixture
def sample_health_context(test_data_factory):
    """Provide sample health check context."""
    return test_data_factory.create_health_check_context()


@pytest.fixture
def sample_cli_args(test_data_factory):
    """Provide sample CLI arguments."""
    return test_data_factory.create_cli_command_args()


# Async test utilities
@pytest.fixture
def event_loop():
    """Provide event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class AsyncTestHelper:
    """Helper for async testing."""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: int = 30):
        """Run coroutine with timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise pytest.TimeoutError(f"Test timed out after {timeout} seconds")
    
    @staticmethod
    async def mock_async_function(result: Any = None, delay: float = 0.1):
        """Mock async function for testing."""
        await asyncio.sleep(delay)
        return result or {"status": "success"}


# Test decorators
def integration_test(func):
    """Mark test as integration test."""
    return pytest.mark.integration(func)


def performance_test(func):
    """Mark test as performance test."""
    return pytest.mark.performance(func)


def unit_test(func):
    """Mark test as unit test."""
    return pytest.mark.unit(func)


def slow_test(func):
    """Mark test as slow running."""
    return pytest.mark.slow(func)


def requires_dependency(dependency: str):
    """Mark test as requiring specific dependency."""
    def decorator(func):
        try:
            __import__(dependency)
            return func
        except ImportError:
            return pytest.mark.skip(reason=f"Requires {dependency}")(func)
    return decorator


# Test assertion helpers
class TestAssertions:
    """Custom assertion helpers."""
    
    @staticmethod
    def assert_health_status(health_result: Dict[str, Any], expected_status: str = "healthy"):
        """Assert health status."""
        assert health_result["overall_status"] == expected_status, \
            f"Expected {expected_status}, got {health_result['overall_status']}"
    
    @staticmethod
    def assert_coverage_threshold(coverage: float, threshold: float = 90.0):
        """Assert coverage meets threshold."""
        assert coverage >= threshold, \
            f"Coverage {coverage}% below threshold {threshold}%"
    
    @staticmethod
    def assert_performance_within_bounds(duration: float, max_duration: float):
        """Assert performance is within bounds."""
        assert duration <= max_duration, \
            f"Duration {duration}s exceeds maximum {max_duration}s"
    
    @staticmethod
    def assert_pdca_cycle_complete(cycle_result: Dict[str, Any]):
        """Assert PDCA cycle completed successfully."""
        assert cycle_result["status"] == "completed", \
            f"PDCA cycle not completed: {cycle_result}"
        assert "cycle_id" in cycle_result, "Missing cycle_id"
        assert "success_rate" in cycle_result, "Missing success_rate"
        assert cycle_result["success_rate"] > 0.8, "Success rate too low"


# Test data generators
class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_large_dataset(size: int = 1000) -> List[Dict[str, Any]]:
        """Generate large dataset for performance testing."""
        return [
            {
                "id": i,
                "name": f"item_{i}",
                "value": i * 1.5,
                "category": f"category_{i % 10}",
                "timestamp": datetime.now().isoformat()
            }
            for i in range(size)
        ]
    
    @staticmethod
    def generate_error_scenarios() -> List[Dict[str, Any]]:
        """Generate error scenarios for testing."""
        return [
            {"error_type": "timeout", "message": "Operation timed out"},
            {"error_type": "connection", "message": "Connection failed"},
            {"error_type": "validation", "message": "Invalid input data"},
            {"error_type": "permission", "message": "Access denied"},
            {"error_type": "resource", "message": "Insufficient resources"}
        ]
    
    @staticmethod
    def generate_config_variations() -> List[Dict[str, Any]]:
        """Generate configuration variations for testing."""
        base_config = {
            "timeout": 30,
            "retry_count": 3,
            "parallel": True,
            "log_level": "INFO"
        }
        
        variations = []
        for timeout in [10, 30, 60, 120]:
            for retry_count in [1, 3, 5]:
                for parallel in [True, False]:
                    config = base_config.copy()
                    config.update({
                        "timeout": timeout,
                        "retry_count": retry_count,
                        "parallel": parallel
                    })
                    variations.append(config)
        
        return variations


if __name__ == "__main__":
    # Run basic tests for utilities
    pytest.main([__file__, "-v"])

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

