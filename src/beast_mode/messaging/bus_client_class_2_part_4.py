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
    async def connect(self) -> bool:
        Establish connection to Redis server with retry logic.
        Returns:
            bool: True if connection successful, False otherwise
        for attempt in range(self.max_retries):
            try:
                logger.info(f'Attempting to connect to Redis (attempt {attempt + 1}/{self.max_retries})')
                self.client = redis.from_url(self.redis_url, socket_connect_timeout=self.connection_timeout, socket_timeout=self.connection_timeout, retry_on_timeout=True, decode_responses=True)
                await self.client.ping()
                self.is_connected = True
                if self.discovery_enabled:
                    self.agent_registry.start_background_cleanup()
                self.collaboration_scheduler.start_background_tasks()
                if self.message_router is None:
                    self.message_router = StandardMessageRouter(agent_id=self.agent_id, capabilities=self.capabilities)
                logger.info(f'Successfully connected to Redis at {self.redis_url}')
                return True
            except (ConnectionError, TimeoutError) as e:
                self.stats['connection_errors'] += 1
                logger.warning(f'Connection attempt {attempt + 1} failed: {e}')
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * 2 ** attempt)
                else:
                    logger.error(f'Failed to connect to Redis after {self.max_retries} attempts')
                    return False
            except Exception as e:
                logger.error(f'Unexpected error connecting to Redis: {e}')
                return False
        return False
    async def disconnect(self) -> None:
        try:
            self.is_listening = False
            if self.discovery_enabled:
                self.agent_registry.stop_background_cleanup()
            self.collaboration_scheduler.stop_background_tasks()
            if self.pubsub:
                await self.pubsub.unsubscribe(self.channel)
                await self.pubsub.aclose()
                self.pubsub = None
            if self.client:
                await self.client.aclose()
                self.client = None
            self.is_connected = False
            logger.info('Disconnected from Redis')
        except Exception as e:
            logger.error(f'Error during disconnect: {e}')
    async def announce_presence(self) -> None:
        if not self.is_connected:
            raise RuntimeError('Not connected to Redis')
        capabilities_data = AgentCapabilities(agent_id=self.agent_id, capabilities=self.capabilities, availability='ready_for_business', last_seen=datetime.now())
        message = BeastModeMessage(type=MessageType.AGENT_DISCOVERY, source=self.agent_id, target=None, payload={'agent_capabilities': capabilities_data.model_dump(), 'announcement': f'Agent {self.agent_id} is ready for collaboration'}, priority=3)
        await self.send_message(message)
        logger.info(f'Announced presence for agent {self.agent_id}')
    async def send_message(self, message: BeastModeMessage) -> None:
        Send a message to the network.
        Args:
            message: The message to send
        if not self.is_connected or not self.client:
            raise RuntimeError('Not connected to Redis')
        try:
            if not message.source:
                message.source = self.agent_id
            message_data = message.model_dump()
            message_json = json.dumps(message_data, default=str)
            await self.client.publish(self.channel, message_json)
            self.stats['messages_sent'] += 1
            self.stats['last_activity'] = datetime.now()
            logger.debug(f"Sent {message.type} message from {message.source} to {message.target or 'broadcast'}")
        except Exception as e:
            logger.error(f'Error sending message: {e}')
            raise
    async def send_simple_message(self, content: str, target: Optional[str]=None) -> None:
        message = BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source=self.agent_id, target=target, payload={'content': content})
        await self.send_message(message)
    async def send_help_request(self, required_capabilities: List[str], description: str, urgency: HelpUrgency=HelpUrgency.NORMAL, max_helpers: int=1, timeout_hours: Optional[float]=None, context: Optional[Dict[str, Any]]=None) -> str:
        Send a help request with required capabilities.
        Args:
            required_capabilities: List of required capabilities
            description: Description of what help is needed
            urgency: Urgency level of the request
            max_helpers: Maximum number of helpers needed
            timeout_hours: Hours until request expires
            context: Additional context information
        Returns:
            str: Request ID for tracking
        help_request = self.help_system.create_help_request(requester_id=self.agent_id, required_capabilities=required_capabilities, description=description, urgency=urgency, max_helpers=max_helpers, timeout_hours=timeout_hours, context=context)
        message = self.help_system.create_help_request_message(help_request)
        if self.client and self.client is not True:
            await self.send_message(message)
        return help_request.request_id
    async def listen_for_messages(self, message_callback: Optional[Callable[[BeastModeMessage], None]]=None) -> None:
        Listen for messages from the network.
        Args:
            message_callback: Optional callback function to handle received messages
        if not self.is_connected or not self.client:
            raise RuntimeError('Not connected to Redis')
        try:
            self.pubsub = self.client.pubsub()
            await self.pubsub.subscribe(self.channel)
            self.is_listening = True
            logger.info(f'Started listening on channel {self.channel}')
            async for raw_message in self.pubsub.listen():
                if not self.is_listening:
                    break
                if raw_message['type'] == 'message':
                    try:
                        message_data = json.loads(raw_message['data'])
                        message = BeastModeMessage(**message_data)
                        if message.source == self.agent_id:
                            continue
                        self.stats['messages_received'] += 1
                        self.stats['last_activity'] = datetime.now()
                        self.received_messages.append(message)
                        if self.message_router:
                            try:
                                router_responses = await self.message_router.process_message(message)
                                for response in router_responses:
                                    await self.send_message(response)
                            except Exception as e:
                                logger.error(f'Error in message router: {e}')
                        await self._handle_message(message)
                        if message_callback:
                            try:
                                message_callback(message)
                            except Exception as e:
                                logger.error(f'Error in message callback: {e}')
                        logger.debug(f'Received {message.type} from {message.source}')
                    except json.JSONDecodeError as e:
                        logger.error(f'Failed to parse message JSON: {e}')
                        logger.debug(f"Raw message data: {raw_message['data']}")
                    except Exception as e:
                        logger.error(f'Error processing message: {e}')
                        logger.debug(f'Message data: {raw_message}')
        except Exception as e:
            logger.error(f'Error in message listener: {e}')
            raise
        finally:
            self.is_listening = False
    async def _handle_message(self, message: BeastModeMessage) -> None:
        try:
            if message.type == MessageType.AGENT_DISCOVERY:
                await self._handle_agent_discovery(message)
            elif message.type == MessageType.AGENT_RESPONSE:
                await self._handle_agent_response(message)
            elif message.type == MessageType.HELP_WANTED:
                await self._handle_help_request(message)
            elif message.type == MessageType.HELP_RESPONSE:
                await self._handle_help_response(message)
            elif message.type == MessageType.OFFICE_HOURS_ANNOUNCEMENT:
                await self._handle_office_hours_announcement(message)
            elif message.type == MessageType.COLLABORATION_REQUEST:
                await self._handle_collaboration_request(message)
            elif message.type == MessageType.COLLABORATION_RESPONSE:
                await self._handle_collaboration_response(message)
            elif message.type == MessageType.COLLABORATION_START:
                await self._handle_collaboration_start(message)
            elif message.type == MessageType.COLLABORATION_END:
                await self._handle_collaboration_end(message)
            elif message.type == MessageType.COLLABORATION_UPDATE:
                await self._handle_collaboration_update(message)
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f'Error in message handler: {e}')
        except Exception as e:
            logger.error(f'Error in internal message handler: {e}')
    async def _handle_agent_discovery(self, message: BeastModeMessage) -> None:
        if self.discovery_enabled:
            try:
                discovered_agent = self.agent_registry.register_agent_discovery(message)
                logger.info(f'Registered agent {discovered_agent.agent_id} with capabilities: {discovered_agent.capabilities.capabilities}')
            except Exception as e:
                logger.error(f'Error registering discovered agent: {e}')
        response = BeastModeMessage(type=MessageType.AGENT_RESPONSE, source=self.agent_id, target=message.source, payload={'agent_capabilities': AgentCapabilities(agent_id=self.agent_id, capabilities=self.capabilities, availability='ready_for_business').model_dump(), 'response_to': message.id}, correlation_id=message.id, priority=3)
        await self.send_message(response)
        logger.info(f'Responded to discovery from {message.source}')
    async def _handle_agent_response(self, message: BeastModeMessage) -> None:
        if self.discovery_enabled:
