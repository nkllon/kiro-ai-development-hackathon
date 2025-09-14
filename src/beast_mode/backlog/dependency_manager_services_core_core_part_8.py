from src.rm_ddd.core.health import ModuleHealth

class CalculatecriticalpathClass:
    """Auto-generated class for functions."""

    def calculate_critical_path(self, track_filter: Optional[str]=None) -> CriticalPathAnalysis:
    """
    Calculate critical path through dependency graph with performance optimization

    Args:
    track_filter: Optional filter to specific strategic track

    Returns:
    CriticalPathAnalysis with critical path and performance metrics
    """
    start_time = time.time()
    try:
    graph = self._get_cached_graph()
    filtered_nodes = self._filter_nodes_by_track(graph.nodes, track_filter) if track_filter else graph.nodes
    critical_path, total_duration = self._calculate_longest_path(graph, filtered_nodes)
    bottlenecks = self._identify_bottlenecks(graph, critical_path)
    risk_factors = self._assess_path_risks(critical_path)
    calculation_time = (time.time() - start_time) * 1000
    return CriticalPathAnalysis(critical_path=critical_path, total_duration=total_duration, bottlenecks=bottlenecks, risk_factors=risk_factors, calculation_time_ms=calculation_time)
    except Exception as e:
    self.logger.error(f'Critical path calculation failed: {str(e)}')
    calculation_time = (time.time() - start_time) * 1000
    return CriticalPathAnalysis(critical_path=[], total_duration=timedelta(0), bottlenecks=[], risk_factors={}, calculation_time_ms=calculation_time)
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

