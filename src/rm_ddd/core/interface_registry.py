"""
Interface Registry - Requirements-Driven Implementation
====================================================
File: src/rm_ddd/core/interface_registry.py
Generated from requirements: Interface management and registration
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path

class InterfaceType(Enum):
    """Interface type enumeration"""
    REFLECTIVE_MODULE = "reflective_module"
    DOMAIN_SERVICE = "domain_service"
    API_INTERFACE = "api_interface"
    DATA_MODEL = "data_model"
    VALIDATION_RULE = "validation_rule"
    CONFIGURATION = "configuration"
    NOTIFICATION = "notification"
    STORAGE = "storage"
    TRANSPORT = "transport"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    MONITORING = "monitoring"
    LOGGING = "logging"
    METRICS = "metrics"
    HEALTH_CHECK = "health_check"
    CACHE = "cache"
    QUEUE = "queue"
    WORKFLOW = "workflow"
    ORCHESTRATION = "orchestration"

class InterfaceStatus(Enum):
    """Interface status enumeration"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    INTERNAL = "internal"
    PUBLIC = "public"
    PRIVATE = "private"

@dataclass
class InterfaceMetadata:
    """Interface metadata"""
    interface_id: str
    interface_name: str
    interface_type: InterfaceType
    version: str
    status: InterfaceStatus
    description: str
    domain_terms: List[str]
    capabilities: List[str]
    dependencies: List[str]
    file_path: str
    created_at: datetime
    last_modified: datetime
    created_by: str
    usage_count: int = 0
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None

@dataclass
class InterfaceSearchResult:
    """Result of interface search"""
    interface: InterfaceMetadata
    relevance_score: float
    matched_terms: List[str]
    search_context: str

