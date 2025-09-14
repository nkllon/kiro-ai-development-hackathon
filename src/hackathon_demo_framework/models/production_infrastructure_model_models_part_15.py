
    def _generate_cost_metrics(self, config: GKEConfig) -> Dict[str, Any]:
        """Generate cost metrics for deployed cluster"""
        base_cost = 500.0
        node_cost = config.node_count * 50.0
        machine_cost = 100.0 if 'e2-medium' in config.machine_type else 150.0
        scaling_cost = 50.0 if config.auto_scaling else 0.0
        total_cost = base_cost + node_cost + machine_cost + scaling_cost
        return {'monthly_cost': total_cost, 'cost_breakdown': {'base_cost': base_cost, 'node_cost': node_cost, 'machine_cost': machine_cost, 'scaling_cost': scaling_cost}, 'optimization_potential': {'savings_percentage': 25.0, 'potential_savings': total_cost * 0.25, 'optimization_level': config.cost_optimization.value}, 'cost_per_request': total_cost / 1000000, 'roi_metrics': {'break_even_months': 3, 'annual_savings': total_cost * 0.25 * 12}}
