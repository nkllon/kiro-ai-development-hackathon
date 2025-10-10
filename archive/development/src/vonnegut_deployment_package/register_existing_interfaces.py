#!/usr/bin/env python3
"""
Register Existing Interfaces

This script scans the entire codebase for existing ReflectiveModule implementations
and registers them with the Beast Mode Interface Registry to prevent future duplicates.
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.append("src")

from beast_mode.interface_governance import (
    BeastModeInterfaceRegistry,
    InterfaceMetadata,
    InterfaceType,
    InterfaceStatus,
)


class InterfaceScanner:
    """Scanner for existing ReflectiveModule implementations"""

    def __init__(self, registry: BeastModeInterfaceRegistry):
        self.registry = registry
        self.scanned_files = 0
        self.registered_interfaces = 0
        self.duplicates_found = 0

    def scan_codebase(self, root_path: str = "src") -> Dict[str, Any]:
        """Scan entire codebase for ReflectiveModule implementations"""
        print(
            f"🔍 Scanning codebase at {root_path} for ReflectiveModule implementations..."
        )

        results = {
            "scanned_files": 0,
            "registered_interfaces": 0,
            "duplicates_found": 0,
            "interfaces": [],
        }

        for py_file in Path(root_path).rglob("*.py"):
            try:
                interfaces = self.scan_file(str(py_file))
                results["scanned_files"] += 1
                results["interfaces"].extend(interfaces)

                for interface in interfaces:
                    success = self.registry.register_interface(interface)
                    if success:
                        results["registered_interfaces"] += 1
                    else:
                        results["duplicates_found"] += 1

            except Exception as e:
                print(f"⚠️ Error scanning {py_file}: {e}")

        return results

    def scan_file(self, file_path: str) -> List[InterfaceMetadata]:
        """Scan a single Python file for ReflectiveModule implementations"""
        interfaces = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class inherits from ReflectiveModule
                    if self.is_reflective_module_class(node):
                        interface = self.extract_interface_metadata(
                            node, file_path, content
                        )
                        if interface:
                            interfaces.append(interface)

        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")

        return interfaces

    def is_reflective_module_class(self, class_node: ast.ClassDef) -> bool:
        """Check if a class inherits from ReflectiveModule"""
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "ReflectiveModule":
                return True
            elif isinstance(base, ast.Attribute):
                # Handle cases like src.beast_mode.core.interfaces.ReflectiveModule
                if base.attr == "ReflectiveModule":
                    return True
        return False

    def extract_interface_metadata(
        self, class_node: ast.ClassDef, file_path: str, content: str
    ) -> Optional[InterfaceMetadata]:
        """Extract interface metadata from a class definition"""
        try:
            # Get line number
            line_number = class_node.lineno

            # Extract methods
            methods = []
            for item in class_node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)

            # Extract domain terms from file path and class name
            domain_terms = self.extract_domain_terms(file_path, class_node.name)

            # Determine interface type
            interface_type = self.determine_interface_type(class_node.name, file_path)

            return InterfaceMetadata(
                interface_name=class_node.name,
                interface_type=interface_type,
                file_path=file_path,
                line_number=line_number,
                methods=methods,
                domain_terms=domain_terms,
                status=InterfaceStatus.ACTIVE,
            )

        except Exception as e:
            print(
                f"⚠️ Error extracting metadata from {class_node.name} in {file_path}: {e}"
            )
            return None

    def extract_domain_terms(self, file_path: str, class_name: str) -> List[str]:
        """Extract domain terms from file path and class name"""
        terms = set()

        # Add path components as domain terms
        path_parts = file_path.replace("src/", "").replace(".py", "").split("/")
        for part in path_parts:
            if part and part != "__init__":
                terms.add(part)

        # Add class name components
        class_parts = re.findall(r"[A-Z][a-z]*", class_name)
        for part in class_parts:
            if part.lower() not in ["module", "interface", "class"]:
                terms.add(part.lower())

        # Add common domain terms
        if "beast_mode" in file_path:
            terms.add("beast_mode")
        if "reflective" in class_name.lower():
            terms.add("reflective")
        if "interface" in class_name.lower():
            terms.add("interface")

        return list(terms)

    def determine_interface_type(
        self, class_name: str, file_path: str
    ) -> InterfaceType:
        """Determine the interface type based on class name and file path"""
        if "ReflectiveModule" in class_name:
            return InterfaceType.REFLECTIVE_MODULE
        elif "Service" in class_name:
            return InterfaceType.DOMAIN_SERVICE
        elif "API" in class_name or "Interface" in class_name:
            return InterfaceType.API_INTERFACE
        elif "Model" in class_name or "Data" in class_name:
            return InterfaceType.DATA_MODEL
        elif "Validation" in class_name or "Rule" in class_name:
            return InterfaceType.VALIDATION_RULE
        elif "Config" in class_name:
            return InterfaceType.CONFIGURATION
        else:
            return InterfaceType.REFLECTIVE_MODULE  # Default


def main():
    """Main function to register existing interfaces"""
    print("🚀 Beast Mode Interface Registration")
    print("=" * 50)

    # Initialize registry
    registry = BeastModeInterfaceRegistry()
    scanner = InterfaceScanner(registry)

    # Register the canonical ReflectiveModule interface first
    print("📝 Registering canonical ReflectiveModule interface...")
    canonical_interface = InterfaceMetadata(
        interface_name="ReflectiveModule",
        interface_type=InterfaceType.REFLECTIVE_MODULE,
        file_path="src/beast_mode/core/interfaces.py",
        line_number=9,
        methods=["get_health_status", "get_metrics", "get_module_info"],
        domain_terms=["beast_mode", "core", "reflective", "interface"],
        status=InterfaceStatus.ACTIVE,
    )

    canonical_registered = registry.register_interface(canonical_interface)
    print(f"✅ Canonical ReflectiveModule registered: {canonical_registered}")

    # Scan and register all existing interfaces
    results = scanner.scan_codebase()

    print("\n📊 Registration Results:")
    print(f"   📁 Files scanned: {results['scanned_files']}")
    print(f"   ✅ Interfaces registered: {results['registered_interfaces']}")
    print(f"   ❌ Duplicates found: {results['duplicates_found']}")
    print(f"   📋 Total interfaces found: {len(results['interfaces'])}")

    # Show registry status
    status = registry.get_registry_status()
    print(f"\n📊 Registry Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")

    print("\n🎉 Interface registration completed!")


if __name__ == "__main__":
    main()
