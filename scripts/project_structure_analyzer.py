#!/usr/bin/env python3
"""
Project Structure Analyzer for Beast Mode AI Development Framework Cleanup
Analyzes current project structure and generates cleanup recommendations.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FileAnalysis:
    """Analysis results for a single file or directory."""
    path: str
    type: str  # 'file' or 'directory'
    size: int
    category: str
    action: str
    reason: str
    priority: int  # 1=high, 2=medium, 3=low

@dataclass
class CleanupPlan:
    """Complete cleanup plan for the project."""
    keep_in_root: List[str]
    move_to_src: List[str]
    move_to_docs: List[str]
    move_to_examples: List[str]
    move_to_tests: List[str]
    move_to_scripts: List[str]
    archive: List[str]
    delete: List[str]
    security_review: List[str]
    total_files: int
    estimated_size_reduction: int

class ProjectStructureAnalyzer:
    """Analyzes project structure and generates cleanup recommendations."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.analysis_results: List[FileAnalysis] = []
        
        # Essential root files that should stay
        self.essential_root_files = {
            'README.md', 'LICENSE', 'requirements.txt', 'pyproject.toml',
            'Makefile', '.gitignore', '.env.example', 'Dockerfile',
            'docker-compose.yml', 'pytest.ini', 'uv.lock'
        }
        
        # Directories that should stay in root
        self.essential_root_dirs = {
            'src', 'docs', 'examples', 'tests', 'scripts', '.git',
            '.github', '.kiro', 'ADRS'
        }
        
        # Patterns for different file types
        self.source_patterns = {
            r'\.py$', r'\.js$', r'\.ts$', r'\.jsx$', r'\.tsx$',
            r'\.java$', r'\.cpp$', r'\.c$', r'\.h$', r'\.hpp$'
        }
        
        self.doc_patterns = {
            r'\.md$', r'\.rst$', r'\.txt$', r'\.pdf$', r'\.docx?$',
            r'README', r'CHANGELOG', r'CONTRIBUTING', r'LICENSE'
        }
        
        self.config_patterns = {
            r'\.yml$', r'\.yaml$', r'\.json$', r'\.toml$', r'\.ini$',
            r'\.cfg$', r'\.conf$', r'\.env'
        }
        
        # Temporary/build artifacts to delete
        self.delete_patterns = {
            r'\.pyc$', r'__pycache__', r'\.pytest_cache', r'\.coverage',
            r'\.DS_Store$', r'\.log$', r'nohup\.out$', r'\.tmp$',
            r'\.cache', r'node_modules', r'\.venv', r'venv'
        }
        
        # Development artifacts to archive
        self.archive_patterns = {
            r'backup_', r'_backup', r'archive', r'migration_backup',
            r'\.bak$', r'\.old$', r'test_', r'debug_', r'investigation'
        }
        
        # Security-sensitive patterns
        self.security_patterns = {
            r'\.env$', r'secret', r'password', r'key', r'token',
            r'credential', r'auth', r'oauth'
        }

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file and determine its category and action."""
        relative_path = str(file_path.relative_to(self.root_path))
        
        try:
            size = file_path.stat().st_size if file_path.is_file() else 0
        except (OSError, PermissionError):
            size = 0
        
        file_type = 'directory' if file_path.is_dir() else 'file'
        
        # Determine category and action
        category, action, reason, priority = self._categorize_path(relative_path, file_path)
        
        return FileAnalysis(
            path=relative_path,
            type=file_type,
            size=size,
            category=category,
            action=action,
            reason=reason,
            priority=priority
        )

    def _categorize_path(self, relative_path: str, full_path: Path) -> Tuple[str, str, str, int]:
        """Categorize a path and determine the appropriate action."""
        path_name = Path(relative_path).name
        
        # Check if it's an essential root file/directory
        if relative_path in self.essential_root_files or relative_path in self.essential_root_dirs:
            return "essential", "keep_in_root", "Essential project file/directory", 1
        
        # Check for security-sensitive files
        if any(re.search(pattern, relative_path, re.IGNORECASE) for pattern in self.security_patterns):
            return "security", "security_review", "Contains potentially sensitive information", 1
        
        # Check for files to delete
        if any(re.search(pattern, relative_path, re.IGNORECASE) for pattern in self.delete_patterns):
            return "temporary", "delete", "Temporary/build artifact", 1
        
        # Check for files to archive
        if any(re.search(pattern, relative_path, re.IGNORECASE) for pattern in self.archive_patterns):
            return "development", "archive", "Development artifact/backup", 2
        
        # Check if it's already in the right place
        if relative_path.startswith('src/'):
            return "source", "keep_in_place", "Already in src/ directory", 3
        elif relative_path.startswith('docs/'):
            return "documentation", "keep_in_place", "Already in docs/ directory", 3
        elif relative_path.startswith('examples/'):
            return "example", "keep_in_place", "Already in examples/ directory", 3
        elif relative_path.startswith('tests/'):
            return "test", "keep_in_place", "Already in tests/ directory", 3
        elif relative_path.startswith('scripts/'):
            return "script", "keep_in_place", "Already in scripts/ directory", 3
        
        # Categorize based on file patterns
        if any(re.search(pattern, relative_path) for pattern in self.source_patterns):
            return "source", "move_to_src", "Source code file", 2
        elif any(re.search(pattern, relative_path) for pattern in self.doc_patterns):
            return "documentation", "move_to_docs", "Documentation file", 2
        elif 'example' in relative_path.lower() or 'demo' in relative_path.lower():
            return "example", "move_to_examples", "Example/demo file", 2
        elif 'test' in relative_path.lower():
            return "test", "move_to_tests", "Test file", 2
        elif 'script' in relative_path.lower() or relative_path.endswith('.sh'):
            return "script", "move_to_scripts", "Script file", 2
        elif any(re.search(pattern, relative_path) for pattern in self.config_patterns):
            return "configuration", "move_to_src", "Configuration file", 2
        
        # Default categorization for unknown files
        if full_path.is_dir():
            return "unknown", "archive", "Unknown directory - archive for review", 3
        else:
            return "unknown", "archive", "Unknown file - archive for review", 3

    def scan_project(self) -> None:
        """Scan the entire project and analyze all files and directories."""
        print("Scanning project structure...")
        
        # Skip certain directories entirely
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        
        for root, dirs, files in os.walk(self.root_path):
            # Filter out directories we want to skip
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            root_path = Path(root)
            
            # Analyze directories
            for dir_name in dirs:
                dir_path = root_path / dir_name
                analysis = self.analyze_file(dir_path)
                self.analysis_results.append(analysis)
            
            # Analyze files
            for file_name in files:
                file_path = root_path / file_name
                analysis = self.analyze_file(file_path)
                self.analysis_results.append(analysis)

    def generate_cleanup_plan(self) -> CleanupPlan:
        """Generate a comprehensive cleanup plan based on analysis results."""
        plan = CleanupPlan(
            keep_in_root=[],
            move_to_src=[],
            move_to_docs=[],
            move_to_examples=[],
            move_to_tests=[],
            move_to_scripts=[],
            archive=[],
            delete=[],
            security_review=[],
            total_files=len(self.analysis_results),
            estimated_size_reduction=0
        )
        
        for analysis in self.analysis_results:
            if analysis.action == "keep_in_root" or analysis.action == "keep_in_place":
                plan.keep_in_root.append(analysis.path)
            elif analysis.action == "move_to_src":
                plan.move_to_src.append(analysis.path)
            elif analysis.action == "move_to_docs":
                plan.move_to_docs.append(analysis.path)
            elif analysis.action == "move_to_examples":
                plan.move_to_examples.append(analysis.path)
            elif analysis.action == "move_to_tests":
                plan.move_to_tests.append(analysis.path)
            elif analysis.action == "move_to_scripts":
                plan.move_to_scripts.append(analysis.path)
            elif analysis.action == "archive":
                plan.archive.append(analysis.path)
            elif analysis.action == "delete":
                plan.delete.append(analysis.path)
                plan.estimated_size_reduction += analysis.size
            elif analysis.action == "security_review":
                plan.security_review.append(analysis.path)
        
        return plan

    def save_analysis(self, output_file: str = "project_structure_analysis.json") -> None:
        """Save the analysis results to a JSON file."""
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "analysis_results": [asdict(result) for result in self.analysis_results],
            "summary": {
                "total_items": len(self.analysis_results),
                "by_category": {},
                "by_action": {}
            }
        }
        
        # Generate summary statistics
        for result in self.analysis_results:
            category = result.category
            action = result.action
            
            if category not in analysis_data["summary"]["by_category"]:
                analysis_data["summary"]["by_category"][category] = 0
            analysis_data["summary"]["by_category"][category] += 1
            
            if action not in analysis_data["summary"]["by_action"]:
                analysis_data["summary"]["by_action"][action] = 0
            analysis_data["summary"]["by_action"][action] += 1
        
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"Analysis saved to {output_file}")

    def print_summary(self) -> None:
        """Print a summary of the analysis results."""
        print("\n" + "="*60)
        print("PROJECT STRUCTURE ANALYSIS SUMMARY")
        print("="*60)
        
        # Count by action
        action_counts = {}
        for result in self.analysis_results:
            action = result.action
            if action not in action_counts:
                action_counts[action] = 0
            action_counts[action] += 1
        
        print(f"\nTotal items analyzed: {len(self.analysis_results)}")
        print("\nActions recommended:")
        for action, count in sorted(action_counts.items()):
            print(f"  {action}: {count} items")
        
        # High priority items
        high_priority = [r for r in self.analysis_results if r.priority == 1]
        if high_priority:
            print(f"\nHigh priority items ({len(high_priority)}):")
            for item in high_priority[:10]:  # Show first 10
                print(f"  {item.action}: {item.path} - {item.reason}")
            if len(high_priority) > 10:
                print(f"  ... and {len(high_priority) - 10} more")

def main():
    """Main function to run the project structure analysis."""
    analyzer = ProjectStructureAnalyzer()
    
    print("Starting project structure analysis...")
    analyzer.scan_project()
    
    print("Generating cleanup plan...")
    cleanup_plan = analyzer.generate_cleanup_plan()
    
    # Save detailed analysis
    analyzer.save_analysis("project_structure_analysis.json")
    
    # Save cleanup plan
    with open("cleanup_plan.json", 'w') as f:
        json.dump(asdict(cleanup_plan), f, indent=2)
    
    # Print summary
    analyzer.print_summary()
    
    print(f"\nCleanup plan saved to cleanup_plan.json")
    print(f"Estimated size reduction: {cleanup_plan.estimated_size_reduction / (1024*1024):.1f} MB")
    
    return cleanup_plan

if __name__ == "__main__":
    main()