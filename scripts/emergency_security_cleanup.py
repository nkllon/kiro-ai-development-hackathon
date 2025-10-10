#!/usr/bin/env python3
"""
Emergency Security Cleanup Script
Immediately removes exposed credentials and sensitive files from the repository.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List

class EmergencySecurityCleanup:
    """Handles immediate removal of exposed credentials and sensitive files."""
    
    def __init__(self):
        self.removed_files = []
        self.security_issues = []
        
    def scan_for_exposed_credentials(self) -> List[str]:
        """Scan for files with exposed credentials in filenames or content."""
        exposed_files = []
        
        # Check for the specific OAuth token file we found
        oauth_file = "claude-test-with-token.logCLAUDE_CODE_OAUTH_TOKEN=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"
        if os.path.exists(oauth_file):
            exposed_files.append(oauth_file)
        
        # Check for other credential files
        credential_patterns = [
            "*.key", "*.pem", "*token*", "*secret*", "*password*",
            "*credential*", "*auth*", "*.env"
        ]
        
        for root, dirs, files in os.walk("."):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip .git directory
                if ".git" in file_path:
                    continue
                    
                # Check filename patterns
                for pattern in credential_patterns:
                    if any(keyword in file.lower() for keyword in ["token", "secret", "password", "credential", "auth", "key"]):
                        if file_path not in exposed_files:
                            exposed_files.append(file_path)
        
        return exposed_files
    
    def remove_exposed_file(self, file_path: str) -> bool:
        """Safely remove an exposed credential file."""
        try:
            if os.path.exists(file_path):
                # Create backup in secure location first
                backup_dir = ".security_cleanup_backup"
                os.makedirs(backup_dir, exist_ok=True)
                
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                shutil.copy2(file_path, backup_path)
                
                # Remove the original file
                os.remove(file_path)
                self.removed_files.append(file_path)
                print(f"REMOVED: {file_path} (backed up to {backup_path})")
                return True
            else:
                print(f"File not found: {file_path}")
                return False
        except Exception as e:
            print(f"Error removing {file_path}: {e}")
            return False
    
    def clean_env_files(self):
        """Clean up .env files by removing sensitive content."""
        env_files = [".env", "sample.env"]
        
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        content = f.read()
                    
                    # Check if it contains actual credentials
                    sensitive_patterns = ["sk-", "oauth", "token", "password", "secret"]
                    has_credentials = any(pattern in content.lower() for pattern in sensitive_patterns)
                    
                    if has_credentials:
                        # Move to backup and create template
                        backup_path = f".security_cleanup_backup/{env_file}.backup"
                        shutil.copy2(env_file, backup_path)
                        
                        # Create template version
                        template_content = self.create_env_template(content)
                        with open(f"{env_file}.template", 'w') as f:
                            f.write(template_content)
                        
                        # Remove original
                        os.remove(env_file)
                        print(f"CLEANED: {env_file} -> {env_file}.template (original backed up)")
                        self.removed_files.append(env_file)
                
                except Exception as e:
                    print(f"Error cleaning {env_file}: {e}")
    
    def create_env_template(self, content: str) -> str:
        """Create a template version of an env file with placeholders."""
        lines = content.split('\n')
        template_lines = []
        
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                # Replace actual values with placeholders
                template_lines.append(f"{key}=YOUR_{key.upper()}_HERE")
            else:
                template_lines.append(line)
        
        return '\n'.join(template_lines)
    
    def run_emergency_cleanup(self):
        """Run the complete emergency security cleanup."""
        print("🚨 EMERGENCY SECURITY CLEANUP STARTING")
        print("="*50)
        
        # Create backup directory
        os.makedirs(".security_cleanup_backup", exist_ok=True)
        
        # 1. Remove the exposed OAuth token file immediately
        oauth_file = "claude-test-with-token.logCLAUDE_CODE_OAUTH_TOKEN=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"
        if os.path.exists(oauth_file):
            self.remove_exposed_file(oauth_file)
        
        # 2. Clean up .env files
        self.clean_env_files()
        
        # 3. Remove other credential files from the security review list
        security_files = [
            "docker/google-calendar-mcp/gcp-oauth.keys.json",
            "vonnegut_deployment_package/tunnel-credentials.json"
        ]
        
        for file_path in security_files:
            if os.path.exists(file_path):
                self.remove_exposed_file(file_path)
        
        # 4. Generate security report
        self.generate_security_report()
        
        print("\n✅ EMERGENCY SECURITY CLEANUP COMPLETED")
        print(f"Removed {len(self.removed_files)} files with potential security issues")
        print("All removed files have been backed up to .security_cleanup_backup/")
        print("\n⚠️  IMPORTANT: Review the backup files and ensure no credentials are committed to git!")
    
    def generate_security_report(self):
        """Generate a report of security actions taken."""
        report = {
            "timestamp": "2025-01-27T10:00:00Z",
            "action": "emergency_security_cleanup",
            "removed_files": self.removed_files,
            "backup_location": ".security_cleanup_backup",
            "recommendations": [
                "Review all backup files for sensitive content",
                "Update .gitignore to prevent future credential commits",
                "Rotate any exposed credentials immediately",
                "Implement pre-commit hooks for credential scanning"
            ]
        }
        
        with open("security_cleanup_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Security report saved to security_cleanup_report.json")

def main():
    """Run emergency security cleanup."""
    cleanup = EmergencySecurityCleanup()
    cleanup.run_emergency_cleanup()

if __name__ == "__main__":
    main()