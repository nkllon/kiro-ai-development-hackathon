
    def mark_beast_ready(self, item_id: str, mpm_validation: MPMValidation) -> ReadinessResult:
        """Mark an item as beast-ready after MPM validation"""
        return self._core_operations.mark_beast_ready(item_id, mpm_validation)


