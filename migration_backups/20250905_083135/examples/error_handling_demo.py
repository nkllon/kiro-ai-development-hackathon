#!/usr/bin/env python3
"""
Beast Mode Framework - Error Handling and Graceful Degradation Demo
Demonstrates comprehensive error handling for RCA integration
Requirements: 1.1, 1.4, 4.1 - Error handling, fallback reporting, health monitoring, retry logic
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.beast_mode.testing.error_handler import (
    RCAErrorHandler, DegradationLevel, ErrorCategory, RetryConfiguration
)
from src.beast_mode.testing.rca_integration import TestFailureData
from src.beast_mode.analysis.rca_engine import Failure, FailureCategory


def demo_basic_error_handling():
    """Demonstrate basic error handling capabilities"""
    print("🔧 Demo: Basic Error Handling")
    print("=" * 50)
    
    error_handler = RCAErrorHandler()
    
    # Simulate successful operation
    try:
        with error_handler.handle_rca_operation("demo_success", "demo_component"):
            print("✅ Successful operation completed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    # Simulate failed operation
    try:
        with error_handler.handle_rca_operation("demo_failure", "demo_component"):
            raise Exception("Simulated operation failure")
    except Exception as e:
        print(f"❌ Expected error handled: {e}")
        
    # Show error tracking
    print(f"📊 Total errors handled: {error_handler.total_errors_handled}")
    print(f"📈 Error history entries: {len(error_handler.error_history)}")
    print()


def demo_fallback_reporting():
    """Demonstrate fallback report generation"""
    print("📋 Demo: Fallback Report Generation")
    print("=" * 50)
    
    error_handler = RCAErrorHandler()
    
    # Create sample test failures
    test_failures = [
        TestFailureData(
            test_name="test_demo_failure",
            test_file="demo_test.py",
            failure_type="assertion",
            error_message="AssertionError: Demo test failed",
            stack_trace="Traceback (most recent call last):\n  File 'demo_test.py', line 10",
            test_function="test_demo_failure",
            test_class="TestDemo",
            failure_timestamp=datetime.now(),
            test_context={"demo": True},
            pytest_node_id="demo_test.py::TestDemo::test_demo_failure"
        )
    ]
    
    # Generate fallback report
    fallback_report = error_handler.generate_fallback_report(
        test_failures,
        Exception("RCA engine unavailable")
    )
    
    print(f"📊 Fallback Report Generated:")
    print(f"   • Total failures: {fallback_report.total_failures}")
    print(f"   • Failures analyzed: {fallback_report.failures_analyzed}")
    print(f"   • Critical issues: {len(fallback_report.summary.critical_issues)}")
    print(f"   • Recommendations: {len(fallback_report.recommendations)}")
    print(f"   • Next steps: {len(fallback_report.next_steps)}")
    
    print("\n🔍 Sample recommendations:")
    for i, rec in enumerate(fallback_report.recommendations[:3], 1):
        print(f"   {i}. {rec}")
    print()


def demo_graceful_degradation():
    """Demonstrate graceful degradation system"""
    print("⚡ Demo: Graceful Degradation")
    print("=" * 50)
    
    error_handler = RCAErrorHandler()
    
    # Apply different degradation levels
    degradation_levels = [
        (DegradationLevel.MINIMAL, "High load detected"),
        (DegradationLevel.MODERATE, "Multiple component failures"),
        (DegradationLevel.SEVERE, "Critical system issues"),
        (DegradationLevel.EMERGENCY, "System failure - emergency mode")
    ]
    
    for level, reason in degradation_levels:
        result = error_handler.apply_graceful_degradation(level, reason)
        
        print(f"🔄 Applied {level.name} degradation:")
        print(f"   • Reason: {reason}")
        print(f"   • Success: {result['success']}")
        print(f"   • Actions: {list(result['actions_taken'].keys())}")
        print()
        
    # Show final system state
    print(f"🎯 Final degradation level: {error_handler.degradation_level.name}")
    print(f"🏥 System healthy: {error_handler.is_healthy()}")
    print()


def demo_retry_logic():
    """Demonstrate retry logic with simplified parameters"""
    print("🔄 Demo: Retry Logic")
    print("=" * 50)
    
    error_handler = RCAErrorHandler()
    
    # Simulate operation that succeeds after retries
    attempt_count = 0
    
    def failing_operation():
        nonlocal attempt_count
        attempt_count += 1
        print(f"   🔄 Attempt {attempt_count}")
        
        if attempt_count < 3:
            raise Exception(f"Temporary failure {attempt_count}")
        return f"Success after {attempt_count} attempts"
    
    try:
        result = error_handler.retry_with_simplified_parameters(
            operation=failing_operation,
            original_error=Exception("Original error"),
            max_retries=3
        )
        print(f"✅ Retry successful: {result}")
        print(f"📊 Successful retries: {error_handler.successful_retries}")
    except Exception as e:
        print(f"❌ All retries failed: {e}")
    print()


def demo_health_monitoring():
    """Demonstrate component health monitoring"""
    print("🏥 Demo: Health Monitoring")
    print("=" * 50)
    
    error_handler = RCAErrorHandler()
    
    # Simulate component operations
    components = ["rca_engine", "pattern_library", "report_generator"]
    
    for component in components:
        print(f"📊 Monitoring {component}:")
        
        # Simulate successful operations
        for _ in range(5):
            error_handler.monitor_component_health(component, True, 100.0)
            
        # Simulate some failures
        for _ in range(2):
            error_handler.monitor_component_health(component, False, 1000.0)
            
        health_metrics = error_handler.component_health[component]
        print(f"   • Healthy: {health_metrics.is_healthy}")
        print(f"   • Success rate: {health_metrics.success_rate_last_hour:.2%}")
        print(f"   • Error count: {health_metrics.error_count_last_hour}")
        print()
        
    # Show overall health
    overall_health = error_handler._get_overall_component_health()
    print(f"🎯 Overall system health: {overall_health:.2%}")
    print()


def demo_comprehensive_error_report():
    """Demonstrate comprehensive error reporting"""
    print("📈 Demo: Comprehensive Error Report")
    print("=" * 50)
    
    error_handler = RCAErrorHandler()
    
    # Generate some activity
    error_handler.total_errors_handled = 15
    error_handler.successful_recoveries = 12
    error_handler.fallback_reports_generated = 3
    error_handler.retry_attempts_made = 20
    error_handler.successful_retries = 18
    
    # Apply degradation
    error_handler.apply_graceful_degradation(
        DegradationLevel.MODERATE,
        "Demo degradation for reporting"
    )
    
    # Generate comprehensive report
    error_report = error_handler.get_error_report()
    
    print("📊 Error Handling Summary:")
    summary = error_report["error_handling_summary"]
    print(f"   • Total errors: {summary['total_errors_handled']}")
    print(f"   • Recovery rate: {summary['recovery_rate']:.1%}")
    print(f"   • Degradation level: {summary['current_degradation_level']}")
    
    print("\n🔄 Retry Statistics:")
    retry_stats = error_report["retry_statistics"]
    print(f"   • Retry attempts: {retry_stats['retry_attempts_made']}")
    print(f"   • Success rate: {retry_stats['retry_success_rate']:.1%}")
    
    print("\n🏥 Component Health:")
    for name, health in error_report["component_health"].items():
        status = "✅" if health["is_healthy"] else "❌"
        print(f"   • {name}: {status} ({health['success_rate_last_hour']:.1%})")
    print()


def main():
    """Run all error handling demos"""
    print("🚀 Beast Mode Framework - Error Handling Demo")
    print("=" * 60)
    print("Demonstrating comprehensive error handling and graceful degradation")
    print("Requirements: 1.1, 1.4, 4.1")
    print()
    
    demos = [
        demo_basic_error_handling,
        demo_fallback_reporting,
        demo_graceful_degradation,
        demo_retry_logic,
        demo_health_monitoring,
        demo_comprehensive_error_report
    ]
    
    for i, demo in enumerate(demos, 1):
        try:
            demo()
            if i < len(demos):
                print("⏳ Press Enter to continue to next demo...")
                input()
                print()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
            print()
            
    print("🎉 Error handling demo completed!")
    print("The RCA integration system now has comprehensive error handling:")
    print("   ✅ Automatic error detection and categorization")
    print("   ✅ Fallback reporting when RCA analysis fails")
    print("   ✅ Graceful degradation under system stress")
    print("   ✅ Automatic retry logic with simplified parameters")
    print("   ✅ Real-time health monitoring of all components")
    print("   ✅ Comprehensive error reporting and metrics")


if __name__ == "__main__":
    main()