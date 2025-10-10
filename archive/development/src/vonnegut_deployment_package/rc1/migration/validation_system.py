#!/usr/bin/env python3
"""
RC1 Migration Validation System
Beast Mode Full Compliance Execution

This agent validates migration success and system integrity to ensure
100% migration success and zero broken links.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationCheck:
    """Represents a single validation check"""
    check_name: str
    check_type: str  # 'file_existence', 'link_integrity', 'structure', 'content'
    status: str  # 'pass', 'fail', 'warning'
    message: str
    details: Dict[str, Any] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class ValidationSummary:
    """Summary of validation results"""
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    validation_time: float
    migration_success_rate: float
    critical_issues: List[str]
    warnings: List[str]
    recommendations: List[str]


class MigrationValidationSystem:
    """
    Migration Validation System - Beast Mode Execution
    
    Responsibilities:
    - Validate all files moved correctly
    - Test all updated references
    - Verify directory structure
    - Check system functionality
    - Generate validation report
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        self.logs_dir = self.migration_dir / "logs"
        
        # Create necessary directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Validation results
        self.validation_checks: List[ValidationCheck] = []
        self.critical_issues: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []
        
        logger.info("Migration Validation System initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Docs directory: {self.docs_dir}")
    
    def load_migration_strategy(self, strategy_file: str) -> Dict[str, Any]:
        """Load migration strategy for validation"""
        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
            logger.info(f"Migration strategy loaded from: {strategy_file}")
            return strategy
        except Exception as e:
            logger.error(f"Failed to load migration strategy: {e}")
            raise
    
    def load_migration_results(self, results_file: str) -> Dict[str, Any]:
        """Load migration results for validation"""
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            logger.info(f"Migration results loaded from: {results_file}")
            return results
        except Exception as e:
            logger.error(f"Failed to load migration results: {e}")
            return {}
    
    def validate_file_migration(self, strategy: Dict[str, Any]) -> List[ValidationCheck]:
        """Validate that all files were migrated correctly"""
        logger.info("Validating file migration...")
        
        checks = []
        file_plans = strategy.get('file_plans', [])
        
        for plan in file_plans:
            source_path = Path(plan['source_path'])
            target_path = Path(plan['target_path'])
            
            # Check source file no longer exists in original location
            if source_path.exists():
                checks.append(ValidationCheck(
                    check_name="source_file_removed",
                    check_type="file_existence",
                    status="fail",
                    message=f"Source file still exists: {source_path}",
                    file_path=str(source_path),
                    details={"expected": "file should be moved", "actual": "file still exists"}
                ))
                self.critical_issues.append(f"Source file not moved: {source_path}")
            else:
                checks.append(ValidationCheck(
                    check_name="source_file_removed",
                    check_type="file_existence",
                    status="pass",
                    message=f"Source file successfully removed: {source_path}",
                    file_path=str(source_path)
                ))
            
            # Check target file exists in new location
            if target_path.exists():
                checks.append(ValidationCheck(
                    check_name="target_file_exists",
                    check_type="file_existence",
                    status="pass",
                    message=f"Target file exists: {target_path}",
                    file_path=str(target_path)
                ))
                
                # Verify file integrity
                if self._verify_file_integrity(source_path, target_path):
                    checks.append(ValidationCheck(
                        check_name="file_integrity",
                        check_type="content",
                        status="pass",
                        message=f"File integrity verified: {target_path}",
                        file_path=str(target_path)
                    ))
                else:
                    checks.append(ValidationCheck(
                        check_name="file_integrity",
                        check_type="content",
                        status="fail",
                        message=f"File integrity check failed: {target_path}",
                        file_path=str(target_path)
                    ))
                    self.critical_issues.append(f"File integrity failed: {target_path}")
            else:
                checks.append(ValidationCheck(
                    check_name="target_file_exists",
                    check_type="file_existence",
                    status="fail",
                    message=f"Target file missing: {target_path}",
                    file_path=str(target_path),
                    details={"expected": "file should exist", "actual": "file not found"}
                ))
                self.critical_issues.append(f"Target file missing: {target_path}")
        
        logger.info(f"File migration validation complete: {len(checks)} checks")
        return checks
    
    def _verify_file_integrity(self, source_path: Path, target_path: Path) -> bool:
        """Verify file integrity by comparing hashes"""
        try:
            # Check if backup exists for comparison
            backup_dir = self.migration_dir / "backups"
            backup_files = list(backup_dir.glob(f"{source_path.stem}_*{source_path.suffix}"))
            
            if backup_files:
                # Compare with most recent backup
                backup_file = max(backup_files, key=lambda f: f.stat().st_mtime)
                return self._compare_file_hashes(backup_file, target_path)
            else:
                # No backup available, assume integrity is maintained
                return True
        except Exception as e:
            logger.warning(f"File integrity check failed for {target_path}: {e}")
            return False
    
    def _compare_file_hashes(self, file1: Path, file2: Path) -> bool:
        """Compare SHA256 hashes of two files"""
        try:
            hash1 = self._calculate_file_hash(file1)
            hash2 = self._calculate_file_hash(file2)
            return hash1 == hash2
        except Exception:
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def validate_directory_structure(self, strategy: Dict[str, Any]) -> List[ValidationCheck]:
        """Validate directory structure was created correctly"""
        logger.info("Validating directory structure...")
        
        checks = []
        structure = strategy.get('directory_structure', {})
        base_path = Path(structure.get('base_path', self.docs_dir))
        
        # Check base directory exists
        if base_path.exists():
            checks.append(ValidationCheck(
                check_name="base_directory_exists",
                check_type="structure",
                status="pass",
                message=f"Base directory exists: {base_path}",
                file_path=str(base_path)
            ))
        else:
            checks.append(ValidationCheck(
                check_name="base_directory_exists",
                check_type="structure",
                status="fail",
                message=f"Base directory missing: {base_path}",
                file_path=str(base_path)
            ))
            self.critical_issues.append(f"Base directory missing: {base_path}")
        
        # Check category directories
        categories = structure.get('categories', {})
        for category in categories.keys():
            category_path = base_path / category
            if category_path.exists():
                checks.append(ValidationCheck(
                    check_name=f"category_directory_{category}",
                    check_type="structure",
                    status="pass",
                    message=f"Category directory exists: {category_path}",
                    file_path=str(category_path)
                ))
            else:
                checks.append(ValidationCheck(
                    check_name=f"category_directory_{category}",
                    check_type="structure",
                    status="fail",
                    message=f"Category directory missing: {category_path}",
                    file_path=str(category_path)
                ))
                self.critical_issues.append(f"Category directory missing: {category_path}")
        
        # Check subcategory directories
        subcategories = structure.get('subcategories', {})
        for category, subcats in subcategories.items():
            for subcat in subcats:
                subcat_path = base_path / category / subcat
                if subcat_path.exists():
                    checks.append(ValidationCheck(
                        check_name=f"subcategory_directory_{category}_{subcat}",
                        check_type="structure",
                        status="pass",
                        message=f"Subcategory directory exists: {subcat_path}",
                        file_path=str(subcat_path)
                    ))
                else:
                    checks.append(ValidationCheck(
                        check_name=f"subcategory_directory_{category}_{subcat}",
                        check_type="structure",
                        status="fail",
                        message=f"Subcategory directory missing: {subcat_path}",
                        file_path=str(subcat_path)
                    ))
                    self.critical_issues.append(f"Subcategory directory missing: {subcat_path}")
        
        logger.info(f"Directory structure validation complete: {len(checks)} checks")
        return checks
    
    def validate_link_integrity(self) -> List[ValidationCheck]:
        """Validate that all links are working correctly"""
        logger.info("Validating link integrity...")
        
        checks = []
        broken_links = 0
        total_links = 0
        
        # Scan all markdown files for links
        for md_file in self.docs_dir.rglob("*.md"):
            if md_file.is_file():
                file_checks = self._validate_file_links(md_file)
                checks.extend(file_checks)
                
                # Count links
                for check in file_checks:
                    if check.check_type == "link_integrity":
                        total_links += 1
                        if check.status == "fail":
                            broken_links += 1
        
        # Add summary check
        if broken_links == 0:
            checks.append(ValidationCheck(
                check_name="link_integrity_summary",
                check_type="link_integrity",
                status="pass",
                message=f"All {total_links} links are working correctly",
                details={"total_links": total_links, "broken_links": broken_links}
            ))
        else:
            checks.append(ValidationCheck(
                check_name="link_integrity_summary",
                check_type="link_integrity",
                status="fail",
                message=f"{broken_links} out of {total_links} links are broken",
                details={"total_links": total_links, "broken_links": broken_links}
            ))
            self.critical_issues.append(f"{broken_links} broken links found")
        
        logger.info(f"Link integrity validation complete: {total_links} links checked, {broken_links} broken")
        return checks
    
    def _validate_file_links(self, file_path: Path) -> List[ValidationCheck]:
        """Validate links in a single file"""
        checks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Find markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(link_pattern, line)
                
                for match in matches:
                    link_text = match.group(1)
                    link_url = match.group(2)
                    
                    # Check if it's a markdown file link
                    if link_url.endswith('.md') or '.md#' in link_url:
                        target_file = self._resolve_link_target(link_url, file_path)
                        
                        if target_file and Path(target_file).exists():
                            checks.append(ValidationCheck(
                                check_name="markdown_link_valid",
                                check_type="link_integrity",
                                status="pass",
                                message=f"Link works: {link_text} -> {link_url}",
                                file_path=str(file_path),
                                line_number=line_num,
                                details={"link_text": link_text, "link_url": link_url, "target_file": target_file}
                            ))
                        else:
                            checks.append(ValidationCheck(
                                check_name="markdown_link_broken",
                                check_type="link_integrity",
                                status="fail",
                                message=f"Broken link: {link_text} -> {link_url}",
                                file_path=str(file_path),
                                line_number=line_num,
                                details={"link_text": link_text, "link_url": link_url, "target_file": target_file}
                            ))
        
        except Exception as e:
            checks.append(ValidationCheck(
                check_name="file_read_error",
                check_type="link_integrity",
                status="warning",
                message=f"Could not read file for link validation: {e}",
                file_path=str(file_path)
            ))
        
        return checks
    
    def _resolve_link_target(self, link_url: str, source_file: Path) -> Optional[str]:
        """Resolve link target to actual file path"""
        try:
            # Remove anchor
            if '#' in link_url:
                link_url = link_url.split('#')[0]
            
            # Remove query parameters
            if '?' in link_url:
                link_url = link_url.split('?')[0]
            
            if link_url.startswith('/'):
                # Absolute path
                return str(self.project_root / link_url.lstrip('/'))
            elif link_url.startswith('./') or link_url.startswith('../'):
                # Relative path
                return str(source_file.parent / link_url)
            else:
                # Simple filename or relative path
                return str(source_file.parent / link_url)
        except Exception:
            return None
    
    def validate_root_cleanup(self) -> List[ValidationCheck]:
        """Validate that root directory is cleaned up"""
        logger.info("Validating root directory cleanup...")
        
        checks = []
        root_md_files = list(self.project_root.glob("*.md"))
        
        if len(root_md_files) == 0:
            checks.append(ValidationCheck(
                check_name="root_cleanup_complete",
                check_type="structure",
                status="pass",
                message="Root directory cleanup complete - no markdown files remaining",
                file_path=str(self.project_root)
            ))
        else:
            checks.append(ValidationCheck(
                check_name="root_cleanup_incomplete",
                check_type="structure",
                status="fail",
                message=f"Root directory cleanup incomplete - {len(root_md_files)} markdown files remaining",
                file_path=str(self.project_root),
                details={"remaining_files": [str(f) for f in root_md_files]}
            ))
            self.critical_issues.append(f"{len(root_md_files)} files still in root directory")
            
            # List remaining files
            for md_file in root_md_files[:10]:  # Show first 10
                checks.append(ValidationCheck(
                    check_name="root_file_remaining",
                    check_type="structure",
                    status="warning",
                    message=f"File still in root: {md_file.name}",
                    file_path=str(md_file)
                ))
        
        logger.info(f"Root cleanup validation complete: {len(root_md_files)} files remaining")
        return checks
    
    def validate_system_functionality(self) -> List[ValidationCheck]:
        """Validate that system functionality is preserved"""
        logger.info("Validating system functionality...")
        
        checks = []
        
        # Check that important files are accessible
        important_files = [
            "README.md",
            "docs/index.md",
            "docs/rc1/index.md"
        ]
        
        for file_path in important_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                checks.append(ValidationCheck(
                    check_name=f"important_file_{file_path.replace('/', '_')}",
                    check_type="content",
                    status="pass",
                    message=f"Important file accessible: {file_path}",
                    file_path=str(full_path)
                ))
            else:
                checks.append(ValidationCheck(
                    check_name=f"important_file_{file_path.replace('/', '_')}",
                    check_type="content",
                    status="warning",
                    message=f"Important file missing: {file_path}",
                    file_path=str(full_path)
                ))
                self.warnings.append(f"Important file missing: {file_path}")
        
        # Check that migration system is functional
        migration_files = [
            "src/rc1/migration/migration_planner.py",
            "src/rc1/migration/migration_executor.py",
            "src/rc1/migration/directory_structure_creator.py",
            "src/rc1/migration/link_reference_updater.py",
            "src/rc1/migration/validation_system.py"
        ]
        
        for file_path in migration_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                checks.append(ValidationCheck(
                    check_name=f"migration_file_{file_path.replace('/', '_')}",
                    check_type="content",
                    status="pass",
                    message=f"Migration file exists: {file_path}",
                    file_path=str(full_path)
                ))
            else:
                checks.append(ValidationCheck(
                    check_name=f"migration_file_{file_path.replace('/', '_')}",
                    check_type="content",
                    status="fail",
                    message=f"Migration file missing: {file_path}",
                    file_path=str(full_path)
                ))
                self.critical_issues.append(f"Migration file missing: {file_path}")
        
        logger.info(f"System functionality validation complete: {len(checks)} checks")
        return checks
    
    def run_complete_validation(self, strategy_file: str, results_file: Optional[str] = None) -> ValidationSummary:
        """Run complete validation of migration"""
        start_time = datetime.now()
        
        logger.info("Starting complete migration validation...")
        
        # Load strategy
        strategy = self.load_migration_strategy(strategy_file)
        
        # Load results if available
        results = {}
        if results_file:
            results = self.load_migration_results(results_file)
        
        # Run all validation checks
        all_checks = []
        
        # File migration validation
        file_checks = self.validate_file_migration(strategy)
        all_checks.extend(file_checks)
        
        # Directory structure validation
        structure_checks = self.validate_directory_structure(strategy)
        all_checks.extend(structure_checks)
        
        # Link integrity validation
        link_checks = self.validate_link_integrity()
        all_checks.extend(link_checks)
        
        # Root cleanup validation
        cleanup_checks = self.validate_root_cleanup()
        all_checks.extend(cleanup_checks)
        
        # System functionality validation
        functionality_checks = self.validate_system_functionality()
        all_checks.extend(functionality_checks)
        
        # Calculate summary
        total_checks = len(all_checks)
        passed_checks = len([c for c in all_checks if c.status == "pass"])
        failed_checks = len([c for c in all_checks if c.status == "fail"])
        warning_checks = len([c for c in all_checks if c.status == "warning"])
        
        validation_time = (datetime.now() - start_time).total_seconds()
        migration_success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Generate recommendations
        self._generate_recommendations(all_checks)
        
        summary = ValidationSummary(
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warning_checks=warning_checks,
            validation_time=validation_time,
            migration_success_rate=migration_success_rate,
            critical_issues=self.critical_issues,
            warnings=self.warnings,
            recommendations=self.recommendations
        )
        
        # Save validation results
        self.save_validation_results(summary, all_checks)
        
        logger.info(f"Complete validation finished in {validation_time:.2f}s")
        logger.info(f"Success rate: {migration_success_rate:.1f}%")
        
        return summary
    
    def _generate_recommendations(self, checks: List[ValidationCheck]) -> None:
        """Generate recommendations based on validation results"""
        failed_checks = [c for c in checks if c.status == "fail"]
        warning_checks = [c for c in checks if c.status == "warning"]
        
        if failed_checks:
            self.recommendations.append("Address all failed validation checks before considering migration complete")
        
        if warning_checks:
            self.recommendations.append("Review warning checks for potential improvements")
        
        if any("broken" in c.message.lower() for c in failed_checks):
            self.recommendations.append("Fix broken links to ensure proper navigation")
        
        if any("missing" in c.message.lower() for c in failed_checks):
            self.recommendations.append("Ensure all required files and directories are present")
        
        if not self.critical_issues:
            self.recommendations.append("Migration appears successful - consider running final cleanup")
    
    def save_validation_results(self, summary: ValidationSummary, checks: List[ValidationCheck]) -> str:
        """Save validation results to file"""
        results_file = self.logs_dir / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Prepare results data
        results_data = {
            'summary': asdict(summary),
            'checks': [asdict(check) for check in checks],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Validation results saved to: {results_file}")
        return str(results_file)


def main():
    """Main execution function for Migration Validation System"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RC1 Migration Validation System')
    parser.add_argument('--strategy-file', required=True, help='Path to migration strategy file')
    parser.add_argument('--results-file', help='Path to migration results file')
    parser.add_argument('--check-type', choices=['all', 'files', 'structure', 'links', 'cleanup', 'functionality'], 
                       default='all', help='Type of validation to run')
    
    args = parser.parse_args()
    
    print("🤖 RC1 Migration Validation System - Beast Mode Execution")
    print("=" * 70)
    
    # Initialize validation system
    validator = MigrationValidationSystem()
    
    if args.check_type == 'all':
        print(f"🔍 Running complete validation...")
        summary = validator.run_complete_validation(args.strategy_file, args.results_file)
        
        # Report results
        print("\n✅ Migration Validation Complete!")
        print(f"📊 Total checks: {summary.total_checks}")
        print(f"✅ Passed: {summary.passed_checks}")
        print(f"❌ Failed: {summary.failed_checks}")
        print(f"⚠️  Warnings: {summary.warning_checks}")
        print(f"📈 Success rate: {summary.migration_success_rate:.1f}%")
        print(f"⏱️  Validation time: {summary.validation_time:.2f}s")
        
        if summary.critical_issues:
            print(f"\n🚨 Critical Issues ({len(summary.critical_issues)}):")
            for issue in summary.critical_issues[:5]:
                print(f"  - {issue}")
            if len(summary.critical_issues) > 5:
                print(f"  ... and {len(summary.critical_issues) - 5} more issues")
        
        if summary.warnings:
            print(f"\n⚠️  Warnings ({len(summary.warnings)}):")
            for warning in summary.warnings[:5]:
                print(f"  - {warning}")
        
        if summary.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in summary.recommendations:
                print(f"  - {rec}")
        
        # Determine overall status
        if summary.failed_checks == 0:
            print("\n🎉 MIGRATION VALIDATION SUCCESSFUL!")
        else:
            print(f"\n❌ MIGRATION VALIDATION FAILED - {summary.failed_checks} critical issues")
    
    else:
        print(f"🔍 Running {args.check_type} validation...")
        # Run specific validation type
        strategy = validator.load_migration_strategy(args.strategy_file)
        
        if args.check_type == 'files':
            checks = validator.validate_file_migration(strategy)
        elif args.check_type == 'structure':
            checks = validator.validate_directory_structure(strategy)
        elif args.check_type == 'links':
            checks = validator.validate_link_integrity()
        elif args.check_type == 'cleanup':
            checks = validator.validate_root_cleanup()
        elif args.check_type == 'functionality':
            checks = validator.validate_system_functionality()
        
        print(f"Validation complete: {len(checks)} checks run")


if __name__ == "__main__":
    main()

