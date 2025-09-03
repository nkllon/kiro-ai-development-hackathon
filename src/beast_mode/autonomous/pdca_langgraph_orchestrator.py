"""
Beast Mode Framework - Autonomous PDCA LangGraph Orchestrator
Creates self-improving task execution loop using local LLM instances
No API keys required - uses local Ollama/similar for autonomous operation
"""

from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from pathlib import Path

# LangGraph imports (would need: pip install langgraph)
try:
    from langgraph import StateGraph, END
    from langgraph.graph import Graph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not available - install with: pip install langgraph")

from ..core.reflective_module import ReflectiveModule, HealthStatus

class PDCAState(TypedDict):
    """State that flows through the PDCA graph"""
    current_task: str
    task_context: Dict[str, Any]
    plan_result: Optional[Dict[str, Any]]
    do_result: Optional[Dict[str, Any]]
    check_result: Optional[Dict[str, Any]]
    act_result: Optional[Dict[str, Any]]
    learning_history: List[Dict[str, Any]]
    cycle_count: int
    should_continue: bool
    error_state: Optional[str]

@dataclass
class LocalLLMConfig:
    """Configuration for local LLM instances"""
    model_name: str = "llama2"  # or "codellama", "mistral", etc.
    base_url: str = "http://localhost:11434"  # Ollama default
    temperature: float = 0.1  # Low for systematic approach
    max_tokens: int = 4000
    timeout: int = 300

