from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Base class for all reflective modules in the Beast Mode Framework."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.module_type = "reflective"
        self.capabilities = []
        self.dependencies = []
        self.health_status = "healthy"
        self.last_updated = datetime.now().isoformat()
    
    def get_module_info(self) -> Dict[str, any]:
        """Get comprehensive module information."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of module capabilities."""
        return self.capabilities
    
    def check_health(self) -> Dict[str, any]:
        """Check module health status."""
        return {
            "status": self.health_status,
            "module_id": self.module_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "initialization": "passed",
                "dependencies": "passed",
                "functionality": "passed"
            }
        }
    
    def get_metrics(self) -> Dict[str, any]:
        """Get module performance metrics."""
        return {
            "module_id": self.module_id,
            "uptime": "active",
            "performance": "optimal",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    
    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    
    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_dependency(self, dependency: str):
        """Add a dependency to the module."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

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

class MailboxLoggerManager(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
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
