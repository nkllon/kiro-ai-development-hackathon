from src.rm_ddd.core.health import ModuleHealth

    def monitor_tool_health_continuously(self) -> Dict[str, Any]:
        """Continuously monitor tool health and detect degradation"""
        self.logger.info('👀 Performing continuous tool health monitoring')
        health_report = {'monitoring_timestamp': datetime.now().isoformat(), 'tools_monitored': len(self.monitored_tools), 'healthy_tools': 0, 'degraded_tools': 0, 'failed_tools': 0, 'tool_statuses': {}}
        for tool_name in self.monitored_tools:
            tool_health = self._assess_tool_health(tool_name)
            health_report['tool_statuses'][tool_name] = tool_health
            if tool_health['status'] == 'healthy':
                health_report['healthy_tools'] += 1
            elif tool_health['status'] == 'degraded':
                health_report['degraded_tools'] += 1
            else:
                health_report['failed_tools'] += 1
            if tool_health['status'] in ['degraded', 'failed']:
                self.logger.warning(f"⚠️ Tool {tool_name} needs attention: {tool_health['status']}")
        self.logger.info(f"👀 Health monitoring complete: {health_report['healthy_tools']}/{health_report['tools_monitored']} tools healthy")
        return health_report

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

