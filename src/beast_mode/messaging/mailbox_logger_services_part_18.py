from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def start(self) -> None:
        """Start the mailbox logger in a background thread"""
        if self.is_running:
            logger.warning('MailboxLogger is already running')
            return
