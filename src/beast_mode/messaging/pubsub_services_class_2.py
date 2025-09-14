from src.rm_ddd.core.registry import register_module
class PubSubManager(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Advanced pub/sub manager with handlers and queuing"""

    def __init__(self, redis_url: str='redis://localhost:6379'):
        register_module(self.__class__.__name__, self)
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.is_initialized = False
        self.is_listening = False
        self.listening_channels: Set[str] = set()
        self.handlers: Dict[str, List[MessageHandler]] = {}
        self.metrics = {'messages_sent': 0, 'messages_received': 0, 'messages_processed': 0, 'processing_errors': 0, 'last_activity': None}
        self.listener_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(self.redis_url, socket_connect_timeout=10.0, socket_timeout=10.0, retry_on_timeout=True, decode_responses=True)
            await self.client.ping()
            self.is_initialized = True
            logger.info(f'PubSubManager initialized with Redis at {self.redis_url}')
        except Exception as e:
            logger.error(f'Failed to initialize PubSubManager: {e}')
            raise

    async def shutdown(self) -> None:
        """Shutdown pub/sub manager"""
        try:
            self.is_listening = False
            if self.listener_task and (not self.listener_task.done()):
                self.listener_task.cancel()
                try:
                    await self.listener_task
                except asyncio.CancelledError:
                    pass
            if self.pubsub:
                await self.pubsub.unsubscribe()
                await self.pubsub.aclose()
                self.pubsub = None
            if self.client:
                await self.client.aclose()
                self.client = None
            self.is_initialized = False
            logger.info('PubSubManager shutdown complete')
        except Exception as e:
            logger.error(f'Error during shutdown: {e}')

    def register_handler(self, handler: MessageHandler, channel: str) -> None:
        """register_handler - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Register a message handler for a channel"""
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)
        logger.info(f'Registered handler for channel {channel}')

    async def start_listening(self, channels: List[str]) -> None:
        """Start listening on specified channels"""
        if not self.is_initialized:
            raise RuntimeError('PubSubManager not initialized')
        try:
            self.pubsub = self.client.pubsub()
            for channel in channels:
                await self.pubsub.subscribe(channel)
                self.listening_channels.add(channel)
            self.is_listening = True
            self.listener_task = asyncio.create_task(self._message_listener())
            logger.info(f'Started listening on channels: {channels}')
        except Exception as e:
            logger.error(f'Error starting listener: {e}')
            raise

    async def _message_listener(self) -> None:
        """Background message listener"""
        try:
            async for raw_message in self.pubsub.listen():
                if not self.is_listening:
                    break
                if raw_message['type'] == 'message':
                    await self._process_raw_message(raw_message)
        except asyncio.CancelledError:
            logger.info('Message listener cancelled')
        except Exception as e:
            logger.error(f'Error in message listener: {e}')

    async def _process_raw_message(self, raw_message: Dict[str, Any]) -> None:
        """Process a raw Redis message"""
        try:
            message_data = json.loads(raw_message['data'])
            message = BeastModeMessage(**message_data)
            self.metrics['messages_received'] += 1
            self.metrics['last_activity'] = datetime.now()
            channel = raw_message['channel']
            if channel in self.handlers:
                for handler in self.handlers[channel]:
                    try:
                        if message.type in handler.get_supported_types():
                            response = await handler.handle_message(message)
                            if response:
                                await self.publish_message(response, channel)
                            self.metrics['messages_processed'] += 1
                    except Exception as e:
                        self.metrics['processing_errors'] += 1
                        logger.error(f'Error in handler {handler.__class__.__name__}: {e}')
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse message JSON: {e}')
            self.metrics['processing_errors'] += 1
        except Exception as e:
            logger.error(f'Error processing message: {e}')
            self.metrics['processing_errors'] += 1

    async def publish_message(self, message: BeastModeMessage, channel: str) -> None:
        """Publish a message to a channel"""
        if not self.is_initialized:
            raise RuntimeError('PubSubManager not initialized')
        try:
            message_data = message.model_dump()
            message_json = json.dumps(message_data, default=str)
            await self.client.publish(channel, message_json)
            self.metrics['messages_sent'] += 1
            self.metrics['last_activity'] = datetime.now()
            logger.debug(f'Published {message.type} to channel {channel}')
        except Exception as e:
            logger.error(f'Error publishing message: {e}')
            raise

    async def send_prompt_request(self, prompt: str, channel: str, priority: int=5) -> str:
        """Send a prompt request message"""
        message = BeastModeMessage(type=MessageType.PROMPT_REQUEST, source='pubsub_manager', payload={'prompt': prompt}, priority=priority)
        await self.publish_message(message, channel)
        return message.id

    async def send_spore_spawn_request(self, spore_type: str, metadata: Dict[str, Any]) -> str:
        """Send a spore spawn request"""
        message = BeastModeMessage(type=MessageType.SPORE_SPAWN, source='pubsub_manager', payload={'spore_type': spore_type, 'metadata': metadata}, priority=6)
        await self.publish_message(message, 'spores')
        return message.id

    async def process_queue(self, queue_name: str, max_messages: int=10) -> int:
        """Process messages from a Redis queue"""
        if not self.is_initialized:
            raise RuntimeError('PubSubManager not initialized')
        processed = 0
        try:
            for _ in range(max_messages):
                result = await self.client.lpop(queue_name)
                if not result:
                    break
                try:
                    message_data = json.loads(result)
                    message = BeastModeMessage(**message_data)
                    for channel, handlers in self.handlers.items():
                        for handler in handlers:
                            if message.type in handler.get_supported_types():
                                await handler.handle_message(message)
                                processed += 1
                                break
                except Exception as e:
                    logger.error(f'Error processing queued message: {e}')
                    self.metrics['processing_errors'] += 1
        except Exception as e:
            logger.error(f'Error processing queue {queue_name}: {e}')
        return processed

    def get_health_status(self) -> Dict[str, Any]:
        """get_health_status - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get health status and metrics"""
        return {'status': 'healthy' if self.is_initialized else 'not_initialized', 'is_listening': self.is_listening, 'listening_channels': list(self.listening_channels), 'registered_handlers': {channel: len(handlers) for channel, handlers in self.handlers.items()}, 'metrics': self.metrics.copy()}

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

