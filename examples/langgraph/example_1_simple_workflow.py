#!/usr/bin/env python3
"""
LangGraph Example 1: Simple Workflow
=====================================

Demonstrates basic LangGraph concepts:
- StateGraph with TypedDict state schema
- Simple node functions
- Linear workflow: Input → Process → Output

Integration with Beast Mode:
- Extends ReflectiveModule for built-in Jaeger tracing
- Uses trace_operation() context manager
- Auto-registers with Runtime State Registry

Run with Jaeger UI at: http://localhost:16686
"""

import os
import sys
from typing import TypedDict, Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from langgraph.graph import StateGraph, END
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install with: pip install langgraph")
    sys.exit(1)


# State Schema - TypedDict defines the structure of state flowing through the graph
class SimpleWorkflowState(TypedDict):
    """State that flows through the workflow"""
    input_text: str
    processed_text: str
    output_text: str
    timestamp: str
    step_count: int


class SimpleWorkflowOrchestrator(ReflectiveModule):
    """
    Simple LangGraph workflow orchestrator.

    Extends ReflectiveModule to get:
    - Jaeger tracing via trace_operation()
    - Prometheus metrics
    - Redis auto-registration
    - Health monitoring
    """

    def __init__(self):
        super().__init__()
        self.module_id = "SimpleWorkflowOrchestrator"
        self._logger.info("🚀 Initializing Simple Workflow Orchestrator")
        self.graph = self._create_graph()

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "module_name": "SimpleWorkflowOrchestrator",
            "version": "1.0.0",
            "description": "Simple LangGraph workflow example",
            "graph_nodes": ["input_node", "process_node", "output_node"]
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING
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
            "recovery_suggestions": ["Check LangGraph installation", "Verify state schema"]
        }

    # Node Functions - Each node is a simple function that takes state and returns updated state

    def input_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """
        First node: Receives input and initializes state.

        Pattern: Nodes receive state dict, modify it, return it.
        """
        with self.trace_operation("input_node", input=state.get("input_text", "")):
            self._logger.info(f"📥 Input Node: {state.get('input_text', '')}")

            # Update state
            state["timestamp"] = datetime.now().isoformat()
            state["step_count"] = state.get("step_count", 0) + 1

            self._logger.info(f"✅ Input processed, step {state['step_count']}")
            return state

    def process_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """
        Second node: Processes the input text.

        Pattern: Read from state, transform, write back to state.
        """
        with self.trace_operation("process_node", step=state["step_count"]):
            self._logger.info(f"⚙️  Process Node: step {state['step_count']}")

            # Simple processing: uppercase the input
            input_text = state.get("input_text", "")
            processed = input_text.upper()

            state["processed_text"] = processed
            state["step_count"] += 1

            self._logger.info(f"✅ Processed: {processed[:50]}...")
            return state

    def output_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """
        Final node: Generates output.

        Pattern: Read processed data, create final output.
        """
        with self.trace_operation("output_node", step=state["step_count"]):
            self._logger.info(f"📤 Output Node: step {state['step_count']}")

            # Create output message
            output = f"[{state['timestamp']}] Processed: {state['processed_text']}"
            state["output_text"] = output
            state["step_count"] += 1

            self._logger.info(f"✅ Output generated: {output[:50]}...")
            return state

    def _create_graph(self) -> StateGraph:
        """
        Create the LangGraph workflow.

        Graph structure:
        START → input_node → process_node → output_node → END
        """
        with self.trace_operation("create_graph"):
            self._logger.info("🔨 Building LangGraph workflow")

            # Create graph with our state schema
            workflow = StateGraph(SimpleWorkflowState)

            # Add nodes
            workflow.add_node("input_node", self.input_node)
            workflow.add_node("process_node", self.process_node)
            workflow.add_node("output_node", self.output_node)

            # Add edges - defines the flow
            workflow.set_entry_point("input_node")  # Start here
            workflow.add_edge("input_node", "process_node")  # input → process
            workflow.add_edge("process_node", "output_node")  # process → output
            workflow.add_edge("output_node", END)  # output → END

            # Compile the graph
            compiled = workflow.compile()

            self._logger.info("✅ LangGraph workflow compiled")
            return compiled

    def run_workflow(self, input_text: str) -> Dict[str, Any]:
        """
        Execute the workflow with given input.

        Returns the final state.
        """
        with self.trace_operation("run_workflow", input_length=len(input_text)):
            self._logger.info(f"🚀 Running workflow with input: {input_text[:50]}...")

            # Create initial state
            initial_state: SimpleWorkflowState = {
                "input_text": input_text,
                "processed_text": "",
                "output_text": "",
                "timestamp": "",
                "step_count": 0
            }

            # Execute the graph
            result = self.graph.invoke(initial_state)

            self._logger.info(f"✅ Workflow complete: {result['step_count']} steps")
            return result


def main():
    """Run the simple workflow example"""
    print("=" * 80)
    print("LangGraph Example 1: Simple Workflow")
    print("=" * 80)
    print()
    print("📊 Jaeger UI: http://localhost:16686")
    print("   (View traces to see workflow execution)")
    print()

    # Create orchestrator (ReflectiveModule auto-starts Jaeger tracing)
    orchestrator = SimpleWorkflowOrchestrator()

    # Test inputs
    test_inputs = [
        "Hello, LangGraph!",
        "This is a simple workflow example",
        "Testing node execution and state flow"
    ]

    print("Running workflow examples:")
    print("-" * 80)

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n{i}. Input: {test_input}")

        result = orchestrator.run_workflow(test_input)

        print(f"   Output: {result['output_text']}")
        print(f"   Steps: {result['step_count']}")
        print(f"   Timestamp: {result['timestamp']}")

    print()
    print("-" * 80)
    print("✅ All examples complete!")
    print()
    print("🔍 Check Jaeger UI to see traces:")
    print("   http://localhost:16686")
    print("   - Service: beast-mode")
    print("   - Operations: run_workflow, input_node, process_node, output_node")
    print()
    print("💡 Key Learnings:")
    print("   1. StateGraph takes TypedDict schema")
    print("   2. Nodes are simple functions: state → state")
    print("   3. Edges define workflow flow")
    print("   4. ReflectiveModule gives Jaeger tracing for free")
    print("=" * 80)


if __name__ == "__main__":
    main()
