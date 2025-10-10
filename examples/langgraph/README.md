# LangGraph Examples with Beast Mode Integration

Progressive examples demonstrating LangGraph integrated with Beast Mode's ReflectiveModule pattern for built-in observability.

## 🎯 What You'll Learn

- LangGraph fundamentals (StateGraph, nodes, edges, routing)
- ReflectiveModule integration for automatic Jaeger tracing
- Conditional routing and retry logic
- Parallel agent execution
- State persistence and checkpointing

## 📋 Prerequisites

### 1. Install Dependencies
```bash
pip install langgraph langsmith opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger
```

### 2. Verify Jaeger is Running
```bash
docker ps | grep jaeger
# Should show: local-jaeger container running
```

### 3. Access Jaeger UI
Open http://localhost:16686 - you'll see traces here after running examples.

### 4. (Optional) Set Up LangSmith
For LangChain-specific tracing (complements Jaeger):
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your_key>
export LANGCHAIN_PROJECT=langgraph-examples
```

## 📚 Examples

### Example 1: Simple Workflow
**File**: `example_1_simple_workflow.py` | **Notebook**: `example_1_simple_workflow.ipynb`

Basic LangGraph concepts:
- StateGraph with TypedDict schema
- Simple node functions (state → state)
- Linear workflow: Input → Process → Output
- ReflectiveModule integration

**Run it:**
```bash
python3 examples/langgraph/example_1_simple_workflow.py
```

**Or use Jupyter:**
```bash
jupyter notebook examples/langgraph/example_1_simple_workflow.ipynb
```

**What to expect:**
- 3 workflows execute successfully
- Check Jaeger UI for traces showing node execution
- Service: `beast-mode`, Operations: `run_workflow`, `input_node`, `process_node`, `output_node`

### Example 2: Conditional Routing (Coming Soon)
Demonstrates:
- Conditional edges
- Routing functions
- Retry logic with max iterations
- Error handling

### Example 3: Parallel Agents (Coming Soon)
Demonstrates:
- Parallel node execution
- Multi-agent consultation
- Result aggregation
- Performance comparison

### Example 4: State Persistence (Coming Soon)
Demonstrates:
- Checkpointing
- Resume from checkpoint
- Long-running workflows

## 🔍 Observability

### Jaeger (Infrastructure Tracing)
All examples automatically send traces to Jaeger via ReflectiveModule:

1. **View Traces**: http://localhost:16686
2. **Select Service**: `beast-mode`
3. **Find Operations**:
   - `run_workflow` - Overall execution
   - `create_graph` - Graph compilation
   - Individual node operations

4. **Inspect Span**: Click on any trace to see:
   - Duration
   - Tags (input parameters)
   - Nested operations

### LangSmith (LangChain Tracing - Optional)
If configured, you'll also get LangChain-specific insights:
- LLM calls
- Chain execution
- Token usage
- State transitions

Together, Jaeger + LangSmith = complete observability!

## 🏗️ Architecture

### ReflectiveModule Integration
All examples extend `ReflectiveModule` which provides:

```python
class MyWorkflow(ReflectiveModule):
    def some_operation(self, state):
        with self.trace_operation("operation_name", param=value):
            # Your code here
            # Automatically traced in Jaeger!
            return result
```

**Benefits:**
- ✅ Automatic Jaeger tracing
- ✅ Prometheus metrics
- ✅ Redis auto-registration
- ✅ Health monitoring
- ✅ Graceful degradation

### Graph Structure Pattern
```python
# 1. Define state schema
class MyState(TypedDict):
    field1: str
    field2: int

# 2. Create nodes (simple functions)
def node_function(state: MyState) -> MyState:
    # Modify state
    return state

# 3. Build graph
workflow = StateGraph(MyState)
workflow.add_node("node1", node_function)
workflow.add_edge("node1", "node2")
workflow.set_entry_point("node1")

# 4. Compile and run
graph = workflow.compile()
result = graph.invoke(initial_state)
```

## 🎓 Key Learnings

### From Example 1:
1. **StateGraph takes TypedDict schema** - Defines state structure
2. **Nodes are simple functions** - `state → state` signature
3. **Edges define workflow flow** - Connect nodes together
4. **ReflectiveModule gives tracing for free** - Use `trace_operation()` context manager
5. **Compile before running** - `workflow.compile()`
6. **Invoke to execute** - `graph.invoke(initial_state)`

### General Patterns:
- **State is immutable-ish**: Modify and return, don't mutate in place
- **Nodes should be pure functions**: Given same state, return same result
- **Use context managers for tracing**: Automatic span creation
- **Check Jaeger early and often**: Verify traces are being sent

## 📊 Monitoring Dashboard

When running examples, you can monitor:

1. **Jaeger UI** (http://localhost:16686)
   - Distributed traces
   - Operation timings
   - Error tracking

2. **Grafana** (http://localhost:3000)
   - System metrics
   - Resource usage
   - Performance graphs

3. **Prometheus** (http://localhost:9090)
   - Raw metrics data
   - Custom queries

## 🐛 Troubleshooting

### Jaeger not showing traces?
```bash
# Check Jaeger is running
docker ps | grep jaeger

# Check OpenTelemetry is configured
python3 -c "from src.beast_mode.tracing.tracer import TRACING_AVAILABLE; print(TRACING_AVAILABLE)"
```

### LangGraph import error?
```bash
pip install langgraph
```

### "module_id not found" error?
This is expected during initialization - Redis registration happens after module_id is set. Safe to ignore.

## 📖 References

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Jaeger Docs**: https://www.jaegertracing.io/docs/
- **LangSmith**: https://docs.smith.langchain.com/
- **ReflectiveModule**: `src/rm_ddd/core/unified_reflective_module.py`
- **Beast Mode Tracing**: `src/beast_mode/tracing/tracer.py`

## 🚀 Next Steps

1. Run Example 1 and check Jaeger traces
2. Try modifying the workflow (add new nodes, change processing)
3. Experiment with different state schemas
4. Move on to Example 2 for conditional routing
5. Explore parallel execution in Example 3

Happy LangGraph learning! 🎉
