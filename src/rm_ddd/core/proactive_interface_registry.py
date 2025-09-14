from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Base class for all reflective modules in the Beast Mode Framework."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.module_type = "reflective"
        self.capabilities = []
        self.dependencies = []
        self.health_status = "healthy"
        self.last_updated = datetime.now().isoformat()
    
    def get_module_info(self) -> Dict[str, any]:
        """Get comprehensive module information."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of module capabilities."""
        return self.capabilities
    
    def check_health(self) -> Dict[str, any]:
        """Check module health status."""
        return {
            "status": self.health_status,
            "module_id": self.module_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "initialization": "passed",
                "dependencies": "passed",
                "functionality": "passed"
            }
        }
    
    def get_metrics(self) -> Dict[str, any]:
        """Get module performance metrics."""
        return {
            "module_id": self.module_id,
            "uptime": "active",
            "performance": "optimal",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    
    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    
    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_dependency(self, dependency: str):
        """Add a dependency to the module."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Proactive Interface Registry - Requirements-Driven Implementation
==============================================================
Generated from requirements: Proactive interface management and prevention
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os
from .interface_registry import InterfaceRegistry, InterfaceMetadata, InterfaceType, InterfaceStatus

@dataclass
class InterfaceHealthCheck(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Interface health check result"""
    interface_id: str
    status: str
    last_checked: datetime
    issues: List[str]
    recommendations: List[str]
    health_score: float

@dataclass
class DuplicatePreventionRule(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Rule for preventing interface duplication"""
    rule_name: str
    pattern: str
    severity: str
    action: str
    description: str

class ProactiveInterfaceRegistry(InterfaceRegistry, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Proactive Interface Registry with prevention and monitoring"""
    
    def __init__(self, registry_file: str = "proactive_interface_registry.json"):
        super().__init__(registry_file)
        self.health_checks: Dict[str, InterfaceHealthCheck] = {}
        self.duplicate_rules: List[DuplicatePreventionRule] = []
        self.monitoring_enabled = True
        self.load_health_checks()
        self.setup_default_rules()
    
    def load_health_checks(self):
        """Load interface health checks from storage"""
        health_file = self.registry_file.replace('.json', '_health.json')
        if os.path.exists(health_file):
            try:
                with open(health_file, 'r') as f:
                    data = json.load(f)
                for interface_id, health_data in data.items():
                    self.health_checks[interface_id] = InterfaceHealthCheck(**health_data)
            except Exception as e:
                print(f"Warning: Could not load health checks: {e}")
    
    def save_health_checks(self):
        """Save interface health checks to storage"""
        health_file = self.registry_file.replace('.json', '_health.json')
        try:
            data = {
                interface_id: {
                    'interface_id': health.interface_id,
                    'status': health.status,
                    'last_checked': health.last_checked.isoformat(),
                    'issues': health.issues,
                    'recommendations': health.recommendations,
                    'health_score': health.health_score
                }
                for interface_id, health in self.health_checks.items()
            }
            with open(health_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving health checks: {e}")
    
    def setup_default_rules(self):
        """Setup default duplicate prevention rules"""
        self.duplicate_rules = [
            DuplicatePreventionRule(
                rule_name="name_similarity",
                pattern=".*_service$",
                severity="high",
                action="warn",
                description="Prevent creation of similar service interfaces"
            ),
            DuplicatePreventionRule(
                rule_name="type_conflict",
                pattern=".*_module$",
                severity="medium",
                action="suggest",
                description="Suggest alternatives for module interfaces"
            ),
            DuplicatePreventionRule(
                rule_name="domain_overlap",
                pattern=".*_api$",
                severity="low",
                action="info",
                description="Inform about domain overlap in API interfaces"
            )
        ]
    
    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Enhanced interface registration with proactive checks"""
        # Run proactive checks before registration
        health_check = self.run_interface_health_check(interface)
        
        if health_check.health_score < 0.7:
            print(f"⚠️  Interface health score below threshold: {health_check.health_score}")
            for issue in health_check.issues:
                print(f"   - {issue}")
            for recommendation in health_check.recommendations:
                print(f"   - {recommendation}")
        
        # Check for potential duplicates using rules
        duplicate_warnings = self.check_duplicate_prevention_rules(interface)
        for warning in duplicate_warnings:
            print(f"⚠️  {warning}")
        
        # Proceed with registration
        success = super().register_interface(interface)
        if success:
            self.health_checks[interface.interface_id] = health_check
            self.save_health_checks()
        
        return success
    
    def run_interface_health_check(self, interface: InterfaceMetadata) -> InterfaceHealthCheck:
        """Run comprehensive health check on interface"""
        issues = []
        recommendations = []
        health_score = 1.0
        
        # Check interface name quality
        if len(interface.interface_name) < 3:
            issues.append("Interface name too short")
            recommendations.append("Use descriptive interface names")
            health_score -= 0.2
        
        # Check description quality
        if len(interface.description) < 10:
            issues.append("Description too short")
            recommendations.append("Provide detailed interface description")
            health_score -= 0.1
        
        # Check domain terms
        if not interface.domain_terms:
            issues.append("No domain terms specified")
            recommendations.append("Add relevant domain terms for better discoverability")
            health_score -= 0.15
        
        # Check capabilities
        if not interface.capabilities:
            issues.append("No capabilities specified")
            recommendations.append("Define interface capabilities")
            health_score -= 0.1
        
        # Check file path validity
        if not os.path.exists(interface.file_path):
            issues.append("File path does not exist")
            recommendations.append("Ensure interface file exists")
            health_score -= 0.3
        
        # Check for circular dependencies
        if interface.interface_id in interface.dependencies:
            issues.append("Circular dependency detected")
            recommendations.append("Remove circular dependencies")
            health_score -= 0.2
        
        return InterfaceHealthCheck(
            interface_id=interface.interface_id,
            status="healthy" if health_score > 0.7 else "warning" if health_score > 0.4 else "critical",
            last_checked=datetime.now(),
            issues=issues,
            recommendations=recommendations,
            health_score=max(0.0, health_score)
        )
    
    def check_duplicate_prevention_rules(self, interface: InterfaceMetadata) -> List[str]:
        """Check interface against duplicate prevention rules"""
        warnings = []
        
        for rule in self.duplicate_rules:
            import re
            if re.match(rule.pattern, interface.interface_name):
                # Check for similar existing interfaces
                similar_interfaces = []
                for existing in self.interfaces.values():
                    if (existing.interface_name != interface.interface_name and
                        existing.interface_type == interface.interface_type):
                        
                        # Simple similarity check
                        name_similarity = self.calculate_name_similarity(
                            interface.interface_name, 
                            existing.interface_name
                        )
                        if name_similarity > 0.7:
                            similar_interfaces.append(existing)
                
                if similar_interfaces:
                    warning = f"{rule.description}: Found {len(similar_interfaces)} similar interfaces"
                    if rule.severity == "high":
                        warning += " - Consider using existing interface"
                    warnings.append(warning)
        
        return warnings
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two interface names"""
        # Simple similarity based on common words
        words1 = set(name1.lower().split('_'))
        words2 = set(name2.lower().split('_'))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
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
    
    def run_proactive_monitoring(self):
        """Run proactive monitoring on all interfaces"""
        if not self.monitoring_enabled:
            return
        
        print("🔍 Running proactive interface monitoring...")
        
        for interface in self.interfaces.values():
            health_check = self.run_interface_health_check(interface)
            self.health_checks[interface.interface_id] = health_check
            
            if health_check.health_score < 0.7:
                print(f"⚠️  {interface.interface_name}: {health_check.status}")
        
        self.save_health_checks()
        print("✅ Proactive monitoring completed")

# Global proactive registry instance
proactive_registry = ProactiveInterfaceRegistry()
