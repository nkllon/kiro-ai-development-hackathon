from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def register_handler(self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]):
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """
        Register a message handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to call when message received
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        self.logger.info(f'Registered handler for {message_type}')

    async def _handle_message(self, message: BeastModeMessage):
        """
        Internal message handler called by transport.
        
        Args:
            message: Received message
        """
        try:
            self.stats['messages_received'] += 1
            self.stats['last_activity'] = datetime.now()
            await self.shared_state.increment_counter('messages_received', self.agent_id)
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception as e:
                        self.logger.error(f'Handler error for {message.type}: {e}')
            await self._handle_builtin_messages(message)
        except Exception as e:
            self.logger.error(f'Error handling message: {e}')

    async def _handle_builtin_messages(self, message: BeastModeMessage):
        """Handle built-in message types."""
        if message.type == MessageType.AGENT_DISCOVERY:
            response = BeastModeMessage(type=MessageType.AGENT_RESPONSE, source=self.agent_id, target=message.source, payload={'agent_id': self.agent_id, 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_type': self.transport_type, 'status': 'online'})
            await self.send_message(response)

    async def _announce_presence(self):
        """Announce agent presence in shared state."""
        agent_state = {'status': 'online', 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_type': self.transport_type, 'last_seen': datetime.now().isoformat(), 'stats': self.stats.copy()}
        await self.shared_state.update_agent_state(self.agent_id, agent_state)

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

