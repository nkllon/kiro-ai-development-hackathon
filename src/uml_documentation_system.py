#!/usr/bin/env python3
"""
Comprehensive UML Documentation System
Generates multiple UML diagram types and converts them to SVG format.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from advanced_uml_viewer import AdvancedUMLViewer, UMLDiagramType

class UMLDocumentationSystem:
    """Comprehensive UML documentation system."""
    
    def __init__(self, repository_root: str = "."):
        self.viewer = AdvancedUMLViewer(repository_root)
        self.output_dir = Path("diagrams")
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_comprehensive_documentation(self, target_classes: List[str]) -> Dict[str, Dict[str, str]]:
        """Generate comprehensive UML documentation for target classes."""
        results = {}
        
        # Discover architecture
        print("Discovering repository architecture...")
        self.viewer.discover_architecture()
        print(f"Discovered {len(self.viewer.classes)} classes")
        
        for class_name in target_classes:
            print(f"\nGenerating documentation for {class_name}...")
            results[class_name] = {}
            
            # Generate class diagram
            try:
                plantuml_file, svg_file = self.viewer.generate_and_convert(
                    class_name, UMLDiagramType.CLASS_DIAGRAM, 
                    f"{class_name}_class_diagram"
                )
                results[class_name]['class_diagram'] = {
                    'plantuml': plantuml_file,
                    'svg': svg_file
                }
                print(f"  ✓ Class diagram: {svg_file}")
            except Exception as e:
                print(f"  ✗ Class diagram failed: {e}")
                results[class_name]['class_diagram'] = {'error': str(e)}
            
            # Generate sequence diagram
            try:
                plantuml_file, svg_file = self.viewer.generate_and_convert(
                    class_name, UMLDiagramType.SEQUENCE_DIAGRAM, 
                    f"{class_name}_sequence_diagram"
                )
                results[class_name]['sequence_diagram'] = {
                    'plantuml': plantuml_file,
                    'svg': svg_file
                }
                print(f"  ✓ Sequence diagram: {svg_file}")
            except Exception as e:
                print(f"  ✗ Sequence diagram failed: {e}")
                results[class_name]['sequence_diagram'] = {'error': str(e)}
            
            # Generate component diagram
            try:
                plantuml_file, svg_file = self.viewer.generate_and_convert(
                    class_name, UMLDiagramType.COMPONENT_DIAGRAM, 
                    f"{class_name}_component_diagram"
                )
                results[class_name]['component_diagram'] = {
                    'plantuml': plantuml_file,
                    'svg': svg_file
                }
                print(f"  ✓ Component diagram: {svg_file}")
            except Exception as e:
                print(f"  ✗ Component diagram failed: {e}")
                results[class_name]['component_diagram'] = {'error': str(e)}
        
        return results
    
    def generate_architecture_overview(self) -> Dict[str, str]:
        """Generate high-level architecture overview diagrams."""
        print("\nGenerating architecture overview...")
        
        # Generate package diagram
        try:
            plantuml_file, svg_file = self.viewer.generate_and_convert(
                None, UMLDiagramType.COMPONENT_DIAGRAM, 
                "architecture_overview"
            )
            print(f"  ✓ Architecture overview: {svg_file}")
            return {'architecture_overview': {'plantuml': plantuml_file, 'svg': svg_file}}
        except Exception as e:
            print(f"  ✗ Architecture overview failed: {e}")
            return {'architecture_overview': {'error': str(e)}}
    
    def create_documentation_index(self, results: Dict[str, Dict[str, str]]) -> str:
        """Create an HTML index of all generated diagrams."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UML Documentation Index</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        .class-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background: #fafafa; }
        .diagram-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 15px 0; }
        .diagram-item { text-align: center; padding: 15px; border: 1px solid #ccc; border-radius: 5px; background: white; }
        .diagram-item h3 { margin: 0 0 10px 0; color: #333; }
        .diagram-item img { max-width: 100%; height: auto; border: 1px solid #ddd; }
        .error { color: #d32f2f; background: #ffebee; padding: 10px; border-radius: 3px; }
        .success { color: #2e7d32; }
        a { color: #007acc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>UML Documentation Index</h1>
        <p>Comprehensive UML diagrams for the repository architecture.</p>
"""
        
        for class_name, diagrams in results.items():
            html_content += f"""
        <div class="class-section">
            <h2>{class_name}</h2>
            <div class="diagram-grid">
"""
            
            for diagram_type, diagram_info in diagrams.items():
                if 'error' in diagram_info:
                    html_content += f"""
                <div class="diagram-item">
                    <h3>{diagram_type.replace('_', ' ').title()}</h3>
                    <div class="error">Error: {diagram_info['error']}</div>
                </div>
"""
                else:
                    svg_path = diagram_info['svg']
                    if svg_path.endswith('.svg'):
                        html_content += f"""
                <div class="diagram-item">
                    <h3>{diagram_type.replace('_', ' ').title()}</h3>
                    <img src="{svg_path}" alt="{class_name} {diagram_type}">
                    <p><a href="{svg_path}" target="_blank">View Full Size</a></p>
                </div>
"""
                    else:
                        html_content += f"""
                <div class="diagram-item">
                    <h3>{diagram_type.replace('_', ' ').title()}</h3>
                    <p><a href="{svg_path}" target="_blank">View PlantUML File</a></p>
                </div>
"""
            
            html_content += """
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w') as f:
            f.write(html_content)
        
        return str(index_file)
    
    def install_plantuml(self) -> bool:
        """Install PlantUML if not available."""
        try:
            result = subprocess.run(['plantuml', '-version'], 
                                  capture_output=True, text=True, check=True)
            print("PlantUML is already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("PlantUML not found. Attempting to install...")
            
            # Try different installation methods
            install_commands = [
                ['brew', 'install', 'plantuml'],  # macOS
                ['apt-get', 'install', 'plantuml'],  # Ubuntu/Debian
                ['yum', 'install', 'plantuml'],  # CentOS/RHEL
            ]
            
            for cmd in install_commands:
                try:
                    subprocess.run(cmd, check=True)
                    print(f"PlantUML installed successfully using {cmd[0]}")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            print("Could not install PlantUML automatically. Please install manually.")
            print("Visit: https://plantuml.com/starting")
            return False

def main():
    """CLI interface for the UML documentation system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="UML Documentation System")
    parser.add_argument("--classes", nargs="+", 
                       default=["ReflectiveModule", "ImportDependencyRegistry", "BeastModeRegistry"],
                       help="Classes to generate documentation for")
    parser.add_argument("--overview", action='store_true', 
                       help="Generate architecture overview")
    parser.add_argument("--install-plantuml", action='store_true',
                       help="Install PlantUML if not available")
    
    args = parser.parse_args()
    
    system = UMLDocumentationSystem()
    
    # Install PlantUML if requested
    if args.install_plantuml:
        if not system.install_plantuml():
            return 1
    
    # Generate documentation for specified classes
    print(f"Generating UML documentation for: {', '.join(args.classes)}")
    results = system.generate_comprehensive_documentation(args.classes)
    
    # Generate architecture overview if requested
    if args.overview:
        overview_results = system.generate_architecture_overview()
        results['architecture'] = overview_results
    
    # Create documentation index
    print("\nCreating documentation index...")
    index_file = system.create_documentation_index(results)
    print(f"Documentation index created: {index_file}")
    
    print(f"\nUML documentation complete! View results at: {index_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())


