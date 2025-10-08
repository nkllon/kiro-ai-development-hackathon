# 🔬 Beast Mode Notebooks: Exploration & Enhancement Guide

This guide shows you how to explore, experiment with, and enhance the Beast Mode demonstration notebooks.

## 📚 Available Notebooks

### 1. [Constellation Orchestrator Demo](constellation_orchestrator_demo.ipynb)
**What it demonstrates**: DAG-based AI workflow orchestration with mathematical governance

**Exploration ideas**:
- 📝 Create your own workflow with custom dependencies
- 🔍 Add more complex dependency patterns
- ⚡ Experiment with different parallelization strategies
- 📊 Add custom metrics and visualizations
- 🧪 Test cycle detection with your own examples

**Quick experiments**:
```python
# After running the notebook, try this in a new cell:

# Create a custom workflow for your domain
custom_tasks = [
    TaskDefinition(
        task_id="your_task_1",
        prompt="Your custom prompt here",
        dependencies=[],
        timeout=60,
        category="your-category",
        tags=["custom", "experiment"]
    ),
    # Add more tasks...
]

# Analyze it
analysis, depths = analyze_dag_properties(custom_tasks)
print(f"Your workflow has {analysis['max_depth']} levels")
print(f"Speedup potential: {analysis['total_nodes'] / analysis['max_depth']:.2f}x")

# Visualize it
mermaid = generate_mermaid_dag(custom_tasks)
display(Markdown(f"```mermaid\n{mermaid}\n```"))
```

---

### 2. [AI Memory Palace Demo](ai_memory_palace_demo.ipynb)
**What it demonstrates**: Persistent context management across AI sessions

**Exploration ideas**:
- 📅 Extend the scenario to more days
- 💾 Add different types of context (decisions, errors, patterns)
- 📈 Experiment with context growth patterns
- 🎯 Add custom optimization strategies
- 📊 Create new performance visualizations

**Quick experiments**:
```python
# After running the notebook, try this in a new cell:

# Add a new day to the scenario
day_4_session = {
    'day': 4,
    'focus': 'Performance Optimization',
    'events': 5,
    'context_mb': 0.120,
    'load_time_ms': 1800,
    'decisions': 4,
    'errors': 2,
    'loc': 480
}

# Append to existing sessions
sessions.append(day_4_session)

# Recalculate metrics
total_events = sum(s['events'] for s in sessions)
total_loc = sum(s['loc'] for s in sessions)
avg_load = sum(s['load_time_ms'] for s in sessions) / len(sessions)

print(f"📊 Updated Stats:")
print(f"  Total days: {len(sessions)}")
print(f"  Total events: {total_events}")
print(f"  Total LOC: {total_loc}")
print(f"  Avg load time: {avg_load:.0f}ms")

# Re-run visualization cell to see updated chart
```

---

### 3. [ReflectiveModule Pattern Demo](reflective_module_demo.ipynb)
**What it demonstrates**: Universal observability pattern for all Beast Mode components

**Exploration ideas**:
- 🏗️ Create new component types using ReflectiveModule
- 📊 Add custom metrics to components
- 🚨 Experiment with different health thresholds
- 🔍 Add custom health check logic
- 📈 Create aggregated metrics across components

**Quick experiments**:
```python
# After running the notebook, try this in a new cell:

# Create a custom component
class CacheManager(ReflectiveModule):
    """Custom cache manager with built-in observability."""

    def __init__(self, name: str):
        super().__init__(name)
        self.cache = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        try:
            if key in self.cache:
                self.hits += 1
                self._record_metric("cache_hit", 1.0)
                return self.cache[key]
            else:
                self.misses += 1
                self._record_metric("cache_miss", 1.0)
                return None
        except Exception as e:
            self._handle_error(e, {"operation": "get", "key": key})
            return None

    def set(self, key: str, value: Any):
        """Set item in cache."""
        try:
            self.cache[key] = value
            self._record_metric("cache_set", 1.0)
        except Exception as e:
            self._handle_error(e, {"operation": "set", "key": key})

    def health_check(self) -> Dict[str, Any]:
        """Custom health check."""
        base_health = super().health_check()
        hit_rate = self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0

        base_health['cache_stats'] = {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1%}"
        }

        return base_health

# Test it
cache = CacheManager("app_cache")

# Simulate operations
for i in range(50):
    key = f"key_{i % 10}"  # Only 10 unique keys = high hit rate
    value = cache.get(key)
    if value is None:
        cache.set(key, f"value_{i}")

# Check health
health = cache.health_check()
print(f"Cache health: {health['status']}")
print(f"Hit rate: {health['cache_stats']['hit_rate']}")
```

---

## 🎯 Cross-Notebook Experiments

### Combine Concepts

Try combining concepts from multiple notebooks:

```python
# Example: Add ReflectiveModule observability to a Constellation task executor

class ObservableTaskExecutor(ReflectiveModule):
    """Task executor with built-in observability."""

    def __init__(self, name: str):
        super().__init__(name)
        self.executed_tasks = []

    def execute_task(self, task: TaskDefinition) -> Dict[str, Any]:
        """Execute a task with full observability."""
        start_time = time.time()

        try:
            # Simulate task execution
            time.sleep(0.1)  # Simulate work

            duration = (time.time() - start_time) * 1000
            self._record_metric("task_execution", duration)

            result = {
                'task_id': task.task_id,
                'status': 'completed',
                'duration_ms': duration
            }

            self.executed_tasks.append(result)
            return result

        except Exception as e:
            self._handle_error(e, {"task_id": task.task_id})
            return {
                'task_id': task.task_id,
                'status': 'failed',
                'error': str(e)
            }

# Use it
executor = ObservableTaskExecutor("dag_executor")

# Execute some tasks
for task in simple_tasks[:2]:
    result = executor.execute_task(task)
    print(f"✅ {result['task_id']}: {result['duration_ms']:.0f}ms")

# Check health
health = executor.health_check()
print(f"\n📊 Executor health:")
print(f"   Status: {health['status']}")
print(f"   Operations: {health['operation_count']}")
print(f"   Errors: {health['error_count']}")
```

