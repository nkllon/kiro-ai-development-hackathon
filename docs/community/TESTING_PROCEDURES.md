# Testing Procedures

This document outlines the comprehensive testing procedures for the Beast Mode AI Development Framework.

## Testing Philosophy

Our testing approach follows these principles:

- **Security First**: All tests validate security requirements
- **Comprehensive Coverage**: Unit, integration, and end-to-end testing
- **Environment Validation**: Tests work across different environments
- **Performance Awareness**: Tests include performance validation
- **Documentation Testing**: All examples and documentation are tested

## Test Categories

### 1. Unit Tests

**Purpose**: Test individual functions and classes in isolation

**Location**: `tests/unit/`

**Requirements**:
- Test all public functions and methods
- Mock external dependencies
- Validate error handling
- Test edge cases and boundary conditions

**Example**:
```python
import pytest
from unittest.mock import patch, MagicMock
from src.memory_palace import MemoryPalace

class TestMemoryPalace:
    def test_store_knowledge_success(self):
        palace = MemoryPalace()
        result = palace.store("test_key", {"data": "value"})
        assert result is True
    
    def test_store_knowledge_with_invalid_key(self):
        palace = MemoryPalace()
        with pytest.raises(ValueError):
            palace.store("", {"data": "value"})
```

### 2. Integration Tests

**Purpose**: Test component interactions and data flow

**Location**: `tests/integration/`

**Requirements**:
- Test component integration points
- Validate data flow between components
- Test configuration and environment setup
- Validate Redis connectivity and operations

### 3. Security Tests

**Purpose**: Validate security requirements and credential management

**Location**: `tests/security/`

**Requirements**:
- Scan for hardcoded credentials
- Validate environment variable usage
- Test authentication and authorization
- Validate input sanitization

### 4. Performance Tests

**Purpose**: Validate performance characteristics and resource usage

**Location**: `tests/performance/`

**Requirements**:
- Test execution time limits
- Validate memory usage
- Test concurrent operations
- Validate scalability characteristics

### 5. End-to-End Tests

**Purpose**: Test complete user workflows and scenarios

**Location**: `tests/e2e/`

**Requirements**:
- Test complete user journeys
- Validate examples work correctly
- Test installation and setup procedures
- Validate documentation accuracy## Runni
ng Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest tests/ --run

# Run specific test category
python -m pytest tests/unit/ --run
python -m pytest tests/integration/ --run
python -m pytest tests/security/ --run

# Run specific test file
python -m pytest tests/unit/test_memory_palace.py --run

# Run specific test function
python -m pytest tests/unit/test_memory_palace.py::test_store_knowledge --run
```

### Test Coverage

```bash
# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html --run

# View coverage report
open htmlcov/index.html

# Coverage requirements
# - Overall coverage: > 90%
# - Critical modules: > 95%
# - Security modules: 100%
```

### Parallel Test Execution

```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
python -m pytest tests/ -n auto --run

# Run with specific number of workers
python -m pytest tests/ -n 4 --run
```

## Test Environment Setup

### Local Testing Environment

```bash
# Set up test environment
export ENVIRONMENT=test
export REDIS_PASSWORD=test_password
export LOG_LEVEL=DEBUG

# Start test Redis instance
docker run -d --name test-redis -p 6380:6379 redis:7-alpine redis-server --requirepass test_password

# Run tests against test environment
REDIS_PORT=6380 python -m pytest tests/ --run
```

### CI/CD Testing Environment

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    services:
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: python -m pytest tests/ --cov=src --run
      env:
        REDIS_PASSWORD: test_password
        ENVIRONMENT: test
```

## Security Testing

### Credential Scanning

```bash
# Scan for hardcoded credentials
python -m pytest tests/security/test_credential_scanning.py --run

# Manual credential scanning
grep -r "password.*=" --include="*.py" src/
grep -r "api_key.*=" --include="*.py" src/
grep -r "secret.*=" --include="*.py" src/

# Use detect-secrets tool
pip install detect-secrets
detect-secrets scan --all-files
```

### Security Test Example

```python
# tests/security/test_credential_scanning.py
import os
import re
from pathlib import Path

def test_no_hardcoded_passwords():
    """Ensure no hardcoded passwords in source code."""
    src_path = Path("src")
    password_pattern = re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE)
    
    for py_file in src_path.rglob("*.py"):
        content = py_file.read_text()
        matches = password_pattern.findall(content)
        assert not matches, f"Hardcoded password found in {py_file}: {matches}"

def test_environment_variable_usage():
    """Ensure environment variables are used for sensitive data."""
    # Test that required environment variables are checked
    from src.config import Config
    
    # This should raise an error if REDIS_PASSWORD is not set
    with pytest.raises(ValueError, match="REDIS_PASSWORD"):
        Config(redis_password="")
```

## Performance Testing

### Performance Test Framework

