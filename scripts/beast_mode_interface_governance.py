#!/usr/bin/env python3
"""
Beast Mode Interface Governance - Pre-commit hook for interface validation
=======================================================================

This script validates Beast Mode interfaces and prevents duplication issues.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Pre-commit validation for Beast Mode interfaces
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass

@dataclass
class InterfaceViolation:
    """Interface violation detected."""
    file_path: str
    line_number: int
    violation_type: str
    description: str
    suggestion: str

class BeastModeInterfaceGovernance:
    """Validates Beast Mode interfaces and prevents violations."""
    
    def __init__(self):
        self.violations = []
        self.interface_patterns = {
            'ReflectiveModule': r'class\s+\w+.*ReflectiveModule',
            'ToolHealthManager': r'class\s+\w*[Tt]ool.*[Hh]ealth.*[Mm]anager',
            'DocumentationManager': r'class\s+\w*[Dd]ocument.*[Mm]anager',
            'ValidationEngine': r'class\s+\w*[Vv]alidation.*[Ee]ngine'
        }
    
    def validate_file(self, file_path: Path) -> List[InterfaceViolation]:
        """Validate a single file for interface violations."""
        violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                violations.append(InterfaceViolation(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    violation_type="syntax_error",
                    description=f"Syntax error: {e.msg}",
                    suggestion="Fix syntax errors before validation"
                ))
                return violations
            
            # Check for interface patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for ReflectiveModule implementation
                    if any(base.id == 'ReflectiveModule' for base in node.bases if hasattr(base, 'id')):
                        # Validate ReflectiveModule implementation
                        violations.extend(self._validate_reflective_module(file_path, node, lines))
                    
                    # Check for other interface patterns
                    violations.extend(self._validate_interface_patterns(file_path, node, lines))
            
            return violations
            
        except Exception as e:
            violations.append(InterfaceViolation(
                file_path=str(file_path),
                line_number=0,
                violation_type="validation_error",
                description=f"Validation failed: {str(e)}",
                suggestion="Check file accessibility and format"
            ))
            return violations
    
    def _validate_reflective_module(self, file_path: Path, class_node: ast.ClassDef, lines: List[str]) -> List[InterfaceViolation]:
        """Validate ReflectiveModule implementation."""
        violations = []
        
        # Check for required methods
        required_methods = ['__init__', 'perform_core_operation', 'check_health', 
                          'get_capabilities', 'get_dependencies', 'get_module_info']
        
        class_methods = [child.name for child in class_node.body if isinstance(child, ast.FunctionDef)]
        
        for method in required_methods:
            if method not in class_methods:
                violations.append(InterfaceViolation(
                    file_path=str(file_path),
                    line_number=class_node.lineno,
                    violation_type="missing_method",
                    description=f"ReflectiveModule class '{class_node.name}' missing required method '{method}'",
                    suggestion=f"Implement '{method}' method in ReflectiveModule"
                ))
        
        # Check for proper inheritance
        has_proper_inheritance = any(
            hasattr(base, 'id') and base.id == 'ReflectiveModule' 
            for base in class_node.bases
        )
        
        if not has_proper_inheritance:
            violations.append(InterfaceViolation(
                file_path=str(file_path),
                line_number=class_node.lineno,
                violation_type="inheritance_error",
                description=f"Class '{class_node.name}' should inherit from ReflectiveModule",
                suggestion="Add ReflectiveModule to class inheritance"
            ))
        
        return violations
    
    def _validate_interface_patterns(self, file_path: Path, class_node: ast.ClassDef, lines: List[str]) -> List[InterfaceViolation]:
        """Validate interface patterns."""
        violations = []
        
        # Check for duplicate interface implementations
        class_name = class_node.name
        
        # Check for naming conventions
        if 'Manager' in class_name and not any(base.id == 'ReflectiveModule' for base in class_node.bases if hasattr(base, 'id')):
            violations.append(InterfaceViolation(
                file_path=str(file_path),
                line_number=class_node.lineno,
                violation_type="naming_convention",
                description=f"Manager class '{class_name}' should inherit from ReflectiveModule",
                suggestion="Add ReflectiveModule inheritance to Manager classes"
            ))
        
        return violations
    
    def validate_files(self, file_paths: List[str]) -> bool:
        """Validate multiple files for interface violations."""
        all_valid = True
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            if not file_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue
            
            if not file_path.suffix == '.py':
                continue
            
            violations = self.validate_file(file_path)
            
            if violations:
                all_valid = False
                print(f"❌ {file_path}:")
                for violation in violations:
                    print(f"  • Line {violation.line_number}: {violation.description}")
                    print(f"    Suggestion: {violation.suggestion}")
            else:
                print(f"✅ {file_path}: No interface violations")
        
        return all_valid

def main():
    """Main function for pre-commit hook."""
    if len(sys.argv) < 2:
        print("Usage: python3 beast_mode_interface_governance.py <file1> [file2] ...")
        sys.exit(1)
    
    governance = BeastModeInterfaceGovernance()
    file_paths = sys.argv[1:]
    
    is_valid = governance.validate_files(file_paths)
    
    if not is_valid:
        print("\n🚨 Beast Mode interface governance validation failed!")
        print("Please fix interface violations before committing.")
        sys.exit(1)
    else:
        print("\n✅ All files passed Beast Mode interface governance validation!")

if __name__ == "__main__":
    main()
