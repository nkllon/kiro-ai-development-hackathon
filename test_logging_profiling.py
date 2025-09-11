#!/usr/bin/env python3
"""
Test script for logging and profiling infrastructure

Tests the new logging, profiling, and debugging capabilities.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from devpost_integration.logging_infrastructure import (
    LoggingInfrastructure, LoggingConfig, LogLevel, 
    get_logging_infrastructure, initialize_logging
)
from devpost_integration.performance_profiler import (
    PerformanceProfiler, get_performance_profiler, 
    profile_operation, measure_execution_time
)
from devpost_integration.debugging_engine import (
    DebuggingEngine, DebugLevel, get_debugging_engine,
    enable_debug_mode, trace_execution
)


def test_logging_infrastructure():
    """Test logging infrastructure"""
    print("Testing Logging Infrastructure...")
    
    # Initialize logging
    config = LoggingConfig(
        log_level="DEBUG",
        log_format="JSON",
        enable_console=True,
        enable_file=True
    )
    initialize_logging(config)
    
    logging = get_logging_infrastructure()
    
    # Test basic logging
    logging.log_event(LogLevel.INFO, "Test info message", {"test": "data"})
    logging.log_event(LogLevel.WARNING, "Test warning message", {"warning": "test"})
    logging.log_event(LogLevel.ERROR, "Test error message", {"error": "test"})
    
    # Test performance logging
    logging.log_performance("test_operation", 1.5, {"memory": 1024, "cpu": 50.0})
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logging.log_error(e, {"context": "test_error_logging"})
    
    print("✅ Logging Infrastructure test completed")


def test_performance_profiler():
    """Test performance profiler"""
    print("Testing Performance Profiler...")
    
    profiler = get_performance_profiler()
    
    # Test context manager
    with profiler.profile_operation("test_operation", {"test": "data"}) as context:
        time.sleep(0.1)  # Simulate work
        print(f"  Profiling context: {context.operation_id}")
    
    # Test decorator
    @measure_execution_time("decorated_function")
    def test_function():
        time.sleep(0.05)
        return "test result"
    
    result = test_function()
    print(f"  Decorated function result: {result}")
    
    # Test metrics
    metrics = profiler.get_performance_metrics()
    print(f"  Performance metrics: {len(metrics)} operations tracked")
    
    # Test system metrics
    system_metrics = profiler.get_system_metrics()
    print(f"  System metrics: {system_metrics}")
    
    print("✅ Performance Profiler test completed")


def test_debugging_engine():
    """Test debugging engine"""
    print("Testing Debugging Engine...")
    
    debug_engine = get_debugging_engine()
    
    # Test debug mode
    enable_debug_mode("test_module", DebugLevel.DETAILED)
    
    # Test execution tracing
    trace = trace_execution("test_operation")
    debug_engine.add_trace_step(trace, "step1", "SUCCESS", {"data": "test"})
    debug_engine.add_trace_step(trace, "step2", "SUCCESS", {"data": "test2"})
    debug_engine.complete_trace(trace)
    
    # Test issue diagnosis
    diagnostic = debug_engine.diagnose_issue("Test error occurred")
    print(f"  Diagnostic result: {diagnostic.severity} - {diagnostic.root_cause}")
    
    # Test system state
    system_state = debug_engine.get_system_state()
    print(f"  System state modules: {len(system_state.get('modules', {}))}")
    
    print("✅ Debugging Engine test completed")


def test_integration():
    """Test integration between all components"""
    print("Testing Integration...")
    
    logging = get_logging_infrastructure()
    profiler = get_performance_profiler()
    debug_engine = get_debugging_engine()
    
    # Test integrated workflow
    with profiler.profile_operation("integrated_test", {"integration": "test"}):
        logging.log_event(LogLevel.INFO, "Starting integrated test", {"test": "integration"})
        
        # Simulate some work
        time.sleep(0.1)
        
        # Enable debug mode
        enable_debug_mode("integration_test", DebugLevel.BASIC)
        
        # Get debug info
        debug_info = debug_engine.get_debug_info("integration_test")
        if debug_info:
            print(f"  Debug info collected for: {debug_info.module_id}")
        
        logging.log_event(LogLevel.INFO, "Integrated test completed", {"test": "integration"})
    
    print("✅ Integration test completed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING LOGGING AND PROFILING INFRASTRUCTURE")
    print("=" * 60)
    
    try:
        test_logging_infrastructure()
        print()
        
        test_performance_profiler()
        print()
        
        test_debugging_engine()
        print()
        
        test_integration()
        print()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
