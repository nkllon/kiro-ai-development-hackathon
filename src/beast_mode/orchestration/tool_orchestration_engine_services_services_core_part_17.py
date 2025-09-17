
def integrate_with_rca_engine(self, rca_engine_instance: Optional[Any]=None) -> Dict[str, Any]:
    """
        Integrate with completed RCA engine for systematic tool problem resolution
        Task 14 Requirement: Integrate with completed RCA engine
        """
    try:
        if rca_engine_instance:
            self.rca_engine = rca_engine_instance
        else:
            from ..analysis.rca_engine import RCAEngine
from src.rm_ddd.core.health import ModuleHealth

            self.rca_engine = RCAEngine()
        self.logger.info('Successfully integrated with completed RCA engine')
        return {'integration_successful': True, 'rca_engine_healthy': self.rca_engine.is_healthy(), 'rca_pattern_library_size': len(getattr(self.rca_engine, 'pattern_library', {})), 'systematic_tool_resolution_enabled': True}
    except Exception as e:
        self.logger.error(f'RCA engine integration failed: {e}')
        return {'integration_successful': False, 'error': str(e), 'fallback_mode': 'basic_tool_orchestration'}

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

