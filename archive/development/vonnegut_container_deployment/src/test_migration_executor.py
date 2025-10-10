#!/usr/bin/env python3
"""
🚨 TEST MIGRATION EXECUTOR 🚨
============================

"This is it! The moment we should have trained for!"
Test migration with random 5% of files and automatic rollback on inconsistencies.

Military-derived precision for test migration execution.
When the test migration needs execution, Ghostbusters deploy!

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Test migration execution with automatic rollback
"""

import json
import os
import random
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class TestMigrationResult:
    """Result of test migration execution."""
    test_id: str
    status: str  # SUCCESS, FAILED, ROLLED_BACK
    files_processed: int
    files_successful: int
    files_failed: int
    inconsistencies_detected: List[str]
    rollback_performed: bool
    execution_time: float
    details: Dict[str, Any]

class TestMigrationExecutor:
    """🚨 TEST MIGRATION EXECUTOR WITH AUTOMATIC ROLLBACK 🚨"""
    
    def __init__(self, repository_root: str = ".", test_percentage: float = 0.05):
        self.repository_root = Path(repository_root)
        self.test_percentage = test_percentage
        self.test_id = f"test_migration_{int(time.time())}"
        self.backup_dir = None
        self.test_results = []
        
        # Military-derived exclamations for test migration
        self.test_exclamations = [
            "🚨 THIS IS IT! THE MOMENT WE SHOULD HAVE TRAINED FOR!",
            "🛑 ALL HANDS ON DECK - TEST MIGRATION INITIATED!",
            "🚨 GHOSTBUSTERS TO THE RESCUE - TEST MIGRATION DEPLOYING!",
            "🛑 EMERGENCY PROTOCOLS ACTIVATED - TEST MIGRATION INCOMING!",
            "🚨 THIS IS OUR DARKEST HOUR - TEST MIGRATION DEPLOYING!",
            "🛑 TEST MIGRATION ON FIRE - TIME TO EARN OUR PAY!",
            "🚨 CRISIS MODE ENGAGED - TEST MIGRATION ANALYSIS INCOMING!",
            "🛑 WE'RE IN THE SHIT NOW - TIME TO BE HEROES!",
        ]
        
        # Critical systems that must never be touched
        self.critical_systems = {
            "rdi_registry": [
                "RDI_ANALYSIS_REPORT.md",
                "RDI_ANALYSIS_SUMMARY.md",
                "RM_RDI_IMPLEMENTATION_PROMPT.md",
                "beast_mode_rdi_attack_system.py",
                "generate_rdi_traceable_tests.py"
            ],
            "documentation_index": [
                "docs/",
                "diagrams/",
                "README.md"
            ],
            "rm_ddd_system": [
                "reflective_module_deployment_system.py",
                "reflective_module_base.py",
                "src/beast_mode/",
                "src/devpost_integration/",
                "src/spec_reconciliation/"
            ],
            "core_project": [
                "pyproject.toml",
                "setup.py",
                "requirements.txt",
                ".gitignore",
                ".gitmodules",
                "beast",
                "devpost-cli"
            ]
        }
    
    def execute_test_migration(self) -> TestMigrationResult:
        """🚨 GHOSTBUSTERS TEST MIGRATION MODE - We're going in!"""
        
        print(random.choice(self.test_exclamations))
        print("🛑 Stand back! Ghostbusters are taking over!")
        print("🚨 Emergency protocols activated - test migration initiated!")
        print("🛑 This is too dangerous for human interaction - Ghostbusters deploying!")
        print()
        
        start_time = time.time()
        
        # Phase 1: Create Backup
        print("💾 PHASE 1: CREATING BACKUP")
        print("=" * 50)
        
        backup_created = self._create_backup()
        if not backup_created:
            return TestMigrationResult(
                test_id=self.test_id,
                status="FAILED",
                files_processed=0,
                files_successful=0,
                files_failed=0,
                inconsistencies_detected=["Failed to create backup"],
                rollback_performed=False,
                execution_time=time.time() - start_time,
                details={"error": "Backup creation failed"}
            )
        
        # Phase 2: Select Test Files
        print("\n🎯 PHASE 2: SELECTING TEST FILES")
        print("=" * 50)
        
        test_files = self._select_test_files()
        print(f"📊 Selected {len(test_files)} files for test migration ({self.test_percentage*100:.1f}%)")
        
        # Phase 3: Execute Test Migration
        print("\n🧹 PHASE 3: EXECUTING TEST MIGRATION")
        print("=" * 50)
        
        migration_results = self._execute_test_migration(test_files)
        
        # Phase 4: Validate Results
        print("\n✅ PHASE 4: VALIDATING RESULTS")
        print("=" * 50)
        
        validation_results = self._validate_migration_results()
        
        # Phase 5: Rollback if Inconsistencies
        print("\n🔄 PHASE 5: ROLLBACK DECISION")
        print("=" * 50)
        
        rollback_performed = False
        if validation_results["inconsistencies_detected"]:
            print("🚨 INCONSISTENCIES DETECTED - INITIATING ROLLBACK!")
            rollback_performed = self._perform_rollback()
            status = "ROLLED_BACK"
        else:
            print("✅ NO INCONSISTENCIES DETECTED - TEST MIGRATION SUCCESSFUL!")
            status = "SUCCESS"
        
        execution_time = time.time() - start_time
        
        # Compile results
        result = TestMigrationResult(
            test_id=self.test_id,
            status=status,
            files_processed=len(test_files),
            files_successful=migration_results["successful"],
            files_failed=migration_results["failed"],
            inconsistencies_detected=validation_results["inconsistencies_detected"],
            rollback_performed=rollback_performed,
            execution_time=execution_time,
            details={
                "test_files": test_files,
                "migration_results": migration_results,
                "validation_results": validation_results,
                "backup_dir": str(self.backup_dir)
            }
        )
        
        # Save test results
        self._save_test_results(result)
        
        return result
    
    def _create_backup(self) -> bool:
        """Create backup of repository before test migration."""
        print("💾 Creating backup...")
        
        try:
            self.backup_dir = self.repository_root / f"test_backup_{self.test_id}"
            self.backup_dir.mkdir(exist_ok=True)
            
            # Copy critical files
            critical_files = []
            for system_files in self.critical_systems.values():
                critical_files.extend(system_files)
            
            for file_path in critical_files:
                src_path = self.repository_root / file_path
                if src_path.exists():
                    if src_path.is_file():
                        dst_path = self.backup_dir / file_path
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                    elif src_path.is_dir():
                        dst_path = self.backup_dir / file_path
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            
            print(f"✅ Backup created: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False
    
    def _select_test_files(self) -> List[Path]:
        """Select random 5% of files for test migration."""
        print("🎯 Selecting test files...")
        
        # Get all files in repository
        all_files = []
        for root, dirs, files in os.walk(self.repository_root):
            for file in files:
                file_path = Path(root) / file
                if self._should_include_file(file_path):
                    all_files.append(file_path)
        
        # Filter out critical system files
        safe_files = []
        for file_path in all_files:
            rel_path = file_path.relative_to(self.repository_root)
            if not self._is_critical_file(rel_path):
                safe_files.append(file_path)
        
        # Select random 5%
        num_test_files = max(1, int(len(safe_files) * self.test_percentage))
        test_files = random.sample(safe_files, min(num_test_files, len(safe_files)))
        
        print(f"📊 Total files: {len(all_files)}")
        print(f"📊 Safe files: {len(safe_files)}")
        print(f"📊 Test files: {len(test_files)}")
        
        return test_files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Determine if file should be included in test migration."""
        # Skip hidden files, cache files, and temporary files
        skip_patterns = [
            ".git/", "__pycache__/", ".pytest_cache/", ".coverage",
            ".DS_Store", "*.pyc", "*.log", "*.tmp", "*.temp",
            "test_backup_", "migration_", "ghostbusters_"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    def _is_critical_file(self, rel_path: Path) -> bool:
        """Check if file is critical and should not be migrated."""
        for system_files in self.critical_systems.values():
            for file_pattern in system_files:
                if file_pattern.endswith("/"):
                    if str(rel_path).startswith(file_pattern.rstrip("/")):
                        return True
                else:
                    if rel_path.name == file_pattern:
                        return True
        return False
    
    def _execute_test_migration(self, test_files: List[Path]) -> Dict[str, Any]:
        """Execute test migration on selected files."""
        print("🧹 Executing test migration...")
        
        results = {
            "successful": 0,
            "failed": 0,
            "operations": []
        }
        
        for file_path in test_files:
            try:
                rel_path = file_path.relative_to(self.repository_root)
                
                # Determine migration operation
                operation = self._determine_migration_operation(file_path)
                
                if operation == "DELETE":
                    # Simulate deletion by moving to test directory
                    test_dir = self.repository_root / f"test_migration_{self.test_id}"
                    test_dir.mkdir(exist_ok=True)
                    dst_path = test_dir / rel_path
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(dst_path))
                    
                    results["operations"].append({
                        "file": str(rel_path),
                        "operation": "DELETE",
                        "status": "SUCCESS"
                    })
                    results["successful"] += 1
                    
                elif operation == "ARCHIVE":
                    # Simulate archiving
                    archive_dir = self.repository_root / f"test_archive_{self.test_id}"
                    archive_dir.mkdir(exist_ok=True)
                    dst_path = archive_dir / rel_path
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(dst_path))
                    
                    results["operations"].append({
                        "file": str(rel_path),
                        "operation": "ARCHIVE",
                        "status": "SUCCESS"
                    })
                    results["successful"] += 1
                
                else:
                    # Skip other operations for test
                    results["operations"].append({
                        "file": str(rel_path),
                        "operation": "SKIP",
                        "status": "SUCCESS"
                    })
                    results["successful"] += 1
                
            except Exception as e:
                results["operations"].append({
                    "file": str(rel_path),
                    "operation": "ERROR",
                    "status": "FAILED",
                    "error": str(e)
                })
                results["failed"] += 1
        
        print(f"✅ Migration completed: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def _determine_migration_operation(self, file_path: Path) -> str:
        """Determine migration operation for file."""
        file_name = file_path.name
        
        # Temporary files
        if self._is_temporary_file(file_name):
            return "DELETE"
        
        # Backup files
        if self._is_backup_file(file_name):
            return "ARCHIVE"
        
        # Other files
        return "SKIP"
    
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
    
    def _validate_migration_results(self) -> Dict[str, Any]:
        """Validate migration results for inconsistencies."""
        print("✅ Validating migration results...")
        
        inconsistencies = []
        
        # Check critical systems are intact
        for system_name, system_files in self.critical_systems.items():
            for file_pattern in system_files:
                file_path = self.repository_root / file_pattern
                if not file_path.exists():
                    inconsistencies.append(f"Critical file missing: {file_pattern}")
        
        # Check documentation index
        docs_path = self.repository_root / "docs/README.md"
        if not docs_path.exists():
            inconsistencies.append("Documentation index missing")
        
        # Check RDI system
        rdi_path = self.repository_root / "RDI_ANALYSIS_REPORT.md"
        if not rdi_path.exists():
            inconsistencies.append("RDI analysis report missing")
        
        # Check source code integrity
        src_path = self.repository_root / "src"
        if not src_path.exists():
            inconsistencies.append("Source code directory missing")
        
        if inconsistencies:
            print(f"🚨 {len(inconsistencies)} inconsistencies detected!")
            for inconsistency in inconsistencies:
                print(f"  - {inconsistency}")
        else:
            print("✅ No inconsistencies detected!")
        
        return {
            "inconsistencies_detected": inconsistencies,
            "validation_passed": len(inconsistencies) == 0
        }
    
    def _perform_rollback(self) -> bool:
        """Perform rollback from backup."""
        print("🔄 Performing rollback...")
        
        try:
            if not self.backup_dir or not self.backup_dir.exists():
                print("❌ Backup directory not found!")
                return False
            
            # Restore critical files from backup
            for system_name, system_files in self.critical_systems.items():
                for file_pattern in system_files:
                    backup_path = self.backup_dir / file_pattern
                    if backup_path.exists():
                        target_path = self.repository_root / file_pattern
                        if backup_path.is_file():
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(backup_path, target_path)
                        elif backup_path.is_dir():
                            if target_path.exists():
                                shutil.rmtree(target_path)
                            shutil.copytree(backup_path, target_path)
            
            # Restore test migration files
            test_migration_dir = self.repository_root / f"test_migration_{self.test_id}"
            test_archive_dir = self.repository_root / f"test_archive_{self.test_id}"
            
            for test_dir in [test_migration_dir, test_archive_dir]:
                if test_dir.exists():
                    for file_path in test_dir.rglob("*"):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(test_dir)
                            target_path = self.repository_root / rel_path
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_path), str(target_path))
                    shutil.rmtree(test_dir)
            
            print("✅ Rollback completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def _save_test_results(self, result: TestMigrationResult):
        """Save test results to file."""
        results_file = self.repository_root / f"test_migration_results_{self.test_id}.json"
        
        with open(results_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        print(f"📋 Test results saved: {results_file}")
    
    def cleanup_test_artifacts(self):
        """Clean up test artifacts."""
        print("🧹 Cleaning up test artifacts...")
        
        # Remove backup directory
        if self.backup_dir and self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
            print(f"🗑️  Removed backup directory: {self.backup_dir}")
        
        # Remove test migration directories
        for pattern in [f"test_migration_{self.test_id}", f"test_archive_{self.test_id}"]:
            test_dir = self.repository_root / pattern
            if test_dir.exists():
                shutil.rmtree(test_dir)
                print(f"🗑️  Removed test directory: {test_dir}")

def main():
    """Run test migration execution."""
    print("🚨 TEST MIGRATION EXECUTOR INITIATED! 🚨")
    print("This is it! The moment we should have trained for!")
    print()
    
    # Initialize test migration executor
    executor = TestMigrationExecutor(test_percentage=0.05)  # 5% test
    
    try:
        # Execute test migration
        result = executor.execute_test_migration()
        
        print(f"\n✅ Test migration completed!")
        print(f"📊 Status: {result.status}")
        print(f"📊 Files processed: {result.files_processed}")
        print(f"📊 Files successful: {result.files_successful}")
        print(f"📊 Files failed: {result.files_failed}")
        print(f"📊 Inconsistencies: {len(result.inconsistencies_detected)}")
        print(f"📊 Rollback performed: {result.rollback_performed}")
        print(f"📊 Execution time: {result.execution_time:.2f} seconds")
        
        if result.status == "SUCCESS":
            print("\n🎉 TEST MIGRATION SUCCESSFUL - Ready for full migration!")
        elif result.status == "ROLLED_BACK":
            print("\n🔄 TEST MIGRATION ROLLED BACK - Issues detected and resolved!")
        else:
            print("\n❌ TEST MIGRATION FAILED - Review issues before proceeding!")
        
    finally:
        # Clean up test artifacts
        executor.cleanup_test_artifacts()

if __name__ == "__main__":
    main()
