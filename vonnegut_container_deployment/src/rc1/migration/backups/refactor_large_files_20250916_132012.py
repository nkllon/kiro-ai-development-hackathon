#!/usr/bin/env python3
"""
Refactor Large Files for RDI Compliance

This script breaks down large files (>200 lines) into smaller, focused modules
following RDI compliance principles.
"""

import os
import re
from pathlib import Path


def refactor_notification_models():
    """Refactor notification_models.py into smaller modules."""
    input_file = "src/devpost_integration/notification_models.py"

    if not os.path.exists(input_file):
        print(f"File {input_file} not found")
        return

    with open(input_file, "r") as f:
        content = f.read()

    # Split into classes
    class_pattern = r"^class (\w+)\(ReflectiveModule\):"
    classes = re.finditer(class_pattern, content, re.MULTILINE)

    class_positions = []
    for match in classes:
        class_positions.append((match.start(), match.group(1)))

    # Create separate files for each class
    for i, (start_pos, class_name) in enumerate(class_positions):
        # Find the end of this class (start of next class or end of file)
        if i + 1 < len(class_positions):
            end_pos = class_positions[i + 1][0]
        else:
            end_pos = len(content)

        class_content = content[start_pos:end_pos]

        # Create the new file
        new_filename = f"src/devpost_integration/notification_{class_name.lower()}.py"

        # Add proper imports and module header
        header = '''"""
Notification {} Module

Extracted from notification_models.py for RDI compliance.
This module contains the {} class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import NotificationTiming
from typing import Dict, List, Any, Optional

'''.format(
            class_name, class_name
        )

        with open(new_filename, "w") as f:
            f.write(header + class_content)

        print(f"Created {new_filename}")


def refactor_project_models():
    """Refactor project_models.py into smaller modules."""
    input_file = "src/devpost_integration/project_models.py"

    if not os.path.exists(input_file):
        print(f"File {input_file} not found")
        return

    with open(input_file, "r") as f:
        content = f.read()

    # Split into classes
    class_pattern = r"^class (\w+)\(ReflectiveModule\):"
    classes = re.finditer(class_pattern, content, re.MULTILINE)

    class_positions = []
    for match in classes:
        class_positions.append((match.start(), match.group(1)))

    # Create separate files for each class
    for i, (start_pos, class_name) in enumerate(class_positions):
        # Find the end of this class (start of next class or end of file)
        if i + 1 < len(class_positions):
            end_pos = class_positions[i + 1][0]
        else:
            end_pos = len(content)

        class_content = content[start_pos:end_pos]

        # Create the new file
        new_filename = f"src/devpost_integration/project_{class_name.lower()}.py"

        # Add proper imports and module header
        header = '''"""
Project {} Module

Extracted from project_models.py for RDI compliance.
This module contains the {} class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import ProjectStatus, ProjectPriority
from typing import Dict, List, Any, Optional

'''.format(
            class_name, class_name
        )

        with open(new_filename, "w") as f:
            f.write(header + class_content)

        print(f"Created {new_filename}")


def refactor_sync_models():
    """Refactor sync_models.py into smaller modules."""
    input_file = "src/devpost_integration/sync_models.py"

    if not os.path.exists(input_file):
        print(f"File {input_file} not found")
        return

    with open(input_file, "r") as f:
        content = f.read()

    # Split into classes
    class_pattern = r"^class (\w+)\(ReflectiveModule\):"
    classes = re.finditer(class_pattern, content, re.MULTILINE)

    class_positions = []
    for match in classes:
        class_positions.append((match.start(), match.group(1)))

    # Create separate files for each class
    for i, (start_pos, class_name) in enumerate(class_positions):
        # Find the end of this class (start of next class or end of file)
        if i + 1 < len(class_positions):
            end_pos = class_positions[i + 1][0]
        else:
            end_pos = len(content)

        class_content = content[start_pos:end_pos]

        # Create the new file
        new_filename = f"src/devpost_integration/sync_{class_name.lower()}.py"

        # Add proper imports and module header
        header = '''"""
Sync {} Module

Extracted from sync_models.py for RDI compliance.
This module contains the {} class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import SyncStatus, SyncType
from typing import Dict, List, Any, Optional

'''.format(
            class_name, class_name
        )

        with open(new_filename, "w") as f:
            f.write(header + class_content)

        print(f"Created {new_filename}")


