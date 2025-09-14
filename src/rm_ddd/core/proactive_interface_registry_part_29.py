from datetime import datetime
from typing import Dict, List, Any

    def check_duplicate_prevention_rules(self, interface: InterfaceMetadata) -> List[str]:
        """Check interface against duplicate prevention rules"""
        warnings = []
        
        for rule in self.duplicate_rules:
            import re
from src.rm_ddd.core.health import ModuleHealth

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
    