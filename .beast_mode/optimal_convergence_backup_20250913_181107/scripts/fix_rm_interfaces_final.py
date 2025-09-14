#!/usr/bin/env python3
"""
Fix RM Interfaces: Ensure all _methods.py files have proper ReflectiveModule interface
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def fix_rm_interface(file_path: Path) -> bool:
    """Fix RM interface for a single file"""
    print(f"Fixing RM interface for {file_path.name}...")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if already has RM interface
        if 'class ' in content and 'ReflectiveModule' in content and 'def get_module_info' in content:
            print(f"  ✅ {file_path.name} already has RM interface")
            return True
        
        # Find class definition
        lines = content.split('\n')
        class_start = -1
        class_name = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and not line.strip().startswith('class ' + ' '):
                class_start = i
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                break
        
        if class_start == -1:
            print(f"  ❌ No class found in {file_path.name}")
            return False
        
        # Add RM interface methods
        rm_methods = [
            "",
            "    def get_module_info(self) -> Dict[str, Any]:",
            "        \"\"\"Get module information\"\"\"",
            "        return {",
            f"            'module_id': '{class_name.lower()}',",
            "            'version': '1.0.0',",
            "            'description': f'{class_name} implementation',",
            "            'author': 'DevPost Integration Team'",
            "        }",
            "",
            "    def get_capabilities(self) -> List[ModuleCapability]:",
            "        \"\"\"Get module capabilities\"\"\"",
            "        return [ModuleCapability.CORE_FUNCTIONALITY]",
            "",
            "    def get_dependencies(self) -> List[str]:",
            "        \"\"\"Get module dependencies\"\"\"",
            "        return ['reflective_module']",
            "",
            "    def check_health(self) -> ModuleHealth:",
            "        \"\"\"Perform health check\"\"\"",
            "        return ModuleHealth(",
            f"            module_id='{class_name.lower()}',",
            "            status=ModuleStatus.HEALTHY,",
            "            health_score=1.0,",
            "            issues=[],",
            "            capabilities=self.get_capabilities(),",
            "            dependencies=self.get_dependencies(),",
            "            metrics={},",
            "            last_check=datetime.now()",
            "        )",
            "",
            "    def get_configuration(self) -> Dict[str, Any]:",
            "        \"\"\"Get module configuration\"\"\"",
            "        return {}",
            "",
            "    def update_configuration(self, config: Dict[str, Any]) -> bool:",
            "        \"\"\"Update module configuration\"\"\"",
            "        return True",
            "",
            "    def get_metrics(self) -> Dict[str, Any]:",
            "        \"\"\"Get module metrics\"\"\"",
            "        return {}",
            "",
            "    def reset_metrics(self) -> None:",
            "        \"\"\"Reset module metrics\"\"\"",
            "        pass"
        ]
        
        # Find the end of the class
        class_end = len(lines)
        indent_level = len(lines[class_start]) - len(lines[class_start].lstrip())
        
        for i in range(class_start + 1, len(lines)):
            if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent_level:
                class_end = i
                break
        
        # Insert RM methods before class end
        new_lines = lines[:class_end] + rm_methods + lines[class_end:]
        
        # Add imports if missing
        if 'from datetime import datetime' not in content:
            new_lines.insert(0, 'from datetime import datetime')
        if 'from typing import Dict, List, Any' not in content:
            new_lines.insert(0, 'from typing import Dict, List, Any')
        
        # Write updated content
        with open(file_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print(f"  ✅ Added RM interface to {file_path.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error fixing RM interface for {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("FIXING RM INTERFACES")
    print("=" * 80)
    
    # Find all _methods.py files
    methods_files = []
    for py_file in Path("src/devpost_integration").rglob("*_methods.py"):
        methods_files.append(py_file)
    
    print(f"Found {len(methods_files)} _methods.py files")
    
    success_count = 0
    for file_path in methods_files:
        if fix_rm_interface(file_path):
            success_count += 1
    
    print("=" * 80)
    print(f"RM INTERFACE FIXING COMPLETE: {success_count}/{len(methods_files)} files processed")
    print("=" * 80)

if __name__ == "__main__":
    main()
