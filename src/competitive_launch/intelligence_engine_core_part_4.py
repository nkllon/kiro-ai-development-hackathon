from src.rm_ddd.core.health import ModuleHealth

def generate_differentiation_strategy(self, competitor_move: CompetitorMove) -> Dict[str, Any]:
    """
        Generate systematic differentiation strategy.
        
        Args:
            competitor_move: The competitor move to respond to
            
        Returns:
            Dict containing differentiation strategy
        """
    logger.info(f'Generating differentiation strategy for {competitor_move.competitor} move: {competitor_move.move_type}')
    try:
        move_analysis = self._analyze_competitor_move(competitor_move)
        differentiation_ops = self._identify_differentiation_opportunities(move_analysis)
        counter_strategy = self._generate_counter_strategy(differentiation_ops)
        implementation_plan = self._create_implementation_plan(counter_strategy)
        advantage_metrics = self._calculate_differentiation_advantage(counter_strategy)
        result = {'strategy_type': counter_strategy['type'], 'differentiation_factors': differentiation_ops['factors'], 'implementation_timeline': implementation_plan['timeline_days'], 'competitive_advantage': advantage_metrics['advantage_score'], 'success_criteria': counter_strategy['success_criteria'], 'risk_mitigation': counter_strategy['risk_mitigation']}
        logger.info(f"Differentiation strategy generated: {result['competitive_advantage']:.2%} advantage")
        return result
    except Exception as e:
        logger.error(f'Differentiation strategy generation failed: {e}')
        return {'strategy_type': 'failed', 'error': str(e)}

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

