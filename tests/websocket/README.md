# WebSocket Connectivity Test Suite

## Overview

This comprehensive test suite validates WebSocket functionality for the Beast Mode Observatory system, ensuring >90% test coverage and robust connectivity under various load conditions.

## Test Structure

```
tests/websocket/
├── unit/                          # Unit tests for individual components
│   ├── test_websocket_manager.py  # WebSocket manager functionality
│   ├── test_connection_handler.py # Connection handling and state management
│   └── test_retry_logic.py        # Retry strategy and exponential backoff
├── integration/                   # Integration tests for system components
│   ├── test_tunnel_websocket.py   # Tunnel WebSocket connectivity
│   ├── test_end_to_end.py         # End-to-end WebSocket scenarios
│   └── test_fallback_integration.py # Fallback and recovery scenarios
├── load/                          # Load and performance tests
│   ├── test_concurrent_connections.py # Concurrent connection handling
│   ├── test_message_throughput.py     # Message throughput testing
│   └── test_connection_stability.py   # Long-term stability testing
├── fixtures/                      # Test fixtures and mock data
│   ├── websocket_test_data.py     # Test data generators and configurations
│   └── mock_tunnel_config.py      # Mock tunnel configurations
├── run_websocket_tests.py         # Test runner with coverage validation
└── README.md                      # This documentation
```

## Test Categories

### Unit Tests (`tests/websocket/unit/`)

**Purpose**: Test individual WebSocket components in isolation

**Coverage**:
- WebSocket Manager initialization, connection management, and lifecycle
- Connection handler state transitions, message sending/receiving
- Retry logic with exponential backoff and error handling
- Health monitoring and callback mechanisms

**Key Test Scenarios**:
- Successful connection establishment
- Connection failure handling and recovery
- Message roundtrip communication
- Retry strategy validation
- Connection state management

### Integration Tests (`tests/websocket/integration/`)

**Purpose**: Test WebSocket components working together

**Coverage**:
- Tunnel WebSocket connectivity and validation
- End-to-end message flow scenarios
- Fallback and recovery mechanisms
- Health monitoring integration
- Error scenario handling

**Key Test Scenarios**:
- Tunnel connection lifecycle
- WebSocket upgrade validation
- End-to-end message communication
- Primary-to-fallback switching
- Multi-endpoint connectivity

### Load Tests (`tests/websocket/load/`)

**Purpose**: Validate WebSocket performance under load

**Coverage**:
- Concurrent connection handling (10-200 connections)
- Message throughput (100-2000 messages/second)
- Connection stability over extended periods (30+ minutes)
- Memory and CPU usage monitoring

**Key Test Scenarios**:
- Light load: 10 concurrent connections, 100 msg/s
- Medium load: 50 concurrent connections, 500 msg/s
- Heavy load: 100 concurrent connections, 1000 msg/s
- Stress test: 200 concurrent connections, 2000 msg/s
- Sustained load: 30+ minute stability testing

## Test Requirements Coverage

### Requirements 7.1: WebSocket Connection Management
- ✅ Connection establishment and teardown
- ✅ Connection pooling and lifecycle management
- ✅ Health monitoring and status tracking
- ✅ Error handling and recovery

### Requirements 7.2: Tunnel WebSocket Connectivity
- ✅ Tunnel endpoint connectivity validation
- ✅ WebSocket upgrade request validation
- ✅ Protocol handshake verification
- ✅ Endpoint health monitoring

### Requirements 7.3: Load Testing
- ✅ Concurrent connection testing (100+ connections)
- ✅ Message throughput testing (1000+ msg/s)
- ✅ Connection stability testing (30+ minutes)
- ✅ Performance metrics collection

### Requirements 7.7: Quality Assurance
- ✅ >90% test coverage requirement
- ✅ Comprehensive error scenario testing
- ✅ Performance benchmarking
- ✅ Documentation and reporting

## Running Tests

### Run All Tests with Coverage
```bash
python tests/websocket/run_websocket_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/websocket/unit/ -v --cov=src/beast_mode/observatory/websocket

# Integration tests only
pytest tests/websocket/integration/ -v --cov=src/beast_mode/observatory/websocket

# Load tests only
pytest tests/websocket/load/ -v --timeout=1800
```

