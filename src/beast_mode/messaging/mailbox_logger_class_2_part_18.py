from src.rm_ddd.core.registry import register_module

def __init__(self, **logger_kwargs):
    self.logger = MailboxLogger(**logger_kwargs)
    self.background_thread: Optional[threading.Thread] = None
    self.event_loop: Optional[asyncio.AbstractEventLoop] = None
    self.is_running = False
