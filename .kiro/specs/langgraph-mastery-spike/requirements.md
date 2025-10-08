# Requirements Document - LangGraph Mastery Spike

## Introduction

This is a **spike** (time-boxed research task) to properly learn and master LangGraph for AI collaboration workflows. While we have existing LangGraph code (hybrid_code_generator_langgraph.py.bak, pdca_langgraph_orchestrator_core.py), we need to systematically understand LangGraph's nuances and best practices before using it in production.

**Spike Goal:** Understand LangGraph well enough to confidently use it for Ghostbusters multi-agent orchestration and AI collaboration.

**Time Box:** 4-6 hours of focused learning and experimentation

## Requirements

### Requirement 1 - Understand LangGraph Fundamentals

**User Story:** As a developer, I want to understand LangGraph's core concepts (StateGraph, nodes, edges, routing), so that I can use it correctly without guessing.

#### Acceptance Criteria

1. WHEN learning StateGraph THEN I SHALL understand how it differs from simple LangChain chains
2. WHEN defining state THEN I SHALL understand TypedDict schemas and state updates
3. WHEN creating nodes THEN I SHALL understand node functions and their signatures
4. WHEN routing THEN I SHALL understand conditional edges and routing functions
5. WHEN compiling THEN I SHALL understand graph compilation and execution

### Requirement 2 - Study Existing LangGraph Code

**User Story:** As a developer, I want to analyze our existing LangGraph implementations, so that I can learn from what we've already built.

#### Acceptance Criteria

1. WHEN analyzing hybrid_code_generator_langgraph.py.bak THEN I SHALL understand the DeepSeek→Claude review workflow
2. WHEN studying pdca_langgraph_orchestrator_core.py THEN I SHALL understand PDCA cycle implementation
3. WHEN reviewing state schemas THEN I SHALL understand how state flows through the graph
4. WHEN examining routing logic THEN I SHALL understand when to refine vs. end workflows
5. WHEN checking error handling THEN I SHALL identify gaps and improvements needed

### Requirement 3 - Create Simple LangGraph Examples

**User Story:** As a developer, I want to create simple, working LangGraph examples, so that I can build up understanding incrementally.

#### Acceptance Criteria

1. WHEN creating example 1 THEN I SHALL build a simple 2-node graph (generate → validate)
2. WHEN creating example 2 THEN I SHALL add conditional routing (pass → fail → retry)
3. WHEN creating example 3 THEN I SHALL implement multi-agent consultation (parallel nodes)
4. WHEN creating example 4 THEN I SHALL add state persistence and checkpointing
5. WHEN documenting examples THEN I SHALL include clear comments explaining each concept

### Requirement 4 - Identify LangGraph Pitfalls

**User Story:** As a developer, I want to understand common LangGraph mistakes and nuances, so that I can avoid them in production code.

#### Acceptance Criteria

1. WHEN researching THEN I SHALL document state mutation patterns (when to copy vs. modify)
2. WHEN testing THEN I SHALL identify async/await edge cases
3. WHEN investigating THEN I SHALL understand memory management with large state objects
4. WHEN exploring THEN I SHALL document error handling best practices
5. WHEN compiling THEN I SHALL understand when graph compilation can fail

### Requirement 5 - Design Ghostbusters LangGraph Architecture

**User Story:** As a developer, I want to design how Ghostbusters will use LangGraph for multi-agent consultation, so that we have a clear implementation plan.

#### Acceptance Criteria

1. WHEN designing state THEN I SHALL define GhostbustersState schema with all expert results
2. WHEN designing nodes THEN I SHALL plan CodeQuality, Security, Performance, Architecture expert nodes
3. WHEN designing routing THEN I SHALL plan how to aggregate expert opinions
4. WHEN designing context THEN I SHALL plan how to inject project context (.claude/instructions.md)
5. WHEN designing fallbacks THEN I SHALL plan graceful degradation if experts fail

### Requirement 6 - Set Up Observability: Jaeger (local) + LangSmith (cloud)

