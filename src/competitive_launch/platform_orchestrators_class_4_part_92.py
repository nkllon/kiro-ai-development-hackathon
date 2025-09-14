from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def __init__(self):
    """Initialize Kiro orchestrator."""
    self.platform_type = PlatformType.KIRO
    self.ai_agents_active = False
    self.quality_gates_active = False
    logger.info('Kiro Platform Orchestrator initialized')
