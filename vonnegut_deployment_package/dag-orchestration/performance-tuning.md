# DAG Orchestration Performance Tuning Guide

## Overview

This guide provides comprehensive recommendations for optimizing DAG orchestration performance across different dimensions: execution speed, resource utilization, cost efficiency, and scalability.

## Performance Fundamentals

### Key Performance Metrics

1. **Execution Time**: Total time from DAG start to completion
2. **Throughput**: Tasks completed per unit time
3. **Resource Utilization**: CPU, memory, I/O, and network usage
4. **Parallelization Efficiency**: Actual speedup vs theoretical maximum
5. **Cost Efficiency**: Performance per dollar (especially for LLM tasks)

### Performance Measurement

```python
import time
from dag_orchestration.core.performance_monitor import PerformanceMonitor

def measure_dag_performance(orchestrator, tasks):
    """Comprehensive performance measurement."""
    
    monitor = PerformanceMonitor()
    
    # Start monitoring
    monitor.start_monitoring()
    start_time = time.time()
    
    # Execute DAG
    result = orchestrator.execute_dag(tasks)
    
    # Stop monitoring
    end_time = time.time()
    monitor.stop_monitoring()
    
    # Calculate metrics
    metrics = {
        'total_execution_time': end_time - start_time,
        'task_count': len(tasks),
        'throughput': len(tasks) / (end_time - start_time),
        'success_rate': len(result.completed_tasks) / len(tasks),
        'resource_usage': monitor.get_resource_summary(),
        'parallelization_efficiency': calculate_parallelization_efficiency(result)
    }
    
    return metrics

def calculate_parallelization_efficiency(result):
    """Calculate how efficiently parallel resources were used."""
    total_task_time = sum(task.duration for task in result.completed_tasks)
    actual_execution_time = result.execution_time
    
    if actual_execution_time > 0:
        return total_task_time / actual_execution_time
    return 0
```

## Execution Strategy Optimization

### 1. Choosing the Right Execution Strategy

```python
from dag_orchestration.core.execution_strategy import ExecutionStrategy

# For CPU-intensive tasks with good parallelization
execution_engine = ParallelExecutionEngine(
    max_workers=8,
    execution_strategy=ExecutionStrategy.PARALLEL
)

# For mixed workloads with varying resource requirements
execution_engine = ParallelExecutionEngine(
    max_workers=6,
    execution_strategy=ExecutionStrategy.ADAPTIVE
)

# For resource-constrained environments
execution_engine = ParallelExecutionEngine(
    max_workers=2,
    execution_strategy=ExecutionStrategy.CONSERVATIVE
)
```

### 2. Dynamic Worker Adjustment

```python
class AdaptiveExecutionEngine(ParallelExecutionEngine):
    """Execution engine that adapts worker count based on performance."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.performance_history = []
        self.adjustment_interval = 30  # seconds
        
    def adjust_workers_dynamically(self):
        """Adjust worker count based on recent performance."""
        
        current_metrics = self.get_current_metrics()
        
        # Increase workers if CPU utilization is low and tasks are queued
        if (current_metrics.cpu_usage < 60 and 
            current_metrics.queued_tasks > 0 and 
            self.max_workers < 12):
            
            self.max_workers += 1
            print(f"🔧 Increased workers to {self.max_workers}")
            
        # Decrease workers if resource usage is high
        elif (current_metrics.cpu_usage > 85 or 
              current_metrics.memory_usage > 80):
            
            self.max_workers = max(1, self.max_workers - 1)
            print(f"🔧 Decreased workers to {self.max_workers}")
```

### 3. Task Batching Optimization

```python
def optimize_task_batching(tasks, batch_size=None):
    """Optimize task execution through intelligent batching."""
    
    if batch_size is None:
        # Calculate optimal batch size based on task characteristics
        avg_task_duration = estimate_average_task_duration(tasks)
        if avg_task_duration < 10:  # Short tasks
            batch_size = 10
        elif avg_task_duration < 60:  # Medium tasks
            batch_size = 5
        else:  # Long tasks
            batch_size = 2
    
    # Group independent tasks into batches
    batched_tasks = []
    current_batch = []
    
    for task in tasks:
        if len(current_batch) < batch_size:
            current_batch.append(task)
        else:
            # Create batch task
            batch_task = create_batch_task(current_batch)
            batched_tasks.append(batch_task)
            current_batch = [task]
    
    # Add remaining tasks
    if current_batch:
        batch_task = create_batch_task(current_batch)
        batched_tasks.append(batch_task)
    
    return batched_tasks
```

