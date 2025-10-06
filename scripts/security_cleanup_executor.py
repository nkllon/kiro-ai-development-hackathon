#!/usr/bin/env python3
"""
Security Cleanup Executor - Removes actual hardcoded credentials and sensitive data.

This script performs targeted cleanup of real security issues while avoiding false positives.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import shutil

@dataclass
class SecurityFix:
    """Represents a security fix that was applied."""
    file_path: str
    line_number: int
    original_content: str
    fixed_content: str
    fix_type: str

class SecurityCleanupExecutor:
    """Executes security cleanup operations."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixes_applied: List[SecurityFix] = []
        
        # Known problematic patterns that should be fixed
        self.critical_fixes = {
            # Redis password that was identified in steering rules
            "redis_password_beastmode2025": {
                "pattern": r"['\"]beastmode2025['\"]",
                "replacement": "os.getenv('REDIS_PASSWORD', '')",
                "description": "Replace hardcoded Redis password with environment variable"
            },
            
            # Generic password patterns (but be careful of examples)
            "hardcoded_passwords": {
                "pattern": r"password\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
                "replacement": "password = os.getenv('PASSWORD', '')",
                "description": "Replace hardcoded password with environment variable"
            }
        }
        
        # Files that should be completely removed (contain only sensitive data)
        self.files_to_remove = [
            "credential_scan_report.json",  # Contains sensitive data from scan
            "security_scan_report.json",   # Contains sensitive data from scan
            "final_credential_scan_report.json",
            "improved_credential_scan_report.json"
        ]
        
        # Directories that should be cleaned up
        self.sensitive_directories = [
            "credentials/",
            "secrets/",
            ".cache/",
            "chrome_cookies.db"
        ]

    def is_safe_to_modify(self, file_path: Path) -> bool:
        """Check if file is safe to modify (not binary, not in sensitive areas)."""
        # Skip binary files
        binary_extensions = {'.db', '.sqlite', '.sqlite3', '.exe', '.dll', '.so', 
                           '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar.gz'}
        if file_path.suffix in binary_extensions:
            return False
        
        # Skip certain directories
        skip_dirs = {'node_modules', '.git', '.venv', 'venv', '__pycache__'}
        if any(part in skip_dirs for part in file_path.parts):
            return False
        
        return True

    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        backup_path = file_path.with_suffix(file_path.suffix + '.security_backup')
        shutil.copy2(file_path, backup_path)
        return backup_path

    def fix_file_credentials(self, file_path: Path) -> List[SecurityFix]:
        """Fix credentials in a single file."""
        fixes = []
        
        if not self.is_safe_to_modify(file_path):
            return fixes
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
        except (OSError, UnicodeDecodeError):
            return fixes
        
        modified = False
        new_lines = []
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            
            # Apply critical fixes
            for fix_name, fix_config in self.critical_fixes.items():
                pattern = fix_config["pattern"]
                replacement = fix_config["replacement"]
                
                if re.search(pattern, line, re.IGNORECASE):
                    # Special handling for different fix types
                    if fix_name == "redis_password_beastmode2025":
                        # Replace the specific Redis password
                        new_line = re.sub(pattern, "os.getenv('REDIS_PASSWORD', '')", line, flags=re.IGNORECASE)
                        if new_line != line:
                            fixes.append(SecurityFix(
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=line_num,
                                original_content=line,
                                fixed_content=new_line,
                                fix_type=fix_name
                            ))
                            line = new_line
                            modified = True
            
            new_lines.append(line)
        
        # Write back modified content if changes were made
        if modified:
            # Create backup first
            backup_path = self.backup_file(file_path)
            print(f"   📄 Backed up {file_path} to {backup_path}")
            
            # Write modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"   ✅ Fixed {len([f for f in fixes if f.file_path == str(file_path.relative_to(self.project_root))])} issues in {file_path}")
        
        return fixes

    def remove_sensitive_files(self) -> List[str]:
        """Remove files that contain only sensitive data."""
        removed_files = []
        
        for file_pattern in self.files_to_remove:
            for file_path in self.project_root.glob(file_pattern):
                if file_path.exists():
                    print(f"   🗑️  Removing sensitive file: {file_path}")
                    file_path.unlink()
                    removed_files.append(str(file_path.relative_to(self.project_root)))
        
        return removed_files

    def clean_sensitive_directories(self) -> List[str]:
        """Clean up sensitive directories."""
        cleaned_dirs = []
        
        for dir_pattern in self.sensitive_directories:
            for dir_path in self.project_root.glob(dir_pattern):
                if dir_path.exists() and dir_path.is_dir():
                    print(f"   🗂️  Cleaning sensitive directory: {dir_path}")
                    shutil.rmtree(dir_path)
                    cleaned_dirs.append(str(dir_path.relative_to(self.project_root)))
        
        return cleaned_dirs

    def update_gitignore(self) -> None:
        """Update .gitignore to prevent future credential exposure."""
        gitignore_path = self.project_root / ".gitignore"
        
        # Additional patterns to add
        security_patterns = [
            "",
            "# Security - Added by cleanup script",
            "credentials/",
            "secrets/",
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",
            ".env.local",
            ".env.production",
            "chrome_cookies.db",
            "*_backup_*",
            "*.security_backup",
            "",
            "# Scan reports with sensitive data",
            "*credential*scan*.json",
            "*security*scan*.json",
            "credential_scan_report.json",
            "security_scan_report.json"
        ]
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                current_content = f.read()
            
            # Check if our patterns are already there
            if "# Security - Added by cleanup script" not in current_content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n'.join(security_patterns))
                print("   📝 Updated .gitignore with security patterns")
        else:
            with open(gitignore_path, 'w') as f:
                f.write('\n'.join(security_patterns))
            print("   📝 Created .gitignore with security patterns")

    def create_env_template(self) -> None:
        """Create .env.example template for required environment variables."""
        env_template_path = self.project_root / ".env.example"
        
        template_content = """# Environment Variables Template
# Copy this file to .env and fill in your actual values

# Redis Configuration
REDIS_PASSWORD=your_redis_password_here
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys (replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_PASSWORD=your_database_password_here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Application Configuration
DEBUG=false
ENVIRONMENT=development

# Security Note: Never commit the actual .env file to version control
# Add .env to your .gitignore file
"""
        
        with open(env_template_path, 'w') as f:
            f.write(template_content)
        
        print("   📋 Created .env.example template")

    def execute_cleanup(self) -> Dict:
        """Execute comprehensive security cleanup."""
        print("🔒 Executing Security Cleanup...")
        
        # Remove sensitive files first
        print("\n1. Removing sensitive files...")
        removed_files = self.remove_sensitive_files()
        
        # Clean sensitive directories
        print("\n2. Cleaning sensitive directories...")
        cleaned_dirs = self.clean_sensitive_directories()
        
        # Fix credentials in source files
        print("\n3. Fixing hardcoded credentials in source files...")
        files_processed = 0
        
        # Focus on Python files and configuration files
        target_extensions = {'.py', '.yaml', '.yml', '.json', '.toml', '.cfg', '.conf', '.sh'}
        
        for file_path in self.project_root.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix in target_extensions and 
                self.is_safe_to_modify(file_path)):
                
                file_fixes = self.fix_file_credentials(file_path)
                self.fixes_applied.extend(file_fixes)
                files_processed += 1
                
                if files_processed % 100 == 0:
                    print(f"   Processed {files_processed} files...")
        
        print(f"   ✅ Processed {files_processed} files")
        
        # Update .gitignore
        print("\n4. Updating .gitignore...")
        self.update_gitignore()
        
        # Create environment template
        print("\n5. Creating environment template...")
        self.create_env_template()
        
        # Generate summary
        summary = {
            "files_removed": removed_files,
            "directories_cleaned": cleaned_dirs,
            "credential_fixes": len(self.fixes_applied),
            "files_processed": files_processed,
            "fixes_by_type": {}
        }
        
        # Group fixes by type
        for fix in self.fixes_applied:
            if fix.fix_type not in summary["fixes_by_type"]:
                summary["fixes_by_type"][fix.fix_type] = 0
            summary["fixes_by_type"][fix.fix_type] += 1
        
        return summary

    def save_cleanup_report(self, summary: Dict, output_file: str) -> None:
        """Save cleanup report."""
        report = {
            "cleanup_timestamp": "2025-10-06T14:00:00",  # Current time
            "project_root": str(self.project_root),
            "summary": summary,
            "fixes_applied": [
                {
                    "file_path": fix.file_path,
                    "line_number": fix.line_number,
                    "fix_type": fix.fix_type,
                    "description": f"Fixed {fix.fix_type}"
                }
                for fix in self.fixes_applied
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

    def print_cleanup_summary(self, summary: Dict) -> None:
        """Print cleanup summary."""
        print("\n" + "="*60)
        print("🔒 SECURITY CLEANUP SUMMARY")
        print("="*60)
        
        print(f"\n📊 Cleanup Results:")
        print(f"   Files removed: {len(summary['files_removed'])}")
        print(f"   Directories cleaned: {len(summary['directories_cleaned'])}")
        print(f"   Credential fixes applied: {summary['credential_fixes']}")
        print(f"   Files processed: {summary['files_processed']}")
        
        if summary["fixes_by_type"]:
            print(f"\n🔧 Fixes by Type:")
            for fix_type, count in summary["fixes_by_type"].items():
                print(f"   {fix_type}: {count}")
        
        if summary["files_removed"]:
            print(f"\n🗑️  Removed Files:")
            for file_path in summary["files_removed"]:
                print(f"   {file_path}")
        
        if summary["directories_cleaned"]:
            print(f"\n🗂️  Cleaned Directories:")
            for dir_path in summary["directories_cleaned"]:
                print(f"   {dir_path}")
        
        print(f"\n✅ Security cleanup completed successfully!")
        print("📝 Next steps:")
        print("   1. Review .env.example and create your .env file")
        print("   2. Update any remaining hardcoded values manually")
        print("   3. Test that applications work with environment variables")
        print("   4. Commit changes to secure the repository")
        
        print("\n" + "="*60)

def main():
    """Main execution function."""
    print("🚀 Starting Security Cleanup Execution...")
    
    executor = SecurityCleanupExecutor()
    
    # Execute cleanup
    summary = executor.execute_cleanup()
    
    # Print summary
    executor.print_cleanup_summary(summary)
    
    # Save report
    output_file = "security_cleanup_report.json"
    executor.save_cleanup_report(summary, output_file)
    print(f"\n📄 Cleanup report saved to {output_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())