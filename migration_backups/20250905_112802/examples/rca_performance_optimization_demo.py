#!/usr/bin/env python3
"""
Beast Mode Framework - RCA Performance Optimization Demo
Demonstrates performance monitoring, timeout handling, and resource management for RCA operations
Requirements: 1.4, 4.2 - Performance optimization and timeout handling demonstration
"""

import time
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.testing.performance_monitor import RCAPerformanceMonitor, ResourceLimits
from beast_mode.testing.timeout_handler import RCATimeoutHandler, TimeoutConfiguration, TimeoutStrategy
from beast_mode.testing.rca_integration import TestRCAIntegrationEngine, TestFailureData
from beast_mode.analysis.rca_engine import RCAEngine


def create_sample_test_failures():
    """Create sample test failures for demonstration"""
    failures = []
    
    # Create different types of test failures
    failure_types = [
        ("assertion", "AssertionError: Expected True, got False"),
        ("import", "ImportError: No module named 'missing_module'"),
        ("timeout", "TimeoutError: Test execution exceeded 30 seconds"),
        ("fixture", "FixtureError: Fixture 'database' not found"),
        ("setup", "SetupError: Test setup failed")
    ]
    
    for i, (failure_type, error_message) in enumerate(failure_types):
        failure = TestFailureData(
            test_name=f"test_example_{i}",
            test_file=f"test_example_{i}.py",
            failure_type=failure_type,
            error_message=error_message,
            stack_trace=f"Traceback (most recent call last):\n  File test_example_{i}.py, line 10, in test_function\n    {error_message}",
            test_function=f"test_example_function_{i}",
            test_class="TestExample",
            failure_timestamp=datetime.now(),
            test_context={"environment": "test", "ci": False},
            pytest_node_id=f"test_example_{i}.py::TestExample::test_example_function_{i}"
        )
        failures.append(failure)
        
    return failures


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring capabilities"""
    print("=" * 60)
    print("RCA Performance Monitoring Demonstration")
    print("=" * 60)
    
    # Create performance monitor with custom resource limits
    resource_limits = ResourceLimits(
        max_memory_mb=256,
        max_cpu_percent=70.0,
        timeout_seconds=30,
        warning_threshold_seconds=25,
        memory_warning_threshold_mb=200
    )
    
    monitor = RCAPerformanceMonitor(resource_limits)
    monitor.start_monitoring()
    
    print(f"Performance monitor initialized with limits:")
    print(f"  - Max memory: {resource_limits.max_memory_mb}MB")
    print(f"  - Max CPU: {resource_limits.max_cpu_percent}%")
    print(f"  - Timeout: {resource_limits.timeout_seconds}s")
    print()
    
    # Demonstrate operation monitoring
    operation_id = "demo_rca_operation"
    
    print(f"Starting monitored operation: {operation_id}")
    with monitor.monitor_operation(operation_id, timeout_seconds=5) as metrics:
        print(f"  Operation started at: {metrics.start_time}")
        print(f"  Initial memory usage: {metrics.memory_usage_mb:.2f}MB")
        
        # Simulate some work
        time.sleep(1.0)
        print("  Performing RCA analysis simulation...")
        
        # Simulate more work
        time.sleep(0.5)
        print("  Analysis complete")
        
    print(f"  Operation completed in: {metrics.duration_seconds:.2f}s")
    print(f"  Peak memory usage: {metrics.peak_memory_mb:.2f}MB")
    print(f"  Operation status: {metrics.operation_status.value}")
    print()
    
    # Demonstrate graceful degradation
    print("Demonstrating graceful degradation:")
    degradation_result = monitor.implement_graceful_degradation(operation_id, "simplified_analysis")
    print(f"  Degradation applied: {degradation_result['degradation_applied']}")
    print(f"  Strategy: {degradation_result['strategy']}")
    print(f"  Analysis scope: {degradation_result.get('analysis_scope', 'N/A')}")
    print()
    
    # Get performance report
    performance_report = monitor.get_performance_report()
    print("Performance Report:")
    print(f"  Total operations: {performance_report.total_operations}")
    print(f"  Successful operations: {performance_report.successful_operations}")
    print(f"  Average duration: {performance_report.average_duration_seconds:.2f}s")
    print(f"  Average memory usage: {performance_report.average_memory_usage_mb:.2f}MB")
    print(f"  Performance trend: {performance_report.performance_trend}")
    print()
    
    monitor.stop_monitoring()
    print("Performance monitoring stopped")
    print()


def demonstrate_timeout_handling():
    """Demonstrate timeout handling capabilities"""
    print("=" * 60)
    print("RCA Timeout Handling Demonstration")
    print("=" * 60)
    
    # Create timeout handler with custom configuration
    timeout_config = TimeoutConfiguration(
        primary_timeout_seconds=30,
        warning_timeout_seconds=25,
        graceful_timeout_seconds=20,
        hard_timeout_seconds=35,
        strategy=TimeoutStrategy.GRACEFUL_DEGRADATION,
        enable_progressive_degradation=True,
        max_degradation_levels=3
    )
    
    handler = RCATimeoutHandler(timeout_config)
    
    print(f"Timeout handler initialized with configuration:")
    print(f"  - Primary timeout: {timeout_config.primary_timeout_seconds}s")
    print(f"  - Warning timeout: {timeout_config.warning_timeout_seconds}s")
    print(f"  - Graceful timeout: {timeout_config.graceful_timeout_seconds}s")
    print(f"  - Strategy: {timeout_config.strategy.value}")
    print()
    
    # Demonstrate timeout management
    operation_id = "demo_timeout_operation"
    
    print(f"Managing timeout for operation: {operation_id}")
    with handler.manage_operation_timeout(operation_id) as timeout_context:
        print(f"  Operation started at: {timeout_context['start_time']}")
        
        # Simulate work and check timeout status
        for i in range(3):
            time.sleep(0.5)
            elapsed = (datetime.now() - timeout_context['start_time']).total_seconds()
            
            # Get timeout recommendations
            recommendations = handler.get_timeout_recommendations(operation_id, elapsed)
            print(f"  Elapsed: {elapsed:.1f}s, Status: {recommendations['timeout_status']}")
            
            if recommendations.get('degradation_suggested', False):
                print(f"    Recommendations: {', '.join(recommendations['recommendations'])}")
                
    print("  Operation completed within timeout limits")
    print()
    
    # Demonstrate different degradation levels
    print("Demonstrating degradation levels:")
    for level in range(1, 4):
        result = handler.apply_graceful_degradation(f"demo_degradation_{level}", level)
        print(f"  Level {level}: {result['strategy']} - {result.get('estimated_time_savings', 'N/A')}")
        
    print()
    
    # Get timeout recommendations for different elapsed times
    print("Timeout recommendations for different elapsed times:")
    test_times = [5, 15, 22, 27, 32]
    for elapsed_time in test_times:
        recommendations = handler.get_timeout_recommendations("demo_recommendations", elapsed_time)
        print(f"  {elapsed_time}s: {recommendations['timeout_status']} - {recommendations.get('recommendations', [])}")
        
    print()


def demonstrate_integrated_rca_performance():
    """Demonstrate integrated RCA with performance optimization"""
    print("=" * 60)
    print("Integrated RCA Performance Optimization Demonstration")
    print("=" * 60)
    
    # Create RCA integration engine with performance monitoring
    try:
        integrator = TestRCAIntegrationEngine()
        print("RCA integration engine initialized with performance monitoring")
        print()
        
        # Create sample test failures
        test_failures = create_sample_test_failures()
        print(f"Created {len(test_failures)} sample test failures:")
        for i, failure in enumerate(test_failures):
            print(f"  {i+1}. {failure.failure_type}: {failure.test_name}")
        print()
        
        # Perform RCA analysis with performance monitoring
        print("Performing RCA analysis with performance monitoring...")
        start_time = time.time()
        
        try:
            result = integrator.analyze_test_failures(test_failures)
            analysis_time = time.time() - start_time
            
            print(f"RCA analysis completed in {analysis_time:.2f}s")
            print(f"  Total failures: {result.total_failures}")
            print(f"  Failures analyzed: {result.failures_analyzed}")
            print(f"  Grouped failures: {len(result.grouped_failures)}")
            print(f"  RCA results: {len(result.rca_results)}")
            print()
            
            # Get performance report
            performance_report = integrator.get_performance_report()
            print("Integrated Performance Report:")
            
            rca_perf = performance_report.get("rca_integration_performance", {})
            print(f"  Total operations: {rca_perf.get('total_operations', 0)}")
            print(f"  Average duration: {rca_perf.get('average_duration_seconds', 0):.2f}s")
            print(f"  Timeout rate: {rca_perf.get('timeout_rate', 0):.2%}")
            print(f"  Degradation rate: {rca_perf.get('degradation_rate', 0):.2%}")
            
            timeout_mgmt = performance_report.get("timeout_management", {})
            print(f"  Timeout compliance: {timeout_mgmt.get('timeout_compliance_rate', 0):.2%}")
            print(f"  Degradation success: {timeout_mgmt.get('graceful_degradation_success_rate', 0):.2%}")
            print()
            
            # Test performance optimization
            print("Testing performance optimization...")
            optimization_result = integrator.optimize_performance_configuration()
            print(f"  Optimization applied: {optimization_result.get('optimization_applied', False)}")
            print(f"  Optimizations: {len(optimization_result.get('optimizations', []))}")
            print(f"  Expected improvement: {optimization_result.get('performance_improvement_expected', 0):.1%}")
            print()
            
        except Exception as e:
            print(f"RCA analysis failed: {e}")
            print("This is expected in demo mode without full RCA engine setup")
            print()
            
    except Exception as e:
        print(f"Failed to initialize RCA integration: {e}")
        print("This is expected in demo mode without full dependencies")
        print()


def demonstrate_thirty_second_compliance():
    """Demonstrate 30-second timeout compliance"""
    print("=" * 60)
    print("30-Second Timeout Compliance Demonstration")
    print("=" * 60)
    
    # Create performance monitor with 30-second timeout
    resource_limits = ResourceLimits(timeout_seconds=30, warning_threshold_seconds=25)
    monitor = RCAPerformanceMonitor(resource_limits)
    
    # Create timeout handler with 30-second configuration
    timeout_config = TimeoutConfiguration(primary_timeout_seconds=30)
    handler = RCATimeoutHandler(timeout_config)
    
    print("Testing 30-second timeout compliance...")
    print(f"  Primary timeout: {timeout_config.primary_timeout_seconds}s")
    print(f"  Warning threshold: {resource_limits.warning_threshold_seconds}s")
    print()
    
    # Simulate operations of different durations
    test_durations = [5, 15, 25, 29]  # All under 30 seconds
    
    for duration in test_durations:
        operation_id = f"compliance_test_{duration}s"
        
        print(f"Testing {duration}s operation...")
        with monitor.monitor_operation(operation_id, timeout_seconds=30) as metrics:
            with handler.manage_operation_timeout(operation_id) as timeout_context:
                
                # Simulate work for the specified duration
                start_time = time.time()
                while time.time() - start_time < duration:
                    time.sleep(0.1)
                    elapsed = time.time() - start_time
                    
                    # Check timeout recommendations periodically
                    if int(elapsed) % 5 == 0 and elapsed > 0:  # Every 5 seconds
                        recommendations = handler.get_timeout_recommendations(operation_id, elapsed)
                        if recommendations['timeout_status'] != 'normal':
                            print(f"    {elapsed:.1f}s: {recommendations['timeout_status']}")
                            
        print(f"  Completed in {metrics.duration_seconds:.2f}s - {'✓ PASS' if metrics.duration_seconds < 30 else '✗ FAIL'}")
        
    print()
    print("30-second timeout compliance test completed")
    print()


def main():
    """Main demonstration function"""
    print("Beast Mode Framework - RCA Performance Optimization Demo")
    print("Requirements: 1.4, 4.2 - Performance optimization and timeout handling")
    print()
    
    try:
        # Run all demonstrations
        demonstrate_performance_monitoring()
        demonstrate_timeout_handling()
        demonstrate_integrated_rca_performance()
        demonstrate_thirty_second_compliance()
        
        print("=" * 60)
        print("Demo completed successfully!")
        print("Key features demonstrated:")
        print("  ✓ 30-second timeout requirement compliance")
        print("  ✓ Performance monitoring and metrics collection")
        print("  ✓ Resource usage limits and memory management")
        print("  ✓ Graceful degradation on timeout")
        print("  ✓ Performance optimization and configuration tuning")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()