from src.rm_ddd.core.health import ModuleHealth

def validate_project_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate project metadata with comprehensive validation"""
    validation_result = {'is_valid': True, 'errors': [], 'warnings': [], 'validated_fields': []}
    required_fields = ['title', 'description', 'team_members']
    for field in required_fields:
        if field not in metadata:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'Missing required field: {field}')
        else:
            validation_result['validated_fields'].append(field)
    if 'title' in metadata:
        title = metadata['title']
        if not isinstance(title, str) or len(title.strip()) == 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append('Title must be a non-empty string')
        elif len(title) > 200:
            validation_result['warnings'].append('Title is very long (over 200 characters)')
    if 'description' in metadata:
        description = metadata['description']
        if not isinstance(description, str):
            validation_result['is_valid'] = False
            validation_result['errors'].append('Description must be a string')
        elif len(description) < 10:
            validation_result['warnings'].append('Description is very short (less than 10 characters)')
        elif len(description) > 5000:
            validation_result['warnings'].append('Description is very long (over 5000 characters)')
    if 'team_members' in metadata:
        team_members = metadata['team_members']
        if not isinstance(team_members, list):
            validation_result['is_valid'] = False
            validation_result['errors'].append('Team members must be a list')
        elif len(team_members) == 0:
            validation_result['warnings'].append('No team members specified')
        elif len(team_members) > 20:
            validation_result['warnings'].append('Large team size (over 20 members)')
        else:
            for i, member in enumerate(team_members):
                if not isinstance(member, dict):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f'Team member {i + 1} must be a dictionary')
                elif 'name' not in member or 'email' not in member:
                    validation_result['warnings'].append(f'Team member {i + 1} missing name or email')
    return validation_result

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

