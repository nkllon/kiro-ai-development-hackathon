from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for tool orchestration engine"""
    return self.project_root.exists() and len(self.tools_registry) > 0 and self.intelligence_engine.is_healthy() and (not self._degradation_active)
