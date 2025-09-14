from datetime import datetime
from typing import Dict, List, Any

    def _write_to_file(self, log_line: str) -> None:
        """Synchronous file write operation"""
        if self.current_log_handle:
            self.current_log_handle.write(log_line)
            self.current_log_handle.flush()

    async def _rotation_manager_loop(self) -> None:
        """Background loop for log rotation management"""
        try:
            while self.is_running:
                await asyncio.sleep(self.rotation_check_interval)
                if self.is_running:
                    await self._check_log_rotation()
        except asyncio.CancelledError:
            logger.info('Rotation manager loop cancelled')
        except Exception as e:
            logger.error(f'Error in rotation manager loop: {e}')

    async def _check_log_rotation(self) -> None:
        """Check if log rotation is needed and perform it"""
        try:
            if self.stats['current_log_size'] >= self.max_log_size_bytes:
                await self._rotate_log_file()
            await self._cleanup_old_logs()
        except Exception as e:
            logger.error(f'Error during log rotation check: {e}')

    async def _rotate_log_file(self) -> None:
        """Rotate the current log file"""
        try:
            logger.info('Rotating log file...')
            if self.current_log_handle:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.current_log_handle.close)
                self.current_log_handle = None
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._initialize_log_file)
            self.stats['current_log_size'] = 0
            self.stats['log_rotations'] += 1
            logger.info(f'Log rotated to: {self.current_log_file}')
        except Exception as e:
            logger.error(f'Error rotating log file: {e}')
            raise

    async def _cleanup_old_logs(self) -> None:
        """Clean up old log files beyond the retention limit"""
        try:
            log_files = []
            for file_path in self.log_directory.glob('mailbox_*.log'):
                if file_path.is_file():
                    stat = file_path.stat()
                    log_files.append((file_path, stat.st_mtime))
            log_files.sort(key=lambda x: x[1], reverse=True)
            if len(log_files) > self.max_log_files:
                files_to_remove = log_files[self.max_log_files:]
                for file_path, _ in files_to_remove:
                    try:
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, file_path.unlink)
                        logger.info(f'Removed old log file: {file_path}')
                    except Exception as e:
                        logger.error(f'Error removing old log file {file_path}: {e}')
        except Exception as e:
            logger.error(f'Error during log cleanup: {e}')

    async def _handle_connection_error(self) -> None:
        """Handle Redis connection errors with reconnection logic"""
        logger.warning('Handling connection error, attempting to reconnect...')
        try:
            await self._disconnect_redis()
            await asyncio.sleep(5.0)
            if self.is_running:
                await self._connect_redis()
                logger.info('Reconnected to Redis successfully')
        except Exception as e:
            logger.error(f'Failed to reconnect to Redis: {e}')
