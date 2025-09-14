# Comprehensive Test Suite

This directory contains a comprehensive test suite for the Beast Mode Framework, providing thorough testing coverage across all components, modules, and functionality.

## Test Structure

```
tests/
├── README.md                           # This file
├── conftest.py                         # Pytest configuration and shared fixtures
├── test_utilities.py                   # Test utilities, helpers, and fixtures
├── run_comprehensive_tests.py          # Comprehensive test runner
├── unit/                               # Unit tests
│   ├── test_beast_mode_core_comprehensive.py
│   ├── test_cli_comprehensive.py
│   └── ...
├── integration/                        # Integration tests
│   ├── test_system_integration_comprehensive.py
│   └── ...
├── performance/                        # Performance tests
│   ├── test_performance_comprehensive.py
│   └── ...
├── fixtures/                           # Test fixtures and data
├── data/                              # Test data files
└── reports/                           # Test reports and coverage
```

## Test Categories

### Unit Tests
- **Location**: `tests/unit/`
- **Purpose**: Test individual components in isolation
- **Coverage**: Core modules, utilities, models, and functions
- **Execution**: Fast, isolated, no external dependencies

### Integration Tests
- **Location**: `tests/integration/`
- **Purpose**: Test interactions between components
- **Coverage**: Cross-module communication, workflows, and system integration
- **Execution**: Moderate speed, requires component interactions

### Performance Tests
- **Location**: `tests/performance/`
- **Purpose**: Test performance, scalability, and load handling
- **Coverage**: Load testing, stress testing, memory usage, and response times
- **Execution**: Slower, resource-intensive

### CLI Tests
- **Location**: `tests/unit/test_cli_comprehensive.py`
- **Purpose**: Test command-line interfaces and user interactions
- **Coverage**: All CLI commands, argument parsing, and output formats
- **Execution**: Fast to moderate

## Running Tests

### Quick Start

```bash
# Run all tests
python tests/run_comprehensive_tests.py

# Run specific test category
python tests/run_comprehensive_tests.py --category unit
python tests/run_comprehensive_tests.py --category integration
python tests/run_comprehensive_tests.py --category performance

# Run with custom configuration
python tests/run_comprehensive_tests.py --timeout 60 --coverage-threshold 95
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run performance tests only
pytest tests/performance/

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_beast_mode_core_comprehensive.py

# Run specific test class
pytest tests/unit/test_beast_mode_core_comprehensive.py::TestBeastModeExceptions

# Run specific test method
pytest tests/unit/test_beast_mode_core_comprehensive.py::TestBeastModeExceptions::test_beast_mode_error_creation
```

### Test Configuration

The test suite uses `pytest.ini` for configuration. Key settings:

- **Timeout**: 30 seconds per test (configurable)
- **Parallel execution**: Enabled by default
- **Coverage threshold**: 90% (configurable)
- **Logging**: INFO level with detailed output
- **Markers**: Categorized tests for selective execution

## Test Utilities

### TestDataFactory
Provides factory methods for creating test data:
- `create_pdca_config()`: Standard PDCA configuration
- `create_model_metadata()`: Model metadata for testing
- `create_health_check_context()`: Health check context
- `create_cli_command_args()`: CLI command arguments

### TestEnvironment
Manages test environment setup and teardown:
- Temporary directory creation
- Configuration file management
- Environment variable setup
- Cleanup management

### PerformanceMonitor
Tracks performance metrics:
- Operation timing
- Memory usage monitoring
- Performance analysis
- Benchmarking

### TestAssertions
Custom assertion helpers:
- `assert_health_status()`: Health status assertions
- `assert_coverage_threshold()`: Coverage threshold assertions
- `assert_performance_within_bounds()`: Performance assertions
- `assert_pdca_cycle_complete()`: PDCA cycle assertions

## Test Markers

Tests are categorized using pytest markers:

```python
@unit_test
def test_basic_functionality():
    """Test basic functionality."""

@integration_test
def test_module_integration():
    """Test module integration."""

@performance_test
def test_performance():
    """Test performance."""

@slow_test
def test_long_running():
    """Test long-running operation."""

@requires_dependency("redis")
def test_redis_integration():
    """Test Redis integration."""
```

## Running Specific Test Types

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only performance tests
pytest -m performance

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"

# Run tests requiring specific dependencies
pytest -m "requires_dependency"
```

## Coverage Reporting

The test suite provides comprehensive coverage reporting:

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Generate JSON coverage report
pytest --cov=src --cov-report=json

# Generate XML coverage report
pytest --cov=src --cov-report=xml

# Check coverage threshold
pytest --cov=src --cov-fail-under=90
```

