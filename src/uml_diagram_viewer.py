#!/usr/bin/env python3
"""
Dynamic UML Diagram Viewer
Generates static structure and object interaction diagrams for any class in the repository.
"""

import ast
import inspect
import importlib
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

@dataclass
class ClassInfo:
    """Information about a class for UML generation."""
    name: str
    module: str
    file_path: str
    base_classes: List[str]
    methods: List[str]
    attributes: List[str]
    docstring: Optional[str]
    is_abstract: bool
    decorators: List[str]

@dataclass
class MethodInfo:
    """Information about a method for UML generation."""
    name: str
    parameters: List[str]
    return_type: Optional[str]
    is_abstract: bool
    is_static: bool
    is_classmethod: bool
    decorators: List[str]

@dataclass
class RelationshipInfo:
    """Information about relationships between classes."""
    source: str
    target: str
    relationship_type: str  # inheritance, composition, aggregation, dependency
    label: Optional[str] = None

class UMLDiagramType(Enum):
    """Types of UML diagrams supported."""
    STATIC_STRUCTURE = "static_structure"
    OBJECT_INTERACTION = "object_interaction"
    CLASS_DIAGRAM = "class_diagram"
    SEQUENCE_DIAGRAM = "sequence_diagram"

class DynamicUMLViewer:
    """Dynamic UML diagram viewer that can generate diagrams for any class."""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root).resolve()
        self.class_registry: Dict[str, ClassInfo] = {}
        self.relationship_registry: List[RelationshipInfo] = []
        self.import_graph: Dict[str, Set[str]] = {}
        
    def discover_classes(self, target_path: Optional[str] = None) -> Dict[str, ClassInfo]:
        """Discover all classes in the repository or specific path."""
        if target_path:
            search_path = self.repository_root / target_path
        else:
            search_path = self.repository_root
            
        classes = {}
        
        for py_file in search_path.rglob("*.py"):
            if py_file.name.startswith("__") or "test_" in py_file.name:
                continue
                
            try:
                module_classes = self._extract_classes_from_file(py_file)
                classes.update(module_classes)
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")
                
        self.class_registry = classes
        return classes
    
    def _extract_classes_from_file(self, file_path: Path) -> Dict[str, ClassInfo]:
        """Extract class information from a Python file."""
        classes = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, file_path)
                    classes[class_info.name] = class_info
                    
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return classes
    
    def _extract_class_info(self, class_node: ast.ClassDef, file_path: Path) -> ClassInfo:
        """Extract detailed information about a class."""
        methods = []
        attributes = []
        decorators = [d.id if isinstance(d, ast.Name) else str(d) for d in class_node.decorator_list]
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_method_info(item)
                methods.append(method_info.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        base_classes = []
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}")
        
        return ClassInfo(
            name=class_node.name,
            module=file_path.stem,
            file_path=str(file_path.relative_to(self.repository_root)),
            base_classes=base_classes,
            methods=methods,
            attributes=attributes,
            docstring=ast.get_docstring(class_node),
            is_abstract=any('abstract' in dec.lower() for dec in decorators),
            decorators=decorators
        )
    
    def _extract_method_info(self, method_node: ast.FunctionDef) -> MethodInfo:
        """Extract information about a method."""
        parameters = [arg.arg for arg in method_node.args.args if arg.arg != 'self']
        decorators = [d.id if isinstance(d, ast.Name) else str(d) for d in method_node.decorator_list]
        
        return MethodInfo(
            name=method_node.name,
            parameters=parameters,
            return_type=None,  # Would need type annotations parsing
            is_abstract='abstractmethod' in decorators,
            is_static='staticmethod' in decorators,
            is_classmethod='classmethod' in decorators,
            decorators=decorators
        )
    
    def generate_static_structure_diagram(self, class_name: str, include_related: bool = True) -> str:
        """Generate a static structure diagram for a class."""
        if class_name not in self.class_registry:
            self.discover_classes()
            
        if class_name not in self.class_registry:
            return f"Class '{class_name}' not found in repository."
        
        target_class = self.class_registry[class_name]
        mermaid_lines = ["classDiagram"]
        
        # Add the target class
        mermaid_lines.append(self._generate_class_mermaid(target_class))
        
        if include_related:
            # Add related classes (base classes, subclasses, dependencies)
            related_classes = self._find_related_classes(class_name)
            for related_class_name in related_classes:
                if related_class_name in self.class_registry:
                    related_class = self.class_registry[related_class_name]
                    mermaid_lines.append(self._generate_class_mermaid(related_class))
        
        # Add relationships
        relationships = self._find_relationships(class_name, include_related)
        for rel in relationships:
            mermaid_lines.append(self._generate_relationship_mermaid(rel))
        
        return "\n".join(mermaid_lines)
    
    def generate_object_interaction_diagram(self, class_name: str, method_name: Optional[str] = None) -> str:
        """Generate an object interaction/sequence diagram for a class."""
        if class_name not in self.class_registry:
            self.discover_classes()
            
        if class_name not in self.class_registry:
            return f"Class '{class_name}' not found in repository."
        
        target_class = self.class_registry[class_name]
        mermaid_lines = ["sequenceDiagram"]
        
        # Add participants
        mermaid_lines.append(f"    participant {class_name} as {class_name}")
        
        # Add related classes as participants
        related_classes = self._find_related_classes(class_name)
        for related_class_name in related_classes[:5]:  # Limit to 5 for readability
            mermaid_lines.append(f"    participant {related_class_name} as {related_class_name}")
        
        # Add interactions
        if method_name:
            mermaid_lines.append(f"    {class_name}->>+{class_name}: {method_name}()")
            mermaid_lines.append(f"    {class_name}-->>-{class_name}: return")
        else:
            # Show main methods
            for method in target_class.methods[:5]:  # Limit to 5 methods
                mermaid_lines.append(f"    {class_name}->>+{class_name}: {method}()")
                mermaid_lines.append(f"    {class_name}-->>-{class_name}: return")
        
        return "\n".join(mermaid_lines)
    
    def _generate_class_mermaid(self, class_info: ClassInfo) -> str:
        """Generate Mermaid class definition."""
        lines = [f"    class {class_info.name} {{"]
        
        # Add attributes
        for attr in class_info.attributes[:5]:  # Limit for readability
            lines.append(f"        +{attr}")
        
        # Add methods
        for method in class_info.methods[:5]:  # Limit for readability
            lines.append(f"        +{method}()")
        
        lines.append("    }")
        return "\n".join(lines)
    
    def _generate_relationship_mermaid(self, relationship: RelationshipInfo) -> str:
        """Generate Mermaid relationship definition."""
        rel_symbols = {
            'inheritance': '--|>',
            'composition': '*--',
            'aggregation': 'o--',
            'dependency': '..>'
        }
        
        symbol = rel_symbols.get(relationship.relationship_type, '-->')
        label = f" : {relationship.label}" if relationship.label else ""
        
        return f"    {relationship.source} {symbol} {relationship.target}{label}"
    
    def _find_related_classes(self, class_name: str) -> List[str]:
        """Find classes related to the target class."""
        related = set()
        
        if class_name in self.class_registry:
            target_class = self.class_registry[class_name]
            
            # Add base classes
            related.update(target_class.base_classes)
            
            # Find subclasses
            for other_class_name, other_class in self.class_registry.items():
                if class_name in other_class.base_classes:
                    related.add(other_class_name)
        
        return list(related)
    
    def _find_relationships(self, class_name: str, include_related: bool) -> List[RelationshipInfo]:
        """Find relationships for the target class."""
        relationships = []
        
        if class_name in self.class_registry:
            target_class = self.class_registry[class_name]
            
            # Add inheritance relationships
            for base_class in target_class.base_classes:
                relationships.append(RelationshipInfo(
                    source=class_name,
                    target=base_class,
                    relationship_type='inheritance'
                ))
            
            if include_related:
                # Find subclasses
                for other_class_name, other_class in self.class_registry.items():
                    if class_name in other_class.base_classes:
                        relationships.append(RelationshipInfo(
                            source=other_class_name,
                            target=class_name,
                            relationship_type='inheritance'
                        ))
        
        return relationships
    
    def generate_diagram_for_class(self, class_name: str, diagram_type: UMLDiagramType = UMLDiagramType.STATIC_STRUCTURE) -> str:
        """Generate a diagram for a specific class."""
        if diagram_type == UMLDiagramType.STATIC_STRUCTURE:
            return self.generate_static_structure_diagram(class_name)
        elif diagram_type == UMLDiagramType.OBJECT_INTERACTION:
            return self.generate_object_interaction_diagram(class_name)
        else:
            return f"Unsupported diagram type: {diagram_type}"
    
    def save_diagram(self, diagram_content: str, filename: str, output_dir: str = "diagrams") -> str:
        """Save diagram to file."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        file_path = output_path / f"{filename}.mmd"
        with open(file_path, 'w') as f:
            f.write(diagram_content)
        
        return str(file_path)

def main():
    """CLI interface for the dynamic UML viewer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dynamic UML Diagram Viewer")
    parser.add_argument("class_name", help="Name of the class to generate diagram for")
    parser.add_argument("--type", choices=['static', 'interaction'], default='static',
                       help="Type of diagram to generate")
    parser.add_argument("--method", help="Specific method for interaction diagram")
    parser.add_argument("--output", help="Output filename (without extension)")
    parser.add_argument("--path", help="Specific path to search for classes")
    
    args = parser.parse_args()
    
    viewer = DynamicUMLViewer()
    
    # Discover classes
    if args.path:
        classes = viewer.discover_classes(args.path)
    else:
        classes = viewer.discover_classes()
    
    print(f"Discovered {len(classes)} classes")
    
    # Generate diagram
    diagram_type = UMLDiagramType.STATIC_STRUCTURE if args.type == 'static' else UMLDiagramType.OBJECT_INTERACTION
    
    if args.method and diagram_type == UMLDiagramType.OBJECT_INTERACTION:
        diagram = viewer.generate_object_interaction_diagram(args.class_name, args.method)
    else:
        diagram = viewer.generate_diagram_for_class(args.class_name, diagram_type)
    
    print(f"\nGenerated {args.type} diagram for {args.class_name}:")
    print("=" * 50)
    print(diagram)
    
    # Save if output specified
    if args.output:
        filename = args.output
    else:
        filename = f"{args.class_name}_{args.type}"
    
    saved_path = viewer.save_diagram(diagram, filename)
    print(f"\nDiagram saved to: {saved_path}")

if __name__ == "__main__":
    main()
