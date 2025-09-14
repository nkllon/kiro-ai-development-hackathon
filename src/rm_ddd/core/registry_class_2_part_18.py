
    def _stop_health_monitoring(self):
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Stop periodic health monitoring."""
        if self._health_check_task:
            self._health_check_task.cancel()
            logger.info('Stopped registry health monitoring')

    async def _health_monitoring_loop(self):
        """Main health monitoring loop for the registry."""
        try:
            while True:
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self._health_check_interval.total_seconds())
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f'Error in registry health monitoring: {e}')
                    await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info('Registry health monitoring cancelled')

    async def _perform_health_checks(self):
        """Perform health checks on all registered modules."""
        with self._lock:
            modules_to_check = list(self._modules.values())
        for registered_module in modules_to_check:
            try:
                health_status = await registered_module.module.perform_health_check()
                await self.update_module_health(registered_module.module_id, health_status)
            except Exception as e:
                logger.error(f'Health check failed for module {registered_module.module_id}: {e}')

    async def shutdown(self):
        """Gracefully shutdown the registry."""
        logger.info('Shutting down GlobalRegistry')
        self._stop_health_monitoring()
        if self._health_check_task:
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        with self._lock:
            self._modules.clear()
            self._capabilities.clear()
        logger.info('GlobalRegistry shutdown complete')
