from src.rm_ddd.core.health import ModuleHealth

def _analyze_task_requirements(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze task requirements to determine tool needs"""
    return {'task_type': task_context.get('task_type', 'unknown'), 'required_tool_types': task_context.get('tool_types', []), 'systematic_constraints': task_context.get('systematic_only', True), 'priority': task_context.get('priority', 'normal')}
