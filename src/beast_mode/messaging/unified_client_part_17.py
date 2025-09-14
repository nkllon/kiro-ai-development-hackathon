from datetime import datetime
from typing import Dict, List, Any

    def __init__(self, agent_id: str, transport_type: str='redis', transport_config: Optional[Dict[str, Any]]=None, shared_state_config: Optional[SharedStateConfig]=None, capabilities: Optional[List[str]]=None, specializations: Optional[List[str]]=None):
        """
        Initialize unified Beast Mode client.
        
        Args:
            agent_id: Unique agent identifier
            transport_type: Type of transport ('redis', 'nats', etc.)
            transport_config: Transport-specific configuration
            shared_state_config: Shared state configuration
            capabilities: Agent capabilities list
            specializations: Agent specializations list
        """
        self.agent_id = agent_id
        self.transport_type = transport_type
        self.capabilities = capabilities or []
        self.specializations = specializations or []
        self.transport = TransportFactory.create_transport(transport_type, agent_id=agent_id, **transport_config or {})
        self.shared_state = BeastModeSharedState(shared_state_config)
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.is_started = False
        self.stats = {'messages_sent': 0, 'messages_received': 0, 'start_time': None, 'last_activity': None}
        self.logger = logging.getLogger(__name__)

    async def start(self) -> bool:
        """
        Start the Beast Mode client.
        
        Returns:
            True if started successfully
        """
        if self.is_started:
            self.logger.warning('Client already started')
            return True
        try:
            if not await self.shared_state.initialize():
                self.logger.error('Failed to initialize shared state')
                return False
            if not await self.transport.initialize({}):
                self.logger.error('Failed to initialize transport')
                return False
            await self.transport.subscribe(self._handle_message)
            if not await self.transport.start_daemon():
                self.logger.error('Failed to start transport daemon')
                return False
            await self._announce_presence()
            self.is_started = True
            self.stats['start_time'] = datetime.now()
            self.logger.info(f'Beast Mode client started: {self.agent_id} using {self.transport_type}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to start client: {e}')
            return False

    async def stop(self):
        """Stop the Beast Mode client gracefully."""
        if not self.is_started:
            return
        try:
            await self.shared_state.remove_agent_state(self.agent_id)
            await self.transport.stop_daemon()
            await self.shared_state.shutdown()
            self.is_started = False
            self.logger.info(f'Beast Mode client stopped: {self.agent_id}')
        except Exception as e:
            self.logger.error(f'Error stopping client: {e}')

    async def send_message(self, message: BeastModeMessage) -> bool:
        """
        Send a message via transport and update shared state.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if not self.is_started:
            self.logger.error('Client not started')
            return False
        try:
            if not message.source:
                message.source = self.agent_id
            success = await self.transport.send_message(message)
            if success:
                self.stats['messages_sent'] += 1
                self.stats['last_activity'] = datetime.now()
                await self.shared_state.increment_counter('messages_sent', self.agent_id)
                await self.shared_state.update_agent_state(self.agent_id, {'last_activity': datetime.now().isoformat(), 'status': 'active'})
            return success
        except Exception as e:
            self.logger.error(f'Failed to send message: {e}')
            return False
