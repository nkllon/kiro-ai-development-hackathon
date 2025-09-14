
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Template for generating remediation steps."""
    issue_type: ComplianceIssueType
    severity: IssueSeverity
    category: RemediationCategory
    title_template: str
    description_template: str
    steps_template: List[str]
    prerequisites: List[str]
    validation_criteria: List[str]
    estimated_effort: str
    tools_required: List[str] = None

@dataclass