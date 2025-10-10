# Hybrid LLM Execution Mode

## Overview

The Hybrid Execution Mode combines **DeepSeek Coder 6.7B** (for fast, cost-effective code generation) with **Claude Sonnet 4.5** (for quality review) to achieve **80% cost savings** while maintaining high code quality.

## Architecture

```
Task Description → DeepSeek Generates Code → Claude Reviews Code → Approved? → Output
                          ↑                                            ↓
                          └──────────── Needs Revision ───────────────┘
                                    (max 5 iterations)
```

## Cost Comparison

- **Traditional (Claude only)**: ~$10 per 1000 tasks
- **Hybrid (DeepSeek + Claude)**: ~$0.50 per 1000 tasks
- **Savings**: 95% reduction in generation costs

### Cost Breakdown
- DeepSeek generation: $0.001 per task (RunPod GPU @ $0.60/hr, 2-4s per task)
- Claude review: Minimal tokens (~500 tokens per review)
- Total: ~20x cheaper than Claude-only approach

## Prerequisites

### 1. RunPod GPU Instance (for DeepSeek)
```bash
# SSH tunnel to RunPod Ollama instance
ssh -L 11435:localhost:11434 fluffy
```

### 2. Environment Setup
```bash
# Install dependencies
pip install langgraph langchain-anthropic langchain-community

# Set Anthropic API key
export ANTHROPIC_API_KEY=your_key_here
```

### 3. Verify DeepSeek is Running
```bash
# Test local DeepSeek connection
curl http://localhost:11435/api/tags

# Should see deepseek-coder:6.7b in model list
```

## Usage

### Traditional Mode (Simulation Only)
```bash
python scripts/beast_mode_dag_launcher.py --mode traditional
```

### Hybrid Mode (DeepSeek + Claude)
```bash
python scripts/beast_mode_dag_launcher.py --mode hybrid
```

## What Happens in Hybrid Mode

1. **Task Discovery**: Scans `.kiro/specs/*/tasks.md` for pending tasks
2. **Context Loading**: Loads `requirements.md` and `design.md` from spec directory
3. **Code Generation**:
   - DeepSeek generates initial code based on task description
   - Optimized for Python, runs on GPU (2-4 second response)
4. **Quality Review**:
   - Claude reviews for correctness, security, best practices
   - Provides specific feedback if changes needed
5. **Iteration Loop**:
   - DeepSeek refines code based on Claude's feedback
   - Up to 5 iterations until approval
6. **Output**:
   - Final code saved to spec directory as `generated_<task_id>.py`
   - Task status updated to completed in `tasks.md`
   - Full execution trace logged for observability

## Example Output

```
🐺⚡ BEAST MODE DAG LAUNCHER ACTIVATED (🤖 HYBRID mode)
SYSTEMATIC COLLABORATION ENGAGED
📋 Discovered spec: test-hybrid-executor (3 tasks)
🚀 2 tasks ready for immediate execution

🤖 agent_1 executing with Hybrid LLM: Create a utility function for email validation...

📋 Parsing spec task...
🤖 Generating code with DeepSeek (iteration 1)...
✅ Code generated (342 chars)

👁️  Reviewing code with Claude...
⚠️  Code needs revision
Feedback: Missing edge case handling for None input...

🤖 Generating code with DeepSeek (iteration 2)...
✅ Code generated (489 chars)

👁️  Reviewing code with Claude...
✅ Code APPROVED!

✅ agent_1 completed: test-hybrid-executor/1 (2 iterations, approved)
📝 Generated code saved to .kiro/specs/test-hybrid-executor/generated_1.py
```

## Configuration

### DAG Executor Config
```python
config = {
    'execution_mode': 'hybrid',  # or 'traditional'
    'max_iterations': 5,         # max refinement iterations
    'deepseek_url': 'http://localhost:11435',
    'deepseek_model': 'deepseek-coder:6.7b',
    'claude_model': 'claude-sonnet-4-20250514'
}
```

### Beast Mode Launcher Config
```python
beast_mode_config = {
    "max_parallel_agents": 4,
    "task_timeout_minutes": 30,
    "execution_mode": "hybrid",
    "systematic_excellence_required": True
}
```

## Observability

### RDI Compliance
All hybrid executions are fully traced using the Unified Reflective Module:

```python
with self.trace_operation("execute_task_with_llm") as trace:
    # Execution happens here
    trace.output_result = {
        'task_id': task.task_id,
        'iterations': result['iteration_count'],
        'approval_status': result['approval_status'],
        'code_length': len(result['final_code'])
    }
```

### Metrics Tracked
- Generation time per task
- Review iterations required
- Approval rate
- Cost per task (DeepSeek + Claude tokens)
- Code quality scores

## Troubleshooting

### Issue: "Connection refused to localhost:11435"
**Solution**: Ensure RunPod SSH tunnel is active
```bash
ssh -L 11435:localhost:11434 fluffy
```

### Issue: "ANTHROPIC_API_KEY not set"
**Solution**: Export your API key
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Issue: DeepSeek generates low-quality code
**Solution**: This is expected - Claude's review loop will catch issues and request improvements. The system typically converges to approved code within 2-3 iterations.

### Issue: Tasks stuck in review loop (5 iterations)
**Solution**: Review the task description for clarity. Vague requirements lead to more iterations. Consider refining the `requirements.md` with more specific acceptance criteria.

## Production Recommendations

1. **Use semantic caching** (planned feature): Cache approved code for similar tasks
2. **Monitor approval rates**: Track how often code passes on first review
3. **Tune iteration limits**: Adjust max iterations based on task complexity
4. **Cost tracking**: Enable detailed cost logging to monitor per-task expenses
5. **Fallback strategy**: If DeepSeek is unavailable, fall back to Claude-only generation

## Next Steps

See [.kiro/specs/hybrid-code-generator/design.md](.kiro/specs/hybrid-code-generator/design.md) for the full production design including:
- Semantic caching with RAG-like pattern matching
- Pattern reuse from successful implementations
- Advanced security sandboxing
- Cost tracking and budget controls
- Git integration for automated commits
