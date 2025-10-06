# Observatory Testing Guide

## Overview

This guide covers the comprehensive testing infrastructure for the Beast Mode Coordination Observatory system, designed to ensure bulletproof reliability for customer demos and production deployments.

## Test Suite Architecture

### 🧪 Unit Tests (`tests/unit/beast_mode/observatory/`)
- **Coverage**: 8 comprehensive test files covering all Observatory components
- **Runtime**: < 2 minutes
- **Dependencies**: Mock-heavy, minimal external dependencies
- **Purpose**: Validate individual component functionality

#### Test Files:
- `test_analytics_engine.py` - Analytics processing and insights
- `test_anomaly_detection.py` - Statistical anomaly detection algorithms
- `test_metrics_collector.py` - Real-time metrics collection
- `test_config.py` - Configuration management
- `test_llm_cost_tracker.py` - Multi-provider LLM cost tracking
- `test_redis_streams.py` - Redis Streams integration
- `test_web_interface.py` - WebSocket and HTTP interfaces
- `test_achievement_models.py` - Gamification and achievement systems

### 🔗 Integration Tests (`tests/integration/beast_mode/observatory/`)
- **Coverage**: Cross-system coordination and real Beast Mode integration
- **Runtime**: 3-5 minutes
- **Dependencies**: Redis, Beast Mode components
- **Purpose**: Validate system interactions and data flow

#### Test Files:
- `test_beast_mode_integration.py` - Integration with TaskQueueManager, PDCA orchestrator
- `test_redis_coordination.py` - Redis-based inter-component communication
- `test_end_to_end_scenarios.py` - Complete workflow testing

### ⚡ Performance Tests (`tests/performance/beast_mode/observatory/`)
- **Coverage**: High-volume metrics processing and system limits
- **Runtime**: 1-10 minutes (configurable)
- **Dependencies**: Redis, performance monitoring tools
- **Purpose**: Validate scalability and performance characteristics

#### Test Files:
- `test_high_volume_performance.py` - 10K+ events, 1000+ events/sec sustained
- `test_stress_and_load.py` - System stress testing and resource limits

#### Key Performance Benchmarks:
- **10K Events Sequential**: < 60 seconds
- **10K Events Concurrent**: < 30 seconds
- **Sustained Load**: 1000 events/second for 60+ seconds
- **Memory Usage**: < 2GB peak, < 800MB sustained
- **Response Time**: 95th percentile < 100ms

### 👁️ Visual Tests (`tests/visual/beast_mode/observatory/`)
- **Coverage**: Dashboard rendering and UI regression testing
- **Runtime**: 2-5 minutes
- **Dependencies**: Selenium, PIL, Chromium
- **Purpose**: Validate visual consistency and user interface

#### Test Files:
- `test_dashboard_rendering.py` - Dashboard layout, responsive design, accessibility
- `test_emoji_rain_effects.py` - Gamification animations and visual effects

## Running Tests

### Quick Commands

```bash
# Run all Observatory tests
make test-observatory

# Run specific test types
make test-observatory-unit
make test-observatory-integration
make test-observatory-performance
make test-observatory-visual

# Run critical smoke tests (< 30 seconds)
make test-observatory-smoke

# Generate coverage report
make test-observatory-coverage
```

### Manual pytest Commands

```bash
# Unit tests with coverage
pytest tests/unit/beast_mode/observatory/ -v --cov=src/beast_mode/observatory --cov-fail-under=85

# Integration tests
pytest tests/integration/beast_mode/observatory/ -v

# Performance tests with benchmarking
pytest tests/performance/beast_mode/observatory/ -v --benchmark-json=results.json

# Visual tests (requires display)
xvfb-run pytest tests/visual/beast_mode/observatory/ -v
```

## CI/CD Pipeline

### Automated Testing Workflows

#### 1. Observatory Testing Suite (`.github/workflows/observatory-testing.yml`)
- **Triggers**: Observatory file changes, scheduled daily, manual dispatch
- **Test Types**: Unit, Integration, Performance, Visual
- **Python Versions**: 3.9, 3.10, 3.11, 3.12
- **Quality Gate**: Comprehensive validation before deployment

#### 2. Main CI Integration (`.github/workflows/ci.yml`)
- **Observatory Smoke Tests**: Critical tests in main pipeline
- **Redis Services**: Automatic Redis setup for testing
- **Coverage Reporting**: Observatory coverage integrated with main coverage

### Pre-commit Hooks (`.pre-commit-config.yaml`)
- **Observatory Smoke Tests**: Fast validation before commits
- **Code Quality**: Black, Ruff, MyPy, Bandit integration
- **Security**: Automatic security scanning

