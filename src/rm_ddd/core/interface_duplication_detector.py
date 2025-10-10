#!/usr/bin/env python3
"""
Interface Duplication Detector
==============================

Detects duplicate interface definitions across the codebase to prevent
interface proliferation and ensure consistent interface governance.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Interface duplication detection and prevention
"""

from typing import Dict, Any, List, Tuple, Set
from datetime import datetime
from pathlib import Path
import ast
import re
from dataclasses import dataclass

try:
    from .interface_registry import InterfaceRegistry, InterfaceDefinition
except ImportError:
    # For standalone execution
    from interface_registry import InterfaceRegistry, InterfaceDefinition


@dataclass
class DuplicationResult:
    """Result of duplication detection."""
    duplicates_found: bool
    duplicate_pairs: List[Tuple[str, str]]
    similarity_scores: Dict[str, float]
    recommendations: List[str]


class InterfaceDuplicationDetector:
    """Detects and prevents interface duplication."""

    def __init__(self):
        self.module_id = "interface_duplication_detector"
        self.timestamp = datetime.now()
        self.registry = InterfaceRegistry()

    def scan_codebase(self, root_path: str = "src") -> DuplicationResult:
        """Scan codebase for interface duplications."""
        interfaces = self._extract_interfaces_from_codebase(root_path)
        duplicates = self._detect_duplicates(interfaces)
        
        return DuplicationResult(
            duplicates_found=len(duplicates) > 0,
            duplicate_pairs=duplicates,
            similarity_scores=self._calculate_similarity_scores(interfaces),
            recommendations=self._generate_recommendations(duplicates)
        )

    def check_interface_against_registry(self, interface_name: str, methods: List[str]) -> Dict[str, Any]:
        """Check if interface conflicts with registry."""
        duplicates = self.registry.check_duplicates(interface_name, methods)
        
        return {
            "interface_name": interface_name,
            "potential_duplicates": duplicates,
            "should_register": len(duplicates) == 0,
            "recommendations": self._generate_merge_recommendations(duplicates) if duplicates else []
        }

    def validate_new_interface(self, name: str, module: str, methods: List[str], description: str) -> Dict[str, Any]:
        """Validate a new interface before registration."""
        # Check for duplicates
        check_result = self.check_interface_against_registry(name, methods)
        
        # Validate naming conventions
        naming_valid = self._validate_naming_conventions(name)
        
        # Check method naming
        method_naming_valid = all(self._validate_method_naming(method) for method in methods)
        
        return {
            "valid": check_result["should_register"] and naming_valid and method_naming_valid,
            "duplicate_check": check_result,
            "naming_valid": naming_valid,
            "method_naming_valid": method_naming_valid,
            "can_register": check_result["should_register"]
        }

    def _extract_interfaces_from_codebase(self, root_path: str) -> List[InterfaceDefinition]:
        """Extract interface definitions from codebase."""
        interfaces = []
        root = Path(root_path)
        
        for py_file in root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to find class definitions
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's an interface-like class
                        if self._is_interface_class(node):
                            methods = self._extract_methods(node)
                            interface = InterfaceDefinition(
                                name=node.name,
                                module=str(py_file),
                                methods=methods,
                                description=self._extract_docstring(node),
                                version="1.0",
                                created_at=datetime.now().isoformat(),
                                updated_at=datetime.now().isoformat()
                            )
                            interfaces.append(interface)
            
            except Exception:
                # Skip files that can't be parsed
                continue
        
        return interfaces

    def _is_interface_class(self, node: ast.ClassDef) -> bool:
        """Check if class is interface-like."""
        # Simple heuristic: class name ends with Interface or has abstract methods
        if node.name.endswith('Interface'):
            return True
        
        # Check for abstract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                        return True
        
        return False

    def _extract_methods(self, node: ast.ClassDef) -> List[str]:
        """Extract method names from class."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                methods.append(item.name)
        return methods

    def _extract_docstring(self, node: ast.ClassDef) -> str:
        """Extract docstring from class."""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return ""

    def _detect_duplicates(self, interfaces: List[InterfaceDefinition]) -> List[Tuple[str, str]]:
        """Detect duplicate interfaces."""
        duplicates = []
        
        for i, iface1 in enumerate(interfaces):
            for j, iface2 in enumerate(interfaces[i+1:], i+1):
                similarity = self._calculate_interface_similarity(iface1, iface2)
                if similarity > 0.7:  # 70% similarity threshold
                    duplicates.append((iface1.name, iface2.name))
        
        return duplicates

    def _calculate_interface_similarity(self, iface1: InterfaceDefinition, iface2: InterfaceDefinition) -> float:
        """Calculate similarity between two interfaces."""
        # Method overlap
        methods1 = set(iface1.methods)
        methods2 = set(iface2.methods)
        
        if not methods1 and not methods2:
            return 0.0
        
        intersection = methods1 & methods2
        union = methods1 | methods2
        
        method_similarity = len(intersection) / len(union) if union else 0.0
        
        # Name similarity (simple check)
        name_similarity = 1.0 if iface1.name == iface2.name else 0.0
        
        # Weighted average
        return 0.8 * method_similarity + 0.2 * name_similarity

    def _calculate_similarity_scores(self, interfaces: List[InterfaceDefinition]) -> Dict[str, float]:
        """Calculate similarity scores for all interface pairs."""
        scores = {}
        
        for i, iface1 in enumerate(interfaces):
            for j, iface2 in enumerate(interfaces[i+1:], i+1):
                similarity = self._calculate_interface_similarity(iface1, iface2)
                key = f"{iface1.name}:{iface2.name}"
                scores[key] = similarity
        
        return scores

    def _generate_recommendations(self, duplicates: List[Tuple[str, str]]) -> List[str]:
        """Generate recommendations for handling duplicates."""
        recommendations = []
        
        for dup1, dup2 in duplicates:
            recommendations.append(
                f"Consider merging interfaces '{dup1}' and '{dup2}' or renaming one to clarify differences"
            )
        
        if duplicates:
            recommendations.append("Review interface definitions to ensure clear separation of concerns")
            recommendations.append("Consider using composition instead of creating similar interfaces")
        
        return recommendations

    def _generate_merge_recommendations(self, duplicates: List[str]) -> List[str]:
        """Generate recommendations for merging with existing interfaces."""
        recommendations = []
        
        for duplicate in duplicates:
            recommendations.append(
                f"Consider extending or using existing interface '{duplicate}' instead of creating new one"
            )
        
        return recommendations

    def _validate_naming_conventions(self, name: str) -> bool:
        """Validate interface naming conventions."""
        # Should be PascalCase and end with Interface
        pattern = r'^[A-Z][a-zA-Z0-9]*Interface$'
        return bool(re.match(pattern, name))

    def _validate_method_naming(self, method: str) -> bool:
        """Validate method naming conventions."""
        # Should be snake_case
        pattern = r'^[a-z][a-z0-9_]*$'
        return bool(re.match(pattern, method))

    def get_info(self) -> Dict[str, Any]:
        """Get detector information."""
        return {
            "module_id": self.module_id,
            "timestamp": self.timestamp.isoformat(),
            "registry_info": self.registry.get_info()
        }


def main():
    """Main function for command-line usage."""
    detector = InterfaceDuplicationDetector()
    result = detector.scan_codebase()
    
    print("Interface Duplication Detection Results:")
    print(f"Duplicates found: {result.duplicates_found}")
    
    if result.duplicate_pairs:
        print("\nDuplicate pairs:")
        for dup1, dup2 in result.duplicate_pairs:
            print(f"  - {dup1} <-> {dup2}")
    
    if result.recommendations:
        print("\nRecommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")


if __name__ == "__main__":
    main()
