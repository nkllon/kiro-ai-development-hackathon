#!/usr/bin/env python3
"""
Advanced UML Diagram Viewer with SVG Generation
Generates professional UML diagrams and converts them to SVG format.
"""

import ast
import inspect
import importlib
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import subprocess
import tempfile

@dataclass
class UMLClass:
    """Represents a UML class."""
    name: str
    module: str
    file_path: str
    attributes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    is_abstract: bool = False
    visibility: str = "public"
    stereotypes: List[str] = field(default_factory=list)

@dataclass
class UMLRelationship:
    """Represents a UML relationship."""
    source: str
    target: str
    relationship_type: str  # inheritance, composition, aggregation, dependency, association
    label: Optional[str] = None
    multiplicity: Optional[str] = None
    direction: str = "forward"  # forward, backward, bidirectional

@dataclass
class UMLPackage:
    """Represents a UML package."""
    name: str
    classes: List[UMLClass] = field(default_factory=list)
    subpackages: List['UMLPackage'] = field(default_factory=list)

class UMLDiagramType(Enum):
    """Types of UML diagrams supported."""
    CLASS_DIAGRAM = "class_diagram"
    SEQUENCE_DIAGRAM = "sequence_diagram"
    COMPONENT_DIAGRAM = "component_diagram"
    PACKAGE_DIAGRAM = "package_diagram"
    ACTIVITY_DIAGRAM = "activity_diagram"