def refactor_core_models():
    """Refactor core_models.py into smaller modules."""
    input_file = "src/devpost_integration/core_models.py"

    if not os.path.exists(input_file):
        print(f"File {input_file} not found")
        return

    with open(input_file, "r") as f:
        content = f.read()

    # Split into classes
    class_pattern = r"^class (\w+)\(ReflectiveModule\):"
    classes = re.finditer(class_pattern, content, re.MULTILINE)

    class_positions = []
    for match in classes:
        class_positions.append((match.start(), match.group(1)))

    # Create separate files for each class
    for i, (start_pos, class_name) in enumerate(class_positions):
        # Find the end of this class (start of next class or end of file)
        if i + 1 < len(class_positions):
            end_pos = class_positions[i + 1][0]
        else:
            end_pos = len(content)

        class_content = content[start_pos:end_pos]

        # Create the new file
        new_filename = f"src/devpost_integration/core_{class_name.lower()}.py"

        # Add proper imports and module header
        header = '''"""
Core {} Module

Extracted from core_models.py for RDI compliance.
This module contains the {} class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import CoreStatus, CoreType
from typing import Dict, List, Any, Optional

'''.format(
            class_name, class_name
        )

        with open(new_filename, "w") as f:
            f.write(header + class_content)

        print(f"Created {new_filename}")


def refactor_config_models():
    """Refactor config_models.py into smaller modules."""
    input_file = "src/devpost_integration/config_models.py"

    if not os.path.exists(input_file):
        print(f"File {input_file} not found")
        return

    with open(input_file, "r") as f:
        content = f.read()

    # Split into classes
    class_pattern = r"^class (\w+)\(ReflectiveModule\):"
    classes = re.finditer(class_pattern, content, re.MULTILINE)

    class_positions = []
    for match in classes:
        class_positions.append((match.start(), match.group(1)))

    # Create separate files for each class
    for i, (start_pos, class_name) in enumerate(class_positions):
        # Find the end of this class (start of next class or end of file)
        if i + 1 < len(class_positions):
            end_pos = class_positions[i + 1][0]
        else:
            end_pos = len(content)

        class_content = content[start_pos:end_pos]

        # Create the new file
        new_filename = f"src/devpost_integration/config_{class_name.lower()}.py"

        # Add proper imports and module header
        header = '''"""
Config {} Module

Extracted from config_models.py for RDI compliance.
This module contains the {} class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import ConfigStatus, ConfigType
from typing import Dict, List, Any, Optional

'''.format(
            class_name, class_name
        )

        with open(new_filename, "w") as f:
            f.write(header + class_content)

        print(f"Created {new_filename}")


def main():
    """Main refactoring function."""
    print("🚀 Starting RDI Compliance Refactoring...")
    print("Breaking down large files into smaller, focused modules...")

    # Create backup directory
    os.makedirs("refactoring_backups", exist_ok=True)

    # Refactor each large file
    print("\n📦 Refactoring notification_models.py...")
    refactor_notification_models()

    print("\n📦 Refactoring project_models.py...")
    refactor_project_models()

    print("\n📦 Refactoring sync_models.py...")
    refactor_sync_models()

    print("\n📦 Refactoring core_models.py...")
    refactor_core_models()

    print("\n📦 Refactoring config_models.py...")
    refactor_config_models()

    print("\n✅ Refactoring complete!")
    print("Large files have been broken down into smaller, RDI-compliant modules.")


if __name__ == "__main__":
    main()
