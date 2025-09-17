from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


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

