
    def is_healthy(self) -> bool:
        """Health assessment for Makefile management capability"""
        return not self._degradation_active
