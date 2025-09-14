"""
Mailbox Logger Services

This module was extracted from mailbox_logger.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError
from .models import BeastModeMessage, MessageType

class MailboxLoggerManager:
    """
    Manager for running MailboxLogger as a background service.
    
    Provides a simple interface for starting/stopping the logger
    and managing its lifecycle.
    """

    def __init__(self, **logger_kwargs):
        self.logger = MailboxLogger(**logger_kwargs)
        self.background_thread: Optional[threading.Thread] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.is_running = False

    def start(self) -> None:
        """Start the mailbox logger in a background thread"""
        if self.is_running:
            logger.warning('MailboxLogger is already running')
            return

        def run_logger():
            """Run the logger in its own event loop"""
            try:
                self.event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.event_loop)
                self.event_loop.run_until_complete(self.logger.start_logging())
                self.event_loop.run_forever()
            except Exception as e:
                logger.error(f'Error in background logger thread: {e}')
            finally:
                if self.event_loop:
                    self.event_loop.close()
        self.background_thread = threading.Thread(target=run_logger, daemon=True)
        self.background_thread.start()
        self.is_running = True
        logger.info('MailboxLogger started in background thread')

    def stop(self) -> None:
        """Stop the mailbox logger"""
        if not self.is_running:
            return
        try:
            if self.event_loop and (not self.event_loop.is_closed()):
                future = asyncio.run_coroutine_threadsafe(self.logger.stop_logging(), self.event_loop)
                future.result(timeout=10.0)
                self.event_loop.call_soon_threadsafe(self.event_loop.stop)
            if self.background_thread and self.background_thread.is_alive():
                self.background_thread.join(timeout=5.0)
            self.is_running = False
            logger.info('MailboxLogger stopped')
        except Exception as e:
            logger.error(f'Error stopping MailboxLogger: {e}')

    def get_status(self) -> Dict[str, Any]:
        """Get status of the logger manager"""
        return {'manager_running': self.is_running, 'thread_alive': self.background_thread.is_alive() if self.background_thread else False, 'logger_status': self.logger.get_health_status()}

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