## Resource Optimization

### 1. Memory Management

```python
from dag_orchestration.core.resource_limits import ResourceLimits

def optimize_memory_usage():
    """Configure optimal memory usage patterns."""
    
    # Set conservative memory limits
    resource_limits = ResourceLimits(
        max_memory_percent=70,  # Leave 30% for system
        memory_cleanup_threshold=60,  # Cleanup at 60%
        max_memory_per_task=1024,  # 1GB per task max
        enable_memory_monitoring=True
    )
    
    return resource_limits

class MemoryOptimizedExecutor:
    """Executor with advanced memory management."""
    
    def __init__(self):
        self.memory_pool = MemoryPool(max_size_gb=8)
        self.task_memory_cache = {}
        
    def execute_task_with_memory_management(self, task):
        """Execute task with optimized memory usage."""
        
        # Estimate memory requirements
        estimated_memory = self.estimate_task_memory(task)
        
        # Wait for memory availability
        self.memory_pool.wait_for_availability(estimated_memory)
        
        try:
            # Allocate memory
            memory_handle = self.memory_pool.allocate(estimated_memory)
            
            # Execute task
            result = self.execute_task(task, memory_handle)
            
            return result
            
        finally:
            # Always release memory
            self.memory_pool.release(memory_handle)
    
    def estimate_task_memory(self, task):
        """Estimate memory requirements for a task."""
        
        # Use historical data if available
        if task.id in self.task_memory_cache:
            return self.task_memory_cache[task.id] * 1.2  # 20% buffer
        
        # Default estimates based on task type
        if task.executor == "llm":
            return 512  # MB
        elif "large-data" in task.command:
            return 2048  # MB
        else:
            return 256  # MB
```

### 2. CPU Optimization

```python
def optimize_cpu_usage(tasks):
    """Optimize CPU usage through intelligent task scheduling."""
    
    # Classify tasks by CPU intensity
    cpu_intensive = []
    io_intensive = []
    mixed_tasks = []
    
    for task in tasks:
        cpu_score = estimate_cpu_intensity(task)
        if cpu_score > 0.8:
            cpu_intensive.append(task)
        elif cpu_score < 0.3:
            io_intensive.append(task)
        else:
            mixed_tasks.append(task)
    
    # Create optimized execution plan
    execution_plan = []
    
    # Run I/O intensive tasks first (can run many in parallel)
    if io_intensive:
        execution_plan.append({
            'tasks': io_intensive,
            'max_workers': min(len(io_intensive), 12),
            'cpu_affinity': None
        })
    
    # Run CPU intensive tasks with limited parallelism
    if cpu_intensive:
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        execution_plan.append({
            'tasks': cpu_intensive,
            'max_workers': cpu_count,
            'cpu_affinity': list(range(cpu_count))
        })
    
    # Run mixed tasks with balanced approach
    if mixed_tasks:
        execution_plan.append({
            'tasks': mixed_tasks,
            'max_workers': 6,
            'cpu_affinity': None
        })
    
    return execution_plan

def estimate_cpu_intensity(task):
    """Estimate CPU intensity of a task (0.0 to 1.0)."""
    
    # Analyze command for CPU-intensive patterns
    cpu_indicators = [
        'compile', 'build', 'process', 'calculate', 'compute',
        'encode', 'decode', 'compress', 'decompress', 'hash'
    ]
    
    io_indicators = [
        'download', 'upload', 'copy', 'move', 'sync',
        'backup', 'restore', 'fetch', 'send'
    ]
    
    command_lower = task.command.lower()
    
    cpu_score = sum(1 for indicator in cpu_indicators if indicator in command_lower)
    io_score = sum(1 for indicator in io_indicators if indicator in command_lower)
    
    if cpu_score + io_score == 0:
        return 0.5  # Default to mixed
    
    return cpu_score / (cpu_score + io_score)
```

### 3. I/O Optimization

