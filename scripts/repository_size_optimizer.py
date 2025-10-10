#!/usr/bin/env python3
"""
Repository Size Optimization Script

This script optimizes repository size by:
1. Removing large binary files and unnecessary assets
2. Archiving or removing redundant backup directories
3. Identifying candidates for git LFS
4. Cleaning up development artifacts

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Information about a file for size optimization."""
    path: str
    size: int
    category: str
    action: str
    reason: str

class RepositorySizeOptimizer:
    """Optimizes repository size by removing unnecessary files and assets."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.root_path = Path(".")
        self.optimization_report = []
        self.total_size_before = 0
        self.total_size_after = 0
        
        # Size thresholds
        self.large_file_threshold = 10 * 1024 * 1024  # 10MB
        self.git_lfs_threshold = 50 * 1024 * 1024     # 50MB
        
        # Directories to clean up completely
        self.cleanup_directories = [
            ".venv",  # Virtual environment - should be recreated
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            "node_modules",
        ]
        
        # File patterns to remove
        self.cleanup_patterns = [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "*.so",
            "*.dylib",
            "*.dll",
            "*.log",
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.backup",
            "*.orig",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini",
        ]
        
        # Large file extensions that should be in git LFS
        self.lfs_extensions = {
            ".tar.gz", ".zip", ".rar", ".7z",
            ".mp4", ".avi", ".mov", ".mkv",
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
            ".pdf", ".doc", ".docx", ".ppt", ".pptx",
            ".bin", ".exe", ".dmg", ".pkg", ".deb", ".rpm",
            ".db", ".sqlite", ".sqlite3",
        }
        
        # Directories to archive instead of delete
        self.archive_directories = [
            "archive/backups",
            "archive/development",
            "archive/migration",
        ]

    def get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, FileNotFoundError):
            pass
        return total

    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"

    def analyze_large_files(self) -> List[FileInfo]:
        """Analyze large files in the repository."""
        large_files = []
        
        logger.info("Analyzing large files...")
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip .git directory for file analysis (but we'll handle it separately)
            if '.git' in Path(root).parts:
                continue
                
            for file in files:
                filepath = Path(root) / file
                try:
                    size = filepath.stat().st_size
                    if size > self.large_file_threshold:
                        category = self._categorize_file(filepath, size)
                        action, reason = self._determine_action(filepath, size, category)
                        
                        large_files.append(FileInfo(
                            path=str(filepath),
                            size=size,
                            category=category,
                            action=action,
                            reason=reason
                        ))
                except (OSError, FileNotFoundError):
                    continue
        
        return sorted(large_files, key=lambda x: x.size, reverse=True)

    def _categorize_file(self, filepath: Path, size: int) -> str:
        """Categorize a file based on its path and extension."""
        path_str = str(filepath).lower()
        extension = filepath.suffix.lower()
        
        if '.venv' in path_str or 'venv' in path_str:
            return "virtual_environment"
        elif 'backup' in path_str or 'archive' in path_str:
            return "backup_archive"
        elif extension in ['.json', '.log', '.txt'] and size > 50 * 1024 * 1024:
            return "large_data_file"
        elif extension in self.lfs_extensions:
            return "binary_asset"
        elif extension in ['.dylib', '.so', '.dll']:
            return "compiled_library"
        elif 'node_modules' in path_str:
            return "node_dependency"
        elif '__pycache__' in path_str or extension in ['.pyc', '.pyo']:
            return "python_cache"
        else:
            return "other"

    def _determine_action(self, filepath: Path, size: int, category: str) -> Tuple[str, str]:
        """Determine what action to take for a file."""
        path_str = str(filepath)
        
        if category == "virtual_environment":
            return "delete", "Virtual environment should be recreated from requirements"
        elif category == "python_cache":
            return "delete", "Python cache files can be regenerated"
        elif category == "node_dependency":
            return "delete", "Node dependencies should be installed via package manager"
        elif category == "backup_archive" and size > 100 * 1024 * 1024:
            return "archive_external", "Large backup files should be stored externally"
        elif category == "large_data_file" and 'security_scan_report' in path_str:
            return "delete", "Security scan reports are temporary and can be regenerated"
        elif category == "large_data_file" and size > 100 * 1024 * 1024:
            return "review", "Large data files need manual review"
        elif category == "binary_asset" and size > self.git_lfs_threshold:
            return "git_lfs", "Large binary files should use Git LFS"
        elif category == "compiled_library":
            return "delete", "Compiled libraries should be installed via package manager"
        else:
            return "review", "File needs manual review for optimization"

    def cleanup_directories_method(self) -> List[FileInfo]:
        """Clean up entire directories that should be removed."""
        cleanup_results = []
        
        for dir_pattern in self.cleanup_directories:
            for path in self.root_path.rglob(dir_pattern):
                if path.is_dir():
                    size = self.get_directory_size(path)
                    cleanup_results.append(FileInfo(
                        path=str(path),
                        size=size,
                        category="cleanup_directory",
                        action="delete",
                        reason=f"Directory {dir_pattern} should be recreated"
                    ))
                    
                    if not self.dry_run:
                        logger.info(f"Removing directory: {path}")
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        logger.info(f"[DRY RUN] Would remove directory: {path} ({self.format_size(size)})")
        
        return cleanup_results

    def cleanup_file_patterns(self) -> List[FileInfo]:
        """Clean up files matching cleanup patterns."""
        cleanup_results = []
        
        for pattern in self.cleanup_patterns:
            for path in self.root_path.rglob(pattern):
                if path.is_file():
                    try:
                        size = path.stat().st_size
                        cleanup_results.append(FileInfo(
                            path=str(path),
                            size=size,
                            category="cleanup_pattern",
                            action="delete",
                            reason=f"Matches cleanup pattern {pattern}"
                        ))
                        
                        if not self.dry_run:
                            path.unlink()
                            logger.info(f"Removed file: {path}")
                        else:
                            logger.info(f"[DRY RUN] Would remove file: {path} ({self.format_size(size)})")
                    except (OSError, FileNotFoundError):
                        continue
        
        return cleanup_results

    def optimize_git_repository(self) -> Dict[str, int]:
        """Optimize git repository size."""
        logger.info("Optimizing git repository...")
        
        git_stats = {}
        
        try:
            # Get initial git size
            result = subprocess.run(['du', '-sh', '.git'], capture_output=True, text=True)
            if result.returncode == 0:
                git_size_before = result.stdout.split()[0]
                git_stats['size_before'] = git_size_before
                logger.info(f"Git repository size before optimization: {git_size_before}")
            
            if not self.dry_run:
                # Run git garbage collection
                logger.info("Running git gc --aggressive --prune=now...")
                subprocess.run(['git', 'gc', '--aggressive', '--prune=now'], check=True)
                
                # Get size after optimization
                result = subprocess.run(['du', '-sh', '.git'], capture_output=True, text=True)
                if result.returncode == 0:
                    git_size_after = result.stdout.split()[0]
                    git_stats['size_after'] = git_size_after
                    logger.info(f"Git repository size after optimization: {git_size_after}")
            else:
                logger.info("[DRY RUN] Would run git gc --aggressive --prune=now")
                git_stats['size_after'] = git_stats.get('size_before', 'unknown')
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Git optimization failed: {e}")
            git_stats['error'] = str(e)
        
        return git_stats

    def create_gitlfs_recommendations(self, large_files: List[FileInfo]) -> List[str]:
        """Create recommendations for Git LFS usage."""
        lfs_recommendations = []
        
        for file_info in large_files:
            if file_info.action == "git_lfs":
                filepath = Path(file_info.path)
                extension = filepath.suffix.lower()
                
                # Create .gitattributes entry
                lfs_pattern = f"*{extension} filter=lfs diff=lfs merge=lfs -text"
                if lfs_pattern not in lfs_recommendations:
                    lfs_recommendations.append(lfs_pattern)
        
        return lfs_recommendations

    def generate_optimization_report(self, large_files: List[FileInfo], 
                                   cleanup_results: List[FileInfo],
                                   git_stats: Dict[str, int]) -> Dict:
        """Generate comprehensive optimization report."""
        
        # Calculate total savings
        total_savings = sum(f.size for f in large_files + cleanup_results 
                          if f.action in ["delete", "archive_external"])
        
        # Group files by action
        actions_summary = {}
        for file_info in large_files + cleanup_results:
            action = file_info.action
            if action not in actions_summary:
                actions_summary[action] = {"count": 0, "size": 0, "files": []}
            actions_summary[action]["count"] += 1
            actions_summary[action]["size"] += file_info.size
            actions_summary[action]["files"].append({
                "path": file_info.path,
                "size": self.format_size(file_info.size),
                "reason": file_info.reason
            })
        
        # Create Git LFS recommendations
        lfs_recommendations = self.create_gitlfs_recommendations(large_files)
        
        report = {
            "timestamp": subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            "dry_run": self.dry_run,
            "repository_analysis": {
                "total_files_analyzed": len(large_files) + len(cleanup_results),
                "large_files_found": len(large_files),
                "cleanup_files_found": len(cleanup_results),
                "estimated_size_reduction": self.format_size(total_savings),
                "estimated_size_reduction_bytes": total_savings
            },
            "actions_summary": {
                action: {
                    "count": data["count"],
                    "total_size": self.format_size(data["size"]),
                    "total_size_bytes": data["size"]
                }
                for action, data in actions_summary.items()
            },
            "detailed_files": actions_summary,
            "git_optimization": git_stats,
            "git_lfs_recommendations": lfs_recommendations,
            "next_steps": [
                "Review files marked for manual review",
                "Set up Git LFS for large binary files",
                "Update .gitignore to prevent future accumulation",
                "Consider external storage for large backup files",
                "Recreate virtual environment from requirements.txt"
            ]
        }
        
        return report

    def run_optimization(self) -> Dict:
        """Run the complete repository size optimization."""
        logger.info(f"Starting repository size optimization (dry_run={self.dry_run})")
        
        # Get initial size
        self.total_size_before = self.get_directory_size(self.root_path)
        logger.info(f"Repository size before optimization: {self.format_size(self.total_size_before)}")
        
        # Analyze large files
        large_files = self.analyze_large_files()
        logger.info(f"Found {len(large_files)} large files")
        
        # Clean up directories and file patterns
        cleanup_results = []
        cleanup_results.extend(self.cleanup_directories_method())
        cleanup_results.extend(self.cleanup_file_patterns())
        
        # Optimize git repository
        git_stats = self.optimize_git_repository()
        
        # Generate report
        report = self.generate_optimization_report(large_files, cleanup_results, git_stats)
        
        # Get final size
        self.total_size_after = self.get_directory_size(self.root_path)
        report["repository_analysis"]["size_before"] = self.format_size(self.total_size_before)
        report["repository_analysis"]["size_after"] = self.format_size(self.total_size_after)
        report["repository_analysis"]["actual_reduction"] = self.format_size(
            self.total_size_before - self.total_size_after
        )
        
        logger.info(f"Repository size after optimization: {self.format_size(self.total_size_after)}")
        logger.info(f"Size reduction: {self.format_size(self.total_size_before - self.total_size_after)}")
        
        return report

def main():
    """Main function to run repository size optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimize repository size")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Run in dry-run mode (default)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform the optimization")
    parser.add_argument("--output", default="data/repository_size_optimization_report.json",
                       help="Output file for the report")
    
    args = parser.parse_args()
    
    # If --execute is specified, turn off dry-run
    dry_run = not args.execute
    
    optimizer = RepositorySizeOptimizer(dry_run=dry_run)
    report = optimizer.run_optimization()
    
    # Save report
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Optimization report saved to: {args.output}")
    
    # Print summary
    print("\n" + "="*80)
    print("REPOSITORY SIZE OPTIMIZATION SUMMARY")
    print("="*80)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTION'}")
    print(f"Files analyzed: {report['repository_analysis']['total_files_analyzed']}")
    print(f"Size before: {report['repository_analysis']['size_before']}")
    print(f"Size after: {report['repository_analysis']['size_after']}")
    print(f"Estimated reduction: {report['repository_analysis']['estimated_size_reduction']}")
    
    if dry_run:
        print(f"\nActual reduction: {report['repository_analysis']['actual_reduction']}")
    
    print(f"\nReport saved to: {args.output}")
    print("\nNext steps:")
    for step in report['next_steps']:
        print(f"  - {step}")

if __name__ == "__main__":
    main()