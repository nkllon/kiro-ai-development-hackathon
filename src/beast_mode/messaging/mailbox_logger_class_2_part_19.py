from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class StartClass:
    """Auto-generated class for functions."""

    def start(self) -> None:
    """Start the mailbox logger in a background thread"""
    if self.is_running:
    logger.warning('MailboxLogger is already running')
    return
