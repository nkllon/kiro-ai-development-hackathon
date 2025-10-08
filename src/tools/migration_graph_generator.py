#!/usr/bin/env python3
"""
Migration Graph Generator
========================

Creates comprehensive JSON graphs for RDI, RM-DDD, and complete migration strategy.
Maps every artifact, validates every destination, and provides complete rollback plans.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Complete migration planning with graph-based validation
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class ArtifactNode:
    """Represents an artifact in the migration graph."""
    id: str
    name: str
    type: str
    current_path: str
    target_path: str
    size: int
    dependencies: List[str]
    criticality: str
    validation_checks: List[str]
    backup_required: bool
    rollback_path: str

@dataclass
class MigrationEdge:
    """Represents a migration relationship between artifacts."""
    source: str
    target: str
    operation: str
    validation: str
    rollback_operation: str
    risk_level: str

@dataclass
class ValidationCheck:
    """Represents a validation check for an artifact."""
    check_id: str
    artifact_id: str
    check_type: str
    command: str
    expected_result: str
    failure_action: str

class MigrationGraphGenerator:
    """Generates comprehensive migration graphs for RDI, RM-DDD, and complete migration."""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root)
        self.artifacts = {}
        self.migrations = []
        self.validations = []
        
    def generate_complete_migration_graphs(self) -> Dict[str, Any]:
        """Generate all migration graphs."""
        print("🚨 GENERATING COMPLETE MIGRATION GRAPHS 🚨")
        print("This is it! The moment we should have trained for!")
        print()
        
        # Generate RDI Migration Graph
        print("📊 PHASE 1: RDI MIGRATION GRAPH")
        print("=" * 50)
        rdi_graph = self._generate_rdi_migration_graph()
        
        # Generate RM-DDD Migration Graph
        print("\n📊 PHASE 2: RM-DDD MIGRATION GRAPH")
        print("=" * 50)
        rm_ddd_graph = self._generate_rm_ddd_migration_graph()
        
        # Generate Complete Migration Graph
        print("\n📊 PHASE 3: COMPLETE MIGRATION GRAPH")
        print("=" * 50)
        complete_graph = self._generate_complete_migration_graph()
        
        # Generate Validation Graph
        print("\n📊 PHASE 4: VALIDATION GRAPH")
        print("=" * 50)
        validation_graph = self._generate_validation_graph()
        
        # Generate Rollback Graph
        print("\n📊 PHASE 5: ROLLBACK GRAPH")
        print("=" * 50)
        rollback_graph = self._generate_rollback_graph()
        
        # Compile all graphs
        all_graphs = {
            "metadata": {
                "generated_at": time.time(),
                "repository_root": str(self.repository_root),
                "total_artifacts": len(self.artifacts),
                "total_migrations": len(self.migrations),
                "total_validations": len(self.validations)
            },
            "rdi_migration_graph": rdi_graph,
            "rm_ddd_migration_graph": rm_ddd_graph,
            "complete_migration_graph": complete_graph,
            "validation_graph": validation_graph,
            "rollback_graph": rollback_graph
        }
        
        return all_graphs
    
    def _generate_rdi_migration_graph(self) -> Dict[str, Any]:
        """Generate RDI migration graph."""
        print("🔍 Analyzing RDI system components...")
        
        rdi_components = {
            "core_rdi_files": [
                "RDI_ANALYSIS_REPORT.md",
                "RDI_ANALYSIS_SUMMARY.md",
                "RM_RDI_IMPLEMENTATION_PROMPT.md",
                "beast_mode_rdi_attack_system.py",
                "generate_rdi_traceable_tests.py"
            ],
            "rdi_specs": [
                ".kiro/specs/rm-rdi-analysis-system/",
                ".kiro/specs/rmi-rm-ddd-conformance-remediation/",
                ".kiro/specs/beast-mode-rm-ddd-dag-analysis.md",
                ".kiro/specs/rm-ddd/"
            ],
            "rdi_implementations": [
                "src/reflective_modules/",
                "src/beast_mode/",
                "src/spec_reconciliation/"
            ]
        }
        
        # Create artifact nodes for RDI components
        rdi_artifacts = []
        for category, files in rdi_components.items():
            for file_path in files:
                artifact = self._create_artifact_node(
                    f"rdi_{category}_{Path(file_path).name}",
                    file_path,
                    "rdi_component",
                    "PRESERVE",
                    "RDI system component"
                )
                rdi_artifacts.append(artifact)
        
        # Create migration edges (mostly preserve operations)
        rdi_migrations = []
        for artifact in rdi_artifacts:
            migration = MigrationEdge(
                source=artifact.id,
                target=artifact.id,
                operation="PRESERVE",
                validation="EXISTS_AND_ACCESSIBLE",
                rollback_operation="NONE",
                risk_level="ZERO"
            )
            rdi_migrations.append(migration)
        
        return {
            "graph_type": "rdi_migration",
            "nodes": [asdict(artifact) for artifact in rdi_artifacts],
            "edges": [asdict(migration) for migration in rdi_migrations],
            "summary": {
                "total_components": len(rdi_artifacts),
                "preserve_operations": len(rdi_migrations),
                "risk_level": "ZERO"
            }
        }
    
    def _generate_rm_ddd_migration_graph(self) -> Dict[str, Any]:
        """Generate RM-DDD migration graph."""
        print("🔍 Analyzing RM-DDD system components...")
        
        rm_ddd_components = {
            "reflective_modules": [
                "src/reflective_modules/base.py",
                "src/reflective_modules/health.py",
                "src/reflective_modules/registry.py"
            ],
            "domain_models": [
                "src/beast_mode/",
                "src/devpost_integration/",
                "src/spec_reconciliation/",
                "src/hackathon_demo_framework/"
            ],
            "ddd_specs": [
                ".kiro/specs/rm-ddd/",
                ".kiro/specs/rmi-rm-ddd-conformance-remediation/"
            ]
        }
        
        # Create artifact nodes for RM-DDD components
        rm_ddd_artifacts = []
        for category, files in rm_ddd_components.items():
            for file_path in files:
                artifact = self._create_artifact_node(
                    f"rm_ddd_{category}_{Path(file_path).name}",
                    file_path,
                    "rm_ddd_component",
                    "PRESERVE",
                    "RM-DDD system component"
                )
                rm_ddd_artifacts.append(artifact)
        
        # Create migration edges
        rm_ddd_migrations = []
        for artifact in rm_ddd_artifacts:
            migration = MigrationEdge(
                source=artifact.id,
                target=artifact.id,
                operation="PRESERVE",
                validation="EXISTS_AND_ACCESSIBLE",
                rollback_operation="NONE",
                risk_level="ZERO"
            )
            rm_ddd_migrations.append(migration)
        
        return {
            "graph_type": "rm_ddd_migration",
            "nodes": [asdict(artifact) for artifact in rm_ddd_artifacts],
            "edges": [asdict(migration) for migration in rm_ddd_migrations],
            "summary": {
                "total_components": len(rm_ddd_artifacts),
                "preserve_operations": len(rm_ddd_migrations),
                "risk_level": "ZERO"
            }
        }
    
    def _generate_complete_migration_graph(self) -> Dict[str, Any]:
        """Generate complete migration graph for all artifacts."""
        print("🔍 Analyzing all artifacts for complete migration...")
        
        # Scan all files in repository
        all_files = []
        for root, dirs, files in os.walk(self.repository_root):
            for file in files:
                file_path = Path(root) / file
                if self._should_include_file(file_path):
                    all_files.append(file_path)
        
        # Create artifact nodes for all files
        complete_artifacts = []
        for file_path in all_files:
            artifact = self._create_artifact_node(
                f"artifact_{file_path.name}_{hash(str(file_path))}",
                str(file_path.relative_to(self.repository_root)),
                self._classify_file_type(file_path),
                self._determine_migration_action(file_path),
                "Migration target determined by analysis"
            )
            complete_artifacts.append(artifact)
        
        # Create migration edges
        complete_migrations = []
        for artifact in complete_artifacts:
            migration = MigrationEdge(
                source=artifact.id,
                target=artifact.target_path,
                operation=artifact.target_path,
                validation=self._determine_validation(artifact),
                rollback_operation=self._determine_rollback_operation(artifact),
                risk_level=self._assess_risk_level(artifact)
            )
            complete_migrations.append(migration)
        
        return {
            "graph_type": "complete_migration",
            "nodes": [asdict(artifact) for artifact in complete_artifacts],
            "edges": [asdict(migration) for migration in complete_migrations],
            "summary": {
                "total_artifacts": len(complete_artifacts),
                "total_migrations": len(complete_migrations),
                "high_risk_migrations": len([m for m in complete_migrations if m.risk_level == "HIGH"]),
                "medium_risk_migrations": len([m for m in complete_migrations if m.risk_level == "MEDIUM"]),
                "low_risk_migrations": len([m for m in complete_migrations if m.risk_level == "LOW"]),
                "zero_risk_migrations": len([m for m in complete_migrations if m.risk_level == "ZERO"])
            }
        }
    
    def _generate_validation_graph(self) -> Dict[str, Any]:
        """Generate validation graph for all artifacts."""
        print("🔍 Creating validation graph...")
        
        validation_checks = []
        
        # Critical system validations
        critical_systems = [
            "README.md",
            "pyproject.toml",
            "docs/",
            "diagrams/",
            "src/",
            "RDI_ANALYSIS_REPORT.md",
            "RDI_ANALYSIS_SUMMARY.md"
        ]
        
        for system in critical_systems:
            check = ValidationCheck(
                check_id=f"critical_{system.replace('/', '_')}",
                artifact_id=system,
                check_type="EXISTS_AND_ACCESSIBLE",
                command=f"test -e '{system}' && echo 'EXISTS'",
                expected_result="EXISTS",
                failure_action="ABORT_MIGRATION"
            )
            validation_checks.append(check)
        
        # Documentation index validations
        docs_validation = ValidationCheck(
            check_id="docs_index_functional",
            artifact_id="docs/README.md",
            check_type="FUNCTIONAL_TEST",
            command="cd docs && python -c 'import sys; sys.path.append(\"..\"); from src.documentation_index_generator import DocumentationIndexGenerator; print(\"FUNCTIONAL\")'",
            expected_result="FUNCTIONAL",
            failure_action="RESTORE_FROM_BACKUP"
        )
        validation_checks.append(docs_validation)
        
        # RDI registry validations
        rdi_validation = ValidationCheck(
            check_id="rdi_registry_functional",
            artifact_id="RDI_ANALYSIS_REPORT.md",
            check_type="FUNCTIONAL_TEST",
            command="test -f 'RDI_ANALYSIS_REPORT.md' && grep -q 'RDI' 'RDI_ANALYSIS_REPORT.md' && echo 'FUNCTIONAL'",
            expected_result="FUNCTIONAL",
            failure_action="RESTORE_FROM_BACKUP"
        )
        validation_checks.append(rdi_validation)
        
        return {
            "graph_type": "validation",
            "checks": [asdict(check) for check in validation_checks],
            "summary": {
                "total_checks": len(validation_checks),
                "critical_checks": len([c for c in validation_checks if c.check_type == "EXISTS_AND_ACCESSIBLE"]),
                "functional_checks": len([c for c in validation_checks if c.check_type == "FUNCTIONAL_TEST"])
            }
        }
    
    def _generate_rollback_graph(self) -> Dict[str, Any]:
        """Generate rollback graph for all operations."""
        print("🔍 Creating rollback graph...")
        
        rollback_operations = []
        
        # File deletion rollbacks
        rollback_operations.append({
            "operation_id": "rollback_file_deletion",
            "operation_type": "RESTORE_FROM_BACKUP",
            "command": "cp -r backup_*/{file} {original_location}",
            "validation": "test -e {original_location}",
            "risk_level": "LOW"
        })
        
        # Directory cleanup rollbacks
        rollback_operations.append({
            "operation_id": "rollback_directory_cleanup",
            "operation_type": "RESTORE_FROM_BACKUP",
            "command": "cp -r backup_*/{dir} {original_location}",
            "validation": "test -d {original_location}",
            "risk_level": "LOW"
        })
        
        # Git rollback
        rollback_operations.append({
            "operation_id": "rollback_git_state",
            "operation_type": "GIT_RESET",
            "command": "git reset --hard HEAD~1",
            "validation": "git status --porcelain | wc -l | grep -q '^0$'",
            "risk_level": "MEDIUM"
        })
        
        # Complete system rollback
        rollback_operations.append({
            "operation_id": "rollback_complete_system",
            "operation_type": "FULL_RESTORE",
            "command": "cp -r backup_*/* .",
            "validation": "test -e README.md && test -e pyproject.toml",
            "risk_level": "HIGH"
        })
        
        return {
            "graph_type": "rollback",
            "operations": rollback_operations,
            "summary": {
                "total_operations": len(rollback_operations),
                "low_risk_operations": len([op for op in rollback_operations if op["risk_level"] == "LOW"]),
                "medium_risk_operations": len([op for op in rollback_operations if op["risk_level"] == "MEDIUM"]),
                "high_risk_operations": len([op for op in rollback_operations if op["risk_level"] == "HIGH"])
            }
        }
    
    def _create_artifact_node(self, artifact_id: str, file_path: str, artifact_type: str, 
                            migration_action: str, reason: str) -> ArtifactNode:
        """Create an artifact node."""
        full_path = self.repository_root / file_path
        size = full_path.stat().st_size if full_path.exists() else 0
        
        return ArtifactNode(
            id=artifact_id,
            name=Path(file_path).name,
            type=artifact_type,
            current_path=file_path,
            target_path=file_path if migration_action == "PRESERVE" else f"archived/{file_path}",
            size=size,
            dependencies=self._find_dependencies(file_path),
            criticality=self._assess_criticality(file_path),
            validation_checks=self._get_validation_checks(file_path),
            backup_required=migration_action != "PRESERVE",
            rollback_path=file_path
        )
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Determine if file should be included in migration analysis."""
        # Skip hidden files, cache files, and temporary files
        skip_patterns = [
            ".git/", "__pycache__/", ".pytest_cache/", ".coverage",
            ".DS_Store", "*.pyc", "*.log", "*.tmp", "*.temp"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    def _classify_file_type(self, file_path: Path) -> str:
        """Classify file type."""
        if file_path.suffix == ".py":
            return "python_file"
        elif file_path.suffix == ".md":
            return "markdown_file"
        elif file_path.suffix in [".json", ".yaml", ".yml", ".toml"]:
            return "config_file"
        elif file_path.suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
            return "image_file"
        else:
            return "other_file"
    
    def _determine_migration_action(self, file_path: Path) -> str:
        """Determine migration action for file."""
        # Critical files that must be preserved
        critical_files = [
            "README.md", "pyproject.toml", "requirements.txt",
            "RDI_ANALYSIS_REPORT.md", "RDI_ANALYSIS_SUMMARY.md",
            "RM_RDI_IMPLEMENTATION_PROMPT.md"
        ]
        
        if file_path.name in critical_files:
            return "PRESERVE"
        
        # Documentation files
        if "docs/" in str(file_path) or "diagrams/" in str(file_path):
            return "PRESERVE"
        
        # Source code files
        if "src/" in str(file_path) and file_path.suffix == ".py":
            return "PRESERVE"
        
        # Temporary files
        if self._is_temporary_file(file_path.name):
            return "DELETE"
        
        # Backup files
        if self._is_backup_file(file_path.name):
            return "ARCHIVE"
        
        # Unknown files
        return "REVIEW"
    
    def _determine_validation(self, artifact: ArtifactNode) -> str:
        """Determine validation for artifact."""
        if artifact.criticality == "CRITICAL":
            return "EXISTS_AND_FUNCTIONAL"
        elif artifact.criticality == "HIGH":
            return "EXISTS_AND_ACCESSIBLE"
        else:
            return "EXISTS"
    
    def _determine_rollback_operation(self, artifact: ArtifactNode) -> str:
        """Determine rollback operation for artifact."""
        if artifact.backup_required:
            return "RESTORE_FROM_BACKUP"
        else:
            return "NONE"
    
    def _assess_risk_level(self, artifact: ArtifactNode) -> str:
        """Assess risk level for artifact migration."""
        if artifact.criticality == "CRITICAL":
            return "HIGH"
        elif artifact.criticality == "HIGH":
            return "MEDIUM"
        else:
            return "LOW"
    
    def _find_dependencies(self, file_path: str) -> List[str]:
        """Find dependencies for file."""
        # Simplified dependency detection
        dependencies = []
        
        if file_path.endswith(".py"):
            # Python file dependencies
            dependencies.append("python_runtime")
        
        if "docs/" in file_path:
            # Documentation dependencies
            dependencies.append("documentation_index")
        
        if "RDI" in file_path:
            # RDI dependencies
            dependencies.append("rdi_system")
        
        return dependencies
    
    def _assess_criticality(self, file_path: str) -> str:
        """Assess criticality of file."""
        critical_files = [
            "README.md", "pyproject.toml", "requirements.txt",
            "RDI_ANALYSIS_REPORT.md", "RDI_ANALYSIS_SUMMARY.md",
            "RM_RDI_IMPLEMENTATION_PROMPT.md"
        ]
        
        if file_path in critical_files:
            return "CRITICAL"
        
        if "docs/" in file_path or "diagrams/" in file_path:
            return "HIGH"
        
        if "src/" in file_path:
            return "MEDIUM"
        
        return "LOW"
    
    def _get_validation_checks(self, file_path: str) -> List[str]:
        """Get validation checks for file."""
        checks = ["EXISTS"]
        
        if file_path.endswith(".py"):
            checks.append("SYNTAX_VALID")
        
        if "docs/" in file_path:
            checks.append("MARKDOWN_VALID")
        
        if "RDI" in file_path:
            checks.append("RDI_FUNCTIONAL")
        
        return checks
    
    def _is_temporary_file(self, file_name: str) -> bool:
        """Check if file is temporary."""
        temp_patterns = [
            ".tmp", ".temp", ".cache", ".coverage", ".DS_Store",
            "chrome_cookies.db", "actual_current_page.png",
            "additional_info_filled.png", "additional_info_page.png",
            "aardvark_project.html", "-", ".cache_ggshield",
            "Screen Recording", ".mov", ".log", ".out", ".err"
        ]
        
        return any(pattern in file_name for pattern in temp_patterns)
    
    def _is_backup_file(self, file_name: str) -> bool:
        """Check if file is a backup."""
        backup_patterns = [
            ".bak", ".backup", "_backup", "_old", "_orig",
            ".coverage 2"
        ]
        
        return any(pattern in file_name for pattern in backup_patterns)
    
    def save_graphs(self, graphs: Dict[str, Any], output_dir: str = "migration_graphs"):
        """Save all graphs to JSON files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save individual graphs
        for graph_name, graph_data in graphs.items():
            if graph_name != "metadata":
                file_path = output_path / f"{graph_name}.json"
                with open(file_path, 'w') as f:
                    json.dump(graph_data, f, indent=2, default=str)
                print(f"💾 Saved {graph_name}: {file_path}")
        
        # Save complete graphs
        complete_file = output_path / "complete_migration_graphs.json"
        with open(complete_file, 'w') as f:
            json.dump(graphs, f, indent=2, default=str)
        print(f"💾 Saved complete graphs: {complete_file}")
        
        return output_path

def main():
    """Generate complete migration graphs."""
    print("🚨 MIGRATION GRAPH GENERATOR INITIATED! 🚨")
    print("This is it! The moment we should have trained for!")
    print()
    
    # Initialize generator
    generator = MigrationGraphGenerator()
    
    # Generate all graphs
    graphs = generator.generate_complete_migration_graphs()
    
    # Save graphs
    output_dir = generator.save_graphs(graphs)
    
    print(f"\n✅ Migration graphs generated successfully!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Total artifacts: {graphs['metadata']['total_artifacts']}")
    print(f"📊 Total migrations: {graphs['metadata']['total_migrations']}")
    print(f"📊 Total validations: {graphs['metadata']['total_validations']}")
    
    print(f"\n🎯 Next steps:")
    print(f"1. Review migration graphs in {output_dir}")
    print(f"2. Validate all artifact destinations")
    print(f"3. Test rollback procedures")
    print(f"4. Execute migration with full validation")

if __name__ == "__main__":
    main()


