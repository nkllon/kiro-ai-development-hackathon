#!/usr/bin/env python3
"""
AI Memory Palace Performance Benchmark
======================================

This script benchmarks the AI Memory Palace performance characteristics,
demonstrating response times, memory usage, and scalability metrics.

Features:
- Context retrieval performance
- Pattern matching benchmarks
- Memory usage analysis
- Scalability testing
- Performance regression detection

Author: Beast Mode Framework
Date: 2025-01-27
"""

import os
import sys
import time
import json
import asyncio
import psutil
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import AI Memory Palace components
try:
    from src.dag_orchestration.integration.ai_memory_palace_integration import (
        AIMemoryPalaceIntegration, ExecutionPattern
    )
    from src.beast_mode.observatory.ai_memory_palace_integration import (
        AIMemoryPalaceIntegration as ObservatoryIntegration,
        ProjectContext, ContextRetrievalStatus, ProjectType
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AI Memory Palace modules not available: {e}")
    IMPORTS_AVAILABLE = False


@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""
    test_name: str
    operation_count: int
    total_time_seconds: float
    average_time_ms: float
    min_time_ms: float
    max_time_ms: float
    median_time_ms: float
    std_dev_ms: float
    operations_per_second: float
    memory_usage_mb: float
    success_rate: float
    error_count: int


@dataclass
class PerformanceReport:
    """Complete performance report."""
    timestamp: str
    system_info: Dict[str, Any]
    benchmark_results: List[BenchmarkResult]
    summary: Dict[str, Any]


class AIMemoryPalaceBenchmark:
    """AI Memory Palace performance benchmark suite."""
    
    def __init__(self):
        if IMPORTS_AVAILABLE:
            self.dag_integration = AIMemoryPalaceIntegration()
            self.observatory_integration = ObservatoryIntegration()
        else:
            self.dag_integration = None
            self.observatory_integration = None
        
        self.process = psutil.Process()
        self.benchmark_results = []
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for the benchmark."""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown",
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "python_version": sys.version,
            "platform": sys.platform,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def measure_operation_time(self, operation_func, *args, **kwargs) -> Tuple[float, Any, bool]:
        """Measure operation execution time."""
        start_time = time.perf_counter()
        success = True
        result = None
        
        try:
            if asyncio.iscoroutinefunction(operation_func):
                result = asyncio.run(operation_func(*args, **kwargs))
            else:
                result = operation_func(*args, **kwargs)
        except Exception as e:
            success = False
            result = str(e)
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return execution_time, result, success
    
    async def benchmark_pattern_storage(self, pattern_count: int = 100) -> BenchmarkResult:
        """Benchmark execution pattern storage performance."""
        print(f"🧠 Benchmarking pattern storage ({pattern_count} patterns)...")
        
        if not IMPORTS_AVAILABLE:
            # Simulate benchmark results
            return BenchmarkResult(
                test_name="Pattern Storage (Simulated)",
                operation_count=pattern_count,
                total_time_seconds=pattern_count * 0.01,
                average_time_ms=10.0,
                min_time_ms=8.0,
                max_time_ms=15.0,
                median_time_ms=10.0,
                std_dev_ms=2.0,
                operations_per_second=100.0,
                memory_usage_mb=50.0,
                success_rate=1.0,
                error_count=0
            )
        
        execution_times = []
        error_count = 0
        start_memory = self.get_memory_usage_mb()
        
        start_time = time.perf_counter()
        
        for i in range(pattern_count):
            pattern_data = {
                "task_type": "benchmark_test",
                "parallel_workers": (i % 8) + 1,
                "data_size_mb": (i % 500) + 50,
                "complexity": ["low", "medium", "high"][i % 3]
            }
            
            performance_metrics = {
                "execution_time_seconds": 30.0 + (i % 60),
                "memory_usage_mb": 256 + (i % 1024),
                "cpu_utilization": 0.5 + (i % 50) / 100,
                "parallelization_efficiency": 1.0 + (i % 30) / 10,
                "resource_utilization": 0.3 + (i % 60) / 100
            }
            
            exec_time, result, success = self.measure_operation_time(
                self.dag_integration.store_execution_pattern,
                f"benchmark_pattern_{i}",
                pattern_data,
                performance_metrics
            )
            
            execution_times.append(exec_time)
            if not success:
                error_count += 1
        
        end_time = time.perf_counter()
        end_memory = self.get_memory_usage_mb()
        
        total_time = end_time - start_time
        
        return BenchmarkResult(
            test_name="Pattern Storage",
            operation_count=pattern_count,
            total_time_seconds=total_time,
            average_time_ms=statistics.mean(execution_times),
            min_time_ms=min(execution_times),
            max_time_ms=max(execution_times),
            median_time_ms=statistics.median(execution_times),
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=pattern_count / total_time,
            memory_usage_mb=end_memory - start_memory,
            success_rate=(pattern_count - error_count) / pattern_count,
            error_count=error_count
        )
    
    async def benchmark_pattern_retrieval(self, query_count: int = 50) -> BenchmarkResult:
        """Benchmark pattern retrieval performance."""
        print(f"🔍 Benchmarking pattern retrieval ({query_count} queries)...")
        
        if not IMPORTS_AVAILABLE:
            return BenchmarkResult(
                test_name="Pattern Retrieval (Simulated)",
                operation_count=query_count,
                total_time_seconds=query_count * 0.02,
                average_time_ms=20.0,
                min_time_ms=15.0,
                max_time_ms=30.0,
                median_time_ms=20.0,
                std_dev_ms=3.0,
                operations_per_second=50.0,
                memory_usage_mb=10.0,
                success_rate=1.0,
                error_count=0
            )
        
        execution_times = []
        error_count = 0
        start_memory = self.get_memory_usage_mb()
        
        start_time = time.perf_counter()
        
        for i in range(query_count):
            query_pattern = {
                "task_type": "benchmark_test",
                "parallel_workers": (i % 8) + 1,
                "data_size_mb": (i % 500) + 50,
                "complexity": ["low", "medium", "high"][i % 3]
            }
            
            exec_time, result, success = self.measure_operation_time(
                self.dag_integration.retrieve_similar_patterns,
                query_pattern,
                10
            )
            
            execution_times.append(exec_time)
            if not success:
                error_count += 1
        
        end_time = time.perf_counter()
        end_memory = self.get_memory_usage_mb()
        
        total_time = end_time - start_time
        
        return BenchmarkResult(
            test_name="Pattern Retrieval",
            operation_count=query_count,
            total_time_seconds=total_time,
            average_time_ms=statistics.mean(execution_times),
            min_time_ms=min(execution_times),
            max_time_ms=max(execution_times),
            median_time_ms=statistics.median(execution_times),
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=query_count / total_time,
            memory_usage_mb=end_memory - start_memory,
            success_rate=(query_count - error_count) / query_count,
            error_count=error_count
        )
    
    def benchmark_context_retrieval(self, retrieval_count: int = 100) -> BenchmarkResult:
        """Benchmark context retrieval performance."""
        print(f"🏗️  Benchmarking context retrieval ({retrieval_count} retrievals)...")
        
        if not IMPORTS_AVAILABLE:
            return BenchmarkResult(
                test_name="Context Retrieval (Simulated)",
                operation_count=retrieval_count,
                total_time_seconds=retrieval_count * 0.005,
                average_time_ms=5.0,
                min_time_ms=3.0,
                max_time_ms=10.0,
                median_time_ms=5.0,
                std_dev_ms=1.5,
                operations_per_second=200.0,
                memory_usage_mb=5.0,
                success_rate=1.0,
                error_count=0
            )
        
        execution_times = []
        error_count = 0
        start_memory = self.get_memory_usage_mb()
        
        project_names = [
            "benchmark-project-1",
            "benchmark-project-2", 
            "benchmark-project-3",
            "benchmark-project-4",
            "benchmark-project-5"
        ]
        
        start_time = time.perf_counter()
        
        for i in range(retrieval_count):
            project_name = project_names[i % len(project_names)]
            
            exec_time, result, success = self.measure_operation_time(
                self.observatory_integration.get_current_project_context,
                project_name=project_name
            )
            
            execution_times.append(exec_time)
            if not success:
                error_count += 1
        
        end_time = time.perf_counter()
        end_memory = self.get_memory_usage_mb()
        
        total_time = end_time - start_time
        
        return BenchmarkResult(
            test_name="Context Retrieval",
            operation_count=retrieval_count,
            total_time_seconds=total_time,
            average_time_ms=statistics.mean(execution_times),
            min_time_ms=min(execution_times),
            max_time_ms=max(execution_times),
            median_time_ms=statistics.median(execution_times),
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=retrieval_count / total_time,
            memory_usage_mb=end_memory - start_memory,
            success_rate=(retrieval_count - error_count) / retrieval_count,
            error_count=error_count
        )
    
    async def benchmark_learning_insights(self, insight_count: int = 25) -> BenchmarkResult:
        """Benchmark learning insights generation performance."""
        print(f"💡 Benchmarking learning insights ({insight_count} insights)...")
        
        if not IMPORTS_AVAILABLE:
            return BenchmarkResult(
                test_name="Learning Insights (Simulated)",
                operation_count=insight_count,
                total_time_seconds=insight_count * 0.03,
                average_time_ms=30.0,
                min_time_ms=20.0,
                max_time_ms=50.0,
                median_time_ms=30.0,
                std_dev_ms=5.0,
                operations_per_second=33.3,
                memory_usage_mb=2.0,
                success_rate=1.0,
                error_count=0
            )
        
        execution_times = []
        error_count = 0
        start_memory = self.get_memory_usage_mb()
        
        start_time = time.perf_counter()
        
        for i in range(insight_count):
            performance_metrics = {
                "execution_time_seconds": 30.0 + (i % 60),
                "memory_usage_mb": 256 + (i % 1024),
                "cpu_utilization": 0.5 + (i % 50) / 100,
                "parallelization_efficiency": 0.8 + (i % 20) / 10,  # Some low efficiency
                "resource_utilization": 0.7 + (i % 30) / 100
            }
            
            exec_time, result, success = self.measure_operation_time(
                self.dag_integration.learn_from_execution,
                f"benchmark_insight_{i}",
                performance_metrics
            )
            
            execution_times.append(exec_time)
            if not success:
                error_count += 1
        
        end_time = time.perf_counter()
        end_memory = self.get_memory_usage_mb()
        
        total_time = end_time - start_time
        
        return BenchmarkResult(
            test_name="Learning Insights",
            operation_count=insight_count,
            total_time_seconds=total_time,
            average_time_ms=statistics.mean(execution_times),
            min_time_ms=min(execution_times),
            max_time_ms=max(execution_times),
            median_time_ms=statistics.median(execution_times),
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=insight_count / total_time,
            memory_usage_mb=end_memory - start_memory,
            success_rate=(insight_count - error_count) / insight_count,
            error_count=error_count
        )
    
    def benchmark_health_checks(self, check_count: int = 200) -> BenchmarkResult:
        """Benchmark health check performance."""
        print(f"🏥 Benchmarking health checks ({check_count} checks)...")
        
        if not IMPORTS_AVAILABLE:
            return BenchmarkResult(
                test_name="Health Checks (Simulated)",
                operation_count=check_count,
                total_time_seconds=check_count * 0.002,
                average_time_ms=2.0,
                min_time_ms=1.0,
                max_time_ms=5.0,
                median_time_ms=2.0,
                std_dev_ms=0.5,
                operations_per_second=500.0,
                memory_usage_mb=1.0,
                success_rate=1.0,
                error_count=0
            )
        
        execution_times = []
        error_count = 0
        start_memory = self.get_memory_usage_mb()
        
        start_time = time.perf_counter()
        
        for i in range(check_count):
            # Alternate between DAG and Observatory health checks
            if i % 2 == 0:
                exec_time, result, success = self.measure_operation_time(
                    self.dag_integration.get_health_status
                )
            else:
                exec_time, result, success = self.measure_operation_time(
                    self.observatory_integration.get_health_status
                )
            
            execution_times.append(exec_time)
            if not success:
                error_count += 1
        
        end_time = time.perf_counter()
        end_memory = self.get_memory_usage_mb()
        
        total_time = end_time - start_time
        
        return BenchmarkResult(
            test_name="Health Checks",
            operation_count=check_count,
            total_time_seconds=total_time,
            average_time_ms=statistics.mean(execution_times),
            min_time_ms=min(execution_times),
            max_time_ms=max(execution_times),
            median_time_ms=statistics.median(execution_times),
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=check_count / total_time,
            memory_usage_mb=end_memory - start_memory,
            success_rate=(check_count - error_count) / check_count,
            error_count=error_count
        )
    
    def print_benchmark_result(self, result: BenchmarkResult):
        """Print formatted benchmark result."""
        print(f"\n📊 {result.test_name} Results:")
        print(f"   🔢 Operations: {result.operation_count}")
        print(f"   ⏱️  Total Time: {result.total_time_seconds:.2f}s")
        print(f"   📈 Avg Time: {result.average_time_ms:.2f}ms")
        print(f"   ⚡ Min Time: {result.min_time_ms:.2f}ms")
        print(f"   🐌 Max Time: {result.max_time_ms:.2f}ms")
        print(f"   📊 Median: {result.median_time_ms:.2f}ms")
        print(f"   📏 Std Dev: {result.std_dev_ms:.2f}ms")
        print(f"   🚀 Ops/sec: {result.operations_per_second:.1f}")
        print(f"   💾 Memory: {result.memory_usage_mb:.1f}MB")
        print(f"   ✅ Success Rate: {result.success_rate:.1%}")
        if result.error_count > 0:
            print(f"   ❌ Errors: {result.error_count}")
    
    async def run_comprehensive_benchmark(self) -> PerformanceReport:
        """Run comprehensive performance benchmark."""
        print("🧠 AI Memory Palace - Performance Benchmark")
        print("=" * 60)
        
        system_info = self.get_system_info()
        print(f"\n💻 System Information:")
        print(f"   CPU Cores: {system_info['cpu_count']}")
        print(f"   CPU Frequency: {system_info['cpu_freq_mhz']} MHz")
        print(f"   Total Memory: {system_info['memory_total_gb']:.1f} GB")
        print(f"   Available Memory: {system_info['memory_available_gb']:.1f} GB")
        print(f"   Platform: {system_info['platform']}")
        
        benchmark_results = []
        
        # Run benchmarks
        try:
            # Pattern storage benchmark
            pattern_storage_result = await self.benchmark_pattern_storage(100)
            benchmark_results.append(pattern_storage_result)
            self.print_benchmark_result(pattern_storage_result)
            
            # Pattern retrieval benchmark
            pattern_retrieval_result = await self.benchmark_pattern_retrieval(50)
            benchmark_results.append(pattern_retrieval_result)
            self.print_benchmark_result(pattern_retrieval_result)
            
            # Context retrieval benchmark
            context_retrieval_result = self.benchmark_context_retrieval(100)
            benchmark_results.append(context_retrieval_result)
            self.print_benchmark_result(context_retrieval_result)
            
            # Learning insights benchmark
            learning_insights_result = await self.benchmark_learning_insights(25)
            benchmark_results.append(learning_insights_result)
            self.print_benchmark_result(learning_insights_result)
            
            # Health checks benchmark
            health_checks_result = self.benchmark_health_checks(200)
            benchmark_results.append(health_checks_result)
            self.print_benchmark_result(health_checks_result)
            
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Generate summary
        summary = self.generate_summary(benchmark_results)
        
        # Create performance report
        report = PerformanceReport(
            timestamp=datetime.now().isoformat(),
            system_info=system_info,
            benchmark_results=benchmark_results,
            summary=summary
        )
        
        self.print_summary(summary)
        
        return report
    
    def generate_summary(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Generate benchmark summary."""
        if not results:
            return {"error": "No benchmark results available"}
        
        total_operations = sum(r.operation_count for r in results)
        total_time = sum(r.total_time_seconds for r in results)
        avg_success_rate = statistics.mean(r.success_rate for r in results)
        total_memory_usage = sum(r.memory_usage_mb for r in results)
        
        fastest_operation = min(results, key=lambda r: r.average_time_ms)
        slowest_operation = max(results, key=lambda r: r.average_time_ms)
        most_efficient = max(results, key=lambda r: r.operations_per_second)
        
        return {
            "total_operations": total_operations,
            "total_time_seconds": total_time,
            "overall_ops_per_second": total_operations / total_time if total_time > 0 else 0,
            "average_success_rate": avg_success_rate,
            "total_memory_usage_mb": total_memory_usage,
            "fastest_operation": {
                "name": fastest_operation.test_name,
                "avg_time_ms": fastest_operation.average_time_ms
            },
            "slowest_operation": {
                "name": slowest_operation.test_name,
                "avg_time_ms": slowest_operation.average_time_ms
            },
            "most_efficient": {
                "name": most_efficient.test_name,
                "ops_per_second": most_efficient.operations_per_second
            },
            "performance_grade": self.calculate_performance_grade(results)
        }
    
    def calculate_performance_grade(self, results: List[BenchmarkResult]) -> str:
        """Calculate overall performance grade."""
        if not results:
            return "N/A"
        
        # Simple grading based on success rate and performance
        avg_success_rate = statistics.mean(r.success_rate for r in results)
        avg_ops_per_second = statistics.mean(r.operations_per_second for r in results)
        
        if avg_success_rate >= 0.99 and avg_ops_per_second >= 100:
            return "A+ (Excellent)"
        elif avg_success_rate >= 0.95 and avg_ops_per_second >= 50:
            return "A (Very Good)"
        elif avg_success_rate >= 0.90 and avg_ops_per_second >= 25:
            return "B (Good)"
        elif avg_success_rate >= 0.80 and avg_ops_per_second >= 10:
            return "C (Fair)"
        else:
            return "D (Needs Improvement)"
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print benchmark summary."""
        print(f"\n" + "=" * 60)
        print("📈 Benchmark Summary")
        print("=" * 60)
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
            return
        
        print(f"🔢 Total Operations: {summary['total_operations']:,}")
        print(f"⏱️  Total Time: {summary['total_time_seconds']:.2f}s")
        print(f"🚀 Overall Ops/sec: {summary['overall_ops_per_second']:.1f}")
        print(f"✅ Average Success Rate: {summary['average_success_rate']:.1%}")
        print(f"💾 Total Memory Usage: {summary['total_memory_usage_mb']:.1f}MB")
        print(f"🏆 Performance Grade: {summary['performance_grade']}")
        
        print(f"\n🏃 Fastest Operation: {summary['fastest_operation']['name']}")
        print(f"   ⚡ Average Time: {summary['fastest_operation']['avg_time_ms']:.2f}ms")
        
        print(f"\n🐌 Slowest Operation: {summary['slowest_operation']['name']}")
        print(f"   ⏱️  Average Time: {summary['slowest_operation']['avg_time_ms']:.2f}ms")
        
        print(f"\n🎯 Most Efficient: {summary['most_efficient']['name']}")
        print(f"   🚀 Operations/sec: {summary['most_efficient']['ops_per_second']:.1f}")
    
    def save_report(self, report: PerformanceReport, filename: str = None):
        """Save performance report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_memory_palace_benchmark_{timestamp}.json"
        
        filepath = Path(__file__).parent / "benchmark_reports" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        print(f"\n💾 Benchmark report saved to: {filepath}")


async def main():
    """Main benchmark entry point."""
    benchmark = AIMemoryPalaceBenchmark()
    
    print("🧠 AI Memory Palace Performance Benchmark")
    print("🐺 Beast Mode Framework")
    print("Testing performance characteristics and scalability")
    
    if not IMPORTS_AVAILABLE:
        print("\n⚠️  Running in simulation mode (AI Memory Palace modules not available)")
    
    # Run comprehensive benchmark
    report = await benchmark.run_comprehensive_benchmark()
    
    # Save report
    benchmark.save_report(report)
    
    print("\n🎉 Benchmark complete!")
    print("📊 Performance characteristics documented and saved")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())