---

## 🧪 Testing Your Changes

After making modifications, test them:

```bash
# Test notebook structure
python3 test_notebooks.py

# Test notebook execution
python3 enhanced_notebook_test.py
```

---

## 📊 Adding Custom Visualizations

### Example: Add a performance comparison chart

```python
import matplotlib.pyplot as plt
import numpy as np

def compare_approaches(metric_name: str, traditional: float, beast_mode: float, unit: str = ""):
    """Create a comparison visualization."""
    fig, ax = plt.subplots(figsize=(10, 6))

    approaches = ['Traditional', 'Beast Mode']
    values = [traditional, beast_mode]
    colors = ['#FF6B6B', '#51CF66']

    bars = ax.barh(approaches, values, color=colors, alpha=0.7)

    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(value + max(values) * 0.02, i, f'{value}{unit}',
                va='center', fontweight='bold')

    # Add improvement percentage
    improvement = ((traditional - beast_mode) / traditional) * 100
    ax.text(max(values) / 2, 0.5,
            f'{improvement:.0f}% Improvement',
            ha='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    ax.set_xlabel(metric_name, fontsize=12, fontweight='bold')
    ax.set_title(f'{metric_name} Comparison', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    return fig

# Use it
fig = compare_approaches(
    'Development Time (hours)',
    traditional=16.0,
    beast_mode=2.0,
    unit='h'
)
plt.show()
```

---

## 🚀 Advanced Experiments

### 1. Real Constellation Execution

If you have Redis and Claude CLI set up:

```python
import asyncio

async def run_real_execution():
    """Run actual Constellation Orchestrator execution."""
    from constellation_orchestrator import ConstellationOrchestrator, ConstellationConfig

    config = ConstellationConfig.load_from_env()
    orchestrator = ConstellationOrchestrator(config)

    await orchestrator.initialize()
    await orchestrator.load_tasks(simple_tasks)

    execution_id = await orchestrator.start_execution("demo_run")
    print(f"Started execution: {execution_id}")

    # Monitor progress
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if state.is_execution_complete():
            break
        await asyncio.sleep(2)

    await orchestrator.shutdown()
    print("✅ Execution complete!")

# Run it
# asyncio.run(run_real_execution())  # Uncomment to run
```

### 2. AI Memory Palace with Real Storage

```python
# Example: Add Redis persistence

import redis
import json

class PersistentMemoryPalace:
    """AI Memory Palace with Redis backend."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url)
        self.key_prefix = "memory_palace:"

    def save_session(self, session_id: str, data: dict):
        """Save session to Redis."""
        key = f"{self.key_prefix}{session_id}"
        self.redis.set(key, json.dumps(data))
        self.redis.expire(key, 86400 * 30)  # 30 days

    def load_session(self, session_id: str) -> Optional[dict]:
        """Load session from Redis."""
        key = f"{self.key_prefix}{session_id}"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def get_all_sessions(self) -> List[dict]:
        """Get all sessions."""
        keys = self.redis.keys(f"{self.key_prefix}*")
        sessions = []
        for key in keys:
            data = self.redis.get(key)
            if data:
                sessions.append(json.loads(data))
        return sessions

# Use it (if Redis is available)
# palace = PersistentMemoryPalace()
# palace.save_session("demo_001", sessions[0])
```

---

## 💡 Contribution Ideas

Want to enhance the notebooks? Here are some ideas:

1. **Add interactive widgets** using ipywidgets
2. **Create animated visualizations** with matplotlib animation
3. **Add real-time monitoring** dashboards
4. **Implement export functions** (PDF, HTML, etc.)
5. **Add more domain-specific examples** (ML pipelines, data analysis, etc.)
6. **Create notebook templates** for common use cases
7. **Add performance benchmarking** tools
8. **Create integration examples** with other Beast Mode components

---

## 📝 Best Practices

### When Modifying Notebooks:

1. **Always run cells in order** - Dependencies matter!
2. **Test after each change** - Use the test scripts
3. **Document your experiments** - Add markdown cells explaining what you did
4. **Save variations** - Copy notebooks before making major changes
5. **Share interesting findings** - Contribute back to the project!

### Performance Tips:

- Use `VIZ = False` to disable visualizations for faster execution
- Sample large datasets before visualization
- Use generators for memory efficiency
- Profile code with `%%timeit` magic command

---

## 🐛 Troubleshooting

### Common Issues:

**"NameError: name 'X' is not defined"**
- Solution: Run cells in order from the top

**"ModuleNotFoundError"**
- Solution: `pip install -r ../../requirements.txt`

**"Cannot connect to display"**
- Solution: Run with `VIZ = False` in first cell

**Visualization not showing**
- Solution: Use `%matplotlib inline` magic command

---

## 🎓 Learning Path

Recommended order for exploring:

1. **Start with ReflectiveModule** - Simplest pattern, foundation of everything
2. **Then AI Memory Palace** - Understand context management
3. **Finally Constellation** - Most complex, brings it all together

Each notebook builds on concepts from the previous ones!

---

## 🚀 Next Steps

After exploring these notebooks:

1. Read the [main README](../../README.md) for full Beast Mode documentation
2. Explore the [source code](../../src/) to understand implementations
3. Check out [other examples](../) for more use cases
4. Join the community and share your experiments!

---

*Happy Exploring! 🐺✨*

**Remember**: These notebooks are starting points. The real power comes from adapting them to your specific needs!