**User Story:** As a developer, I want to use BOTH Jaeger (for local OpenTelemetry tracing) AND LangSmith (for LangChain-specific debugging), so that I have comprehensive observability into LangGraph workflows.

**CRITICAL: We use BOTH tools, not one or the other!**

#### Acceptance Criteria - Jaeger (Already Running!)

1. WHEN checking status THEN Jaeger SHALL be running at http://localhost:16686
2. WHEN configuring OpenTelemetry THEN I SHALL set OTEL_EXPORTER_JAEGER_ENDPOINT environment variable
3. WHEN running examples THEN I SHALL see traces in Jaeger UI (http://localhost:16686)
4. WHEN debugging THEN I SHALL use Jaeger to inspect service traces and spans
5. WHEN documenting THEN I SHALL capture screenshots of Jaeger traces

**JAEGER SETUP (Already Done!):**
- ✅ Running via docker-compose (`local-jaeger` container)
- ✅ UI: http://localhost:16686
- ✅ Ports: 14250, 14268, 6831-6832, 16686
- ✅ Status: Check with `docker ps | grep jaeger`

#### Acceptance Criteria - LangSmith

1. WHEN setting up THEN I SHALL create LangSmith account and get API key
2. WHEN configuring THEN I SHALL set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY environment variables
3. WHEN running examples THEN I SHALL see traces in LangSmith dashboard showing each node execution
4. WHEN debugging THEN I SHALL use LangSmith to inspect state transitions and LLM calls
5. WHEN documenting THEN I SHALL capture screenshots of BOTH Jaeger AND LangSmith traces

**LANGSMITH SETUP:**
```bash
# Install
pip install langsmith

# Configure
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your_api_key>
export LANGCHAIN_PROJECT=langgraph-mastery-spike
```

**WHY BOTH TOOLS:**
- ✅ **Jaeger**: Infrastructure-level tracing (spans, services, dependencies)
  - Already integrated via ReflectiveModule base class!
  - Auto-instruments: FastAPI, Requests, Logging
  - See: src/beast_mode/tracing/tracer.py
- ✅ **LangSmith**: LangChain-specific tracing (LLM calls, chains, state)
  - Specialized for LangChain/LangGraph workflows
  - Shows LLM interactions, token usage, state transitions
- ✅ **Together**: Complete picture from infrastructure to LLM interactions
- ❌ **Without both**: Missing either infrastructure view OR LangChain insights

**IMPORTANT: ReflectiveModule Integration**
- All LangGraph examples should extend ReflectiveModule
- This automatically provides Jaeger tracing via `trace_operation()` context manager
- LangSmith is additive for LangChain-specific insights

### Requirement 7 - Validate LangGraph vs. Alternatives

**User Story:** As a developer, I want to compare LangGraph with simpler alternatives, so that I can make an informed decision.

#### Acceptance Criteria

1. WHEN comparing THEN I SHALL evaluate: LangGraph vs. simple async/await parallel execution
2. WHEN comparing THEN I SHALL evaluate: LangGraph vs. LangChain chains with routing
3. WHEN comparing THEN I SHALL evaluate: State management complexity vs. benefits
4. WHEN deciding THEN I SHALL document when LangGraph is worth the complexity
5. WHEN recommending THEN I SHALL provide clear guidance on LangGraph vs. simpler approaches

## Success Criteria

**Spike is successful when:**
1. ✅ We understand LangGraph well enough to use it confidently
2. ✅ We have 3-4 working examples demonstrating key concepts
3. ✅ We have documented pitfalls and best practices
4. ✅ We have a clear Ghostbusters implementation plan
5. ✅ We can make an informed decision: use LangGraph or use simpler approaches

**Spike outputs:**
- `/examples/langgraph/` directory with working examples
- `LANGGRAPH_LEARNINGS.md` documenting insights and pitfalls
- `GHOSTBUSTERS_LANGGRAPH_DESIGN.md` with architecture plan
- Decision document: "When to use LangGraph vs. alternatives"

## Time Box

**Maximum time:** 6 hours
**Minimum time:** 4 hours

If we can't master it in 6 hours, we defer to simpler approaches.
