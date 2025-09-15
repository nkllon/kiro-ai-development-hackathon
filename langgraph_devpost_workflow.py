#!/usr/bin/env python3
"""
LangGraph DevPost Workflow
=========================

Main orchestrator for the DevPost automation workflow using LangGraph.
This brings together all the nodes and manages the flow between them.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage

from langgraph_devpost_state import (
    DevPostState, 
    WorkflowPhase, 
    create_initial_state,
    get_state_summary
)
from langgraph_devpost_nodes import (
    browser_connection_node,
    page_detection_node,
    form_analysis_node,
    form_population_node,
    form_submission_node,
    navigation_node,
    validation_node,
    completion_node,
    error_recovery_node
)
from session_recovery_node import session_recovery_node
from interactive_recovery_node import (
    interactive_recovery_node, 
    memory_qualification_node,
    handle_recovery_choice
)
from prompt_mode_node import prompt_mode_node, handle_prompt_mode_input
from ghostbusters_consultation_refactored import ghostbusters_consultation_refactored_node


class DevPostWorkflow:
    """
    LangGraph-based DevPost automation workflow.
    
    This class orchestrates the entire DevPost submission process using
    LangGraph's state management and conditional routing.
    """
    
    def __init__(self, workflow_id: Optional[str] = None):
        self.workflow_id = workflow_id
        self.memory = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow graph"""
        
        # Create the state graph
        workflow = StateGraph(DevPostState)
        
        # Add nodes for each phase
        workflow.add_node("browser_connection", browser_connection_node)
        workflow.add_node("session_recovery", session_recovery_node)
        workflow.add_node("prompt_mode", prompt_mode_node)
        workflow.add_node("ghostbusters_consultation", ghostbusters_consultation_refactored_node)
        workflow.add_node("interactive_recovery", interactive_recovery_node)
        workflow.add_node("memory_qualification", memory_qualification_node)
        workflow.add_node("page_detection", page_detection_node)
        workflow.add_node("form_analysis", form_analysis_node)
        workflow.add_node("form_population", form_population_node)
        workflow.add_node("form_submission", form_submission_node)
        workflow.add_node("navigation", navigation_node)
        workflow.add_node("validation", validation_node)
        workflow.add_node("completion", completion_node)
        workflow.add_node("error_recovery", error_recovery_node)
        
        # Define the workflow flow
        workflow.set_entry_point("browser_connection")
        
        # Add conditional edges based on workflow phase
        workflow.add_conditional_edges(
            "browser_connection",
            self._route_from_browser_connection,
            {
                "session_recovery": "session_recovery",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "session_recovery",
            self._route_from_session_recovery,
            {
                "prompt_mode": "prompt_mode",
                "ghostbusters_consultation": "ghostbusters_consultation",
                "interactive_recovery": "interactive_recovery",
                "memory_qualification": "memory_qualification",
                "page_detection": "page_detection",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "prompt_mode",
            self._route_from_prompt_mode,
            {
                "ghostbusters_consultation": "ghostbusters_consultation",
                "page_detection": "page_detection",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "ghostbusters_consultation",
            self._route_from_ghostbusters_consultation,
            {
                "prompt_mode": "prompt_mode",
                "page_detection": "page_detection",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "interactive_recovery",
            self._route_from_interactive_recovery,
            {
                "memory_qualification": "memory_qualification",
                "page_detection": "page_detection",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "memory_qualification",
            self._route_from_memory_qualification,
            {
                "page_detection": "page_detection",
                "interactive_recovery": "interactive_recovery",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "page_detection",
            self._route_from_page_detection,
            {
                "form_analysis": "form_analysis",
                "navigation": "navigation",
                "validation": "validation",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "form_analysis",
            self._route_from_form_analysis,
            {
                "form_population": "form_population",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "form_population",
            self._route_from_form_population,
            {
                "form_submission": "form_submission",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "form_submission",
            self._route_from_form_submission,
            {
                "navigation": "navigation",
                "page_detection": "page_detection",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "navigation",
            self._route_from_navigation,
            {
                "page_detection": "page_detection",
                "validation": "validation",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "validation",
            self._route_from_validation,
            {
                "completion": "completion",
                "error_recovery": "error_recovery",
                "end": END
            }
        )
        
        workflow.add_edge("completion", END)
        
        workflow.add_conditional_edges(
            "error_recovery",
            self._route_from_error_recovery,
            {
                "browser_connection": "browser_connection",
                "page_detection": "page_detection",
                "form_analysis": "form_analysis",
                "navigation": "navigation",
                "end": END
            }
        )
        
        return workflow.compile(checkpointer=self.memory)
    
    def _route_from_browser_connection(self, state: DevPostState) -> str:
        """Route after browser connection phase"""
        if state["browser_status"].value == "connected":
            return "session_recovery"
        elif state["browser_status"].value == "extension_available":
            return "session_recovery"
        elif state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        else:
            return "end"
    
    def _route_from_session_recovery(self, state: DevPostState) -> str:
        """Route after session recovery phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state.get("ghostbusters_mode", False):
            # GHOSTBUSTERS TIME! Need interactive recovery
            return "interactive_recovery"
        elif state.get("ghostbusters_autonomous_mode", False):
            # GHOSTBUSTERS AUTONOMOUS MODE - run consultation
            return "ghostbusters_consultation"
        elif state.get("prompt_mode", False):
            # PROMPT MODE - conversational decision-making
            return "prompt_mode"
        else:
            # Check if memory needs qualification
            memory_manager = state.get("memory_manager")
            if memory_manager and memory_manager.memory_qualification_queue:
                return "memory_qualification"
            else:
                # Proceed to page detection
                return "page_detection"
    
    def _route_from_prompt_mode(self, state: DevPostState) -> str:
        """Route after prompt mode phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state.get("user_input_required", False):
            # Still waiting for user input
            return "end"
        elif state.get("next_mode") == "ghostbusters_consultation":
            # User requested Ghostbusters consultation
            return "ghostbusters_consultation"
        elif state.get("next_mode") == "cautious_navigation":
            # User approved cautious navigation
            return "page_detection"
        elif state.get("next_mode") == "fresh_start":
            # User requested fresh start
            return "page_detection"
        else:
            # Continue in prompt mode or proceed to page detection
            return "page_detection"
    
    def _route_from_ghostbusters_consultation(self, state: DevPostState) -> str:
        """Route after Ghostbusters consultation phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state.get("next_mode") == "prompt_mode_consensus":
            # Return to Prompt Mode for consensus decision
            return "prompt_mode"
        else:
            # Proceed with Ghostbusters recommendations
            return "page_detection"
    
    def _route_from_interactive_recovery(self, state: DevPostState) -> str:
        """Route after interactive recovery phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state.get("user_input_required", False):
            # Still waiting for user input
            return "end"
        elif state.get("ready_to_quit", False):
            # User chose to quit
            return "end"
        else:
            # Check memory qualification before proceeding
            memory_manager = state.get("memory_manager")
            if memory_manager and memory_manager.memory_qualification_queue:
                return "memory_qualification"
            else:
                return "page_detection"
    
    def _route_from_memory_qualification(self, state: DevPostState) -> str:
        """Route after memory qualification phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state.get("awaiting_memory_qualification", False):
            # Still waiting for user qualification
            return "end"
        else:
            # Proceed to page detection
            return "page_detection"
    
    def _route_from_page_detection(self, state: DevPostState) -> str:
        """Route after page detection phase"""
        if state["current_page_type"].value == "login_required":
            return "error_recovery"
        elif state["current_page_type"].value in [
            "project_overview", "project_details", "manage_team", "additional_info"
        ]:
            return "form_analysis"
        elif state["current_page_type"].value == "submission_review":
            return "validation"
        elif state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        else:
            return "navigation"
    
    def _route_from_form_analysis(self, state: DevPostState) -> str:
        """Route after form analysis phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state["form_data"]:
            return "form_population"
        else:
            return "end"
    
    def _route_from_form_population(self, state: DevPostState) -> str:
        """Route after form population phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        else:
            return "form_submission"
    
    def _route_from_form_submission(self, state: DevPostState) -> str:
        """Route after form submission phase"""
        if state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        else:
            # Check if we need to detect the new page after submission
            return "page_detection"
    
    def _route_from_navigation(self, state: DevPostState) -> str:
        """Route after navigation phase"""
        if state["user_input_required"]:
            return "end"  # Wait for user input
        elif state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state["current_phase"] == WorkflowPhase.VALIDATION:
            return "validation"
        else:
            return "page_detection"
    
    def _route_from_validation(self, state: DevPostState) -> str:
        """Route after validation phase"""
        if state["submission_ready"]:
            return "completion"
        elif state["errors"] and state["recovery_attempts"] < state["max_recovery_attempts"]:
            return "error_recovery"
        elif state["user_input_required"]:
            return "end"  # Wait for user input
        else:
            return "completion"
    
    def _route_from_error_recovery(self, state: DevPostState) -> str:
        """Route after error recovery phase"""
        if state["recovery_attempts"] >= state["max_recovery_attempts"]:
            return "end"
        elif state["current_phase"] == WorkflowPhase.BROWSER_CONNECTION:
            return "browser_connection"
        elif state["current_phase"] == WorkflowPhase.PAGE_DETECTION:
            return "page_detection"
        elif state["current_phase"] == WorkflowPhase.FORM_ANALYSIS:
            return "form_analysis"
        else:
            return "navigation"
    
    def run_workflow(
        self, 
        user_data_dir: str = "/tmp/devpost-browser",
        automation_mode: str = "interactive"
    ) -> Dict[str, Any]:
        """
        Run the complete DevPost automation workflow.
        
        Args:
            user_data_dir: Directory to store browser session data
            automation_mode: Mode of operation ("interactive", "automatic", "guided")
            
        Returns:
            Dictionary containing workflow results and summary
        """
        
        print("🚀 Starting DevPost Automation Workflow")
        print(f"📁 User data directory: {user_data_dir}")
        print(f"🤖 Automation mode: {automation_mode}")
        
        # Create initial state
        initial_state = create_initial_state(
            workflow_id=self.workflow_id,
            user_data_dir=user_data_dir,
            automation_mode=automation_mode
        )
        
        # Run the workflow
        try:
            config = {"configurable": {"thread_id": initial_state["workflow_id"]}}
            
            # Stream the execution
            final_state = None
            for state in self.graph.stream(initial_state, config=config):
                print(f"🔄 Phase: {state.get('current_phase', 'Unknown')}")
                
                # Print messages from the current step
                messages = state.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    if isinstance(last_message, AIMessage):
                        print(f"   {last_message.content}")
                
                # Check for errors
                errors = state.get("errors", [])
                if errors:
                    print(f"   ⚠️ Errors: {errors[-1]}")
                
                final_state = state
            
            if final_state:
                # Get final summary
                summary = get_state_summary(final_state)
                
                print("\n🎉 Workflow Completed!")
                print("📊 Final Summary:")
                for key, value in summary.items():
                    print(f"   {key}: {value}")
                
                return {
                    "success": True,
                    "final_state": final_state,
                    "summary": summary,
                    "workflow_id": final_state["workflow_id"]
                }
            else:
                return {
                    "success": False,
                    "error": "Workflow completed without final state",
                    "workflow_id": initial_state["workflow_id"]
                }
                
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": initial_state["workflow_id"]
            }
    
    def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Resume a previously started workflow"""
        
        print(f"🔄 Resuming workflow: {workflow_id}")
        
        try:
            config = {"configurable": {"thread_id": workflow_id}}
            
            # Get current state
            current_state = self.graph.get_state(config)
            
            if current_state:
                print(f"📍 Current phase: {current_state.values.get('current_phase', 'Unknown')}")
                
                # Resume from current state
                final_state = None
                for state in self.graph.stream(None, config=config):
                    print(f"🔄 Phase: {state.get('current_phase', 'Unknown')}")
                    final_state = state
                
                if final_state:
                    summary = get_state_summary(final_state)
                    return {
                        "success": True,
                        "final_state": final_state,
                        "summary": summary,
                        "workflow_id": workflow_id
                    }
            
            return {
                "success": False,
                "error": f"Could not resume workflow {workflow_id}",
                "workflow_id": workflow_id
            }
            
        except Exception as e:
            print(f"❌ Resume failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow"""
        
        try:
            config = {"configurable": {"thread_id": workflow_id}}
            state = self.graph.get_state(config)
            
            if state:
                return {
                    "workflow_id": workflow_id,
                    "current_phase": state.values.get("current_phase", "Unknown"),
                    "status": "running" if state.next else "completed",
                    "errors": state.values.get("errors", []),
                    "user_input_required": state.values.get("user_input_required", False),
                    "ghostbusters_mode": state.values.get("ghostbusters_mode", False),
                    "awaiting_recovery_choice": state.values.get("awaiting_recovery_choice", False),
                    "awaiting_memory_qualification": state.values.get("awaiting_memory_qualification", False),
                    "summary": get_state_summary(state.values)
                }
            else:
                return {
                    "workflow_id": workflow_id,
                    "status": "not_found"
                }
                
        except Exception as e:
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e)
            }
    
    def handle_user_input(self, workflow_id: str, user_input: str) -> Dict[str, Any]:
        """
        Handle user input for interactive recovery or memory qualification
        
        Args:
            workflow_id: The workflow ID to handle input for
            user_input: User's input/choice
            
        Returns:
            Dictionary containing the result of handling the input
        """
        
        try:
            config = {"configurable": {"thread_id": workflow_id}}
            current_state = self.graph.get_state(config)
            
            if not current_state:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }
            
            state_values = current_state.values
            
            # Check what type of input is needed
            if state_values.get("awaiting_recovery_choice", False):
                # Handle recovery choice
                updated_state = handle_recovery_choice(state_values, user_input)
                
                # Update the workflow state
                for state in self.graph.stream(updated_state, config=config):
                    pass
                
                return {
                    "success": True,
                    "message": "Recovery choice handled",
                    "next_action": "continue_workflow"
                }
                
            elif state_values.get("awaiting_memory_qualification", False):
                # Handle memory qualification
                memory_manager = state_values.get("memory_manager")
                if memory_manager:
                    # Parse user qualification input
                    # Expected format: "1: persist, 2: discard, 3: transform - make it shorter"
                    try:
                        qualifications = user_input.split(",")
                        for qual in qualifications:
                            qual = qual.strip()
                            if ":" in qual:
                                item_num, decision = qual.split(":", 1)
                                item_num = int(item_num.strip()) - 1  # Convert to 0-based index
                                decision = decision.strip()
                                
                                if decision.startswith("transform"):
                                    transform_instruction = decision.replace("transform", "").strip()
                                    decision = "transform"
                                else:
                                    transform_instruction = ""
                                
                                # Apply qualification
                                qualification_queue = memory_manager.memory_qualification_queue
                                if 0 <= item_num < len(qualification_queue):
                                    memory_manager.qualify_memory(
                                        qualification_queue[item_num]["key"],
                                        decision,
                                        transform_instruction
                                    )
                        
                        # Update state
                        state_values["awaiting_memory_qualification"] = False
                        
                        # Continue workflow
                        for state in self.graph.stream(state_values, config=config):
                            pass
                        
                        return {
                            "success": True,
                            "message": "Memory qualification handled",
                            "next_action": "continue_workflow"
                        }
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to parse memory qualification: {str(e)}"
                        }
                else:
                    return {
                        "success": False,
                        "error": "Memory manager not available"
                    }
            
            else:
                return {
                    "success": False,
                    "error": "No user input expected at this time"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to handle user input: {str(e)}"
            }


def create_devpost_workflow(workflow_id: Optional[str] = None) -> DevPostWorkflow:
    """Factory function to create a DevPost workflow instance"""
    return DevPostWorkflow(workflow_id)


def main():
    """Main function for testing the workflow"""
    
    # Create and run workflow
    workflow = create_devpost_workflow()
    result = workflow.run_workflow()
    
    if result["success"]:
        print("✅ Workflow completed successfully!")
    else:
        print(f"❌ Workflow failed: {result['error']}")


if __name__ == "__main__":
    main()
