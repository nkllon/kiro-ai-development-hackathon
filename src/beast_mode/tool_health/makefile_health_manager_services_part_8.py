from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """Health assessment for Makefile management capability"""
        return not self._degradation_active
