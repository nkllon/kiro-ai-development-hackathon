from src.rm_ddd.core.health import ModuleHealth

    def __init__(self) -> Any:
        """__init__ - Enhanced for compliance"""
        super().__init__('ToolHealthManager')
        self.logger = logging.getLogger(__name__)
        self.monitored_tools: Dict[str, Dict[str, Any]] = {}
        self.repair_history: List[ToolRepairResult] = []
        self.health_baselines: Dict[str, Dict[str, Any]] = {}
        self._initialize_tool_monitoring()
        self.logger.info('🔧 Tool Health Manager initialized - ready to fix tools first!')
