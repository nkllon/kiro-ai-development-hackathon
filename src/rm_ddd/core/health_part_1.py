
"""Simple health module for testing."""
from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus

def get_interface_metadata():
    """Get interface metadata."""
    return {
        'module_id': 'health_part_1',
        'version': '1.0.0',
        'description': 'Health module part 1'
    }
