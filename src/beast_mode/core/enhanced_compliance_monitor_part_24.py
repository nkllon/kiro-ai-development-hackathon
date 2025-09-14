from datetime import datetime
from typing import Dict, List, Any

    def check_compliance(self) -> ComplianceMetrics:
        """Check current compliance status"""
        try:
            # Run honest compliance reporter
            result = subprocess.run([
                'python3', 'scripts/honest_compliance_reporter.py'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            # Parse compliance data
            compliance_data = self._parse_compliance_output(result.stdout)
            
            # Create metrics
            metrics = ComplianceMetrics(
                total_files=compliance_data['total_files'],
                valid_files=compliance_data['valid_files'],
                error_files=compliance_data['error_files'],
                compliance_percentage=compliance_data['compliance_percentage'],
                compliance_level=self._determine_compliance_level(compliance_data['compliance_percentage']),
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            # Return default metrics on error
            return ComplianceMetrics(
                total_files=0,
                valid_files=0,
                error_files=0,
                compliance_percentage=0.0,
                compliance_level=ComplianceLevel.POOR,
                timestamp=datetime.now()
            )
    