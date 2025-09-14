from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _analyze_trend_alignment(self, trends: List[MarketTrend]) -> Dict[str, Any]:
        """Analyze how well trends align with systematic approach."""
        high_alignment = [t for t in trends if t.alignment_with_systematic > 0.8]
        return {'high_alignment_count': len(high_alignment), 'average_alignment': sum((t.alignment_with_systematic for t in trends)) / len(trends), 'opportunity_score': sum((t.impact_score for t in high_alignment)) / len(high_alignment) if high_alignment else 0}