Coverage reports are generated in:
- `htmlcov/`: HTML coverage report
- `coverage.json`: JSON coverage data
- `coverage.xml`: XML coverage data

## Performance Testing

Performance tests include:

### Load Testing
- Large-scale data processing
- Concurrent operations
- Memory usage under load
- Response time benchmarks

### Stress Testing
- System limits testing
- Error condition handling
- Resource exhaustion scenarios
- Recovery testing

### Benchmarking
- Performance regression detection
- Comparative analysis
- Optimization validation
- Scalability assessment

## Test Data Management

### Fixtures
- **Location**: `tests/fixtures/`
- **Purpose**: Reusable test data and setup
- **Types**: JSON, YAML, CSV, and binary data

### Test Data
- **Location**: `tests/data/`
- **Purpose**: Static test data files
- **Types**: Configuration files, sample data, and test inputs

## Continuous Integration

The test suite is designed for CI/CD integration:

### GitHub Actions
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python tests/run_comprehensive_tests.py
```

### Local Development
```bash
# Pre-commit hook
pre-commit install

# Run tests before commit
git add .
git commit -m "Add feature"
# Tests run automatically
```

## Debugging Tests

### Verbose Output
```bash
# Verbose test output
pytest -v

# Extra verbose output
pytest -vv

# Show local variables on failure
pytest -l
```

### Debug Mode
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

### Test Logging
```bash
# Enable test logging
pytest --log-cli-level=DEBUG

# Log to file
pytest --log-file=test.log
```

## Best Practices

### Writing Tests
1. **Test one thing at a time**: Each test should verify one specific behavior
2. **Use descriptive names**: Test names should clearly describe what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
4. **Use fixtures**: Reuse common setup code with pytest fixtures
5. **Mock external dependencies**: Isolate units under test

### Test Organization
1. **Group related tests**: Use test classes to group related test methods
2. **Use markers**: Categorize tests with appropriate markers
3. **Keep tests independent**: Tests should not depend on each other
4. **Clean up after tests**: Use teardown methods to clean up resources

### Performance Considerations
1. **Use appropriate test types**: Choose unit, integration, or performance tests as needed
2. **Mock expensive operations**: Use mocks for slow external operations
3. **Run tests in parallel**: Use pytest-xdist for parallel execution
4. **Monitor resource usage**: Track memory and CPU usage during tests

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### Permission Errors
```bash
# Ensure test files are executable
chmod +x tests/run_comprehensive_tests.py
```

#### Memory Issues
```bash
# Run tests with memory monitoring
python -m pytest --maxfail=1 --tb=short
```

#### Timeout Issues
```bash
# Increase timeout for slow tests
pytest --timeout=60
```

### Getting Help

1. **Check test output**: Look for error messages and stack traces
2. **Review configuration**: Check `pytest.ini` and test configuration
3. **Check dependencies**: Ensure all required packages are installed
4. **Review logs**: Check test logs for detailed information

## Contributing

When adding new tests:

1. **Follow naming conventions**: Use `test_` prefix for test files and methods
2. **Add appropriate markers**: Categorize tests with markers
3. **Update documentation**: Update this README if adding new test categories
4. **Ensure coverage**: Maintain or improve test coverage
5. **Run full suite**: Ensure all tests pass before submitting

## Test Metrics

The test suite tracks various metrics:

- **Test Count**: Total number of tests
- **Coverage**: Code coverage percentage
- **Performance**: Test execution time and performance benchmarks
- **Reliability**: Test success rate and stability
- **Maintainability**: Test code quality and maintainability

## Future Enhancements

Planned improvements to the test suite:

1. **Visual testing**: Add visual regression testing
2. **API testing**: Expand API testing coverage
3. **Security testing**: Add security-focused tests
4. **Accessibility testing**: Add accessibility compliance tests
5. **Cross-platform testing**: Test on multiple operating systems
6. **Database testing**: Add database integration tests
7. **Cloud testing**: Add cloud platform integration tests

## Support

For questions or issues with the test suite:

1. **Check documentation**: Review this README and inline comments
2. **Search issues**: Look for similar issues in the project repository
3. **Create issue**: Submit a new issue with detailed information
4. **Contact maintainers**: Reach out to the development team

---

*This test suite is designed to ensure the reliability, performance, and maintainability of the Beast Mode Framework. Regular testing is essential for maintaining code quality and preventing regressions.*
