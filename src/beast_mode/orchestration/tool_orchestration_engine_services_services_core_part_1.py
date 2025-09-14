from src.rm_ddd.core.health import ModuleHealth

def __init__(self, project_root: str='.'):
    super().__init__('tool_orchestration_engine')
    self.project_root = Path(project_root)
    self.tools_registry = {}
    self.tool_health_cache = {}
    self.decision_history = []
    self.confidence_thresholds = {'high_threshold': 0.8, 'medium_threshold': 0.5, 'low_threshold': 0.0}
    self.orchestration_metrics = {'total_orchestrations': 0, 'successful_orchestrations': 0, 'failed_orchestrations': 0, 'tools_repaired': 0, 'fallbacks_used': 0, 'average_execution_time_ms': 0.0, 'decision_confidence_distribution': {'high': 0, 'medium': 0, 'low': 0}}
    self.intelligence_engine = ModelDrivenIntelligenceEngine()
    self.rca_engine = RCAEngine()
    self.multi_perspective_engine = MultiStakeholderPerspectiveEngine()
    self.executor = ThreadPoolExecutor(max_workers=5)
    self._initialize_default_tools()
    self._update_health_indicator('tool_orchestration_engine', HealthStatus.HEALTHY, 'operational', 'Tool orchestration engine ready for systematic decision making')
