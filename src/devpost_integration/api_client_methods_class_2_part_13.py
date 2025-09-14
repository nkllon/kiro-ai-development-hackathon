from src.rm_ddd.core.health import ModuleHealth

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        try:
            uptime = (datetime.now() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 0)
            success_count = total_operations - error_count
            success_rate = (success_count / total_operations) if total_operations > 0 else 1.0
            error_rate = (error_count / total_operations) if total_operations > 0 else 0.0
            health_status = self.check_health()
            
            return {
                'uptime_seconds': uptime,
                'total_operations': total_operations,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'health_status': health_status.value,
                'module_id': getattr(self, 'module_id', 'unknown'),
                'version': getattr(self, 'version', 'unknown'),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {
                'error': str(e),
                'health_status': 'UNHEALTHY',
                'last_updated': datetime.now().isoformat()
            }

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

    