### Run Individual Test Files
```bash
# WebSocket manager tests
pytest tests/websocket/unit/test_websocket_manager.py -v

# Connection handler tests
pytest tests/websocket/unit/test_connection_handler.py -v

# Retry logic tests
pytest tests/websocket/unit/test_retry_logic.py -v

# Tunnel integration tests
pytest tests/websocket/integration/test_tunnel_websocket.py -v

# End-to-end tests
pytest tests/websocket/integration/test_end_to_end.py -v

# Concurrent connection load tests
pytest tests/websocket/load/test_concurrent_connections.py -v

# Message throughput load tests
pytest tests/websocket/load/test_message_throughput.py -v

# Connection stability load tests
pytest tests/websocket/load/test_connection_stability.py -v
```

## Test Configuration

### Environment Variables
```bash
export WEBSOCKET_TEST_BASE_URL="ws://localhost:8000"
export WEBSOCKET_TEST_TUNNEL_URL="wss://observatory.nkllon.com"
export WEBSOCKET_TEST_TIMEOUT="30"
export WEBSOCKET_TEST_MAX_CONNECTIONS="100"
```

### Test Data Configuration
Tests use configurable test data from `fixtures/websocket_test_data.py`:
- Test endpoints and URLs
- Message payloads and sizes
- Error scenarios and failure modes
- Load test scenarios and parameters

## Coverage Requirements

### Minimum Coverage: 90%
- Unit tests: Target 95%+ coverage
- Integration tests: Target 90%+ coverage
- Load tests: Target 85%+ coverage
- Overall: Must meet 90%+ requirement

### Coverage Reports
- JSON format: `coverage_all.json`
- HTML format: `htmlcov/index.html`
- Terminal output: Missing lines highlighted

## Performance Benchmarks

### Connection Performance
- Connection establishment: <100ms
- Connection teardown: <50ms
- Health check response: <30ms

### Message Performance
- Small messages (<1KB): <10ms latency
- Medium messages (1-10KB): <50ms latency
- Large messages (>10KB): <200ms latency
- Throughput: >1000 messages/second

### Stability Requirements
- 30+ minute continuous operation
- <1% connection failure rate
- Automatic recovery from failures
- Memory usage stability

## Error Scenarios Tested

### Connection Errors
- Network timeouts
- Authentication failures
- Rate limit exceeded
- Protocol errors
- Network unavailable

### Message Errors
- Send failures
- Receive timeouts
- Invalid message formats
- Connection drops during transmission

### System Errors
- Resource exhaustion
- Memory leaks
- CPU overload
- Disk space issues

## Test Metrics and Reporting

### Metrics Collected
- Connection success/failure rates
- Message throughput (messages/second)
- Connection latency (milliseconds)
- Error counts by type
- Resource usage (memory/CPU)
- Test execution duration

### Report Generation
- JSON test report: `websocket_test_report.json`
- Coverage reports: Multiple formats
- Performance metrics: Detailed timing
- Error analysis: Categorized failures

## Continuous Integration

### CI/CD Integration
Tests are designed to run in CI/CD pipelines with:
- Automated test execution
- Coverage validation
- Performance regression detection
- Report generation and storage

### Test Parallelization
- Unit tests: Can run in parallel
- Integration tests: Sequential execution
- Load tests: Controlled concurrency

## Troubleshooting

### Common Issues
1. **Connection Timeouts**: Check network connectivity and server availability
2. **Coverage Failures**: Ensure all code paths are tested
3. **Performance Degradation**: Monitor system resources during tests
4. **Mock Failures**: Verify mock configurations and expectations

### Debug Mode
```bash
# Run with debug output
pytest tests/websocket/ -v -s --log-cli-level=DEBUG

# Run specific test with detailed output
pytest tests/websocket/unit/test_websocket_manager.py::TestWebSocketManager::test_manager_initialization -v -s
```

## Maintenance

### Regular Updates
- Update test data and scenarios
- Add new error cases as discovered
- Extend load test parameters
- Update performance benchmarks

### Test Data Management
- Refresh test fixtures regularly
- Update mock configurations
- Validate test scenarios against real-world usage
- Maintain test data diversity

## Contributing

### Adding New Tests
1. Follow existing test patterns and naming conventions
2. Include comprehensive docstrings and comments
3. Add appropriate fixtures and mock data
4. Update coverage requirements if needed
5. Document new test scenarios

### Test Quality Standards
- Clear test names and descriptions
- Comprehensive assertions
- Proper error handling
- Resource cleanup
- Performance considerations