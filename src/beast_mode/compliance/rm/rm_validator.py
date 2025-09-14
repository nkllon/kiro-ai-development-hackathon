"""
Compliance System - Requirements-Driven Implementation
====================================================
Generated from requirements: Validate interface compliance standards, Track compliance metrics and scores, Provide compliance reporting, Support automated compliance checks
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ComplianceLevel(Enum):
    """Compliance level enumeration"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"

@dataclass
class ComplianceResult:
    """Compliance validation result"""
    interface_name: str
    compliance_score: float
    level: ComplianceLevel
    issues: List[str]
    recommendations: List[str]
    validated_at: datetime

class ComplianceSystem:
    """Compliance System - Requirements-Driven Implementation"""
    
    def __init__(self):
        self.compliance_results: Dict[str, ComplianceResult] = {}
        self.compliance_file = ".beast_mode/compliance_results.json"
    
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
    
    def get_compliance_score(self, interface_name: str) -> Optional[float]:
        """Get compliance score for interface"""
        if interface_name in self.compliance_results:
            return self.compliance_results[interface_name].compliance_score
        return None
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate compliance report"""
        if not self.compliance_results:
            return {"message": "No compliance data available"}
        
        total_interfaces = len(self.compliance_results)
        high_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.HIGH])
        medium_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.MEDIUM])
        low_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.LOW])
        critical_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.CRITICAL])
        
        avg_score = sum(r.compliance_score for r in self.compliance_results.values()) / total_interfaces
        
        return {
            "total_interfaces": total_interfaces,
            "average_compliance_score": round(avg_score, 2),
            "compliance_distribution": {
                "high": high_compliance,
                "medium": medium_compliance,
                "low": low_compliance,
                "critical": critical_compliance
            },
            "results": {
                name: {
                    "score": result.compliance_score,
                    "level": result.level.value,
                    "issues": result.issues,
                    "recommendations": result.recommendations
                }
                for name, result in self.compliance_results.items()
            }
        }
    
    def check_standards(self, interface_data: Dict[str, Any]) -> List[str]:
        """Check compliance standards"""
        standards_checks = []
        
        # Check naming conventions
        if 'name' in interface_data:
            name = interface_data['name']
            if not name[0].isupper():
                standards_checks.append("Interface name should start with uppercase")
            if '_' in name and not name.isupper():
                standards_checks.append("Consider using CamelCase for interface names")
        
        # Check method naming
        if 'methods' in interface_data:
            for method in interface_data['methods']:
                if not method.startswith(('get_', 'set_', 'is_', 'has_', 'validate_', 'register_')):
                    standards_checks.append(f"Method '{method}' should follow naming conventions")
        
        return standards_checks

# Global compliance system instance
compliance_system = ComplianceSystem()
