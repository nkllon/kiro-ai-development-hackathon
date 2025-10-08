#!/usr/bin/env python3
"""
Makefile Target Generator
=========================

Automated target generation system for comprehensive Makefile creation.
Generates dynamic targets based on discovered system capabilities.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Dynamic Makefile target generation and organization
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from scripts.makefile_system_discovery import MakefileSystemDiscovery, SystemType, DiscoveredScript, DiscoveredService


class TargetCategory(Enum):
    """Target categories for organization."""
    OBSERVATORY = "observatory"
    BEAST_MODE = "beast_mode"
    DAG_ORCHESTRATION = "dag_orchestration"
    INFRASTRUCTURE = "infrastructure"
    DEVELOPMENT = "development"
    TESTING = "testing"
    GOVERNANCE = "governance"
    MAINTENANCE = "maintenance"


@dataclass
class GeneratedTarget:
    """Represents a generated Makefile target."""
    name: str
    category: TargetCategory
    description: str
    commands: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    phony: bool = True
    script_path: Optional[str] = None
    service_name: Optional[str] = None
    priority: int = 1


class MakefileTargetGenerator(ReflectiveModule):
    """
    🎯 MAKEFILE TARGET GENERATOR 🎯
    
    Automated target generation system for comprehensive Makefile creation.
    Generates dynamic targets based on discovered system capabilities.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "makefile_target_generator"
        self.repository_root = Path(repository_root)
        
        # Initialize discovery engine
        self.discovery = MakefileSystemDiscovery(repository_root)
        
        # Generated targets storage
        self.generated_targets: Dict[str, GeneratedTarget] = {}
        
        # Target templates
        self.target_templates = self._initialize_target_templates()
        
        # Category mappings
        self.category_mappings = {
            SystemType.OBSERVATORY: TargetCategory.OBSERVATORY,
            SystemType.BEAST_MODE: TargetCategory.BEAST_MODE,
            SystemType.DAG_ORCHESTRATION: TargetCategory.DAG_ORCHESTRATION,
            SystemType.INFRASTRUCTURE: TargetCategory.INFRASTRUCTURE,
            SystemType.DEVELOPMENT: TargetCategory.DEVELOPMENT,
            SystemType.TESTING: TargetCategory.TESTING,
            SystemType.GOVERNANCE: TargetCategory.GOVERNANCE,
            SystemType.INTEGRATION: TargetCategory.INFRASTRUCTURE
        }
    
    def _initialize_target_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize target generation templates."""
        return {
            "script_execution": {
                "command_template": "python {script_path}",
                "description_template": "{description}",
                "phony": True
            },
            "service_management": {
                "start": {
                    "command_template": "python scripts/start_{service}.py",
                    "description_template": "Start {service} service",
                    "phony": True
                },
                "stop": {
                    "command_template": "python scripts/stop_{service}.py",
                    "description_template": "Stop {service} service",
                    "phony": True
                },
                "status": {
                    "command_template": "python scripts/check_{service}_status.py",
                    "description_template": "Check {service} status",
                    "phony": True
                },
                "health": {
                    "command_template": "curl -s http://localhost:{port}/health || echo '{service} not responding'",
                    "description_template": "Check {service} health",
                    "phony": True
                },
                "logs": {
                    "command_template": "python scripts/view_{service}_logs.py",
                    "description_template": "View {service} logs",
                    "phony": True
                }
            },
            "testing": {
                "test": {
                    "command_template": "python -m pytest tests/{test_path} -v",
                    "description_template": "Run {component} tests",
                    "phony": True
                },
                "test_coverage": {
                    "command_template": "python -m pytest tests/{test_path} --cov={module} --cov-report=html",
                    "description_template": "Run {component} tests with coverage",
                    "phony": True
                }
            },
            "development": {
                "lint": {
                    "command_template": "python scripts/lint_{component}.py",
                    "description_template": "Lint {component} code",
                    "phony": True
                },
                "format": {
                    "command_template": "python scripts/format_{component}.py",
                    "description_template": "Format {component} code",
                    "phony": True
                },
                "validate": {
                    "command_template": "python scripts/validate_{component}.py",
                    "description_template": "Validate {component}",
                    "phony": True
                }
            }
        }
    
    def generate_all_targets(self) -> Dict[str, GeneratedTarget]:
        """Generate all targets based on discovered systems."""
        self._logger.info("🎯 Generating comprehensive target system...")
        
        # Discover system capabilities
        discovered_systems = self.discovery.discover_all_systems()
        
        # Generate targets for each system type
        for system_type, capabilities in discovered_systems.items():
            if capabilities.scripts or capabilities.services:
                self._generate_system_targets(system_type, capabilities)
        
        # Generate meta targets
        self._generate_meta_targets()
        
        # Generate help system
        self._generate_help_targets()
        
        self._logger.info(f"✅ Generated {len(self.generated_targets)} targets")
        return self.generated_targets
    
    def _generate_system_targets(self, system_type: SystemType, capabilities):
        """Generate targets for a specific system type."""
        category = self.category_mappings.get(system_type, TargetCategory.DEVELOPMENT)
        
        # Generate script-based targets
        for script in capabilities.scripts:
            self._generate_script_targets(script, category)
        
        # Generate service-based targets
        for service in capabilities.services:
            self._generate_service_targets(service, category)
        
        # Generate system-level targets
        self._generate_system_level_targets(system_type, category, capabilities)
    
    def _generate_script_targets(self, script: DiscoveredScript, category: TargetCategory):
        """Generate targets for a discovered script."""
        script_name = script.name.replace('_', '-')
        
        # Main execution target
        target_name = f"{category.value}-{script_name}"
        if script_name.startswith(category.value.replace('_', '-')):
            target_name = script_name
        
        target = GeneratedTarget(
            name=target_name,
            category=category,
            description=script.description or f"Execute {script.name}",
            commands=[f"python {script.path}"],
            phony=True,
            script_path=str(script.path),
            priority=self._calculate_script_priority(script)
        )
        
        self.generated_targets[target_name] = target
        
        # Generate capability-specific targets
        for capability in script.capabilities:
            cap_target_name = f"{category.value}-{capability}"
            if cap_target_name not in self.generated_targets:
                cap_target = GeneratedTarget(
                    name=cap_target_name,
                    category=category,
                    description=f"{capability.title()} {category.value} components",
                    commands=[f"python {script.path}"],
                    phony=True,
                    priority=2
                )
                self.generated_targets[cap_target_name] = cap_target
    
    def _generate_service_targets(self, service: DiscoveredService, category: TargetCategory):
        """Generate targets for a discovered service."""
        service_name = service.name.replace('_', '-')
        
        # Service management targets
        management_actions = ["start", "stop", "restart", "status", "health"]
        
        for action in management_actions:
            target_name = f"{category.value}-{service_name}-{action}"
            
            # Generate appropriate command based on action
            if action == "start":
                commands = [f"python scripts/start_{service.name}.py || echo 'Starting {service.name}...'"]
            elif action == "stop":
                commands = [f"python scripts/stop_{service.name}.py || echo 'Stopping {service.name}...'"]
            elif action == "restart":
                commands = [
                    f"python scripts/stop_{service.name}.py || true",
                    f"sleep 2",
                    f"python scripts/start_{service.name}.py || echo 'Restarting {service.name}...'"
                ]
            elif action == "status":
                if service.port:
                    commands = [f"curl -s http://localhost:{service.port}/status || echo '{service.name} status unknown'"]
                else:
                    commands = [f"python scripts/check_{service.name}_status.py || echo '{service.name} status unknown'"]
            elif action == "health":
                if service.port and service.health_endpoint:
                    commands = [f"curl -s http://localhost:{service.port}{service.health_endpoint} || echo '{service.name} health check failed'"]
                else:
                    commands = [f"python scripts/health_check_{service.name}.py || echo '{service.name} health unknown'"]
            
            target = GeneratedTarget(
                name=target_name,
                category=category,
                description=f"{action.title()} {service.name} service",
                commands=commands,
                phony=True,
                service_name=service.name,
                priority=1 if action in ["start", "stop"] else 2
            )
            
            self.generated_targets[target_name] = target
    
    def _generate_system_level_targets(self, system_type: SystemType, category: TargetCategory, capabilities):
        """Generate system-level aggregate targets."""
        system_name = system_type.value.replace('_', '-')
        
        # System-wide operations
        operations = {
            "deploy": f"Deploy all {system_name} components",
            "test": f"Test all {system_name} components", 
            "validate": f"Validate {system_name} system",
            "clean": f"Clean {system_name} artifacts",
            "status": f"Check {system_name} system status"
        }
        
        for operation, description in operations.items():
            target_name = f"{system_name}-{operation}"
            
            # Collect relevant scripts for this operation
            relevant_scripts = [
                script for script in capabilities.scripts
                if operation in script.capabilities or operation in script.name.lower()
            ]
            
            commands = []
            if relevant_scripts:
                for script in relevant_scripts:
                    commands.append(f"python {script.path}")
            else:
                # Generate generic command
                commands.append(f"@echo '{description}' && echo 'No specific scripts found for {operation}'")
            
            target = GeneratedTarget(
                name=target_name,
                category=category,
                description=description,
                commands=commands,
                phony=True,
                priority=1
            )
            
            self.generated_targets[target_name] = target
    
    def _generate_meta_targets(self):
        """Generate meta targets that operate across categories."""
        meta_targets = {
            "discover-system": GeneratedTarget(
                name="discover-system",
                category=TargetCategory.DEVELOPMENT,
                description="Discover all system capabilities",
                commands=["python scripts/makefile_system_discovery.py --verbose"],
                phony=True,
                priority=1
            ),
            "validate-safety": GeneratedTarget(
                name="validate-safety",
                category=TargetCategory.DEVELOPMENT,
                description="Validate system safety",
                commands=["python scripts/makefile_safety_validator.py system"],
                phony=True,
                priority=1
            ),
            "optimize-performance": GeneratedTarget(
                name="optimize-performance",
                category=TargetCategory.DEVELOPMENT,
                description="Optimize system performance",
                commands=["python scripts/makefile_performance_optimizer.py --report"],
                phony=True,
                priority=2
            ),
            "test-system": GeneratedTarget(
                name="test-system",
                category=TargetCategory.TESTING,
                description="Run comprehensive system tests",
                commands=["python scripts/test_makefile_system.py"],
                phony=True,
                priority=1
            ),
            "validate-targets": GeneratedTarget(
                name="validate-targets",
                category=TargetCategory.TESTING,
                description="Validate all Makefile targets",
                commands=["python scripts/validate_makefile_targets.py"],
                phony=True,
                priority=1
            ),
            "lint-makefiles": GeneratedTarget(
                name="lint-makefiles",
                category=TargetCategory.DEVELOPMENT,
                description="Lint all Makefiles",
                commands=["python scripts/lint_makefile.py"],
                phony=True,
                priority=2
            ),
            "generate-reports": GeneratedTarget(
                name="generate-reports",
                category=TargetCategory.DEVELOPMENT,
                description="Generate all system reports",
                commands=[
                    "python scripts/makefile_system_discovery.py --output reports/discovery.json",
                    "python scripts/test_makefile_system.py --report reports/test_results.json",
                    "python scripts/validate_makefile_targets.py --report reports/validation.json",
                    "python scripts/lint_makefile.py --report reports/lint.json"
                ],
                phony=True,
                priority=2
            )
        }
        
        self.generated_targets.update(meta_targets)
    
    def _generate_help_targets(self):
        """Generate comprehensive help system."""
        # Main help target
        help_commands = ["@echo 'Comprehensive Makefile System - Available Targets:'", "@echo ''"]
        
        # Group targets by category
        by_category = {}
        for target in self.generated_targets.values():
            if target.category not in by_category:
                by_category[target.category] = []
            by_category[target.category].append(target)
        
        # Generate help output for each category
        for category, targets in by_category.items():
            help_commands.append(f"@echo '{category.value.replace('_', ' ').title()} Targets:'")
            
            # Sort targets by priority and name
            sorted_targets = sorted(targets, key=lambda t: (t.priority, t.name))
            
            for target in sorted_targets[:5]:  # Show top 5 targets per category
                help_commands.append(f"@echo '  make {target.name:<20} - {target.description}'")
            
            if len(targets) > 5:
                help_commands.append(f"@echo '  ... and {len(targets) - 5} more {category.value} targets'")
            
            help_commands.append("@echo ''")
        
        # Add usage information
        help_commands.extend([
            "@echo 'Usage Examples:'",
            "@echo '  make help                    - Show this help'",
            "@echo '  make discover-system         - Discover system capabilities'",
            "@echo '  make test-system            - Run comprehensive tests'",
            "@echo '  make validate-safety        - Validate system safety'",
            "@echo '  make generate-reports       - Generate all reports'",
            "@echo ''",
            "@echo 'For more information, see: docs/makefile_system_guide.md'"
        ])
        
        help_target = GeneratedTarget(
            name="help",
            category=TargetCategory.DEVELOPMENT,
            description="Show available targets and usage information",
            commands=help_commands,
            phony=True,
            priority=0  # Highest priority
        )
        
        self.generated_targets["help"] = help_target
        
        # Category-specific help targets
        for category in by_category:
            category_help_name = f"help-{category.value.replace('_', '-')}"
            category_targets = by_category[category]
            
            category_commands = [
                f"@echo '{category.value.replace('_', ' ').title()} Targets:'",
                "@echo ''"
            ]
            
            for target in sorted(category_targets, key=lambda t: t.name):
                category_commands.append(f"@echo '  make {target.name:<25} - {target.description}'")
            
            category_help_target = GeneratedTarget(
                name=category_help_name,
                category=category,
                description=f"Show {category.value} targets",
                commands=category_commands,
                phony=True,
                priority=3
            )
            
            self.generated_targets[category_help_name] = category_help_target
    
    def _calculate_script_priority(self, script: DiscoveredScript) -> int:
        """Calculate priority for script-based targets."""
        # Higher priority for executable scripts
        if script.executable:
            priority = 1
        else:
            priority = 2
        
        # Adjust based on capabilities
        high_priority_caps = ["start", "stop", "deploy", "test"]
        if any(cap in script.capabilities for cap in high_priority_caps):
            priority = max(1, priority - 1)
        
        return priority
    
    def generate_makefile_content(self) -> str:
        """Generate complete Makefile content."""
        if not self.generated_targets:
            self.generate_all_targets()
        
        content_lines = [
            "# Comprehensive Makefile System",
            "# Generated automatically by MakefileTargetGenerator",
            f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "# Default target",
            ".DEFAULT_GOAL := help",
            "",
            "# Phony targets declaration"
        ]
        
        # Collect all phony targets
        phony_targets = [target.name for target in self.generated_targets.values() if target.phony]
        
        # Split phony declarations into manageable lines
        phony_line = ".PHONY: "
        for target in sorted(phony_targets):
            if len(phony_line + target + " ") > 80:
                content_lines.append(phony_line.rstrip())
                phony_line = ".PHONY: " + target + " "
            else:
                phony_line += target + " "
        
        if phony_line.strip() != ".PHONY:":
            content_lines.append(phony_line.rstrip())
        
        content_lines.append("")
        
        # Generate targets by category
        by_category = {}
        for target in self.generated_targets.values():
            if target.category not in by_category:
                by_category[target.category] = []
            by_category[target.category].append(target)
        
        # Sort categories for logical organization
        category_order = [
            TargetCategory.DEVELOPMENT,
            TargetCategory.TESTING,
            TargetCategory.OBSERVATORY,
            TargetCategory.BEAST_MODE,
            TargetCategory.DAG_ORCHESTRATION,
            TargetCategory.INFRASTRUCTURE,
            TargetCategory.GOVERNANCE,
            TargetCategory.MAINTENANCE
        ]
        
        for category in category_order:
            if category in by_category:
                content_lines.extend([
                    f"# {category.value.replace('_', ' ').title()} Targets",
                    "# " + "=" * 50,
                    ""
                ])
                
                # Sort targets within category
                targets = sorted(by_category[category], key=lambda t: (t.priority, t.name))
                
                for target in targets:
                    # Target definition with description
                    target_line = f"{target.name}: "
                    if target.dependencies:
                        target_line += " ".join(target.dependencies)
                    target_line += f" ## {target.description}"
                    
                    content_lines.append(target_line)
                    
                    # Target commands
                    for command in target.commands:
                        content_lines.append(f"\t{command}")
                    
                    content_lines.append("")
        
        return "\n".join(content_lines)
    
    def save_generated_makefile(self, output_path: Optional[Path] = None) -> Path:
        """Save generated Makefile content."""
        if output_path is None:
            output_path = self.repository_root / "Makefile.generated"
        
        content = self.generate_makefile_content()
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        self._logger.info(f"📄 Generated Makefile saved: {output_path}")
        return output_path
    
    def save_modular_targets(self, output_dir: Optional[Path] = None) -> Path:
        """Save targets as modular include files."""
        if output_dir is None:
            output_dir = self.repository_root / ".make-tasks"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Group targets by category and save separately
        by_category = {}
        for target in self.generated_targets.values():
            if target.category not in by_category:
                by_category[target.category] = []
            by_category[target.category].append(target)
        
        generated_files = []
        
        for category, targets in by_category.items():
            category_file = output_dir / f"{category.value}.mk"
            
            content_lines = [
                f"# {category.value.replace('_', ' ').title()} Targets",
                f"# Generated automatically by MakefileTargetGenerator",
                f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "# Phony targets for this category"
            ]
            
            # Phony targets for this category
            phony_targets = [t.name for t in targets if t.phony]
            if phony_targets:
                content_lines.append(f".PHONY: {' '.join(sorted(phony_targets))}")
                content_lines.append("")
            
            # Generate targets
            sorted_targets = sorted(targets, key=lambda t: (t.priority, t.name))
            
            for target in sorted_targets:
                target_line = f"{target.name}:"
                if target.dependencies:
                    target_line += " " + " ".join(target.dependencies)
                target_line += f" ## {target.description}"
                
                content_lines.append(target_line)
                
                for command in target.commands:
                    content_lines.append(f"\t{command}")
                
                content_lines.append("")
            
            with open(category_file, 'w') as f:
                f.write("\n".join(content_lines))
            
            generated_files.append(category_file)
        
        # Create master include file
        master_file = output_dir / "generated-targets.mk"
        master_content = [
            "# Generated Targets Master Include",
            f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "# Include all category-specific target files"
        ]
        
        for category in by_category:
            master_content.append(f"include .make-tasks/{category.value}.mk")
        
        with open(master_file, 'w') as f:
            f.write("\n".join(master_content))
        
        generated_files.append(master_file)
        
        self._logger.info(f"📁 Generated {len(generated_files)} modular target files in {output_dir}")
        return output_dir
    
    def generate_target_report(self, output_file: Optional[Path] = None) -> Path:
        """Generate comprehensive target generation report."""
        if output_file is None:
            output_file = self.repository_root / "reports" / "target_generation.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.generated_targets:
            self.generate_all_targets()
        
        # Group targets by category for analysis
        by_category = {}
        for target in self.generated_targets.values():
            if target.category not in by_category:
                by_category[target.category] = []
            by_category[target.category].append(target)
        
        report = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "summary": {
                "total_targets": len(self.generated_targets),
                "categories": len(by_category),
                "phony_targets": len([t for t in self.generated_targets.values() if t.phony]),
                "script_based_targets": len([t for t in self.generated_targets.values() if t.script_path]),
                "service_based_targets": len([t for t in self.generated_targets.values() if t.service_name])
            },
            "by_category": {
                category.value: {
                    "count": len(targets),
                    "targets": [
                        {
                            "name": target.name,
                            "description": target.description,
                            "commands": len(target.commands),
                            "dependencies": target.dependencies,
                            "priority": target.priority,
                            "script_path": target.script_path,
                            "service_name": target.service_name
                        }
                        for target in sorted(targets, key=lambda t: t.name)
                    ]
                }
                for category, targets in by_category.items()
            },
            "generation_stats": {
                "discovery_systems": len(self.discovery.discovered_systems),
                "discovered_scripts": len(self.discovery.all_scripts),
                "discovered_services": len(self.discovery.all_services)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self._logger.info(f"📊 Target generation report saved: {output_file}")
        return output_file
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["target_generation", "system_discovery", "makefile_creation"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Makefile Target Generator",
            "version": "1.0.0",
            "description": "Automated target generation system for comprehensive Makefile creation"
        }
    
    def get_health_status(self):
        """Get module health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleStatus, HealthStatus
        return HealthStatus(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            last_check=time.strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation."""
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_target_generation"
        }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile Target Generator")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--output", help="Output Makefile path")
    parser.add_argument("--modular", action="store_true", help="Generate modular target files")
    parser.add_argument("--report", help="Generate target report to file")
    parser.add_argument("--preview", action="store_true", help="Preview generated targets")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create generator
    generator = MakefileTargetGenerator(args.root)
    
    # Generate targets
    targets = generator.generate_all_targets()
    
    print(f"\n🎯 TARGET GENERATION COMPLETE")
    print(f"Total targets generated: {len(targets)}")
    
    # Group by category for summary
    by_category = {}
    for target in targets.values():
        if target.category not in by_category:
            by_category[target.category] = 0
        by_category[target.category] += 1
    
    print("\nTargets by category:")
    for category, count in sorted(by_category.items(), key=lambda x: x[0].value):
        print(f"  {category.value.replace('_', ' ').title()}: {count}")
    
    # Preview targets if requested
    if args.preview:
        print(f"\n📋 TARGET PREVIEW (first 10 targets):")
        for i, (name, target) in enumerate(list(targets.items())[:10]):
            print(f"  {name}: {target.description}")
        
        if len(targets) > 10:
            print(f"  ... and {len(targets) - 10} more targets")
    
    # Save outputs
    if args.output:
        output_path = generator.save_generated_makefile(Path(args.output))
        print(f"\n📄 Makefile saved: {output_path}")
    
    if args.modular:
        modular_dir = generator.save_modular_targets()
        print(f"\n📁 Modular targets saved: {modular_dir}")
    
    if args.report:
        report_path = generator.generate_target_report(Path(args.report))
        print(f"\n📊 Target report saved: {report_path}")


if __name__ == "__main__":
    main()