#!/usr/bin/env python3
"""
Beast Mode Integration Module
=============================

Integration module for Beast Mode Framework with Makefile governance.
Provides Beast Mode-specific targets and systematic operations.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Beast Mode framework integration for Makefile governance
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class BeastModeComponent(Enum):
    """Beast Mode framework components."""
    CORE = "core"
    ANALYSIS = "analysis"
    ASSESSMENT = "assessment"
    AUTONOMOUS = "autonomous"
    EXECUTION = "execution"
    GHOSTBUSTERS = "ghostbusters"
    ORCHESTRATION = "orchestration"
    QUALITY = "quality"
    TESTING = "testing"
    VALIDATION = "validation"


@dataclass
class ComponentConfig:
    """Beast Mode component configuration."""
    name: str
    path: Path
    test_path: Optional[Path] = None
    config_file: Optional[str] = None
    main_script: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


class BeastModeIntegration(ReflectiveModule):
    """
    🐺 BEAST MODE INTEGRATION MODULE 🐺
    
    Integration module for Beast Mode Framework with Makefile governance.
    Provides systematic operations and quality assurance targets.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "beast_mode_integration"
        self.repository_root = Path(repository_root)
        
        # Beast Mode paths
        self.beast_mode_dir = self.repository_root / "src" / "beast_mode"
        self.scripts_dir = self.repository_root / "scripts"
        self.tests_dir = self.repository_root / "tests"
        
        # Component configurations
        self.components = self._initialize_component_configs()
    
    def _initialize_component_configs(self) -> Dict[BeastModeComponent, ComponentConfig]:
        """Initialize Beast Mode component configurations."""
        return {
            BeastModeComponent.CORE: ComponentConfig(
                name="core",
                path=self.beast_mode_dir / "core",
                test_path=self.tests_dir / "unit" / "beast_mode" / "core",
                main_script="reflective_module.py"
            ),
            BeastModeComponent.ANALYSIS: ComponentConfig(
                name="analysis",
                path=self.beast_mode_dir / "analysis",
                test_path=self.tests_dir / "unit" / "beast_mode" / "analysis",
                main_script="failure_analysis.py"
            ),
            BeastModeComponent.ASSESSMENT: ComponentConfig(
                name="assessment",
                path=self.beast_mode_dir / "assessment",
                test_path=self.tests_dir / "unit" / "beast_mode" / "assessment",
                main_script="production_readiness.py"
            ),
            BeastModeComponent.AUTONOMOUS: ComponentConfig(
                name="autonomous",
                path=self.beast_mode_dir / "autonomous",
                test_path=self.tests_dir / "unit" / "beast_mode" / "autonomous",
                main_script="self_managing.py"
            ),
            BeastModeComponent.EXECUTION: ComponentConfig(
                name="execution",
                path=self.beast_mode_dir / "execution",
                test_path=self.tests_dir / "unit" / "beast_mode" / "execution",
                main_script="task_execution.py"
            ),
            BeastModeComponent.GHOSTBUSTERS: ComponentConfig(
                name="ghostbusters",
                path=self.beast_mode_dir / "ghostbusters",
                test_path=self.tests_dir / "unit" / "beast_mode" / "ghostbusters",
                main_script="agent_framework.py"
            ),
            BeastModeComponent.ORCHESTRATION: ComponentConfig(
                name="orchestration",
                path=self.beast_mode_dir / "orchestration",
                test_path=self.tests_dir / "unit" / "beast_mode" / "orchestration",
                main_script="workflow_orchestration.py"
            ),
            BeastModeComponent.QUALITY: ComponentConfig(
                name="quality",
                path=self.beast_mode_dir / "quality",
                test_path=self.tests_dir / "unit" / "beast_mode" / "quality",
                main_script="quality_gates.py"
            ),
            BeastModeComponent.TESTING: ComponentConfig(
                name="testing",
                path=self.beast_mode_dir / "testing",
                test_path=self.tests_dir / "unit" / "beast_mode" / "testing",
                main_script="test_framework.py"
            ),
            BeastModeComponent.VALIDATION: ComponentConfig(
                name="validation",
                path=self.beast_mode_dir / "validation",
                test_path=self.tests_dir / "unit" / "beast_mode" / "validation",
                main_script="validation_engine.py"
            )
        }
    
    def generate_beast_mode_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate Beast Mode-specific Makefile targets."""
        targets = {}
        
        # Component-specific targets
        for component_type, config in self.components.items():
            component_targets = self._generate_component_targets(component_type, config)
            targets.update(component_targets)
        
        # System-level targets
        system_targets = self._generate_system_targets()
        targets.update(system_targets)
        
        # Quality assurance targets
        quality_targets = self._generate_quality_targets()
        targets.update(quality_targets)
        
        # Systematic operation targets
        systematic_targets = self._generate_systematic_targets()
        targets.update(systematic_targets)
        
        return targets
    
    def _generate_component_targets(self, component_type: BeastModeComponent, 
                                  config: ComponentConfig) -> Dict[str, Dict[str, Any]]:
        """Generate targets for a specific Beast Mode component."""
        component_name = config.name
        targets = {}
        
        # Test component target
        if config.test_path and config.test_path.exists():
            targets[f"beast-{component_name}-test"] = {
                "description": f"Test {component_name} component",
                "commands": [
                    f"@echo '🐺 Testing {component_name} component...'",
                    f"python -m pytest {config.test_path} -v --tb=short"
                ],
                "phony": True,
                "category": "beast_mode"
            }
        
        # Validate component target
        targets[f"beast-{component_name}-validate"] = {
            "description": f"Validate {component_name} component",
            "commands": [
                f"@echo '🐺 Validating {component_name} component...'",
                f"python scripts/validate_beast_mode_component.py {component_name}",
                f"@echo '✅ {component_name} validation complete'"
            ],
            "phony": True,
            "category": "beast_mode"
        }
        
        # Lint component target
        targets[f"beast-{component_name}-lint"] = {
            "description": f"Lint {component_name} component",
            "commands": [
                f"@echo '🐺 Linting {component_name} component...'",
                f"python -m flake8 {config.path} --max-line-length=120",
                f"python -m mypy {config.path} --ignore-missing-imports",
                f"@echo '✅ {component_name} linting complete'"
            ],
            "phony": True,
            "category": "beast_mode"
        }
        
        # Format component target
        targets[f"beast-{component_name}-format"] = {
            "description": f"Format {component_name} component code",
            "commands": [
                f"@echo '🐺 Formatting {component_name} component...'",
                f"python -m black {config.path} --line-length=120",
                f"python -m isort {config.path}",
                f"@echo '✅ {component_name} formatting complete'"
            ],
            "phony": True,
            "category": "beast_mode"
        }
        
        # Component metrics target
        targets[f"beast-{component_name}-metrics"] = {
            "description": f"Generate {component_name} component metrics",
            "commands": [
                f"@echo '🐺 Generating {component_name} metrics...'",
                f"python scripts/generate_component_metrics.py {component_name}",
                f"@echo '✅ {component_name} metrics generated'"
            ],
            "phony": True,
            "category": "beast_mode"
        }
        
        return targets
    
    def _generate_system_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate system-level Beast Mode targets."""
        return {
            "beast-deploy": {
                "description": "Deploy Beast Mode framework",
                "commands": [
                    "@echo '🐺 Deploying Beast Mode framework...'",
                    "python scripts/deploy_beast_mode.py",
                    "$(MAKE) beast-validate-all",
                    "@echo '✅ Beast Mode framework deployed'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-test-all": {
                "description": "Run all Beast Mode tests",
                "commands": [
                    "@echo '🐺 Running all Beast Mode tests...'",
                    "python -m pytest tests/unit/beast_mode/ -v --tb=short",
                    "python -m pytest tests/integration/beast_mode/ -v --tb=short",
                    "@echo '✅ All Beast Mode tests complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-validate-all": {
                "description": "Validate entire Beast Mode framework",
                "commands": [
                    "@echo '🐺 Validating Beast Mode framework...'",
                    "python scripts/validate_beast_mode_framework.py",
                    "$(MAKE) beast-compliance-check",
                    "@echo '✅ Beast Mode framework validation complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-lint-all": {
                "description": "Lint all Beast Mode components",
                "commands": [
                    "@echo '🐺 Linting Beast Mode framework...'",
                    "python -m flake8 src/beast_mode/ --max-line-length=120",
                    "python -m mypy src/beast_mode/ --ignore-missing-imports",
                    "@echo '✅ Beast Mode linting complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-format-all": {
                "description": "Format all Beast Mode code",
                "commands": [
                    "@echo '🐺 Formatting Beast Mode framework...'",
                    "python -m black src/beast_mode/ --line-length=120",
                    "python -m isort src/beast_mode/",
                    "@echo '✅ Beast Mode formatting complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-status": {
                "description": "Check Beast Mode framework status",
                "commands": [
                    "@echo '🐺 Beast Mode Framework Status:'",
                    "@echo '================================'",
                    "python scripts/check_beast_mode_status.py",
                    "python scripts/check_reflective_modules.py"
                ],
                "phony": True,
                "category": "beast_mode"
            }
        }
    
    def _generate_quality_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate quality assurance targets."""
        return {
            "beast-compliance-check": {
                "description": "Run Beast Mode compliance checks",
                "commands": [
                    "@echo '🐺 Running Beast Mode compliance checks...'",
                    "python scripts/check_reflective_module_compliance.py",
                    "python scripts/check_beast_mode_patterns.py",
                    "python scripts/validate_systematic_approaches.py",
                    "@echo '✅ Compliance checks complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-quality-gates": {
                "description": "Run Beast Mode quality gates",
                "commands": [
                    "@echo '🐺 Running Beast Mode quality gates...'",
                    "python scripts/run_quality_gates.py",
                    "python scripts/check_test_coverage.py --threshold=90",
                    "python scripts/validate_documentation.py",
                    "@echo '✅ Quality gates passed'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-security-scan": {
                "description": "Run Beast Mode security scan",
                "commands": [
                    "@echo '🐺 Running Beast Mode security scan...'",
                    "python scripts/security_scan_beast_mode.py",
                    "python -m bandit -r src/beast_mode/ -f json -o reports/beast_mode_security.json",
                    "@echo '✅ Security scan complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-performance-test": {
                "description": "Run Beast Mode performance tests",
                "commands": [
                    "@echo '🐺 Running Beast Mode performance tests...'",
                    "python scripts/performance_test_beast_mode.py",
                    "python -m pytest tests/performance/beast_mode/ -v",
                    "@echo '✅ Performance tests complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-fix-issues": {
                "description": "Automatically fix Beast Mode issues",
                "commands": [
                    "@echo '🐺 Fixing Beast Mode issues...'",
                    "python scripts/auto_fix_beast_mode_issues.py",
                    "$(MAKE) beast-format-all",
                    "$(MAKE) beast-validate-all",
                    "@echo '✅ Issues fixed and validated'"
                ],
                "phony": True,
                "category": "beast_mode"
            }
        }
    
    def _generate_systematic_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate systematic operation targets."""
        return {
            "beast-systematic-analysis": {
                "description": "Run systematic analysis of codebase",
                "commands": [
                    "@echo '🐺 Running systematic analysis...'",
                    "python scripts/systematic_codebase_analysis.py",
                    "python scripts/identify_anti_patterns.py",
                    "python scripts/suggest_improvements.py",
                    "@echo '✅ Systematic analysis complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-pdca-cycle": {
                "description": "Execute PDCA (Plan-Do-Check-Act) cycle",
                "commands": [
                    "@echo '🐺 Executing PDCA cycle...'",
                    "python scripts/pdca_plan.py",
                    "python scripts/pdca_do.py",
                    "python scripts/pdca_check.py",
                    "python scripts/pdca_act.py",
                    "@echo '✅ PDCA cycle complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-refactor-systematic": {
                "description": "Systematic refactoring based on analysis",
                "commands": [
                    "@echo '🐺 Running systematic refactoring...'",
                    "python scripts/systematic_refactoring.py",
                    "$(MAKE) beast-test-all",
                    "$(MAKE) beast-validate-all",
                    "@echo '✅ Systematic refactoring complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-optimize-systematic": {
                "description": "Systematic optimization of Beast Mode components",
                "commands": [
                    "@echo '🐺 Running systematic optimization...'",
                    "python scripts/optimize_beast_mode_performance.py",
                    "python scripts/optimize_memory_usage.py",
                    "python scripts/optimize_resource_utilization.py",
                    "@echo '✅ Systematic optimization complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-documentation-sync": {
                "description": "Synchronize Beast Mode documentation",
                "commands": [
                    "@echo '🐺 Synchronizing Beast Mode documentation...'",
                    "python scripts/generate_beast_mode_docs.py",
                    "python scripts/update_api_documentation.py",
                    "python scripts/validate_documentation_consistency.py",
                    "@echo '✅ Documentation synchronization complete'"
                ],
                "phony": True,
                "category": "beast_mode"
            },
            "beast-metrics-dashboard": {
                "description": "Generate Beast Mode metrics dashboard",
                "commands": [
                    "@echo '🐺 Generating Beast Mode metrics dashboard...'",
                    "python scripts/generate_beast_mode_dashboard.py",
                    "python scripts/update_metrics_visualization.py",
                    "@echo '✅ Metrics dashboard generated'"
                ],
                "phony": True,
                "category": "beast_mode"
            }
        }
    
    def check_beast_mode_status(self) -> Dict[str, Any]:
        """Check the status of Beast Mode framework components."""
        status = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "components": {},
            "overall_status": "unknown",
            "compliance_score": 0.0
        }
        
        healthy_components = 0
        total_components = len(self.components)
        
        for component_type, config in self.components.items():
            component_status = self._check_component_status(config)
            status["components"][config.name] = component_status
            
            if component_status["healthy"]:
                healthy_components += 1
        
        # Calculate compliance score
        status["compliance_score"] = healthy_components / total_components if total_components > 0 else 0
        
        # Determine overall status
        if status["compliance_score"] >= 0.9:
            status["overall_status"] = "excellent"
        elif status["compliance_score"] >= 0.7:
            status["overall_status"] = "good"
        elif status["compliance_score"] >= 0.5:
            status["overall_status"] = "fair"
        else:
            status["overall_status"] = "needs_attention"
        
        status["healthy_components"] = healthy_components
        status["total_components"] = total_components
        
        return status
    
    def _check_component_status(self, config: ComponentConfig) -> Dict[str, Any]:
        """Check the status of a specific Beast Mode component."""
        status = {
            "name": config.name,
            "path": str(config.path),
            "exists": False,
            "healthy": False,
            "test_coverage": 0.0,
            "issues": []
        }
        
        try:
            # Check if component path exists
            status["exists"] = config.path.exists()
            
            if status["exists"]:
                # Check for Python files
                python_files = list(config.path.rglob("*.py"))
                status["python_files"] = len(python_files)
                
                # Check for tests
                if config.test_path and config.test_path.exists():
                    test_files = list(config.test_path.rglob("test_*.py"))
                    status["test_files"] = len(test_files)
                    
                    # Estimate test coverage (simplified)
                    if python_files:
                        status["test_coverage"] = min(1.0, len(test_files) / len(python_files))
                else:
                    status["test_files"] = 0
                    status["issues"].append("No test directory found")
                
                # Check for main script
                if config.main_script:
                    main_script_path = config.path / config.main_script
                    status["has_main_script"] = main_script_path.exists()
                    if not status["has_main_script"]:
                        status["issues"].append(f"Main script not found: {config.main_script}")
                
                # Determine health
                status["healthy"] = (
                    status["exists"] and
                    status.get("python_files", 0) > 0 and
                    status["test_coverage"] > 0.5 and
                    len(status["issues"]) == 0
                )
            else:
                status["issues"].append("Component directory does not exist")
        
        except Exception as e:
            status["issues"].append(f"Error checking component: {str(e)}")
        
        return status
    
    def generate_beast_mode_makefile(self, output_path: Optional[Path] = None) -> Path:
        """Generate Beast Mode-specific Makefile."""
        if output_path is None:
            output_path = self.repository_root / "makefiles" / "beast_mode.mk"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        targets = self.generate_beast_mode_targets()
        
        content_lines = [
            "# Beast Mode Framework Makefile",
            "# Generated by Beast Mode Integration Module",
            f"# Generated on: {self._get_current_timestamp()}",
            "",
            "# Beast Mode systematic operations and quality assurance targets",
            "",
            "# Phony targets"
        ]
        
        # Collect phony targets
        phony_targets = [name for name, target in targets.items() if target.get("phony", False)]
        content_lines.append(f".PHONY: {' '.join(sorted(phony_targets))}")
        content_lines.append("")
        
        # Generate targets grouped by type
        target_groups = {
            "System Operations": [name for name in targets if name.startswith("beast-") and any(x in name for x in ["deploy", "status", "test-all", "validate-all"])],
            "Component Operations": [name for name in targets if any(comp.value in name for comp in BeastModeComponent)],
            "Quality Assurance": [name for name in targets if any(x in name for x in ["compliance", "quality", "security", "performance", "fix"])],
            "Systematic Operations": [name for name in targets if any(x in name for x in ["systematic", "pdca", "refactor", "optimize", "documentation", "metrics"])]
        }
        
        for group_name, target_names in target_groups.items():
            if target_names:
                content_lines.extend([
                    f"# {group_name}",
                    "# " + "=" * len(group_name),
                    ""
                ])
                
                for target_name in sorted(target_names):
                    if target_name in targets:
                        target_config = targets[target_name]
                        
                        # Target definition
                        target_line = f"{target_name}:"
                        if target_config.get("dependencies"):
                            target_line += " " + " ".join(target_config["dependencies"])
                        target_line += f" ## {target_config['description']}"
                        
                        content_lines.append(target_line)
                        
                        # Target commands
                        for command in target_config["commands"]:
                            content_lines.append(f"\t{command}")
                        
                        content_lines.append("")
        
        with open(output_path, 'w') as f:
            f.write("\n".join(content_lines))
        
        self._logger.info(f"🐺 Beast Mode Makefile generated: {output_path}")
        return output_path
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["beast_mode_integration", "systematic_operations", "quality_assurance"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Beast Mode Integration",
            "version": "1.0.0",
            "description": "Integration module for Beast Mode Framework with Makefile governance"
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
            "fallback_mode": "basic_beast_mode_integration"
        }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Beast Mode Integration Module")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--generate-makefile", help="Generate Beast Mode Makefile")
    parser.add_argument("--status", action="store_true", help="Check Beast Mode status")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create integration module
    integration = BeastModeIntegration(args.root)
    
    if args.status:
        status = integration.check_beast_mode_status()
        print(f"\n🐺 BEAST MODE FRAMEWORK STATUS")
        print(f"Overall Status: {status['overall_status'].upper()}")
        print(f"Compliance Score: {status['compliance_score']:.1%}")
        print(f"Healthy Components: {status['healthy_components']}/{status['total_components']}")
        print("\nComponent Details:")
        
        for component_name, component_status in status["components"].items():
            status_icon = "✅" if component_status["healthy"] else "❌"
            coverage = component_status.get("test_coverage", 0) * 100
            print(f"  {status_icon} {component_name} (coverage: {coverage:.1f}%)")
            
            if component_status.get("issues"):
                for issue in component_status["issues"]:
                    print(f"    ⚠️ {issue}")
    
    if args.generate_makefile:
        output_path = integration.generate_beast_mode_makefile(Path(args.generate_makefile))
        print(f"\n🐺 Beast Mode Makefile generated: {output_path}")
        
        targets = integration.generate_beast_mode_targets()
        print(f"Generated {len(targets)} Beast Mode targets")
    
    if not args.status and not args.generate_makefile:
        # Default: show available targets
        targets = integration.generate_beast_mode_targets()
        print(f"\n🐺 BEAST MODE INTEGRATION MODULE")
        print(f"Available targets: {len(targets)}")
        
        # Group by type
        target_types = {}
        for name, target in targets.items():
            if "test" in name:
                target_type = "Testing"
            elif "validate" in name or "compliance" in name or "quality" in name:
                target_type = "Quality Assurance"
            elif "systematic" in name or "pdca" in name:
                target_type = "Systematic Operations"
            else:
                target_type = "General"
            
            if target_type not in target_types:
                target_types[target_type] = []
            target_types[target_type].append(name)
        
        for target_type, target_names in target_types.items():
            print(f"\n{target_type} targets ({len(target_names)}):")
            for name in sorted(target_names)[:5]:  # Show first 5
                print(f"  {name}")
            if len(target_names) > 5:
                print(f"  ... and {len(target_names) - 5} more")


if __name__ == "__main__":
    main()