from datetime import datetime
from typing import Dict, List, Any

    def get_interface_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive interface health report"""
        if not self.health_checks:
            return {"message": "No health checks available"}
        
        total_interfaces = len(self.health_checks)
        healthy_interfaces = len([h for h in self.health_checks.values() if h.health_score > 0.7])
        warning_interfaces = len([h for h in self.health_checks.values() if 0.4 <= h.health_score <= 0.7])
        critical_interfaces = len([h for h in self.health_checks.values() if h.health_score < 0.4])
        
        avg_health_score = sum(h.health_score for h in self.health_checks.values()) / total_interfaces
        
        # Most common issues
        all_issues = []
        for health in self.health_checks.values():
            all_issues.extend(health.issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        most_common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_interfaces': total_interfaces,
            'healthy_interfaces': healthy_interfaces,
            'warning_interfaces': warning_interfaces,
            'critical_interfaces': critical_interfaces,
            'average_health_score': round(avg_health_score, 3),
            'most_common_issues': most_common_issues,
            'health_distribution': {
                'healthy': healthy_interfaces,
                'warning': warning_interfaces,
                'critical': critical_interfaces
            }
        }
    