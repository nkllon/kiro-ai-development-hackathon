
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
    """Represents a queued sync operation."""
    operation_id: str
    priority: SyncPriority
    operation_type: str
    created_at: datetime
    retry_count: int = 0


@dataclass