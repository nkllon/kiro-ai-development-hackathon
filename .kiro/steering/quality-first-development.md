---
inclusion: always
---

# Quality-First Development - Systematic Testing and Validation

## Core Principle

**"Quality is not optional. Every Beast Mode component must have >90% test coverage, systematic error handling, and production-ready observability before deployment."**

## Testing Patterns for Beast Mode

### **ALWAYS Test ReflectiveModule Components**

```python
import pytest
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

class TestYourBeastModeSystem:
    """Systematic testing for Beast Mode components"""
    
    def test_health_endpoint_automatic(self):
        """Test automatic health endpoint from ReflectiveModule"""
        system = YourBeastModeSystem()
        health = system.health_check()
        
        assert health["status"] == "healthy"
        assert "timestamp" in health
        assert "metrics" in health
        assert health["uptime"] >= 0
    
    def test_metrics_collection_automatic(self):
        """Test automatic metrics collection"""
        system = YourBeastModeSystem()
        system.process_request({"test": "data"})
        
        metrics = system.get_metrics()
        assert "requests_processed" in metrics
        assert "response_time_ms" in metrics
        assert "error_rate" in metrics
    
    def test_correlation_id_tracing(self):
        """Test automatic correlation ID generation"""
        system = YourBeastModeSystem()
        
        # Each request gets unique correlation ID
        result1 = system.process_request({"data": "test1"})
        result2 = system.process_request({"data": "test2"})
        
        assert result1.correlation_id != result2.correlation_id
        assert len(result1.correlation_id) == 36  # UUID format
```

### **DAG Orchestration Testing**

```python
from src.dag_orchestration import DAGOrchestrator

class TestDAGOrchestration:
    """Test mathematical governance of task dependencies"""
    
    def test_cycle_detection(self):
        """Test automatic cycle detection"""
        orchestrator = DAGOrchestrator()
        
        # Create cyclic dependency
        orchestrator.add_task("task_a", dependencies=["task_b"])
        orchestrator.add_task("task_b", dependencies=["task_c"])
        orchestrator.add_task("task_c", dependencies=["task_a"])  # Creates cycle
        
        with pytest.raises(CyclicDependencyError):
            orchestrator.execute()
    
    def test_parallel_execution(self):
        """Test automatic parallelization"""
        orchestrator = DAGOrchestrator()
        
        # Independent tasks should run in parallel
        orchestrator.add_task("parallel_task_1", dependencies=[])
        orchestrator.add_task("parallel_task_2", dependencies=[])
        orchestrator.add_task("dependent_task", dependencies=["parallel_task_1", "parallel_task_2"])
        
        start_time = time.time()
        results = orchestrator.execute()
        execution_time = time.time() - start_time
        
        # Should complete faster than sequential execution
        assert execution_time < 2.0  # Parallel execution benefit
        assert len(results) == 3
    
    def test_topological_sorting(self):
        """Test mathematical ordering of tasks"""
        orchestrator = DAGOrchestrator()
        
        orchestrator.add_task("setup", dependencies=[])
        orchestrator.add_task("build", dependencies=["setup"])
        orchestrator.add_task("test", dependencies=["build"])
        orchestrator.add_task("deploy", dependencies=["test"])
        
        execution_order = orchestrator.get_execution_order()
        
        # Verify mathematical ordering
        assert execution_order.index("setup") < execution_order.index("build")
        assert execution_order.index("build") < execution_order.index("test")
        assert execution_order.index("test") < execution_order.index("deploy")
```

### **AI Memory Palace Testing**

```python
from src.ai_memory_palace import MemoryPalace

class TestAIMemoryPalace:
    """Test persistent AI memory across sessions"""
    
    def test_context_persistence(self):
        """Test context survives across sessions"""
        palace = MemoryPalace()
        
        # Store context
        context = {
            "project": "beast_mode_integration",
            "current_task": "implementing_tests",
            "decisions": ["using_pytest", "90_percent_coverage"]
        }
        palace.remember("session_context", context)
        
        # Simulate new session
        new_palace = MemoryPalace()
        recalled_context = new_palace.recall("session_context")
        
        assert recalled_context == context
        assert recalled_context["project"] == "beast_mode_integration"
    
    def test_memory_optimization(self):
        """Test memory storage optimization"""
        palace = MemoryPalace()
        
        # Store large context
        large_context = {"data": "x" * 10000}  # 10KB of data
        palace.remember("large_context", large_context)
        
        # Verify compression/optimization
        storage_stats = palace.get_storage_stats()
        assert storage_stats["compression_ratio"] > 0.5  # At least 50% compression
        assert storage_stats["retrieval_time_ms"] < 100  # Sub-100ms retrieval
```

