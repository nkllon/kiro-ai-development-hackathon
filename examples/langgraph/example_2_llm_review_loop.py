#!/usr/bin/env python3
"""
LangGraph Example 2: LLM Review Loop with Conditional Routing
==============================================================

Demonstrates the REAL LangGraph challenges:
- Developer → Reviewer pattern (like PDCA)
- Conditional routing based on review result
- State management across LLM calls
- Retry logic with max iterations
- Common pitfalls and how to avoid them

This exercises the issues found in hybrid_code_generator_langgraph.py.bak:
- State mutation in routing functions (BUG!)
- Iteration count management
- Feedback loop state flow
- LLM response parsing

Integration with Beast Mode:
- Extends ReflectiveModule for Jaeger tracing
- Tracks state transitions
- Monitors retry patterns

Run with Jaeger UI at: http://localhost:16686
"""

import os
import sys
from typing import TypedDict, Literal, Dict, Any, List
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from langgraph.graph import StateGraph, END
    from src.rm_ddd.core.unified_reflective_module import (
        ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus
    )
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


# State Schema - This is CRITICAL for LangGraph
class CodeReviewState(TypedDict):
    """
    State for developer → reviewer loop.

    CRITICAL: TypedDict defines exact structure.
    All nodes MUST return dict matching this schema.
    """
    task_description: str
    generated_code: str
    review_feedback: str
    approval_status: Literal["pending", "approved", "needs_revision"]
    iteration_count: int
    max_iterations: int
    final_code: str
    timestamp: str


class LLMReviewLoopOrchestrator(ReflectiveModule):
    """
    LLM Review Loop with proper state management.

    Demonstrates:
    - Developer node (generates code)
    - Reviewer node (reviews code)
    - Conditional routing (approved vs. needs_revision)
    - Retry logic (max iterations)
    - State flow across nodes

    Common Pitfalls Addressed:
    1. ❌ DON'T mutate state in routing functions
    2. ❌ DON'T forget to increment iteration_count
    3. ❌ DON'T lose state between iterations
    4. ✅ DO return complete state from every node
    5. ✅ DO check max iterations in routing function
    """

    def __init__(self, max_iterations: int = 3):
        super().__init__()
        self.module_id = "LLMReviewLoopOrchestrator"
        self.max_iterations = max_iterations
        self._logger.info(f"🚀 Initializing LLM Review Loop (max_iterations={max_iterations})")
        self.graph = self._create_graph()

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "module_name": "LLMReviewLoopOrchestrator",
            "version": "1.0.0",
            "description": "Developer → Reviewer loop with retry logic",
            "max_iterations": self.max_iterations,
            "graph_nodes": ["developer", "reviewer"]
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]

    def get_health_status(self) -> ModuleHealth:
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now()
        )

    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        return {
            "degradation_mode": "error_passthrough",
            "error": str(error),
            "recovery_suggestions": ["Check state schema", "Verify routing logic"]
        }

    # Node Functions

    def developer_node(self, state: CodeReviewState) -> CodeReviewState:
        """
        Developer generates or revises code.

        CRITICAL: Must return COMPLETE state dict.
        """
        with self.trace_operation("developer_node", iteration=state["iteration_count"]):
            iteration = state["iteration_count"]
            self._logger.info(f"👨‍💻 Developer Node (iteration {iteration})")

            if iteration == 0:
                # Initial generation
                self._logger.info("  Generating initial code...")
                generated = self._mock_generate_code(state["task_description"])
            else:
                # Revision based on feedback
                self._logger.info(f"  Revising code based on feedback...")
                generated = self._mock_revise_code(
                    state["generated_code"],
                    state["review_feedback"]
                )

            # CRITICAL: Return COMPLETE state
            # Don't just return {"generated_code": generated}!
            return {
                **state,  # Spread existing state
                "generated_code": generated,
                "iteration_count": iteration + 1,  # Increment here, not in routing!
                "timestamp": datetime.now().isoformat()
            }

    def reviewer_node(self, state: CodeReviewState) -> CodeReviewState:
        """
        Reviewer evaluates code and decides: approve or request revision.

        CRITICAL: Sets approval_status which routing function uses.
        """
        with self.trace_operation("reviewer_node", iteration=state["iteration_count"]):
            self._logger.info(f"👀 Reviewer Node (iteration {state['iteration_count']})")

            # Mock review (in real version, this calls Claude API)
            review_result = self._mock_review_code(
                state["generated_code"],
                state["iteration_count"]
            )

            self._logger.info(f"  Review: {review_result['status']}")
            if review_result["feedback"]:
                self._logger.info(f"  Feedback: {review_result['feedback'][:100]}")

            # Update state with review results
            return {
                **state,
                "review_feedback": review_result["feedback"],
                "approval_status": review_result["status"],
                "final_code": review_result.get("final_code", state["generated_code"])
            }

    def should_continue_routing(self, state: CodeReviewState) -> Literal["continue", "end"]:
        """
        Routing function: Decide whether to continue revising or end.

        CRITICAL PITFALL: ❌ DON'T MUTATE STATE HERE!
        This function should be PURE - no side effects.

        Original bug in hybrid_code_generator_langgraph.py.bak:
        ```python
        state["final_code"] = state["generated_code"]  # ❌ BAD! Mutating state!
        ```

        Routing functions should only READ state and return route name.
        """
        with self.trace_operation("should_continue_routing",
                                 iteration=state["iteration_count"],
                                 status=state["approval_status"]):

            # Check approval status
            if state["approval_status"] == "approved":
                self._logger.info("✅ Code approved - ending loop")
                return "end"

            # Check max iterations
            if state["iteration_count"] >= state["max_iterations"]:
                self._logger.warning(f"⚠️  Max iterations ({state['max_iterations']}) reached - ending")
                # ❌ DON'T DO THIS: state["final_code"] = state["generated_code"]
                # ✅ DO THIS: Handle in node or let final state handle it
                return "end"

            # Continue revising
            self._logger.info("🔄 Needs revision - continuing loop")
            return "continue"

    def _create_graph(self) -> StateGraph:
        """
        Create the review loop graph.

        Flow:
        START → developer → reviewer → [approved: END | needs_revision: developer]
        """
        with self.trace_operation("create_graph"):
            self._logger.info("🔨 Building review loop graph")

            workflow = StateGraph(CodeReviewState)

            # Add nodes
            workflow.add_node("developer", self.developer_node)
            workflow.add_node("reviewer", self.reviewer_node)

            # Set entry point
            workflow.set_entry_point("developer")

            # Linear edge: developer → reviewer
            workflow.add_edge("developer", "reviewer")

            # Conditional routing after reviewer
            workflow.add_conditional_edges(
                "reviewer",
                self.should_continue_routing,
                {
                    "continue": "developer",  # Loop back for revision
                    "end": END
                }
            )

            compiled = workflow.compile()
            self._logger.info("✅ Review loop graph compiled")
            return compiled

    # Mock LLM functions (in real version, these call actual LLMs)

    def _mock_generate_code(self, task: str) -> str:
        """Mock code generation (would call DeepSeek/Ollama)"""
        return f"# Generated code for: {task}\ndef solution():\n    pass"

    def _mock_revise_code(self, code: str, feedback: str) -> str:
        """Mock code revision based on feedback"""
        return f"{code}\n# Revision based on: {feedback}\n# ... improved code ..."

    def _mock_review_code(self, code: str, iteration: int) -> Dict[str, Any]:
        """
        Mock code review (would call Claude API).

        Returns different results based on iteration to test retry logic.
        """
        if iteration == 1:
            # First review: request changes
            return {
                "status": "needs_revision",
                "feedback": "Add error handling and type hints",
                "final_code": ""
            }
        elif iteration == 2:
            # Second review: still needs work
            return {
                "status": "needs_revision",
                "feedback": "Add docstrings and input validation",
                "final_code": ""
            }
        else:
            # Third review: approved
            return {
                "status": "approved",
                "feedback": "Code looks good!",
                "final_code": code
            }

    def run_review_loop(self, task_description: str) -> Dict[str, Any]:
        """Execute the review loop workflow"""
        with self.trace_operation("run_review_loop", task=task_description):
            self._logger.info(f"🚀 Starting review loop: {task_description}")

            # Initial state
            initial_state: CodeReviewState = {
                "task_description": task_description,
                "generated_code": "",
                "review_feedback": "",
                "approval_status": "pending",
                "iteration_count": 0,
                "max_iterations": self.max_iterations,
                "final_code": "",
                "timestamp": ""
            }

            # Execute graph
            final_state = self.graph.invoke(initial_state)

            self._logger.info(f"✅ Review loop complete: {final_state['iteration_count']} iterations")
            return final_state


