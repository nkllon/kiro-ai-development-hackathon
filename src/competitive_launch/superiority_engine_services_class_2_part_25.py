from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_competitive_advantage_level(self) -> str:
        """Calculate overall competitive advantage level."""
        if not self.metrics:
            return 'Unknown'
        avg_improvement = sum((m.improvement_percentage for m in self.metrics)) / len(self.metrics)
        if avg_improvement > 50:
            return 'Exceptional'
        elif avg_improvement > 30:
            return 'Significant'
        elif avg_improvement > 15:
            return 'Moderate'
        else:
            return 'Minimal'
