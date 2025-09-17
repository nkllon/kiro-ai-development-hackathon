from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def suggest_interface_name(self, purpose: str, domain_terms: List[str], 
                             interface_type: InterfaceType) -> List[str]:
        """Suggest interface names based on purpose and domain terms"""
        suggestions = []
        
        # Generate suggestions based on domain terms
        for term in domain_terms:
            if interface_type == InterfaceType.REFLECTIVE_MODULE:
                suggestions.append(f"{term}_module")
                suggestions.append(f"{term}_reflective_module")
            elif interface_type == InterfaceType.DOMAIN_SERVICE:
                suggestions.append(f"{term}_service")
                suggestions.append(f"{term}_domain_service")
            elif interface_type == InterfaceType.API_INTERFACE:
                suggestions.append(f"{term}_api")
                suggestions.append(f"{term}_interface")
            elif interface_type == InterfaceType.DATA_MODEL:
                suggestions.append(f"{term}_model")
                suggestions.append(f"{term}_data_model")
        
        # Check for existing names and add version suffixes if needed
        existing_names = [interface.interface_name for interface in self.interfaces.values()]
        unique_suggestions = []
        
        for suggestion in suggestions:
            if suggestion not in existing_names:
                unique_suggestions.append(suggestion)
            else:
                # Add version suffix
                for i in range(2, 10):
                    versioned = f"{suggestion}_v{i}"
                    if versioned not in existing_names:
                        unique_suggestions.append(versioned)
                        break
        
        return unique_suggestions[:5]  # Return top 5 suggestions

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    