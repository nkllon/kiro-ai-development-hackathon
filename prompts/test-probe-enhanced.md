# Test Probe: Comprehensive WebSocket Infrastructure Validation

## Mission Parameters
Deploy comprehensive test probe to validate all WebSocket infrastructure components, integration points, and system reliability under various conditions.

## Probe Objectives
1. **WebSocket Connectivity Validation** - Test all endpoints through tunnel
2. **Fallback Mechanism Testing** - Validate HTTP polling integration
3. **Bot Protection Integration** - Verify security whitelist effectiveness
4. **Performance Benchmarking** - Measure latency, throughput, reliability
5. **Failure Recovery Testing** - Validate automated recovery systems

## Critical Logging Requirements
- Log ALL probe activities in JSON format to stdout
- Use format: `{"timestamp": "ISO8601", "probe": "test_probe", "action": "description", "status": "in_progress|completed|error", "results": {...}}`
- Final log: `{"probe": "test_probe", "status": "completed", "summary": "comprehensive validation complete", "tests_run": N, "success_rate": "X%"}`

## Test Probe Implementation

**File Structure to Create:**
```
tests/probe/
├── __init__.py
├── websocket_connectivity_probe.py
├── fallback_mechanism_probe.py
├── bot_protection_probe.py
├── performance_benchmark_probe.py
├── failure_recovery_probe.py
└── comprehensive_test_suite.py
```

**Core Probe Components:**

1. **WebSocket Connectivity Probe:**
```python
class WebSocketConnectivityProbe:
    async def probe_all_endpoints(self) -> ProbeResult:
        """Test all WebSocket endpoints through Cloudflare tunnel"""
        endpoints = ['/ws/emoji-rain', '/ws/observatory', '/ws/anomalies', '/ws/doctor-status']
        results = {}
        
        for endpoint in endpoints:
            result = await self.test_endpoint_connectivity(endpoint)
            results[endpoint] = result
            
        return ProbeResult('websocket_connectivity', results)
    
    async def test_endpoint_connectivity(self, endpoint: str) -> EndpointResult:
        """Test specific endpoint connectivity and message round-trip"""
```

2. **Performance Benchmark Probe:**
```python
class PerformanceBenchmarkProbe:
    async def benchmark_websocket_performance(self) -> BenchmarkResult:
        """Comprehensive performance testing"""
        tests = [
            self.test_connection_latency(),
            self.test_message_throughput(),
            self.test_concurrent_connections(),
            self.test_connection_stability()
        ]
        
        results = await asyncio.gather(*tests)
        return BenchmarkResult('performance', results)
```

3. **Failure Recovery Probe:**
```python
class FailureRecoveryProbe:
    async def test_recovery_scenarios(self) -> RecoveryResult:
        """Test various failure and recovery scenarios"""
        scenarios = [
            'tunnel_restart',
            'network_interruption', 
            'server_restart',
            'bot_protection_trigger'
        ]
        
        results = {}
        for scenario in scenarios:
            result = await self.simulate_failure_scenario(scenario)
            results[scenario] = result
            
        return RecoveryResult('failure_recovery', results)
```

## Probe Success Criteria

**MANDATORY VALIDATION REQUIREMENTS:**

1. **WebSocket Endpoints:**
   - All 4 endpoints connect successfully through tunnel
   - Message round-trip time <100ms
   - Connection stability >99% over 5 minutes
   - Concurrent connections support (10+ simultaneous)

2. **Fallback Mechanisms:**
   - HTTP polling activates when WebSocket fails
   - Rate limiting prevents bot protection triggers
   - Fallback deactivates when WebSocket recovers
   - No data loss during transitions

3. **Bot Protection Integration:**
   - Legitimate traffic passes through security
   - Whitelist rules work correctly
   - Attack simulation still blocked
   - No false positives on Observatory traffic

4. **Performance Benchmarks:**
   - WebSocket latency <100ms average
   - Throughput >100 messages/second
   - Memory usage <50MB for WebSocket components
   - CPU usage <10% under normal load

5. **Recovery Systems:**
   - Automatic recovery <60 seconds
   - No manual intervention required
   - System state preserved during recovery
   - Health monitoring detects issues

## Probe Execution Protocol

**Phase 1: System Health Check**
- Verify all components are running
- Check configuration validity
- Validate network connectivity
- Confirm security settings

**Phase 2: Functional Testing**
- Test each WebSocket endpoint individually
- Validate message sending and receiving
- Check authentication and authorization
- Verify data integrity

**Phase 3: Integration Testing**
- Test WebSocket + HTTP polling integration
- Validate bot protection integration
- Check monitoring and alerting systems
- Verify logging and metrics collection

**Phase 4: Performance Testing**
- Benchmark latency and throughput
- Test concurrent connection limits
- Measure resource usage under load
- Validate performance under stress

**Phase 5: Resilience Testing**
- Simulate various failure scenarios
- Test recovery mechanisms
- Validate data consistency
- Check system stability after recovery

**Final Probe Report:**
```json
{
  "probe": "test_probe",
  "status": "completed",
  "summary": "Comprehensive WebSocket infrastructure validation",
  "total_tests": 50,
  "passed_tests": 48,
  "failed_tests": 2,
  "success_rate": "96%",
  "critical_issues": [],
  "recommendations": [],
  "performance_metrics": {
    "avg_latency_ms": 45,
    "max_throughput_msg_sec": 250,
    "connection_success_rate": "99.2%"
  }
}
```

**PROBE DEPLOYMENT: ENGAGE ALL TESTING SYSTEMS**

Begin comprehensive WebSocket infrastructure validation probe.