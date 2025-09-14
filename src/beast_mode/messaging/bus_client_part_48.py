from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def __init__(self, redis_url: str='redis://localhost:6379', agent_id: str='beast_mode_agent', capabilities: Optional[List[str]]=None, channel: str='beast_mode_network'):
    self.redis_url = redis_url
    self.agent_id = agent_id
    self.capabilities = capabilities or []
    self.channel = channel
    self.client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_connected = False
    self.is_listening = False
    self.message_handlers: Dict[MessageType, List[Callable]] = {}
    self.received_messages: List[BeastModeMessage] = []
    self.message_router: Optional[StandardMessageRouter] = None
    self.agent_registry = AgentRegistry()
    self.discovery_enabled = True
    self.help_system = HelpWantedSystem(self.agent_registry)
    self.collaboration_scheduler = CollaborationScheduler(self.agent_id)
    self.max_retries = 5
    self.retry_delay = 1.0
    self.connection_timeout = 10.0
    self.stats = {'messages_sent': 0, 'messages_received': 0, 'connection_errors': 0, 'last_activity': None}
