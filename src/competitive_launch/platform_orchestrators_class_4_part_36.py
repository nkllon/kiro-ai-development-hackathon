from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def __init__(self):
    """Initialize TiDB orchestrator."""
    self.platform_type = PlatformType.TIDB
    self.htap_enabled = False
    self.analytics_active = False
    logger.info('TiDB Platform Orchestrator initialized')
