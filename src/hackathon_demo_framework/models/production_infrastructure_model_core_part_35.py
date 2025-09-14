
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
    """Result of security validation"""
    validation_id: str
    security_level: SecurityLevel
    vulnerabilities_found: int
    vulnerabilities_critical: int
    compliance_score: float
    remediation_plan: List[str]
    created_at: datetime