```python
def optimize_io_performance():
    """Configure optimal I/O performance."""
    
    # Use async I/O for file operations
    import asyncio
    import aiofiles
    
    async def async_file_task(file_path, operation):
        """Perform file operations asynchronously."""
        
        if operation == 'read':
            async with aiofiles.open(file_path, 'r') as f:
                return await f.read()
        elif operation == 'write':
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(data)
    
    # Batch file operations
    def batch_file_operations(file_tasks):
        """Batch multiple file operations for efficiency."""
        
        # Group by operation type
        read_tasks = [t for t in file_tasks if t.operation == 'read']
        write_tasks = [t for t in file_tasks if t.operation == 'write']
        
        # Execute in batches
        results = []
        
        # Parallel reads
        if read_tasks:
            read_results = asyncio.run(
                asyncio.gather(*[async_file_task(t.file_path, 'read') for t in read_tasks])
            )
            results.extend(read_results)
        
        # Sequential writes (to avoid conflicts)
        for write_task in write_tasks:
            result = asyncio.run(async_file_task(write_task.file_path, 'write'))
            results.append(result)
        
        return results
```

## DAG Structure Optimization

### 1. Dependency Minimization

```python
def optimize_dag_dependencies(tasks):
    """Minimize dependencies to maximize parallelization."""
    
    # Analyze dependency graph
    dependency_graph = build_dependency_graph(tasks)
    
    # Find unnecessary dependencies
    unnecessary_deps = find_transitive_dependencies(dependency_graph)
    
    # Remove transitive dependencies
    optimized_tasks = []
    for task in tasks:
        optimized_deps = [
            dep for dep in task.dependencies 
            if dep not in unnecessary_deps.get(task.id, [])
        ]
        
        optimized_task = TaskDefinition(
            id=task.id,
            name=task.name,
            command=task.command,
            dependencies=optimized_deps,  # Reduced dependencies
            **{k: v for k, v in task.__dict__.items() 
               if k not in ['id', 'name', 'command', 'dependencies']}
        )
        optimized_tasks.append(optimized_task)
    
    return optimized_tasks

def find_transitive_dependencies(graph):
    """Find dependencies that are implied by other dependencies."""
    
    transitive_deps = {}
    
    for task_id, direct_deps in graph.items():
        transitive_deps[task_id] = []
        
        for dep in direct_deps:
            # Find all dependencies of this dependency
            indirect_deps = get_all_dependencies(graph, dep)
            
            # Any direct dependency that's also an indirect dependency is transitive
            for other_dep in direct_deps:
                if other_dep != dep and other_dep in indirect_deps:
                    transitive_deps[task_id].append(other_dep)
    
    return transitive_deps
```

### 2. Critical Path Optimization

```python
def optimize_critical_path(tasks):
    """Optimize the critical path for minimum execution time."""
    
    # Calculate critical path
    critical_path = calculate_critical_path(tasks)
    
    # Optimize critical path tasks
    optimized_tasks = []
    
    for task in tasks:
        if task.id in critical_path:
            # Give critical path tasks higher priority and more resources
            optimized_task = TaskDefinition(
                id=task.id,
                name=task.name,
                command=task.command,
                dependencies=task.dependencies,
                priority=10,  # High priority
                resource_requirements={
                    'cpu': min(4, task.resource_requirements.get('cpu', 1) * 2),
                    'memory': min(4096, task.resource_requirements.get('memory', 512) * 2)
                },
                timeout=task.timeout * 1.5  # More generous timeout
            )
        else:
            # Non-critical tasks get standard treatment
            optimized_task = task
        
        optimized_tasks.append(optimized_task)
    
    return optimized_tasks

def calculate_critical_path(tasks):
    """Calculate the critical path through the DAG."""
    
    # Build dependency graph with durations
    graph = {}
    durations = {}
    
    for task in tasks:
        graph[task.id] = task.dependencies
        durations[task.id] = estimate_task_duration(task)
    
    # Find longest path (critical path)
    def longest_path_to(task_id, memo={}):
        if task_id in memo:
            return memo[task_id]
        
        if not graph[task_id]:  # No dependencies
            memo[task_id] = durations[task_id]
            return durations[task_id]
        
        max_dep_path = max(longest_path_to(dep, memo) for dep in graph[task_id])
        memo[task_id] = max_dep_path + durations[task_id]
        return memo[task_id]
    
    # Find the task with the longest path
    path_lengths = {task_id: longest_path_to(task_id) for task_id in graph}
    critical_end = max(path_lengths, key=path_lengths.get)
    
    # Reconstruct critical path
    critical_path = []
    current = critical_end
    
    while current:
        critical_path.append(current)
        
        # Find the dependency with the longest path
        if graph[current]:
            current = max(graph[current], key=lambda dep: path_lengths[dep])
        else:
            current = None
    
    return list(reversed(critical_path))
```

## LLM Performance Optimization

### 1. Cost-Performance Optimization

