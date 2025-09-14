from src.rm_ddd.core.health import ModuleHealth

def _check_domain_tools(self, domain: Domain) -> List[HealthIssue]:
    """Check if domain tools are available and configured correctly"""
    issues = []
    try:
        tools_to_check = [('linter', domain.tools.linter), ('formatter', domain.tools.formatter), ('validator', domain.tools.validator)]
        for tool_type, tool_name in tools_to_check:
            if tool_name:
                if not isinstance(tool_name, str) or not tool_name.strip():
                    issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Invalid {tool_type} configuration: '{tool_name}'", suggested_fix=f'Set a valid {tool_type} tool name'))
    except Exception as e:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f'Failed to validate domain tools: {str(e)}', suggested_fix='Check domain tools configuration'))
    return issues

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

