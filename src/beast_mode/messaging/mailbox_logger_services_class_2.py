from src.rm_ddd.core.registry import register_module
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
        register_module(self.__class__.__name__, self)
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

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

