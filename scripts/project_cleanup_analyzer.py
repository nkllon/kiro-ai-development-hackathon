#!/usr/bin/env python3
"""
Project Cleanup Analyzer - Comprehensive project structure analysis and cleanup planning.

This script analyzes the current project structure and creates a detailed cleanup plan
for transforming the Beast Mode AI Development Framework into a clean, professional
open-source project.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re

@dataclass
class FileAnalysis:
    """Analysis results for a single file or directory."""
    path: str
    size_mb: float
    file_type: str
    category: str  # keep, move, archive, delete
    reason: str
    suggested_action: str
    priority: int  # 1=high, 2=medium, 3=low

@dataclass
class CleanupPlan:
    """Comprehensive cleanup plan for the project."""
    total_files: int
    total_size_mb: float
    files_to_keep: List[FileAnalysis]
    files_to_move: List[FileAnalysis]
    files_to_archive: List[FileAnalysis]
    files_to_delete: List[FileAnalysis]
    estimated_size_reduction_mb: float
    cleanup_summary: Dict[str, int]

class ProjectCleanupAnalyzer:
    """Analyzes project structure and creates cleanup plan."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_results: List[FileAnalysis] = []
        
        # Define file patterns for categorization
        self.keep_patterns = {
            # Essential project files
            r"^README\.md$": "Essential documentation",
            r"^pyproject\.toml$": "Project configuration",
            r"^requirements.*\.txt$": "Dependencies",
            r"^\.gitignore$": "Version control",
            r"^LICENSE$": "Legal",
            r"^Makefile$": "Build system",
            
            # Source code
            r"^src/.*\.py$": "Source code",
            r"^src/.*/__init__\.py$": "Python packages",
            
            # Tests
            r"^tests/.*\.py$": "Test code",
            r"^tests/conftest\.py$": "Test configuration",
            
            # Essential documentation
            r"^docs/README\.md$": "Documentation",
            r"^docs/.*\.md$": "Documentation files",
            
            # Working examples
            r"^examples/.*\.py$": "Example code",
            r"^examples/.*\.ipynb$": "Jupyter notebooks",
            r"^examples/.*\.md$": "Example documentation",
            
            # Kiro configuration
            r"^\.kiro/specs/.*": "Kiro specifications",
            r"^\.kiro/steering/.*": "Kiro steering rules",
            
            # ADRs
            r"^ADRS/.*\.md$": "Architecture decisions"
        }
        
        self.delete_patterns = {
            # Temporary and cache files
            r".*\.DS_Store$": "macOS system files",
            r".*\.log$": "Log files",
            r".*\.pid$": "Process ID files",
            r".*\.cache$": "Cache files",
            r".*\.tmp$": "Temporary files",
            r".*\.temp$": "Temporary files",
            r".*\.backup.*$": "Backup files",
            r".*\.bak$": "Backup files",
            
            # Database files (should use Docker volumes)
            r".*\.db$": "Database files",
            r".*\.sqlite.*$": "SQLite databases",
            r".*\.db-shm$": "Database shared memory",
            r".*\.db-wal$": "Database WAL files",
            
            # Build artifacts
            r".*/__pycache__/.*": "Python cache",
            r".*\.pyc$": "Python bytecode",
            r".*\.pyo$": "Python optimized bytecode",
            r".*\.egg-info/.*": "Python egg info",
            
            # Screenshots and images (unless in docs/assets)
            r"^[^/]*\.png$": "Root level screenshots",
            r"^[^/]*\.jpg$": "Root level images",
            r"^[^/]*\.jpeg$": "Root level images",
            r"^.*_\d{10,}\.png$": "Timestamped screenshots",
            
            # Large backup directories
            r".*backup.*/$": "Backup directories",
            r".*_backup_.*/$": "Backup directories",
            r"^\.repair_backups.*/$": "Repair backup directories",
            
            # Node modules (if not needed)
            r"^node_modules/.*": "Node.js dependencies",
            
            # Deployment volatile data
            r"deployment/.*/prometheus-data/.*": "Prometheus data",
            r"deployment/.*/grafana-data/.*": "Grafana data",
            r"deployment/.*/logs/.*": "Deployment logs"
        }
        
        self.archive_patterns = {
            # Development artifacts
            r"^scripts-archive/.*": "Archived scripts",
            r"^migration_backups/.*": "Migration backups",
            r"^assessment-results/.*": "Assessment results",
            r"^audit_reports/.*": "Audit reports",
            r"^reports/.*": "Generated reports",
            r"^logs/.*": "Log directories",
            r"^empirical_data/.*": "Empirical data",
            r"^validation_evidence/.*": "Validation evidence",
            r"^test_evidence/.*": "Test evidence",
            
            # Large deployment packages
            r"^.*_deployment_package/.*": "Deployment packages",
            r"^.*_deployment_\d+/.*": "Timestamped deployments",
            
            # Experimental directories
            r"^demo_project/.*": "Demo projects",
            r"^demo_spores/.*": "Demo spores",
            r"^investigation/.*": "Investigation files",
            r"^learning_patterns/.*": "Learning patterns",
            r"^patterns/.*": "Pattern files"
        }
        
        self.move_patterns = {
            # Misplaced files that should be in proper directories
            r"^[^/]*\.py$": "Root level Python files -> scripts/",
            r"^[^/]*\.sh$": "Root level shell scripts -> scripts/",
            r"^[^/]*\.json$": "Root level JSON files -> config/ or data/",
            r"^[^/]*\.yaml$": "Root level YAML files -> config/",
            r"^[^/]*\.yml$": "Root level YAML files -> config/",
            
            # Documentation that should be in docs/
            r"^[^/]*\.md$": "Root level markdown -> docs/",
            
            # Configuration files
            r"^.*-config\..*$": "Configuration files -> config/",
            r"^.*\.conf$": "Configuration files -> config/"
        }

    def get_file_size_mb(self, path: Path) -> float:
        """Get file size in MB."""
        try:
            if path.is_file():
                return path.stat().st_size / (1024 * 1024)
            elif path.is_dir():
                total_size = 0
                for item in path.rglob("*"):
                    if item.is_file():
                        total_size += item.stat().st_size
                return total_size / (1024 * 1024)
        except (OSError, PermissionError):
            return 0.0
        return 0.0

    def categorize_file(self, path: Path) -> Tuple[str, str, str, int]:
        """Categorize a file based on patterns."""
        relative_path = str(path.relative_to(self.project_root))
        
        # Check delete patterns first (highest priority)
        for pattern, reason in self.delete_patterns.items():
            if re.match(pattern, relative_path):
                return "delete", reason, f"Delete {relative_path}", 1
        
        # Check keep patterns
        for pattern, reason in self.keep_patterns.items():
            if re.match(pattern, relative_path):
                return "keep", reason, f"Keep {relative_path}", 3
        
        # Check archive patterns
        for pattern, reason in self.archive_patterns.items():
            if re.match(pattern, relative_path):
                return "archive", reason, f"Archive {relative_path} to archive/", 2
        
        # Check move patterns
        for pattern, reason in self.move_patterns.items():
            if re.match(pattern, relative_path):
                return "move", reason, f"Move {relative_path} to appropriate directory", 2
        
        # Default: keep with review
        return "keep", "Requires manual review", f"Review {relative_path}", 2

    def analyze_file(self, path: Path) -> FileAnalysis:
        """Analyze a single file or directory."""
        size_mb = self.get_file_size_mb(path)
        relative_path = str(path.relative_to(self.project_root))
        
        # Determine file type
        if path.is_dir():
            file_type = "directory"
        else:
            file_type = path.suffix.lower() or "no_extension"
        
        # Categorize the file
        category, reason, suggested_action, priority = self.categorize_file(path)
        
        return FileAnalysis(
            path=relative_path,
            size_mb=size_mb,
            file_type=file_type,
            category=category,
            reason=reason,
            suggested_action=suggested_action,
            priority=priority
        )

    def scan_project(self) -> None:
        """Scan the entire project and analyze all files."""
        print("🔍 Scanning project structure...")
        
        # Get all files and directories (top level first, then recursive)
        items_to_analyze = []
        
        # Add top-level items
        for item in self.project_root.iterdir():
            if item.name.startswith('.git'):
                continue  # Skip .git directory
            items_to_analyze.append(item)
        
        # Analyze each item
        for item in items_to_analyze:
            try:
                analysis = self.analyze_file(item)
                self.analysis_results.append(analysis)
                
                # If it's a directory we're keeping, analyze its contents
                if item.is_dir() and analysis.category == "keep":
                    for subitem in item.rglob("*"):
                        if subitem != item:  # Don't re-analyze the directory itself
                            sub_analysis = self.analyze_file(subitem)
                            self.analysis_results.append(sub_analysis)
                            
            except (OSError, PermissionError) as e:
                print(f"⚠️  Could not analyze {item}: {e}")

    def generate_cleanup_plan(self) -> CleanupPlan:
        """Generate comprehensive cleanup plan."""
        print("📋 Generating cleanup plan...")
        
        files_to_keep = [f for f in self.analysis_results if f.category == "keep"]
        files_to_move = [f for f in self.analysis_results if f.category == "move"]
        files_to_archive = [f for f in self.analysis_results if f.category == "archive"]
        files_to_delete = [f for f in self.analysis_results if f.category == "delete"]
        
        total_size = sum(f.size_mb for f in self.analysis_results)
        size_reduction = sum(f.size_mb for f in files_to_delete + files_to_archive)
        
        cleanup_summary = {
            "keep": len(files_to_keep),
            "move": len(files_to_move),
            "archive": len(files_to_archive),
            "delete": len(files_to_delete)
        }
        
        return CleanupPlan(
            total_files=len(self.analysis_results),
            total_size_mb=total_size,
            files_to_keep=files_to_keep,
            files_to_move=files_to_move,
            files_to_archive=files_to_archive,
            files_to_delete=files_to_delete,
            estimated_size_reduction_mb=size_reduction,
            cleanup_summary=cleanup_summary
        )

    def save_analysis_report(self, plan: CleanupPlan, output_file: str) -> None:
        """Save detailed analysis report."""
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "cleanup_plan": asdict(plan),
            "recommendations": self.generate_recommendations(plan)
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Analysis report saved to {output_file}")

    def generate_recommendations(self, plan: CleanupPlan) -> Dict[str, List[str]]:
        """Generate specific recommendations based on analysis."""
        recommendations = {
            "immediate_actions": [],
            "size_optimization": [],
            "security_actions": [],
            "organization_improvements": []
        }
        
        # Immediate actions
        if plan.cleanup_summary["delete"] > 0:
            recommendations["immediate_actions"].append(
                f"Delete {plan.cleanup_summary['delete']} unnecessary files to save "
                f"{sum(f.size_mb for f in plan.files_to_delete):.1f} MB"
            )
        
        # Size optimization
        large_files = [f for f in plan.files_to_delete + plan.files_to_archive if f.size_mb > 10]
        if large_files:
            recommendations["size_optimization"].append(
                f"Remove {len(large_files)} large files (>10MB each) for significant size reduction"
            )
        
        # Security actions
        sensitive_patterns = ["password", "key", "secret", "token", "credential"]
        for file_analysis in self.analysis_results:
            if any(pattern in file_analysis.path.lower() for pattern in sensitive_patterns):
                recommendations["security_actions"].append(
                    f"Review {file_analysis.path} for potential sensitive data"
                )
        
        # Organization improvements
        if plan.cleanup_summary["move"] > 0:
            recommendations["organization_improvements"].append(
                f"Reorganize {plan.cleanup_summary['move']} misplaced files into proper directories"
            )
        
        return recommendations

    def print_summary(self, plan: CleanupPlan) -> None:
        """Print cleanup plan summary."""
        print("\n" + "="*60)
        print("🧹 PROJECT CLEANUP ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n📊 Current Project Statistics:")
        print(f"   Total files analyzed: {plan.total_files:,}")
        print(f"   Current total size: {plan.total_size_mb:.1f} MB")
        
        print(f"\n📋 Cleanup Plan Breakdown:")
        print(f"   ✅ Keep: {plan.cleanup_summary['keep']:,} files")
        print(f"   📦 Move: {plan.cleanup_summary['move']:,} files")
        print(f"   🗄️  Archive: {plan.cleanup_summary['archive']:,} files")
        print(f"   🗑️  Delete: {plan.cleanup_summary['delete']:,} files")
        
        print(f"\n💾 Size Optimization:")
        print(f"   Estimated size reduction: {plan.estimated_size_reduction_mb:.1f} MB")
        print(f"   Final estimated size: {plan.total_size_mb - plan.estimated_size_reduction_mb:.1f} MB")
        
        # Show top files to delete by size
        large_deletes = sorted(plan.files_to_delete, key=lambda x: x.size_mb, reverse=True)[:10]
        if large_deletes:
            print(f"\n🔍 Largest files to delete:")
            for file_analysis in large_deletes:
                print(f"   {file_analysis.size_mb:6.1f} MB - {file_analysis.path}")
        
        print("\n" + "="*60)

def main():
    """Main execution function."""
    print("🚀 Starting Project Cleanup Analysis...")
    
    analyzer = ProjectCleanupAnalyzer()
    
    # Scan project
    analyzer.scan_project()
    
    # Generate cleanup plan
    plan = analyzer.generate_cleanup_plan()
    
    # Print summary
    analyzer.print_summary(plan)
    
    # Save detailed report
    output_file = "project_cleanup_analysis.json"
    analyzer.save_analysis_report(plan, output_file)
    
    print(f"\n✅ Analysis complete! Review {output_file} for detailed cleanup plan.")
    print("📝 Next steps:")
    print("   1. Review the analysis report")
    print("   2. Execute cleanup actions by category")
    print("   3. Validate results and update documentation")

if __name__ == "__main__":
    main()