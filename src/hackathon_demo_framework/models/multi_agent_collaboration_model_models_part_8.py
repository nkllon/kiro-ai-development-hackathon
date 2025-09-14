from src.rm_ddd.core.health import ModuleHealth

    def _initialize_default_agents(self):
        """Initialize default set of specialized agents"""
        self.agents = [Agent(agent_id='ARCH-001', agent_type=AgentType.ARCHITECT, name='Architect Agent', capabilities=['system_design', 'scalability', 'patterns', 'architecture_review'], expertise_level=0.95, collaboration_score=0.9, created_at=datetime.now()), Agent(agent_id='SEC-001', agent_type=AgentType.SECURITY, name='Security Agent', capabilities=['security_analysis', 'vulnerability_assessment', 'compliance', 'threat_modeling'], expertise_level=0.92, collaboration_score=0.88, created_at=datetime.now()), Agent(agent_id='PERF-001', agent_type=AgentType.PERFORMANCE, name='Performance Agent', capabilities=['performance_analysis', 'optimization', 'monitoring', 'scalability'], expertise_level=0.89, collaboration_score=0.91, created_at=datetime.now()), Agent(agent_id='QUAL-001', agent_type=AgentType.QUALITY, name='Quality Agent', capabilities=['code_review', 'testing', 'validation', 'best_practices'], expertise_level=0.93, collaboration_score=0.87, created_at=datetime.now()), Agent(agent_id='INT-001', agent_type=AgentType.INTEGRATION, name='Integration Agent', capabilities=['api_integration', 'deployment', 'monitoring', 'orchestration'], expertise_level=0.9, collaboration_score=0.89, created_at=datetime.now())]

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

