from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


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
