from src.rm_ddd.core.registry import register_module

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
    