from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        if not self.validation_history:
            return {'message': 'No validation history available'}
        
        total_reports = len(self.validation_history)
        avg_score = sum(report.overall_score for report in self.validation_history) / total_reports
        
        return {
            'total_components_validated': total_reports,
            'average_score': avg_score,
            'last_validation': self.validation_history[-1].timestamp.isoformat(),
            'validation_trend': 'improving' if len(self.validation_history) > 1 and 
                              self.validation_history[-1].overall_score > self.validation_history[-2].overall_score 
                              else 'stable'
        }
    