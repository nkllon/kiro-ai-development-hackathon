#!/usr/bin/env python3
"""
🚨 MAKEFILE SYSTEM MODEL 🚨
===========================

"This is it! The moment we should have trained for!"
Comprehensive Makefile system model with proper projections from all implementations.

Military-derived precision for Makefile system modeling.
When the Makefile system needs to be true'd up, Ghostbusters deploy!

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Unified Makefile system model and implementation
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class MakefileTarget:
    """Represents a Makefile target with its dependencies and commands."""
    name: str
    dependencies: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    description: str = ""
    phony: bool = False
    file_path: str = ""
    line_number: int = 0
    category: str = "general"
    priority: int = 0

@dataclass
class MakefileVariable:
    """Represents a Makefile variable definition."""
    name: str
    value: str
    file_path: str = ""
    line_number: int = 0
    scope: str = "global"  # global, target-specific, pattern-specific

@dataclass
class MakefileProjection:
    """Represents a projection of the Makefile system."""
    name: str
    description: str
    targets: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    categories: Dict[str, List[str]] = field(default_factory=dict)

class MakefileSystemModel:
    """🚨 COMPREHENSIVE MAKEFILE SYSTEM MODEL 🚨"""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root)
        self.targets: Dict[str, MakefileTarget] = {}
        self.variables: Dict[str, MakefileVariable] = {}
        self.projections: Dict[str, MakefileProjection] = {}
        self.makefiles: List[Path] = []
        
        # Military-derived exclamations for Makefile system
        self.makefile_exclamations = [
            "🚨 THIS IS IT! THE MOMENT WE SHOULD HAVE TRAINED FOR!",
            "🛑 ALL HANDS ON DECK - MAKEFILE SYSTEM ANALYSIS INITIATED!",
            "🚨 GHOSTBUSTERS TO THE RESCUE - MAKEFILE SYSTEM DEPLOYING!",
            "🛑 EMERGENCY PROTOCOLS ACTIVATED - MAKEFILE SYSTEM INCOMING!",
            "🚨 THIS IS OUR DARKEST HOUR - MAKEFILE SYSTEM DEPLOYING!",
            "🛑 MAKEFILE SYSTEM ON FIRE - TIME TO EARN OUR PAY!",
            "🚨 CRISIS MODE ENGAGED - MAKEFILE SYSTEM ANALYSIS INCOMING!",
            "🛑 WE'RE IN THE SHIT NOW - TIME TO BE HEROES!",
        ]
        
        # Target categories for systematic organization
        self.target_categories = {
            "build": ["build", "compile", "make", "assemble"],
            "test": ["test", "check", "verify", "validate"],
            "clean": ["clean", "purge", "remove", "delete"],
            "install": ["install", "deploy", "setup", "configure"],
            "dev": ["dev", "development", "watch", "serve"],
            "docs": ["docs", "documentation", "generate-docs"],
            "release": ["release", "package", "distribute", "publish"],
            "quality": ["lint", "format", "style", "quality"],
            "integration": ["integration", "e2e", "end-to-end"],
            "security": ["security", "audit", "scan", "vulnerability"],
            "performance": ["benchmark", "profile", "performance"],
            "migration": ["migrate", "migration", "upgrade", "refactor"],
            "interface": ["interface", "registry", "governance"],
            "beast_mode": ["beast", "beast-mode", "systematic"],
            "rdi": ["rdi", "registry-driven", "interface-driven"],
            "rm_ddd": ["rm-ddd", "reflective-module", "domain-driven"]
        }
    
    def discover_makefiles(self) -> List[Path]:
        """Discover all Makefiles in the repository."""
        print("🔍 Discovering Makefiles...")
        
        makefiles = []
        
        # Look for various Makefile patterns
        patterns = [
            "Makefile",
            "makefile", 
            "Makefile.*",
            "*.mk",
            "**/Makefile",
            "**/makefile",
            "**/*.mk"
        ]
        
        for pattern in patterns:
            for makefile in self.repository_root.rglob(pattern):
                if makefile.is_file() and self._is_valid_makefile(makefile):
                    makefiles.append(makefile)
        
        self.makefiles = makefiles
        print(f"📊 Found {len(makefiles)} Makefiles")
        
        return makefiles
    
    def _is_valid_makefile(self, file_path: Path) -> bool:
        """Check if file is a valid Makefile."""
        # Skip files in virtual environments and cache directories
        skip_patterns = [
            ".venv/", "__pycache__/", ".pytest_cache/", ".mypy_cache/",
            "node_modules/", ".git/", "test_backup_", "migration_"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False
        
        # Check if file contains Makefile syntax
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Look for Makefile patterns
                return any(pattern in content for pattern in [
                    ":", "##", "PHONY", "ifeq", "ifneq", "$("
                ])
        except:
            return False
    
    def parse_makefiles(self) -> Dict[str, Any]:
        """Parse all discovered Makefiles."""
        print("🔍 Parsing Makefiles...")
        
        for makefile in self.makefiles:
            self._parse_single_makefile(makefile)
        
        print(f"📊 Parsed {len(self.targets)} targets and {len(self.variables)} variables")
        
        return {
            "targets": len(self.targets),
            "variables": len(self.variables),
            "makefiles": len(self.makefiles)
        }
    
    def _parse_single_makefile(self, makefile_path: Path):
        """Parse a single Makefile."""
        try:
            with open(makefile_path, 'r') as f:
                lines = f.readlines()
            
            current_target = None
            in_target = False
            
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse variables
                if '=' in line and not line.startswith('\t'):
                    self._parse_variable(line, makefile_path, line_num)
                
                # Parse targets
                elif ':' in line and not line.startswith('\t'):
                    if current_target:
                        self._finalize_target(current_target)
                    
                    current_target = self._parse_target(line, makefile_path, line_num)
                    in_target = True
                
                # Parse commands (lines starting with tab)
                elif line.startswith('\t') and current_target:
                    command = line[1:]  # Remove leading tab
                    current_target.commands.append(command)
            
            # Finalize last target
            if current_target:
                self._finalize_target(current_target)
                
        except Exception as e:
            print(f"⚠️  Error parsing {makefile_path}: {e}")
    
    def _parse_variable(self, line: str, file_path: Path, line_num: int):
        """Parse a variable definition."""
        # Handle different assignment types
        if '?=' in line:
            name, value = line.split('?=', 1)
            assignment_type = "conditional"
        elif ':=' in line:
            name, value = line.split(':=', 1)
            assignment_type = "immediate"
        elif '+=' in line:
            name, value = line.split('+=', 1)
            assignment_type = "append"
        elif '=' in line:
            name, value = line.split('=', 1)
            assignment_type = "recursive"
        else:
            return
        
        name = name.strip()
        value = value.strip()
        
        variable = MakefileVariable(
            name=name,
            value=value,
            file_path=str(file_path),
            line_number=line_num,
            scope="global"
        )
        
        self.variables[name] = variable
    
    def _parse_target(self, line: str, file_path: Path, line_num: int) -> MakefileTarget:
        """Parse a target definition."""
        # Split target and dependencies
        if ':' in line:
            target_part, deps_part = line.split(':', 1)
            target_name = target_part.strip()
            dependencies = [dep.strip() for dep in deps_part.split() if dep.strip()]
        else:
            target_name = line.strip()
            dependencies = []
        
        # Check if it's a PHONY target
        phony = target_name in ['.PHONY', '.DEFAULT_GOAL']
        
        # Extract description from comments
        description = ""
        if '##' in line:
            description = line.split('##', 1)[1].strip()
        
        # Determine category
        category = self._categorize_target(target_name)
        
        # Determine priority
        priority = self._calculate_priority(target_name, category)
        
        target = MakefileTarget(
            name=target_name,
            dependencies=dependencies,
            description=description,
            phony=phony,
            file_path=str(file_path),
            line_number=line_num,
            category=category,
            priority=priority
        )
        
        return target
    
    def _categorize_target(self, target_name: str) -> str:
        """Categorize a target based on its name."""
        target_lower = target_name.lower()
        
        for category, keywords in self.target_categories.items():
            for keyword in keywords:
                if keyword in target_lower:
                    return category
        
        return "general"
    
    def _calculate_priority(self, target_name: str, category: str) -> int:
        """Calculate priority for a target."""
        priority_map = {
            "build": 10,
            "test": 9,
            "clean": 8,
            "install": 7,
            "dev": 6,
            "docs": 5,
            "release": 4,
            "quality": 3,
            "integration": 2,
            "security": 1,
            "performance": 1,
            "migration": 1,
            "interface": 1,
            "beast_mode": 1,
            "rdi": 1,
            "rm_ddd": 1,
            "general": 0
        }
        
        return priority_map.get(category, 0)
    
    def _finalize_target(self, target: MakefileTarget):
        """Finalize a target and add it to the registry."""
        if target.name and not target.phony:
            self.targets[target.name] = target
    
    def generate_projections(self) -> Dict[str, MakefileProjection]:
        """Generate various projections of the Makefile system."""
        print("🎯 Generating Makefile projections...")
        
        # Category-based projection
        self._generate_category_projection()
        
        # Priority-based projection
        self._generate_priority_projection()
        
        # File-based projection
        self._generate_file_projection()
        
        # Dependency-based projection
        self._generate_dependency_projection()
        
        # Beast Mode projection
        self._generate_beast_mode_projection()
        
        # RDI projection
        self._generate_rdi_projection()
        
        # RM-DDD projection
        self._generate_rm_ddd_projection()
        
        print(f"📊 Generated {len(self.projections)} projections")
        
        return self.projections
    
    def _generate_category_projection(self):
        """Generate category-based projection."""
        categories = {}
        for target in self.targets.values():
            if target.category not in categories:
                categories[target.category] = []
            categories[target.category].append(target.name)
        
        projection = MakefileProjection(
            name="category_based",
            description="Targets organized by functional category",
            targets=list(self.targets.keys()),
            categories=categories
        )
        
        self.projections["category_based"] = projection
    
    def _generate_priority_projection(self):
        """Generate priority-based projection."""
        priority_groups = {}
        for target in self.targets.values():
            if target.priority not in priority_groups:
                priority_groups[target.priority] = []
            priority_groups[target.priority].append(target.name)
        
        projection = MakefileProjection(
            name="priority_based",
            description="Targets organized by execution priority",
            targets=list(self.targets.keys()),
            categories=priority_groups
        )
        
        self.projections["priority_based"] = projection
    
    def _generate_file_projection(self):
        """Generate file-based projection."""
        file_groups = {}
        for target in self.targets.values():
            file_path = target.file_path
            if file_path not in file_groups:
                file_groups[file_path] = []
            file_groups[file_path].append(target.name)
        
        projection = MakefileProjection(
            name="file_based",
            description="Targets organized by source Makefile",
            targets=list(self.targets.keys()),
            categories=file_groups
        )
        
        self.projections["file_based"] = projection
    
    def _generate_dependency_projection(self):
        """Generate dependency-based projection."""
        dependencies = {}
        for target in self.targets.values():
            dependencies[target.name] = target.dependencies
        
        projection = MakefileProjection(
            name="dependency_based",
            description="Targets organized by dependency relationships",
            targets=list(self.targets.keys()),
            dependencies=dependencies
        )
        
        self.projections["dependency_based"] = projection
    
    def _generate_beast_mode_projection(self):
        """Generate Beast Mode specific projection."""
        beast_mode_targets = []
        for target in self.targets.values():
            if any(keyword in target.name.lower() for keyword in ["beast", "systematic", "pdca"]):
                beast_mode_targets.append(target.name)
        
        projection = MakefileProjection(
            name="beast_mode",
            description="Beast Mode Framework specific targets",
            targets=beast_mode_targets
        )
        
        self.projections["beast_mode"] = projection
    
    def _generate_rdi_projection(self):
        """Generate RDI specific projection."""
        rdi_targets = []
        for target in self.targets.values():
            if any(keyword in target.name.lower() for keyword in ["rdi", "registry", "interface"]):
                rdi_targets.append(target.name)
        
        projection = MakefileProjection(
            name="rdi",
            description="Registry-Driven Interface specific targets",
            targets=rdi_targets
        )
        
        self.projections["rdi"] = projection
    
    def _generate_rm_ddd_projection(self):
        """Generate RM-DDD specific projection."""
        rm_ddd_targets = []
        for target in self.targets.values():
            if any(keyword in target.name.lower() for keyword in ["rm-ddd", "reflective", "domain", "ddd"]):
                rm_ddd_targets.append(target.name)
        
        projection = MakefileProjection(
            name="rm_ddd",
            description="Reflective Module - Domain-Driven Design specific targets",
            targets=rm_ddd_targets
        )
        
        self.projections["rm_ddd"] = projection
    
    def generate_unified_makefile(self) -> str:
        """Generate a unified Makefile from all discovered Makefiles."""
        print("🔧 Generating unified Makefile...")
        
        makefile_content = []
        
        # Header
        makefile_content.append("# 🚨 UNIFIED MAKEFILE SYSTEM 🚨")
        makefile_content.append("# Generated from all Makefiles in the repository")
        makefile_content.append("# Beast Mode Framework - Systematic Build Orchestration")
        makefile_content.append("")
        
        # PHONY declarations
        phony_targets = [target.name for target in self.targets.values() if target.phony]
        if phony_targets:
            makefile_content.append(".PHONY: " + " ".join(phony_targets))
            makefile_content.append("")
        
        # Default goal
        if "help" in self.targets:
            makefile_content.append(".DEFAULT_GOAL := help")
            makefile_content.append("")
        
        # Variables
        if self.variables:
            makefile_content.append("# Variables")
            for var in self.variables.values():
                makefile_content.append(f"{var.name} := {var.value}")
            makefile_content.append("")
        
        # Targets organized by category
        for category in sorted(self.target_categories.keys()):
            category_targets = [target for target in self.targets.values() if target.category == category]
            if category_targets:
                makefile_content.append(f"# {category.upper()} TARGETS")
                makefile_content.append("")
                
                for target in sorted(category_targets, key=lambda t: t.priority, reverse=True):
                    # Target definition
                    deps = " ".join(target.dependencies) if target.dependencies else ""
                    target_line = f"{target.name}: {deps}".rstrip()
                    makefile_content.append(target_line)
                    
                    # Description
                    if target.description:
                        makefile_content.append(f"\t@echo \"{target.description}\"")
                    
                    # Commands
                    for command in target.commands:
                        makefile_content.append(f"\t{command}")
                    
                    makefile_content.append("")
        
        return "\n".join(makefile_content)
    
    def generate_makefile_documentation(self) -> str:
        """Generate comprehensive Makefile documentation."""
        print("📚 Generating Makefile documentation...")
        
        doc_content = []
        
        # Header
        doc_content.append("# Makefile System Documentation")
        doc_content.append("")
        doc_content.append("## Overview")
        doc_content.append("")
        doc_content.append("This document provides comprehensive documentation for the Makefile system.")
        doc_content.append("")
        
        # Statistics
        doc_content.append("## System Statistics")
        doc_content.append("")
        doc_content.append(f"- **Total Makefiles:** {len(self.makefiles)}")
        doc_content.append(f"- **Total Targets:** {len(self.targets)}")
        doc_content.append(f"- **Total Variables:** {len(self.variables)}")
        doc_content.append(f"- **Total Projections:** {len(self.projections)}")
        doc_content.append("")
        
        # Makefiles
        doc_content.append("## Discovered Makefiles")
        doc_content.append("")
        for makefile in self.makefiles:
            doc_content.append(f"- `{makefile.relative_to(self.repository_root)}`")
        doc_content.append("")
        
        # Targets by category
        doc_content.append("## Targets by Category")
        doc_content.append("")
        for category in sorted(self.target_categories.keys()):
            category_targets = [target for target in self.targets.values() if target.category == category]
            if category_targets:
                doc_content.append(f"### {category.title()}")
                doc_content.append("")
                for target in sorted(category_targets, key=lambda t: t.priority, reverse=True):
                    doc_content.append(f"- **{target.name}** - {target.description or 'No description'}")
                    if target.dependencies:
                        doc_content.append(f"  - Dependencies: {', '.join(target.dependencies)}")
                    doc_content.append(f"  - Priority: {target.priority}")
                    doc_content.append(f"  - Source: `{target.file_path}`")
                    doc_content.append("")
        
        # Projections
        doc_content.append("## System Projections")
        doc_content.append("")
        for projection_name, projection in self.projections.items():
            doc_content.append(f"### {projection_name.replace('_', ' ').title()}")
            doc_content.append("")
            doc_content.append(projection.description)
            doc_content.append("")
            if projection.targets:
                doc_content.append("**Targets:**")
                for target_name in projection.targets:
                    doc_content.append(f"- {target_name}")
                doc_content.append("")
        
        return "\n".join(doc_content)
    
    def save_model(self, output_dir: Path = None):
        """Save the complete Makefile system model."""
        if output_dir is None:
            output_dir = self.repository_root / "makefile_system"
        
        output_dir.mkdir(exist_ok=True)
        
        # Save targets
        targets_file = output_dir / "targets.json"
        with open(targets_file, 'w') as f:
            json.dump({
                name: {
                    "name": target.name,
                    "dependencies": target.dependencies,
                    "commands": target.commands,
                    "description": target.description,
                    "phony": target.phony,
                    "file_path": target.file_path,
                    "line_number": target.line_number,
                    "category": target.category,
                    "priority": target.priority
                }
                for name, target in self.targets.items()
            }, f, indent=2)
        
        # Save variables
        variables_file = output_dir / "variables.json"
        with open(variables_file, 'w') as f:
            json.dump({
                name: {
                    "name": var.name,
                    "value": var.value,
                    "file_path": var.file_path,
                    "line_number": var.line_number,
                    "scope": var.scope
                }
                for name, var in self.variables.items()
            }, f, indent=2)
        
        # Save projections
        projections_file = output_dir / "projections.json"
        with open(projections_file, 'w') as f:
            json.dump({
                name: {
                    "name": proj.name,
                    "description": proj.description,
                    "targets": proj.targets,
                    "variables": proj.variables,
                    "dependencies": proj.dependencies,
                    "categories": proj.categories
                }
                for name, proj in self.projections.items()
            }, f, indent=2)
        
        # Generate unified Makefile
        unified_makefile = output_dir / "Makefile.unified"
        with open(unified_makefile, 'w') as f:
            f.write(self.generate_unified_makefile())
        
        # Generate documentation
        doc_file = output_dir / "README.md"
        with open(doc_file, 'w') as f:
            f.write(self.generate_makefile_documentation())
        
        print(f"📁 Makefile system model saved to: {output_dir}")
        
        return output_dir

def main():
    """Run Makefile system modeling."""
    print("🚨 MAKEFILE SYSTEM MODEL INITIATED! 🚨")
    print("This is it! The moment we should have trained for!")
    print()
    
    # Initialize Makefile system model
    model = MakefileSystemModel()
    
    try:
        # Discover Makefiles
        makefiles = model.discover_makefiles()
        
        # Parse Makefiles
        parse_results = model.parse_makefiles()
        
        # Generate projections
        projections = model.generate_projections()
        
        # Save model
        output_dir = model.save_model()
        
        print(f"\n✅ Makefile system modeling completed!")
        print(f"📊 Makefiles discovered: {len(makefiles)}")
        print(f"📊 Targets parsed: {parse_results['targets']}")
        print(f"📊 Variables parsed: {parse_results['variables']}")
        print(f"📊 Projections generated: {len(projections)}")
        print(f"📁 Model saved to: {output_dir}")
        
    except Exception as e:
        print(f"❌ Makefile system modeling failed: {e}")

if __name__ == "__main__":
    main()