```python
class CostOptimizedLLMManager:
    """LLM manager optimized for cost-performance ratio."""
    
    def __init__(self, cost_budget, performance_targets):
        self.cost_budget = cost_budget
        self.performance_targets = performance_targets
        self.provider_performance = {}
        self.cost_tracking = {}
        
    def select_optimal_llm(self, task):
        """Select LLM based on cost-performance optimization."""
        
        # Calculate cost-performance score for each provider
        scores = {}
        
        for provider, config in self.available_llms.items():
            # Estimate cost
            estimated_cost = self.estimate_task_cost(task, provider)
            
            # Estimate performance (quality * speed)
            estimated_performance = self.estimate_task_performance(task, provider)
            
            # Calculate cost-performance ratio
            if estimated_cost > 0:
                scores[provider] = estimated_performance / estimated_cost
            else:
                scores[provider] = float('inf')  # Free providers get max score
        
        # Select provider with best cost-performance ratio
        best_provider = max(scores, key=scores.get)
        
        return best_provider
    
    def estimate_task_cost(self, task, provider):
        """Estimate cost for executing task with specific provider."""
        
        provider_config = self.available_llms[provider]
        
        if provider_config['cost_model'] == 'subscription':
            return 0.0  # No marginal cost
        
        # Estimate tokens based on task complexity
        estimated_tokens = len(task.command.split()) * 10  # Rough estimate
        
        return estimated_tokens * provider_config.get('cost_per_token', 0.001)
    
    def estimate_task_performance(self, task, provider):
        """Estimate performance for task with specific provider."""
        
        # Use historical performance data if available
        if provider in self.provider_performance:
            historical = self.provider_performance[provider]
            return historical.get('quality', 0.8) * historical.get('speed', 0.8)
        
        # Default performance estimates
        performance_map = {
            'cursor': 0.9,    # High performance, subscription model
            'claude': 0.95,   # Highest quality, pay-per-token
            'kiro': 0.7       # Good performance, subscription model
        }
        
        return performance_map.get(provider, 0.5)
```

### 2. LLM Caching and Reuse

```python
class CachedLLMExecutor:
    """LLM executor with intelligent caching."""
    
    def __init__(self):
        self.response_cache = {}
        self.pattern_cache = {}
        
    def execute_with_caching(self, task):
        """Execute LLM task with caching optimization."""
        
        # Generate cache key based on task content
        cache_key = self.generate_cache_key(task)
        
        # Check for exact match
        if cache_key in self.response_cache:
            print(f"🎯 Cache hit for task {task.id}")
            return self.response_cache[cache_key]
        
        # Check for similar patterns
        similar_response = self.find_similar_response(task)
        if similar_response:
            print(f"🎯 Pattern match for task {task.id}")
            # Adapt similar response instead of full execution
            return self.adapt_response(similar_response, task)
        
        # Execute task normally
        response = self.execute_llm_task(task)
        
        # Cache the response
        self.response_cache[cache_key] = response
        self.update_pattern_cache(task, response)
        
        return response
    
    def generate_cache_key(self, task):
        """Generate cache key for task."""
        import hashlib
        
        content = f"{task.command}:{task.executor}:{task.description}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def find_similar_response(self, task):
        """Find similar cached responses."""
        
        task_keywords = set(task.command.lower().split())
        
        best_match = None
        best_similarity = 0.0
        
        for cached_task, response in self.pattern_cache.items():
            cached_keywords = set(cached_task.lower().split())
            
            # Calculate similarity (Jaccard index)
            intersection = task_keywords & cached_keywords
            union = task_keywords | cached_keywords
            
            if union:
                similarity = len(intersection) / len(union)
                
                if similarity > 0.7 and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = response
        
        return best_match
```

### 3. Parallel LLM Execution

```python
def optimize_llm_parallelization(llm_tasks):
    """Optimize parallel execution of LLM tasks."""
    
    # Group tasks by provider to avoid rate limiting
    provider_groups = {}
    
    for task in llm_tasks:
        provider = select_llm_for_task(task)
        if provider not in provider_groups:
            provider_groups[provider] = []
        provider_groups[provider].append(task)
    
    # Execute each provider group with appropriate concurrency
    execution_plans = []
    
    for provider, tasks in provider_groups.items():
        # Set concurrency limits based on provider
        if provider == 'cursor':
            max_concurrent = 4  # Subscription model, higher limit
        elif provider == 'claude':
            max_concurrent = 2  # Pay-per-token, rate limited
        else:
            max_concurrent = 3  # Default
        
        execution_plans.append({
            'provider': provider,
            'tasks': tasks,
            'max_concurrent': max_concurrent,
            'rate_limit_delay': 1.0 if provider == 'claude' else 0.1
        })
    
    return execution_plans
```

