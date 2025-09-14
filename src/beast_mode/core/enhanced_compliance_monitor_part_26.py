from datetime import datetime
from typing import Dict, List, Any

    def _determine_compliance_level(self, percentage: float) -> ComplianceLevel:
        """Determine compliance level based on percentage"""
        if percentage >= 95.0:
            return ComplianceLevel.EXCELLENT
        elif percentage >= 90.0:
            return ComplianceLevel.GOOD
        elif percentage >= 80.0:
            return ComplianceLevel.FAIR
        else:
            return ComplianceLevel.POOR
    