class PDCALangGraphOrchestrator(ReflectiveModule):
    """
    Autonomous PDCA orchestrator using LangGraph and local LLMs
    Creates self-improving task execution without external API dependencies
    """
    
    def __init__(self, llm_config: Optional[LocalLLMConfig] = None):
        super().__init__("pdca_langgraph_orchestrator")
        
        self.llm_config = llm_config or LocalLLMConfig()
        self.graph = None
        self.learning_database = []
        self.execution_history = []
        
        # PDCA prompts for different phases
        self.pdca_prompts = {
            "plan": """
You are a systematic planning agent for Beast Mode Framework tasks.
Analyze the task and create a detailed execution plan.

Task: {task}
Context: {context}
Previous Learning: {learning}

Create a systematic plan that:
1. Identifies all requirements and constraints
2. Breaks down into concrete steps
3. Anticipates potential issues
4. Defines success criteria
5. Maintains no-workaround approach (C-03)

Return JSON with: {{
    "plan_steps": [...],
    "success_criteria": [...],
    "constraints_to_monitor": [...],
    "risk_mitigation": [...],
    "estimated_effort": "...",
    "confidence_level": 0.0-1.0
}}
""",
            
            "do": """
You are a systematic execution agent for Beast Mode Framework.
Execute the planned task with systematic approach.

Plan: {plan}
Task Context: {context}
Learning History: {learning}

Execute systematically:
1. Follow the plan precisely
2. Reject any workarounds (C-03)
3. Implement with quality focus
4. Generate evidence of systematic approach
5. Track constraint satisfaction

Return JSON with: {{
    "execution_steps_completed": [...],
    "code_files_created": [...],
    "tests_implemented": [...],
    "constraints_satisfied": {...},
    "systematic_evidence": [...],
    "issues_encountered": [...]
}}
""",
            
            "check": """
You are a systematic validation agent for Beast Mode Framework.
Validate the execution results against plan and constraints.

Plan: {plan}
Execution Result: {execution}
Context: {context}

Validate systematically:
1. Check all success criteria met
2. Verify constraint satisfaction
3. Validate systematic approach maintained
4. Assess code quality and evidence
5. Identify gaps or issues

Return JSON with: {{
    "validation_passed": true/false,
    "success_criteria_met": {...},
    "constraint_satisfaction": {...},
    "systematic_approach_score": 0.0-1.0,
    "quality_assessment": {...},
    "issues_found": [...],
    "recommendations": [...]
}}
""",
            
            "act": """
You are a systematic improvement agent for Beast Mode Framework.
Generate improvements and learning from the PDCA cycle.

Plan: {plan}
Execution: {execution}
Validation: {validation}
Previous Learning: {learning}

Generate systematic improvements:
1. Extract key learnings from this cycle
2. Identify optimization opportunities
3. Update systematic approach patterns
4. Generate recommendations for next tasks
5. Build cumulative intelligence

Return JSON with: {{
    "key_learnings": [...],
    "optimization_opportunities": [...],
    "systematic_patterns_updated": [...],
    "next_task_recommendations": [...],
    "cumulative_intelligence": {...},
    "confidence_in_learning": 0.0-1.0
}}
"""
        }
        
        if LANGGRAPH_AVAILABLE:
            self._build_pdca_graph()
            
        self._update_health_indicator(
            "pdca_orchestrator",
            HealthStatus.HEALTHY if LANGGRAPH_AVAILABLE else HealthStatus.DEGRADED,
            "ready" if LANGGRAPH_AVAILABLE else "langgraph_missing",
            "PDCA orchestrator ready" if LANGGRAPH_AVAILABLE else "LangGraph not available"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """PDCA orchestrator operational status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "llm_config": {
                "model": self.llm_config.model_name,
                "base_url": self.llm_config.base_url
            },
            "learning_entries": len(self.learning_database),
            "execution_cycles": len(self.execution_history),
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for PDCA orchestration capability"""
        return LANGGRAPH_AVAILABLE and not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for PDCA orchestration"""
        return {
            "orchestration_capability": {
                "status": "healthy" if LANGGRAPH_AVAILABLE else "degraded",
                "langgraph_available": LANGGRAPH_AVAILABLE,
                "graph_built": self.graph is not None
            },
            "learning_system": {
                "status": "healthy" if len(self.learning_database) > 0 else "degraded",
                "learning_entries": len(self.learning_database),
                "execution_cycles": len(self.execution_history)
            },
            "llm_connectivity": {
                "status": "unknown",  # Would need to test connection
                "model": self.llm_config.model_name,
                "endpoint": self.llm_config.base_url
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Autonomous PDCA orchestration"""
        return "autonomous_pdca_orchestration_with_local_llms"
        
    def _build_pdca_graph(self):
        """Build the LangGraph PDCA workflow"""
        if not LANGGRAPH_AVAILABLE:
            return
            
        # Create the state graph
        workflow = StateGraph(PDCAState)
        
        # Add PDCA nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("do", self._do_node) 
        workflow.add_node("check", self._check_node)
        workflow.add_node("act", self._act_node)
        workflow.add_node("continue_decision", self._continue_decision_node)
        
        # Define the flow
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "do")
        workflow.add_edge("do", "check")
        workflow.add_edge("check", "act")
        workflow.add_edge("act", "continue_decision")
        
        # Conditional edges from continue_decision
        workflow.add_conditional_edges(
            "continue_decision",
            self._should_continue,
            {
                "continue": "plan",  # Loop back for next task
                "end": END
            }
        )
        
        self.graph = workflow.compile()
        self.logger.info("PDCA LangGraph workflow built successfully")
        
    async def _plan_node(self, state: PDCAState) -> PDCAState:
        """Plan phase: Systematic task planning"""
        try:
            prompt = self.pdca_prompts["plan"].format(
                task=state["current_task"],
                context=json.dumps(state["task_context"], indent=2),
                learning=json.dumps(state["learning_history"][-5:], indent=2)  # Last 5 learnings
            )
            
            # Call local LLM (would implement actual LLM call)
            plan_result = await self._call_local_llm(prompt, "plan")
            
            state["plan_result"] = plan_result
            state["error_state"] = None
            
            self.logger.info(f"Plan phase completed for task: {state['current_task']}")
            return state
            
        except Exception as e:
            self.logger.error(f"Plan phase failed: {e}")
            state["error_state"] = f"plan_failed: {e}"
            return state
            
    async def _do_node(self, state: PDCAState) -> PDCAState:
        """Do phase: Systematic task execution"""
        try:
            if state["error_state"]:
                return state
                
            prompt = self.pdca_prompts["do"].format(
                plan=json.dumps(state["plan_result"], indent=2),
                context=json.dumps(state["task_context"], indent=2),
                learning=json.dumps(state["learning_history"][-5:], indent=2)
            )
            
            do_result = await self._call_local_llm(prompt, "do")
            
            state["do_result"] = do_result
            
            self.logger.info(f"Do phase completed for task: {state['current_task']}")
            return state
            
        except Exception as e:
            self.logger.error(f"Do phase failed: {e}")
            state["error_state"] = f"do_failed: {e}"
            return state
            
    async def _check_node(self, state: PDCAState) -> PDCAState:
        """Check phase: Systematic validation"""
        try:
            if state["error_state"]:
                return state
                
            prompt = self.pdca_prompts["check"].format(
                plan=json.dumps(state["plan_result"], indent=2),
                execution=json.dumps(state["do_result"], indent=2),
                context=json.dumps(state["task_context"], indent=2)
            )
            
            check_result = await self._call_local_llm(prompt, "check")
            
            state["check_result"] = check_result
            
            self.logger.info(f"Check phase completed for task: {state['current_task']}")
            return state
            
        except Exception as e:
            self.logger.error(f"Check phase failed: {e}")
            state["error_state"] = f"check_failed: {e}"
            return state
            
    async def _act_node(self, state: PDCAState) -> PDCAState:
        """Act phase: Learning and improvement"""
        try:
            if state["error_state"]:
                return state
                
            prompt = self.pdca_prompts["act"].format(
                plan=json.dumps(state["plan_result"], indent=2),
                execution=json.dumps(state["do_result"], indent=2),
                validation=json.dumps(state["check_result"], indent=2),
                learning=json.dumps(state["learning_history"][-10:], indent=2)
            )
            
            act_result = await self._call_local_llm(prompt, "act")
            
            state["act_result"] = act_result
            
            # Add learning to history
            learning_entry = {
                "timestamp": datetime.now().isoformat(),
                "task": state["current_task"],
                "cycle_count": state["cycle_count"],
                "plan": state["plan_result"],
                "execution": state["do_result"],
                "validation": state["check_result"],
                "learning": act_result
            }
            
            state["learning_history"].append(learning_entry)
            self.learning_database.append(learning_entry)
            
            state["cycle_count"] += 1
            
            self.logger.info(f"Act phase completed - Learning captured for task: {state['current_task']}")
            return state
            
        except Exception as e:
            self.logger.error(f"Act phase failed: {e}")
            state["error_state"] = f"act_failed: {e}"
            return state
            
    async def _continue_decision_node(self, state: PDCAState) -> PDCAState:
        """Decide whether to continue with next task or end"""
        # Logic to determine if there are more tasks to process
        # This would check the task list and update current_task
        
        # For now, simple logic - could be enhanced
        if state["cycle_count"] >= 10:  # Max cycles
            state["should_continue"] = False
        else:
            # Check if there are more tasks (would integrate with task list)
            state["should_continue"] = False  # Placeholder
            
        return state
        
    def _should_continue(self, state: PDCAState) -> str:
        """Conditional edge function"""
        return "continue" if state["should_continue"] else "end"
        
    async def _call_local_llm(self, prompt: str, phase: str) -> Dict[str, Any]:
        """Call local LLM instance (Ollama, etc.)"""
        # This would implement actual local LLM calls
        # For now, return mock response
        
        mock_responses = {
            "plan": {
                "plan_steps": ["Step 1", "Step 2", "Step 3"],
                "success_criteria": ["Criteria 1", "Criteria 2"],
                "constraints_to_monitor": ["C-03", "C-05"],
                "risk_mitigation": ["Risk 1 mitigation"],
                "estimated_effort": "medium",
                "confidence_level": 0.8
            },
            "do": {
                "execution_steps_completed": ["Implemented core logic", "Added tests"],
                "code_files_created": ["module.py", "test_module.py"],
                "tests_implemented": ["test_basic_functionality"],
                "constraints_satisfied": {"C-03": True, "C-05": True},
                "systematic_evidence": ["No workarounds used", "Systematic approach maintained"],
                "issues_encountered": []
            },
            "check": {
                "validation_passed": True,
                "success_criteria_met": {"criteria_1": True, "criteria_2": True},
                "constraint_satisfaction": {"C-03": True, "C-05": True},
                "systematic_approach_score": 0.9,
                "quality_assessment": {"code_quality": "high", "test_coverage": "good"},
                "issues_found": [],
                "recommendations": ["Continue with systematic approach"]
            },
            "act": {
                "key_learnings": ["Systematic approach works well", "Constraint resolution effective"],
                "optimization_opportunities": ["Cache common patterns", "Improve test automation"],
                "systematic_patterns_updated": ["Pattern 1 refined"],
                "next_task_recommendations": ["Apply learned patterns", "Focus on constraint satisfaction"],
                "cumulative_intelligence": {"total_cycles": 1, "success_rate": 1.0},
                "confidence_in_learning": 0.85
            }
        }
        
        # Simulate LLM call delay
        await asyncio.sleep(0.1)
        
        return mock_responses.get(phase, {})
        
    async def execute_autonomous_pdca_loop(self, initial_task: str, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomous PDCA loop for task completion"""
        if not self.graph:
            raise RuntimeError("PDCA graph not available - LangGraph not installed")
            
        initial_state = PDCAState(
            current_task=initial_task,
            task_context=task_context,
            plan_result=None,
            do_result=None,
            check_result=None,
            act_result=None,
            learning_history=self.learning_database.copy(),
            cycle_count=0,
            should_continue=True,
            error_state=None
        )
        
        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Store execution history
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "task": initial_task,
                "cycles_completed": final_state["cycle_count"],
                "success": final_state["error_state"] is None,
                "learning_generated": len(final_state["learning_history"]) > len(initial_state["learning_history"])
            }
            
            self.execution_history.append(execution_record)
            
            return {
                "success": final_state["error_state"] is None,
                "cycles_completed": final_state["cycle_count"],
                "learning_entries_added": len(final_state["learning_history"]) - len(initial_state["learning_history"]),
                "final_state": final_state,
                "execution_record": execution_record
            }
            
        except Exception as e:
            self.logger.error(f"Autonomous PDCA execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "cycles_completed": 0,
                "learning_entries_added": 0
            }
            
    def get_learning_intelligence(self) -> Dict[str, Any]:
        """Extract cumulative learning intelligence"""
        if not self.learning_database:
            return {"status": "no_learning_data"}
            
        # Analyze learning patterns
        total_cycles = len(self.learning_database)
        successful_cycles = sum(1 for entry in self.learning_database 
                              if entry.get("validation", {}).get("validation_passed", False))
        
        # Extract common patterns
        common_learnings = {}
        optimization_opportunities = []
        
        for entry in self.learning_database:
            learning = entry.get("learning", {})
            for key_learning in learning.get("key_learnings", []):
                common_learnings[key_learning] = common_learnings.get(key_learning, 0) + 1
                
            optimization_opportunities.extend(learning.get("optimization_opportunities", []))
            
        return {
            "total_cycles": total_cycles,
            "success_rate": successful_cycles / max(1, total_cycles),
            "common_learnings": dict(sorted(common_learnings.items(), key=lambda x: x[1], reverse=True)[:10]),
            "optimization_opportunities": list(set(optimization_opportunities)),
            "learning_trend": "improving" if total_cycles > 5 else "building",
            "systematic_approach_effectiveness": self._calculate_systematic_effectiveness()
        }
        
    def _calculate_systematic_effectiveness(self) -> float:
        """Calculate effectiveness of systematic approach"""
        if not self.learning_database:
            return 0.0
            
        # Analyze constraint satisfaction rates
        constraint_satisfaction_scores = []
        for entry in self.learning_database:
            validation = entry.get("validation", {})
            systematic_score = validation.get("systematic_approach_score", 0.0)
            constraint_satisfaction_scores.append(systematic_score)
            
        return sum(constraint_satisfaction_scores) / len(constraint_satisfaction_scores) if constraint_satisfaction_scores else 0.0