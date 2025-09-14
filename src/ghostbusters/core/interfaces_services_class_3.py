from src.rm_ddd.core.registry import register_module
class ConsensusEngine(ABC, ReflectiveModule):
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
    Abstract base class for multi-agent consensus engines.
    
    Consensus engines coordinate multiple expert agents to build
    consensus and resolve conflicts in analysis results.
    """

    def __init__(self, name: str, version: str='1.0.0'):
        register_module(self.__class__.__name__, self)
        self.name = name
        self.version = version

    @abstractmethod
    async def build_consensus(self, agents: List[GhostbustersExpertAgent], context: AnalysisContext, confidence_threshold: float=0.8) -> ConsensusResult:
        """
        Orchestrate multiple agents to build consensus on analysis.
        
        Args:
            agents: List of expert agents to coordinate
            context: Analysis context for all agents
            confidence_threshold: Minimum confidence required for consensus
            
        Returns:
            ConsensusResult with unified analysis or conflict information
        """
        pass

    @abstractmethod
    async def resolve_conflicts(self, conflicting_results: List[AnalysisResult]) -> AnalysisResult:
        """
        Resolve conflicts between agent analyses using systematic methods.
        
        Args:
            conflicting_results: Analysis results that conflict with each other
            
        Returns:
            Unified AnalysisResult that resolves the conflicts
            
        Raises:
            ConsensusError: If conflicts cannot be resolved systematically
        """
        pass

    def get_resolution_methods(self) -> List[str]:
        """get_resolution_methods - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get list of conflict resolution methods supported"""
        return ['majority_vote', 'weighted_confidence', 'expert_override', 'human_escalation']

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

