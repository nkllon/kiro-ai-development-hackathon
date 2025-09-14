from src.rm_ddd.core.health import ModuleHealth

def _validate_cursor_rules_integration(self) -> ValidationResult:
    """Validate cursor rules integration"""
    issues = []
    recommendations = []
    if not self.config.cursor_rules_path.exists():
        return ValidationResult(component='cursor_rules', status=IntegrationStatus.MISSING, details='Cursor rules directory not found', issues=['.cursor/rules directory missing'], recommendations=['Create .cursor/rules directory with Beast Mode integration'])
    try:
        beast_mode_rules = ['beast-mode-integration.mdc', 'beast.mdc']
        missing_rules = []
        for rule_file in beast_mode_rules:
            rule_path = self.config.cursor_rules_path / rule_file
            if not rule_path.exists():
                missing_rules.append(rule_file)
        if missing_rules:
            issues.append(f"Missing Beast Mode rules: {', '.join(missing_rules)}")
            recommendations.append('Create Beast Mode cursor rules for systematic development')
        rule_files = list(self.config.cursor_rules_path.glob('*.mdc'))
        beast_mode_mentions = 0
        for rule_file in rule_files:
            try:
                content = rule_file.read_text()
                if 'beast' in content.lower() or 'systematic' in content.lower():
                    beast_mode_mentions += 1
            except Exception:
                continue
        if beast_mode_mentions == 0:
            issues.append('No Beast Mode integration found in existing rules')
            recommendations.append('Add Beast Mode methodology to cursor rules')
        if not issues:
            status = IntegrationStatus.INTEGRATED
            details = 'Cursor rules fully integrated with Beast Mode methodology'
        elif len(issues) <= 2:
            status = IntegrationStatus.PARTIAL
            details = 'Cursor rules partially integrated, some rules missing'
        else:
            status = IntegrationStatus.FAILED
            details = 'Cursor rules integration incomplete'
        self.integration_status['cursor_rules'] = status.value
        return ValidationResult(component='cursor_rules', status=status, details=details, issues=issues, recommendations=recommendations)
    except Exception as e:
        self.integration_status['cursor_rules'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='cursor_rules', status=IntegrationStatus.FAILED, details=f'Cursor rules validation failed: {str(e)}', issues=[f'Validation error: {str(e)}'], recommendations=['Debug cursor rules validation process'])
