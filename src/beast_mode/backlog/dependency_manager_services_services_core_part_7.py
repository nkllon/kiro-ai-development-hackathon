from src.rm_ddd.core.health import ModuleHealth

def detect_circular_dependencies(self) -> CircularDependencyReport:
    """
        Detect circular dependencies in the dependency graph
        
        Returns:
            CircularDependencyReport with detected cycles and resolution suggestions
        """
    start_time = time.time()
    try:
        graph = self._get_cached_graph()
        cycles = self._find_cycles_dfs(graph)
        affected_items = set()
        for cycle in cycles:
            affected_items.update(cycle)
        suggestions = self._generate_cycle_resolution_suggestions(cycles)
        detection_time = (time.time() - start_time) * 1000
        return CircularDependencyReport(cycles_found=cycles, affected_items=affected_items, resolution_suggestions=suggestions, detection_time_ms=detection_time)
    except Exception as e:
        self.logger.error(f'Cycle detection failed: {str(e)}')
        detection_time = (time.time() - start_time) * 1000
        return CircularDependencyReport(cycles_found=[], affected_items=set(), resolution_suggestions=[f'Error during cycle detection: {str(e)}'], detection_time_ms=detection_time)
    finally:
        self._record_operation_time(time.time() - start_time)

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

