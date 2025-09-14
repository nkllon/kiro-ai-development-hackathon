from src.rm_ddd.core.health import ModuleHealth

def _identify_systematic_violations(self, file_analyses: List[FileAnalysis]) -> List[Dict[str, Any]]:
    """Identify systematic violations requiring immediate attention"""
    violations = []
    for analysis in file_analyses:
        if analysis.cleanup_priority in [CleanupPriority.CRITICAL, CleanupPriority.HIGH]:
            violations.append({'file': str(analysis.file_path), 'violation_type': analysis.category.value, 'priority': analysis.cleanup_priority.value, 'systematic_impact': analysis.systematic_impact, 'recommended_action': f'Move to {analysis.recommended_location}'})
    return violations
