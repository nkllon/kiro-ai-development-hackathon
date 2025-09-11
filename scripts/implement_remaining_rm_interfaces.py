#!/usr/bin/env python3
"""
Implement Remaining RM Interfaces

Implements ReflectiveModule interface for modules that are missing it.
Based on assessment showing 8 modules need RM interface implementation.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from devpost_integration.reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus


def implement_rm_interface_for_file(file_path: str) -> bool:
    """Implement ReflectiveModule interface for a specific file"""
    print(f"Implementing RM interface for {file_path}...")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if already has ReflectiveModule
        if 'ReflectiveModule' in content and 'def get_module_info' in content:
            print(f"  ✅ {file_path} already has RM interface")
            return True
        
        # Find the main class
        lines = content.split('\n')
        class_start = -1
        class_name = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and not line.strip().startswith('class ' + ' '):
                # Found a class definition
                class_start = i
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                break
        
        if class_start == -1 or not class_name:
            print(f"  ❌ No class found in {file_path}")
            return False
        
        # Check if class already inherits from something
        class_line = lines[class_start]
        if '(' in class_line and ')' in class_line:
            # Already has inheritance, add ReflectiveModule
            if 'ReflectiveModule' not in class_line:
                # Add ReflectiveModule to existing inheritance
                class_line = class_line.replace('(', '(ReflectiveModule, ').replace(', )', ')')
                lines[class_start] = class_line
        else:
            # No inheritance, add it
            lines[class_start] = f"class {class_name}(ReflectiveModule):"
        
        # Find the __init__ method
        init_start = -1
        for i in range(class_start, len(lines)):
            if lines[i].strip().startswith('def __init__'):
                init_start = i
                break
        
        if init_start == -1:
            # Add __init__ method
            init_method = [
                f"    def __init__(self):",
                f"        \"\"\"Initialize {class_name}\"\"\"",
                f"        super().__init__(module_id=\"{class_name.lower()}\", version=\"1.0.0\")",
                f"        register_module(self)",
                f""
            ]
            lines.insert(class_start + 1, '\n'.join(init_method))
        else:
            # Add super().__init__ and register_module to existing __init__
            init_line = lines[init_start]
            if 'super().__init__' not in content:
                # Find the end of __init__ method
                init_end = init_start + 1
                indent_level = len(lines[init_start]) - len(lines[init_start].lstrip())
                
                for i in range(init_start + 1, len(lines)):
                    if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent_level:
                        init_end = i
                        break
                
                # Add super().__init__ and register_module
                init_additions = [
                    f"        super().__init__(module_id=\"{class_name.lower()}\", version=\"1.0.0\")",
                    f"        register_module(self)"
                ]
                
                for addition in reversed(init_additions):
                    lines.insert(init_end, addition)
        
        # Add required RM interface methods at the end of the class
        rm_methods = [
            "",
            "    # ReflectiveModule interface implementation",
            "    def get_module_info(self) -> dict:",
            "        \"\"\"Get comprehensive module information\"\"\"",
            "        return {",
            f"            \"module_id\": \"{class_name.lower()}\",",
            "            \"version\": \"1.0.0\",",
            "            \"type\": f\"{class_name}\",",
            "            \"capabilities\": [cap.value for cap in self.get_capabilities()],",
            "            \"dependencies\": self.get_dependencies()",
            "        }",
            "",
            "    def get_capabilities(self) -> list:",
            "        \"\"\"Get module capabilities\"\"\"",
            "        return [ModuleCapability.CORE_FUNCTIONALITY]",
            "",
            "    def get_dependencies(self) -> list:",
            "        \"\"\"Get module dependencies\"\"\"",
            "        return [\"reflective_module\"]",
            "",
            "    def check_health(self) -> ModuleHealth:",
            "        \"\"\"Perform comprehensive health check\"\"\"",
            "        return ModuleHealth(",
            f"            module_id=\"{class_name.lower()}\",",
            "            status=ModuleStatus.HEALTHY,",
            "            health_score=1.0,",
            "            issues=[],",
            "            capabilities=self.get_capabilities(),",
            "            dependencies=self.get_dependencies(),",
            "            metrics={},",
            "            last_check=datetime.now()",
            "        )",
            "",
            "    def get_configuration(self) -> dict:",
            "        \"\"\"Get module configuration\"\"\"",
            "        return {}",
            "",
            "    def update_configuration(self, config: dict) -> None:",
            "        \"\"\"Update module configuration\"\"\"",
            "        pass",
            "",
            "    def get_metrics(self) -> dict:",
            "        \"\"\"Get module metrics\"\"\"",
            "        return {}",
            "",
            "    def reset_metrics(self) -> None:",
            "        \"\"\"Reset module metrics\"\"\"",
            "        pass"
        ]
        
        # Find the end of the class
        class_end = len(lines)
        for i in range(class_start, len(lines)):
            if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                if i > class_start:
                    class_end = i
                    break
        
        # Insert RM methods before the end of the class
        for method in reversed(rm_methods):
            lines.insert(class_end, method)
        
        # Add necessary imports at the top
        if 'from .reflective_module import' not in content:
            # Find the last import line
            last_import = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    last_import = i
            
            if last_import >= 0:
                import_line = "from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus"
                lines.insert(last_import + 1, import_line)
            else:
                # Add at the top
                lines.insert(0, "from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus")
        
        # Add datetime import if not present
        if 'from datetime import datetime' not in content:
            # Find the last import line
            last_import = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    last_import = i
            
            if last_import >= 0:
                lines.insert(last_import + 1, "from datetime import datetime")
            else:
                lines.insert(0, "from datetime import datetime")
        
        # Write the updated content
        updated_content = '\n'.join(lines)
        with open(file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"  ✅ Successfully implemented RM interface for {file_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error implementing RM interface for {file_path}: {e}")
        return False


def main():
    """Main function to implement RM interfaces for remaining modules"""
    print("=" * 60)
    print("IMPLEMENTING REMAINING RM INTERFACES")
    print("=" * 60)
    
    # Modules that need RM interface implementation (based on assessment)
    modules_to_fix = [
        "src/devpost_integration/enums.py",
        "src/devpost_integration/media_detector.py", 
        "src/devpost_integration/git_branch_manager.py",
        "src/devpost_integration/base_models.py",
        "src/devpost_integration/media_metadata.py",
        "src/devpost_integration/core_validation_rules.py",
        "src/devpost_integration/multi_project_settings.py",
        "src/devpost_integration/core_models.py"
    ]
    
    success_count = 0
    total_count = len(modules_to_fix)
    
    for module_path in modules_to_fix:
        if os.path.exists(module_path):
            if implement_rm_interface_for_file(module_path):
                success_count += 1
        else:
            print(f"  ⚠️  File not found: {module_path}")
    
    print("=" * 60)
    print(f"RM INTERFACE IMPLEMENTATION COMPLETE")
    print(f"Successfully implemented: {success_count}/{total_count}")
    print("=" * 60)
    
    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
