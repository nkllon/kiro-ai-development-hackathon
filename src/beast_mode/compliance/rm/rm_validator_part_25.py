from datetime import datetime
from typing import Dict, List, Any

    def get_compliance_score(self, interface_name: str) -> Optional[float]:
        """Get compliance score for interface"""
        if interface_name in self.compliance_results:
            return self.compliance_results[interface_name].compliance_score
        return None
    