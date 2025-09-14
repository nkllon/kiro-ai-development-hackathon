from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class InitClass:
    """Auto-generated class for functions."""

    def __init__(self):
    register_module(self.__class__.__name__, self)
    self.logger = logging.getLogger(__name__)
    self.alert_rules: Dict[str, AlertRule] = {}
    self.active_alerts: Dict[str, Alert] = {}
    self.alert_history: List[Alert] = []
    self.last_evaluation: Dict[str, datetime] = {}
    self.last_alert_time: Dict[str, datetime] = {}
    self.alerting_active = False
    self.alerting_task: Optional[asyncio.Task] = None
    self.alert_handlers: List[Callable] = []

    async def register_alert_rule(self, name: str, description: str, severity: AlertSeverity, condition_function: Callable, threshold_value: Optional[float]=None, evaluation_interval_seconds: int=60, cooldown_seconds: int=300, auto_resolve: bool=True, auto_resolve_threshold: Optional[float]=None) -> None:
    """Register a new alert rule."""
    self.alert_rules[name] = AlertRule(name=name, description=description, severity=severity, condition_function=condition_function, threshold_value=threshold_value, evaluation_interval_seconds=evaluation_interval_seconds, cooldown_seconds=cooldown_seconds, auto_resolve=auto_resolve, auto_resolve_threshold=auto_resolve_threshold)
    self.logger.info(f'Registered alert rule: {name}')

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

