#!/usr/bin/env python3
"""
Constellation Inventory Analyzer
Comprehensive analysis of all 108+ specifications in the repository constellation
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SpecStatus:
    """Status of a specification's completion"""
    requirements_md: str
    design_md: str
    tasks_md: str
    completion_percentage: int

@dataclass
class SpecArtifacts:
    """Artifacts present in a specification directory"""
    has_requirements: bool
    has_design: bool
    has_tasks: bool
    has_dag: bool
    has_spec_state: bool
    other_files: List[str]

@dataclass
class SpecInventoryItem:
    """Complete inventory item for a specification"""
    spec_name: str
    display_name: str
    constellation_layer: int
    layer_name: str
    status: SpecStatus
    artifacts: SpecArtifacts
    missing_artifacts: List[str]
    priority: str
    estimated_effort: str
    dependencies: List[str]

class ConstellationInventoryAnalyzer:
    """Analyzes the complete constellation of specifications"""
    
    def __init__(self, specs_dir: str = ".kiro/specs"):
        self.specs_dir = Path(specs_dir)
        self.inventory: List[SpecInventoryItem] = []
        
        # Layer classification patterns
        self.layer_patterns = {
            0: {  # Bootstrap
                "patterns": [
                    "repository-setup", "installation", "onboarding", "bootstrap",
                    "setup", "install"
                ],
                "name": "Bootstrap"
            },
            1: {  # Foundation
                "patterns": [
                    "governance", "consistency", "health", "auto-start", "cms",
                    "infrastructure", "deployment", "system", "service",
                    "monitoring", "reliability", "security"
                ],
                "name": "Foundation"
            },
            2: {  # Intelligence
                "patterns": [
                    "discovery", "ghostbusters", "rm-ddd", "pdca", "rca",
                    "analysis", "intelligence", "observatory", "memory-palace",
                    "ai-", "classification", "indexing", "content"
                ],
                "name": "Intelligence"
            },
            3: {  # Application
                "patterns": [
                    "collaboration", "requirements", "workflow", "dashboard",
                    "integration", "devpost", "discord", "mcp", "engagement",
                    "coordination", "multi-", "live-"
                ],
                "name": "Application"
            }
        }
        
        # Priority classification
        self.critical_path_specs = {
            "repository-setup-and-installation",
            "repository-content-discovery-indexing",
            "cms-architecture",
            "spec-consistency-governance",
            "system-health-mitigation-framework",
            "service-auto-start-governance",
            "ai-memory-palace",
            "ghostbusters-productivity-triage",
            "comprehensive-makefile-system",
            "dag-orchestrated-parallel-execution"
        }

    def analyze_spec_directory(self, spec_path: Path) -> SpecInventoryItem:
        """Analyze a single specification directory"""
        spec_name = spec_path.name
        
        # Check for core files
        requirements_path = spec_path / "requirements.md"
        design_path = spec_path / "design.md"
        tasks_path = spec_path / "tasks.md"
        spec_state_path = spec_path / ".spec-state"
        
        # Analyze file presence and quality
        has_requirements = requirements_path.exists() and requirements_path.stat().st_size > 100
        has_design = design_path.exists() and design_path.stat().st_size > 100
        has_tasks = tasks_path.exists() and tasks_path.stat().st_size > 100
        has_spec_state = spec_state_path.exists()
        
        # Check for DAG files
        dag_files = list(spec_path.glob("*DAG*.md")) + list(spec_path.glob("*dag*.md"))
        has_dag = len(dag_files) > 0
        
        # Get other files
        all_files = [f.name for f in spec_path.iterdir() if f.is_file()]
        core_files = {"requirements.md", "design.md", "tasks.md", ".spec-state"}
        other_files = [f for f in all_files if f not in core_files]
        
        # Calculate completion status
        completion_count = sum([has_requirements, has_design, has_tasks])
        completion_percentage = int((completion_count / 3) * 100)
        
        status_map = {
            3: "COMPLETE",
            2: "PARTIAL", 
            1: "PARTIAL",
            0: "MISSING"
        }
        
        status = SpecStatus(
            requirements_md="COMPLETE" if has_requirements else "MISSING",
            design_md="COMPLETE" if has_design else "MISSING", 
            tasks_md="COMPLETE" if has_tasks else "MISSING",
            completion_percentage=completion_percentage
        )
        
        artifacts = SpecArtifacts(
            has_requirements=has_requirements,
            has_design=has_design,
            has_tasks=has_tasks,
            has_dag=has_dag,
            has_spec_state=has_spec_state,
            other_files=other_files
        )
        
        # Identify missing artifacts
        missing_artifacts = []
        if not has_requirements:
            missing_artifacts.append("requirements.md")
        if not has_design:
            missing_artifacts.append("design.md")
        if not has_tasks:
            missing_artifacts.append("tasks.md")
            
        # Classify layer
        layer = self.classify_layer(spec_name)
        layer_name = self.layer_patterns[layer]["name"]
        
        # Determine priority
        if spec_name in self.critical_path_specs:
            priority = "CRITICAL_PATH"
        elif completion_percentage == 100:
            priority = "HIGH"
        elif completion_percentage >= 66:
            priority = "MEDIUM"
        else:
            priority = "LOW"
            
        # Estimate effort
        if completion_percentage == 100:
            estimated_effort = "0 days (complete)"
        elif completion_percentage >= 66:
            estimated_effort = "1-2 days"
        elif completion_percentage >= 33:
            estimated_effort = "3-5 days"
        else:
            estimated_effort = "1-2 weeks"
            
        # Extract dependencies (simplified - would need content analysis for full accuracy)
        dependencies = self.extract_dependencies(spec_path)
        
        # Create display name
        display_name = spec_name.replace("-", " ").title()
        
        return SpecInventoryItem(
            spec_name=spec_name,
            display_name=display_name,
            constellation_layer=layer,
            layer_name=layer_name,
            status=status,
            artifacts=artifacts,
            missing_artifacts=missing_artifacts,
            priority=priority,
            estimated_effort=estimated_effort,
            dependencies=dependencies
        )

    def classify_layer(self, spec_name: str) -> int:
        """Classify a spec into its constellation layer"""
        spec_lower = spec_name.lower()
        
        # Check each layer's patterns
        for layer, config in self.layer_patterns.items():
            for pattern in config["patterns"]:
                if pattern in spec_lower:
                    return layer
                    
        # Default to Application layer if no match
        return 3

    def extract_dependencies(self, spec_path: Path) -> List[str]:
        """Extract dependencies from spec files (simplified analysis)"""
        dependencies = []
        
        # Check requirements.md for explicit dependencies
        requirements_path = spec_path / "requirements.md"
        if requirements_path.exists():
            try:
                content = requirements_path.read_text()
                # Look for common dependency patterns
                if "cms-architecture" in content.lower():
                    dependencies.append("cms-architecture")
                if "repository-content-discovery" in content.lower():
                    dependencies.append("repository-content-discovery-indexing")
                if "system-health" in content.lower():
                    dependencies.append("system-health-mitigation-framework")
            except:
                pass
                
        return dependencies

    def analyze_all_specs(self) -> None:
        """Analyze all specifications in the specs directory"""
        if not self.specs_dir.exists():
            raise FileNotFoundError(f"Specs directory not found: {self.specs_dir}")
            
        # Get all spec directories
        spec_dirs = [d for d in self.specs_dir.iterdir() 
                    if d.is_dir() and not d.name.startswith('.')]
        
        print(f"Found {len(spec_dirs)} specification directories")
        
        # Analyze each spec
        for spec_dir in sorted(spec_dirs):
            try:
                spec_item = self.analyze_spec_directory(spec_dir)
                self.inventory.append(spec_item)
                print(f"✅ Analyzed: {spec_item.spec_name} ({spec_item.status.completion_percentage}% complete)")
            except Exception as e:
                print(f"❌ Error analyzing {spec_dir.name}: {e}")

    def generate_reports(self) -> None:
        """Generate all required reports"""
        reports_dir = Path(".kiro/reports")
        reports_dir.mkdir(exist_ok=True)
        
        # 1. Main inventory JSON
        self.generate_inventory_json(reports_dir)
        
        # 2. Layer analysis summary
        self.generate_layer_analysis(reports_dir)
        
        # 3. Missing artifacts report
        self.generate_missing_artifacts_report(reports_dir)
        
        # 4. Dependency graph
        self.generate_dependency_graph(reports_dir)

    def generate_inventory_json(self, reports_dir: Path) -> None:
        """Generate the main constellation inventory JSON"""
        inventory_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_specs": len(self.inventory),
                "analyzer_version": "1.0.0"
            },
            "specifications": [asdict(item) for item in self.inventory]
        }
        
        output_path = reports_dir / "constellation-inventory-2025.json"
        with open(output_path, 'w') as f:
            json.dump(inventory_data, f, indent=2)
        
        print(f"✅ Generated: {output_path}")

    def generate_layer_analysis(self, reports_dir: Path) -> None:
        """Generate layer analysis summary"""
        layer_stats = {}
        
        for layer in range(4):
            layer_name = self.layer_patterns[layer]["name"]
            layer_specs = [s for s in self.inventory if s.constellation_layer == layer]
            
            total_specs = len(layer_specs)
            complete_specs = len([s for s in layer_specs if s.status.completion_percentage == 100])
            partial_specs = len([s for s in layer_specs if 0 < s.status.completion_percentage < 100])
            missing_specs = len([s for s in layer_specs if s.status.completion_percentage == 0])
            
            avg_completion = sum(s.status.completion_percentage for s in layer_specs) / total_specs if total_specs > 0 else 0
            
            layer_stats[layer] = {
                "name": layer_name,
                "total_specs": total_specs,
                "complete_specs": complete_specs,
                "partial_specs": partial_specs,
                "missing_specs": missing_specs,
                "completion_percentage": round(avg_completion, 1)
            }
        
        # Generate markdown report
        report_content = f"""# Layer Analysis Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

Total Specifications: {len(self.inventory)}

"""
        
        for layer, stats in layer_stats.items():
            report_content += f"""### Layer {layer}: {stats['name']}

- **Total Specs:** {stats['total_specs']}
- **Complete:** {stats['complete_specs']} ({stats['complete_specs']/stats['total_specs']*100:.1f}%)
- **Partial:** {stats['partial_specs']} ({stats['partial_specs']/stats['total_specs']*100:.1f}%)
- **Missing:** {stats['missing_specs']} ({stats['missing_specs']/stats['total_specs']*100:.1f}%)
- **Average Completion:** {stats['completion_percentage']}%

"""
        
        # Add critical path analysis
        critical_specs = [s for s in self.inventory if s.priority == "CRITICAL_PATH"]
        critical_complete = len([s for s in critical_specs if s.status.completion_percentage == 100])
        
        report_content += f"""## Critical Path Analysis

- **Critical Path Specs:** {len(critical_specs)}
- **Critical Path Complete:** {critical_complete} ({critical_complete/len(critical_specs)*100:.1f}%)
- **Critical Path Remaining:** {len(critical_specs) - critical_complete}

### Critical Path Specs:
"""
        
        for spec in critical_specs:
            status_icon = "✅" if spec.status.completion_percentage == 100 else "⚠️" if spec.status.completion_percentage > 0 else "❌"
            report_content += f"- {status_icon} **{spec.display_name}** ({spec.status.completion_percentage}% complete)\n"
        
        output_path = reports_dir / "layer-analysis-summary.md"
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        print(f"✅ Generated: {output_path}")

    def generate_missing_artifacts_report(self, reports_dir: Path) -> None:
        """Generate missing artifacts report"""
        specs_with_missing = [s for s in self.inventory if s.missing_artifacts]
        
        report_content = f"""# Missing Artifacts Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Specs:** {len(self.inventory)}
- **Specs with Missing Artifacts:** {len(specs_with_missing)}
- **Complete Specs:** {len(self.inventory) - len(specs_with_missing)}

## Missing Artifacts by Type

"""
        
        # Count missing by type
        missing_requirements = len([s for s in self.inventory if not s.artifacts.has_requirements])
        missing_design = len([s for s in self.inventory if not s.artifacts.has_design])
        missing_tasks = len([s for s in self.inventory if not s.artifacts.has_tasks])
        
        report_content += f"""- **Missing requirements.md:** {missing_requirements} specs
- **Missing design.md:** {missing_design} specs
- **Missing tasks.md:** {missing_tasks} specs

## Detailed Missing Artifacts

"""
        
        for spec in sorted(specs_with_missing, key=lambda x: x.priority):
            priority_icon = "🔴" if spec.priority == "CRITICAL_PATH" else "🟡" if spec.priority == "HIGH" else "🟢"
            report_content += f"""### {priority_icon} {spec.display_name}
- **Layer:** {spec.layer_name}
- **Priority:** {spec.priority}
- **Missing:** {', '.join(spec.missing_artifacts)}
- **Estimated Effort:** {spec.estimated_effort}

"""
        
        output_path = reports_dir / "missing-artifacts-report.md"
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        print(f"✅ Generated: {output_path}")

    def generate_dependency_graph(self, reports_dir: Path) -> None:
        """Generate Mermaid dependency graph"""
        graph_content = """graph TD
    %% Constellation Dependency Graph
    %% Generated automatically from spec analysis
    
    %% Layer 0: Bootstrap
"""
        
        # Group specs by layer
        layers = {}
        for spec in self.inventory:
            layer = spec.constellation_layer
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(spec)
        
        # Generate nodes by layer
        for layer in sorted(layers.keys()):
            layer_name = self.layer_patterns[layer]["name"]
            graph_content += f"\n    %% Layer {layer}: {layer_name}\n"
            
            for spec in layers[layer]:
                node_id = spec.spec_name.replace("-", "_")
                status_style = "fill:#90EE90" if spec.status.completion_percentage == 100 else "fill:#FFE4B5" if spec.status.completion_percentage > 0 else "fill:#FFB6C1"
                
                if spec.priority == "CRITICAL_PATH":
                    graph_content += f'    {node_id}["{spec.display_name}<br/>({spec.status.completion_percentage}%)"]:::critical\n'
                else:
                    graph_content += f'    {node_id}["{spec.display_name}<br/>({spec.status.completion_percentage}%)"]:::normal\n'
        
        # Add dependencies
        graph_content += "\n    %% Dependencies\n"
        for spec in self.inventory:
            node_id = spec.spec_name.replace("-", "_")
            for dep in spec.dependencies:
                dep_id = dep.replace("-", "_")
                graph_content += f"    {dep_id} --> {node_id}\n"
        
        # Add layer dependencies (simplified)
        graph_content += "\n    %% Layer Dependencies\n"
        for layer in range(1, 4):
            prev_layer_specs = [s for s in self.inventory if s.constellation_layer == layer - 1]
            curr_layer_specs = [s for s in self.inventory if s.constellation_layer == layer]
            
            if prev_layer_specs and curr_layer_specs:
                # Connect key specs from previous layer to current layer
                key_prev = [s for s in prev_layer_specs if s.priority in ["CRITICAL_PATH", "HIGH"]][:2]
                key_curr = [s for s in curr_layer_specs if s.priority in ["CRITICAL_PATH", "HIGH"]][:2]
                
                for prev_spec in key_prev:
                    for curr_spec in key_curr:
                        prev_id = prev_spec.spec_name.replace("-", "_")
                        curr_id = curr_spec.spec_name.replace("-", "_")
                        graph_content += f"    {prev_id} -.-> {curr_id}\n"
        
        # Add styles
        graph_content += """
    %% Styles
    classDef critical fill:#FF6B6B,stroke:#333,stroke-width:3px,color:#fff
    classDef normal fill:#4ECDC4,stroke:#333,stroke-width:1px,color:#333
    classDef complete fill:#90EE90,stroke:#333,stroke-width:1px,color:#333
    classDef partial fill:#FFE4B5,stroke:#333,stroke-width:1px,color:#333
    classDef missing fill:#FFB6C1,stroke:#333,stroke-width:1px,color:#333
"""
        
        output_path = reports_dir / "spec-dependency-graph.mmd"
        with open(output_path, 'w') as f:
            f.write(graph_content)
        
        print(f"✅ Generated: {output_path}")

    def print_summary_statistics(self) -> None:
        """Print summary statistics to console"""
        total_specs = len(self.inventory)
        complete_specs = len([s for s in self.inventory if s.status.completion_percentage == 100])
        partial_specs = len([s for s in self.inventory if 0 < s.status.completion_percentage < 100])
        missing_specs = len([s for s in self.inventory if s.status.completion_percentage == 0])
        
        critical_specs = len([s for s in self.inventory if s.priority == "CRITICAL_PATH"])
        critical_complete = len([s for s in self.inventory if s.priority == "CRITICAL_PATH" and s.status.completion_percentage == 100])
        
        print(f"""
📊 CONSTELLATION INVENTORY SUMMARY
=====================================

Total Specs: {total_specs}
Complete: {complete_specs} ({complete_specs/total_specs*100:.1f}%)
Partial: {partial_specs} ({partial_specs/total_specs*100:.1f}%)
Missing: {missing_specs} ({missing_specs/total_specs*100:.1f}%)

Critical Path: {critical_specs} specs
Critical Complete: {critical_complete} ({critical_complete/critical_specs*100:.1f}%)

Layer Breakdown:
""")
        
        for layer in range(4):
            layer_name = self.layer_patterns[layer]["name"]
            layer_specs = [s for s in self.inventory if s.constellation_layer == layer]
            layer_complete = len([s for s in layer_specs if s.status.completion_percentage == 100])
            
            print(f"Layer {layer} ({layer_name}): {len(layer_specs)} specs ({layer_complete} complete)")

def main():
    """Main execution function"""
    print("🔍 Starting Constellation Inventory Analysis...")
    
    analyzer = ConstellationInventoryAnalyzer()
    
    try:
        # Analyze all specs
        analyzer.analyze_all_specs()
        
        # Generate reports
        analyzer.generate_reports()
        
        # Print summary
        analyzer.print_summary_statistics()
        
        print("\n✅ Constellation inventory analysis complete!")
        print("📁 Reports generated in .kiro/reports/")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main()