## Monitoring and Profiling

### 1. Real-Time Performance Monitoring

```python
class PerformanceMonitor:
    """Real-time performance monitoring for DAG execution."""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
        self.monitoring_active = False
        
    def start_monitoring(self):
        """Start real-time performance monitoring."""
        
        self.monitoring_active = True
        
        # Start monitoring thread
        import threading
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        
        while self.monitoring_active:
            # Collect metrics
            current_metrics = self._collect_metrics()
            
            # Check for performance issues
            self._check_performance_alerts(current_metrics)
            
            # Store metrics
            timestamp = time.time()
            self.metrics[timestamp] = current_metrics
            
            # Cleanup old metrics (keep last hour)
            cutoff = timestamp - 3600
            self.metrics = {t: m for t, m in self.metrics.items() if t > cutoff}
            
            time.sleep(5)  # Monitor every 5 seconds
    
    def _collect_metrics(self):
        """Collect current performance metrics."""
        
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict(),
            'network_io': psutil.net_io_counters()._asdict(),
            'active_tasks': self._count_active_tasks(),
            'queue_length': self._get_queue_length()
        }
    
    def _check_performance_alerts(self, metrics):
        """Check for performance issues and generate alerts."""
        
        # CPU usage alert
        if metrics['cpu_percent'] > 90:
            self.alerts.append({
                'type': 'high_cpu',
                'message': f"High CPU usage: {metrics['cpu_percent']}%",
                'timestamp': time.time(),
                'severity': 'warning'
            })
        
        # Memory usage alert
        if metrics['memory_percent'] > 85:
            self.alerts.append({
                'type': 'high_memory',
                'message': f"High memory usage: {metrics['memory_percent']}%",
                'timestamp': time.time(),
                'severity': 'warning'
            })
        
        # Queue length alert
        if metrics['queue_length'] > 20:
            self.alerts.append({
                'type': 'long_queue',
                'message': f"Long task queue: {metrics['queue_length']} tasks",
                'timestamp': time.time(),
                'severity': 'info'
            })
```

### 2. Performance Profiling

```python
def profile_dag_execution(orchestrator, tasks):
    """Comprehensive performance profiling of DAG execution."""
    
    import cProfile
    import pstats
    import io
    
    # Profile execution
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = orchestrator.execute_dag(tasks)
    
    profiler.disable()
    
    # Analyze profiling results
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats(50)  # Top 50 functions
    
    profiling_output = s.getvalue()
    
    # Generate performance report
    report = {
        'execution_result': result,
        'profiling_output': profiling_output,
        'performance_metrics': calculate_performance_metrics(result),
        'optimization_recommendations': generate_optimization_recommendations(result)
    }
    
    return report

def generate_optimization_recommendations(result):
    """Generate specific optimization recommendations based on execution results."""
    
    recommendations = []
    
    # Analyze task durations
    task_durations = [task.duration for task in result.completed_tasks]
    avg_duration = sum(task_durations) / len(task_durations)
    
    # Long-running task recommendation
    long_tasks = [task for task in result.completed_tasks if task.duration > avg_duration * 2]
    if long_tasks:
        recommendations.append({
            'type': 'task_optimization',
            'message': f"Consider breaking down {len(long_tasks)} long-running tasks",
            'tasks': [task.task_id for task in long_tasks],
            'priority': 'high'
        })
    
    # Parallelization recommendation
    total_task_time = sum(task_durations)
    actual_execution_time = result.execution_time
    parallelization_efficiency = total_task_time / actual_execution_time
    
    if parallelization_efficiency < 2.0:
        recommendations.append({
            'type': 'parallelization',
            'message': f"Low parallelization efficiency: {parallelization_efficiency:.2f}x",
            'suggestion': "Review task dependencies and increase worker count",
            'priority': 'medium'
        })
    
    # Resource utilization recommendation
    if hasattr(result, 'resource_usage'):
        if result.resource_usage.max_cpu_percent < 50:
            recommendations.append({
                'type': 'resource_utilization',
                'message': f"Low CPU utilization: {result.resource_usage.max_cpu_percent}%",
                'suggestion': "Consider increasing worker count or task complexity",
                'priority': 'low'
            })
    
    return recommendations
```

