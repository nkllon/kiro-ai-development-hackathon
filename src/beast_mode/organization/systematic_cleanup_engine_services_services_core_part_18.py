from src.rm_ddd.core.health import ModuleHealth

def _plan_directory_creation(self) -> List[Dict[str, Any]]:
    """Plan systematic directory structure creation"""
    directories = ['docs/systematic', 'archive/development-artifacts', 'archive/research', 'archive/media', 'archive/uncategorized', 'scripts', 'config']
    actions = []
    for directory in directories:
        actions.append({'type': 'create_directory', 'target': directory, 'description': f'Create systematic directory: {directory}', 'priority': 'HIGH', 'systematic_impact': 'Establishes systematic organizational structure'})
    return actions
