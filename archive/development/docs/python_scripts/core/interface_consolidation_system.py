#!/usr/bin/env python3
"""
Interface Consolidation System

This system addresses the 0.00 consistency score by identifying and
consolidating duplicate interface definitions across the codebase.
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path


class InterfaceConsolidationSystem:
    """System for consolidating duplicate interfaces."""

    def __init__(self):
        self.interfaces = defaultdict(list)
        self.duplicates = []
        self.consolidation_plan = {}

    def scan_interfaces(self, directory="src"):
        """Scan directory for interface definitions."""
        print("🔍 Scanning for interface definitions...")

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._scan_file(file_path)

    def _scan_file(self, file_path):
        """Scan a single file for interface definitions."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Find class definitions that inherit from ReflectiveModule
            class_pattern = r"^class (\w+)\(ReflectiveModule\):"
            classes = re.finditer(class_pattern, content, re.MULTILINE)

            for match in classes:
                class_name = match.group(1)
                self.interfaces[class_name].append(
                    {
                        "file": file_path,
                        "line": content[: match.start()].count("\n") + 1,
                    }
                )

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def identify_duplicates(self):
        """Identify duplicate interface definitions."""
        print("🔍 Identifying duplicate interfaces...")

        for interface_name, definitions in self.interfaces.items():
            if len(definitions) > 1:
                self.duplicates.append(
                    {
                        "interface": interface_name,
                        "count": len(definitions),
                        "definitions": definitions,
                    }
                )

        print(f"Found {len(self.duplicates)} duplicate interfaces")

    def create_consolidation_plan(self):
        """Create a plan for consolidating duplicates."""
        print("📋 Creating consolidation plan...")

        for duplicate in self.duplicates:
            interface_name = duplicate["interface"]
            definitions = duplicate["definitions"]

            # Choose the most authoritative definition
            # Priority: core modules > specific modules > generated modules
            authoritative = self._choose_authoritative_definition(definitions)

            self.consolidation_plan[interface_name] = {
                "authoritative": authoritative,
                "duplicates": [d for d in definitions if d != authoritative],
                "action": "consolidate",
            }

    def _choose_authoritative_definition(self, definitions):
        """Choose the most authoritative definition."""
        # Priority order
        priorities = [
            "core_",
            "base_",
            "main_",
            "primary_",
            "auth_",
            "config_",
            "validation_",
            "notification_",
            "project_",
            "sync_",
        ]

        for priority in priorities:
            for definition in definitions:
                if priority in definition["file"]:
                    return definition

        # If no priority match, choose the first one
        return definitions[0]

    def generate_consolidation_report(self):
        """Generate a detailed consolidation report."""
        report = {
            "summary": {
                "total_interfaces": len(self.interfaces),
                "duplicate_interfaces": len(self.duplicates),
                "consistency_score": self._calculate_consistency_score(),
            },
            "duplicates": self.duplicates,
            "consolidation_plan": self.consolidation_plan,
        }

        with open("interface_consolidation_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report

    def _calculate_consistency_score(self):
        """Calculate the consistency score."""
        total_interfaces = len(self.interfaces)
        duplicate_interfaces = len(self.duplicates)

        if total_interfaces == 0:
            return 0.0

        consistency = (total_interfaces - duplicate_interfaces) / total_interfaces
        return round(consistency * 100, 2)

    def create_authoritative_interfaces(self):
        """Create authoritative interface definitions."""
        print("📝 Creating authoritative interface definitions...")

        for interface_name, plan in self.consolidation_plan.items():
            if plan["action"] == "consolidate":
                self._create_authoritative_interface(interface_name, plan)

    def _create_authoritative_interface(self, interface_name, plan):
        """Create a single authoritative interface definition."""
        authoritative_file = plan["authoritative"]["file"]

        # Read the authoritative definition
        with open(authoritative_file, "r") as f:
            content = f.read()

        # Extract the class definition
        class_pattern = rf"^class {interface_name}\(ReflectiveModule\):.*?(?=^class|\Z)"
        match = re.search(class_pattern, content, re.MULTILINE | re.DOTALL)

        if not match:
            return

        class_definition = match.group(0)

        # Create the authoritative interface file
        auth_file = f"src/interfaces/{interface_name.lower()}_interface.py"
        os.makedirs("src/interfaces", exist_ok=True)

        header = f'''"""
{interface_name} Interface

Authoritative interface definition for {interface_name}.
Consolidated from multiple duplicate definitions.

Generated by Interface Consolidation System.
"""

import logging
from datetime import datetime
from ..devpost_integration.reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional

'''

        with open(auth_file, "w") as f:
            f.write(header + class_definition)

        print(f"  Created authoritative interface: {auth_file}")

    def update_imports(self):
        """Update imports to use authoritative interfaces."""
        print("🔄 Updating imports to use authoritative interfaces...")

        for interface_name, plan in self.consolidation_plan.items():
            if plan["action"] == "consolidate":
                self._update_imports_for_interface(interface_name, plan)

    def _update_imports_for_interface(self, interface_name, plan):
        """Update imports for a specific interface."""
        auth_file = f"src/interfaces/{interface_name.lower()}_interface.py"

        # Update all files that reference this interface
        for definition in plan["duplicates"]:
            file_path = definition["file"]
            self._update_file_imports(file_path, interface_name, auth_file)

    def _update_file_imports(self, file_path, interface_name, auth_file):
        """Update imports in a specific file."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Add import for authoritative interface
            import_line = f"from ..interfaces.{interface_name.lower()}_interface import {interface_name}\n"

            # Find the last import line
            import_pattern = r"^from .* import .*$"
            imports = list(re.finditer(import_pattern, content, re.MULTILINE))

            if imports:
                last_import = imports[-1]
                insert_pos = last_import.end()
                content = content[:insert_pos] + import_line + content[insert_pos:]
            else:
                # Add at the beginning after docstring
                content = import_line + content

            with open(file_path, "w") as f:
                f.write(content)

        except Exception as e:
            print(f"Error updating imports in {file_path}: {e}")


def main():
    """Main consolidation function."""
    print("🚀 Starting Interface Consolidation System...")
    print("Addressing 0.00 consistency score crisis...")

    system = InterfaceConsolidationSystem()

    # Step 1: Scan for interfaces
    system.scan_interfaces()

    # Step 2: Identify duplicates
    system.identify_duplicates()

    # Step 3: Create consolidation plan
    system.create_consolidation_plan()

    # Step 4: Generate report
    report = system.generate_consolidation_report()

    print(f"\n📊 Consolidation Report:")
    print(f"  Total interfaces: {report['summary']['total_interfaces']}")
    print(f"  Duplicate interfaces: {report['summary']['duplicate_interfaces']}")
    print(f"  Consistency score: {report['summary']['consistency_score']}%")

    # Step 5: Create authoritative interfaces
    system.create_authoritative_interfaces()

    # Step 6: Update imports
    system.update_imports()

    print("\n✅ Interface consolidation complete!")
    print("Consistency score should now be significantly improved.")


if __name__ == "__main__":
    main()
