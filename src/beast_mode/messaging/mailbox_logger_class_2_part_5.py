from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class InitializelogfileClass:
    """Auto-generated class for functions."""

    def _initialize_log_file(self) -> None:
    """Initialize the current log file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    self.current_log_file = self.log_directory / f'mailbox_{timestamp}.log'
    try:
    self.current_log_handle = open(self.current_log_file, 'a', encoding='utf-8')
    logger.info(f'Initialized log file: {self.current_log_file}')
    except Exception as e:
    logger.error(f'Failed to initialize log file: {e}')
    raise

    async def start_logging(self) -> None:
    """Start the continuous background logging process"""
    if self.is_running:
    logger.warning('Mailbox logger is already running')
    return
    try:
    await self._connect_redis()
    self.is_running = True
    self.stats['start_time'] = datetime.now()
    self.logger_task = asyncio.create_task(self._message_logger_loop())
    self.rotation_task = asyncio.create_task(self._rotation_manager_loop())
    logger.info('Mailbox logger started successfully')
    except Exception as e:
    logger.error(f'Failed to start mailbox logger: {e}')
    await self.stop_logging()
    raise

    async def stop_logging(self) -> None:
    """Stop the background logging process"""
    logger.info('Stopping mailbox logger...')
    self.is_running = False
    if self.logger_task and (not self.logger_task.done()):
    self.logger_task.cancel()
    try:
    await self.logger_task
    except asyncio.CancelledError:
    pass
    if self.rotation_task and (not self.rotation_task.done()):
    self.rotation_task.cancel()
    try:
    await self.rotation_task
    except asyncio.CancelledError:
    pass
    await self._disconnect_redis()
    if self.current_log_handle:
    try:
    self.current_log_handle.close()
    self.current_log_handle = None
    except Exception as e:
    logger.error(f'Error closing log file: {e}')
    logger.info('Mailbox logger stopped')

    async def _connect_redis(self) -> None:
    """Connect to Redis with retry logic"""
    max_retries = 5
    retry_delay = 1.0
    for attempt in range(max_retries):
    try:
    logger.info(f'Connecting to Redis (attempt {attempt + 1}/{max_retries})')
    self.client = redis.from_url(self.redis_url, socket_connect_timeout=10.0, socket_timeout=10.0, retry_on_timeout=True, decode_responses=True)
    await self.client.ping()
    self.is_connected = True
    logger.info(f'Connected to Redis at {self.redis_url}')
    return
    except (ConnectionError, TimeoutError) as e:
    self.stats['connection_errors'] += 1
    logger.warning(f'Connection attempt {attempt + 1} failed: {e}')
    if attempt < max_retries - 1:
    await asyncio.sleep(retry_delay * 2 ** attempt)
    else:
    raise ConnectionError(f'Failed to connect to Redis after {max_retries} attempts')
    except Exception as e:
    logger.error(f'Unexpected error connecting to Redis: {e}')
    raise

    async def _disconnect_redis(self) -> None:
    """Disconnect from Redis"""
    try:
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
    logger.error(f'Error during Redis disconnect: {e}')

    async def _message_logger_loop(self) -> None:
    """Main message logging loop"""
    try:
    self.pubsub = self.client.pubsub()
    await self.pubsub.subscribe(self.channel)
    logger.info(f'Started logging messages from channel: {self.channel}')
    async for raw_message in self.pubsub.listen():
    if not self.is_running:
    break
    if raw_message['type'] == 'message':
    await self._log_message(raw_message)
    except asyncio.CancelledError:
    logger.info('Message logger loop cancelled')
    except Exception as e:
    logger.error(f'Error in message logger loop: {e}')
    if self.is_running:
    await self._handle_connection_error()

    async def _log_message(self, raw_message: Dict[str, Any]) -> None:
    """Log a single message with full content preservation"""
    timestamp = datetime.now()
    try:
    log_entry = {'timestamp': timestamp.isoformat(), 'channel': raw_message.get('channel', self.channel), 'raw_data': raw_message['data'], 'parsed_message': None, 'parsing_error': None}
    try:
    message_data = json.loads(raw_message['data'])
    message = BeastModeMessage(**message_data)
    log_entry['parsed_message'] = message.model_dump()
    except json.JSONDecodeError as e:
    log_entry['parsing_error'] = f'JSON decode error: {str(e)}'
    self.stats['parsing_errors'] += 1
    except Exception as e:
    log_entry['parsing_error'] = f'Message validation error: {str(e)}'
    self.stats['parsing_errors'] += 1
    await self._write_log_entry(log_entry)
    self.stats['messages_logged'] += 1
    self.stats['last_message_time'] = timestamp
    except Exception as e:
    logger.error(f'Error logging message: {e}')

    async def _write_log_entry(self, log_entry: Dict[str, Any]) -> None:
    """Write a log entry to the current log file"""
    try:
    log_line = json.dumps(log_entry, default=str) + '\n'
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, self._write_to_file, log_line)
    self.stats['current_log_size'] += len(log_line.encode('utf-8'))
    except Exception as e:
    logger.error(f'Error writing log entry: {e}')
    raise

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

