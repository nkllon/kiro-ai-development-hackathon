from src.rm_ddd.core.health import ModuleHealth

def _validate_beast_mode_configuration(self) -> ValidationResult:
    """Validate Beast Mode configuration and specs"""
    issues = []
    recommendations = []
    if not self.config.beast_mode_config_path.exists():
        return ValidationResult(component='beast_mode_config', status=IntegrationStatus.MISSING, details='Beast Mode configuration directory not found', issues=['.kiro/specs/beast-mode-framework directory missing'], recommendations=['Create Beast Mode configuration directory with specs'])
    try:
        required_config_files = ['requirements.md', 'design.md', 'tasks.md']
        missing_configs = []
        for config_file in required_config_files:
            config_path = self.config.beast_mode_config_path / config_file
            if not config_path.exists():
                missing_configs.append(config_file)
        if missing_configs:
            issues.append(f"Missing configuration files: {', '.join(missing_configs)}")
            recommendations.append('Create complete Beast Mode specification files')
        beast_mode_src = self.project_root / 'src' / 'beast_mode'
        if not beast_mode_src.exists():
            issues.append('Beast Mode source code directory missing')
            recommendations.append('Create src/beast_mode directory with framework code')
        else:
            core_modules = ['core/reflective_module.py', 'orchestration/tool_orchestration_engine.py', 'integration/infrastructure_integration_manager.py']
            missing_modules = []
            for module in core_modules:
                module_path = beast_mode_src / module
                if not module_path.exists():
                    missing_modules.append(module)
            if missing_modules:
                issues.append(f"Missing core modules: {', '.join(missing_modules)}")
                recommendations.append('Implement missing Beast Mode core modules')
        if not issues:
            status = IntegrationStatus.INTEGRATED
            details = 'Beast Mode configuration fully integrated and complete'
        elif len(issues) <= 2:
            status = IntegrationStatus.PARTIAL
            details = 'Beast Mode configuration partially complete'
        else:
            status = IntegrationStatus.FAILED
            details = 'Beast Mode configuration incomplete or missing'
        self.integration_status['beast_mode_config'] = status.value
        return ValidationResult(component='beast_mode_config', status=status, details=details, issues=issues, recommendations=recommendations)
    except Exception as e:
        self.integration_status['beast_mode_config'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='beast_mode_config', status=IntegrationStatus.FAILED, details=f'Beast Mode configuration validation failed: {str(e)}', issues=[f'Validation error: {str(e)}'], recommendations=['Debug Beast Mode configuration validation'])
