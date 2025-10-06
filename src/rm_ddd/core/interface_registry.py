#!/usr/bin/env python3
"""
Interface Registry
==================

Central registry for all system interfaces to prevent duplication and ensure
consistent interface definitions across the Beast Mode Framework.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Interface governance and duplication prevention
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class InterfaceDefinition:
    """Definition of a system interface."""
    name: str
    module: str
    methods: List[str]
    description: str
    version: str
    created_at: str
    updated_at: str


class InterfaceRegistry:
    """Central registry for system interfaces with duplication detection."""

    def __init__(self):
        self.module_id = "interface_registry"
        self.timestamp = datetime.now()
        self._interfaces: Dict[str, InterfaceDefinition] = {}
        self._load_existing_interfaces()

    def register_interface(self, interface_def: InterfaceDefinition) -> bool:
        """Register a new interface or update existing one."""
        if interface_def.name in self._interfaces:
            # Update existing interface
            existing = self._interfaces[interface_def.name]
            existing.methods = interface_def.methods
            existing.description = interface_def.description
            existing.version = interface_def.version
            existing.updated_at = datetime.now().isoformat()
            return False  # Not new
        else:
            # Register new interface
            self._interfaces[interface_def.name] = interface_def
            return True  # New interface

    def get_interface(self, name: str) -> Optional[InterfaceDefinition]:
        """Get interface definition by name."""
        return self._interfaces.get(name)

    def list_interfaces(self) -> List[InterfaceDefinition]:
        """List all registered interfaces."""
        return list(self._interfaces.values())

    def check_duplicates(self, interface_name: str, methods: List[str]) -> List[str]:
        """Check for potential duplicate interfaces."""
        duplicates = []
        
        for name, interface in self._interfaces.items():
            if name == interface_name:
                continue
                
            # Check method overlap
            method_overlap = set(methods) & set(interface.methods)
            if len(method_overlap) > len(methods) * 0.5:  # 50% overlap threshold
                duplicates.append(name)
        
        return duplicates

    def validate_interface_compliance(self, module_path: str) -> Dict[str, Any]:
        """Validate interface compliance for a module."""
        # This would analyze the module and check compliance
        # For now, return basic validation
        return {
            "module": module_path,
            "compliant": True,
            "issues": [],
            "recommendations": []
        }

    def get_info(self) -> Dict[str, Any]:
        """Get registry information."""
        return {
            "module_id": self.module_id,
            "timestamp": self.timestamp.isoformat(),
            "interface_count": len(self._interfaces),
            "interfaces": [iface.name for iface in self._interfaces.values()]
        }

    def _load_existing_interfaces(self) -> None:
        """Load existing interfaces from registry file."""
        registry_file = Path("interface_registry.json")
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    for iface_data in data.get("interfaces", []):
                        interface = InterfaceDefinition(**iface_data)
                        self._interfaces[interface.name] = interface
            except Exception:
                # If loading fails, start with empty registry
                pass

    def save_registry(self) -> None:
        """Save registry to file."""
        registry_file = Path("interface_registry.json")
        data = {
            "timestamp": datetime.now().isoformat(),
            "interfaces": [
                {
                    "name": iface.name,
                    "module": iface.module,
                    "methods": iface.methods,
                    "description": iface.description,
                    "version": iface.version,
                    "created_at": iface.created_at,
                    "updated_at": iface.updated_at
                }
                for iface in self._interfaces.values()
            ]
        }
        
        with open(registry_file, 'w') as f:
            json.dump(data, f, indent=2)
