from src.rm_ddd.core.health import ModuleHealth

def validate_health_monitoring(self, module_path: str) -> HealthMonitoringResult:
    """
        Validate health monitoring implementation in RM components.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            HealthMonitoringResult with validation details
        """
    issues = []
    health_methods_implemented = []
    missing_health_methods = []
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        tree = ast.parse(source_code)
        method_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_names.add(node.name)
        for method_name, description in self.HEALTH_MONITORING_METHODS.items():
            if method_name in method_names:
                health_methods_implemented.append(method_name)
            else:
                missing_health_methods.append(method_name)
                if method_name in ['is_healthy', 'get_health_indicators']:
                    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.CRITICAL, description=f'Missing health monitoring method: {method_name}', affected_files=[module_path], remediation_steps=[f'Implement the {method_name} method', f'Method should: {description}'], blocking_merge=True))
        has_health_indicators = 'self._health_indicators' in source_code
        has_critical_health_methods = 'is_healthy' in method_names and 'get_health_indicators' in method_names
        if not has_health_indicators and has_critical_health_methods:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.MEDIUM, description='No health indicators found in module', affected_files=[module_path], remediation_steps=['Add health indicators to track module status', 'Use _update_health_indicator method to maintain health state'], blocking_merge=False))
        total_health_methods = len(self.HEALTH_MONITORING_METHODS)
        implemented_health_methods = len(health_methods_implemented)
        health_monitoring_score = implemented_health_methods / total_health_methods if total_health_methods > 0 else 0.0
        has_health_monitoring = len(missing_health_methods) == 0
        return HealthMonitoringResult(module_path=module_path, has_health_monitoring=has_health_monitoring, health_methods_implemented=health_methods_implemented, missing_health_methods=missing_health_methods, health_monitoring_score=health_monitoring_score, issues=issues)
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Failed to validate health monitoring: {str(e)}', affected_files=[module_path], remediation_steps=['Fix syntax errors in the module', 'Ensure module is valid Python code'], blocking_merge=True))
        return HealthMonitoringResult(module_path=module_path, has_health_monitoring=False, health_methods_implemented=[], missing_health_methods=list(self.HEALTH_MONITORING_METHODS.keys()), health_monitoring_score=0.0, issues=issues)

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

