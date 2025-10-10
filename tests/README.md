# Makefile Governance System Tests

This directory contains comprehensive unit and integration tests for the Makefile Syntax Repair and Governance System.

## Test Structure

```
tests/
├── unit/                           # Unit tests
│   └── makefile_governance/
│       ├── test_syntax_validator.py      # MakefileSyntaxValidator tests
│       ├── test_governance_engine.py     # MakefileGovernanceEngine tests
│       └── test_health_monitor.py        # MakefileHealthMonitor tests
├── integration/                    # Integration tests
│   └── makefile_governance/
│       └── test_integrated_system.py     # End-to-end system tests
├── conftest.py                     # Pytest configuration and fixtures
└── README.md                       # This file
```

## Test Categories

### Unit Tests

#### `test_syntax_validator.py`
Tests for the `MakefileSyntaxValidator` class:
- ✅ Module initialization and ReflectiveModule integration
- ✅ GNU Make syntax validation (missing separators, invalid recipes)
- ✅ Embedded Python code validation
- ✅ Automatic syntax repair functionality
- ✅ PHONY target detection and warnings
- ✅ Backup creation and rollback procedures
- ✅ Health monitoring and statistics tracking
- ✅ Beast Mode framework integration (tracing, metrics)

**Key Test Cases:**
- Valid makefile validation (should pass)
- Missing tab separator detection and repair
- Space-indented recipe detection and repair
- Invalid Python syntax detection
- Missing PHONY declaration warnings
- Backup file creation during repairs
- Statistics and health metrics tracking

#### `test_governance_engine.py`
Tests for the `MakefileGovernanceEngine` class:
- ✅ Governance rule initialization and management
- ✅ Naming convention validation (kebab-case enforcement)
- ✅ PHONY declaration requirement checking
- ✅ Recipe complexity limit enforcement
- ✅ Environment variable naming validation
- ✅ Target description requirement checking
- ✅ Quality and complexity score calculation
- ✅ Violation severity and graduated response system
- ✅ Health monitoring and compliance tracking

**Key Test Cases:**
- Compliant makefile validation (should pass)
- Naming convention violations (underscore, CamelCase, UPPERCASE)
- Missing PHONY declaration detection
- Complex recipe detection (>3 lines)
- Environment variable naming violations
- Missing target description detection
- Quality score calculation with various violation types
- Rule management (enable/disable, custom rules)

#### `test_health_monitor.py`
Tests for the `MakefileHealthMonitor` class:
- ✅ Health metrics collection and storage
- ✅ Validation, repair, and governance result tracking
- ✅ Alert creation and resolution system
- ✅ System health score calculation
- ✅ Performance monitoring and response time tracking
- ✅ Health recommendations generation
- ✅ Beast Mode observability integration
- ✅ Graceful degradation capabilities

**Key Test Cases:**
- Successful operation recording and metrics
- Failed operation tracking and error rates
- Alert creation for threshold violations
- Alert resolution and cleanup
- Health score calculation with various metrics
- Performance monitoring and response time tracking
- Recommendation generation based on health status

### Integration Tests

#### `test_integrated_system.py`
End-to-end integration tests for the complete system:
- ✅ Complete makefile processing workflow
- ✅ Cross-component communication and data flow
- ✅ Error handling and recovery across components
- ✅ Performance monitoring integration
- ✅ Beast Mode framework integration patterns
- ✅ Operation tracing across all components
- ✅ End-to-end makefile improvement workflow

**Key Test Scenarios:**
- Processing problematic makefile through complete pipeline
- Processing compliant makefile (happy path)
- Health monitoring across multiple operations
- Error handling with corrupted/missing files
- Performance monitoring with large makefiles
- Beast Mode integration (ReflectiveModule patterns)
- Complete improvement workflow (assess → repair → re-assess)

## Running Tests

### Run All Tests
```bash
# Run all makefile governance tests
python scripts/run_makefile_governance_tests.py

# Or use pytest directly
python -m pytest tests/ -k makefile_governance -v
```

### Run Specific Test Categories
```bash
# Unit tests only
python scripts/run_makefile_governance_tests.py --unit

# Integration tests only
python scripts/run_makefile_governance_tests.py --integration

# With coverage report
python scripts/run_makefile_governance_tests.py --coverage
```

