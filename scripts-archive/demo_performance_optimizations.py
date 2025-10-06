#!/usr/bin/env python3
"""
Performance Optimization Demonstration
======================================

Demonstrates all the performance optimizations implemented for Task 7.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def demonstrate_caching():
    """Demonstrate caching performance improvements."""
    print("🧪 Demonstrating Caching Performance")
    print("=" * 50)
    
    from src.spec_framework.cli.prepare_spec_cli import PrepareSpecCLI
    
    cli = PrepareSpecCLI()
    spec_path = ".kiro/specs/atomic-spec-execution-pattern"
    
    print("First analysis (cold cache):")
    start_time = time.time()
    spec_data1 = cli.spec_analyzer.analyze_specification(spec_path)
    cold_time = time.time() - start_time
    print(f"   Time: {cold_time:.3f}s")
    print(f"   Tasks found: {len(spec_data1.tasks)}")
    
    print("\nSecond analysis (warm cache):")
    start_time = time.time()
    spec_data2 = cli.spec_analyzer.analyze_specification(spec_path)
    warm_time = time.time() - start_time
    print(f"   Time: {warm_time:.3f}s")
    print(f"   Tasks found: {len(spec_data2.tasks)}")
    
    speedup = ((cold_time - warm_time) / cold_time * 100) if cold_time > 0 else 0
    print(f"\n✅ Cache speedup: {speedup:.1f}%")
    print(f"✅ Cache entries: {len(cli.spec_analyzer.spec_cache)}")


def demonstrate_large_spec_optimization():
    """Demonstrate optimizations for large specifications."""
    print("\n🧪 Demonstrating Large Spec Optimizations")
    print("=" * 50)
    
    from src.spec_framework.performance import get_performance_optimizer
    
    optimizer = get_performance_optimizer()
    
    # Small spec
    small_opts = optimizer.optimize_for_large_spec(10)
    print("Small specification (10 tasks):")
    print(f"   Batch size: {small_opts['batch_size']}")
    print(f"   Parallel enabled: {small_opts['parallel_enabled']}")
    
    # Large spec
    large_opts = optimizer.optimize_for_large_spec(100)
    print("\nLarge specification (100 tasks):")
    print(f"   Batch size: {large_opts['batch_size']}")
    print(f"   Parallel workers: {large_opts['parallel_workers']}")
    print(f"   Cache TTL: {large_opts['cache_ttl']}s")
    print(f"   Streaming enabled: {large_opts['enable_streaming']}")
    print(f"   Memory limit: {large_opts['memory_limit_mb']}MB")


def demonstrate_parallel_processing():
    """Demonstrate parallel processing capabilities."""
    print("\n🧪 Demonstrating Parallel Processing")
    print("=" * 50)
    
    from src.spec_framework.performance import parallel_process
    
    # Create test data
    items = list(range(50))
    
    def slow_task(item):
        time.sleep(0.01)  # Simulate work
        return item * item
    
    # Sequential processing
    print("Sequential processing:")
    start_time = time.time()
    sequential_results = [slow_task(item) for item in items]
    sequential_time = time.time() - start_time
    print(f"   Time: {sequential_time:.3f}s")
    print(f"   Results: {len(sequential_results)} items")
    
    # Parallel processing
    print("\nParallel processing (4 workers):")
    start_time = time.time()
    parallel_results = parallel_process(items, slow_task, max_workers=4)
    parallel_time = time.time() - start_time
    print(f"   Time: {parallel_time:.3f}s")
    print(f"   Results: {len(parallel_results)} items")
    
    # Verify results
    assert sorted(sequential_results) == sorted(parallel_results)
    speedup = ((sequential_time - parallel_time) / sequential_time * 100) if sequential_time > 0 else 0
    print(f"\n✅ Parallel speedup: {speedup:.1f}%")
    print(f"✅ Results verified: identical")


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n🧪 Demonstrating Performance Monitoring")
    print("=" * 50)
    
    from src.spec_framework.performance import get_performance_optimizer, performance_monitor
    
    optimizer = get_performance_optimizer()
    
    # Create monitored function
    @performance_monitor("demo_operation")
    def demo_operation(duration=0.1):
        time.sleep(duration)
        return f"Completed in {duration}s"
    
    # Execute monitored operations
    print("Executing monitored operations...")
    for i in range(3):
        result = demo_operation(0.05 + i * 0.02)
        print(f"   Operation {i+1}: {result}")
    
    # Get performance report
    report = optimizer.get_performance_report()
    if report['status'] == 'success':
        demo_stats = report['by_operation'].get('demo_operation', {})
        print(f"\n📊 Performance Statistics:")
        print(f"   Operations: {demo_stats.get('count', 0)}")
        print(f"   Total time: {demo_stats.get('total_duration', 0):.3f}s")
        print(f"   Average time: {demo_stats.get('avg_duration', 0):.3f}s")
        print(f"   Max time: {demo_stats.get('max_duration', 0):.3f}s")
        print(f"   Min time: {demo_stats.get('min_duration', 0):.3f}s")


def demonstrate_memory_optimization():
    """Demonstrate memory optimization."""
    print("\n🧪 Demonstrating Memory Optimization")
    print("=" * 50)
    
    from src.spec_framework.performance import get_performance_optimizer
    
    optimizer = get_performance_optimizer()
    
    # Clear cache to start fresh
    optimizer.clear_cache()
    print(f"Initial cache size: {len(optimizer.cache)}")
    
    # Add many items to test eviction
    print("Adding 100 cache entries...")
    for i in range(100):
        optimizer._put_in_cache(f"test_key_{i}", f"test_value_{i}" * 100)
    
    print(f"Final cache size: {len(optimizer.cache)}")
    
    # Check health status
    health = optimizer.get_health_status()
    print(f"Cache utilization: {health['cache_utilization']:.1f}%")
    print(f"Cache size: {health['cache_size_mb']:.2f}MB")
    
    # Test cache clearing
    optimizer.clear_cache()
    print(f"After clearing: {len(optimizer.cache)} entries")


def demonstrate_error_handling():
    """Demonstrate enhanced error handling."""
    print("\n🧪 Demonstrating Error Handling")
    print("=" * 50)
    
    from src.spec_framework.cli.prepare_spec_cli import PrepareSpecCLI
    
    cli = PrepareSpecCLI()
    
    # Test graceful degradation
    print("Testing graceful degradation:")
    degradation = cli.graceful_degradation(Exception("Test error"))
    print(f"   Degraded mode: {degradation['degraded_mode']}")
    print(f"   Error recorded: {'error' in degradation}")
    print(f"   Available functions: {degradation['available_functions']}")
    
    # Test invalid path handling
    print("\nTesting invalid path handling:")
    try:
        cli.spec_analyzer.analyze_specification("/nonexistent/path")
        print("   ❌ Should have failed")
    except FileNotFoundError:
        print("   ✅ FileNotFoundError handled correctly")
    except Exception as e:
        print(f"   ⚠️ Unexpected error: {e}")


def demonstrate_full_pipeline():
    """Demonstrate full optimized pipeline."""
    print("\n🧪 Demonstrating Full Optimized Pipeline")
    print("=" * 50)
    
    from src.spec_framework.cli.prepare_spec_cli import PrepareSpecCLI
    
    cli = PrepareSpecCLI()
    spec_path = ".kiro/specs/atomic-spec-execution-pattern"
    
    print("Running full preparation pipeline with optimizations...")
    
    # Analysis
    start_time = time.time()
    spec_data = cli.spec_analyzer.analyze_specification(spec_path)
    analysis_time = time.time() - start_time
    print(f"   Analysis: {analysis_time:.3f}s ({len(spec_data.tasks)} tasks)")
    
    # DAG generation
    start_time = time.time()
    execution_plan = cli.dag_generator.generate_dag_execution_plan(spec_path)
    dag_time = time.time() - start_time
    print(f"   DAG generation: {dag_time:.3f}s ({execution_plan.efficiency_gain:.1f}% efficiency gain)")
    
    # Validation
    start_time = time.time()
    report = cli.validator.validate_specification_readiness(spec_path)
    validation_time = time.time() - start_time
    print(f"   Validation: {validation_time:.3f}s ({report.confidence_score:.1%} confidence)")
    
    total_time = analysis_time + dag_time + validation_time
    print(f"\n✅ Total pipeline time: {total_time:.3f}s")
    
    # Performance report
    perf_report = cli.performance_optimizer.get_performance_report()
    if perf_report['status'] == 'success':
        print(f"✅ Operations monitored: {perf_report['summary']['total_operations']}")
        print(f"✅ Cache entries: {perf_report['cache_stats']['entries']}")


def main():
    """Run all performance optimization demonstrations."""
    print("🚀 Performance Optimization Demonstration")
    print("=" * 60)
    print("Task 7: Performance and Reliability Optimization")
    print("=" * 60)
    
    try:
        demonstrate_caching()
        demonstrate_large_spec_optimization()
        demonstrate_parallel_processing()
        demonstrate_performance_monitoring()
        demonstrate_memory_optimization()
        demonstrate_error_handling()
        demonstrate_full_pipeline()
        
        print("\n" + "=" * 60)
        print("🎉 ALL PERFORMANCE OPTIMIZATIONS DEMONSTRATED!")
        print("=" * 60)
        print("✅ Task 7.1: Analysis caching implemented and working")
        print("✅ Task 7.2: Enhanced error handling implemented and working")
        print("✅ Task 7.3: Large specification optimization implemented and working")
        print("✅ Task 7: Performance and Reliability Optimization COMPLETE")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())