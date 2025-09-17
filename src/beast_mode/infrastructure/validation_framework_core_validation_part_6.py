from src.rm_ddd.core.health import ModuleHealth

def _validate_documentation_infrastructure(self) -> ValidationResult:
    """Validate documentation infrastructure for systematic knowledge management"""
    issues = []
    recommendations = []
    docs_dir = Path('docs')
    if not docs_dir.exists():
        issues.append(InfrastructureIssue(component=InfrastructureComponent.DOCUMENTATION, issue_type='missing_docs_directory', severity=ValidationSeverity.MEDIUM, description='Documentation directory missing', systematic_impact='Cannot organize systematic documentation', remediation_steps=['Create docs/ directory', 'Setup systematic documentation structure', 'Implement documentation standards'], estimated_fix_time='15 minutes'))
    systematic_docs_dir = Path('docs/systematic')
    if systematic_docs_dir.exists():
        doc_count = len([f for f in systematic_docs_dir.iterdir() if f.is_file()])
        self.logger.debug(f'✅ Systematic documentation: {doc_count} documents found')
    compliance_score = 0.9 if len(issues) == 0 else 0.7
    status = 'PASS' if compliance_score >= 0.8 else 'WARNING'
    recommendations.extend(['Implement systematic documentation standards', 'Setup automated documentation generation', 'Add systematic knowledge management capabilities'])
    return ValidationResult(component=InfrastructureComponent.DOCUMENTATION, status=status, issues=issues, systematic_compliance_score=compliance_score, recommendations=recommendations, validation_timestamp=datetime.now())

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

