#!/usr/bin/env python3
"""
Domain Diagram Generator
Creates vertical, readable UML diagrams for all major domains in the system.
"""

import os
from pathlib import Path
from typing import Dict, List, Set
from uml_diagram_viewer import DynamicUMLViewer

class DomainDiagramGenerator:
    """Generates organized domain diagrams."""
    
    def __init__(self, repository_root: str = "."):
        self.viewer = DynamicUMLViewer(repository_root)
        self.output_dir = Path("diagrams/domains")
        self.output_dir.mkdir(exist_ok=True)
        
    def discover_domains(self) -> Dict[str, List[str]]:
        """Discover all major domains and their classes."""
        print("Discovering domains...")
        classes = self.viewer.discover_classes()
        
        domains = {}
        
        # Define domain patterns
        domain_patterns = {
            'ImportDependency': ['Import', 'Dependency', 'Registry'],
            'BeastMode': ['BeastMode', 'SCA', 'SCALPEL'],
            'DevPost': ['DevPost', 'Devpost'],
            'GKE': ['GKE', 'GKEService'],
            'RCA': ['RCA', 'RootCause'],
            'Validation': ['Validation', 'Validator', 'Compliance'],
            'Monitoring': ['Monitor', 'Health', 'Logging'],
            'CLI': ['CLI', 'Command'],
            'Task': ['Task', 'Execution', 'DAG'],
            'Governance': ['Governance', 'Framework', 'Controller'],
            'Agent': ['Agent', 'Orchestration'],
            'Systematic': ['Systematic', 'SystematicComparison'],
            'Domain': ['Domain', 'BoundedContext'],
            'Infrastructure': ['Infrastructure', 'Infra'],
            'Security': ['Security', 'Auth'],
            'Notification': ['Notification', 'Message'],
            'Project': ['Project', 'File', 'Connection'],
            'Analysis': ['Analysis', 'Analyzer', 'Pattern'],
            'Migration': ['Migration', 'LiveMigration'],
            'Quality': ['Quality', 'Gates', 'Assessment']
        }
        
        for class_name, class_info in classes.items():
            assigned = False
            for domain_name, patterns in domain_patterns.items():
                if any(pattern.lower() in class_name.lower() for pattern in patterns):
                    if domain_name not in domains:
                        domains[domain_name] = []
                    domains[domain_name].append(class_name)
                    assigned = True
                    break
            
            # If no specific domain found, check for common patterns
            if not assigned:
                if 'System' in class_name:
                    if 'System' not in domains:
                        domains['System'] = []
                    domains['System'].append(class_name)
                elif 'Engine' in class_name:
                    if 'Engine' not in domains:
                        domains['Engine'] = []
                    domains['Engine'].append(class_name)
                elif 'Manager' in class_name:
                    if 'Manager' not in domains:
                        domains['Manager'] = []
                    domains['Manager'].append(class_name)
        
        return domains
    
    def generate_domain_diagrams(self, domains: Dict[str, List[str]]) -> None:
        """Generate vertical diagrams for each domain."""
        for domain_name, class_names in domains.items():
            if len(class_names) < 2:  # Skip domains with too few classes
                continue
                
            print(f"Generating diagrams for {domain_name} domain ({len(class_names)} classes)...")
            self._generate_domain_markdown(domain_name, class_names)
    
    def _generate_domain_markdown(self, domain_name: str, class_names: List[str]) -> None:
        """Generate markdown file for a specific domain."""
        # Sort classes by name for consistency
        class_names.sort()
        
        # Split into sections if too many classes
        max_classes_per_section = 8
        sections = []
        for i in range(0, len(class_names), max_classes_per_section):
            sections.append(class_names[i:i + max_classes_per_section])
        
        markdown_content = f"# {domain_name} Domain Architecture\n\n"
        markdown_content += f"**Total Classes**: {len(class_names)}\n\n"
        
        for i, section_classes in enumerate(sections):
            section_title = f"Section {i+1}" if len(sections) > 1 else "Class Diagram"
            markdown_content += f"## {section_title}\n\n"
            
            # Generate Mermaid diagram
            mermaid_diagram = self._generate_mermaid_diagram(section_classes)
            markdown_content += f"```mermaid\n{mermaid_diagram}\n```\n\n"
        
        # Add class list
        markdown_content += "## All Classes in Domain\n\n"
        for class_name in class_names:
            markdown_content += f"- `{class_name}`\n"
        
        # Save to file
        filename = f"{domain_name.lower()}_domain_diagrams.md"
        file_path = self.output_dir / filename
        
        with open(file_path, 'w') as f:
            f.write(markdown_content)
        
        print(f"  ✓ Generated: {file_path}")
    
    def _generate_mermaid_diagram(self, class_names: List[str]) -> str:
        """Generate Mermaid class diagram for a list of classes."""
        lines = ["classDiagram"]
        
        # Add classes
        for class_name in class_names:
            if class_name in self.viewer.class_registry:
                class_info = self.viewer.class_registry[class_name]
                lines.append(f"    class {class_name} {{")
                
                # Add methods (limit to 5 for readability)
                for method in class_info.methods[:5]:
                    lines.append(f"        +{method}()")
                
                lines.append("    }")
        
        # Add relationships
        for class_name in class_names:
            if class_name in self.viewer.class_registry:
                class_info = self.viewer.class_registry[class_name]
                for base_class in class_info.base_classes:
                    if base_class in class_names:
                        lines.append(f"    {class_name} --|> {base_class}")
        
        return "\n".join(lines)
    
    def generate_domain_index(self, domains: Dict[str, List[str]]) -> None:
        """Generate index page for all domains."""
        markdown_content = "# Domain Architecture Overview\n\n"
        markdown_content += "This directory contains organized UML diagrams for all major domains in the system.\n\n"
        
        # Sort domains by number of classes (descending)
        sorted_domains = sorted(domains.items(), key=lambda x: len(x[1]), reverse=True)
        
        markdown_content += "## Available Domains\n\n"
        
        for domain_name, class_names in sorted_domains:
            if len(class_names) < 2:
                continue
                
            filename = f"{domain_name.lower()}_domain_diagrams.md"
            markdown_content += f"### [{domain_name} Domain]({filename})\n"
            markdown_content += f"- **Classes**: {len(class_names)}\n"
            markdown_content += f"- **Key Classes**: {', '.join(class_names[:3])}"
            if len(class_names) > 3:
                markdown_content += f" (and {len(class_names)-3} more)"
            markdown_content += "\n\n"
        
        # Save index
        index_path = self.output_dir / "README.md"
        with open(index_path, 'w') as f:
            f.write(markdown_content)
        
        print(f"✓ Generated domain index: {index_path}")

def main():
    """Generate domain diagrams for all major domains."""
    generator = DomainDiagramGenerator()
    
    print("🔍 Discovering domains...")
    domains = generator.discover_domains()
    
    print(f"\n📊 Found {len(domains)} domains:")
    for domain_name, class_names in sorted(domains.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {domain_name}: {len(class_names)} classes")
    
    print(f"\n🎨 Generating domain diagrams...")
    generator.generate_domain_diagrams(domains)
    
    print(f"\n📋 Generating domain index...")
    generator.generate_domain_index(domains)
    
    print(f"\n✅ Domain diagrams generated in: diagrams/domains/")

if __name__ == "__main__":
    main()


