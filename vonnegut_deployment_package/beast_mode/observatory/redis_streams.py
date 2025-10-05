"""
Redis Streams configuration and utilities for Observatory metrics collection.

This module provides Redis Streams setup and management for real-time metrics
collection and distribution across Observatory components.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime

import redis.asyncio as redis

from .models import CoordinationEvent, CoordinationMetrics, RedisConfig


logger = logging.getLogger(__name__)


class ObservatoryRedisStreams:
    """Manages Redis Streams for Observatory metrics collection and distribution."""
    
    def __init__(self, config: RedisConfig):
        self._config = config
        self._redis_client: Optional[redis.Redis] = None
        self._stream_name = config.stream_name
        self._consumer_group = "observatory_consumers"
        self._consumer_name = f"observatory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def initialize(self) -> bool:
        """Initialize Redis connection and streams."""
        try:
            # Create Redis connection
            self._redis_client = redis.from_url(
                f"redis://{self._config.host}:{self._config.port}",
                password=self._config.password,
                ssl=self._config.ssl,
                max_connections=self._config.connection_pool_size,
                decode_responses=True
            )
            
            # Test connection
            await self._redis_client.ping()
            logger.info(f"Connected to Redis at {self._config.host}:{self._config.port}")
            
            # Create consumer group if it doesn't exist
            try:
                await self._redis_client.xgroup_create(
                    self._stream_name, 
                    self._consumer_group, 
                    id='0', 
                    mkstream=True
                )
                logger.info(f"Created consumer group {self._consumer_group}")
            except redis.ResponseError as e:
                if "BUSYGROUP" in str(e):
                    logger.info(f"Consumer group {self._consumer_group} already exists")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis streams: {e}")
            return False
    
    async def publish_event(self, event: CoordinationEvent) -> bool:
        """Publish a coordination event to the Redis stream."""
        try:
            if not self._redis_client:
                logger.error("Redis client not initialized")
                return False
            
            # Serialize event data
            event_data = {
                'event_id': event.event_id,
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type.name,
                'source_component': event.source_component,
                'event_data': json.dumps(event.event_data),
                'correlation_id': event.correlation_id or '',
                'user_id': event.user_id or ''
            }
            
            # Add to stream
            stream_id = await self._redis_client.xadd(self._stream_name, event_data)
            logger.debug(f"Published event {event.event_id} to stream with ID {stream_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            return False
    
    async def consume_events(self, count: int = 10, block: int = 1000) -> AsyncGenerator[CoordinationEvent, None]:
        """Consume coordination events from the Redis stream."""
        try:
            if not self._redis_client:
                logger.error("Redis client not initialized")
                return
            
            while True:
                try:
                    # Read from stream
                    messages = await self._redis_client.xreadgroup(
                        self._consumer_group,
                        self._consumer_name,
                        {self._stream_name: '>'},
                        count=count,
                        block=block
                    )
                    
                    for stream, msgs in messages:
                        for msg_id, fields in msgs:
                            try:
                                # Deserialize event
                                event = self._deserialize_event(fields)
                                if event:
                                    yield event
                                
                                # Acknowledge message
                                await self._redis_client.xack(
                                    self._stream_name, 
                                    self._consumer_group, 
                                    msg_id
                                )
                                
                            except Exception as e:
                                logger.error(f"Error processing message {msg_id}: {e}")
                
                except redis.ResponseError as e:
                    if "NOGROUP" in str(e):
                        logger.warning("Consumer group doesn't exist, recreating...")
                        await self.initialize()
                    else:
                        logger.error(f"Redis error in consume_events: {e}")
                        await asyncio.sleep(1)
                
                except Exception as e:
                    logger.error(f"Error in consume_events: {e}")
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info("Event consumption cancelled")
        except Exception as e:
            logger.error(f"Fatal error in consume_events: {e}")
    
    def _deserialize_event(self, fields: Dict[str, str]) -> Optional[CoordinationEvent]:
        """Deserialize event data from Redis stream fields."""
        try:
            from .models import CoordinationEventType
            
            event = CoordinationEvent(
                event_id=fields['event_id'],
                timestamp=datetime.fromisoformat(fields['timestamp']),
                event_type=CoordinationEventType[fields['event_type']],
                source_component=fields['source_component'],
                event_data=json.loads(fields['event_data']) if fields['event_data'] else {},
                correlation_id=fields['correlation_id'] if fields['correlation_id'] else None,
                user_id=fields['user_id'] if fields['user_id'] else None
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to deserialize event: {e}")
            return None
    
    async def get_stream_info(self) -> Dict[str, any]:
        """Get information about the Observatory stream."""
        try:
            if not self._redis_client:
                return {}
            
            info = await self._redis_client.xinfo_stream(self._stream_name)
            return {
                'length': info.get('length', 0),
                'first_entry': info.get('first-entry'),
                'last_entry': info.get('last-entry'),
                'consumer_groups': info.get('groups', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            return {}
    
    async def cleanup_old_messages(self, max_length: int = 10000) -> bool:
        """Clean up old messages from the stream to prevent memory issues."""
        try:
            if not self._redis_client:
                return False
            
            # Trim stream to max length
            await self._redis_client.xtrim(self._stream_name, maxlen=max_length, approximate=True)
            logger.debug(f"Trimmed stream {self._stream_name} to max length {max_length}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup old messages: {e}")
            return False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis_client:
            await self._redis_client.close()
            logger.info("Redis connection closed")