#!/usr/bin/env python3
"""
Registry Integration Beast Mode - Simple Implementation
Implements registry integration for all modules with ReflectiveModule interface
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main execution function"""
    logger.info("🚀 BEAST MODE: Registry Integration Implementation")
    logger.info("=" * 50)

    start_time = datetime.now()

    # Find all Python modules
    devpost_path = Path("src/devpost_integration")
    modules = list(devpost_path.glob("*.py"))
    modules = [
        m
        for m in modules
        if m.name != "__init__.py" and m.name != "reflective_module.py"
    ]

    logger.info(f"Found {len(modules)} modules to process")

    modules_enhanced = 0

    for module_path in modules:
        try:
            logger.info(f"Processing {module_path.name}...")

            with open(module_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if module has ReflectiveModule classes
            if "ReflectiveModule" not in content or "class " not in content:
                logger.info(f"  ⚠️  {module_path.name} has no ReflectiveModule classes")
                continue

            # Check if already has registry integration
            if (
                "register_module(self)" in content
                and "from .reflective_module import" in content
            ):
                logger.info(f"  ✅ {module_path.name} already has registry integration")
                continue

            # Add registry integration
            enhanced_content = content

            # Add register_module import if not present
            if "register_module" not in content:
                if "from .reflective_module import" in content:
                    enhanced_content = enhanced_content.replace(
                        "from .reflective_module import",
                        "from .reflective_module import register_module,",
                    )
                else:
                    # Add import at the top
                    lines = enhanced_content.split("\n")
                    import_line = "from .reflective_module import register_module"
                    lines.insert(0, import_line)
                    enhanced_content = "\n".join(lines)

            # Add register_module call in __init__ methods
            if (
                "def __init__" in enhanced_content
                and "register_module(self)" not in enhanced_content
            ):
                enhanced_content = enhanced_content.replace(
                    "def __init__", "def __init__"
                )

                # Find __init__ methods and add register_module call
                lines = enhanced_content.split("\n")
                new_lines = []
                i = 0

                while i < len(lines):
                    line = lines[i]
                    new_lines.append(line)

                    if "def __init__" in line and "self" in line:
                        # Find the end of the __init__ method
                        indent = len(line) - len(line.lstrip())
                        i += 1

                        # Skip docstring
                        while i < len(lines) and (
                            lines[i].strip().startswith('"""')
                            or lines[i].strip().startswith("'''")
                        ):
                            new_lines.append(lines[i])
                            i += 1
                            if lines[i - 1].strip().endswith('"""') or lines[
                                i - 1
                            ].strip().endswith("'''"):
                                break

                        # Add register_module call
                        new_lines.append(f"{' ' * (indent + 1)}register_module(self)")
                        new_lines.append("")

                    i += 1

                enhanced_content = "\n".join(new_lines)

            if enhanced_content != content:
                with open(module_path, "w", encoding="utf-8") as f:
                    f.write(enhanced_content)

                logger.info(
                    f"  ✅ Enhanced registry integration for {module_path.name}"
                )
                modules_enhanced += 1
            else:
                logger.info(f"  ⚠️  No changes needed for {module_path.name}")

        except Exception as e:
            logger.error(f"  ❌ Error processing {module_path.name}: {e}")

    # Generate report
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("")
    logger.info("🎯 BEAST MODE REGISTRY INTEGRATION COMPLETION REPORT")
    logger.info("=" * 50)
    logger.info(f"⏱️  Duration: {duration:.1f} seconds")
    logger.info(f"📊 Modules Processed: {len(modules)}")
    logger.info(f"✅ Modules Enhanced: {modules_enhanced}")
    logger.info(f"🎉 SUCCESS RATE: {(modules_enhanced/len(modules)*100):.1f}%")
    logger.info("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
