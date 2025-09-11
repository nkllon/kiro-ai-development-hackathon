#!/usr/bin/env python3
"""
Project Context Manager - Context switching and management

Extracted from multi_project_manager.py for RM-DDD compliance.
Single responsibility: Project context switching and management.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import ProjectSummary, ContextSwitchResult

logger = logging.getLogger(__name__)


class ProjectContextManager:
    """Project context switching and management."""
    
    def __init__(self):
        """Initialize project context manager."""
        self.current_project_id: Optional[str] = None
        self.context_history: List[Dict[str, Any]] = []
        self.context_data: Dict[str, Any] = {}
    
    def switch_context(self, project_id: str, context_data: Optional[Dict[str, Any]] = None) -> ContextSwitchResult:
        """Switch to a different project context."""
        try:
            previous_project_id = self.current_project_id
            
            # Save current context if switching away
            if self.current_project_id and self.current_project_id != project_id:
                self._save_current_context()
            
            # Switch to new project
            self.current_project_id = project_id
            self.context_data = context_data or {}
            
            # Record context switch
            switch_record = {
                'from_project_id': previous_project_id,
                'to_project_id': project_id,
                'switch_time': datetime.now(),
                'context_data': self.context_data.copy()
            }
            self.context_history.append(switch_record)
            
            # Keep only last 10 context switches
            if len(self.context_history) > 10:
                self.context_history = self.context_history[-10:]
            
            return ContextSwitchResult(
                success=True,
                from_project_id=previous_project_id,
                to_project_id=project_id,
                context_data=self.context_data.copy()
            )
            
        except Exception as e:
            logger.error(f"Error switching context to {project_id}: {e}")
            return ContextSwitchResult(
                success=False,
                to_project_id=project_id,
                error_message=str(e)
            )
    
    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """Get current project context."""
        if not self.current_project_id:
            return None
        
        return {
            'project_id': self.current_project_id,
            'context_data': self.context_data.copy(),
            'switch_time': self.context_history[-1]['switch_time'] if self.context_history else None
        }
    
    def clear_context(self) -> bool:
        """Clear current project context."""
        try:
            if self.current_project_id:
                self._save_current_context()
            
            self.current_project_id = None
            self.context_data = {}
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing context: {e}")
            return False
    
    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get context switch history."""
        return self.context_history.copy()
    
    def is_context_active(self, project_id: str) -> bool:
        """Check if a project context is currently active."""
        return self.current_project_id == project_id
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context state."""
        return {
            'current_project_id': self.current_project_id,
            'context_data_keys': list(self.context_data.keys()),
            'history_length': len(self.context_history),
            'last_switch': self.context_history[-1] if self.context_history else None
        }
    
    def _save_current_context(self) -> None:
        """Save current context data."""
        if self.current_project_id and self.context_data:
            # In a real implementation, this would save to persistent storage
            logger.debug(f"Saving context for project {self.current_project_id}")
    
    def restore_context(self, project_id: str) -> bool:
        """Restore context for a project."""
        try:
            # In a real implementation, this would restore from persistent storage
            logger.debug(f"Restoring context for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring context for {project_id}: {e}")
            return False
    
    def validate_context_data(self, context_data: Dict[str, Any]) -> bool:
        """Validate context data structure."""
        if not isinstance(context_data, dict):
            return False
        
        # Add specific validation rules as needed
        return True
    
    def merge_context_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new context data with existing data."""
        if not self.validate_context_data(new_data):
            raise ValueError("Invalid context data structure")
        
        # Merge data, with new data taking precedence
        merged_data = self.context_data.copy()
        merged_data.update(new_data)
        
        return merged_data
    
    def get_context_metrics(self) -> Dict[str, Any]:
        """Get context management metrics."""
        return {
            'total_switches': len(self.context_history),
            'current_project_active': self.current_project_id is not None,
            'context_data_size': len(self.context_data),
            'average_switch_interval': self._calculate_average_switch_interval()
        }
    
    def _calculate_average_switch_interval(self) -> Optional[float]:
        """Calculate average time between context switches."""
        if len(self.context_history) < 2:
            return None
        
        intervals = []
        for i in range(1, len(self.context_history)):
            prev_time = self.context_history[i-1]['switch_time']
            curr_time = self.context_history[i]['switch_time']
            interval = (curr_time - prev_time).total_seconds()
            intervals.append(interval)
        
        return sum(intervals) / len(intervals) if intervals else None
