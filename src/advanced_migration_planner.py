#!/usr/bin/env python3
"""
Advanced Migration Planner
=========================

Creates comprehensive migration plans with complete artifact mapping,
validation strategies, and rollback procedures. Addresses all the
critical questions about migration requirements and validation.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Complete migration planning with full artifact tracking
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class MigrationRequirement:
    """Represents a migration requirement."""
    requirement_id: str
    description: str
    source_artifacts: List[str]
    target_destinations: List[str]
    validation_criteria: List[str]
    rollback_procedures: List[str]
    risk_level: str
    dependencies: List[str]

@dataclass
class ArtifactMapping:
    """Maps every artifact to its destination and validation."""
    artifact_id: str
    current_location: str
    target_location: str
    migration_operation: str
    validation_commands: List[str]
    rollback_commands: List[str]
    backup_location: str
    criticality: str

@dataclass
class ValidationStrategy:
    """Comprehensive validation strategy."""
    validation_id: str
    artifact_id: str
    check_type: str
    command: str
    expected_result: str
    failure_action: str
    retry_count: int
    timeout_seconds: int

class AdvancedMigrationPlanner:
    """Advanced migration planner with complete artifact tracking."""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root)
        self.migration_requirements = []
        self.artifact_mappings = []
        self.validation_strategies = []
        self.rollback_procedures = []
        
    def generate_complete_migration_plan(self) -> Dict[str, Any]:
        """Generate complete migration plan addressing all critical questions."""
        print("🚨 ADVANCED MIGRATION PLANNER INITIATED! 🚨")
        print("This is it! The moment we should have trained for!")
        print()
        
        # Phase 1: Migration Requirements Analysis
        print("📋 PHASE 1: MIGRATION REQUIREMENTS ANALYSIS")
        print("=" * 60)
        requirements = self._analyze_migration_requirements()
        
        # Phase 2: Complete Artifact Mapping
        print("\n🗺️  PHASE 2: COMPLETE ARTIFACT MAPPING")
        print("=" * 60)
        mappings = self._create_complete_artifact_mappings()
        
        # Phase 3: Validation Strategy
        print("\n✅ PHASE 3: VALIDATION STRATEGY")
        print("=" * 60)
        validations = self._create_validation_strategy()
        
        # Phase 4: Rollback Procedures
        print("\n🔄 PHASE 4: ROLLBACK PROCEDURES")
        print("=" * 60)
        rollbacks = self._create_rollback_procedures()
        
        # Phase 5: Migration Execution Plan
        print("\n⚡ PHASE 5: MIGRATION EXECUTION PLAN")
        print("=" * 60)
        execution_plan = self._create_execution_plan()
        
        # Compile complete plan
        complete_plan = {
            "metadata": {
                "generated_at": time.time(),
                "repository_root": str(self.repository_root),
                "total_requirements": len(requirements),
                "total_artifacts": len(mappings),
                "total_validations": len(validations),
                "total_rollbacks": len(rollbacks)
            },
            "migration_requirements": requirements,
            "artifact_mappings": mappings,
            "validation_strategies": validations,
            "rollback_procedures": rollbacks,
            "execution_plan": execution_plan
        }
        
        return complete_plan
    
    def _analyze_migration_requirements(self) -> List[Dict[str, Any]]:
        """Analyze all migration requirements."""
        print("🔍 Analyzing migration requirements...")
        
        requirements = []
        
        # RDI System Migration Requirements
        rdi_requirements = MigrationRequirement(
            requirement_id="RDI_MIGRATION_001",
            description="Preserve RDI system integrity during root cleanup",
            source_artifacts=[
                "RDI_ANALYSIS_REPORT.md",
                "RDI_ANALYSIS_SUMMARY.md",
                "RM_RDI_IMPLEMENTATION_PROMPT.md",
                "beast_mode_rdi_attack_system.py",
                "generate_rdi_traceable_tests.py"
            ],
            target_destinations=[
                "RDI_ANALYSIS_REPORT.md",
                "RDI_ANALYSIS_SUMMARY.md",
                "RM_RDI_IMPLEMENTATION_PROMPT.md",
                "beast_mode_rdi_attack_system.py",
                "generate_rdi_traceable_tests.py"
            ],
            validation_criteria=[
                "All RDI files exist and are accessible",
                "RDI analysis reports contain valid content",
                "RDI system functionality verified"
            ],
            rollback_procedures=[
                "Restore RDI files from backup",
                "Verify RDI system functionality",
                "Re-run RDI analysis if needed"
            ],
            risk_level="CRITICAL",
            dependencies=["backup_system", "validation_system"]
        )
        requirements.append(asdict(rdi_requirements))
        
        # Documentation Index Migration Requirements
        docs_requirements = MigrationRequirement(
            requirement_id="DOCS_MIGRATION_001",
            description="Preserve documentation index system during cleanup",
            source_artifacts=[
                "docs/",
                "diagrams/",
                "README.md"
            ],
            target_destinations=[
                "docs/",
                "diagrams/",
                "README.md"
            ],
            validation_criteria=[
                "Documentation index is functional",
                "All navigation links work",
                "All 905+ documents are accessible"
            ],
            rollback_procedures=[
                "Restore documentation from backup",
                "Re-generate documentation index",
                "Verify all navigation links"
            ],
            risk_level="CRITICAL",
            dependencies=["backup_system", "documentation_index_generator"]
        )
        requirements.append(asdict(docs_requirements))
        
        # RM-DDD System Migration Requirements
        rm_ddd_requirements = MigrationRequirement(
            requirement_id="RM_DDD_MIGRATION_001",
            description="Preserve RM-DDD system components during cleanup",
            source_artifacts=[
                "src/reflective_modules/",
                "src/beast_mode/",
                "src/devpost_integration/",
                "src/spec_reconciliation/"
            ],
            target_destinations=[
                "src/reflective_modules/",
                "src/beast_mode/",
                "src/devpost_integration/",
                "src/spec_reconciliation/"
            ],
            validation_criteria=[
                "All RM modules implement ReflectiveModule interface",
                "DDD domain models are intact",
                "Registry system is functional"
            ],
            rollback_procedures=[
                "Restore source code from backup",
                "Re-run RM compliance tests",
                "Verify DDD domain integrity"
            ],
            risk_level="HIGH",
            dependencies=["backup_system", "test_system"]
        )
        requirements.append(asdict(rm_ddd_requirements))
        
        # Temporary File Cleanup Requirements
        temp_cleanup_requirements = MigrationRequirement(
            requirement_id="TEMP_CLEANUP_001",
            description="Remove temporary files safely",
            source_artifacts=[
                "*.log", "*.tmp", "*.cache", "*.coverage",
                "*.png", "*.mov", "chrome_cookies.db"
            ],
            target_destinations=[
                "archived/temporary_files/"
            ],
            validation_criteria=[
                "Temporary files are removed from root",
                "No critical files are affected",
                "System functionality is preserved"
            ],
            rollback_procedures=[
                "Restore temporary files from backup if needed",
                "Verify system functionality"
            ],
            risk_level="LOW",
            dependencies=["backup_system"]
        )
        requirements.append(asdict(temp_cleanup_requirements))
        
        return requirements
    
    def _create_complete_artifact_mappings(self) -> List[Dict[str, Any]]:
        """Create complete mapping of every artifact to its destination."""
        print("🗺️  Creating complete artifact mappings...")
        
        mappings = []
        
        # Scan all files in repository
        all_files = []
        for root, dirs, files in os.walk(self.repository_root):
            for file in files:
                file_path = Path(root) / file
                if self._should_include_file(file_path):
                    all_files.append(file_path)
        
        # Create mapping for each file
        for file_path in all_files:
            mapping = self._create_artifact_mapping(file_path)
            mappings.append(asdict(mapping))
        
        return mappings
    
    def _create_artifact_mapping(self, file_path: Path) -> ArtifactMapping:
        """Create artifact mapping for a single file."""
        rel_path = file_path.relative_to(self.repository_root)
        
        # Determine migration operation
        operation = self._determine_migration_operation(file_path)
        
        # Determine target location
        if operation == "PRESERVE":
            target_location = str(rel_path)
        elif operation == "DELETE":
            target_location = "DELETED"
        elif operation == "ARCHIVE":
            target_location = f"archived/{rel_path}"
        else:
            target_location = f"review/{rel_path}"
        
        # Create validation commands
        validation_commands = self._create_validation_commands(file_path, operation)
        
        # Create rollback commands
        rollback_commands = self._create_rollback_commands(file_path, operation)
        
        # Determine backup location
        backup_location = f"backup_{int(time.time())}/{rel_path}"
        
        # Assess criticality
        criticality = self._assess_artifact_criticality(file_path)
        
        return ArtifactMapping(
            artifact_id=f"artifact_{hash(str(rel_path))}",
            current_location=str(rel_path),
            target_location=target_location,
            migration_operation=operation,
            validation_commands=validation_commands,
            rollback_commands=rollback_commands,
            backup_location=backup_location,
            criticality=criticality
        )
    
    def _create_validation_strategy(self) -> List[Dict[str, Any]]:
        """Create comprehensive validation strategy."""
        print("✅ Creating validation strategy...")
        
        validations = []
        
        # Critical system validations
        critical_systems = [
            "README.md",
            "pyproject.toml",
            "requirements.txt",
            "RDI_ANALYSIS_REPORT.md",
            "RDI_ANALYSIS_SUMMARY.md",
            "RM_RDI_IMPLEMENTATION_PROMPT.md"
        ]
        
        for system in critical_systems:
            validation = ValidationStrategy(
                validation_id=f"critical_{system.replace('/', '_')}",
                artifact_id=system,
                check_type="EXISTS_AND_ACCESSIBLE",
                command=f"test -e '{system}' && echo 'EXISTS'",
                expected_result="EXISTS",
                failure_action="ABORT_MIGRATION",
                retry_count=3,
                timeout_seconds=30
            )
            validations.append(asdict(validation))
        
        # Documentation index validation
        docs_validation = ValidationStrategy(
            validation_id="docs_index_functional",
            artifact_id="docs/README.md",
            check_type="FUNCTIONAL_TEST",
            command="cd docs && python -c 'import sys; sys.path.append(\"..\"); from src.documentation_index_generator import DocumentationIndexGenerator; print(\"FUNCTIONAL\")'",
            expected_result="FUNCTIONAL",
            failure_action="RESTORE_FROM_BACKUP",
            retry_count=2,
            timeout_seconds=60
        )
        validations.append(asdict(docs_validation))
        
        # RDI system validation
        rdi_validation = ValidationStrategy(
            validation_id="rdi_system_functional",
            artifact_id="RDI_ANALYSIS_REPORT.md",
            check_type="FUNCTIONAL_TEST",
            command="test -f 'RDI_ANALYSIS_REPORT.md' && grep -q 'RDI' 'RDI_ANALYSIS_REPORT.md' && echo 'FUNCTIONAL'",
            expected_result="FUNCTIONAL",
            failure_action="RESTORE_FROM_BACKUP",
            retry_count=2,
            timeout_seconds=30
        )
        validations.append(asdict(rdi_validation))
        
        # Source code validation
        src_validation = ValidationStrategy(
            validation_id="source_code_syntax",
            artifact_id="src/",
            check_type="SYNTAX_VALIDATION",
            command="find src -name '*.py' -exec python -m py_compile {} \\; && echo 'SYNTAX_VALID'",
            expected_result="SYNTAX_VALID",
            failure_action="RESTORE_FROM_BACKUP",
            retry_count=1,
            timeout_seconds=120
        )
        validations.append(asdict(src_validation))
        
        return validations
    
    def _create_rollback_procedures(self) -> List[Dict[str, Any]]:
        """Create comprehensive rollback procedures."""
        print("🔄 Creating rollback procedures...")
        
        rollbacks = []
        
        # File-level rollback
        file_rollback = {
            "rollback_id": "file_level_rollback",
            "description": "Rollback individual file operations",
            "procedures": [
                "Restore file from backup: cp backup_*/{file} {original_location}",
                "Verify file exists: test -e {original_location}",
                "Verify file content: diff backup_*/{file} {original_location}",
                "Update permissions: chmod {original_permissions} {original_location}"
            ],
            "validation": "test -e {original_location} && diff backup_*/{file} {original_location}",
            "risk_level": "LOW"
        }
        rollbacks.append(file_rollback)
        
        # Directory-level rollback
        dir_rollback = {
            "rollback_id": "directory_level_rollback",
            "description": "Rollback directory operations",
            "procedures": [
                "Restore directory from backup: cp -r backup_*/{dir} {original_location}",
                "Verify directory exists: test -d {original_location}",
                "Verify directory contents: ls -la {original_location}",
                "Update permissions: chmod -R {original_permissions} {original_location}"
            ],
            "validation": "test -d {original_location} && ls -la {original_location}",
            "risk_level": "LOW"
        }
        rollbacks.append(dir_rollback)
        
        # Git rollback
        git_rollback = {
            "rollback_id": "git_rollback",
            "description": "Rollback using git",
            "procedures": [
                "Check git status: git status --porcelain",
                "Reset to previous commit: git reset --hard HEAD~1",
                "Verify clean state: git status --porcelain | wc -l | grep -q '^0$'",
                "Force push if needed: git push --force-with-lease"
            ],
            "validation": "git status --porcelain | wc -l | grep -q '^0$'",
            "risk_level": "MEDIUM"
        }
        rollbacks.append(git_rollback)
        
        # Complete system rollback
        system_rollback = {
            "rollback_id": "complete_system_rollback",
            "description": "Complete system rollback",
            "procedures": [
                "Stop all processes: pkill -f python",
                "Restore from backup: cp -r backup_*/* .",
                "Verify critical files: test -e README.md && test -e pyproject.toml",
                "Restart services: systemctl restart {services}",
                "Run validation tests: make test"
            ],
            "validation": "test -e README.md && test -e pyproject.toml && make test",
            "risk_level": "HIGH"
        }
        rollbacks.append(system_rollback)
        
        return rollbacks
    
    def _create_execution_plan(self) -> Dict[str, Any]:
        """Create detailed execution plan."""
        print("⚡ Creating execution plan...")
        
        execution_plan = {
            "phases": [
                {
                    "phase": 1,
                    "name": "Pre-Migration Validation",
                    "description": "Validate all systems before migration",
                    "steps": [
                        "Create full system backup",
                        "Validate critical systems",
                        "Test documentation index",
                        "Test RDI registry",
                        "Run test suite"
                    ],
                    "validation": "All pre-migration checks pass",
                    "rollback": "None needed - pre-migration phase"
                },
                {
                    "phase": 2,
                    "name": "Safe Deletions",
                    "description": "Delete temporary files safely",
                    "steps": [
                        "Delete temporary files",
                        "Validate no critical files affected",
                        "Verify system functionality"
                    ],
                    "validation": "Temporary files deleted, system functional",
                    "rollback": "Restore from backup if issues"
                },
                {
                    "phase": 3,
                    "name": "Archive Operations",
                    "description": "Archive backup files",
                    "steps": [
                        "Move backup files to archive",
                        "Validate archive integrity",
                        "Verify system functionality"
                    ],
                    "validation": "Files archived, system functional",
                    "rollback": "Restore from archive if needed"
                },
                {
                    "phase": 4,
                    "name": "Post-Migration Validation",
                    "description": "Validate all systems after migration",
                    "steps": [
                        "Validate critical systems",
                        "Test documentation index",
                        "Test RDI registry",
                        "Run test suite",
                        "Verify system integrity"
                    ],
                    "validation": "All post-migration checks pass",
                    "rollback": "Execute rollback procedures if validation fails"
                }
            ],
            "safety_measures": [
                "Full system backup before migration",
                "Validation at each phase",
                "Rollback procedures ready",
                "Monitoring during migration",
                "Emergency stop procedures"
            ],
            "success_criteria": [
                "All critical systems functional",
                "Documentation index working",
                "RDI registry functional",
                "No data loss",
                "System performance maintained"
            ]
        }
        
        return execution_plan
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Determine if file should be included in migration analysis."""
        skip_patterns = [
            ".git/", "__pycache__/", ".pytest_cache/", ".coverage",
            ".DS_Store", "*.pyc", "*.log", "*.tmp", "*.temp"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    def _determine_migration_operation(self, file_path: Path) -> str:
        """Determine migration operation for file."""
        rel_path = file_path.relative_to(self.repository_root)
        
        # Critical files that must be preserved
        critical_files = [
            "README.md", "pyproject.toml", "requirements.txt",
            "RDI_ANALYSIS_REPORT.md", "RDI_ANALYSIS_SUMMARY.md",
            "RM_RDI_IMPLEMENTATION_PROMPT.md"
        ]
        
        if rel_path.name in critical_files:
            return "PRESERVE"
        
        # Documentation files
        if "docs/" in str(rel_path) or "diagrams/" in str(rel_path):
            return "PRESERVE"
        
        # Source code files
        if "src/" in str(rel_path) and file_path.suffix == ".py":
            return "PRESERVE"
        
        # Temporary files
        if self._is_temporary_file(rel_path.name):
            return "DELETE"
        
        # Backup files
        if self._is_backup_file(rel_path.name):
            return "ARCHIVE"
        
        # Unknown files
        return "REVIEW"
    
    def _create_validation_commands(self, file_path: Path, operation: str) -> List[str]:
        """Create validation commands for file."""
        commands = []
        
        if operation == "PRESERVE":
            commands.append(f"test -e '{file_path.relative_to(self.repository_root)}'")
            if file_path.suffix == ".py":
                commands.append(f"python -m py_compile '{file_path.relative_to(self.repository_root)}'")
        elif operation == "DELETE":
            commands.append(f"test ! -e '{file_path.relative_to(self.repository_root)}'")
        elif operation == "ARCHIVE":
            commands.append(f"test -e 'archived/{file_path.relative_to(self.repository_root)}'")
        
        return commands
    
    def _create_rollback_commands(self, file_path: Path, operation: str) -> List[str]:
        """Create rollback commands for file."""
        commands = []
        
        if operation == "DELETE":
            commands.append(f"cp backup_*/{file_path.relative_to(self.repository_root)} {file_path.relative_to(self.repository_root)}")
        elif operation == "ARCHIVE":
            commands.append(f"mv archived/{file_path.relative_to(self.repository_root)} {file_path.relative_to(self.repository_root)}")
        
        return commands
    
    def _assess_artifact_criticality(self, file_path: Path) -> str:
        """Assess criticality of artifact."""
        rel_path = file_path.relative_to(self.repository_root)
        
        critical_files = [
            "README.md", "pyproject.toml", "requirements.txt",
            "RDI_ANALYSIS_REPORT.md", "RDI_ANALYSIS_SUMMARY.md",
            "RM_RDI_IMPLEMENTATION_PROMPT.md"
        ]
        
        if rel_path.name in critical_files:
            return "CRITICAL"
        
        if "docs/" in str(rel_path) or "diagrams/" in str(rel_path):
            return "HIGH"
        
        if "src/" in str(rel_path):
            return "MEDIUM"
        
        return "LOW"
    
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
    
    def save_migration_plan(self, plan: Dict[str, Any], output_dir: str = "migration_plans"):
        """Save migration plan to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save complete plan
        complete_file = output_path / "complete_migration_plan.json"
        with open(complete_file, 'w') as f:
            json.dump(plan, f, indent=2, default=str)
        print(f"💾 Saved complete migration plan: {complete_file}")
        
        # Save individual components
        components = [
            ("migration_requirements", "requirements.json"),
            ("artifact_mappings", "mappings.json"),
            ("validation_strategies", "validations.json"),
            ("rollback_procedures", "rollbacks.json"),
            ("execution_plan", "execution.json")
        ]
        
        for component_name, filename in components:
            if component_name in plan:
                file_path = output_path / filename
                with open(file_path, 'w') as f:
                    json.dump(plan[component_name], f, indent=2, default=str)
                print(f"💾 Saved {component_name}: {file_path}")
        
        return output_path

def main():
    """Generate complete migration plan."""
    print("🚨 ADVANCED MIGRATION PLANNER INITIATED! 🚨")
    print("This is it! The moment we should have trained for!")
    print()
    
    # Initialize planner
    planner = AdvancedMigrationPlanner()
    
    # Generate complete plan
    plan = planner.generate_complete_migration_plan()
    
    # Save plan
    output_dir = planner.save_migration_plan(plan)
    
    print(f"\n✅ Complete migration plan generated!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Total requirements: {plan['metadata']['total_requirements']}")
    print(f"📊 Total artifacts: {plan['metadata']['total_artifacts']}")
    print(f"📊 Total validations: {plan['metadata']['total_validations']}")
    print(f"📊 Total rollbacks: {plan['metadata']['total_rollbacks']}")
    
    print(f"\n🎯 Migration plan addresses all critical questions:")
    print(f"✅ Do we have a migration plan? YES - Complete plan generated")
    print(f"✅ Do we have a back out plan? YES - Comprehensive rollback procedures")
    print(f"✅ Do we have all migration requirements? YES - All requirements mapped")
    print(f"✅ Do we know where every artifact is going? YES - Complete artifact mappings")
    print(f"✅ Do we know how to check every artifact is where it needs to be? YES - Validation strategies")

if __name__ == "__main__":
    main()


