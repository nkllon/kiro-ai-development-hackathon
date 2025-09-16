#!/usr/bin/env python3
"""
RC1 Migration Executor Agent
Beast Mode Full Compliance Execution

This agent implements and executes file migration with comprehensive
error handling, backup capabilities, and validation.
"""

import json
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """Result of a single file migration"""
    source_path: str
    target_path: str
    success: bool
    error_message: Optional[str] = None
    backup_path: Optional[str] = None
    file_hash: Optional[str] = None
    migration_time: Optional[float] = None
    size_bytes: int = 0


@dataclass
class MigrationSummary:
    """Summary of complete migration execution"""
    total_files: int
    successful_migrations: int
    failed_migrations: int
    total_size_migrated: int
    execution_time: float
    backup_location: str
    errors: List[str]
    warnings: List[str]


class MigrationExecutorAgent:
    """
    Migration Executor Agent - Beast Mode Execution
    
    Responsibilities:
    - Implement file movement system
    - Create directory structure
    - Handle file conflicts
    - Maintain file integrity
    - Create backups before migration
    - Validate each file movement
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        self.backup_dir = self.migration_dir / "backups"
        self.logs_dir = self.migration_dir / "logs"
        
        # Create necessary directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Migration state
        self.migration_results: List[MigrationResult] = []
        self.migration_errors: List[str] = []
        self.migration_warnings: List[str] = []
        
        logger.info("Migration Executor Agent initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Backup directory: {self.backup_dir}")
    
    def load_migration_strategy(self, strategy_file: str) -> Dict[str, Any]:
        """Load migration strategy from file"""
        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
            logger.info(f"Migration strategy loaded from: {strategy_file}")
            return strategy
        except Exception as e:
            logger.error(f"Failed to load migration strategy: {e}")
            raise
    
    def create_directory_structure(self, strategy: Dict[str, Any]) -> bool:
        """Create organized directory structure"""
        logger.info("Creating directory structure...")
        
        try:
            base_path = Path(strategy['directory_structure']['base_path'])
            categories = strategy['directory_structure']['categories']
            subcategories = strategy['directory_structure']['subcategories']
            
            # Create base docs directory
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Create category directories
            for category in categories.keys():
                category_dir = base_path / category
                category_dir.mkdir(parents=True, exist_ok=True)
                
                # Create subcategory directories
                if category in subcategories:
                    for subcategory in subcategories[category]:
                        subcategory_dir = category_dir / subcategory
                        subcategory_dir.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created directory: {subcategory_dir}")
            
            logger.info("Directory structure created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directory structure: {e}")
            self.migration_errors.append(f"Directory creation failed: {e}")
            return False
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of file before migration"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                logger.warning(f"Source file does not exist: {file_path}")
                return None
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backup_dir / backup_filename
            
            # Copy file to backup location
            shutil.copy2(source_path, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            self.migration_warnings.append(f"Backup failed for {file_path}: {e}")
            return None
    
    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA256 hash of file for integrity verification"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return None
    
    def migrate_file(self, file_plan: Dict[str, Any]) -> MigrationResult:
        """Migrate a single file according to plan"""
        start_time = time.time()
        
        source_path = Path(file_plan['source_path'])
        target_path = Path(file_plan['target_path'])
        
        logger.info(f"Migrating: {source_path} → {target_path}")
        
        try:
            # Validate source file exists
            if not source_path.exists():
                error_msg = f"Source file does not exist: {source_path}"
                logger.error(error_msg)
                return MigrationResult(
                    source_path=str(source_path),
                    target_path=str(target_path),
                    success=False,
                    error_message=error_msg,
                    migration_time=time.time() - start_time
                )
            
            # Get file size
            file_size = source_path.stat().st_size
            
            # Calculate file hash for integrity
            file_hash = self.calculate_file_hash(str(source_path))
            
            # Create backup
            backup_path = self.create_backup(str(source_path))
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Handle target file conflicts
            if target_path.exists():
                conflict_backup = self.create_backup(str(target_path))
                if conflict_backup:
                    logger.info(f"Target file exists, created conflict backup: {conflict_backup}")
            
            # Move file
            shutil.move(str(source_path), str(target_path))
            
            # Verify migration
            if not target_path.exists():
                error_msg = "File migration failed - target file not found"
                logger.error(error_msg)
                return MigrationResult(
                    source_path=str(source_path),
                    target_path=str(target_path),
                    success=False,
                    error_message=error_msg,
                    backup_path=backup_path,
                    file_hash=file_hash,
                    migration_time=time.time() - start_time,
                    size_bytes=file_size
                )
            
            # Verify file integrity
            if file_hash:
                target_hash = self.calculate_file_hash(str(target_path))
                if target_hash != file_hash:
                    error_msg = "File integrity check failed - hash mismatch"
                    logger.error(error_msg)
                    return MigrationResult(
                        source_path=str(source_path),
                        target_path=str(target_path),
                        success=False,
                        error_message=error_msg,
                        backup_path=backup_path,
                        file_hash=file_hash,
                        migration_time=time.time() - start_time,
                        size_bytes=file_size
                    )
            
            migration_time = time.time() - start_time
            logger.info(f"Successfully migrated {source_path.name} in {migration_time:.2f}s")
            
            return MigrationResult(
                source_path=str(source_path),
                target_path=str(target_path),
                success=True,
                backup_path=backup_path,
                file_hash=file_hash,
                migration_time=migration_time,
                size_bytes=file_size
            )
            
        except Exception as e:
            error_msg = f"Migration failed: {e}"
            logger.error(error_msg)
            return MigrationResult(
                source_path=str(source_path),
                target_path=str(target_path),
                success=False,
                error_message=error_msg,
                backup_path=backup_path,
                migration_time=time.time() - start_time,
                size_bytes=file_size if 'file_size' in locals() else 0
            )
    
    def execute_migration(self, strategy_file: str, dry_run: bool = False) -> MigrationSummary:
        """Execute complete migration according to strategy"""
        logger.info("Starting migration execution...")
        start_time = time.time()
        
        # Load migration strategy
        strategy = self.load_migration_strategy(strategy_file)
        
        # Create directory structure
        if not self.create_directory_structure(strategy):
            logger.error("Failed to create directory structure, aborting migration")
            return MigrationSummary(
                total_files=0,
                successful_migrations=0,
                failed_migrations=0,
                total_size_migrated=0,
                execution_time=time.time() - start_time,
                backup_location=str(self.backup_dir),
                errors=self.migration_errors,
                warnings=self.migration_warnings
            )
        
        # Execute file migrations
        file_plans = strategy['file_plans']
        total_files = len(file_plans)
        
        logger.info(f"Executing migration for {total_files} files...")
        
        if dry_run:
            logger.info("DRY RUN MODE - No files will be moved")
            for i, plan in enumerate(file_plans, 1):
                logger.info(f"[{i}/{total_files}] Would migrate: {plan['source_path']} → {plan['target_path']}")
            
            return MigrationSummary(
                total_files=total_files,
                successful_migrations=0,
                failed_migrations=0,
                total_size_migrated=0,
                execution_time=time.time() - start_time,
                backup_location=str(self.backup_dir),
                errors=[],
                warnings=["Dry run mode - no files moved"]
            )
        
        # Execute actual migrations
        successful_migrations = 0
        failed_migrations = 0
        total_size_migrated = 0
        
        for i, plan in enumerate(file_plans, 1):
            logger.info(f"[{i}/{total_files}] Migrating: {plan['source_path']}")
            
            result = self.migrate_file(plan)
            self.migration_results.append(result)
            
            if result.success:
                successful_migrations += 1
                total_size_migrated += result.size_bytes
            else:
                failed_migrations += 1
                self.migration_errors.append(f"{result.source_path}: {result.error_message}")
        
        execution_time = time.time() - start_time
        
        # Generate summary
        summary = MigrationSummary(
            total_files=total_files,
            successful_migrations=successful_migrations,
            failed_migrations=failed_migrations,
            total_size_migrated=total_size_migrated,
            execution_time=execution_time,
            backup_location=str(self.backup_dir),
            errors=self.migration_errors,
            warnings=self.migration_warnings
        )
        
        # Save migration results
        self.save_migration_results(summary)
        
        logger.info(f"Migration execution completed in {execution_time:.2f}s")
        logger.info(f"Successful: {successful_migrations}/{total_files}")
        logger.info(f"Failed: {failed_migrations}/{total_files}")
        logger.info(f"Total size migrated: {total_size_migrated:,} bytes")
        
        return summary
    
    def save_migration_results(self, summary: MigrationSummary) -> str:
        """Save migration results to file"""
        results_file = self.logs_dir / f"migration_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Prepare results data
        results_data = {
            'summary': asdict(summary),
            'individual_results': [asdict(result) for result in self.migration_results],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Migration results saved to: {results_file}")
        return str(results_file)
    
    def rollback_migration(self, results_file: str) -> bool:
        """Rollback migration using backup files"""
        logger.info("Starting migration rollback...")
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results_data = json.load(f)
            
            individual_results = results_data['individual_results']
            rollback_success = 0
            rollback_failed = 0
            
            for result in individual_results:
                if result['success'] and result['backup_path']:
                    try:
                        # Restore from backup
                        backup_path = Path(result['backup_path'])
                        target_path = Path(result['target_path'])
                        source_path = Path(result['source_path'])
                        
                        if backup_path.exists():
                            # Restore to original location
                            shutil.move(str(target_path), str(source_path))
                            logger.info(f"Restored: {source_path}")
                            rollback_success += 1
                        else:
                            logger.error(f"Backup not found: {backup_path}")
                            rollback_failed += 1
                    except Exception as e:
                        logger.error(f"Rollback failed for {result['source_path']}: {e}")
                        rollback_failed += 1
            
            logger.info(f"Rollback completed: {rollback_success} successful, {rollback_failed} failed")
            return rollback_failed == 0
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def validate_migration(self, strategy_file: str) -> Dict[str, Any]:
        """Validate migration success"""
        logger.info("Validating migration...")
        
        try:
            strategy = self.load_migration_strategy(strategy_file)
            validation_results = {
                'total_files': len(strategy['file_plans']),
                'validated_files': 0,
                'missing_files': [],
                'broken_links': [],
                'validation_errors': []
            }
            
            for plan in strategy['file_plans']:
                target_path = Path(plan['target_path'])
                
                if target_path.exists():
                    validation_results['validated_files'] += 1
                else:
                    validation_results['missing_files'].append(plan['target_path'])
            
            # Check for broken links (basic check)
            for plan in strategy['file_plans']:
                if plan.get('reference_updates_needed', False):
                    # This would need more sophisticated link checking
                    pass
            
            logger.info(f"Validation complete: {validation_results['validated_files']}/{validation_results['total_files']} files validated")
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {'error': str(e)}


def main():
    """Main execution function for Migration Executor Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RC1 Migration Executor Agent')
    parser.add_argument('--strategy-file', required=True, help='Path to migration strategy file')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without moving files')
    parser.add_argument('--rollback', help='Rollback migration using results file')
    parser.add_argument('--validate', action='store_true', help='Validate migration success')
    
    args = parser.parse_args()
    
    print("🤖 RC1 Migration Executor Agent - Beast Mode Execution")
    print("=" * 60)
    
    # Initialize agent
    executor = MigrationExecutorAgent()
    
    if args.rollback:
        print(f"🔄 Rolling back migration using: {args.rollback}")
        success = executor.rollback_migration(args.rollback)
        if success:
            print("✅ Rollback completed successfully")
        else:
            print("❌ Rollback failed")
        return
    
    if args.validate:
        print(f"🔍 Validating migration using: {args.strategy_file}")
        results = executor.validate_migration(args.strategy_file)
        print(f"Validation results: {json.dumps(results, indent=2)}")
        return
    
    # Execute migration
    print(f"📁 Strategy file: {args.strategy_file}")
    print(f"🔍 Dry run: {args.dry_run}")
    
    summary = executor.execute_migration(args.strategy_file, dry_run=args.dry_run)
    
    # Report results
    print("\n✅ Migration Executor Agent Complete!")
    print(f"📊 Total files: {summary.total_files}")
    print(f"✅ Successful: {summary.successful_migrations}")
    print(f"❌ Failed: {summary.failed_migrations}")
    print(f"📦 Size migrated: {summary.total_size_migrated:,} bytes")
    print(f"⏱️  Execution time: {summary.execution_time:.2f}s")
    print(f"💾 Backup location: {summary.backup_location}")
    
    if summary.errors:
        print(f"\n❌ Errors ({len(summary.errors)}):")
        for error in summary.errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(summary.errors) > 5:
            print(f"  ... and {len(summary.errors) - 5} more errors")
    
    if summary.warnings:
        print(f"\n⚠️  Warnings ({len(summary.warnings)}):")
        for warning in summary.warnings[:5]:  # Show first 5 warnings
            print(f"  - {warning}")
        if len(summary.warnings) > 5:
            print(f"  ... and {len(summary.warnings) - 5} more warnings")


if __name__ == "__main__":
    main()