## Quality Gates and Validation

### **Mandatory Quality Checks**

```python
class QualityGate:
    """Systematic quality validation for Beast Mode components"""
    
    def validate_component(self, component_class):
        """Comprehensive quality validation"""
        
        # 1. Test Coverage Validation
        coverage = self.measure_test_coverage(component_class)
        if coverage < 0.90:
            raise QualityGateFailure(f"Test coverage {coverage} < 90% required")
        
        # 2. ReflectiveModule Inheritance
        if not issubclass(component_class, ReflectiveModule):
            raise QualityGateFailure("Component must inherit from ReflectiveModule")
        
        # 3. Health Endpoint Validation
        instance = component_class()
        health = instance.health_check()
        if health["status"] != "healthy":
            raise QualityGateFailure("Health check failed")
        
        # 4. Metrics Collection Validation
        metrics = instance.get_metrics()
        required_metrics = ["requests_processed", "response_time_ms", "error_rate"]
        for metric in required_metrics:
            if metric not in metrics:
                raise QualityGateFailure(f"Missing required metric: {metric}")
        
        # 5. Error Handling Validation
        try:
            instance.process_invalid_request({"invalid": "data"})
        except Exception as e:
            if not hasattr(e, 'correlation_id'):
                raise QualityGateFailure("Errors must include correlation IDs")
        
        return True
```

### **Performance Validation**

```python
class PerformanceValidator:
    """Validate performance requirements"""
    
    def validate_performance(self, system):
        """Systematic performance validation"""
        
        # 1. Startup Time Validation
        start_time = time.time()
        system.initialize()
        startup_time = time.time() - start_time
        
        if startup_time > 2.0:
            raise PerformanceFailure(f"Startup time {startup_time}s > 2s limit")
        
        # 2. Memory Usage Validation
        memory_usage = self.measure_memory_usage(system)
        if memory_usage > 100 * 1024 * 1024:  # 100MB
            raise PerformanceFailure(f"Memory usage {memory_usage} > 100MB limit")
        
        # 3. Throughput Validation
        throughput = self.measure_throughput(system, duration=10)
        if throughput < 1000:  # 1000 ops/second
            raise PerformanceFailure(f"Throughput {throughput} < 1000 ops/s")
        
        # 4. Response Time Validation
        response_times = self.measure_response_times(system, samples=100)
        p95_response_time = np.percentile(response_times, 95)
        
        if p95_response_time > 100:  # 100ms
            raise PerformanceFailure(f"P95 response time {p95_response_time}ms > 100ms")
        
        return True
```

## Error Handling and Resilience Testing

### **Systematic Error Handling Tests**

```python
class TestErrorHandling:
    """Test systematic error handling patterns"""
    
    def test_graceful_degradation(self):
        """Test graceful degradation on failures"""
        system = YourBeastModeSystem()
        
        # Simulate dependency failure
        with mock.patch.object(system.dependency, 'process', side_effect=Exception("Dependency failed")):
            result = system.process_request({"test": "data"})
            
            # Should return fallback response, not crash
            assert result is not None
            assert result.status == "degraded"
            assert "fallback" in result.response_type
    
    def test_correlation_id_propagation(self):
        """Test correlation ID propagation through error paths"""
        system = YourBeastModeSystem()
        
        try:
            system.process_invalid_request({"invalid": "data"})
        except Exception as e:
            assert hasattr(e, 'correlation_id')
            assert len(e.correlation_id) == 36  # UUID format
            
            # Check logs contain correlation ID
            logs = system.get_recent_logs()
            assert any(e.correlation_id in log for log in logs)
    
    def test_circuit_breaker_pattern(self):
        """Test circuit breaker for failing dependencies"""
        system = YourBeastModeSystem()
        
        # Trigger multiple failures to open circuit breaker
        for _ in range(5):
            with mock.patch.object(system.dependency, 'process', side_effect=Exception("Failure")):
                system.process_request({"test": "data"})
        
        # Circuit breaker should be open
        assert system.circuit_breaker.is_open()
        
        # Subsequent requests should fail fast
        start_time = time.time()
        result = system.process_request({"test": "data"})
        response_time = time.time() - start_time
        
        assert response_time < 0.01  # Fail fast (< 10ms)
        assert result.status == "circuit_open"
```

### **Resilience Testing**

