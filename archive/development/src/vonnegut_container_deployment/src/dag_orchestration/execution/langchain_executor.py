#!/usr/bin/env python3
"""
LangChain LLM Executor
=====================

Example implementation of LangChain integration for DAG orchestration.
Demonstrates how to extend the LLM orchestration system with LangChain capabilities.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

# Optional LangChain imports - graceful degradation if not available
try:
    from langchain.llms import OpenAI, Anthropic
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class LangChainExecutor(ReflectiveModule):
    """LangChain-based LLM executor for DAG orchestration tasks."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "LangChainExecutor"
        self.available_chains = self._initialize_chains() if LANGCHAIN_AVAILABLE else {}
        
    def get_capabilities(self) -> List[str]:
        return ["langchain_execution", "chain_composition", "memory_management", "streaming_operations"]
    
    def get_health_status(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if LANGCHAIN_AVAILABLE and self.available_chains else "degraded",
            "langchain_available": LANGCHAIN_AVAILABLE,
            "available_chains": list(self.available_chains.keys()),
            "total_chains": len(self.available_chains)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        return {
            "module_name": "LangChainExecutor",
            "version": "1.0.0",
            "description": "LangChain integration for DAG orchestration",
            "langchain_available": LANGCHAIN_AVAILABLE
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        return {
            "degradation_mode": "fallback_to_cli",
            "error": str(error),
            "available_operations": ["cli_fallback", "status_reporting"],
            "recovery_suggestions": ["Install LangChain", "Check API keys", "Use CLI fallback"]
        }
    
    def _initialize_chains(self) -> Dict[str, Any]:
        """Initialize available LangChain chains."""
        if not LANGCHAIN_AVAILABLE:
            return {}
        
        chains = {}
        
        # Task implementation chain
        task_prompt = PromptTemplate(
            input_variables=["task_id", "task_description", "spec_path", "requirements"],
            template="""
You are implementing a task in a DAG orchestration system.

Task ID: {task_id}
Task Description: {task_description}
Specification Path: {spec_path}
Requirements: {requirements}

Please implement this task following these guidelines:
1. Use systematic approaches and proven patterns
2. Implement comprehensive error handling and logging
3. Follow the ReflectiveModule pattern for observability
4. Include structured progress reporting
5. Ensure all cross-cutting concerns are addressed

Implementation:
"""
        )
        
        try:
            # OpenAI chain
            openai_llm = OpenAI(temperature=0.1, streaming=True)
            chains["openai"] = {
                "llm": openai_llm,
                "chain": LLMChain(llm=openai_llm, prompt=task_prompt, memory=ConversationBufferMemory()),
                "cost_model": "pay_per_token",
                "estimated_cost": 0.02
            }
        except Exception as e:
            logging.warning(f"OpenAI chain initialization failed: {e}")
        
        try:
            # Anthropic chain
            anthropic_llm = Anthropic(temperature=0.1, streaming=True)
            chains["anthropic"] = {
                "llm": anthropic_llm,
                "chain": LLMChain(llm=anthropic_llm, prompt=task_prompt, memory=ConversationBufferMemory()),
                "cost_model": "pay_per_token", 
                "estimated_cost": 0.015
            }
        except Exception as e:
            logging.warning(f"Anthropic chain initialization failed: {e}")
        
        return chains
    
    def execute_task_with_langchain(self, task_id: str, task_description: str, 
                                  spec_path: str, requirements: List[str] = None) -> Dict[str, Any]:
        """Execute a task using LangChain."""
        
        if not LANGCHAIN_AVAILABLE:
            return {
                "success": False,
                "error": "LangChain not available",
                "fallback": "cli_execution"
            }
        
        if not self.available_chains:
            return {
                "success": False,
                "error": "No LangChain chains available",
                "fallback": "cli_execution"
            }
        
        # Select best chain (prefer Anthropic for code tasks)
        chain_name = "anthropic" if "anthropic" in self.available_chains else list(self.available_chains.keys())[0]
        chain_config = self.available_chains[chain_name]
        
        try:
            # Prepare inputs
            inputs = {
                "task_id": task_id,
                "task_description": task_description,
                "spec_path": spec_path,
                "requirements": "\\n".join(requirements or [])
            }
            
            # Execute with streaming and logging
            print(f"🔗 Executing Task {task_id} with LangChain ({chain_name})")
            print(f"📝 Description: {task_description}")
            print(f"💰 Estimated cost: ${chain_config['estimated_cost']}")
            
            # Stream execution with tee-like logging
            result = chain_config["chain"].run(**inputs)
            
            # Log results
            execution_log = {
                "task_id": task_id,
                "chain_used": chain_name,
                "success": True,
                "result_length": len(result),
                "cost_incurred": chain_config["estimated_cost"]
            }
            
            print(f"✅ Task {task_id} completed with LangChain")
            
            return {
                "success": True,
                "result": result,
                "execution_log": execution_log,
                "chain_used": chain_name
            }
            
        except Exception as e:
            error_log = {
                "task_id": task_id,
                "chain_attempted": chain_name,
                "error": str(e),
                "success": False
            }
            
            print(f"❌ Task {task_id} failed with LangChain: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_log": error_log,
                "fallback": "cli_execution"
            }
    
    def create_streaming_chain(self, task_type: str) -> Optional[Any]:
        """Create a streaming chain for specific task types."""
        
        if not LANGCHAIN_AVAILABLE or not self.available_chains:
            return None
        
        # Task-specific prompt templates
        prompts = {
            "code_generation": """
Generate code for: {task_description}
Requirements: {requirements}
Output structured progress updates as you work.
""",
            "analysis": """
Analyze the following: {task_description}
Context: {context}
Provide systematic analysis with clear reasoning.
""",
            "documentation": """
Create documentation for: {task_description}
Include examples and clear explanations.
"""
        }
        
        if task_type not in prompts:
            task_type = "code_generation"  # Default
        
        prompt = PromptTemplate(
            input_variables=["task_description", "requirements", "context"],
            template=prompts[task_type]
        )
        
        # Use best available chain
        chain_name = "anthropic" if "anthropic" in self.available_chains else list(self.available_chains.keys())[0]
        llm = self.available_chains[chain_name]["llm"]
        
        return LLMChain(llm=llm, prompt=prompt, memory=ConversationBufferMemory())


# Integration function for the main LLM orchestrator
def create_langchain_executor() -> Optional[LangChainExecutor]:
    """Factory function to create LangChain executor with graceful degradation."""
    
    try:
        executor = LangChainExecutor()
        if executor.get_health_status()["status"] == "healthy":
            return executor
        else:
            print("⚠️  LangChain executor degraded - falling back to CLI execution")
            return None
    except Exception as e:
        print(f"❌ LangChain executor creation failed: {e}")
        return None


if __name__ == "__main__":
    # Test the LangChain executor
    executor = create_langchain_executor()
    
    if executor:
        print("✅ LangChain executor available")
        print(f"Health: {executor.get_health_status()}")
        
        # Test task execution
        result = executor.execute_task_with_langchain(
            task_id="test.1",
            task_description="Create a simple Python function that adds two numbers",
            spec_path=".kiro/specs/test",
            requirements=["Function should handle edge cases", "Include comprehensive error handling"]
        )
        
        print(f"Execution result: {result}")
    else:
        print("❌ LangChain executor not available - using CLI fallback")