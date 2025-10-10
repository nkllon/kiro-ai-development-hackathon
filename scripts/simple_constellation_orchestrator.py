#!/usr/bin/env python3
"""
Simple Constellation Orchestrator for Testing
Works with existing prompts only
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass

@dataclass
class SimplePromptTask:
    """Simple prompt task for testing"""
    name: str
    prompt_file: str
    dependencies: List[str]
    status: str = "pending"
    
class ConstellationOrchestrator:
    """Simplified orchestrator for testing with existing prompts"""
    
    def __init__(self, max_agents: int = 3, status_file: str = "constellation_status.json"):
        self.max_agents = max_agents
        self.status_file = Path(status_file)
        self.prompts_dir = Path("prompts/staging")
        
        # Initialize status
        self.status = {
            "completed": set(),
            "running": set(),
            "failed": set(),
            "start_time": time.time()
        }
        
        # Load existing status if available
        self._load_status()
        
        # Define DAG with existing prompts only
        self.dag = self._create_simple_dag()
    
    def _create_simple_dag(self) -> Dict[str, List[str]]:
        """Create simple DAG with only existing prompts"""
        
        # Check which prompts actually exist
        existing_prompts = []
        for prompt_file in self.prompts_dir.glob("*.md"):
            existing_prompts.append(prompt_file.stem)
        
        # Define simple dependencies for existing prompts
        dag = {}
        
        # Core prompts that should exist
        core_prompts = [
            ("phase-1a-constellation-inventory", []),
            ("phase-1b-stakeholder-landscape-mapping", []),
            ("phase-1c-cms-dependency-discovery", []),
            ("phase-1d-ontology-gap-analysis", []),
            ("phase-1b1-stakeholder-extraction", ["phase-1b-stakeholder-landscape-mapping"]),
        ]
        
        # Add only existing prompts to DAG
        for prompt_name, deps in core_prompts:
            if prompt_name in existing_prompts:
                # Filter dependencies to only include existing prompts
                existing_deps = [dep for dep in deps if dep in existing_prompts]
                dag[prompt_name] = existing_deps
        
        # Add any other existing prompts with no dependencies
        for prompt_name in existing_prompts:
            if prompt_name not in dag:
                dag[prompt_name] = []
        
        return dag
    
    def get_ready_prompts(self) -> List[str]:
        """Get prompts that are ready to execute (dependencies satisfied)"""
        ready = []
        
        for prompt_id, dependencies in self.dag.items():
            # Skip if already completed, running, or failed
            if (prompt_id in self.status["completed"] or 
                prompt_id in self.status["running"] or
                prompt_id in self.status["failed"]):
                continue
            
            # Check if all dependencies are completed
            deps_satisfied = all(dep in self.status["completed"] for dep in dependencies)
            
            if deps_satisfied:
                ready.append(prompt_id)
        
        return ready
    
    def save_status(self):
        """Save status to file"""
        # Convert sets to lists for JSON serialization
        status_for_json = {
            "completed": list(self.status["completed"]),
            "running": list(self.status["running"]),
            "failed": list(self.status["failed"]),
            "start_time": self.status["start_time"]
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status_for_json, f, indent=2)
    
    def _load_status(self):
        """Load status from file"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    loaded_status = json.load(f)
                
                # Convert lists back to sets
                self.status["completed"] = set(loaded_status.get("completed", []))
                self.status["running"] = set(loaded_status.get("running", []))
                self.status["failed"] = set(loaded_status.get("failed", []))
                self.status["start_time"] = loaded_status.get("start_time", time.time())
                
            except Exception as e:
                print(f"Warning: Could not load status file: {e}")
                # Reset to defaults on load failure
                self.status = {
                    "completed": set(),
                    "running": set(),
                    "failed": set(),
                    "start_time": time.time()
                }
    
    async def execute_prompt(self, prompt_id: str, agent_id: int) -> Dict[str, Any]:
        """Execute a single prompt (to be overridden in tests)"""
        # This is the method that will be overridden in mock tests
        # or implemented for real execution
        
        prompt_file = self.prompts_dir / f"{prompt_id}.md"
        if not prompt_file.exists():
            return {
                "status": "failed",
                "error": f"Prompt file not found: {prompt_file}"
            }
        
        # Mark as running
        self.status["running"].add(prompt_id)
        self.save_status()
        
        try:
            # Real execution would happen here
            # For now, just simulate
            await asyncio.sleep(1)
            
            # Mark as completed
            self.status["running"].discard(prompt_id)
            self.status["completed"].add(prompt_id)
            self.save_status()
            
            return {
                "status": "completed",
                "prompt_id": prompt_id,
                "agent_id": agent_id
            }
            
        except Exception as e:
            # Mark as failed
            self.status["running"].discard(prompt_id)
            self.status["failed"].add(prompt_id)
            self.save_status()
            
            return {
                "status": "failed",
                "error": str(e)
            }