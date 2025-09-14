
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
    """
    Base class for domain entities.
    
    Provides systematic implementation of DDD entity patterns with built-in
    RM compliance, identity management, equality semantics, and domain validation.
    
    Key Responsibilities:
    - Identity management and equality semantics
    - Domain boundary definition and enforcement
    - Domain invariant validation
    - Version tracking for optimistic locking
    - Integration with RM health monitoring
    
    Accountability Chain:
    - Domain Expert: Responsible for business rules and invariants
    - Entity Owner: Responsible for entity-specific logic
    - RM Framework: Responsible for systematic compliance
    """
