#!/usr/bin/env python3
"""
Requirements Inheritance Registry
===============================
Multi-dimensional requirements inheritance with abdication support.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Track requirements vectors and handle immediate abdication
"""

from typing import Dict, Set, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid


class RequirementType(Enum):
    """Types of requirements that can be inherited."""
    INTERFACE = "interface"
    DATA = "data"
    VALIDATION = "validation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"


@dataclass
class Requirement:
    """A single requirement with source tracking."""
    requirement_id: str
    requirement_type: RequirementType
    description: str
    source_parent: str
    created_at: datetime
    is_active: bool = True


@dataclass
class InheritanceEvent:
    """Audit trail for inheritance and abdication events."""
    event_id: str
    event_type: str  # "inheritance", "abdication", "requirement_added"
    module_id: str
    parent_id: Optional[str]
    requirements_transferred: List[str]
    timestamp: datetime
    reason: str


class RequirementsInheritanceRegistry:
    """
    Multi-dimensional requirements inheritance registry.
    
    Tracks requirements vectors from multiple parents and handles
    immediate abdication when parents die.
    """
    
    def __init__(self):
        self.modules: Dict[str, Set[str]] = {}  # module -> parents
        self.parents: Dict[str, Set[str]] = {}  # parent -> children
        self.requirements: Dict[str, Requirement] = {}  # req_id -> requirement
        self.module_requirements: Dict[str, Set[str]] = {}  # module -> requirement_ids
        self.requirement_sources: Dict[str, str] = {}  # req_id -> source_parent
        self.audit_log: List[InheritanceEvent] = []
        self.registry_id = f"req_inheritance_{uuid.uuid4().hex[:8]}"
    
    def register_module(self, module_id: str, parent_ids: Set[str] = None) -> bool:
        """Register module with its parent requirements."""
        parent_ids = parent_ids or set()
        
        # Register module
        self.modules[module_id] = parent_ids.copy()
        self.module_requirements[module_id] = set()
        
        # Update parent relationships
        for parent_id in parent_ids:
            if parent_id not in self.parents:
                self.parents[parent_id] = set()
            self.parents[parent_id].add(module_id)
        
        # Inherit requirements from parents
        self._inherit_requirements(module_id, parent_ids)
        
        # Log inheritance event
        self._log_event("inheritance", module_id, None, list(parent_ids), 
                       f"Module {module_id} inherited from parents {parent_ids}")
        
        return True
    
    def add_requirement(self, module_id: str, requirement: Requirement) -> bool:
        """Add a new requirement to a module."""
        self.requirements[requirement.requirement_id] = requirement
        self.module_requirements[module_id].add(requirement.requirement_id)
        self.requirement_sources[requirement.requirement_id] = module_id
        
        self._log_event("requirement_added", module_id, None, [requirement.requirement_id],
                       f"Added {requirement.requirement_type.value} requirement to {module_id}")
        
        return True
    
    def abdicate_parent(self, parent_id: str, reason: str = "Parent module removed") -> bool:
        """Handle immediate abdication when parent dies."""
        if parent_id not in self.parents:
            return False
        
        children = self.parents[parent_id].copy()
        parent_requirements = self._get_parent_requirements(parent_id)
        
        # Transfer requirements to all children
        for child_id in children:
            self._transfer_requirements_to_child(child_id, parent_requirements)
        
        # Log abdication event
        self._log_event("abdication", parent_id, None, list(parent_requirements.keys()),
                       f"Parent {parent_id} abdicated to children {children}. Reason: {reason}")
        
        # Remove parent
        del self.parents[parent_id]
        for child_id in children:
            self.modules[child_id].discard(parent_id)
        
        return True
    
    def _inherit_requirements(self, module_id: str, parent_ids: Set[str]):
        """Inherit all requirements from parents."""
        for parent_id in parent_ids:
            parent_reqs = self._get_parent_requirements(parent_id)
            for req_id in parent_reqs:
                self.module_requirements[module_id].add(req_id)
    
    def _get_parent_requirements(self, parent_id: str) -> Dict[str, Requirement]:
        """Get all requirements from a parent."""
        parent_reqs = {}
        for req_id, req in self.requirements.items():
            if req.source_parent == parent_id and req.is_active:
                parent_reqs[req_id] = req
        return parent_reqs
    
    def _transfer_requirements_to_child(self, child_id: str, requirements: Dict[str, Requirement]):
        """Transfer requirements to child during abdication."""
        for req_id in requirements:
            self.module_requirements[child_id].add(req_id)
    
    def _log_event(self, event_type: str, module_id: str, parent_id: Optional[str], 
                   requirements: List[str], reason: str):
        """Log inheritance/abdication event."""
        event = InheritanceEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            module_id=module_id,
            parent_id=parent_id,
            requirements_transferred=requirements,
            timestamp=datetime.now(),
            reason=reason
        )
        self.audit_log.append(event)
    
    def get_module_requirements(self, module_id: str) -> List[Requirement]:
        """Get all requirements for a module (inherited + own)."""
        req_ids = self.module_requirements.get(module_id, set())
        return [self.requirements[req_id] for req_id in req_ids if req_id in self.requirements]
    
    def get_requirements_coverage(self) -> Dict[str, Any]:
        """Check if all requirements are still covered after abdications."""
        coverage = {
            "total_requirements": len(self.requirements),
            "active_requirements": len([r for r in self.requirements.values() if r.is_active]),
            "modules_with_requirements": len(self.module_requirements),
            "orphaned_requirements": [],
            "coverage_status": "complete"
        }
        
        # Check for orphaned requirements
        for req_id, req in self.requirements.items():
            if req.is_active and req.source_parent not in self.parents:
                coverage["orphaned_requirements"].append(req_id)
        
        if coverage["orphaned_requirements"]:
            coverage["coverage_status"] = "incomplete"
        
        return coverage
    
    def get_audit_trail(self) -> List[InheritanceEvent]:
        """Get complete audit trail."""
        return self.audit_log.copy()
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "registry_id": self.registry_id,
            "total_modules": len(self.modules),
            "total_parents": len(self.parents),
            "total_requirements": len(self.requirements),
            "total_events": len(self.audit_log),
            "coverage": self.get_requirements_coverage()
        }


# Global registry instance
requirements_registry = RequirementsInheritanceRegistry()


def register_module_with_requirements(module_id: str, parent_ids: Set[str] = None) -> bool:
    """Register module with requirements inheritance."""
    return requirements_registry.register_module(module_id, parent_ids)


def add_requirement_to_module(module_id: str, requirement: Requirement) -> bool:
    """Add requirement to module."""
    return requirements_registry.add_requirement(module_id, requirement)


def abdicate_parent_requirements(parent_id: str, reason: str = "Parent removed") -> bool:
    """Handle parent abdication."""
    return requirements_registry.abdicate_parent(parent_id, reason)


def get_module_requirements(module_id: str) -> List[Requirement]:
    """Get all requirements for a module."""
    return requirements_registry.get_module_requirements(module_id)


def get_requirements_coverage() -> Dict[str, Any]:
    """Check requirements coverage."""
    return requirements_registry.get_requirements_coverage()


def get_audit_trail() -> List[InheritanceEvent]:
    """Get audit trail."""
    return requirements_registry.get_audit_trail()
