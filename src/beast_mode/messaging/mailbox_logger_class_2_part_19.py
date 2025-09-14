from src.rm_ddd.core.registry import register_module

def start(self) -> None:
    """Start the mailbox logger in a background thread"""
    if self.is_running:
        logger.warning('MailboxLogger is already running')
        return