```python
# tests/performance/test_memory_palace_performance.py
import time
import pytest
from src.memory_palace import MemoryPalace

class TestMemoryPalacePerformance:
    def test_store_performance(self):
        """Test knowledge storage performance."""
        palace = MemoryPalace()
        
        start_time = time.time()
        for i in range(1000):
            palace.store(f"key_{i}", {"data": f"value_{i}"})
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Storage took {execution_time}s, expected < 5s"
    
    def test_retrieval_performance(self):
        """Test knowledge retrieval performance."""
        palace = MemoryPalace()
        
        # Setup test data
        for i in range(100):
            palace.store(f"key_{i}", {"data": f"value_{i}"})
        
        start_time = time.time()
        for i in range(100):
            result = palace.retrieve(f"key_{i}")
            assert result is not None
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 1.0, f"Retrieval took {execution_time}s, expected < 1s"
```

## Integration Testing

### Redis Integration Tests

```python
# tests/integration/test_redis_integration.py
import pytest
import redis
from src.execution_tracking import RedisExecutionTracker

class TestRedisIntegration:
    @pytest.fixture
    def redis_client(self):
        """Create Redis client for testing."""
        client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
        yield client
        # Cleanup
        client.flushdb()
    
    def test_execution_tracking(self, redis_client):
        """Test execution tracking with Redis."""
        tracker = RedisExecutionTracker()
        
        # Start tracking
        task_id = tracker.start_task("test_task")
        assert task_id is not None
        
        # Update progress
        tracker.update_progress(task_id, 50)
        
        # Complete task
        tracker.complete_task(task_id, {"result": "success"})
        
        # Verify in Redis
        task_data = redis_client.hgetall(f"task:{task_id}")
        assert task_data["status"] == "completed"
        assert task_data["progress"] == "100"
```

## Documentation Testing

### Example Code Testing

```python
# tests/documentation/test_examples.py
import subprocess
import pytest
from pathlib import Path

class TestDocumentationExamples:
    def test_quick_start_example(self):
        """Test that quick start example runs successfully."""
        example_path = Path("examples/quick_start/basic_example.py")
        assert example_path.exists()
        
        result = subprocess.run(
            ["python", str(example_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0, f"Example failed: {result.stderr}"
        assert "success" in result.stdout.lower()
    
    def test_all_examples_syntax(self):
        """Test that all example files have valid Python syntax."""
        examples_path = Path("examples")
        
        for py_file in examples_path.rglob("*.py"):
            with open(py_file, 'r') as f:
                content = f.read()
            
            try:
                compile(content, str(py_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")
```

## Test Data Management

### Test Fixtures

```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_directory():
    """Create temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_knowledge_data():
    """Provide sample data for testing."""
    return {
        "user_preferences": {
            "theme": "dark",
            "language": "python",
            "notifications": True
        },
        "project_config": {
            "name": "test_project",
            "version": "1.0.0",
            "dependencies": ["redis", "pytest"]
        }
    }

@pytest.fixture(scope="session")
def test_redis_client():
    """Create Redis client for testing session."""
    import redis
    client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    yield client
    # Cleanup after all tests
    client.flushdb()
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/comprehensive-tests.yml
name: Comprehensive Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Security scan
      run: |
        pip install bandit detect-secrets
        bandit -r src/
        detect-secrets scan --all-files
  
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Run unit tests
      run: |
        pip install -r requirements.txt -r requirements-dev.txt
        python -m pytest tests/unit/ --cov=src --run
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    steps:
    - uses: actions/checkout@v3
    - name: Run integration tests
      run: |
        pip install -r requirements.txt -r requirements-dev.txt
        python -m pytest tests/integration/ --run
      env:
        REDIS_PASSWORD: ""
        REDIS_HOST: localhost
        REDIS_PORT: 6379
```

## Test Reporting

### Coverage Reports

```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=src --cov-report=html --run

# Generate XML coverage report for CI
python -m pytest tests/ --cov=src --cov-report=xml --run

# Generate console coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing --run
```

### Test Result Analysis

```python
# scripts/analyze_test_results.py
import json
import sys
from pathlib import Path

def analyze_test_results():
    """Analyze test results and generate summary."""
    results_file = Path("test-results.json")
    
    if not results_file.exists():
        print("No test results found")
        return
    
    with open(results_file) as f:
        results = json.load(f)
    
    total_tests = results.get("total", 0)
    passed_tests = results.get("passed", 0)
    failed_tests = results.get("failed", 0)
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Test Summary:")
    print(f"  Total: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if success_rate < 95:
        print("WARNING: Test success rate below 95%")
        sys.exit(1)

if __name__ == "__main__":
    analyze_test_results()
```

## Best Practices

### Test Writing Guidelines

1. **Clear Test Names**: Use descriptive test function names
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Independent Tests**: Each test should be independent
4. **Mock External Dependencies**: Use mocks for external services
5. **Test Edge Cases**: Include boundary conditions and error cases

### Test Maintenance

1. **Regular Updates**: Keep tests current with code changes
2. **Performance Monitoring**: Monitor test execution times
3. **Flaky Test Management**: Identify and fix unreliable tests
4. **Test Data Management**: Keep test data clean and relevant

### Quality Gates

- **Unit Test Coverage**: > 90%
- **Integration Test Coverage**: > 80%
- **Security Test Coverage**: 100%
- **Performance Test Pass Rate**: 100%
- **Documentation Test Pass Rate**: 100%

---

**Remember**: Testing is not just about finding bugs - it's about ensuring quality, security, and maintainability of the codebase.