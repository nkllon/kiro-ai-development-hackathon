#!/usr/bin/env python3
"""
Root Directory Cleanup Planner
==============================

Creates a safe cleanup plan for the root directory while preserving:
1. Documentation index system
2. RDI registry and critical systems
3. Essential project files

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Clean root directory without breaking critical systems
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class FileInfo:
    """Information about a file for cleanup planning."""
    path: Path
    size: int
    category: str
    action: str
    reason: str
    dependencies: List[str] = None

class FileCategory(Enum):
    """Categories for file classification."""
    CRITICAL = "critical"           # Must keep - core system files
    ESSENTIAL = "essential"         # Should keep - important project files
    DOCUMENTATION = "documentation" # Keep - documentation system
    TEMPORARY = "temporary"         # Safe to delete - temp files
    BACKUP = "backup"              # Archive - backup files
    GENERATED = "generated"         # Regenerate - generated files
    UNKNOWN = "unknown"            # Review - needs manual inspection

class RootCleanupPlanner:
    """Plans safe cleanup of root directory."""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root)
        self.critical_files = set()
        self.essential_files = set()
        self.documentation_files = set()
        self.cleanup_plan = {}
        
    def analyze_root_directory(self) -> Dict[str, List[FileInfo]]:
        """Analyze root directory and create cleanup plan."""
        print("🔍 Analyzing root directory...")
        
        # Define critical files that must be preserved
        self._define_critical_files()
        
        # Define essential files that should be preserved
        self._define_essential_files()
        
        # Define documentation files that are part of the index
        self._define_documentation_files()
        
        # Analyze all files in root
        files = self._scan_root_files()
        
        # Categorize files
        categorized = self._categorize_files(files)
        
        # Create cleanup plan
        self._create_cleanup_plan(categorized)
        
        return categorized
    
    def _define_critical_files(self):
        """Define critical files that must be preserved."""
        self.critical_files = {
            # Core project files
            "README.md",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "requirements-dev.txt",
            ".gitignore",
            ".gitmodules",
            ".gitguardian.yaml",
            ".pre-commit-config.yaml",
            ".mcp.json",
            
            # RDI and Registry critical files
            "RDI_ANALYSIS_REPORT.md",
            "RDI_ANALYSIS_SUMMARY.md",
            "RM_RDI_IMPLEMENTATION_PROMPT.md",
            "beast_mode_rdi_attack_system.py",
            "generate_rdi_traceable_tests.py",
            
            # Core system files
            "beast",
            "devpost-cli",
            
            # Configuration files
            ".DS_Store",  # macOS system file
        }
    
    def _define_essential_files(self):
        """Define essential files that should be preserved."""
        self.essential_files = {
            # Documentation system
            "docs/",
            "diagrams/",
            
            # Source code
            "src/",
            
            # Configuration and specs
            ".kiro/",
            ".github/",
            ".cursor/",
            
            # Important project files
            "ARCHITECTURE_REFACTOR.md",
            "ADJACENCY_CLUSTER_ANALYSIS_COMPLETE.md",
            "adjacency_cluster_analysis.json",
            "adaptive_knowledge_base.json",
        }
    
    def _define_documentation_files(self):
        """Define documentation files that are part of the index system."""
        # All files in docs/ directory are part of documentation index
        docs_dir = self.repository_root / "docs"
        if docs_dir.exists():
            for file_path in docs_dir.rglob("*"):
                if file_path.is_file():
                    self.documentation_files.add(str(file_path.relative_to(self.repository_root)))
        
        # All files in diagrams/ directory are part of documentation index
        diagrams_dir = self.repository_root / "diagrams"
        if diagrams_dir.exists():
            for file_path in diagrams_dir.rglob("*"):
                if file_path.is_file():
                    self.documentation_files.add(str(file_path.relative_to(self.repository_root)))
    
    def _scan_root_files(self) -> List[Path]:
        """Scan all files in root directory."""
        files = []
        for item in self.repository_root.iterdir():
            if item.is_file():
                files.append(item)
        return files
    
    def _categorize_files(self, files: List[Path]) -> Dict[str, List[FileInfo]]:
        """Categorize files for cleanup."""
        categorized = {
            "critical": [],
            "essential": [],
            "documentation": [],
            "temporary": [],
            "backup": [],
            "generated": [],
            "unknown": []
        }
        
        for file_path in files:
            file_info = self._classify_file(file_path)
            categorized[file_info.category].append(file_info)
        
        return categorized
    
    def _classify_file(self, file_path: Path) -> FileInfo:
        """Classify a single file."""
        file_name = file_path.name
        file_size = file_path.stat().st_size if file_path.exists() else 0
        
        # Check if critical
        if file_name in self.critical_files:
            return FileInfo(
                path=file_path,
                size=file_size,
                category=FileCategory.CRITICAL.value,
                action="KEEP",
                reason="Critical system file"
            )
        
        # Check if part of documentation system
        rel_path = str(file_path.relative_to(self.repository_root))
        if rel_path in self.documentation_files:
            return FileInfo(
                path=file_path,
                size=file_size,
                category=FileCategory.DOCUMENTATION.value,
                action="KEEP",
                reason="Part of documentation index system"
            )
        
        # Check if temporary file
        if self._is_temporary_file(file_name):
            return FileInfo(
                path=file_path,
                size=file_size,
                category=FileCategory.TEMPORARY.value,
                action="DELETE",
                reason="Temporary file"
            )
        
        # Check if backup file
        if self._is_backup_file(file_name):
            return FileInfo(
                path=file_path,
                size=file_size,
                category=FileCategory.BACKUP.value,
                action="ARCHIVE",
                reason="Backup file"
            )
        
        # Check if generated file
        if self._is_generated_file(file_name):
            return FileInfo(
                path=file_path,
                size=file_size,
                category=FileCategory.GENERATED.value,
                action="REGENERATE",
                reason="Generated file"
            )
        
        # Check if essential
        if self._is_essential_file(file_name):
            return FileInfo(
                path=file_path,
                size=file_size,
                category=FileCategory.ESSENTIAL.value,
                action="KEEP",
                reason="Essential project file"
            )
        
        # Unknown - needs review
        return FileInfo(
            path=file_path,
            size=file_size,
            category=FileCategory.UNKNOWN.value,
            action="REVIEW",
            reason="Needs manual inspection"
        )
    
    def _is_temporary_file(self, file_name: str) -> bool:
        """Check if file is temporary."""
        temp_patterns = [
            ".tmp", ".temp", ".cache", ".coverage", ".DS_Store",
            "chrome_cookies.db", "actual_current_page.png",
            "additional_info_filled.png", "additional_info_page.png",
            "aardvark_project.html", "-", ".cache_ggshield"
        ]
        
        return any(pattern in file_name for pattern in temp_patterns)
    
    def _is_backup_file(self, file_name: str) -> bool:
        """Check if file is a backup."""
        backup_patterns = [
            ".bak", ".backup", "_backup", "_old", "_orig",
            ".coverage 2"  # Duplicate coverage file
        ]
        
        return any(pattern in file_name for pattern in backup_patterns)
    
    def _is_generated_file(self, file_name: str) -> bool:
        """Check if file is generated."""
        generated_patterns = [
            ".pyc", "__pycache__", ".log", ".out", ".err"
        ]
        
        return any(pattern in file_name for pattern in generated_patterns)
    
    def _is_essential_file(self, file_name: str) -> bool:
        """Check if file is essential."""
        essential_patterns = [
            ".py", ".md", ".json", ".yaml", ".yml", ".toml",
            ".txt", ".cfg", ".conf", ".ini", ".env"
        ]
        
        return any(file_name.endswith(pattern) for pattern in essential_patterns)
    
    def _create_cleanup_plan(self, categorized: Dict[str, List[FileInfo]]):
        """Create detailed cleanup plan."""
        self.cleanup_plan = {
            "summary": {
                "total_files": sum(len(files) for files in categorized.values()),
                "critical_files": len(categorized["critical"]),
                "essential_files": len(categorized["essential"]),
                "documentation_files": len(categorized["documentation"]),
                "temporary_files": len(categorized["temporary"]),
                "backup_files": len(categorized["backup"]),
                "generated_files": len(categorized["generated"]),
                "unknown_files": len(categorized["unknown"])
            },
            "actions": {
                "keep": categorized["critical"] + categorized["essential"] + categorized["documentation"],
                "delete": categorized["temporary"],
                "archive": categorized["backup"],
                "regenerate": categorized["generated"],
                "review": categorized["unknown"]
            }
        }
    
    def generate_cleanup_report(self) -> str:
        """Generate detailed cleanup report."""
        report = "# Root Directory Cleanup Plan\n\n"
        report += f"**Generated:** {Path.cwd()}\n"
        report += f"**Total Files Analyzed:** {self.cleanup_plan['summary']['total_files']}\n\n"
        
        # Summary
        report += "## 📊 Cleanup Summary\n\n"
        report += "| Category | Count | Action |\n"
        report += "|----------|-------|--------|\n"
        report += f"| Critical | {self.cleanup_plan['summary']['critical_files']} | KEEP |\n"
        report += f"| Essential | {self.cleanup_plan['summary']['essential_files']} | KEEP |\n"
        report += f"| Documentation | {self.cleanup_plan['summary']['documentation_files']} | KEEP |\n"
        report += f"| Temporary | {self.cleanup_plan['summary']['temporary_files']} | DELETE |\n"
        report += f"| Backup | {self.cleanup_plan['summary']['backup_files']} | ARCHIVE |\n"
        report += f"| Generated | {self.cleanup_plan['summary']['generated_files']} | REGENERATE |\n"
        report += f"| Unknown | {self.cleanup_plan['summary']['unknown_files']} | REVIEW |\n"
        
        # Detailed actions
        report += "\n## 🗑️ Files to Delete (Temporary)\n\n"
        for file_info in self.cleanup_plan["actions"]["delete"]:
            report += f"- `{file_info.path.name}` ({file_info.size} bytes) - {file_info.reason}\n"
        
        report += "\n## 📦 Files to Archive (Backup)\n\n"
        for file_info in self.cleanup_plan["actions"]["archive"]:
            report += f"- `{file_info.path.name}` ({file_info.size} bytes) - {file_info.reason}\n"
        
        report += "\n## 🔄 Files to Regenerate (Generated)\n\n"
        for file_info in self.cleanup_plan["actions"]["regenerate"]:
            report += f"- `{file_info.path.name}` ({file_info.size} bytes) - {file_info.reason}\n"
        
        report += "\n## ❓ Files to Review (Unknown)\n\n"
        for file_info in self.cleanup_plan["actions"]["review"]:
            report += f"- `{file_info.path.name}` ({file_info.size} bytes) - {file_info.reason}\n"
        
        # Safety measures
        report += "\n## 🛡️ Safety Measures\n\n"
        report += "### Before Cleanup:\n"
        report += "1. **Backup critical files** to a separate location\n"
        report += "2. **Test documentation index** to ensure it still works\n"
        report += "3. **Verify RDI registry** is not affected\n"
        report += "4. **Run tests** to ensure system integrity\n\n"
        
        report += "### During Cleanup:\n"
        report += "1. **Delete temporary files** first (safest)\n"
        report += "2. **Archive backup files** to `archived/` directory\n"
        report += "3. **Regenerate generated files** as needed\n"
        report += "4. **Review unknown files** manually\n\n"
        
        report += "### After Cleanup:\n"
        report += "1. **Verify documentation index** still works\n"
        report += "2. **Test RDI registry** functionality\n"
        report += "3. **Run full test suite**\n"
        report += "4. **Update .gitignore** to prevent future clutter\n\n"
        
        return report
    
    def create_cleanup_script(self) -> str:
        """Create executable cleanup script."""
        script = "#!/bin/bash\n"
        script += "# Root Directory Cleanup Script\n"
        script += "# Generated by RootCleanupPlanner\n\n"
        
        script += "set -e  # Exit on any error\n\n"
        
        script += "echo '🧹 Starting root directory cleanup...'\n\n"
        
        # Create backup directory
        script += "# Create backup directory\n"
        script += "mkdir -p archived/$(date +%Y%m%d_%H%M%S)\n"
        script += "BACKUP_DIR=\"archived/$(date +%Y%m%d_%H%M%S)\"\n\n"
        
        # Delete temporary files
        script += "# Delete temporary files\n"
        script += "echo '🗑️  Deleting temporary files...'\n"
        for file_info in self.cleanup_plan["actions"]["delete"]:
            script += f"rm -f \"{file_info.path.name}\" 2>/dev/null || echo \"  ⚠️  Could not delete {file_info.path.name}\"\n"
        script += "\n"
        
        # Archive backup files
        script += "# Archive backup files\n"
        script += "echo '📦 Archiving backup files...'\n"
        for file_info in self.cleanup_plan["actions"]["archive"]:
            script += f"mv \"{file_info.path.name}\" \"$BACKUP_DIR/\" 2>/dev/null || echo \"  ⚠️  Could not archive {file_info.path.name}\"\n"
        script += "\n"
        
        # Regenerate generated files
        script += "# Regenerate generated files\n"
        script += "echo '🔄 Regenerating generated files...'\n"
        script += "# Add regeneration commands here\n"
        script += "\n"
        
        script += "echo '✅ Cleanup completed!'\n"
        script += "echo \"📦 Backup files saved to: $BACKUP_DIR\"\n"
        
        return script

def main():
    """Generate root directory cleanup plan."""
    planner = RootCleanupPlanner()
    
    print("🔍 Analyzing root directory for cleanup...")
    categorized = planner.analyze_root_directory()
    
    print(f"📊 Found {planner.cleanup_plan['summary']['total_files']} files:")
    print(f"  - Critical: {planner.cleanup_plan['summary']['critical_files']}")
    print(f"  - Essential: {planner.cleanup_plan['summary']['essential_files']}")
    print(f"  - Documentation: {planner.cleanup_plan['summary']['documentation_files']}")
    print(f"  - Temporary: {planner.cleanup_plan['summary']['temporary_files']}")
    print(f"  - Backup: {planner.cleanup_plan['summary']['backup_files']}")
    print(f"  - Generated: {planner.cleanup_plan['summary']['generated_files']}")
    print(f"  - Unknown: {planner.cleanup_plan['summary']['unknown_files']}")
    
    # Generate report
    report = planner.generate_cleanup_report()
    
    # Save report
    report_path = Path("ROOT_CLEANUP_PLAN.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Cleanup plan generated: {report_path}")
    
    # Generate cleanup script
    script = planner.create_cleanup_script()
    script_path = Path("cleanup_root.sh")
    with open(script_path, 'w') as f:
        f.write(script)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Cleanup script generated: {script_path}")
    print(f"\n🚀 Next steps:")
    print(f"1. Review {report_path}")
    print(f"2. Run ./cleanup_root.sh (after backup)")
    print(f"3. Test documentation index and RDI registry")

if __name__ == "__main__":
    main()