class InterfaceRegistry:
    """Interface Registry - Requirements-Driven Implementation"""
    
    def __init__(self, registry_file: str = "interface_registry.json"):
        self.registry_file = registry_file
        self.interfaces: Dict[str, InterfaceMetadata] = {}
        self.domain_index: Dict[str, set] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load registry from persistent storage"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                for interface_id, interface_data in data.get('interfaces', {}).items():
                    self.interfaces[interface_id] = InterfaceMetadata(**interface_data)
                self.domain_index = data.get('domain_index', {})
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")
    
    def save_registry(self):
        """Save registry to persistent storage"""
        try:
            data = {
                'interfaces': {
                    interface_id: {
                        'interface_id': interface.interface_id,
                        'interface_name': interface.interface_name,
                        'interface_type': interface.interface_type.value,
                        'version': interface.version,
                        'status': interface.status.value,
                        'description': interface.description,
                        'domain_terms': interface.domain_terms,
                        'capabilities': interface.capabilities,
                        'dependencies': interface.dependencies,
                        'file_path': interface.file_path,
                        'created_at': interface.created_at.isoformat(),
                        'last_modified': interface.last_modified.isoformat(),
                        'created_by': interface.created_by,
                        'usage_count': interface.usage_count,
                        'tags': interface.tags,
                        'examples': interface.examples,
                        'documentation_url': interface.documentation_url
                    }
                    for interface_id, interface in self.interfaces.items()
                },
                'domain_index': self.domain_index
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    
    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Register a new interface"""
        try:
            # Check for duplicates
            existing = self.find_interface_by_name_and_type(interface.interface_name, interface.interface_type)
            if existing and existing.status != InterfaceStatus.DEPRECATED:
                print(f"❌ DUPLICATE INTERFACE DETECTED!")
                print(f"   New: {interface.interface_name} ({interface.interface_type.value})")
                print(f"   Existing: {existing.interface_name} ({existing.interface_type.value})")
                print(f"   File: {existing.file_path}")
                return False
            
            # Register the interface
            self.interfaces[interface.interface_id] = interface
            
            # Update domain index
            for term in interface.domain_terms:
                if term not in self.domain_index:
                    self.domain_index[term] = set()
                self.domain_index[term].add(interface.interface_id)
            
            # Save registry
            self.save_registry()
            print(f"✅ Interface registered: {interface.interface_name}")
            return True
            
        except Exception as e:
            print(f"Error registering interface: {e}")
            return False
    
    def find_interface_by_name_and_type(self, name: str, interface_type: InterfaceType) -> Optional[InterfaceMetadata]:
        """Find interface by name and type"""
        for interface in self.interfaces.values():
            if (interface.interface_name == name and 
                interface.interface_type == interface_type and 
                interface.status != InterfaceStatus.DEPRECATED):
                return interface
        return None
    
    def search_by_ubiquitous_language(self, terms: List[str], context: str = "") -> List[InterfaceSearchResult]:
        """Search interfaces using ubiquitous language terms"""
        results = []
        for interface in self.interfaces.values():
            if interface.status == InterfaceStatus.DEPRECATED:
                continue
            
            matched_terms = []
            relevance_score = 0.0
            
            # Check domain terms
            for term in terms:
                term_lower = term.lower()
                for domain_term in interface.domain_terms:
                    if term_lower in domain_term.lower() or domain_term.lower() in term_lower:
                        matched_terms.append(term)
                        relevance_score += 1.0
            
            # Check interface name
            for term in terms:
                if term.lower() in interface.interface_name.lower():
                    matched_terms.append(term)
                    relevance_score += 0.8
            
            # Check description
            for term in terms:
                if term.lower() in interface.description.lower():
                    matched_terms.append(term)
                    relevance_score += 0.6
            
            # Check capabilities
            for term in terms:
                for capability in interface.capabilities:
                    if term.lower() in capability.lower():
                        matched_terms.append(term)
                        relevance_score += 0.4
            
            if matched_terms:
                results.append(InterfaceSearchResult(
                    interface=interface,
                    relevance_score=relevance_score,
                    matched_terms=list(set(matched_terms)),
                    search_context=context
                ))
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    def get_interface_right_to_use(self, interface_name: str, interface_type: InterfaceType, 
                                 creator: str, purpose: str) -> tuple[bool, Optional[InterfaceMetadata], str]:
        """Check right-to-use before creating an interface"""
        existing = self.find_interface_by_name_and_type(interface_name, interface_type)
        if existing:
            # Check if creator is the same
            if existing.created_by != creator:
                return False, existing, f"Interface '{interface_name}' already exists and is owned by {existing.created_by}"
            
            # Check if interface is deprecated
            if existing.status == InterfaceStatus.DEPRECATED:
                return True, existing, f"Interface '{interface_name}' is deprecated and can be replaced"
            
            # Check if purpose is different
            if purpose.lower() not in existing.description.lower():
                return False, existing, f"Interface '{interface_name}' already serves this purpose"
            
            return False, existing, f"Interface '{interface_name}' already exists with similar functionality"
        
        return True, None, "Interface creation allowed"
    
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
    
    def get_interface_governance_report(self) -> Dict[str, Any]:
        """Generate interface governance report"""
        total_interfaces = len(self.interfaces)
        active_interfaces = len([i for i in self.interfaces.values() if i.status == InterfaceStatus.ACTIVE])
        deprecated_interfaces = len([i for i in self.interfaces.values() if i.status == InterfaceStatus.DEPRECATED])
        
        # Count by type
        type_counts = {}
        for interface in self.interfaces.values():
            type_name = interface.interface_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Count by domain
        domain_counts = {}
        for interface in self.interfaces.values():
            for term in interface.domain_terms:
                domain_counts[term] = domain_counts.get(term, 0) + 1
        
        return {
            'total_interfaces': total_interfaces,
            'active_interfaces': active_interfaces,
            'deprecated_interfaces': deprecated_interfaces,
            'type_distribution': type_counts,
            'domain_distribution': domain_counts,
            'most_used_terms': sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
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
    
    def _extract_domain_terms_from_path(self, file_path: str) -> List[str]:
        """Extract domain terms from file path"""
        import re
        path_parts = Path(file_path).parts
        domain_terms = []
        
        for part in path_parts:
            # Split camelCase and snake_case
            words = re.findall(r'[A-Z][a-z]*|[a-z]+', part)
            domain_terms.extend([word.lower() for word in words])
        
        return list(set(domain_terms))  # Remove duplicates

# Global registry instance
registry = InterfaceRegistry()
