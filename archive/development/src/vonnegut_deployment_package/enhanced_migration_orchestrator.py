#!/usr/bin/env python3
"""
Enhanced RC1 Migration Orchestrator with Integrated Link Validation
Beast Mode Full Compliance Execution with Link Validation

This enhanced orchestrator includes link validation integrated from the start,
applying lessons learned from the original migration process.
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

class EnhancedMigrationOrchestrator:
    """
    Enhanced RC1 Migration Orchestrator with Integrated Link Validation
    
    This orchestrator includes link validation integrated from the start,
    applying lessons learned from the original migration process.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        self.logs_dir = self.migration_dir / "logs"
        self.scripts_dir = self.project_root / "scripts"
        
        # Create necessary directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    def execute_enhanced_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute enhanced migration with integrated link validation
        
        This process includes:
        1. Pre-migration link audit
        2. Hash baseline establishment
        3. Migration planning with validation
        4. Directory structure creation
        5. File migration with integrity validation
        6. Reference updates with link verification
        7. Post-migration validation
        8. Quality assurance
        """
        logger.info("🚀 Starting Enhanced RC1 Migration with Integrated Link Validation")
        
        migration_results = {
            "start_time": datetime.now().isoformat(),
            "dry_run": dry_run,
            "phases": {},
            "success": False,
            "errors": []
        }
        
        try:
            # Phase 1: Pre-Migration Link Audit
            logger.info("📋 Phase 1: Pre-Migration Link Audit")
            link_audit_results = self._pre_migration_link_audit()
            migration_results["phases"]["pre_migration_audit"] = link_audit_results
            
            if not link_audit_results["success"]:
                raise Exception("Pre-migration link audit failed")
            
            # Phase 2: Hash Baseline Establishment
            logger.info("🔍 Phase 2: Hash Baseline Establishment")
            hash_baseline_results = self._establish_hash_baseline()
            migration_results["phases"]["hash_baseline"] = hash_baseline_results
            
            if not hash_baseline_results["success"]:
                raise Exception("Hash baseline establishment failed")
            
            # Phase 3: Migration Planning with Validation
            logger.info("📊 Phase 3: Migration Planning with Validation")
            planning_results = self._enhanced_migration_planning()
            migration_results["phases"]["enhanced_planning"] = planning_results
            
            if not planning_results["success"]:
                raise Exception("Enhanced migration planning failed")
            
            if not dry_run:
                # Phase 4: Directory Structure Creation
                logger.info("🏗️ Phase 4: Directory Structure Creation")
                directory_results = self._create_directory_structure(planning_results["strategy"])
                migration_results["phases"]["directory_creation"] = directory_results
                
                if not directory_results["success"]:
                    raise Exception("Directory structure creation failed")
                
                # Phase 5: File Migration with Integrity Validation
                logger.info("📁 Phase 5: File Migration with Integrity Validation")
                migration_results = self._execute_file_migration_with_validation(
                    planning_results["strategy"], migration_results
                )
                
                if not migration_results["phases"]["file_migration"]["success"]:
                    raise Exception("File migration with validation failed")
                
                # Phase 6: Reference Updates with Link Verification
                logger.info("🔗 Phase 6: Reference Updates with Link Verification")
                reference_results = self._update_references_with_verification()
                migration_results["phases"]["reference_updates"] = reference_results
                
                if not reference_results["success"]:
                    raise Exception("Reference updates with verification failed")
                
                # Phase 7: Post-Migration Validation
                logger.info("✅ Phase 7: Post-Migration Validation")
                validation_results = self._post_migration_validation()
                migration_results["phases"]["post_migration_validation"] = validation_results
                
                if not validation_results["success"]:
                    raise Exception("Post-migration validation failed")
                
                # Phase 8: Quality Assurance
                logger.info("🎯 Phase 8: Quality Assurance")
                quality_results = self._quality_assurance()
                migration_results["phases"]["quality_assurance"] = quality_results
                
                if not quality_results["success"]:
                    raise Exception("Quality assurance failed")
            
            migration_results["success"] = True
            migration_results["end_time"] = datetime.now().isoformat()
            
            logger.info("🎉 Enhanced Migration Completed Successfully!")
            
        except Exception as e:
            logger.error(f"❌ Enhanced Migration Failed: {e}")
            migration_results["errors"].append(str(e))
            migration_results["success"] = False
            migration_results["end_time"] = datetime.now().isoformat()
        
        return migration_results
    
    def _pre_migration_link_audit(self) -> Dict[str, Any]:
        """Pre-migration link audit using hash verification system"""
        logger.info("🔍 Running pre-migration link audit...")
        
        try:
            # Run hash verification to establish baseline
            result = subprocess.run(
                ["./scripts/verify_document_hashes_simple.sh", "verify-all"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pre-migration link audit failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _establish_hash_baseline(self) -> Dict[str, Any]:
        """Establish hash baseline for all documents"""
        logger.info("📊 Establishing hash baseline...")
        
        try:
            # Create hash baseline file
            baseline_file = self.logs_dir / f"hash_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            result = subprocess.run(
                ["find", ".", "-name", "*.md", "-o", "-name", "*.json", "-o", "-name", "*.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                with open(baseline_file, 'w') as f:
                    for file_path in files:
                        if file_path.strip():
                            hash_result = subprocess.run(
                                ["md5sum", file_path],
                                cwd=self.project_root,
                                capture_output=True,
                                text=True
                            )
                            if hash_result.returncode == 0:
                                f.write(hash_result.stdout)
                
                return {
                    "success": True,
                    "baseline_file": str(baseline_file),
                    "files_processed": len(files),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Hash baseline establishment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _enhanced_migration_planning(self) -> Dict[str, Any]:
        """Enhanced migration planning with validation requirements"""
        logger.info("📋 Running enhanced migration planning...")
        
        try:
            # Import and run migration planner
            from src.rc1.migration.migration_planner import MigrationPlannerAgent
            
            planner = MigrationPlannerAgent(str(self.project_root))
            strategy = planner.generate_migration_strategy()
            
            # Add validation requirements to strategy
            strategy["validation_requirements"] = {
                "pre_migration_audit": True,
                "hash_baseline": True,
                "link_validation": True,
                "integrity_validation": True,
                "post_migration_verification": True
            }
            
            return {
                "success": True,
                "strategy": strategy,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced migration planning failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_directory_structure(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create directory structure based on strategy"""
        logger.info("🏗️ Creating directory structure...")
        
        try:
            from src.rc1.migration.directory_structure_creator import DirectoryStructureCreatorAgent
            
            creator = DirectoryStructureCreatorAgent(str(self.project_root))
            result = creator.create_directory_structure(strategy)
            
            return {
                "success": result["success"],
                "directories_created": result.get("directories_created", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Directory structure creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _execute_file_migration_with_validation(self, strategy: Dict[str, Any], migration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file migration with integrity validation"""
        logger.info("📁 Executing file migration with validation...")
        
        try:
            from src.rc1.migration.migration_executor import MigrationExecutorAgent
            
            executor = MigrationExecutorAgent(str(self.project_root))
            result = executor.execute_migration_with_validation(strategy)
            
            migration_results["phases"]["file_migration"] = result
            
            return migration_results
            
        except Exception as e:
            logger.error(f"File migration with validation failed: {e}")
            migration_results["phases"]["file_migration"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return migration_results
    
    def _update_references_with_verification(self) -> Dict[str, Any]:
        """Update references with link verification"""
        logger.info("🔗 Updating references with verification...")
        
        try:
            from src.rc1.migration.link_reference_updater import LinkReferenceUpdaterAgent
            
            updater = LinkReferenceUpdaterAgent(str(self.project_root))
            result = updater.update_references_with_verification()
            
            return {
                "success": result["success"],
                "references_updated": result.get("references_updated", 0),
                "links_verified": result.get("links_verified", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reference updates with verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _post_migration_validation(self) -> Dict[str, Any]:
        """Post-migration validation using hash verification"""
        logger.info("✅ Running post-migration validation...")
        
        try:
            # Run comprehensive hash verification
            result = subprocess.run(
                ["./scripts/verify_document_hashes_simple.sh", "verify-all"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Post-migration validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _quality_assurance(self) -> Dict[str, Any]:
        """Quality assurance with comprehensive checking"""
        logger.info("🎯 Running quality assurance...")
        
        try:
            from src.rc1.quality.quality_validator import QualityAssuranceAgent
            
            validator = QualityAssuranceAgent(str(self.project_root))
            result = validator.run_comprehensive_validation()
            
            return {
                "success": result["success"],
                "checks_passed": result.get("checks_passed", 0),
                "total_checks": result.get("total_checks", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Quality assurance failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def save_enhanced_migration_results(self, results: Dict[str, Any]) -> str:
        """Save enhanced migration results"""
        results_file = self.logs_dir / f"enhanced_migration_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enhanced migration results saved to: {results_file}")
        return str(results_file)


def main():
    """Main execution function for Enhanced Migration Orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced RC1 Migration Orchestrator with Link Validation")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    orchestrator = EnhancedMigrationOrchestrator(args.project_root)
    results = orchestrator.execute_enhanced_migration(dry_run=args.dry_run)
    
    # Save results
    results_file = orchestrator.save_enhanced_migration_results(results)
    
    # Print summary
    print("\n" + "="*60)
    print("🚀 ENHANCED MIGRATION SUMMARY")
    print("="*60)
    print(f"Success: {'✅ YES' if results['success'] else '❌ NO'}")
    print(f"Dry Run: {'✅ YES' if results['dry_run'] else '❌ NO'}")
    print(f"Start Time: {results['start_time']}")
    print(f"End Time: {results['end_time']}")
    print(f"Results File: {results_file}")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("\n📊 Phase Results:")
    for phase, phase_results in results['phases'].items():
        status = "✅" if phase_results.get('success', False) else "❌"
        print(f"  {status} {phase.replace('_', ' ').title()}")
    
    print("="*60)
    
    return 0 if results['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
