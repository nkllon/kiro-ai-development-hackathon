#!/usr/bin/env python3
"""
🔧 PHASE 3 SOURCE REPAIR TOOL
=============================

This script systematically repairs syntax issues in source modules that are
blocking RDI test execution. It focuses on indentation errors, misplaced imports,
and class structure issues.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Phase 3A - Critical Module Repair
"""

import re
import ast
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime

class SourceRepairTool:
    """Systematically repairs syntax issues in source modules."""
    
    def __init__(self):
        self.repository_root = Path.cwd()
        self.repaired_files = []
        self.repair_log = []
        self.backup_dir = self.repository_root / ".repair_backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of the original file."""
        backup_path = self.backup_dir / f"{file_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def analyze_syntax_issues(self, file_path: Path) -> List[str]:
        """Analyze syntax issues in a file."""
        issues = []
        try:
            content = file_path.read_text()
            ast.parse(content)
            return issues  # No syntax issues
        except SyntaxError as e:
            issues.append(f"Line {e.lineno}: {e.msg}")
        except Exception as e:
            issues.append(f"Parse error: {str(e)}")
        return issues
    
    def repair_document_management_module(self, file_path: Path) -> bool:
        """Repair document management modules with specific issues."""
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            # Fix common issues in document management modules
            fixed_lines = []
            in_function = False
            function_indent = 0
            
            for i, line in enumerate(lines):
                line_num = i + 1
                
                # Fix misplaced imports inside functions
                if line.strip().startswith('from src.rm_ddd.core.health import ModuleHealth'):
                    if in_function:
                        # Move import to top of function or module
                        fixed_lines.append('        from src.rm_ddd.core.health import ModuleHealth')
                    else:
                        # Move to top of module
                        fixed_lines.append('from src.rm_ddd.core.health import ModuleHealth')
                    continue
                
                # Fix indentation issues
                if line.strip().startswith('pattern = '):
                    if in_function:
                        # Ensure proper indentation for pattern assignment
                        fixed_lines.append('    ' * (function_indent + 1) + line.strip())
                    else:
                        fixed_lines.append(line)
                    continue
                
                # Track function context
                if line.strip().startswith('def ') and 'self' in line:
                    in_function = True
                    # Extract indentation level
                    function_indent = len(line) - len(line.lstrip())
                elif line.strip() == '' or (line.strip() and not line.startswith(' ')):
                    in_function = False
                    function_indent = 0
                
                # Fix other indentation issues
                if line.strip() and line.startswith('    ') and not in_function:
                    # This line is indented but not in a function/class - fix it
                    fixed_lines.append(line.lstrip())
                else:
                    fixed_lines.append(line)
            
            # Write the repaired content
            file_path.write_text('\n'.join(fixed_lines))
            return True
            
        except Exception as e:
            self.repair_log.append(f"Error repairing {file_path}: {e}")
            return False
    
    def repair_tool_health_module(self, file_path: Path) -> bool:
        """Repair tool health modules with specific issues."""
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            # Fix common issues in tool health modules
            fixed_lines = []
            in_class = False
            class_indent = 0
            
            for i, line in enumerate(lines):
                # Track class context
                if line.strip().startswith('class '):
                    in_class = True
                    class_indent = len(line) - len(line.lstrip())
                    fixed_lines.append(line)
                    continue
                elif line.strip() == '' or (line.strip() and not line.startswith(' ')):
                    in_class = False
                    class_indent = 0
                    fixed_lines.append(line)
                    continue
                
                # Fix indentation issues in classes
                if in_class and line.strip().startswith('def '):
                    # Ensure proper method indentation
                    expected_indent = class_indent + 4
                    if not line.startswith(' ' * expected_indent):
                        fixed_lines.append(' ' * expected_indent + line.strip())
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            # Write the repaired content
            file_path.write_text('\n'.join(fixed_lines))
            return True
            
        except Exception as e:
            self.repair_log.append(f"Error repairing {file_path}: {e}")
            return False
    
    def repair_generic_module(self, file_path: Path) -> bool:
        """Generic repair for common syntax issues."""
        try:
            content = file_path.read_text()
            
            # Fix common patterns
            fixes = [
                # Fix misplaced imports
                (r'(\s+)from src\.rm_ddd\.core\.health import ModuleHealth\n', r'\1    from src.rm_ddd.core.health import ModuleHealth\n'),
                # Fix indentation issues
                (r'^(\s+)pattern = \'[^\']+\'\n', r'\1    pattern = \'^\\d+\\.\\d+\\.\\d+$\'\n'),
                # Fix function definitions outside classes
                (r'^def ([^(]+)\(self,', r'    def \1(self,'),
            ]
            
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Write the repaired content
            file_path.write_text(content)
            return True
            
        except Exception as e:
            self.repair_log.append(f"Error repairing {file_path}: {e}")
            return False
    
    def repair_critical_modules(self, module_paths: List[str]) -> Dict[str, bool]:
        """Repair critical modules that are blocking RDI test execution."""
        results = {}
        
        print(f"🔧 Repairing {len(module_paths)} critical modules...")
        
        for module_path in module_paths:
            file_path = Path(module_path.replace('.', '/') + '.py')
            
            if not file_path.exists():
                results[module_path] = False
                self.repair_log.append(f"File not found: {file_path}")
                continue
            
            # Create backup
            backup_path = self.backup_file(file_path)
            print(f"📋 Backed up {file_path} to {backup_path}")
            
            # Analyze issues
            issues = self.analyze_syntax_issues(file_path)
            if not issues:
                results[module_path] = True
                continue
            
            print(f"🔧 Repairing {file_path} (Issues: {', '.join(issues)})")
            
            # Choose repair strategy based on module type
            if 'document_management' in module_path:
                success = self.repair_document_management_module(file_path)
            elif 'tool_health' in module_path:
                success = self.repair_tool_health_module(file_path)
            else:
                success = self.repair_generic_module(file_path)
            
            # Validate repair
            if success:
                new_issues = self.analyze_syntax_issues(file_path)
                if not new_issues:
                    results[module_path] = True
                    self.repaired_files.append(file_path)
                    print(f"✅ Successfully repaired {file_path}")
                else:
                    results[module_path] = False
                    print(f"❌ Repair failed for {file_path}: {new_issues}")
            else:
                results[module_path] = False
                print(f"❌ Repair failed for {file_path}")
        
        return results
    
    def generate_repair_report(self, results: Dict[str, bool]) -> str:
        """Generate a comprehensive repair report."""
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        report = f"""
🔧 PHASE 3A SOURCE REPAIR REPORT
===============================

REPAIR SUMMARY:
- Total Modules Attempted: {total}
- Successfully Repaired: {successful}
- Failed Repairs: {total - successful}
- Success Rate: {successful/total*100:.1f}%

DETAILED RESULTS:
"""
        
        for module, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            report += f"  {status}: {module}\n"
        
        if self.repair_log:
            report += f"\nREPAIR LOG:\n"
            for log_entry in self.repair_log:
                report += f"  - {log_entry}\n"
        
        report += f"\nBACKUP LOCATION: {self.backup_dir}\n"
        report += f"REPAIRED FILES: {len(self.repaired_files)}\n"
        
        return report

