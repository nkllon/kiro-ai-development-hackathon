#!/usr/bin/env python3
"""
RDI Extraction Engine
====================

Systematic extraction and analysis of Requirements, Designs, and Implementations
across the entire repository to identify gaps and ensure complete RDI compliance.

This tool performs comprehensive analysis to find:
- Requirements without corresponding Designs
- Designs without corresponding Implementations  
- Implementations without corresponding Requirements
- Partial RDI chains that need completion

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import ast
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RDIComponentType(Enum):
    REQUIREMENT = "requirement"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"

@dataclass
class RDIComponent:
    """Represents a single RDI component (Requirement, Design, or Implementation)"""
    id: str
    component_type: RDIComponentType
    title: str
    description: str
    source_file: str
    line_number: int
    content: str
    related_ids: List[str]
    status: str = "unknown"
    priority: str = "medium"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class RDIExtractionEngine:
    """Main engine for extracting and analyzing RDI components"""
    
    def __init__(self, repository_root: str):
        self.repository_root = Path(repository_root)
        self.requirements: List[RDIComponent] = []
        self.designs: List[RDIComponent] = []
        self.implementations: List[RDIComponent] = []
        self.rdi_gaps: List[Dict[str, Any]] = []
        
        # Patterns for identifying RDI components
        self.requirement_patterns = [
            r'requirement\s+\d+',
            r'req\s+\d+',
            r'user\s+story',
            r'acceptance\s+criteria',
            r'when\s+.*\s+then\s+.*\s+shall',
            r'as\s+a\s+.*\s+i\s+want\s+to',
            r'must\s+.*\s+so\s+that',
            r'shall\s+.*\s+so\s+that',
            r'functional\s+requirement',
            r'non-functional\s+requirement'
        ]
        
        self.design_patterns = [
            r'design\s+document',
            r'architecture\s+diagram',
            r'component\s+diagram',
            r'sequence\s+diagram',
            r'class\s+diagram',
            r'interface\s+definition',
            r'api\s+specification',
            r'data\s+model',
            r'system\s+architecture',
            r'high-level\s+design',
            r'detailed\s+design'
        ]
        
        self.implementation_patterns = [
            r'class\s+\w+.*:',
            r'def\s+\w+.*:',
            r'async\s+def\s+\w+.*:',
            r'@\w+.*\n\s*def\s+\w+',
            r'interface\s+\w+',
            r'implements\s+\w+',
            r'extends\s+\w+',
            r'function\s+\w+',
            r'module\s+\w+',
            r'component\s+\w+'
        ]

    def extract_all_rdi_components(self) -> Dict[str, List[RDIComponent]]:
        """Extract all RDI components from the repository"""
        logger.info("Starting comprehensive RDI extraction...")
        
        # Extract requirements
        logger.info("Extracting requirements...")
        self.requirements = self._extract_requirements()
        logger.info(f"Found {len(self.requirements)} requirements")
        
        # Extract designs
        logger.info("Extracting designs...")
        self.designs = self._extract_designs()
        logger.info(f"Found {len(self.designs)} designs")
        
        # Extract implementations
        logger.info("Extracting implementations...")
        self.implementations = self._extract_implementations()
        logger.info(f"Found {len(self.implementations)} implementations")
        
        # Analyze gaps
        logger.info("Analyzing RDI gaps...")
        self.rdi_gaps = self._analyze_rdi_gaps()
        logger.info(f"Found {len(self.rdi_gaps)} RDI gaps")
        
        return {
            'requirements': self.requirements,
            'designs': self.designs,
            'implementations': self.implementations,
            'gaps': self.rdi_gaps
        }

    def _extract_requirements(self) -> List[RDIComponent]:
        """Extract all requirements from the repository"""
        requirements = []
        
        # Search in specification files
        spec_files = list(self.repository_root.glob(".kiro/specs/*/requirements.md"))
        for spec_file in spec_files:
            requirements.extend(self._extract_from_file(spec_file, RDIComponentType.REQUIREMENT))
        
        # Search in docs directory
        doc_files = list(self.repository_root.glob("docs/**/*.md"))
        for doc_file in doc_files:
            if 'requirement' in doc_file.name.lower():
                requirements.extend(self._extract_from_file(doc_file, RDIComponentType.REQUIREMENT))
        
        # Search in README files
        readme_files = list(self.repository_root.glob("**/README.md"))
        for readme_file in readme_files:
            requirements.extend(self._extract_from_file(readme_file, RDIComponentType.REQUIREMENT))
        
        return requirements

    def _extract_designs(self) -> List[RDIComponent]:
        """Extract all designs from the repository"""
        designs = []
        
        # Search in specification files
        spec_files = list(self.repository_root.glob(".kiro/specs/*/design.md"))
        for spec_file in spec_files:
            designs.extend(self._extract_from_file(spec_file, RDIComponentType.DESIGN))
        
        # Search in architecture diagrams
        diagram_files = list(self.repository_root.glob("**/*.puml")) + \
                       list(self.repository_root.glob("**/*.mmd")) + \
                       list(self.repository_root.glob("**/*.mermaid"))
        for diagram_file in diagram_files:
            designs.extend(self._extract_from_file(diagram_file, RDIComponentType.DESIGN))
        
        # Search in docs directory
        doc_files = list(self.repository_root.glob("docs/**/*.md"))
        for doc_file in doc_files:
            if 'design' in doc_file.name.lower() or 'architecture' in doc_file.name.lower():
                designs.extend(self._extract_from_file(doc_file, RDIComponentType.DESIGN))
        
        return designs

    def _extract_implementations(self) -> List[RDIComponent]:
        """Extract all implementations from the repository"""
        implementations = []
        
        # Search in source code
        python_files = list(self.repository_root.glob("src/**/*.py"))
        for py_file in python_files:
            implementations.extend(self._extract_from_file(py_file, RDIComponentType.IMPLEMENTATION))
        
        # Search in test files
        test_files = list(self.repository_root.glob("tests/**/*.py"))
        for test_file in test_files:
            implementations.extend(self._extract_from_file(test_file, RDIComponentType.IMPLEMENTATION))
        
        # Search in scripts
        script_files = list(self.repository_root.glob("scripts/**/*.py"))
        for script_file in script_files:
            implementations.extend(self._extract_from_file(script_file, RDIComponentType.IMPLEMENTATION))
        
        return implementations

    def _extract_from_file(self, file_path: Path, component_type: RDIComponentType) -> List[RDIComponent]:
        """Extract RDI components from a specific file"""
        components = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            if component_type == RDIComponentType.REQUIREMENT:
                components = self._extract_requirements_from_content(content, lines, file_path)
            elif component_type == RDIComponentType.DESIGN:
                components = self._extract_designs_from_content(content, lines, file_path)
            elif component_type == RDIComponentType.IMPLEMENTATION:
                components = self._extract_implementations_from_content(content, lines, file_path)
                
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {e}")
        
        return components

    def _extract_requirements_from_content(self, content: str, lines: List[str], file_path: Path) -> List[RDIComponent]:
        """Extract requirements from file content"""
        components = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for requirement patterns
            for pattern in self.requirement_patterns:
                if re.search(pattern, line_lower):
                    # Extract requirement details
                    req_id = f"REQ_{file_path.stem}_{i+1}"
                    title = self._extract_title_from_line(line)
                    description = self._extract_description_from_context(lines, i)
                    
                    component = RDIComponent(
                        id=req_id,
                        component_type=RDIComponentType.REQUIREMENT,
                        title=title,
                        description=description,
                        source_file=str(file_path.relative_to(self.repository_root)),
                        line_number=i+1,
                        content=line.strip(),
                        related_ids=[]
                    )
                    components.append(component)
                    break
        
        return components

    def _extract_designs_from_content(self, content: str, lines: List[str], file_path: Path) -> List[RDIComponent]:
        """Extract designs from file content"""
        components = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for design patterns
            for pattern in self.design_patterns:
                if re.search(pattern, line_lower):
                    # Extract design details
                    design_id = f"DESIGN_{file_path.stem}_{i+1}"
                    title = self._extract_title_from_line(line)
                    description = self._extract_description_from_context(lines, i)
                    
                    component = RDIComponent(
                        id=design_id,
                        component_type=RDIComponentType.DESIGN,
                        title=title,
                        description=description,
                        source_file=str(file_path.relative_to(self.repository_root)),
                        line_number=i+1,
                        content=line.strip(),
                        related_ids=[]
                    )
                    components.append(component)
                    break
        
        return components

    def _extract_implementations_from_content(self, content: str, lines: List[str], file_path: Path) -> List[RDIComponent]:
        """Extract implementations from file content"""
        components = []
        
        try:
            # Parse Python AST for better implementation detection
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    impl_id = f"IMPL_{file_path.stem}_{node.lineno}"
                    component = RDIComponent(
                        id=impl_id,
                        component_type=RDIComponentType.IMPLEMENTATION,
                        title=f"Class: {node.name}",
                        description=self._extract_class_description(node),
                        source_file=str(file_path.relative_to(self.repository_root)),
                        line_number=node.lineno,
                        content=ast.get_source_segment(content, node),
                        related_ids=[]
                    )
                    components.append(component)
                
                elif isinstance(node, ast.FunctionDef):
                    impl_id = f"IMPL_{file_path.stem}_{node.lineno}"
                    component = RDIComponent(
                        id=impl_id,
                        component_type=RDIComponentType.IMPLEMENTATION,
                        title=f"Function: {node.name}",
                        description=self._extract_function_description(node),
                        source_file=str(file_path.relative_to(self.repository_root)),
                        line_number=node.lineno,
                        content=ast.get_source_segment(content, node),
                        related_ids=[]
                    )
                    components.append(component)
                    
        except SyntaxError:
            # Fallback to pattern matching for non-Python files
            for i, line in enumerate(lines):
                line_lower = line.lower()
                for pattern in self.implementation_patterns:
                    if re.search(pattern, line_lower):
                        impl_id = f"IMPL_{file_path.stem}_{i+1}"
                        component = RDIComponent(
                            id=impl_id,
                            component_type=RDIComponentType.IMPLEMENTATION,
                            title=self._extract_title_from_line(line),
                            description=self._extract_description_from_context(lines, i),
                            source_file=str(file_path.relative_to(self.repository_root)),
                            line_number=i+1,
                            content=line.strip(),
                            related_ids=[]
                        )
                        components.append(component)
                        break
        
        return components

    def _extract_title_from_line(self, line: str) -> str:
        """Extract a title from a line of text"""
        # Remove markdown headers
        title = re.sub(r'^#+\s*', '', line.strip())
        # Remove common prefixes
        title = re.sub(r'^(requirement|req|design|implementation|class|function|def)\s*\d*:?\s*', '', title, flags=re.IGNORECASE)
        return title[:100] if title else "Untitled"

    def _extract_description_from_context(self, lines: List[str], line_index: int) -> str:
        """Extract description from surrounding context"""
        start = max(0, line_index - 2)
        end = min(len(lines), line_index + 3)
        context_lines = lines[start:end]
        return ' '.join(context_lines).strip()[:200]

    def _extract_class_description(self, node: ast.ClassDef) -> str:
        """Extract description from a class definition"""
        if node.docstring:
            return node.docstring[:200]
        return f"Class {node.name} with {len(node.body)} methods"

    def _extract_function_description(self, node: ast.FunctionDef) -> str:
        """Extract description from a function definition"""
        if node.docstring:
            return node.docstring[:200]
        return f"Function {node.name} with {len(node.args.args)} parameters"

    def _analyze_rdi_gaps(self) -> List[Dict[str, Any]]:
        """Analyze gaps between Requirements, Designs, and Implementations"""
        gaps = []
        
        # Find requirements without designs
        req_ids = {req.id for req in self.requirements}
        design_related_ids = set()
        for design in self.designs:
            design_related_ids.update(design.related_ids)
        
        orphaned_requirements = req_ids - design_related_ids
        for req_id in orphaned_requirements:
            req = next((r for r in self.requirements if r.id == req_id), None)
            if req:
                gaps.append({
                    'gap_type': 'requirement_without_design',
                    'component_id': req_id,
                    'component': req,
                    'severity': 'high',
                    'description': f"Requirement '{req.title}' has no corresponding design",
                    'mitigation': f"Create design document for requirement {req_id}"
                })
        
        # Find designs without implementations
        design_ids = {design.id for design in self.designs}
        impl_related_ids = set()
        for impl in self.implementations:
            impl_related_ids.update(impl.related_ids)
        
        orphaned_designs = design_ids - impl_related_ids
        for design_id in orphaned_designs:
            design = next((d for d in self.designs if d.id == design_id), None)
            if design:
                gaps.append({
                    'gap_type': 'design_without_implementation',
                    'component_id': design_id,
                    'component': design,
                    'severity': 'high',
                    'description': f"Design '{design.title}' has no corresponding implementation",
                    'mitigation': f"Implement design {design_id}"
                })
        
        # Find implementations without requirements
        impl_ids = {impl.id for impl in self.implementations}
        req_related_ids = set()
        for req in self.requirements:
            req_related_ids.update(req.related_ids)
        
        orphaned_implementations = impl_ids - req_related_ids
        for impl_id in orphaned_implementations:
            impl = next((i for i in self.implementations if i.id == impl_id), None)
            if impl:
                gaps.append({
                    'gap_type': 'implementation_without_requirement',
                    'component_id': impl_id,
                    'component': impl,
                    'severity': 'medium',
                    'description': f"Implementation '{impl.title}' has no corresponding requirement",
                    'mitigation': f"Document requirement for implementation {impl_id} or remove orphaned code"
                })
        
        return gaps

    def generate_rdi_report(self, output_file: str = None) -> str:
        """Generate comprehensive RDI analysis report"""
        if not output_file:
            output_file = self.repository_root / "docs/rc1/analysis/RDI_COMPREHENSIVE_ANALYSIS_REPORT.md"
        
        report = f"""# COMPREHENSIVE RDI ANALYSIS REPORT

