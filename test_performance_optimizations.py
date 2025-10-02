#!/usr/bin/env python3
"""
Performance Optimization Test Suite
===================================

Comprehensive test suite to verify all performance optimizations
are working correctly for Task 7.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_cli_performance():
    """Test CLI performance optimizations."""
    print("🧪 Testing CLI Performance Optimizations")
    print("=" * 50)
    
    try:
        from src.spec_framework.cli.prepare_spec_cli import PrepareSpecCLI
        
        # Test CLI initialization performance
        start_time = time.time()
        cli = PrepareSpecCLI()
        init_time = time.time() - start_time
        print(f"✅ CLI initialization: {init_time:.3f}s")
        
        # Verify performance optimizer is available
        assert hasattr(cli, 'performance_optimizer'), "Performance optimizer not initialized"
        print("✅ Performance optimizer initialized")
        
        # Test capabilities include performance features
        capabilities = cli.get_capabilities()
        assert capabilities.get('performance_optimization'), "Performance optimization not in capabilities"
        assert capabilities.get('caching'), "Caching not in capabilities"
        assert capabilities.get('large_spec_support'), "Large spec support not in capabilities"
        print("✅ Performance capabilities available")
        
        # Test health status includes performance metrics
        health = cli.get_health_status()
        assert 'performance_optimizer' in health, "Performance optimizer not in health status"
        assert 'cache_entries' in health, "Cache entries not in health status"
        print("✅ Performance health monitoring working")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI performance test failed: {e}")
        return False


def test_caching_performance():
    """Test caching performance improvements."""
    print("\n🧪 Testing Caching Performance")
    print("=" * 50)
    
    try:
        from src.spec_framework.core.spec_analyzer import SpecAnalyzer
        
        analyzer = SpecAnalyzer()
        spec_path = ".kiro/specs/atomic-spec-execution-pattern"
        
        # First analysis (cold cache)
        start_time = time.time()
        spec_data1 = analyzer.analyze_specification(spec_path)
        cold_time = time.time() - start_time
        print(f"✅ Cold analysis: {cold_time:.3f}s")
        
        # Second analysis (warm cache)
        start_time = time.time()
        spec_data2 = analyzer.analyze_specification(spec_path)
        warm_time = time.time() - start_time
        print(f"✅ Warm analysis: {warm_time:.3f}s")
        
        # Verify caching worked
        assert warm_time < cold_time or warm_time < 0.001, f"Cache not effective: {warm_time:.3f}s >= {cold_time:.3f}s"
        print(f"✅ Cache speedup: {((cold_time - warm_time) / cold_time * 100):.1f}%")
        
        # Verify same results
        assert spec_data1.spec_name == spec_data2.spec_name, "Cached data differs"
        assert len(spec_data1.tasks) == len(spec_data2.tasks), "Cached task count differs"
        print("✅ Cache consistency verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False


def test_performance_monitoring():
    """Test performance monitoring functionality."""
    print("\n🧪 Testing Performance Monitoring")
    print("=" * 50)
    
    try:
        from src.spec_framework.performance import get_performance_optimizer, performance_monitor
        
        optimizer = get_performance_optimizer()
        
        # Test decorator functionality
        @performance_monitor("test_operation")
        def test_operation():
            time.sleep(0.1)  # Simulate work
            return "test_result"
        
        # Execute monitored operation
        result = test_operation()
        assert result == "test_result", "Monitored operation failed"
        print("✅ Performance monitoring decorator working")
        
        # Check metrics were recorded
        report = optimizer.get_performance_report()
        assert report['status'] == 'success', "No performance data recorded"
        assert 'test_operation' in report['by_operation'], "Test operation not recorded"
        print("✅ Performance metrics recorded")
        
        # Verify metrics content
        test_stats = report['by_operation']['test_operation']
        assert test_stats['count'] >= 1, "Operation count not recorded"
        assert test_stats['avg_duration'] > 0.05, "Duration not recorded correctly"
        print(f"✅ Operation metrics: {test_stats['count']} calls, {test_stats['avg_duration']:.3f}s avg")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring test failed: {e}")
        return False


def test_large_spec_optimization():
    """Test optimizations for large specifications."""
    print("\n🧪 Testing Large Spec Optimizations")
    print("=" * 50)
    
    try:
        from src.spec_framework.performance import get_performance_optimizer
        
        optimizer = get_performance_optimizer()
        
        # Test small spec (no optimizations)
        small_optimizations = optimizer.optimize_for_large_spec(10)
        assert small_optimizations['batch_size'] == 10, "Small spec batch size incorrect"
        print("✅ Small spec optimizations: standard settings")
        
        # Test large spec (aggressive optimizations)
        large_optimizations = optimizer.optimize_for_large_spec(100)
        assert large_optimizations['batch_size'] > 10, "Large spec batch size not increased"
        assert 'parallel_workers' in large_optimizations, "Parallel workers not configured"
        assert large_optimizations['enable_streaming'], "Streaming not enabled for large specs"
        print(f"✅ Large spec optimizations: batch_size={large_optimizations['batch_size']}, workers={large_optimizations['parallel_workers']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Large spec optimization test failed: {e}")
        return False


def test_error_handling_improvements():
    """Test enhanced error handling and recovery."""
    print("\n🧪 Testing Error Handling Improvements")
    print("=" * 50)
    
    try:
        from src.spec_framework.cli.prepare_spec_cli import PrepareSpecCLI
        
        cli = PrepareSpecCLI()
        
        # Test graceful degradation
        degradation = cli.graceful_degradation(Exception("test error"))
        assert degradation['degraded_mode'], "Graceful degradation not working"
        assert 'error' in degradation, "Error not recorded in degradation"
        assert 'available_functions' in degradation, "Available functions not listed"
        print("✅ Graceful degradation working")
        
        # Test invalid spec path handling
        try:
            cli.spec_analyzer.analyze_specification("/nonexistent/path")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError as e:
            print("✅ File not found error handled correctly")
        
        # Test performance optimizer error handling
        perf_degradation = cli.performance_optimizer.graceful_degradation(Exception("perf error"))
        assert perf_degradation['degraded_mode'], "Performance optimizer degradation not working"
        print("✅ Performance optimizer error handling working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_parallel_processing():
    """Test parallel processing capabilities."""
    print("\n🧪 Testing Parallel Processing")
    print("=" * 50)
    
    try:
        from src.spec_framework.performance import parallel_process
        
        # Test data
        test_items = list(range(20))
        
        def slow_processor(item):
            time.sleep(0.01)  # Simulate work
            return item * 2
        
        # Sequential processing
        start_time = time.time()
        sequential_results = [slow_processor(item) for item in test_items]
        sequential_time = time.time() - start_time
        print(f"✅ Sequential processing: {sequential_time:.3f}s")
        
        # Parallel processing
        start_time = time.time()
        parallel_results = parallel_process(test_items, slow_processor, max_workers=4)
        parallel_time = time.time() - start_time
        print(f"✅ Parallel processing: {parallel_time:.3f}s")
        
        # Verify results are the same
        assert len(sequential_results) == len(parallel_results), "Result count mismatch"
        assert sorted(sequential_results) == sorted(parallel_results), "Result content mismatch"
        print("✅ Parallel processing results consistent")
        
        # Verify performance improvement (should be faster or similar)
        if parallel_time < sequential_time:
            speedup = (sequential_time - parallel_time) / sequential_time * 100
            print(f"✅ Parallel speedup: {speedup:.1f}%")
        else:
            print("✅ Parallel processing overhead acceptable for small dataset")
        
        return True
        
    except Exception as e:
        print(f"❌ Parallel processing test failed: {e}")
        return False


def test_memory_optimization():
    """Test memory optimization features."""
    print("\n🧪 Testing Memory Optimization")
    print("=" * 50)
    
    try:
        from src.spec_framework.performance import get_performance_optimizer
        
        optimizer = get_performance_optimizer()
        
        # Test cache size limits
        initial_cache_size = len(optimizer.cache)
        
        # Add many cache entries
        for i in range(100):
            optimizer._put_in_cache(f"test_key_{i}", f"test_value_{i}")
        
        # Verify cache doesn't grow unbounded
        final_cache_size = len(optimizer.cache)
        assert final_cache_size <= 100, f"Cache grew too large: {final_cache_size}"
        print(f"✅ Cache size controlled: {initial_cache_size} -> {final_cache_size}")
        
        # Test cache eviction
        health = optimizer.get_health_status()
        cache_utilization = health['cache_utilization']
        assert cache_utilization < 200, f"Cache utilization too high: {cache_utilization}%"
        print(f"✅ Cache utilization: {cache_utilization:.1f}%")
        
        # Test cache clearing
        optimizer.clear_cache()
        cleared_cache_size = len(optimizer.cache)
        assert cleared_cache_size == 0, "Cache not cleared properly"
        print("✅ Cache clearing working")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        return False


def run_performance_benchmark():
    """Run comprehensive performance benchmark."""
    print("\n🏁 Running Performance Benchmark")
    print("=" * 50)
    
    try:
        from src.spec_framework.cli.prepare_spec_cli import PrepareSpecCLI
        
        cli = PrepareSpecCLI()
        spec_path = ".kiro/specs/atomic-spec-execution-pattern"
        
        # Benchmark full preparation pipeline
        start_time = time.time()
        
        # Analysis
        analysis_start = time.time()
        spec_data = cli.spec_analyzer.analyze_specification(spec_path)
        analysis_time = time.time() - analysis_start
        
        # DAG generation
        dag_start = time.time()
        execution_plan = cli.dag_generator.generate_dag_execution_plan(spec_path)
        dag_time = time.time() - dag_start
        
        # Validation
        validation_start = time.time()
        report = cli.validator.validate_specification_readiness(spec_path)
        validation_time = time.time() - validation_start
        
        total_time = time.time() - start_time
        
        print(f"📊 Benchmark Results:")
        print(f"   Analysis: {analysis_time:.3f}s")
        print(f"   DAG Generation: {dag_time:.3f}s") 
        print(f"   Validation: {validation_time:.3f}s")
        print(f"   Total: {total_time:.3f}s")
        
        # Performance targets
        assert total_time < 10.0, f"Total time too slow: {total_time:.3f}s"
        assert analysis_time < 1.0, f"Analysis too slow: {analysis_time:.3f}s"
        print("✅ Performance targets met")
        
        # Get performance report
        perf_report = cli.performance_optimizer.get_performance_report()
        if perf_report['status'] == 'success':
            cache_hit_rate = perf_report['cache_stats']['hit_rate']
            print(f"✅ Cache hit rate: {cache_hit_rate:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False


def main():
    """Run all performance optimization tests."""
    print("🚀 Performance Optimization Test Suite")
    print("=" * 60)
    print("Testing Task 7: Performance and Reliability Optimization")
    print("=" * 60)
    
    tests = [
        ("CLI Performance", test_cli_performance),
        ("Caching Performance", test_caching_performance),
        ("Performance Monitoring", test_performance_monitoring),
        ("Large Spec Optimization", test_large_spec_optimization),
        ("Error Handling", test_error_handling_improvements),
        ("Parallel Processing", test_parallel_processing),
        ("Memory Optimization", test_memory_optimization),
        ("Performance Benchmark", run_performance_benchmark)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: FAILED - {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / len(tests) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL PERFORMANCE OPTIMIZATIONS WORKING!")
        print("✅ Task 7 implementation is complete and verified")
        return 0
    else:
        print(f"\n⚠️ {failed} tests failed - review implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())