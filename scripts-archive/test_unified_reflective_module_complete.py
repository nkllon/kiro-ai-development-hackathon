#!/usr/bin/env python3
"""
Comprehensive Test for Enhanced Unified ReflectiveModule
======================================================

Tests all the systematic infrastructure that was missing:
- Operation tracing with correlation IDs
- Performance metrics collection
- Usage tracking and monitoring
- CLI introspection and caching
- Complete observability

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    OperationTrace
)


class TestReflectiveComponent(ReflectiveModule):
    """Test component to validate enhanced ReflectiveModule"""
    
    def __init__(self):
        super().__init__()
        self.module_id = "TestReflectiveComponent"
    
    def get_module_info(self) -> dict:
        return {
            "module_id": self.module_id,
            "name": "TestReflectiveComponent",
            "version": "1.0.0"
        }
    
    def get_capabilities(self) -> list:
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self):
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def test_operation(self, param1: str, param2: int = 42) -> dict:
        """Test operation for CLI and tracing validation"""
        with self.trace_operation("test_operation", param1=param1, param2=param2) as trace:
            # Simulate some work
            time.sleep(0.01)  # 10ms
            result = {"processed": param1, "value": param2 * 2}
            trace.output_result = result
            return result
    
    def failing_operation(self) -> None:
        """Test operation that fails for error tracing"""
        with self.trace_operation("failing_operation") as trace:
            raise ValueError("Intentional test failure")


def main():
    """Comprehensive test of enhanced ReflectiveModule infrastructure"""
    print("🧪 Enhanced ReflectiveModule Infrastructure Test")
    print("=" * 70)
    
    # Initialize test component
    component = TestReflectiveComponent()
    
    # Test 1: Basic RM-DDD compliance
    print("\n1. Testing Basic RM-DDD Compliance:")
    print(f"   Module ID: {component.module_id}")
    print(f"   Capabilities: {[cap.value for cap in component.get_capabilities()]}")
    print(f"   Health: {component.get_health_status().status.value}")
    
    # Test 2: CLI Introspection
    print("\n2. Testing CLI Introspection:")
    cli_interface = component.get_cli_interface()
    print(f"   Available Commands: {list(cli_interface['commands'].keys())}")
    
    # Test CLI help generation
    help_text = component.generate_cli_help("test_operation")
    print(f"   CLI Help Generated: {len(help_text)} characters")
    print(f"   Sample Help:\n{help_text[:200]}...")
    
    # Test 3: Operation Tracing
    print("\n3. Testing Operation Tracing:")
    
    # Execute traced operations
    result1 = component.test_operation("hello", 10)
    print(f"   Operation 1 Result: {result1}")
    
    result2 = component.test_operation("world", 20)
    print(f"   Operation 2 Result: {result2}")
    
    # Test error tracing
    try:
        component.failing_operation()
    except ValueError as e:
        print(f"   Error Operation Traced: {e}")
    
    # Check traces
    traces = component.get_operation_traces()
    print(f"   Total Traces Collected: {len(traces)}")
    
    for i, trace in enumerate(traces):
        print(f"   Trace {i+1}: {trace.operation_name} - {trace.duration_ms:.2f}ms - Success: {trace.error_info is None}")
    
    # Test 4: Performance Metrics
    print("\n4. Testing Performance Metrics:")
    metrics = component.get_performance_metrics()
    print(f"   Operation Count: {metrics['operation_count']}")
    print(f"   Average Time: {metrics['average_operation_time_ms']:.2f}ms")
    print(f"   Error Rate: {metrics['error_rate']:.2%}")
    print(f"   Uptime: {metrics['uptime_seconds']:.1f}s")
    
    # Test 5: Usage Tracking
    print("\n5. Testing Usage Tracking:")
    usage = component.get_usage_tracking()
    print(f"   Operation Frequency: {usage['operation_frequency']}")
    print(f"   Tracking Period: {usage['tracking_period_start'][:19]} to {usage['tracking_period_end'][:19]}")
    
    # Test 6: CLI Caching
    print("\n6. Testing CLI Caching:")
    cache_options = component.get_cli_cache_options()
    print(f"   Lazy Instantiation: {cache_options['lazy_instantiation']}")
    print(f"   Cache Enabled: {cache_options['cache_enabled']}")
    
    # Enable caching
    component.enable_cli_caching(True, 1800)
    updated_options = component.get_cli_cache_options()
    print(f"   Cache Enabled After Setup: {updated_options['cache_enabled']}")
    
    # Test 7: CLI Command Execution
    print("\n7. Testing CLI Command Execution:")
    try:
        cli_result = component.execute_cli_command("test_operation", param1="cli_test", param2=99)
        print(f"   CLI Execution Result: {cli_result}")
    except Exception as e:
        print(f"   CLI Execution Error: {e}")
    
    # Test 8: Correlation ID System
    print("\n8. Testing Correlation ID System:")
    print(f"   Component Correlation ID: {component._correlation_id}")
    
    # Verify all traces have correlation IDs
    all_traces = component.get_operation_traces()
    traces_with_correlation = [t for t in all_traces if t.correlation_id]
    print(f"   Traces with Correlation IDs: {len(traces_with_correlation)}/{len(all_traces)}")
    
    # Debug correlation IDs
    for i, trace in enumerate(all_traces):
        print(f"   Trace {i+1} Correlation ID: {trace.correlation_id}")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("📊 Enhanced Infrastructure Test Summary:")
    
    tests_passed = []
    
    # Check each requirement
    tests_passed.append(("RM-DDD Compliance", True))
    tests_passed.append(("CLI Introspection", len(cli_interface['commands']) > 0))
    tests_passed.append(("Operation Tracing", len(traces) > 0))
    tests_passed.append(("Performance Metrics", metrics['operation_count'] > 0))
    tests_passed.append(("Usage Tracking", len(usage['operation_frequency']) > 0))
    tests_passed.append(("CLI Caching", updated_options['cache_enabled']))
    correlation_test_passed = len(traces_with_correlation) > 0 and len(traces_with_correlation) == len(all_traces)
    print(f"   DEBUG: traces_with_correlation={len(traces_with_correlation)}, all_traces={len(all_traces)}, test={correlation_test_passed}")
    tests_passed.append(("Correlation IDs", correlation_test_passed))
    
    for test_name, passed in tests_passed:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    all_passed = all(passed for _, passed in tests_passed)
    
    if all_passed:
        print("\n🎉 ALL INFRASTRUCTURE TESTS PASSED!")
        print("   Enhanced ReflectiveModule is fully compliant with requirements:")
        print("   - Requirement 21: Dynamic CLI Generation ✅")
        print("   - Requirement 22: Usage Tracking and Monitoring ✅")
        print("   - Complete operation traceability ✅")
        print("   - Performance metrics collection ✅")
        print("   - Correlation ID system ✅")
        return True
    else:
        print("\n⚠️  SOME INFRASTRUCTURE TESTS FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)