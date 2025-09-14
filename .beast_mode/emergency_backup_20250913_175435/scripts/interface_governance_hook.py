#!/usr/bin/env python3
"""
Interface Governance Pre-commit Hook

This hook prevents interface duplication by checking the registry before
any interface creation or modification. It enforces RDI compliance at
the point of creation, not after the fact.

RDI Compliance:
- Prevents interface duplication at source
- Enforces right-to-use validation
- Provides ubiquitous language-based suggestions
- Maintains single source of truth
"""

import sys
import os
import re
import ast
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add src to path
sys.path.append('src')

from rm_ddd.core.interface_registry import (
    InterfaceRegistry, InterfaceMetadata, InterfaceType, InterfaceStatus
)


class InterfaceGovernanceHook:
    """Pre-commit hook for interface governance"""
    
    def __init__(self):
        self.registry = InterfaceRegistry()
        self.violations = []
        self.suggestions = []
    
    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze a file for interface creation/modification"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Find class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's an interface class
                    if self._is_interface_class(node, content):
                        interface_info = self._extract_interface_info(node, file_path, content)
                        
                        # Validate interface creation
                        is_valid, reason, suggestions = self.registry.validate_interface_creation(
                            interface_info['name'],
                            interface_info['type'],
                            file_path,
                            interface_info['creator']
                        )
                        
                        if not is_valid:
                            issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'interface_name': interface_info['name'],
                                'interface_type': interface_info['type'].value,
                                'reason': reason,
                                'suggestions': suggestions,
                                'severity': 'error'
                            })
                        
                        # Check for interface duplication patterns
                        duplicate_patterns = self._check_duplicate_patterns(node, content)
                        if duplicate_patterns:
                            issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'interface_name': interface_info['name'],
                                'reason': f"Potential duplication patterns: {', '.join(duplicate_patterns)}",
                                'suggestions': ['Use existing interface from registry', 'Rename to avoid conflicts'],
                                'severity': 'warning'
                            })
        
        except Exception as e:
            issues.append({
                'file': file_path,
                'line': 0,
                'reason': f"Error analyzing file: {e}",
                'severity': 'error'
            })
        
        return issues
    
    def _is_interface_class(self, node: ast.ClassDef, content: str) -> bool:
        """Check if a class is an interface class"""
        # Check for ReflectiveModule inheritance
        for base in node.bases:
            if isinstance(base, ast.Name) and 'ReflectiveModule' in base.id:
                return True
            if isinstance(base, ast.Attribute) and 'ReflectiveModule' in base.attr:
                return True
        
        # Check for interface patterns in docstring
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                docstring = node.body[0].value.value
                if any(term in docstring.lower() for term in [
                    'interface', 'api', 'service', 'model', 'module', 'abstract'
                ]):
                    return True
        
        # Check for abstract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith('get_'):
                return True
        
        return False
    
    def _extract_interface_info(self, node: ast.ClassDef, file_path: str, content: str) -> Dict[str, Any]:
        """Extract interface information from AST node"""
        # Determine interface type based on context
        interface_type = self._determine_interface_type(node, file_path, content)
        
        # Extract creator from git or file metadata
        creator = self._extract_creator(file_path)
        
        # Extract domain terms from file path and class name
        domain_terms = self._extract_domain_terms(file_path, node.name)
        
        return {
            'name': node.name,
            'type': interface_type,
            'creator': creator,
            'domain_terms': domain_terms,
            'file_path': file_path
        }
    
    def _determine_interface_type(self, node: ast.ClassDef, file_path: str, content: str) -> InterfaceType:
        """Determine interface type based on context"""
        file_path_lower = file_path.lower()
        class_name_lower = node.name.lower()
        
        if 'reflective_module' in class_name_lower or 'ReflectiveModule' in content:
            return InterfaceType.REFLECTIVE_MODULE
        elif 'service' in class_name_lower or 'service' in file_path_lower:
            return InterfaceType.DOMAIN_SERVICE
        elif 'api' in class_name_lower or 'api' in file_path_lower:
            return InterfaceType.API_INTERFACE
        elif 'model' in class_name_lower or 'model' in file_path_lower:
            return InterfaceType.DATA_MODEL
        elif 'config' in class_name_lower or 'config' in file_path_lower:
            return InterfaceType.CONFIGURATION
        elif 'notification' in class_name_lower or 'notification' in file_path_lower:
            return InterfaceType.NOTIFICATION
        elif 'storage' in class_name_lower or 'storage' in file_path_lower:
            return InterfaceType.STORAGE
        elif 'transport' in class_name_lower or 'transport' in file_path_lower:
            return InterfaceType.TRANSPORT
        elif 'auth' in class_name_lower or 'auth' in file_path_lower:
            return InterfaceType.AUTHENTICATION
        elif 'monitor' in class_name_lower or 'monitor' in file_path_lower:
            return InterfaceType.MONITORING
        elif 'log' in class_name_lower or 'log' in file_path_lower:
            return InterfaceType.LOGGING
        elif 'metric' in class_name_lower or 'metric' in file_path_lower:
            return InterfaceType.METRICS
        elif 'health' in class_name_lower or 'health' in file_path_lower:
            return InterfaceType.HEALTH_CHECK
        elif 'cache' in class_name_lower or 'cache' in file_path_lower:
            return InterfaceType.CACHE
        elif 'queue' in class_name_lower or 'queue' in file_path_lower:
            return InterfaceType.QUEUE
        elif 'workflow' in class_name_lower or 'workflow' in file_path_lower:
            return InterfaceType.WORKFLOW
        elif 'orchestrat' in class_name_lower or 'orchestrat' in file_path_lower:
            return InterfaceType.ORCHESTRATION
        else:
            return InterfaceType.REFLECTIVE_MODULE  # Default
    
    def _extract_creator(self, file_path: str) -> str:
        """Extract creator information"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '--format=%an', '-n', '1', file_path],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "unknown"
    
    def _extract_domain_terms(self, file_path: str, class_name: str) -> List[str]:
        """Extract domain terms from file path and class name"""
        terms = []
        
        # Extract from file path
        path_parts = Path(file_path).parts
        for part in path_parts:
            words = re.findall(r'[A-Z][a-z]*|[a-z]+', part)
            terms.extend([word.lower() for word in words if len(word) > 2])
        
        # Extract from class name
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', class_name)
        terms.extend([word.lower() for word in words if len(word) > 2])
        
        return list(set(terms))
    
    def _check_duplicate_patterns(self, node: ast.ClassDef, content: str) -> List[str]:
        """Check for duplicate patterns in interface"""
        patterns = []
        
        # Check for common interface patterns
        if 'get_module_info' in content and 'get_capabilities' in content:
            patterns.append('ReflectiveModule pattern')
        
        if 'check_health' in content and 'is_healthy' in content:
            patterns.append('Health monitoring pattern')
        
        if 'get_configuration' in content and 'get_metrics' in content:
            patterns.append('Configuration pattern')
        
        return patterns
    
    def run_hook(self, staged_files: List[str]) -> bool:
        """Run the interface governance hook"""
        print("🔍 Interface Governance Pre-commit Hook")
        print("=" * 40)
        
        all_issues = []
        
        for file_path in staged_files:
            if file_path.endswith('.py'):
                issues = self.analyze_file(file_path)
                all_issues.extend(issues)
        
        if all_issues:
            print("\n❌ INTERFACE GOVERNANCE VIOLATIONS DETECTED:")
            print("=" * 50)
            
            for issue in all_issues:
                print(f"\n📁 {issue['file']}:{issue['line']}")
                print(f"   Interface: {issue.get('interface_name', 'Unknown')}")
                print(f"   Type: {issue.get('interface_type', 'Unknown')}")
                print(f"   Reason: {issue['reason']}")
                
                if issue.get('suggestions'):
                    print("   Suggestions:")
                    for suggestion in issue['suggestions']:
                        print(f"     - {suggestion}")
            
            print(f"\n🚨 Total violations: {len(all_issues)}")
            print("\n💡 To fix these issues:")
            print("   1. Check the interface registry for existing interfaces")
            print("   2. Use existing interfaces instead of creating duplicates")
            print("   3. Rename interfaces to avoid conflicts")
            print("   4. Follow the ubiquitous language for interface naming")
            
            return False
        
        print("✅ No interface governance violations detected")
        return True


def main():
    """Main entry point for the hook"""
    if len(sys.argv) < 2:
        print("Usage: interface_governance_hook.py <file1> [file2] ...")
        sys.exit(1)
    
    staged_files = sys.argv[1:]
    hook = InterfaceGovernanceHook()
    
    success = hook.run_hook(staged_files)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()









