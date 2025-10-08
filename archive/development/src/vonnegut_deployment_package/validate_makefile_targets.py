#!/usr/bin/env python3
"""
Makefile Target Validator
=========================

Comprehensive validation system for Makefile targets.
Validates syntax, dependencies, and execution safety.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Target validation and dependency analysis for Makefile system
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ValidationLevel(Enum):
    """Validation levels."""
    SYNTAX = "syntax"
    DEPENDENCIES = "dependencies"
    SAFETY = "safety"
    PERFORMANCE = "performance"
    COMPREHENSIVE = "comprehensive"


class IssueType(Enum):
    """Types of validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    type: IssueType
    category: str
    message: str
    target: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class TargetInfo:
    """Information about a Makefile target."""
    name: str
    dependencies: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    phony: bool = False
    file_path: str = ""
    line_number: int = 0
    description: str = ""


@dataclass
class ValidationReport:
    """Validation report for targets."""
    target: str
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    dependencies_valid: bool = True
    circular_dependencies: List[str] = field(default_factory=list)
    missing_dependencies: List[str] = field(default_factory=list)
    performance_score: float = 1.0
    safety_score: float = 1.0


class MakefileTargetValidator(ReflectiveModule):
    """
    🎯 MAKEFILE TARGET VALIDATOR 🎯
    
    Comprehensive validation system for Makefile targets.
    Validates syntax, dependencies, safety, and performance.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "makefile_target_validator"
        self.repository_root = Path(repository_root)
        
        # Target registry
        self.targets: Dict[str, TargetInfo] = {}
        self.validation_reports: Dict[str, ValidationReport] = {}
        
        # Validation rules
        self.syntax_rules = self._initialize_syntax_rules()
        self.safety_rules = self._initialize_safety_rules()
        self.performance_rules = self._initialize_performance_rules()
        
        # Load targets
        self._load_makefile_targets()
    
    def _initialize_syntax_rules(self) -> Dict[str, Any]:
        """Initialize syntax validation rules."""
        return {
            "target_naming": {
                "pattern": r"^[a-zA-Z][a-zA-Z0-9_-]*$",
                "message": "Target names should start with letter and contain only letters, numbers, hyphens, and underscores"
            },
            "phony_declaration": {
                "required_for": ["help", "clean", "test", "install", "deploy"],
                "message": "Common targets should be declared as .PHONY"
            },
            "tab_indentation": {
                "message": "Commands must be indented with tabs, not spaces"
            },
            "line_continuation": {
                "pattern": r"\\\s*$",
                "message": "Line continuations should end with backslash"
            },
            "variable_syntax": {
                "pattern": r"\$\([A-Z_][A-Z0-9_]*\)",
                "message": "Variables should use $(VAR) syntax with uppercase names"
            }
        }
    
    def _initialize_safety_rules(self) -> Dict[str, Any]:
        """Initialize safety validation rules."""
        return {
            "dangerous_commands": {
                "patterns": [
                    r"rm\s+-rf\s+/",
                    r"rm\s+-rf\s+\*",
                    r"sudo\s+rm",
                    r"format\s+[A-Z]:",
                    r"dd\s+if=.*of=/dev/",
                    r"chmod\s+777",
                    r"chown\s+.*:.*\s+/"
                ],
                "message": "Dangerous command detected"
            },
            "protected_paths": {
                "paths": ["/", "/usr", "/bin", "/sbin", "/etc", "/var", "/home", "/root"],
                "message": "Operation affects protected system path"
            },
            "confirmation_required": {
                "targets": ["clean", "reset", "purge", "delete", "remove"],
                "message": "Destructive targets should require confirmation"
            },
            "error_handling": {
                "message": "Commands should include error handling"
            }
        }
    
    def _initialize_performance_rules(self) -> Dict[str, Any]:
        """Initialize performance validation rules."""
        return {
            "parallel_safe": {
                "message": "Target should be safe for parallel execution"
            },
            "dependency_optimization": {
                "message": "Dependencies could be optimized"
            },
            "command_efficiency": {
                "message": "Commands could be more efficient"
            },
            "caching_opportunity": {
                "message": "Target could benefit from caching"
            }
        }
    
    def _load_makefile_targets(self):
        """Load targets from all Makefiles."""
        makefile_paths = [
            self.repository_root / "Makefile",
            self.repository_root / "makefiles" / "governance.mk",
            self.repository_root / "makefiles" / "testing.mk"
        ]
        
        for makefile_path in makefile_paths:
            if makefile_path.exists():
                self._parse_makefile(makefile_path)
    
    def _parse_makefile(self, makefile_path: Path):
        """Parse a Makefile and extract target information."""
        try:
            with open(makefile_path, 'r') as f:
                lines = f.readlines()
            
            current_target = None
            phony_targets = set()
            
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Check for .PHONY declaration
                if line.startswith('.PHONY:'):
                    phony_list = line[7:].strip().split()
                    phony_targets.update(phony_list)
                    continue
                
                # Check for target definition
                if ':' in line and not line.startswith('\t'):
                    target_match = re.match(r'^([^:]+):\s*(.*?)(?:\s*##\s*(.*))?$', line)
                    if target_match:
                        target_name = target_match.group(1).strip()
                        dependencies = [dep.strip() for dep in target_match.group(2).split() if dep.strip()]
                        description = target_match.group(3) or ""
                        
                        current_target = TargetInfo(
                            name=target_name,
                            dependencies=dependencies,
                            phony=target_name in phony_targets,
                            file_path=str(makefile_path),
                            line_number=line_num,
                            description=description
                        )
                        
                        self.targets[target_name] = current_target
                
                # Check for command lines
                elif line.startswith('\t') and current_target:
                    command = line[1:]  # Remove tab
                    current_target.commands.append(command)
            
            # Update phony status for all targets
            for target_name in phony_targets:
                if target_name in self.targets:
                    self.targets[target_name].phony = True
                    
        except Exception as e:
            self._logger.error(f"Failed to parse {makefile_path}: {e}")
    
    def validate_target(self, target_name: str, 
                       validation_level: ValidationLevel = ValidationLevel.COMPREHENSIVE) -> ValidationReport:
        """Validate a specific target."""
        if target_name not in self.targets:
            return ValidationReport(
                target=target_name,
                valid=False,
                issues=[ValidationIssue(
                    type=IssueType.ERROR,
                    category="existence",
                    message=f"Target '{target_name}' not found",
                    target=target_name
                )]
            )
        
        target_info = self.targets[target_name]
        report = ValidationReport(target=target_name, valid=True)
        
        # Run validation based on level
        if validation_level in [ValidationLevel.SYNTAX, ValidationLevel.COMPREHENSIVE]:
            self._validate_syntax(target_info, report)
        
        if validation_level in [ValidationLevel.DEPENDENCIES, ValidationLevel.COMPREHENSIVE]:
            self._validate_dependencies(target_info, report)
        
        if validation_level in [ValidationLevel.SAFETY, ValidationLevel.COMPREHENSIVE]:
            self._validate_safety(target_info, report)
        
        if validation_level in [ValidationLevel.PERFORMANCE, ValidationLevel.COMPREHENSIVE]:
            self._validate_performance(target_info, report)
        
        # Determine overall validity
        report.valid = not any(issue.type == IssueType.ERROR for issue in report.issues)
        
        self.validation_reports[target_name] = report
        return report
    
    def _validate_syntax(self, target_info: TargetInfo, report: ValidationReport):
        """Validate target syntax."""
        # Check target naming
        naming_rule = self.syntax_rules["target_naming"]
        if not re.match(naming_rule["pattern"], target_info.name):
            report.issues.append(ValidationIssue(
                type=IssueType.WARNING,
                category="syntax",
                message=naming_rule["message"],
                target=target_info.name,
                line_number=target_info.line_number
            ))
        
        # Check .PHONY declaration
        phony_rule = self.syntax_rules["phony_declaration"]
        if target_info.name in phony_rule["required_for"] and not target_info.phony:
            report.issues.append(ValidationIssue(
                type=IssueType.WARNING,
                category="syntax",
                message=f"{phony_rule['message']}: {target_info.name}",
                target=target_info.name,
                suggestion=f"Add '.PHONY: {target_info.name}' to Makefile"
            ))
        
        # Check command indentation (this would require access to raw file content)
        # For now, we assume commands are properly indented since they were parsed
        
        # Check variable syntax in commands
        var_rule = self.syntax_rules["variable_syntax"]
        for i, command in enumerate(target_info.commands):
            # Look for variables that don't follow convention
            bad_vars = re.findall(r'\$\([a-z_][a-z0-9_]*\)', command)
            if bad_vars:
                report.issues.append(ValidationIssue(
                    type=IssueType.SUGGESTION,
                    category="syntax",
                    message=f"Variable naming: {var_rule['message']}",
                    target=target_info.name,
                    suggestion=f"Use uppercase variable names: {', '.join(bad_vars)}"
                ))
    
    def _validate_dependencies(self, target_info: TargetInfo, report: ValidationReport):
        """Validate target dependencies."""
        # Check for missing dependencies
        missing_deps = []
        for dep in target_info.dependencies:
            if dep not in self.targets:
                # Check if it's a file that exists
                dep_path = self.repository_root / dep
                if not dep_path.exists():
                    missing_deps.append(dep)
        
        if missing_deps:
            report.missing_dependencies = missing_deps
            report.dependencies_valid = False
            report.issues.append(ValidationIssue(
                type=IssueType.ERROR,
                category="dependencies",
                message=f"Missing dependencies: {', '.join(missing_deps)}",
                target=target_info.name,
                suggestion="Create missing targets or verify file paths"
            ))
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(target_info.name)
        if circular_deps:
            report.circular_dependencies = circular_deps
            report.dependencies_valid = False
            report.issues.append(ValidationIssue(
                type=IssueType.ERROR,
                category="dependencies",
                message=f"Circular dependency detected: {' -> '.join(circular_deps)}",
                target=target_info.name,
                suggestion="Remove circular dependencies by restructuring targets"
            ))
    
    def _detect_circular_dependencies(self, target_name: str, visited: Set[str] = None, 
                                    path: List[str] = None) -> List[str]:
        """Detect circular dependencies using DFS."""
        if visited is None:
            visited = set()
        if path is None:
            path = []
        
        if target_name in path:
            # Found cycle
            cycle_start = path.index(target_name)
            return path[cycle_start:] + [target_name]
        
        if target_name in visited or target_name not in self.targets:
            return []
        
        visited.add(target_name)
        path.append(target_name)
        
        target_info = self.targets[target_name]
        for dep in target_info.dependencies:
            cycle = self._detect_circular_dependencies(dep, visited, path.copy())
            if cycle:
                return cycle
        
        return []
    
    def _validate_safety(self, target_info: TargetInfo, report: ValidationReport):
        """Validate target safety."""
        safety_score = 1.0
        
        # Check for dangerous commands
        dangerous_rule = self.safety_rules["dangerous_commands"]
        for command in target_info.commands:
            for pattern in dangerous_rule["patterns"]:
                if re.search(pattern, command, re.IGNORECASE):
                    report.issues.append(ValidationIssue(
                        type=IssueType.ERROR,
                        category="safety",
                        message=f"{dangerous_rule['message']}: {command}",
                        target=target_info.name,
                        suggestion="Add confirmation prompt or use safer alternatives"
                    ))
                    safety_score -= 0.3
        
        # Check for protected paths
        protected_rule = self.safety_rules["protected_paths"]
        for command in target_info.commands:
            for path in protected_rule["paths"]:
                if path in command:
                    report.issues.append(ValidationIssue(
                        type=IssueType.WARNING,
                        category="safety",
                        message=f"{protected_rule['message']}: {path}",
                        target=target_info.name,
                        suggestion="Avoid operations on system paths"
                    ))
                    safety_score -= 0.1
        
        # Check if destructive targets require confirmation
        confirm_rule = self.safety_rules["confirmation_required"]
        if any(keyword in target_info.name.lower() for keyword in confirm_rule["targets"]):
            has_confirmation = any("read" in cmd or "confirm" in cmd or "echo" in cmd 
                                 for cmd in target_info.commands)
            if not has_confirmation:
                report.issues.append(ValidationIssue(
                    type=IssueType.WARNING,
                    category="safety",
                    message=f"{confirm_rule['message']}: {target_info.name}",
                    target=target_info.name,
                    suggestion="Add confirmation prompt for destructive operations"
                ))
                safety_score -= 0.2
        
        report.safety_score = max(0.0, safety_score)
    
    def _validate_performance(self, target_info: TargetInfo, report: ValidationReport):
        """Validate target performance characteristics."""
        performance_score = 1.0
        
        # Check for parallel safety
        has_file_conflicts = self._check_file_conflicts(target_info)
        if has_file_conflicts:
            report.issues.append(ValidationIssue(
                type=IssueType.INFO,
                category="performance",
                message="Target may not be safe for parallel execution",
                target=target_info.name,
                suggestion="Ensure no file conflicts with other targets"
            ))
            performance_score -= 0.1
        
        # Check for optimization opportunities
        if len(target_info.commands) > 5:
            report.issues.append(ValidationIssue(
                type=IssueType.SUGGESTION,
                category="performance",
                message="Target has many commands, consider splitting",
                target=target_info.name,
                suggestion="Split into smaller, focused targets"
            ))
            performance_score -= 0.1
        
        # Check for caching opportunities
        has_expensive_ops = any(
            keyword in " ".join(target_info.commands).lower()
            for keyword in ["compile", "build", "test", "download", "install"]
        )
        if has_expensive_ops and not any("cache" in cmd.lower() for cmd in target_info.commands):
            report.issues.append(ValidationIssue(
                type=IssueType.SUGGESTION,
                category="performance",
                message="Target could benefit from caching",
                target=target_info.name,
                suggestion="Consider adding caching for expensive operations"
            ))
            performance_score -= 0.1
        
        report.performance_score = max(0.0, performance_score)
    
    def _check_file_conflicts(self, target_info: TargetInfo) -> bool:
        """Check if target has potential file conflicts."""
        # Simple heuristic: check if target writes to common locations
        common_outputs = ["build/", "dist/", "reports/", "logs/"]
        
        for command in target_info.commands:
            for output in common_outputs:
                if output in command and (">" in command or "mkdir" in command):
                    return True
        
        return False
    
    def validate_all_targets(self, validation_level: ValidationLevel = ValidationLevel.COMPREHENSIVE) -> Dict[str, Any]:
        """Validate all targets."""
        self._logger.info(f"🎯 Validating {len(self.targets)} targets...")
        
        results = {}
        for target_name in self.targets:
            results[target_name] = self.validate_target(target_name, validation_level)
        
        # Generate summary
        total = len(results)
        valid = len([r for r in results.values() if r.valid])
        errors = sum(len([i for i in r.issues if i.type == IssueType.ERROR]) for r in results.values())
        warnings = sum(len([i for i in r.issues if i.type == IssueType.WARNING]) for r in results.values())
        
        return {
            "timestamp": self._get_current_timestamp(),
            "summary": {
                "total_targets": total,
                "valid_targets": valid,
                "invalid_targets": total - valid,
                "validation_rate": valid / total if total > 0 else 0,
                "total_errors": errors,
                "total_warnings": warnings
            },
            "results": {name: self._serialize_report(report) for name, report in results.items()}
        }
    
    def _serialize_report(self, report: ValidationReport) -> Dict[str, Any]:
        """Serialize validation report to dict."""
        return {
            "target": report.target,
            "valid": report.valid,
            "dependencies_valid": report.dependencies_valid,
            "safety_score": report.safety_score,
            "performance_score": report.performance_score,
            "issues": [
                {
                    "type": issue.type.value,
                    "category": issue.category,
                    "message": issue.message,
                    "line_number": issue.line_number,
                    "suggestion": issue.suggestion
                }
                for issue in report.issues
            ],
            "circular_dependencies": report.circular_dependencies,
            "missing_dependencies": report.missing_dependencies
        }
    
    def generate_validation_report(self, output_file: Optional[Path] = None) -> Path:
        """Generate comprehensive validation report."""
        if output_file is None:
            output_file = self.repository_root / "reports" / "makefile_target_validation.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Run comprehensive validation if not done
        if not self.validation_reports:
            self.validate_all_targets()
        
        report_data = self.validate_all_targets()
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self._logger.info(f"📊 Validation report saved: {output_file}")
        return output_file
    
    def get_target_dependency_graph(self) -> Dict[str, Any]:
        """Generate target dependency graph."""
        graph = {
            "nodes": [],
            "edges": []
        }
        
        for target_name, target_info in self.targets.items():
            graph["nodes"].append({
                "id": target_name,
                "label": target_name,
                "phony": target_info.phony,
                "commands": len(target_info.commands),
                "description": target_info.description
            })
            
            for dep in target_info.dependencies:
                graph["edges"].append({
                    "source": dep,
                    "target": target_name,
                    "type": "dependency"
                })
        
        return graph


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile Target Validator")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--target", help="Validate specific target")
    parser.add_argument("--level", choices=["syntax", "dependencies", "safety", "performance", "comprehensive"],
                       default="comprehensive", help="Validation level")
    parser.add_argument("--report", help="Generate validation report to file")
    parser.add_argument("--graph", action="store_true", help="Show dependency graph")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create validator
    validator = MakefileTargetValidator(args.root)
    
    validation_level = ValidationLevel(args.level)
    
    if args.target:
        # Validate specific target
        report = validator.validate_target(args.target, validation_level)
        
        print(f"\n🎯 TARGET VALIDATION: {args.target}")
        print(f"Valid: {'✅ YES' if report.valid else '❌ NO'}")
        print(f"Dependencies Valid: {'✅ YES' if report.dependencies_valid else '❌ NO'}")
        print(f"Safety Score: {report.safety_score:.2f}")
        print(f"Performance Score: {report.performance_score:.2f}")
        
        if report.issues:
            print(f"\nIssues ({len(report.issues)}):")
            for issue in report.issues:
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️", "suggestion": "💡"}[issue.type.value]
                print(f"  {icon} [{issue.category}] {issue.message}")
                if issue.suggestion:
                    print(f"      💡 {issue.suggestion}")
        
        if report.circular_dependencies:
            print(f"\nCircular Dependencies: {' -> '.join(report.circular_dependencies)}")
        
        if report.missing_dependencies:
            print(f"\nMissing Dependencies: {', '.join(report.missing_dependencies)}")
    
    else:
        # Validate all targets
        results = validator.validate_all_targets(validation_level)
        
        print(f"\n🎯 ALL TARGETS VALIDATION")
        print(f"Total targets: {results['summary']['total_targets']}")
        print(f"Valid targets: {results['summary']['valid_targets']}")
        print(f"Invalid targets: {results['summary']['invalid_targets']}")
        print(f"Validation rate: {results['summary']['validation_rate']:.1%}")
        print(f"Total errors: {results['summary']['total_errors']}")
        print(f"Total warnings: {results['summary']['total_warnings']}")
        
        if args.verbose:
            invalid_targets = [name for name, report in results['results'].items() if not report['valid']]
            if invalid_targets:
                print(f"\nInvalid targets: {', '.join(invalid_targets)}")
    
    # Generate report if requested
    if args.report:
        report_path = validator.generate_validation_report(Path(args.report))
        print(f"\n📊 Validation report saved: {report_path}")
    
    # Show dependency graph if requested
    if args.graph:
        graph = validator.get_target_dependency_graph()
        print(f"\n📊 DEPENDENCY GRAPH")
        print(f"Nodes: {len(graph['nodes'])}")
        print(f"Edges: {len(graph['edges'])}")
        
        if args.verbose:
            print("\nTargets:")
            for node in graph['nodes']:
                phony_marker = " (PHONY)" if node['phony'] else ""
                print(f"  {node['id']}{phony_marker}: {node['commands']} commands")


if __name__ == "__main__":
    main()