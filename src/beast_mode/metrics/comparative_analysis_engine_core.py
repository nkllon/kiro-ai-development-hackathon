"""
Interface Registry - Requirements-Driven Implementation
====================================================
Generated from requirements: Manage interface metadata with proper typing, Provide registration methods for interfaces, Support interface discovery and validation, Maintain interface compliance tracking
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class InterfaceType(Enum):
    """Interface type enumeration"""
    REFLECTIVE_MODULE = "reflective_module"
    DOMAIN_SERVICE = "domain_service"
    INFRASTRUCTURE = "infrastructure"
    APPLICATION_SERVICE = "application_service"

class InterfaceStatus(Enum):
    """Interface status enumeration"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"

@dataclass
class InterfaceMetadata:
    """Interface metadata"""
    name: str
    type: InterfaceType
    status: InterfaceStatus
    file_path: str
    line_number: int
    methods: List[str]
    created_at: datetime
    compliance_score: float

class InterfaceRegistry:
    """Interface Registry - Requirements-Driven Implementation"""
    
    def __init__(self):
        self.interfaces: Dict[str, InterfaceMetadata] = {}
        self.registry_file = ".beast_mode/interface_registry.json"
    
    def register(self, name: str, interface_type: InterfaceType, 
                file_path: str, line_number: int, methods: List[str]) -> bool:
        """Register an interface"""
        try:
            metadata = InterfaceMetadata(
                name=name,
                type=interface_type,
                status=InterfaceStatus.ACTIVE,
                file_path=file_path,
                line_number=line_number,
                methods=methods,
                created_at=datetime.now(),
                compliance_score=0.0
            )
            self.interfaces[name] = metadata
            self.save_registry()
            return True
        except Exception as e:
            print(f"Error registering interface {name}: {e}")
            return False
    
    def get_metadata(self, name: str) -> Optional[InterfaceMetadata]:
        """Get interface metadata"""
        return self.interfaces.get(name)
    
    def validate_interface(self, name: str) -> bool:
        """Validate interface compliance"""
        if name not in self.interfaces:
            return False
        
        metadata = self.interfaces[name]
        
        # Basic validation checks
        if not metadata.name or not metadata.file_path:
            return False
        
        if metadata.compliance_score < 0.0 or metadata.compliance_score > 100.0:
            return False
        
        return True
    
    def list_interfaces(self) -> List[str]:
        """List all registered interfaces"""
        return list(self.interfaces.keys())
    
    def save_registry(self):
        """Save registry to file"""
        try:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, 'w') as f:
                json.dump(self._serialize_registry(), f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    
    def _serialize_registry(self) -> Dict[str, Any]:
        """Serialize registry for JSON storage"""
        return {
            name: {
                'name': metadata.name,
                'type': metadata.type.value,
                'status': metadata.status.value,
                'file_path': metadata.file_path,
                'line_number': metadata.line_number,
                'methods': metadata.methods,
                'created_at': metadata.created_at.isoformat(),
                'compliance_score': metadata.compliance_score
            }
            for name, metadata in self.interfaces.items()
        }

# Global registry instance
registry = InterfaceRegistry()