## Benchmarking and Testing

### 1. Performance Benchmarks

```python
def run_performance_benchmarks():
    """Run comprehensive performance benchmarks."""
    
    benchmarks = [
        ('small_dag', create_small_dag_tasks()),
        ('medium_dag', create_medium_dag_tasks()),
        ('large_dag', create_large_dag_tasks()),
        ('parallel_heavy', create_parallel_heavy_tasks()),
        ('sequential_heavy', create_sequential_heavy_tasks())
    ]
    
    results = {}
    
    for benchmark_name, tasks in benchmarks:
        print(f"🏃 Running benchmark: {benchmark_name}")
        
        # Run benchmark multiple times for statistical significance
        benchmark_results = []
        
        for run in range(3):
            orchestrator = create_optimized_orchestrator()
            
            start_time = time.time()
            result = orchestrator.execute_dag(tasks)
            end_time = time.time()
            
            benchmark_results.append({
                'execution_time': end_time - start_time,
                'task_count': len(tasks),
                'success_rate': len(result.completed_tasks) / len(tasks),
                'throughput': len(tasks) / (end_time - start_time)
            })
        
        # Calculate statistics
        execution_times = [r['execution_time'] for r in benchmark_results]
        throughputs = [r['throughput'] for r in benchmark_results]
        
        results[benchmark_name] = {
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_throughput': sum(throughputs) / len(throughputs),
            'task_count': len(tasks)
        }
        
        print(f"✅ {benchmark_name}: {results[benchmark_name]['avg_execution_time']:.2f}s avg")
    
    return results
```

### 2. Load Testing

```python
def run_load_tests():
    """Run load tests to determine system limits."""
    
    load_levels = [10, 25, 50, 100, 200, 500]
    results = {}
    
    for task_count in load_levels:
        print(f"🔥 Load test: {task_count} tasks")
        
        # Create load test tasks
        tasks = create_load_test_tasks(task_count)
        
        # Monitor system resources during execution
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        try:
            orchestrator = create_optimized_orchestrator()
            
            start_time = time.time()
            result = orchestrator.execute_dag(tasks)
            end_time = time.time()
            
            # Collect results
            results[task_count] = {
                'execution_time': end_time - start_time,
                'success_rate': len(result.completed_tasks) / len(tasks),
                'throughput': len(tasks) / (end_time - start_time),
                'max_cpu': max(m['cpu_percent'] for m in monitor.metrics.values()),
                'max_memory': max(m['memory_percent'] for m in monitor.metrics.values()),
                'failed_tasks': len(result.failed_tasks)
            }
            
            print(f"✅ {task_count} tasks: {results[task_count]['execution_time']:.2f}s, "
                  f"{results[task_count]['success_rate']*100:.1f}% success")
            
        except Exception as e:
            print(f"❌ {task_count} tasks: Failed with {e}")
            results[task_count] = {'error': str(e)}
            
        finally:
            monitor.stop_monitoring()
    
    return results
```

## Best Practices Summary

### 1. DAG Design Best Practices

- **Minimize dependencies**: Remove unnecessary dependencies to maximize parallelization
- **Balance task granularity**: Avoid tasks that are too small (overhead) or too large (poor parallelization)
- **Optimize critical path**: Focus optimization efforts on the critical path tasks
- **Use resource requirements**: Specify resource requirements for better scheduling

### 2. Resource Management Best Practices

- **Set appropriate limits**: Configure resource limits based on your system capacity
- **Monitor continuously**: Use real-time monitoring to detect performance issues
- **Implement adaptive strategies**: Use adaptive execution strategies for varying workloads
- **Plan for peak usage**: Design for peak resource requirements, not average

### 3. LLM Optimization Best Practices

- **Cache responses**: Implement intelligent caching for similar LLM tasks
- **Optimize provider selection**: Use cost-performance optimization for LLM selection
- **Batch similar tasks**: Group similar LLM tasks to reduce overhead
- **Monitor costs**: Track LLM costs in real-time and implement budget controls

### 4. Monitoring and Alerting Best Practices

- **Implement comprehensive monitoring**: Monitor all key performance metrics
- **Set up alerting**: Configure alerts for performance degradation
- **Regular benchmarking**: Run regular benchmarks to track performance trends
- **Profile regularly**: Use profiling to identify performance bottlenecks

This performance tuning guide provides a comprehensive framework for optimizing DAG orchestration performance across all dimensions. Apply these techniques based on your specific use case and performance requirements.