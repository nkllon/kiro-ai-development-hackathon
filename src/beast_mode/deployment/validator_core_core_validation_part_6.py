from src.rm_ddd.core.health import ModuleHealth

def _validate_configuration(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Configuration validation"""
    results = []
    issues = self.config_manager.validate_config(config)
    if not issues:
        results.append(ValidationResult(name='Configuration validation', passed=True, message='Configuration is valid and complete'))
    else:
        results.append(ValidationResult(name='Configuration validation', passed=False, message=f"Configuration issues found: {', '.join(issues)}", details={'issues': issues}))
    directories = [config.agent.spore_directory]
    for directory in directories:
        if os.path.exists(directory):
            results.append(ValidationResult(name=f'Directory exists: {directory}', passed=True, message=f'Required directory exists: {directory}'))
        else:
            results.append(ValidationResult(name=f'Directory exists: {directory}', passed=False, message=f'Required directory missing: {directory}'))
    return results