## Test Environment Setup

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -e ".[dev]"
   pip install pytest-asyncio pytest-mock pytest-benchmark redis selenium pillow
   ```

2. **Start Redis** (required for integration tests):
   ```bash
   # Docker
   docker run -d -p 6379:6379 redis:7-alpine

   # Or local Redis
   redis-server --port 6379
   ```

3. **For Visual Tests** (optional):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install chromium-browser chromium-chromedriver xvfb

   # macOS
   brew install chromium chromedriver
   ```

### CI/CD Environment

The automated pipelines handle all dependencies and services automatically:
- Redis 7.x with health checks
- Python 3.9-3.12 matrix testing
- Chromium + Selenium for visual tests
- Performance monitoring and regression detection

## Test Data and Fixtures

### Shared Fixtures (`conftest.py` files)

- **Observatory Configuration**: Standardized test configurations
- **Mock Services**: Redis, WebSocket, HTTP client mocks
- **Sample Data**: Metrics, events, coordination patterns
- **Performance Setup**: Optimized configurations for load testing

### Test Data Patterns

- **Metrics Generation**: Realistic LLM cost data, system metrics
- **Event Simulation**: Coordination events, task lifecycle events
- **Error Scenarios**: Network failures, service outages, data corruption

## Coverage Requirements

### Unit Tests
- **Minimum Coverage**: 85%
- **Target Coverage**: 90%+
- **Critical Components**: 95%+ (metrics collector, analytics engine)

### Integration Tests
- **Cross-system Flows**: Complete request/response cycles
- **Error Handling**: Graceful degradation scenarios
- **Performance Baselines**: Established benchmarks for regression detection

## Quality Gates

### Development
- **Pre-commit**: Smoke tests must pass
- **PR Requirements**: Unit + integration tests pass
- **Code Review**: Test coverage and quality review

### Production
- **Master Branch**: All test suites must pass
- **Performance**: No regression in key benchmarks
- **Visual**: No UI regressions detected
- **Security**: All security scans pass

## Troubleshooting

### Common Issues

1. **Redis Connection Errors**:
   ```bash
   # Check Redis is running
   redis-cli ping
   # Should return: PONG
   ```

2. **Visual Test Failures**:
   ```bash
   # Run with display for debugging
   DISPLAY=:0 pytest tests/visual/ -v -s
   ```

3. **Performance Test Timeouts**:
   ```bash
   # Increase timeout for slower systems
   PYTEST_TIMEOUT=1800 pytest tests/performance/ -v
   ```

4. **Import Errors**:
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=src
   pytest tests/unit/beast_mode/observatory/ -v
   ```

### Debug Mode

```bash
# Run with maximum verbosity and no capture
pytest tests/unit/beast_mode/observatory/ -vvs --tb=long

# Run single test with debugging
pytest tests/unit/beast_mode/observatory/test_metrics_collector.py::test_collect_basic_metrics -vvs --pdb
```

## Performance Monitoring

### Continuous Benchmarking
- **Regression Detection**: Automatic performance baseline comparison
- **Trend Analysis**: Performance metrics tracked over time
- **Alerting**: Slack/email notifications for performance degradation

### Key Metrics Tracked
- **Throughput**: Events processed per second
- **Latency**: P95, P99 response times
- **Memory**: Peak and sustained memory usage
- **CPU**: Processing efficiency and utilization
- **Network**: Redis operations per second

## Contributing

### Adding New Tests

1. **Follow Naming Conventions**: `test_[component]_[functionality].py`
2. **Use Async Patterns**: Consistent async/await for real-time components
3. **Mock External Dependencies**: Keep tests isolated and fast
4. **Include Performance Tests**: For any new high-volume features
5. **Add Visual Tests**: For any UI changes or new dashboard components

### Test Review Checklist

- [ ] Tests cover happy path and error scenarios
- [ ] Async tests use proper fixtures and cleanup
- [ ] Performance tests have realistic benchmarks
- [ ] Visual tests include accessibility checks
- [ ] Integration tests validate actual system behavior
- [ ] Tests are documented and maintainable

---

## Success Criteria

The Observatory testing suite ensures:

✅ **Bulletproof Reliability**: 99.9% uptime for customer demos
✅ **Performance Guarantees**: Sub-100ms response times at scale
✅ **Visual Consistency**: Zero UI regressions in production
✅ **Integration Stability**: Seamless Beast Mode coordination
✅ **Security Compliance**: Automated vulnerability detection
✅ **Developer Confidence**: Comprehensive test coverage and fast feedback

*This testing infrastructure supports the Observatory's mission of providing real-time insights and coordination for the Beast Mode Framework.*