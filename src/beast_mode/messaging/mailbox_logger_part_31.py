from datetime import datetime
from typing import Dict, List, Any

def __init__(self, **logger_kwargs):
    self.logger = MailboxLogger(**logger_kwargs)
    self.background_thread: Optional[threading.Thread] = None
    self.event_loop: Optional[asyncio.AbstractEventLoop] = None
    self.is_running = False
