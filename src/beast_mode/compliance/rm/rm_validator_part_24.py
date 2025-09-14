from datetime import datetime
from typing import Dict, List, Any

    def validate_compliance(self, interface_name: str, interface_data: Dict[str, Any]) -> ComplianceResult:
        """Validate interface compliance standards"""
        issues = []
        recommendations = []
        score = 100.0
        
        # Check interface name
        if not interface_name or len(interface_name) < 3:
            issues.append("Interface name too short")
            score -= 20
        
        # Check required methods
        required_methods = ['register', 'validate', 'get_metadata']
        if 'methods' in interface_data:
            missing_methods = [method for method in required_methods if method not in interface_data['methods']]
            if missing_methods:
                issues.append(f"Missing required methods: {missing_methods}")
                score -= len(missing_methods) * 10
        
        # Check file path
        if 'file_path' not in interface_data or not interface_data['file_path']:
            issues.append("Missing file path")
            score -= 15
        
        # Generate recommendations
        if score < 80:
            recommendations.append("Improve interface implementation")
        if score < 60:
            recommendations.append("Add missing required methods")
        if score < 40:
            recommendations.append("Critical compliance issues need immediate attention")
        
        # Determine compliance level
        if score >= 90:
            level = ComplianceLevel.HIGH
        elif score >= 70:
            level = ComplianceLevel.MEDIUM
        elif score >= 50:
            level = ComplianceLevel.LOW
        else:
            level = ComplianceLevel.CRITICAL
        
        result = ComplianceResult(
            interface_name=interface_name,
            compliance_score=max(0.0, score),
            level=level,
            issues=issues,
            recommendations=recommendations,
            validated_at=datetime.now()
        )
        
        self.compliance_results[interface_name] = result
        return result
    