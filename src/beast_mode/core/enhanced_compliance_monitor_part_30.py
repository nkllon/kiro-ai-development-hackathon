from datetime import datetime
from typing import Dict, List, Any

    def export_compliance_report(self, file_path: str):
        """Export compliance report to file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'compliance_report': self.get_compliance_report(),
            'metrics_history': [
                {
                    'timestamp': metrics.timestamp.isoformat(),
                    'compliance_percentage': metrics.compliance_percentage,
                    'compliance_level': metrics.compliance_level.value,
                    'total_files': metrics.total_files,
                    'valid_files': metrics.valid_files,
                    'error_files': metrics.error_files
                }
                for metrics in self.metrics_history
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)

# Global instance