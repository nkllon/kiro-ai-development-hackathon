from src.rm_ddd.core.registry import register_module

def __init__(self, redis_url: str='redis://localhost:6379', log_directory: str='beast_mode_mailbox', channel: str='beast_mode_network', max_log_size_mb: int=100, max_log_files: int=10, rotation_check_interval: int=300):
    self.redis_url = redis_url
    self.log_directory = Path(log_directory)
    self.channel = channel
    self.max_log_size_bytes = max_log_size_mb * 1024 * 1024
    self.max_log_files = max_log_files
    self.rotation_check_interval = rotation_check_interval
    self.client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_running = False
    self.is_connected = False
    self.logger_task: Optional[asyncio.Task] = None
    self.rotation_task: Optional[asyncio.Task] = None
    self.current_log_file: Optional[Path] = None
    self.current_log_handle = None
    self.stats = {'messages_logged': 0, 'parsing_errors': 0, 'connection_errors': 0, 'log_rotations': 0, 'start_time': None, 'last_message_time': None, 'current_log_size': 0}
    self.log_directory.mkdir(parents=True, exist_ok=True)
    self._initialize_log_file()
