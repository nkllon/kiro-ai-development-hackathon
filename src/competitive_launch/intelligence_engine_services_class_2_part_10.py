from src.rm_ddd.core.registry import register_module

    def _detect_competitor_moves(self) -> List[CompetitorMove]:
        """Detect recent competitor moves (simulated)."""
        return [CompetitorMove(competitor='Meta', move_type='feature_announcement', announcement_date=datetime.now() - timedelta(days=1), description='Meta announces AI-powered development tools', market_impact=0.7, response_urgency=ThreatLevel.URGENT)]
