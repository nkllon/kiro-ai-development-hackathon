#!/usr/bin/env python3
"""
LangGraph Example 3: Multi-LLM Workflow (DeepSeek + Claude)
============================================================

Demonstrates the PERVERSE case that likely caused issues:
- Using MULTIPLE different LLMs in ONE LangGraph workflow
- DeepSeek (fast, local) for code generation
- Claude (capable, API) for code review
- Switching LLM context between nodes
- State management across different LLM providers
- LangChain model confusion

This is the REAL issue from hybrid_code_generator_langgraph.py.bak!

Potential Issues:
1. LangChain model instances getting confused
2. Different LLM response formats
3. Context/memory leaking between LLMs
4. State serialization issues
5. LangGraph not expecting model switches

Integration with Beast Mode:
- ReflectiveModule for Jaeger tracing
- Separate traces for each LLM call
- Monitor LLM switch boundaries

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

    # Import LangChain LLM wrappers
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_community.chat_models import ChatOllama
        from langchain_core.messages import HumanMessage, SystemMessage
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        print("⚠️  LangChain not fully available - using mocks")
        LANGCHAIN_AVAILABLE = False

    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


# State Schema - Must work with BOTH LLMs
class MultiLLMState(TypedDict):
    """
    State that flows through multi-LLM workflow.

    CRITICAL: Both DeepSeek and Claude must handle this schema.
    Watch for:
    - Different LLM response formats
    - Context bleeding between models
    - State serialization
    """
    task_description: str
    deepseek_generated_code: str  # From DeepSeek
    claude_review_result: str     # From Claude
    approval_status: Literal["pending", "approved", "needs_revision"]
    iteration_count: int
    max_iterations: int
    final_code: str
    timestamp: str
    # Track which LLM was last used
    last_llm_used: Literal["deepseek", "claude", "none"]


class MultiLLMOrchestrator(ReflectiveModule):
    """
    Orchestrates workflow across multiple LLMs.

    DeepSeek (local, fast) → generates code
    Claude (API, capable) → reviews code

    This is where things can go wrong:
    1. LangChain model instances getting mixed up
    2. Different prompt formats
    3. Memory/context leaking
    4. State not matching what LLMs expect
    """

    def __init__(self, max_iterations: int = 2, use_real_llms: bool = False):
        super().__init__()
        self.module_id = "MultiLLMOrchestrator"
        self.max_iterations = max_iterations
        self.use_real_llms = use_real_llms

        # Initialize LLM instances
        if use_real_llms and LANGCHAIN_AVAILABLE:
            self._init_real_llms()
        else:
            self._init_mock_llms()

        self._logger.info(f"🚀 Initializing Multi-LLM Orchestrator (real_llms={use_real_llms})")
        self.graph = self._create_graph()

    def _init_real_llms(self):
        """Initialize real LLM instances"""
        try:
            # DeepSeek via Ollama (local)
            self.deepseek = ChatOllama(
                model="deepseek-coder:6.7b",
                base_url=os.getenv("DEEPSEEK_URL", "http://localhost:11434"),
                temperature=0.1
            )
            self._logger.info("✅ DeepSeek initialized (Ollama)")
        except Exception as e:
            self._logger.warning(f"⚠️  DeepSeek init failed: {e}, using mock")
            self.deepseek = None

        try:
            # Claude via Anthropic API
            self.claude = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                temperature=0,
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )
            self._logger.info("✅ Claude initialized (Anthropic API)")
        except Exception as e:
            self._logger.warning(f"⚠️  Claude init failed: {e}, using mock")
            self.claude = None

    def _init_mock_llms(self):
        """Use mock LLMs for testing"""
        self.deepseek = None
        self.claude = None
        self._logger.info("Using mock LLMs")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "module_name": "MultiLLMOrchestrator",
            "version": "1.0.0",
            "description": "Multi-LLM workflow: DeepSeek + Claude",
            "llms_used": ["deepseek-coder", "claude-sonnet-4"],
            "use_real_llms": self.use_real_llms
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.API_INTEGRATION
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
            "degradation_mode": "fallback_to_mock",
            "error": str(error),
            "recovery_suggestions": ["Check LLM API keys", "Verify Ollama is running"]
        }

    # Node Functions - Each uses DIFFERENT LLM

    def deepseek_generate_node(self, state: MultiLLMState) -> MultiLLMState:
        """
        Use DeepSeek to generate code.

        CRITICAL: Switching TO DeepSeek from previous Claude context.
        Watch for:
        - LangChain model instance confusion
        - Different message formats
        - Context bleeding
        """
        with self.trace_operation("deepseek_generate",
                                 iteration=state["iteration_count"],
                                 last_llm=state["last_llm_used"]):

            self._logger.info(f"🤖 DeepSeek Node (iteration {state['iteration_count']})")
            self._logger.info(f"   Previous LLM: {state['last_llm_used']}")

            if state["iteration_count"] == 0:
                # Initial generation
                prompt = f"Generate Python code for: {state['task_description']}"
                self._logger.info(f"   Generating initial code...")
            else:
                # Revision based on Claude's feedback
                prompt = f"Revise this code:\n{state['deepseek_generated_code']}\n\nFeedback: {state['claude_review_result']}"
                self._logger.info(f"   Revising based on Claude feedback...")

            # Call DeepSeek (or mock)
            if self.deepseek:
                try:
                    response = self.deepseek.invoke([HumanMessage(content=prompt)])
                    generated_code = response.content
                    self._logger.info(f"   ✅ Real DeepSeek response: {len(generated_code)} chars")
                except Exception as e:
                    self._logger.error(f"   ❌ DeepSeek error: {e}")
                    generated_code = self._mock_deepseek(prompt)
            else:
                generated_code = self._mock_deepseek(prompt)

            # Update state - CRITICAL: Note LLM switch
            return {
                **state,
                "deepseek_generated_code": generated_code,
                "iteration_count": state["iteration_count"] + 1,
                "last_llm_used": "deepseek",  # Track LLM switch!
                "timestamp": datetime.now().isoformat()
            }

    def claude_review_node(self, state: MultiLLMState) -> MultiLLMState:
        """
        Use Claude to review code.

        CRITICAL: Switching TO Claude from previous DeepSeek context.
        This is where confusion can happen!

        Issues to watch:
        - Claude seeing DeepSeek's context
        - Different response parsing
        - State format mismatches
        """
        with self.trace_operation("claude_review",
                                 iteration=state["iteration_count"],
                                 last_llm=state["last_llm_used"]):

            self._logger.info(f"👁️  Claude Node (iteration {state['iteration_count']})")
            self._logger.info(f"   Previous LLM: {state['last_llm_used']}")

            # Prepare review prompt
            prompt = f"""Review this code for: {state['task_description']}

