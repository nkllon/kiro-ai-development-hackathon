"""
Beast Mode Interface Registry - Working Implementation

This registry provides interface governance and duplication prevention
without depending on the broken RM-DDD dependency chain.

Implements proactive interface validation and duplication prevention
for Beast Mode development workflow.
"""

import json
import os
import ast
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from enum import Enum


class InterfaceType(Enum):
    """Types of interfaces in the registry"""
    REFLECTIVE_MODULE = "reflective_module"
    DOMAIN_SERVICE = "domain_service"
    API_INTERFACE = "api_interface"
    DATA_MODEL = "data_model"
    VALIDATION_RULE = "validation_rule"
    CONFIGURATION = "configuration"


class InterfaceStatus(Enum):
    """Status of interfaces in the registry"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    CONFLICT = "conflict"
    DUPLICATE = "duplicate"


@dataclass
class InterfaceMetadata:
    """Metadata for registered interfaces"""
    interface_name: str
    interface_type: InterfaceType
    file_path: str
    line_number: int
    methods: List[str] = field(default_factory=list)
    domain_terms: List[str] = field(default_factory=list)
    status: InterfaceStatus = InterfaceStatus.ACTIVE
    registered_at: datetime = field(default_factory=datetime.now)
    conflicts: List[str] = field(default_factory=list)


class BeastModeInterfaceRegistry:
    """
    Beast Mode Interface Registry - Working Implementation
    
    Provides interface governance and duplication prevention for Beast Mode
    development workflow without broken dependencies.
    """
    
    def __init__(self, registry_file: str = ".beast_mode/interface_registry.json"):
        self.registry_file = registry_file
        self.interfaces: Dict[str, InterfaceMetadata] = {}
        self.domain_index: Dict[str, Set[str]] = {}
        self.duplicates: List[InterfaceMetadata] = []
        self.conflicts: List[InterfaceMetadata] = []
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
        
        self.load_registry()
    
    def load_registry(self) -> None:
        """Load registry from persistent storage"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load interfaces
                    for interface_id, interface_data in data.get('interfaces', {}).items():
                        interface_data['interface_type'] = InterfaceType(interface_data['interface_type'])
                        interface_data['status'] = InterfaceStatus(interface_data['status'])
                        interface_data['registered_at'] = datetime.fromisoformat(interface_data['registered_at'])
                        self.interfaces[interface_id] = InterfaceMetadata(**interface_data)
                    
                    # Load domain index
                    self.domain_index = {
                        term: set(interface_ids) 
                        for term, interface_ids in data.get('domain_index', {}).items()
                    }
                    
                    # Load duplicates and conflicts
                    self.duplicates = [
                        InterfaceMetadata(**dup_data) for dup_data in data.get('duplicates', [])
                    ]
                    self.conflicts = [
                        InterfaceMetadata(**conf_data) for conf_data in data.get('conflicts', [])
                    ]
                    
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")
    
    def save_registry(self) -> None:
        """Save registry to persistent storage"""
        try:
            data = {
                'interfaces': {
                    interface_id: {
                        'interface_name': interface.interface_name,
                        'interface_type': interface.interface_type.value if hasattr(interface.interface_type, 'value') else str(interface.interface_type),
                        'file_path': interface.file_path,
                        'line_number': interface.line_number,
                        'methods': interface.methods,
                        'domain_terms': interface.domain_terms,
                        'status': interface.status.value if hasattr(interface.status, 'value') else str(interface.status),
                        'registered_at': interface.registered_at.isoformat(),
                        'conflicts': interface.conflicts
                    }
                    for interface_id, interface in self.interfaces.items()
                },
                'domain_index': {
                    term: list(interface_ids) 
                    for term, interface_ids in self.domain_index.items()
                },
                'duplicates': [
                    {
                        'interface_name': dup.interface_name,
                        'interface_type': dup.interface_type.value,
                        'file_path': dup.file_path,
                        'line_number': dup.line_number,
                        'methods': dup.methods,
                        'domain_terms': dup.domain_terms,
                        'status': dup.status.value,
                        'registered_at': dup.registered_at.isoformat(),
                        'conflicts': dup.conflicts
                    }
                    for dup in self.duplicates
                ],
                'conflicts': [
                    {
                        'interface_name': conf.interface_name,
                        'interface_type': conf.interface_type.value,
                        'file_path': conf.file_path,
                        'line_number': conf.line_number,
                        'methods': conf.methods,
                        'domain_terms': conf.domain_terms,
                        'status': conf.status.value,
                        'registered_at': conf.registered_at.isoformat(),
                        'conflicts': conf.conflicts
                    }
                    for conf in self.conflicts
                ]
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving registry: {e}")
    
    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """
        Register a new interface with duplication prevention
        
        Returns:
            True if registration successful, False if duplicate detected
        """
        # Check for duplicates by name and type
        existing = self.find_interface_by_name_and_type(
            interface.interface_name, 
            interface.interface_type
        )
        
        if existing:
            print(f"❌ DUPLICATE INTERFACE DETECTED!")
            print(f"   New: {interface.interface_name} ({interface.interface_type.value}) at {interface.file_path}:{interface.line_number}")
            print(f"   Existing: {existing.interface_name} ({existing.interface_type.value}) at {existing.file_path}:{existing.line_number}")
            print(f"   Resolution: Use existing interface or rename new interface")
            
            # Mark as duplicate
            interface.status = InterfaceStatus.DUPLICATE
            interface.conflicts.append(f"Duplicate of {existing.file_path}:{existing.line_number}")
            self.duplicates.append(interface)
            self.save_registry()
            return False
        
        # Register the interface
        interface_id = f"{interface.interface_name}_{interface.interface_type.value}"
        self.interfaces[interface_id] = interface
        
        # Update domain index
        for term in interface.domain_terms:
            if term not in self.domain_index:
                self.domain_index[term] = set()
            self.domain_index[term].add(interface_id)
        
        # Save registry
        self.save_registry()
        
        print(f"✅ Interface registered: {interface.interface_name}")
        return True
    
    def find_interface_by_name_and_type(self, name: str, interface_type: InterfaceType) -> Optional[InterfaceMetadata]:
        """Find interface by name and type"""
        for interface in self.interfaces.values():
            if (interface.interface_name == name and 
                interface.interface_type == interface_type and
                interface.status != InterfaceStatus.DEPRECATED):
                return interface
        return None
    
    def validate_interface_compliance(self, file_path: str, interface_name: str) -> Dict[str, Any]:
        """
        Validate interface compliance with Beast Mode standards
        
        Returns:
            Validation results with compliance status and recommendations
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find the interface class
            interface_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == interface_name:
                    interface_class = node
                    break
            
            if not interface_class:
                return {
                    'compliant': False,
                    'error': f'Interface {interface_name} not found in {file_path}',
                    'recommendations': [f'Ensure {interface_name} class exists in {file_path}']
                }
            
            # Check if it's a ReflectiveModule
            is_reflective_module = False
            for base in interface_class.bases:
                if isinstance(base, ast.Name) and base.id == 'ReflectiveModule':
                    is_reflective_module = True
                    break
            
            if not is_reflective_module:
                return {
                    'compliant': False,
                    'error': f'{interface_name} does not inherit from ReflectiveModule',
                    'recommendations': [
                        f'Change class {interface_name}(ReflectiveModule):',
                        'Implement required ReflectiveModule methods'
                    ]
                }
            
            # Check for required methods
            methods = [node.name for node in interface_class.body if isinstance(node, ast.FunctionDef)]
            required_methods = ['get_health_status', 'get_metrics']
            missing_methods = [method for method in required_methods if method not in methods]
            
            if missing_methods:
                return {
                    'compliant': False,
                    'error': f'Missing required methods: {missing_methods}',
                    'recommendations': [
                        f'Implement missing methods: {missing_methods}',
                        'Follow Beast Mode ReflectiveModule interface'
                    ]
                }
            
            return {
                'compliant': True,
                'interface_name': interface_name,
                'file_path': file_path,
                'methods': methods,
                'is_reflective_module': True,
                'recommendations': ['Interface is compliant with Beast Mode standards']
            }
            
        except Exception as e:
            return {
                'compliant': False,
                'error': f'Validation failed: {str(e)}',
                'recommendations': [f'Fix syntax errors in {file_path}']
            }
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status and statistics"""
        return {
            'total_interfaces': len(self.interfaces),
            'active_interfaces': len([i for i in self.interfaces.values() if i.status == InterfaceStatus.ACTIVE]),
            'duplicates': len(self.duplicates),
            'conflicts': len(self.conflicts),
            'domain_terms': len(self.domain_index),
            'registry_file': self.registry_file,
            'last_updated': datetime.now().isoformat()
        }
