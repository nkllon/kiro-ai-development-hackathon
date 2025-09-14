from src.rm_ddd.core.registry import register_module

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the mailbox logger"""
        return {'status': 'healthy' if self.is_running and self.is_connected else 'unhealthy', 'is_running': self.is_running, 'is_connected': self.is_connected, 'redis_url': self.redis_url, 'channel': self.channel, 'log_directory': str(self.log_directory), 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'stats': self.get_logger_stats(), 'log_files': len(self.get_log_files())}

        register_module(self.__class__.__name__, self)