```python
class TestResilience:
    """Test system resilience patterns"""
    
    def test_retry_with_exponential_backoff(self):
        """Test automatic retry with exponential backoff"""
        system = YourBeastModeSystem()
        
        call_count = 0
        def failing_dependency():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        with mock.patch.object(system.dependency, 'process', side_effect=failing_dependency):
            result = system.process_request({"test": "data"})
            
            assert result.status == "success"
            assert call_count == 3  # Retried twice before success
    
    def test_timeout_handling(self):
        """Test timeout handling for long-running operations"""
        system = YourBeastModeSystem()
        
        def slow_dependency():
            time.sleep(5)  # Simulate slow operation
            return "slow_result"
        
        with mock.patch.object(system.dependency, 'process', side_effect=slow_dependency):
            start_time = time.time()
            result = system.process_request({"test": "data"}, timeout=2)
            execution_time = time.time() - start_time
            
            assert execution_time < 3  # Should timeout before 5s
            assert result.status == "timeout"
```

## Integration Testing Patterns

### **End-to-End Testing**

```python
class TestEndToEnd:
    """End-to-end testing for complete Beast Mode systems"""
    
    def test_complete_workflow(self):
        """Test complete workflow from request to response"""
        system = YourBeastModeSystem()
        
        # 1. Initialize system
        system.initialize()
        assert system.health_check()["status"] == "healthy"
        
        # 2. Process request with memory persistence
        request = {"user_id": "test_user", "action": "create_project"}
        result = system.process_request(request)
        
        assert result.status == "success"
        assert result.correlation_id is not None
        
        # 3. Verify memory persistence
        context = system.memory.recall("user_session")
        assert context["last_action"] == "create_project"
        
        # 4. Verify metrics collection
        metrics = system.get_metrics()
        assert metrics["requests_processed"] >= 1
        
        # 5. Verify health monitoring
        health = system.health_check()
        assert health["status"] == "healthy"
        assert health["last_request_time"] is not None
```

## Quality Metrics and Reporting

### **Automated Quality Reporting**

```python
class QualityReporter:
    """Generate comprehensive quality reports"""
    
    def generate_quality_report(self, system):
        """Generate comprehensive quality metrics"""
        
        return {
            "test_coverage": self.measure_test_coverage(system),
            "performance_metrics": {
                "startup_time_ms": self.measure_startup_time(system),
                "memory_usage_mb": self.measure_memory_usage(system) / 1024 / 1024,
                "throughput_ops_per_sec": self.measure_throughput(system),
                "p95_response_time_ms": self.measure_p95_response_time(system)
            },
            "reliability_metrics": {
                "error_rate": self.calculate_error_rate(system),
                "availability": self.calculate_availability(system),
                "mttr_minutes": self.calculate_mttr(system),
                "mtbf_hours": self.calculate_mtbf(system)
            },
            "security_metrics": {
                "hardcoded_secrets": self.scan_for_hardcoded_secrets(system),
                "vulnerability_count": self.security_scan(system),
                "compliance_score": self.compliance_check(system)
            },
            "maintainability_metrics": {
                "cyclomatic_complexity": self.calculate_complexity(system),
                "code_duplication": self.measure_duplication(system),
                "technical_debt_hours": self.estimate_technical_debt(system)
            }
        }
```

## Anti-Patterns - Quality Violations

### ❌ **Manual Health Checks**
```python
# WRONG: Manual health check without systematic monitoring
def health_check():
    return {"status": "ok"}  # No metrics, no correlation IDs
```

### ❌ **Ad-hoc Testing**
```python
# WRONG: Inconsistent testing without coverage requirements
def test_something():
    assert True  # No real validation
```

### ❌ **No Error Handling**
```python
# WRONG: No systematic error handling
def process_request(request):
    return do_processing(request)  # Will crash on errors
```

## Success Metrics

### **Quality Gates**
- **Test Coverage**: >90% for all components
- **Performance**: <2s startup, <100ms P95 response time
- **Reliability**: >99.9% availability, <5min MTTR
- **Security**: Zero hardcoded secrets, zero critical vulnerabilities

### **Systematic Validation**
- **ReflectiveModule Inheritance**: 100% of components
- **Health Endpoints**: Automatic for all components
- **Metrics Collection**: Comprehensive for all operations
- **Error Handling**: Systematic with correlation IDs

## The Meta-Principle

**"Quality is not negotiable. Every Beast Mode component must meet systematic quality standards before deployment. If it doesn't have >90% test coverage and systematic observability, it's not ready for production."**

Quality-first development ensures:
- **Reliability** through comprehensive testing
- **Observability** through systematic monitoring
- **Maintainability** through quality metrics
- **Security** through systematic validation
- **Performance** through continuous measurement

---

**This steering rule ensures all Beast Mode development follows quality-first principles with systematic testing, validation, and observability.**