#!/usr/bin/env python3
"""
File Organization Executor for Beast Mode AI Development Framework Cleanup
Executes the systematic reorganization of project files based on the cleanup plan.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class FileOrganizationExecutor:
    """Executes systematic file organization based on cleanup plan."""
    
    def __init__(self, cleanup_plan_file: str = "cleanup_plan.json"):
        self.cleanup_plan_file = cleanup_plan_file
        self.cleanup_plan = self.load_cleanup_plan()
        self.execution_log = []
        self.dry_run = True  # Start with dry run for safety
        
    def load_cleanup_plan(self) -> Dict:
        """Load the cleanup plan from JSON file."""
        try:
            with open(self.cleanup_plan_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Cleanup plan file {self.cleanup_plan_file} not found!")
            return {}
    
    def create_target_directories(self):
        """Create target directories if they don't exist."""
        target_dirs = [
            "src", "docs", "examples", "tests", "scripts", 
            "archive", "archive/development", "archive/backups",
            "archive/investigation", "archive/migration"
        ]
        
        for dir_path in target_dirs:
            if not self.dry_run:
                os.makedirs(dir_path, exist_ok=True)
                self.log_action(f"Created directory: {dir_path}")
            else:
                print(f"[DRY RUN] Would create directory: {dir_path}")
    
    def log_action(self, action: str):
        """Log an action taken during file organization."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action
        }
        self.execution_log.append(log_entry)
        print(f"✓ {action}")
    
    def move_file_safely(self, source: str, destination: str) -> bool:
        """Move a file safely with conflict resolution."""
        if not os.path.exists(source):
            print(f"⚠️  Source file not found: {source}")
            return False
        
        # Create destination directory if needed
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            if not self.dry_run:
                os.makedirs(dest_dir, exist_ok=True)
            else:
                print(f"[DRY RUN] Would create directory: {dest_dir}")
        
        # Handle conflicts
        if os.path.exists(destination):
            if os.path.isfile(destination):
                # Create backup of existing file
                backup_dest = f"{destination}.backup"
                if not self.dry_run:
                    shutil.move(destination, backup_dest)
                    self.log_action(f"Backed up existing file: {destination} -> {backup_dest}")
                else:
                    print(f"[DRY RUN] Would backup: {destination} -> {backup_dest}")
        
        # Move the file
        if not self.dry_run:
            shutil.move(source, destination)
            self.log_action(f"Moved: {source} -> {destination}")
        else:
            print(f"[DRY RUN] Would move: {source} -> {destination}")
        
        return True
    
    def delete_file_safely(self, file_path: str) -> bool:
        """Delete a file safely with backup."""
        if not os.path.exists(file_path):
            return True
        
        # Create backup before deletion
        backup_dir = "archive/deleted_files"
        if not self.dry_run:
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            
            # Handle backup conflicts
            counter = 1
            while os.path.exists(backup_path):
                name, ext = os.path.splitext(os.path.basename(file_path))
                backup_path = os.path.join(backup_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.copy2(file_path, backup_path)
            os.remove(file_path)
            self.log_action(f"Deleted: {file_path} (backed up to {backup_path})")
        else:
            print(f"[DRY RUN] Would delete: {file_path} (with backup)")
        
        return True
    
    def organize_source_files(self):
        """Organize source files into src/ directory."""
        print("\n📁 Organizing source files...")
        
        for file_path in self.cleanup_plan.get("move_to_src", []):
            if file_path.startswith("src/"):
                continue  # Already in the right place
            
            # Determine target path in src/
            target_path = f"src/{file_path}"
            self.move_file_safely(file_path, target_path)
    
    def organize_documentation(self):
        """Organize documentation files into docs/ directory."""
        print("\n📚 Organizing documentation...")
        
        for file_path in self.cleanup_plan.get("move_to_docs", []):
            if file_path.startswith("docs/"):
                continue  # Already in the right place
            
            # Determine target path in docs/
            target_path = f"docs/{file_path}"
            self.move_file_safely(file_path, target_path)
    
    def organize_examples(self):
        """Organize example files into examples/ directory."""
        print("\n🎯 Organizing examples...")
        
        for file_path in self.cleanup_plan.get("move_to_examples", []):
            if file_path.startswith("examples/"):
                continue  # Already in the right place
            
            # Determine target path in examples/
            target_path = f"examples/{file_path}"
            self.move_file_safely(file_path, target_path)
    
    def organize_tests(self):
        """Organize test files into tests/ directory."""
        print("\n🧪 Organizing tests...")
        
        for file_path in self.cleanup_plan.get("move_to_tests", []):
            if file_path.startswith("tests/"):
                continue  # Already in the right place
            
            # Determine target path in tests/
            target_path = f"tests/{file_path}"
            self.move_file_safely(file_path, target_path)
    
    def organize_scripts(self):
        """Organize script files into scripts/ directory."""
        print("\n⚙️ Organizing scripts...")
        
        for file_path in self.cleanup_plan.get("move_to_scripts", []):
            if file_path.startswith("scripts/"):
                continue  # Already in the right place
            
            # Determine target path in scripts/
            target_path = f"scripts/{file_path}"
            self.move_file_safely(file_path, target_path)
    
    def archive_development_artifacts(self):
        """Archive development artifacts and experimental code."""
        print("\n📦 Archiving development artifacts...")
        
        for file_path in self.cleanup_plan.get("archive", []):
            # Categorize archives
            if "backup" in file_path.lower():
                target_path = f"archive/backups/{os.path.basename(file_path)}"
            elif "investigation" in file_path.lower() or "debug" in file_path.lower():
                target_path = f"archive/investigation/{os.path.basename(file_path)}"
            elif "migration" in file_path.lower():
                target_path = f"archive/migration/{os.path.basename(file_path)}"
            else:
                target_path = f"archive/development/{os.path.basename(file_path)}"
            
            self.move_file_safely(file_path, target_path)
    
    def clean_temporary_files(self):
        """Delete temporary and build artifacts."""
        print("\n🗑️ Cleaning temporary files...")
        
        for file_path in self.cleanup_plan.get("delete", []):
            self.delete_file_safely(file_path)
    
    def handle_security_files(self):
        """Handle files flagged for security review."""
        print("\n🔒 Handling security-sensitive files...")
        
        security_files = self.cleanup_plan.get("security_review", [])
        if security_files:
            print(f"Found {len(security_files)} files requiring security review:")
            for file_path in security_files[:10]:  # Show first 10
                print(f"  - {file_path}")
            if len(security_files) > 10:
                print(f"  ... and {len(security_files) - 10} more")
            
            print("\n⚠️  These files require manual security review before processing.")
            print("Run the security cleanup script first: python scripts/security_cleanup_executor.py")
    
    def generate_organization_report(self):
        """Generate a report of the file organization process."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "cleanup_plan_file": self.cleanup_plan_file,
            "actions_taken": len(self.execution_log),
            "execution_log": self.execution_log,
            "summary": {
                "files_moved": len([log for log in self.execution_log if "Moved:" in log["action"]]),
                "files_deleted": len([log for log in self.execution_log if "Deleted:" in log["action"]]),
                "directories_created": len([log for log in self.execution_log if "Created directory:" in log["action"]])
            }
        }
        
        report_file = f"file_organization_report_{'dry_run' if self.dry_run else 'actual'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Organization report saved to: {report_file}")
        return report_file
    
    def execute_organization(self, dry_run: bool = True):
        """Execute the complete file organization process."""
        self.dry_run = dry_run
        
        print("🚀 STARTING FILE ORGANIZATION")
        print("="*50)
        print(f"Mode: {'DRY RUN' if dry_run else 'ACTUAL EXECUTION'}")
        print(f"Total items to process: {self.cleanup_plan.get('total_files', 0)}")
        
        # Create target directories
        self.create_target_directories()
        
        # Handle security files first
        self.handle_security_files()
        
        # Organize files by category
        self.organize_source_files()
        self.organize_documentation()
        self.organize_examples()
        self.organize_tests()
        self.organize_scripts()
        
        # Archive and cleanup
        self.archive_development_artifacts()
        self.clean_temporary_files()
        
        # Generate report
        report_file = self.generate_organization_report()
        
        print(f"\n✅ FILE ORGANIZATION {'DRY RUN' if dry_run else 'EXECUTION'} COMPLETED")
        print(f"Actions logged: {len(self.execution_log)}")
        print(f"Report saved to: {report_file}")
        
        if dry_run:
            print("\n💡 This was a dry run. To execute for real, run:")
            print("python scripts/file_organization_executor.py --execute")

def main():
    """Main function to run file organization."""
    import sys
    
    executor = FileOrganizationExecutor()
    
    # Check command line arguments
    execute_for_real = "--execute" in sys.argv
    
    if execute_for_real:
        print("⚠️  WARNING: This will actually move and delete files!")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    executor.execute_organization(dry_run=not execute_for_real)

if __name__ == "__main__":
    main()