**Generated**: {self._get_timestamp()}
**Repository**: {self.repository_root}
**Analysis Engine**: RDI Extraction Engine v1.0

## EXECUTIVE SUMMARY

This report provides a comprehensive analysis of Requirements-Design-Implementation (RDI) compliance across the entire repository.

### Key Metrics
- **Total Requirements**: {len(self.requirements)}
- **Total Designs**: {len(self.designs)}
- **Total Implementations**: {len(self.implementations)}
- **RDI Gaps Identified**: {len(self.rdi_gaps)}

### Critical Issues
- **Requirements without Designs**: {len([g for g in self.rdi_gaps if g['gap_type'] == 'requirement_without_design'])}
- **Designs without Implementations**: {len([g for g in self.rdi_gaps if g['gap_type'] == 'design_without_implementation'])}
- **Implementations without Requirements**: {len([g for g in self.rdi_gaps if g['gap_type'] == 'implementation_without_requirement'])}

## DETAILED ANALYSIS

### Requirements Inventory
"""
        
        for req in self.requirements:
            report += f"""
#### {req.id}
- **Title**: {req.title}
- **Source**: {req.source_file}:{req.line_number}
- **Status**: {req.status}
- **Description**: {req.description[:200]}...
"""
        
        report += "\n### Designs Inventory\n"
        for design in self.designs:
            report += f"""
