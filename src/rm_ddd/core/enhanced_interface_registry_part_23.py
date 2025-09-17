from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Enhanced interface registration with metrics"""
        success = super().register_interface(interface)
        if success:
            # Initialize metrics for new interface
            self.metrics[interface.interface_id] = InterfaceMetrics(
                interface_id=interface.interface_id,
                usage_count=0,
                last_accessed=datetime.now(),
                performance_score=1.0,
                error_count=0,
                success_rate=1.0
            )
            self.save_metrics()
        return success

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

    