### Run Individual Test Files
```bash
# Syntax validator tests
python -m pytest tests/unit/makefile_governance/test_syntax_validator.py -v

# Governance engine tests
python -m pytest tests/unit/makefile_governance/test_governance_engine.py -v

# Health monitor tests
python -m pytest tests/unit/makefile_governance/test_health_monitor.py -v

# Integration tests
python -m pytest tests/integration/makefile_governance/test_integrated_system.py -v
```

### Run Specific Test Methods
```bash
# Run specific test method
python -m pytest tests/unit/makefile_governance/test_syntax_validator.py::TestMakefileSyntaxValidator::test_validate_valid_makefile -v

# Run tests matching pattern
python -m pytest tests/ -k "test_naming_convention" -v
```

## Test Fixtures and Data

### Common Fixtures (from `conftest.py`)
- `sample_makefile_content`: Well-formed makefile for positive tests
- `problematic_makefile_content`: Makefile with various issues for negative tests
- `complex_makefile_content`: Large, complex makefile for performance tests
- `test_data_dir`: Path to test data directory
- `temp_dir`: Temporary directory for file-based tests

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.performance`: Performance-related tests

## Test Coverage

The test suite provides comprehensive coverage of:

### Functional Coverage
- ✅ All public methods and interfaces
- ✅ Error handling and edge cases
- ✅ Configuration and rule management
- ✅ Cross-component integration
- ✅ Beast Mode framework integration

### Scenario Coverage
- ✅ Valid makefiles (positive cases)
- ✅ Invalid makefiles (negative cases)
- ✅ Complex makefiles (performance cases)
- ✅ Missing/corrupted files (error cases)
- ✅ Mixed quality makefiles (realistic cases)

### Integration Coverage
- ✅ Syntax validation → Governance checking
- ✅ Validation results → Health monitoring
- ✅ Repair operations → Re-validation
- ✅ Health monitoring → Alerting
- ✅ All components → Beast Mode framework

## Expected Test Results

### Unit Tests
- **Syntax Validator**: ~25 test methods, all should pass
- **Governance Engine**: ~20 test methods, all should pass  
- **Health Monitor**: ~20 test methods, all should pass

### Integration Tests
- **Integrated System**: ~8 comprehensive test scenarios, all should pass

### Performance Expectations
- Unit tests should complete in < 30 seconds
- Integration tests should complete in < 60 seconds
- Total test suite should complete in < 2 minutes

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure src directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or run from project root
cd /path/to/kiro-ai-development-hackathon
python -m pytest tests/
```

#### Missing Dependencies
```bash
# Install test dependencies
pip install pytest pytest-cov

# Install project dependencies
pip install -r requirements.txt
```

#### File Permission Issues
```bash
# Ensure test runner is executable
chmod +x scripts/run_makefile_governance_tests.py
```

### Test Debugging

#### Verbose Output
```bash
# Maximum verbosity
python -m pytest tests/ -vvv --tb=long

# Show print statements
python -m pytest tests/ -s
```

#### Debug Specific Test
```bash
# Run single test with debugging
python -m pytest tests/unit/makefile_governance/test_syntax_validator.py::TestMakefileSyntaxValidator::test_validate_valid_makefile -vvv --tb=long --pdb
```

#### Coverage Analysis
```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=src/makefile_governance --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Contributing

When adding new tests:

1. **Follow naming conventions**: `test_*.py` files, `Test*` classes, `test_*` methods
2. **Use appropriate fixtures**: Leverage existing fixtures from `conftest.py`
3. **Add docstrings**: Document what each test validates
4. **Use parametrized tests**: For testing multiple similar scenarios
5. **Mock external dependencies**: Use `unittest.mock` for external calls
6. **Test error conditions**: Include negative test cases
7. **Update this README**: Document new test categories or scenarios

### Example Test Structure
```python
def test_new_functionality(self, validator, temp_dir):
    \"\"\"Test description of what this validates.\"\"\"
    # Arrange
    test_data = "test content"
    test_file = temp_dir / "test.mk"
    test_file.write_text(test_data)
    
    # Act
    result = validator.some_method(test_file)
    
    # Assert
    assert result.is_valid is True
    assert len(result.errors) == 0
```

## Quality Metrics

The test suite maintains high quality standards:

- **Coverage**: >90% code coverage for all components
- **Reliability**: All tests should pass consistently
- **Performance**: Fast execution for rapid feedback
- **Maintainability**: Clear, well-documented test code
- **Completeness**: Tests for all public interfaces and edge cases