def main():
    """Run the LLM review loop example"""
    print("=" * 80)
    print("LangGraph Example 2: LLM Review Loop with Conditional Routing")
    print("=" * 80)
    print()
    print("📊 Jaeger UI: http://localhost:16686")
    print("   (View traces to see routing decisions and retry logic)")
    print()

    # Create orchestrator
    orchestrator = LLMReviewLoopOrchestrator(max_iterations=3)

    # Test tasks
    test_tasks = [
        "Implement a function to validate email addresses",
        "Create a simple REST API endpoint",
        "Write a data processing pipeline"
    ]

    print("Running review loop examples:")
    print("-" * 80)

    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. Task: {task}")
        print("   " + "-" * 60)

        result = orchestrator.run_review_loop(task)

        print(f"   Status: {result['approval_status']}")
        print(f"   Iterations: {result['iteration_count']}")
        print(f"   Final code: {result['final_code'][:100]}...")
        if result['review_feedback']:
            print(f"   Last feedback: {result['review_feedback'][:80]}...")

    print()
    print("-" * 80)
    print("✅ All examples complete!")
    print()
    print("🔍 Check Jaeger UI to see:")
    print("   - Routing decisions (should_continue_routing spans)")
    print("   - Retry iterations (multiple developer/reviewer cycles)")
    print("   - State flow through the graph")
    print()
    print("💡 Key Learnings:")
    print("   1. Routing functions must be PURE (no state mutation)")
    print("   2. Nodes must return COMPLETE state dict (use spread operator)")
    print("   3. Increment counters in nodes, not routing functions")
    print("   4. Check max iterations in routing function")
    print("   5. Use trace_operation() to track state flow")
    print()
    print("⚠️  Common Pitfalls Demonstrated:")
    print("   - State mutation in routing (DON'T DO IT)")
    print("   - Forgetting to spread existing state")
    print("   - Incrementing counters in wrong place")
    print("=" * 80)


if __name__ == "__main__":
    main()
