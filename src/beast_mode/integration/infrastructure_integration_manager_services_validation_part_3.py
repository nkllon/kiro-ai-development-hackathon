
def _validate_project_registry_integration(self) -> ValidationResult:
    """Validate project model registry integration"""
    issues = []
    recommendations = []
    if not self.config.project_registry_path.exists():
        return ValidationResult(component='project_registry', status=IntegrationStatus.MISSING, details='Project model registry not found', issues=['project_model_registry.json missing'], recommendations=['Create project model registry with domain architecture'])
    try:
        registry_content = json.loads(self.config.project_registry_path.read_text())
        required_keys = ['domain_architecture', 'project_purpose', 'description']
        for key in required_keys:
            if key not in registry_content:
                issues.append(f'Missing required key: {key}')
                recommendations.append(f'Add {key} section to project registry')
        if 'domain_architecture' in registry_content:
            domain_arch = registry_content['domain_architecture']
            for domain in self.config.required_registry_domains:
                if domain not in domain_arch:
                    issues.append(f'Missing required domain: {domain}')
                    recommendations.append(f'Add {domain} domain to registry')
            total_domains = domain_arch.get('overview', {}).get('total_domains', 0)
            if total_domains < 50:
                issues.append(f'Insufficient domains: {total_domains} (minimum 50)')
                recommendations.append('Expand domain architecture to meet requirements')
        compliance = registry_content.get('domain_architecture', {}).get('overview', {}).get('compliance_standard')
        if compliance != 'Reflective Module (RM)':
            issues.append('Compliance standard not set to Reflective Module (RM)')
            recommendations.append("Set compliance_standard to 'Reflective Module (RM)'")
        if not issues:
            status = IntegrationStatus.INTEGRATED
            details = 'Project registry fully integrated with Beast Mode requirements'
        elif len(issues) <= 3:
            status = IntegrationStatus.PARTIAL
            details = 'Project registry partially integrated, some issues detected'
        else:
            status = IntegrationStatus.FAILED
            details = 'Project registry integration failed, multiple issues detected'
        self.integration_status['project_registry'] = status.value
        return ValidationResult(component='project_registry', status=status, details=details, issues=issues, recommendations=recommendations)
    except json.JSONDecodeError as e:
        self.integration_status['project_registry'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='project_registry', status=IntegrationStatus.FAILED, details=f'Invalid JSON in project registry: {str(e)}', issues=[f'JSON parsing error: {str(e)}'], recommendations=['Fix JSON syntax in project_model_registry.json'])
    except Exception as e:
        self.integration_status['project_registry'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='project_registry', status=IntegrationStatus.FAILED, details=f'Registry validation failed: {str(e)}', issues=[f'Validation error: {str(e)}'], recommendations=['Debug project registry validation process'])
