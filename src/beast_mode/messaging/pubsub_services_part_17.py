from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, redis_url: str='redis://localhost:6379'):
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
