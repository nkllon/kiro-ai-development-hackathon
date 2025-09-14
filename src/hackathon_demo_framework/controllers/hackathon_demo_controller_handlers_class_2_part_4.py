from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        register_module(self.__class__.__name__, self)
        self.spec_model = SpecToCodeModel()
        self.superiority_model = SystematicSuperiorityModel()
        self.agent_model = MultiAgentCollaborationModel()
        self.infra_model = ProductionInfrastructureModel()
        self.demo_view = HackathonDemoView()
        self.active_sessions: Dict[str, DemoSession] = {}
        self.transformation_history: List[TransformationResult] = []
        self.collaboration_history: List[CollaborationResult] = []
        self.systematic_scores: List[float] = []
        self.learning_patterns: List[Dict[str, Any]] = []