class AdvancedUMLViewer:
    """Advanced UML diagram viewer with SVG generation capabilities."""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root).resolve()
        self.classes: Dict[str, UMLClass] = {}
        self.relationships: List[UMLRelationship] = []
        self.packages: Dict[str, UMLPackage] = {}
        
    def discover_architecture(self, target_path: Optional[str] = None) -> Dict[str, UMLClass]:
        """Discover the complete architecture of the repository."""
        if target_path:
            search_path = self.repository_root / target_path
        else:
            search_path = self.repository_root
            
        classes = {}
        
        for py_file in search_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                file_classes = self._extract_uml_classes_from_file(py_file)
                classes.update(file_classes)
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")
        
        self.classes = classes
        self._build_relationships()
        self._organize_packages()
        
        return classes
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "test_",
            "__init__.py",
            ".pyc"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _extract_uml_classes_from_file(self, file_path: Path) -> Dict[str, UMLClass]:
        """Extract UML class information from a Python file."""
        classes = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    uml_class = self._create_uml_class(node, file_path)
                    classes[uml_class.name] = uml_class
                    
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return classes
    
    def _create_uml_class(self, class_node: ast.ClassDef, file_path: Path) -> UMLClass:
        """Create a UMLClass from an AST class node."""
        attributes = []
        methods = []
        stereotypes = []
        
        # Extract decorators for stereotypes
        for decorator in class_node.decorator_list:
            if isinstance(decorator, ast.Name):
                stereotypes.append(decorator.id)
        
        # Extract attributes and methods
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        # Determine if abstract
        is_abstract = any('abstract' in dec.lower() for dec in stereotypes)
        
        # Extract base classes
        base_classes = []
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}")
        
        return UMLClass(
            name=class_node.name,
            module=file_path.stem,
            file_path=str(file_path.relative_to(self.repository_root)),
            attributes=attributes[:10],  # Limit for readability
            methods=methods[:10],  # Limit for readability
            base_classes=base_classes,
            is_abstract=is_abstract,
            stereotypes=stereotypes
        )
    
    def _build_relationships(self):
        """Build relationships between classes."""
        self.relationships = []
        
        for class_name, uml_class in self.classes.items():
            # Inheritance relationships
            for base_class in uml_class.base_classes:
                if base_class in self.classes:
                    self.relationships.append(UMLRelationship(
                        source=class_name,
                        target=base_class,
                        relationship_type="inheritance"
                    ))
    
    def _organize_packages(self):
        """Organize classes into packages based on file structure."""
        self.packages = {}
        
        for class_name, uml_class in self.classes.items():
            package_path = Path(uml_class.file_path).parent
            package_name = str(package_path) if str(package_path) != "." else "root"
            
            if package_name not in self.packages:
                self.packages[package_name] = UMLPackage(name=package_name)
            
            self.packages[package_name].classes.append(uml_class)
    
    def generate_class_diagram(self, target_class: Optional[str] = None, 
                             include_related: bool = True) -> str:
        """Generate a PlantUML class diagram."""
        if target_class and target_class not in self.classes:
            return f"Class '{target_class}' not found."
        
        plantuml_lines = ["@startuml"]
        plantuml_lines.append("!theme plain")
        plantuml_lines.append("skinparam classAttributeIconSize 0")
        plantuml_lines.append("")
        
        if target_class:
            # Generate diagram for specific class
            uml_class = self.classes[target_class]
            plantuml_lines.extend(self._generate_class_plantuml(uml_class))
            
            if include_related:
                related_classes = self._find_related_classes(target_class)
                for related_class_name in related_classes:
                    if related_class_name in self.classes:
                        related_class = self.classes[related_class_name]
                        plantuml_lines.extend(self._generate_class_plantuml(related_class))
        else:
            # Generate diagram for all classes (limited set)
            class_count = 0
            for uml_class in self.classes.values():
                if class_count >= 20:  # Limit for readability
                    break
                plantuml_lines.extend(self._generate_class_plantuml(uml_class))
                class_count += 1
        
        # Add relationships
        for rel in self.relationships:
            plantuml_lines.append(self._generate_relationship_plantuml(rel))
        
        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)
    
    def generate_sequence_diagram(self, target_class: str, 
                                method_name: Optional[str] = None) -> str:
        """Generate a PlantUML sequence diagram."""
        if target_class not in self.classes:
            return f"Class '{target_class}' not found."
        
        plantuml_lines = ["@startuml"]
        plantuml_lines.append("!theme plain")
        plantuml_lines.append("")
        
        uml_class = self.classes[target_class]
        
        # Add participants
        plantuml_lines.append(f"participant {target_class} as {target_class}")
        
        # Add related classes as participants
        related_classes = self._find_related_classes(target_class)
        for related_class_name in related_classes[:5]:  # Limit for readability
            plantuml_lines.append(f"participant {related_class_name} as {related_class_name}")
        
        # Add interactions
        if method_name:
            plantuml_lines.append(f"{target_class} -> {target_class}: {method_name}()")
            plantuml_lines.append(f"{target_class} --> {target_class}: return")
        else:
            # Show main methods
            for method in uml_class.methods[:5]:  # Limit to 5 methods
                plantuml_lines.append(f"{target_class} -> {target_class}: {method}()")
                plantuml_lines.append(f"{target_class} --> {target_class}: return")
        
        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)
    
    def generate_component_diagram(self, target_package: Optional[str] = None) -> str:
        """Generate a PlantUML component diagram."""
        plantuml_lines = ["@startuml"]
        plantuml_lines.append("!theme plain")
        plantuml_lines.append("")
        
        if target_package and target_package in self.packages:
            package = self.packages[target_package]
            plantuml_lines.append(f"package \"{package.name}\" {{")
            for uml_class in package.classes:
                plantuml_lines.append(f"  component {uml_class.name}")
            plantuml_lines.append("}")
        else:
            # Show all packages
            for package_name, package in list(self.packages.items())[:10]:  # Limit for readability
                plantuml_lines.append(f"package \"{package_name}\" {{")
                for uml_class in package.classes[:5]:  # Limit classes per package
                    plantuml_lines.append(f"  component {uml_class.name}")
                plantuml_lines.append("}")
        
        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)
    
    def _generate_class_plantuml(self, uml_class: UMLClass) -> List[str]:
        """Generate PlantUML class definition."""
        lines = []
        
        # Class header
        if uml_class.is_abstract:
            lines.append(f"abstract class {uml_class.name} {{")
        else:
            lines.append(f"class {uml_class.name} {{")
        
        # Add attributes
        for attr in uml_class.attributes:
            lines.append(f"  +{attr}")
        
        # Add methods
        for method in uml_class.methods:
            lines.append(f"  +{method}()")
        
        lines.append("}")
        lines.append("")
        
        return lines
    
    def _generate_relationship_plantuml(self, relationship: UMLRelationship) -> str:
        """Generate PlantUML relationship definition."""
        rel_symbols = {
            'inheritance': '--|>',
            'composition': '*--',
            'aggregation': 'o--',
            'dependency': '..>',
            'association': '-->'
        }
        
        symbol = rel_symbols.get(relationship.relationship_type, '-->')
        label = f" : {relationship.label}" if relationship.label else ""
        
        return f"{relationship.source} {symbol} {relationship.target}{label}"
    
    def _find_related_classes(self, class_name: str) -> List[str]:
        """Find classes related to the target class."""
        related = set()
        
        if class_name in self.classes:
            uml_class = self.classes[class_name]
            
            # Add base classes
            related.update(uml_class.base_classes)
            
            # Find subclasses
            for other_class_name, other_class in self.classes.items():
                if class_name in other_class.base_classes:
                    related.add(other_class_name)
        
        return list(related)
    
    def generate_diagram(self, target: str, diagram_type: UMLDiagramType, 
                        **kwargs) -> str:
        """Generate a diagram of the specified type."""
        if diagram_type == UMLDiagramType.CLASS_DIAGRAM:
            # Remove method parameter for class diagrams
            class_kwargs = {k: v for k, v in kwargs.items() if k != 'method'}
            return self.generate_class_diagram(target, **class_kwargs)
        elif diagram_type == UMLDiagramType.SEQUENCE_DIAGRAM:
            return self.generate_sequence_diagram(target, **kwargs)
        elif diagram_type == UMLDiagramType.COMPONENT_DIAGRAM:
            return self.generate_component_diagram(target, **kwargs)
        else:
            return f"Unsupported diagram type: {diagram_type}"
    
    def save_diagram(self, diagram_content: str, filename: str, 
                    output_dir: str = "diagrams") -> str:
        """Save diagram to file."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        file_path = output_path / f"{filename}.puml"
        with open(file_path, 'w') as f:
            f.write(diagram_content)
        
        return str(file_path)
    
    def convert_to_svg(self, plantuml_file: str, output_file: Optional[str] = None) -> str:
        """Convert PlantUML file to SVG using plantuml command."""
        plantuml_path = Path(plantuml_file)
        
        if not plantuml_path.exists():
            raise FileNotFoundError(f"PlantUML file not found: {plantuml_file}")
        
        if output_file is None:
            output_file = plantuml_path.with_suffix('.svg')
        
        try:
            # Try to use plantuml command
            result = subprocess.run([
                'plantuml', '-tsvg', '-o', str(Path(output_file).parent), 
                str(plantuml_path)
            ], capture_output=True, text=True, check=True)
            
            return str(output_file)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: return the PlantUML file path
            print(f"Warning: PlantUML command not found. Returning PlantUML file: {plantuml_file}")
            return str(plantuml_file)
    
    def generate_and_convert(self, target: str, diagram_type: UMLDiagramType, 
                           filename: str, **kwargs) -> Tuple[str, str]:
        """Generate diagram and convert to SVG."""
        # Generate diagram
        diagram_content = self.generate_diagram(target, diagram_type, **kwargs)
        
        # Save PlantUML file
        plantuml_file = self.save_diagram(diagram_content, filename)
        
        # Convert to SVG
        svg_file = self.convert_to_svg(plantuml_file)
        
        return plantuml_file, svg_file

def main():
    """CLI interface for the advanced UML viewer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced UML Diagram Viewer")
    parser.add_argument("target", help="Target class or package name")
    parser.add_argument("--type", choices=['class', 'sequence', 'component'], 
                       default='class', help="Type of diagram to generate")
    parser.add_argument("--method", help="Specific method for sequence diagram")
    parser.add_argument("--output", help="Output filename (without extension)")
    parser.add_argument("--path", help="Specific path to search for classes")
    parser.add_argument("--svg", action='store_true', help="Convert to SVG")
    
    args = parser.parse_args()
    
    viewer = AdvancedUMLViewer()
    
    # Discover architecture
    if args.path:
        classes = viewer.discover_architecture(args.path)
    else:
        classes = viewer.discover_architecture()
    
    print(f"Discovered {len(classes)} classes")
    
    # Generate diagram
    diagram_type_map = {
        'class': UMLDiagramType.CLASS_DIAGRAM,
        'sequence': UMLDiagramType.SEQUENCE_DIAGRAM,
        'component': UMLDiagramType.COMPONENT_DIAGRAM
    }
    
    diagram_type = diagram_type_map[args.type]
    
    if args.method and diagram_type == UMLDiagramType.SEQUENCE_DIAGRAM:
        diagram = viewer.generate_sequence_diagram(args.target, args.method)
    else:
        diagram = viewer.generate_diagram(args.target, diagram_type)
    
    print(f"\nGenerated {args.type} diagram for {args.target}:")
    print("=" * 50)
    print(diagram)
    
    # Save diagram
    if args.output:
        filename = args.output
    else:
        filename = f"{args.target}_{args.type}"
    
    if args.svg:
        plantuml_file, svg_file = viewer.generate_and_convert(
            args.target, diagram_type, filename, 
            method=args.method if args.method else None
        )
        print(f"\nPlantUML file saved to: {plantuml_file}")
        print(f"SVG file saved to: {svg_file}")
    else:
        saved_path = viewer.save_diagram(diagram, filename)
        print(f"\nDiagram saved to: {saved_path}")

if __name__ == "__main__":
    main()
