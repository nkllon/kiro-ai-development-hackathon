from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, redis_url: str='redis://localhost:6379'):
        self.redis_url = redis_url
        self.logger = logging.getLogger(__name__)
        self.recovery_actions: Dict[str, RecoveryAction] = {}
        self.recovery_attempts: List[RecoveryAttempt] = []
        self.active_recoveries: Dict[str, RecoveryAttempt] = {}
        self.recovery_active = False
        self.recovery_task: Optional[asyncio.Task] = None
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.recovery_callbacks: List[Callable] = []

    async def register_recovery_action(self, name: str, action_type: RecoveryActionType, description: str, action_function: Callable, max_attempts: int=3, retry_delay_seconds: int=30, timeout_seconds: int=60, prerequisites: Optional[List[str]]=None, escalation_action: Optional[str]=None) -> None:
        """Register a recovery action."""
        self.recovery_actions[name] = RecoveryAction(name=name, action_type=action_type, description=description, action_function=action_function, max_attempts=max_attempts, retry_delay_seconds=retry_delay_seconds, timeout_seconds=timeout_seconds, prerequisites=prerequisites or [], escalation_action=escalation_action)
        self.logger.info(f'Registered recovery action: {name}')

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

