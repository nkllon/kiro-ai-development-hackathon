from src.rm_ddd.core.health import ModuleHealth

def analyze(self, context: Dict[str, Any]) -> ComplianceAnalysisResult:
    """
        Analyze git repository for compliance.
        
        Args:
            context: Analysis context containing repository information
            
        Returns:
            Compliance analysis result with git analysis data
        """
    self.logger.info('Starting git compliance analysis')
    result = ComplianceAnalysisResult()
    try:
        target_branch = context.get('target_branch', self._config['target_branch'])
        base_branch = context.get('base_branch', self._config['base_branch'])
        result.commits_analyzed = self.get_commits_ahead_of_main(target_branch, base_branch)
        file_changes = self.analyze_file_changes(result.commits_analyzed)
        result.recommendations.append(f'Analyzed {len(result.commits_analyzed)} commits with {file_changes.total_files_changed} file changes')
        self.logger.info('Git compliance analysis completed successfully')
    except Exception as e:
        self.logger.error(f'Error during git analysis: {str(e)}')
        result.critical_issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.CRITICAL, description=f'Git analysis failed: {str(e)}', blocking_merge=True))
    return result

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

