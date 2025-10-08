#!/usr/bin/env python3
"""
RC1 Migration Orchestrator
Beast Mode Full Compliance Execution

This orchestrator coordinates all migration agents to execute
the complete RC1 document migration with full compliance.
"""

import json
import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import migration agents
from .migration_planner import MigrationPlannerAgent
from .migration_executor import MigrationExecutorAgent
from .directory_structure_creator import DirectoryStructureCreatorAgent
from .link_reference_updater import LinkReferenceUpdaterAgent
from .validation_system import MigrationValidationSystem
from ..quality.quality_validator import QualityAssuranceAgent


class MigrationOrchestrator:
    """
    RC1 Migration Orchestrator - Beast Mode Execution
    
    Coordinates all migration agents to execute complete document migration
    with full compliance and systematic approach.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        self.logs_dir = self.migration_dir / "logs"
        
        # Create necessary directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize agents
        self.planner = MigrationPlannerAgent(project_root)
        self.executor = MigrationExecutorAgent(project_root)
        self.directory_creator = DirectoryStructureCreatorAgent(project_root)
        self.reference_updater = LinkReferenceUpdaterAgent(project_root)
        self.validator = MigrationValidationSystem(project_root)
        self.quality_agent = QualityAssuranceAgent(project_root)
        
        # Migration state
        self.strategy_file: Optional[str] = None
        self.results_file: Optional[str] = None
        self.migration_success = False
        
        logger.info("Migration Orchestrator initialized")
        logger.info(f"Project root: {self.project_root}")
    
    def execute_complete_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute complete migration with all agents"""
        start_time = datetime.now()
        
        print("🚀 RC1 Migration Orchestrator - Beast Mode Execution")
        print("=" * 70)
        print(f"📅 Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 Dry run: {dry_run}")
        print()
        
        migration_results = {
            'start_time': start_time.isoformat(),
            'dry_run': dry_run,
            'phases': {},
            'success': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Phase 1: Migration Planning
            print("🤖 Phase 1: Migration Planning Agent")
            print("-" * 40)
            strategy = self.planner.generate_migration_strategy()
            self.strategy_file = self.planner.save_migration_strategy(strategy)
            plan_file = self.planner.generate_execution_plan(strategy)
            
            migration_results['phases']['planning'] = {
                'status': 'completed',
                'strategy_file': self.strategy_file,
                'plan_file': plan_file,
                'total_files': strategy.total_files
            }
            
            print(f"✅ Migration strategy created: {strategy.total_files} files")
            print(f"📁 Strategy file: {self.strategy_file}")
            print()
            
            if dry_run:
                print("🔍 DRY RUN MODE - No files will be moved")
                migration_results['success'] = True
                return migration_results
            
            # Phase 2: Directory Structure Creation
            print("🤖 Phase 2: Directory Structure Creator Agent")
            print("-" * 40)
            structure, structure_file = self.directory_creator.create_complete_structure()
            
            migration_results['phases']['directory_creation'] = {
                'status': 'completed',
                'structure_file': structure_file,
                'total_directories': structure.total_directories
            }
            
            print(f"✅ Directory structure created: {structure.total_directories} directories")
            print(f"📁 Structure file: {structure_file}")
            print()
            
            # Phase 3: File Migration Execution
            print("🤖 Phase 3: Migration Executor Agent")
            print("-" * 40)
            migration_summary = self.executor.execute_migration(self.strategy_file, dry_run=False)
            self.results_file = self.executor.save_migration_results(migration_summary)
            
            migration_results['phases']['file_migration'] = {
                'status': 'completed' if migration_summary.failed_migrations == 0 else 'partial',
                'results_file': self.results_file,
                'successful_migrations': migration_summary.successful_migrations,
                'failed_migrations': migration_summary.failed_migrations,
                'total_size_migrated': migration_summary.total_size_migrated
            }
            
            print(f"✅ File migration completed: {migration_summary.successful_migrations}/{migration_summary.total_files}")
            print(f"📦 Size migrated: {migration_summary.total_size_migrated:,} bytes")
            print(f"📁 Results file: {self.results_file}")
            print()
            
            if migration_summary.failed_migrations > 0:
                migration_results['errors'].extend(migration_summary.errors)
                print(f"⚠️  {migration_summary.failed_migrations} migrations failed")
            
            # Phase 4: Reference Updates
            print("🤖 Phase 4: Reference Updater Agent")
            print("-" * 40)
            reference_summary = self.reference_updater.update_all_references(self.strategy_file)
            
            migration_results['phases']['reference_updates'] = {
                'status': 'completed' if reference_summary.total_references_failed == 0 else 'partial',
                'total_references_found': reference_summary.total_references_found,
                'total_references_updated': reference_summary.total_references_updated,
                'total_references_failed': reference_summary.total_references_failed
            }
            
            print(f"✅ Reference updates completed: {reference_summary.total_references_updated}/{reference_summary.total_references_found}")
            print(f"🔗 Broken links fixed: {reference_summary.broken_links_fixed}")
            print()
            
            if reference_summary.total_references_failed > 0:
                migration_results['errors'].extend(reference_summary.update_errors)
                print(f"⚠️  {reference_summary.total_references_failed} reference updates failed")
            
            # Phase 5: Migration Validation
            print("🤖 Phase 5: Validation Agent")
            print("-" * 40)
            validation_summary = self.validator.run_complete_validation(self.strategy_file, self.results_file)
            
            migration_results['phases']['validation'] = {
                'status': 'completed' if validation_summary.failed_checks == 0 else 'partial',
                'total_checks': validation_summary.total_checks,
                'passed_checks': validation_summary.passed_checks,
                'failed_checks': validation_summary.failed_checks,
                'migration_success_rate': validation_summary.migration_success_rate
            }
            
            print(f"✅ Validation completed: {validation_summary.passed_checks}/{validation_summary.total_checks} checks passed")
            print(f"📈 Success rate: {validation_summary.migration_success_rate:.1f}%")
            print()
            
            if validation_summary.failed_checks > 0:
                migration_results['errors'].extend(validation_summary.critical_issues)
                print(f"⚠️  {validation_summary.failed_checks} validation checks failed")
            
            # Phase 6: Quality Assurance
            print("🤖 Phase 6: Quality Assurance Agent")
            print("-" * 40)
            quality_summary = self.quality_agent.run_complete_quality_check()
            
            migration_results['phases']['quality_assurance'] = {
                'status': 'completed' if quality_summary.failed_checks == 0 else 'partial',
                'total_checks': quality_summary.total_checks,
                'passed_checks': quality_summary.passed_checks,
                'failed_checks': quality_summary.failed_checks,
                'quality_score': quality_summary.quality_score
            }
            
            print(f"✅ Quality assurance completed: {quality_summary.passed_checks}/{quality_summary.total_checks} checks passed")
            print(f"📈 Quality score: {quality_summary.quality_score:.1f}%")
            print()
            
            if quality_summary.failed_checks > 0:
                migration_results['errors'].extend(quality_summary.critical_issues)
                print(f"⚠️  {quality_summary.failed_checks} quality checks failed")
            
            # Determine overall success
            total_failures = (
                migration_summary.failed_migrations +
                reference_summary.total_references_failed +
                validation_summary.failed_checks +
                quality_summary.failed_checks
            )
            
            migration_results['success'] = total_failures == 0
            migration_results['end_time'] = datetime.now().isoformat()
            migration_results['total_execution_time'] = (datetime.now() - start_time).total_seconds()
            
            # Final report
            print("🎯 MIGRATION EXECUTION COMPLETE")
            print("=" * 70)
            print(f"📊 Overall success: {'✅ SUCCESS' if migration_results['success'] else '❌ PARTIAL/FAILED'}")
            print(f"⏱️  Total execution time: {migration_results['total_execution_time']:.2f}s")
            print(f"📁 Files migrated: {migration_summary.successful_migrations}/{migration_summary.total_files}")
            print(f"🔗 References updated: {reference_summary.total_references_updated}/{reference_summary.total_references_found}")
            print(f"✅ Validation checks: {validation_summary.passed_checks}/{validation_summary.total_checks}")
            print(f"📈 Quality score: {quality_summary.quality_score:.1f}%")
            
            if migration_results['errors']:
                print(f"\n❌ Errors ({len(migration_results['errors'])}):")
                for error in migration_results['errors'][:5]:
                    print(f"  - {error}")
                if len(migration_results['errors']) > 5:
                    print(f"  ... and {len(migration_results['errors']) - 5} more errors")
            
            # Save final results
            self.save_migration_results(migration_results)
            
            return migration_results
            
        except Exception as e:
            logger.error(f"Migration execution failed: {e}")
            migration_results['success'] = False
            migration_results['errors'].append(f"Migration execution failed: {e}")
            migration_results['end_time'] = datetime.now().isoformat()
            migration_results['total_execution_time'] = (datetime.now() - start_time).total_seconds()
            
            print(f"\n❌ MIGRATION EXECUTION FAILED: {e}")
            return migration_results
    
    def save_migration_results(self, results: Dict[str, Any]) -> str:
        """Save complete migration results"""
        results_file = self.logs_dir / f"migration_orchestrator_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Migration results saved to: {results_file}")
        return str(results_file)
    
    def rollback_migration(self, results_file: str) -> bool:
        """Rollback migration using results file"""
        print("🔄 Rolling back migration...")
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Rollback file migrations
            if 'file_migration' in results['phases'] and 'results_file' in results['phases']['file_migration']:
                migration_results_file = results['phases']['file_migration']['results_file']
                success = self.executor.rollback_migration(migration_results_file)
                
                if success:
                    print("✅ Migration rollback completed successfully")
                    return True
                else:
                    print("❌ Migration rollback failed")
                    return False
            else:
                print("❌ No migration results found for rollback")
                return False
                
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            print(f"❌ Rollback failed: {e}")
            return False


def main():
    """Main execution function for Migration Orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RC1 Migration Orchestrator')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without moving files')
    parser.add_argument('--rollback', help='Rollback migration using results file')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = MigrationOrchestrator()
    
    if args.rollback:
        success = orchestrator.rollback_migration(args.rollback)
        sys.exit(0 if success else 1)
    
    # Execute migration
    results = orchestrator.execute_complete_migration(dry_run=args.dry_run)
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()
