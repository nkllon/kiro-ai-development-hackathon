"""
AI Memory Palace Context Validator

Validates context integrity and mathematical governance compliance.
"""

import logging
from typing import Dict, Any, List, Set, Optional, Tuple
from datetime import datetime

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..models.context_models import SessionContext, ContextEvent


class ContextValidator(ReflectiveModule):
    """Validates context integrity and DAG compliance."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def validate_dag_integrity(self, context: SessionContext) -> Dict[str, Any]:
        """Validate DAG integrity for mathematical governance."""
        try:
            # Extract events and their dependencies
            events = context.conversation_history
            
            # Build dependency graph
            graph = {}
            for event in events:
                if isinstance(event, dict) and 'id' in event:
                    event_id = event['id']
                    dependencies = event.get('dependencies', [])
                    graph[event_id] = dependencies
            
            # Check for cycles using DFS
            cycles = self._detect_cycles(graph)
            
            # Validate topological ordering
            topo_order = self._topological_sort(graph)
            
            return {
                "is_valid_dag": len(cycles) == 0,
                "cycles_detected": cycles,
                "topological_order": topo_order,
                "total_events": len(events),
                "validation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"DAG validation failed: {e}")
            return {
                "is_valid_dag": False,
                "error": str(e),
                "validation_timestamp": datetime.now().isoformat()
            }
    
    def _detect_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect cycles in dependency graph using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor, path + [node]):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort of dependency graph."""
        in_degree = {node: 0 for node in graph}
        
        # Calculate in-degrees
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Remove edges from this node
            for neighbor in graph.get(node, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        return result
    
    def check_context_consistency(self, context: SessionContext) -> Dict[str, Any]:
        """Check context consistency and integrity."""
        try:
            issues = []
            
            # Check basic structure
            if not context.project_id:
                issues.append("Missing project_id")
            
            if not context.session_id:
                issues.append("Missing session_id")
            
            # Check timestamp validity
            if context.timestamp > datetime.now():
                issues.append("Future timestamp detected")
            
            # Check conversation history structure
            for i, item in enumerate(context.conversation_history):
                if not isinstance(item, dict):
                    issues.append(f"Invalid conversation item at index {i}")
            
            # Check project state
            if context.project_state:
                if not context.project_state.architecture_overview:
                    issues.append("Missing architecture overview")
            
            return {
                "is_consistent": len(issues) == 0,
                "issues": issues,
                "validation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Consistency check failed: {e}")
            return {
                "is_consistent": False,
                "issues": [f"Validation error: {str(e)}"],
                "validation_timestamp": datetime.now().isoformat()
            }
    
    def repair_context_corruption(self, corrupted_context: SessionContext) -> Tuple[SessionContext, Dict[str, Any]]:
        """Attempt to repair corrupted context."""
        try:
            repair_log = []
            repaired_context = corrupted_context
            
            # Repair missing fields
            if not repaired_context.project_id:
                repaired_context.project_id = "recovered_project"
                repair_log.append("Set default project_id")
            
            if not repaired_context.session_id:
                repaired_context.session_id = f"recovered_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                repair_log.append("Set default session_id")
            
            # Repair conversation history
            valid_history = []
            for item in repaired_context.conversation_history:
                if isinstance(item, dict):
                    valid_history.append(item)
                else:
                    repair_log.append(f"Removed invalid conversation item: {type(item)}")
            
            repaired_context.conversation_history = valid_history
            
            # Ensure project state exists
            if not repaired_context.project_state:
                from ..models.context_models import ProjectState
                repaired_context.project_state = ProjectState(
                    architecture_overview="Recovered project state"
                )
                repair_log.append("Created default project state")
            
            return repaired_context, {
                "repair_successful": True,
                "repairs_applied": repair_log,
                "repair_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Context repair failed: {e}")
            return corrupted_context, {
                "repair_successful": False,
                "error": str(e),
                "repair_timestamp": datetime.now().isoformat()
            }
