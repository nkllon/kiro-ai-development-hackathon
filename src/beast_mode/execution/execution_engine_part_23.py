from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _assign_tasks(self, ready_tasks: List[Task], available_agents: List[Agent]) -> int:
        """Assign ready tasks to available agents."""
        assignments_made = 0
        
        for task in ready_tasks:
            if not available_agents:
                break
            
            best_agent = self.agent_manager.find_best_agent(task, available_agents)
            
            if best_agent:
                if self.agent_manager.assign_task(best_agent.id, task.id):
                    # Start the task
                    self.task_manager.start_task(task.id, best_agent.id)
                    
                    # Execute the task immediately (simulated)
                    success = self.task_manager.execute_task(task.id)
                    
                    # Release the agent
                    self.agent_manager.release_agent(best_agent.id)
                    
                    available_agents.remove(best_agent)
                    assignments_made += 1
                    
                    self.logger.info(f"Task {task.id} {'completed' if success else 'failed'}")
        
        return assignments_made

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    