#### {design.id}
- **Title**: {design.title}
- **Source**: {design.source_file}:{design.line_number}
- **Status**: {design.status}
- **Description**: {design.description[:200]}...
"""
        
        report += "\n### Implementations Inventory\n"
        for impl in self.implementations:
            report += f"""
#### {impl.id}
- **Title**: {impl.title}
- **Source**: {impl.source_file}:{impl.line_number}
- **Status**: {impl.status}
- **Description**: {impl.description[:200]}...
"""
        
        report += "\n## RDI GAPS ANALYSIS\n"
        for gap in self.rdi_gaps:
            report += f"""
### {gap['gap_type'].replace('_', ' ').title()}
- **Component ID**: {gap['component_id']}
- **Severity**: {gap['severity']}
- **Description**: {gap['description']}
- **Mitigation**: {gap['mitigation']}
"""
        
        report += f"""

## MITIGATION PLAN

### High Priority Actions
1. **Address Requirements without Designs** ({len([g for g in self.rdi_gaps if g['gap_type'] == 'requirement_without_design'])} items)
2. **Address Designs without Implementations** ({len([g for g in self.rdi_gaps if g['gap_type'] == 'design_without_implementation'])} items)

### Medium Priority Actions
1. **Address Implementations without Requirements** ({len([g for g in self.rdi_gaps if g['gap_type'] == 'implementation_without_requirement'])} items)

### Next Steps
1. Review each identified gap
2. Create specific action plans for each gap
3. Implement fixes according to priority
4. Validate RDI compliance after fixes
5. Establish ongoing RDI monitoring

---
*This report was generated by the RDI Extraction Engine as part of the systematic RDI compliance analysis.*
"""
        
        # Write report to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"RDI report written to {output_file}")
        return str(output_file)

    def _get_timestamp(self) -> str:
        """Get current timestamp for report"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main entry point for RDI extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract and analyze RDI components")
    parser.add_argument("--repository", default=".", help="Repository root path")
    parser.add_argument("--output", help="Output report file path")
    
    args = parser.parse_args()
    
    # Initialize extraction engine
    engine = RDIExtractionEngine(args.repository)
    
    # Extract all RDI components
    results = engine.extract_all_rdi_components()
    
    # Generate report
    report_file = engine.generate_rdi_report(args.output)
    
    print(f"RDI analysis complete. Report generated: {report_file}")
    print(f"Found {len(results['requirements'])} requirements, {len(results['designs'])} designs, {len(results['implementations'])} implementations")
    print(f"Identified {len(results['gaps'])} RDI gaps")

if __name__ == "__main__":
    main()