def main():
    """Main repair execution."""
    repair_tool = SourceRepairTool()
    
    # Critical modules identified from RDI test analysis
    critical_modules = [
        "src.beast_mode.documentation.document_management_rm_core_core_validation",
        "src.beast_mode.documentation.document_management_rm_core_validation",
        "src.beast_mode.tool_health.makefile_health_manager_services_part_12",
        "src.beast_mode.tool_health.makefile_health_manager_services_part_13",
        "src.beast_mode.tool_health.makefile_health_manager_services_part_16",
        "src.beast_mode.tool_health.makefile_health_manager_services_part_17",
        "src.beast_mode.tool_health.makefile_health_manager_services_part_18",
        "src.beast_mode.tool_health.makefile_health_manager_services_part_19",
        "src.beast_mode.tool_health.makefile_health_manager_services_part_26",
        "src.beast_mode.tool_health.tool_health_manager_validation",
    ]
    
    print("🚀 Starting Phase 3A Critical Module Repair...")
    results = repair_tool.repair_critical_modules(critical_modules)
    
    # Generate and save report
    report = repair_tool.generate_repair_report(results)
    report_path = Path("phase3a_repair_report.md")
    report_path.write_text(report)
    
    print(f"\n📋 Repair report saved to: {report_path}")
    print(report)

if __name__ == "__main__":
    main()
