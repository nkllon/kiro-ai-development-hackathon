from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, project_path: Path, config: Optional[HackathonConfig]=None):
        register_module(self.__class__.__name__, self)
        """
        Initialize the demo controller.
        
        Args:
            project_path: Path to the project being prepared for hackathon
            config: Hackathon configuration (uses DevPost template if not provided)
        """
        self.project_path = Path(project_path)
        self.config = config or DEVPOST_HACKATHON_TEMPLATE
        self.logger = logging.getLogger(__name__)
        self.beast_mode_orchestrator = None
        self.rca_analyzer = None
        self.rdi_validator = None
        if BEAST_MODE_AVAILABLE:
            try:
                self.beast_mode_orchestrator = BeastModeTestOrchestrator(self.project_path)
                self.rca_analyzer = RCAPatternAnalyzer()
                self.rdi_validator = RDIChainValidator(self.project_path)
                self.logger.info('Beast Mode framework integration initialized')
            except Exception as e:
                self.logger.warning(f'Beast Mode integration failed: {e}')
        self.validation_gates = ['technical_completeness', 'systematic_excellence', 'presentation_readiness', 'compliance_verification', 'demo_reliability']
        self.logger.info(f'Hackathon Demo Controller initialized for {self.config.hackathon_name}')
