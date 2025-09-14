from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, agent_id: str, **config):
        self.agent_id = agent_id
        self.config = config
        self.daemon = BeastModeDaemon(agent_id, **config)
        self.message_handlers: List[Callable[[BeastModeMessage], None]] = []
        self.is_processing = False
        self.processing_task = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize Redis transport.
        
        Args:
            config: Additional configuration parameters
            
        Returns:
            True if initialization successful
        """
        # Update config if provided
        if config:
            self.config.update(config)
            # Create new daemon with updated config if needed
            if any(key in config for key in ['redis_url', 'channel', 'max_queue_size']):
                self.daemon = BeastModeDaemon(self.agent_id, **self.config)
        
        # Daemon initializes in constructor, so just return True
        # Real connection happens in start_daemon()
        return True
    
    async def send_message(self, message: BeastModeMessage) -> bool:
        """
        Send message via Redis daemon.
        
        Args:
            message: Message to send
            
        Returns:
            True if queued successfully (daemon handles actual sending)
        """
        try:
            # Ensure source is set
            if not message.source:
                message.source = self.agent_id
            
            # Use daemon's send_message (thread-safe)
            self.daemon.send_message(message)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    async def subscribe(self, handler: Callable[[BeastModeMessage], None]) -> bool:
        """
        Subscribe to messages with handler.
        
        Args:
            handler: Function to call when messages are received
            
        Returns:
            True if subscription successful
        """
        try:
            self.message_handlers.append(handler)
            
            # Start message processing if this is the first handler
            if len(self.message_handlers) == 1 and not self.is_processing:
                await self._start_message_processing()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe handler: {e}")
            return False
    
    async def start_daemon(self) -> bool:
        """
        Start Redis daemon.
        
        Returns:
            True if daemon started successfully
        """
        try:
            success = self.daemon.start_daemon()
            if success:
                # Announce presence (preserves existing behavior)
                self.daemon.announce_presence()
                
                # Start message processing if we have handlers
                if self.message_handlers and not self.is_processing:
                    await self._start_message_processing()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
            return False
    
    async def stop_daemon(self) -> None:
        """Stop Redis daemon gracefully."""
        try:
            # Stop message processing
            await self._stop_message_processing()
            
            # Stop daemon
            self.daemon.stop_daemon()
            
        except Exception as e:
            self.logger.error(f"Error stopping daemon: {e}")

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

    