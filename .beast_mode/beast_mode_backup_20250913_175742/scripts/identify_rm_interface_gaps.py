#!/usr/bin/env python3
"""
Identify RM Interface Gaps - Find modules missing ReflectiveModule interface methods
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
    logger.info("🔍 IDENTIFYING RM INTERFACE GAPS")
    logger.info("=" * 50)
    
    # Find all Python modules
    devpost_path = Path("src/devpost_integration")
    modules = list(devpost_path.glob("*.py"))
    modules = [m for m in modules if m.name != "__init__.py" and m.name != "reflective_module.py"]
    
    logger.info(f"Found {len(modules)} modules to analyze")
    
    incomplete_modules = []
    complete_modules = []
    
    for module_path in modules:
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if module has ReflectiveModule classes
            if "ReflectiveModule" not in content or "class " not in content:
                logger.info(f"  ⚠️  {module_path.name} has no ReflectiveModule classes")
                continue
            
            # Check RM interface completeness
            missing_methods = check_rm_interface_completeness(content)
            
            if missing_methods:
                incomplete_modules.append((module_path.name, missing_methods))
                logger.info(f"  ❌ {module_path.name} missing: {', '.join(missing_methods)}")
            else:
                complete_modules.append(module_path.name)
                logger.info(f"  ✅ {module_path.name} has complete RM interface")
                
        except Exception as e:
            logger.error(f"  ❌ Error analyzing {module_path.name}: {e}")
    
    # Generate report
    logger.info("")
    logger.info("🎯 RM INTERFACE GAP ANALYSIS REPORT")
    logger.info("=" * 50)
    logger.info(f"📊 Total Modules: {len(modules)}")
    logger.info(f"✅ Complete RM Interface: {len(complete_modules)}")
    logger.info(f"❌ Incomplete RM Interface: {len(incomplete_modules)}")
    logger.info(f"📈 Completion Rate: {(len(complete_modules)/len(modules)*100):.1f}%")
    
    if incomplete_modules:
        logger.info("\n🚨 MODULES NEEDING RM INTERFACE COMPLETION:")
        for module_name, missing_methods in incomplete_modules:
            logger.info(f"  - {module_name}: {', '.join(missing_methods)}")
    
    logger.info("=" * 50)
    
    return len(incomplete_modules)

def check_rm_interface_completeness(content: str) -> list:
    """Check which RM interface methods are missing"""
    required_methods = [
        'get_module_info',
        'get_capabilities', 
        'get_dependencies',
        'check_health',
        'get_configuration',
        'update_configuration',
        'get_metrics',
        'reset_metrics'
    ]
    
    missing = []
    for method in required_methods:
        if method not in content:
            missing.append(method)
    
    return missing

if __name__ == "__main__":
    sys.exit(main())
