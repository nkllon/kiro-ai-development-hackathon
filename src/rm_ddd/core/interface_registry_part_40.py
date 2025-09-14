from datetime import datetime
from typing import Dict, List, Any

    def validate_interface_creation(self, interface_name: str, interface_type: InterfaceType, 
                                  file_path: str, creator: str) -> tuple[bool, str, List[str]]:
        """Validate interface creation before it happens"""
        # Check right-to-use
        allowed, existing, reason = self.get_interface_right_to_use(
            interface_name, interface_type, creator, "New interface creation"
        )
        
        if not allowed:
            suggestions = []
            if existing:
                suggestions.append(f"Use existing interface: {existing.interface_name}")
                suggestions.append(f"Modify existing interface: {existing.file_path}")
            
            # Suggest alternatives
            domain_terms = self._extract_domain_terms_from_path(file_path)
            alternatives = self.suggest_interface_name("Alternative", domain_terms, interface_type)
            suggestions.extend(alternatives)
            
            return False, reason, suggestions
        
        return True, "Interface creation allowed", []
    