Code:
{state['deepseek_generated_code']}

Respond with:
STATUS: [APPROVED or NEEDS_REVISION]
FEEDBACK: [your feedback]
"""

            # Call Claude (or mock)
            if self.claude:
                try:
                    response = self.claude.invoke([
                        SystemMessage(content="You are a code reviewer."),
                        HumanMessage(content=prompt)
                    ])
                    review_text = response.content
                    self._logger.info(f"   ✅ Real Claude response: {len(review_text)} chars")
                except Exception as e:
                    self._logger.error(f"   ❌ Claude error: {e}")
                    review_text = self._mock_claude(prompt, state["iteration_count"])
            else:
                review_text = self._mock_claude(prompt, state["iteration_count"])

            # Parse review result
            if "APPROVED" in review_text.upper():
                status = "approved"
                self._logger.info("   ✅ Code APPROVED")
            else:
                status = "needs_revision"
                self._logger.info("   ⚠️  Code NEEDS REVISION")

            # Update state - CRITICAL: Note LLM switch
            return {
                **state,
                "claude_review_result": review_text,
                "approval_status": status,
                "last_llm_used": "claude",  # Track LLM switch!
                "final_code": state["deepseek_generated_code"] if status == "approved" else ""
            }

    def should_continue_routing(self, state: MultiLLMState) -> Literal["continue", "end"]:
        """
        Routing function - same as Example 2 but now with LLM context switches.

        QUESTION: Does LangGraph get confused when routing between different LLMs?
        """
        with self.trace_operation("routing",
                                 status=state["approval_status"],
                                 last_llm=state["last_llm_used"]):

            if state["approval_status"] == "approved":
                self._logger.info("✅ Approved - ending workflow")
                return "end"

            if state["iteration_count"] >= state["max_iterations"]:
                self._logger.warning(f"⚠️  Max iterations reached - ending")
                return "end"

            self._logger.info("🔄 Needs revision - looping back to DeepSeek")
            return "continue"

    def _create_graph(self) -> StateGraph:
        """
        Create multi-LLM workflow graph.

        Flow:
        DeepSeek → Claude → [approved: END | needs_revision: DeepSeek]

        CRITICAL: LLM switches happen at edges!
        """
        with self.trace_operation("create_graph"):
            self._logger.info("🔨 Building multi-LLM graph")

            workflow = StateGraph(MultiLLMState)

            # Add nodes - each uses DIFFERENT LLM
            workflow.add_node("deepseek_generate", self.deepseek_generate_node)
            workflow.add_node("claude_review", self.claude_review_node)

            # Entry point: start with DeepSeek
            workflow.set_entry_point("deepseek_generate")

            # Linear edge: DeepSeek → Claude (LLM SWITCH!)
            workflow.add_edge("deepseek_generate", "claude_review")

            # Conditional routing after Claude
            workflow.add_conditional_edges(
                "claude_review",
                self.should_continue_routing,
                {
                    "continue": "deepseek_generate",  # Back to DeepSeek (LLM SWITCH!)
                    "end": END
                }
            )

            compiled = workflow.compile()
            self._logger.info("✅ Multi-LLM graph compiled")
            return compiled

    # Mock LLM functions

    def _mock_deepseek(self, prompt: str) -> str:
        """Mock DeepSeek response"""
        return f"# DeepSeek generated code\ndef solution():\n    # TODO: implement\n    pass"

    def _mock_claude(self, prompt: str, iteration: int) -> str:
        """Mock Claude response"""
        if iteration >= 2:
            return "STATUS: APPROVED\nFEEDBACK: Code looks good!"
        else:
            return "STATUS: NEEDS_REVISION\nFEEDBACK: Add error handling and type hints"

    def run_multi_llm_workflow(self, task_description: str) -> Dict[str, Any]:
        """Execute the multi-LLM workflow"""
        with self.trace_operation("run_multi_llm_workflow", task=task_description):
            self._logger.info(f"🚀 Starting multi-LLM workflow: {task_description}")

            initial_state: MultiLLMState = {
                "task_description": task_description,
                "deepseek_generated_code": "",
                "claude_review_result": "",
                "approval_status": "pending",
                "iteration_count": 0,
                "max_iterations": self.max_iterations,
                "final_code": "",
                "timestamp": "",
                "last_llm_used": "none"
            }

            final_state = self.graph.invoke(initial_state)

            self._logger.info(f"✅ Multi-LLM workflow complete: {final_state['iteration_count']} iterations")
            return final_state


def main():
    """Run the multi-LLM workflow example"""
    print("=" * 80)
    print("LangGraph Example 3: Multi-LLM Workflow (DeepSeek + Claude)")
    print("=" * 80)
    print()
    print("⚠️  THIS EXAMPLE DEMONSTRATES THE PERVERSE CASE:")
    print("   Using MULTIPLE different LLMs in ONE LangGraph workflow!")
    print()
    print("📊 Jaeger UI: http://localhost:16686")
    print("   (Watch for LLM switches between DeepSeek and Claude)")
    print()

    # Start with mocks (set use_real_llms=True to test with actual APIs)
    use_real_llms = os.getenv("USE_REAL_LLMS", "false").lower() == "true"

    if use_real_llms:
        print("🔧 Using REAL LLMs (DeepSeek + Claude)")
        print("   Ensure: Ollama running, ANTHROPIC_API_KEY set")
    else:
        print("🔧 Using MOCK LLMs (for testing workflow logic)")
        print("   Set USE_REAL_LLMS=true to use real APIs")
    print()

    orchestrator = MultiLLMOrchestrator(max_iterations=2, use_real_llms=use_real_llms)

    test_tasks = [
        "Implement email validation function",
        "Create REST API endpoint"
    ]

    print("Running multi-LLM workflow examples:")
    print("-" * 80)

    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. Task: {task}")
        print("   " + "-" * 60)

        result = orchestrator.run_multi_llm_workflow(task)

        print(f"   Status: {result['approval_status']}")
        print(f"   Iterations: {result['iteration_count']}")
        print(f"   Last LLM: {result['last_llm_used']}")
        print(f"   DeepSeek code: {result['deepseek_generated_code'][:80]}...")
        print(f"   Claude review: {result['claude_review_result'][:80]}...")

    print()
    print("-" * 80)
    print("✅ All examples complete!")
    print()
    print("🔍 Check Jaeger UI to see:")
    print("   - LLM switches (deepseek → claude → deepseek)")
    print("   - State flow between different LLM contexts")
    print("   - Potential confusion at boundaries")
    print()
    print("💡 Key Learnings:")
    print("   1. Track which LLM was last used (last_llm_used field)")
    print("   2. Different LLMs may expect different formats")
    print("   3. Context can leak between LLM calls")
    print("   4. LangGraph handles model switches but YOU must manage state")
    print("   5. Use separate trace spans for each LLM")
    print()
    print("⚠️  Potential Issues:")
    print("   - LangChain model instances getting confused")
    print("   - Different response parsing for each LLM")
    print("   - Memory bleeding between models")
    print("   - State serialization across LLM boundaries")
    print("=" * 80)


if __name__ == "__main__":
    main()
