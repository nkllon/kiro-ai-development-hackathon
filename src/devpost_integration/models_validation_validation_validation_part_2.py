
def validate_team_member_data(member_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate team member data with comprehensive validation"""
    validation_result = {'is_valid': True, 'errors': [], 'warnings': [], 'validated_fields': []}
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in member_data or not member_data[field]:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'Missing required field: {field}')
        else:
            validation_result['validated_fields'].append(field)
    if 'name' in member_data:
        name = member_data['name']
        if not isinstance(name, str) or len(name.strip()) < 2:
            validation_result['is_valid'] = False
            validation_result['errors'].append('Name must be at least 2 characters long')
        elif len(name) > 100:
            validation_result['warnings'].append('Name is very long (over 100 characters)')
    if 'email' in member_data:
        email = member_data['email']
        if not isinstance(email, str):
            validation_result['is_valid'] = False
            validation_result['errors'].append('Email must be a string')
        elif '@' not in email or '.' not in email.split('@')[-1]:
            validation_result['is_valid'] = False
            validation_result['errors'].append('Invalid email format')
        elif len(email) > 254:
            validation_result['warnings'].append('Email is very long (over 254 characters)')
    if 'role' in member_data:
        valid_roles = ['admin', 'member', 'viewer', 'editor', 'reviewer']
        if member_data['role'] not in valid_roles:
            validation_result['warnings'].append(f"Unknown role: {member_data['role']}")
    return validation_result
