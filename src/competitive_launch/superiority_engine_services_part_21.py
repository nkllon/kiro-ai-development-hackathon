from datetime import datetime
from typing import Dict, List, Any

    def get_superiority_summary(self) -> Dict[str, Any]:
        """Get comprehensive superiority summary."""
        try:
            if not self.metrics:
                self.generate_superiority_metrics()
            total_improvement = sum((m.improvement_percentage for m in self.metrics)) / len(self.metrics) if self.metrics else 0
            high_confidence_metrics = len([m for m in self.metrics if m.confidence_level > 0.8])
            average_confidence = sum((m.confidence_level for m in self.metrics)) / len(self.metrics) if self.metrics else 0
            roi = self.calculate_roi()
            evidence_packages = len(self.evidence_packages)
            return {'total_metrics': len(self.metrics), 'average_improvement_percentage': total_improvement, 'high_confidence_metrics': high_confidence_metrics, 'average_confidence_level': average_confidence, 'roi_percentage': roi.roi_percentage, 'payback_period_months': roi.payback_period_months, 'evidence_packages_generated': evidence_packages, 'superiority_verified': total_improvement > 20 and average_confidence > 0.7, 'competitive_advantage_level': self._calculate_competitive_advantage_level()}
        except Exception as e:
            logger.error(f'Failed to generate superiority summary: {e}')
            return {'error': str(e)}
