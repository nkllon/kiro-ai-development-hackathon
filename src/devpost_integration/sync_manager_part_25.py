from src.rm_ddd.core.health import ModuleHealth

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
    """Comprehensive sync status report."""
    total_operations: int
    completed_operations: int
    failed_operations: int
    pending_operations: int
    conflicts: List[SyncConflict]
    last_sync_time: Optional[datetime] = None


@dataclass