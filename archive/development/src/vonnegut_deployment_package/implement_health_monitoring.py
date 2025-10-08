#!/usr/bin/env python3
"""
Implement Health Monitoring

Implements health monitoring for modules that are missing it.
Based on assessment showing 8 modules need health monitoring implementation.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from devpost_integration.reflective_module import (
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
)


def implement_health_monitoring_for_file(file_path: str) -> bool:
    """Implement health monitoring for a specific file"""
    print(f"Implementing health monitoring for {file_path}...")

    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Check if already has health monitoring
        if "def check_health(self)" in content and "ModuleHealth(" in content:
            print(f"  ✅ {file_path} already has health monitoring")
            return True

        # Find the main class
        lines = content.split("\n")
        class_start = -1
        class_name = None

        for i, line in enumerate(lines):
            if line.strip().startswith("class ") and not line.strip().startswith(
                "class " + " "
            ):
                # Found a class definition
                class_start = i
                class_name = line.split("class ")[1].split("(")[0].split(":")[0].strip()
                break

        if class_start == -1 or not class_name:
            print(f"  ❌ No class found in {file_path}")
            return False

        # Find the check_health method
        health_method_start = -1
        for i in range(class_start, len(lines)):
            if lines[i].strip().startswith("def check_health(self)"):
                health_method_start = i
                break

        if health_method_start == -1:
            print(f"  ❌ No check_health method found in {file_path}")
            return False

        # Find the end of the check_health method
        health_method_end = health_method_start + 1
        indent_level = len(lines[health_method_start]) - len(
            lines[health_method_start].lstrip()
        )

        for i in range(health_method_start + 1, len(lines)):
            if (
                lines[i].strip()
                and len(lines[i]) - len(lines[i].lstrip()) <= indent_level
            ):
                health_method_end = i
                break

        # Replace the check_health method with a comprehensive implementation
        health_implementation = [
            "    def check_health(self) -> ModuleHealth:",
            '        """Perform comprehensive health check"""',
            "        issues = []",
            "        ",
            "        # Check basic module state",
            "        if not hasattr(self, 'module_id'):",
            "            issues.append('Missing module_id attribute')",
            "        ",
            "        if not hasattr(self, 'version'):",
            "            issues.append('Missing version attribute')",
            "        ",
            "        # Check for common health indicators",
            "        try:",
            "            # Test basic functionality",
            "            if hasattr(self, 'get_module_info'):",
            "                info = self.get_module_info()",
            "                if not isinstance(info, dict):",
            "                    issues.append('get_module_info() does not return dict')",
            "            ",
            "            if hasattr(self, 'get_capabilities'):",
            "                caps = self.get_capabilities()",
            "                if not isinstance(caps, list):",
            "                    issues.append('get_capabilities() does not return list')",
            "            ",
            "            if hasattr(self, 'get_dependencies'):",
            "                deps = self.get_dependencies()",
            "                if not isinstance(deps, list):",
            "                    issues.append('get_dependencies() does not return list')",
            "        except Exception as e:",
            "            issues.append(f'Error during health check: {str(e)}')",
            "        ",
            "        # Determine health status",
            "        if not issues:",
            "            status = ModuleStatus.HEALTHY",
            "            health_score = 1.0",
            "        elif len(issues) <= 2:",
            "            status = ModuleStatus.DEGRADED",
            "            health_score = 0.7",
            "        else:",
            "            status = ModuleStatus.UNHEALTHY",
            "            health_score = 0.3",
            "        ",
            "        return ModuleHealth(",
            f'            module_id="{class_name.lower()}",',
            "            status=status,",
            "            health_score=health_score,",
            "            issues=issues,",
            "            capabilities=self.get_capabilities() if hasattr(self, 'get_capabilities') else [],",
            "            dependencies=self.get_dependencies() if hasattr(self, 'get_dependencies') else [],",
            "            metrics=self.get_metrics() if hasattr(self, 'get_metrics') else {},",
            "            last_check=datetime.now()",
            "        )",
        ]

        # Replace the existing check_health method
        lines[health_method_start:health_method_end] = health_implementation

        # Add datetime import if not present
        if "from datetime import datetime" not in content:
            # Find the last import line
            last_import = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith(
                    "from "
                ):
                    last_import = i

            if last_import >= 0:
                lines.insert(last_import + 1, "from datetime import datetime")
            else:
                lines.insert(0, "from datetime import datetime")

        # Write the updated content
        updated_content = "\n".join(lines)
        with open(file_path, "w") as f:
            f.write(updated_content)

        print(f"  ✅ Successfully implemented health monitoring for {file_path}")
        return True

    except Exception as e:
        print(f"  ❌ Error implementing health monitoring for {file_path}: {e}")
        return False


def main():
    """Main function to implement health monitoring for remaining modules"""
    print("=" * 60)
    print("IMPLEMENTING HEALTH MONITORING")
    print("=" * 60)

    # Modules that need health monitoring implementation (based on assessment)
    modules_to_fix = [
        "src/devpost_integration/validation_engine_methods.py",
        "src/devpost_integration/cli_main_methods.py",
        "src/devpost_integration/file_watcher_core_methods.py",
        "src/devpost_integration/notification_manager_methods.py",
        "src/devpost_integration/project_manager_methods.py",
        "src/devpost_integration/api_client_methods.py",
        "src/devpost_integration/preview_generator_methods.py",
        "src/devpost_integration/reflective_module.py",
    ]

    success_count = 0
    total_count = len(modules_to_fix)

    for module_path in modules_to_fix:
        if os.path.exists(module_path):
            if implement_health_monitoring_for_file(module_path):
                success_count += 1
        else:
            print(f"  ⚠️  File not found: {module_path}")

    print("=" * 60)
    print(f"HEALTH MONITORING IMPLEMENTATION COMPLETE")
    print(f"Successfully implemented: {success_count}/{total_count}")
    print("=" * 60)

    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
