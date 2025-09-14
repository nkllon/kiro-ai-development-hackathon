from datetime import datetime
from typing import Dict, List, Any

    def create_command(cls, command_type: str, task_id: str, name: str, description: str) -> TaskCommand:
        """create_command - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Create a command instance based on type."""
        command_class = cls._command_registry.get(command_type)
        if not command_class:
            raise ValueError(f"Unknown command type: {command_type}")
        
        return command_class(task_id, name, description)
    
    @classmethod