#!/usr/bin/env python3
"""
Hardcoded Credential Remediation Tool
====================================

Automatically fixes hardcoded credentials by replacing them with secure environment variable usage.
Part of the security governance enforcement system.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json
import shutil
from datetime import datetime


class CredentialRemediator:
    """Automatically remediates hardcoded credentials."""
    
    def __init__(self):
        """Initialize the credential remediator."""
        self.backup_dir = Path("credential_remediation_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Remediation patterns - maps hardcoded patterns to secure replacements
        self.remediation_patterns = {
            # Redis password patterns
            r'redis_password\s*=\s*["\']beastmode2025["\']': 
                'redis_password = os.getenv("REDIS_PASSWORD", "")',
            
            r'password\s*=\s*["\']beastmode2025["\']': 
                'password = os.getenv("REDIS_PASSWORD", "")',
            
            r'["\']beastmode2025["\']': 
                'os.getenv("REDIS_PASSWORD", "")',
            
            # Generic password patterns
            r'password\s*=\s*["\']([^"\']+)["\']': 
                'password = os.getenv("PASSWORD", "")',
            
            # API key patterns
            r'api_key\s*=\s*["\']sk-([^"\']+)["\']': 
                'api_key = os.getenv("OPENAI_API_KEY", "")',
            
            r'api_key\s*=\s*["\']([^"\']+)["\']': 
                'api_key = os.getenv("API_KEY", "")',
            
            # Token patterns
            r'token\s*=\s*["\']([^"\']+)["\']': 
                'token = os.getenv("AUTH_TOKEN", "")',
            
            # Secret patterns
            r'secret\s*=\s*["\']([^"\']+)["\']': 
                'secret = os.getenv("SECRET_KEY", "")',
        }
        
        # Required imports to add
        self.required_imports = [
            'import os',
            'from src.security.secure_credentials import get_secure_credentials'
        ]
    
    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of the file before modification."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def add_required_imports(self, content: str) -> str:
        """Add required imports if not present."""
        lines = content.split('\n')
        
        # Find where to insert imports (after shebang and docstring)
        insert_index = 0
        in_docstring = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip shebang
            if stripped.startswith('#!'):
                insert_index = i + 1
                continue
            
            # Handle docstrings
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                else:
                    in_docstring = False
                    insert_index = i + 1
                continue
            
            # If we're past docstring and hit an import, insert before it
            if not in_docstring and (stripped.startswith('import ') or stripped.startswith('from ')):
                break
            
            # If we're past docstring and hit non-import code, insert here
            if not in_docstring and stripped and not stripped.startswith('#'):
                break
            
            if not in_docstring:
                insert_index = i + 1
        
        # Check which imports are needed
        imports_to_add = []
        for required_import in self.required_imports:
            if required_import not in content:
                imports_to_add.append(required_import)
        
        # Insert imports
        if imports_to_add:
            lines.insert(insert_index, '')
            for import_line in reversed(imports_to_add):
                lines.insert(insert_index, import_line)
            lines.insert(insert_index, '# ✅ SECURE: Added by credential remediation')
        
        return '\n'.join(lines)
    
    def remediate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Remediate hardcoded credentials in a single file."""
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Create backup
            backup_path = self.backup_file(file_path)
            
            # Apply remediation patterns
            modified_content = original_content
            changes_made = []
            
            for pattern, replacement in self.remediation_patterns.items():
                matches = re.findall(pattern, modified_content, re.IGNORECASE)
                if matches:
                    modified_content = re.sub(pattern, replacement, modified_content, flags=re.IGNORECASE)
                    changes_made.append(f"Replaced pattern: {pattern}")
            
            # Add required imports if changes were made
            if changes_made:
                modified_content = self.add_required_imports(modified_content)
                changes_made.append("Added required imports")
            
            # Write modified content
            if changes_made:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                print(f"✅ Remediated: {file_path}")
                print(f"   Backup: {backup_path}")
                for change in changes_made:
                    print(f"   • {change}")
                
                return True, changes_made
            else:
                # Remove backup if no changes made
                backup_path.unlink()
                return False, []
                
        except Exception as e:
            print(f"❌ Error remediating {file_path}: {e}")
            return False, [f"Error: {e}"]
    
    def remediate_critical_files(self, scan_report_file: str = "credential_scan_report.json") -> Dict:
        """Remediate files with critical credential violations."""
        if not Path(scan_report_file).exists():
            print(f"❌ Scan report not found: {scan_report_file}")
            print("Run: python3 scripts/scan_for_hardcoded_credentials.py first")
            return {}
        
        # Load scan report
        with open(scan_report_file, 'r') as f:
            report = json.load(f)
        
        # Filter critical violations
        critical_violations = [
            v for v in report['violations'] 
            if v['severity'] == 'CRITICAL'
        ]
        
        if not critical_violations:
            print("✅ No critical violations found!")
            return {}
        
        print(f"🚨 Found {len(critical_violations)} critical violations")
        print("🔧 Starting automatic remediation...")
        
        # Group by file
        files_to_remediate = {}
        for violation in critical_violations:
            file_path = violation['file']
            if file_path not in files_to_remediate:
                files_to_remediate[file_path] = []
            files_to_remediate[file_path].append(violation)
        
        # Remediate each file
        remediation_results = {}
        for file_path, violations in files_to_remediate.items():
            print(f"\n🔧 Remediating: {file_path}")
            print(f"   Violations: {len(violations)}")
            
            success, changes = self.remediate_file(Path(file_path))
            remediation_results[file_path] = {
                'success': success,
                'changes': changes,
                'violations_count': len(violations)
            }
        
        return remediation_results
    
    def create_env_template(self, scan_report_file: str = "credential_scan_report.json") -> None:
        """Create a ~/.env template with all required credentials."""
        if not Path(scan_report_file).exists():
            return
        
        with open(scan_report_file, 'r') as f:
            report = json.load(f)
        
        # Extract unique credentials needed
        env_vars = set()
        for violation in report['violations']:
            if os.getenv('REDIS_PASSWORD', '') in violation['pattern'].lower():
                env_vars.add('REDIS_PASSWORD')
            elif 'sk-' in violation['pattern']:
                env_vars.add('OPENAI_API_KEY')
            elif 'password' in violation['type']:
                env_vars.add('PASSWORD')
            elif 'api_key' in violation['type']:
                env_vars.add('API_KEY')
            elif 'token' in violation['type']:
                env_vars.add('AUTH_TOKEN')
            elif 'secret' in violation['type']:
                env_vars.add('SECRET_KEY')
        
        # Create template
        template_content = """# Environment Variables Template
# Generated by credential remediation tool
# Copy this to ~/.env and update with your actual values

# CRITICAL: Never commit this file to version control!

"""
        
        for env_var in sorted(env_vars):
            if env_var == 'REDIS_PASSWORD':
                template_content += f"{env_var}=beastmode2025\n"
            else:
                template_content += f"{env_var}=your_actual_value_here\n"
        
        template_content += """
# Additional common credentials
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DATABASE_PASSWORD=your_db_password_here

# Environment identification
DEVELOPMENT=true
# PRODUCTION=true  # Uncomment for production
"""
        
        template_file = Path.home() / ".env.template"
        with open(template_file, 'w') as f:
            f.write(template_content)
        
        print(f"📄 Environment template created: {template_file}")
        print("💡 Copy to ~/.env and update with your actual values")


def main():
    """Main remediation function."""
    print("🔧 HARDCODED CREDENTIAL REMEDIATION TOOL")
    print("=" * 50)
    
    remediator = CredentialRemediator()
    
    # Check if scan report exists
    scan_report = "credential_scan_report.json"
    if not Path(scan_report).exists():
        print("❌ No scan report found!")
        print("Run this first: python3 scripts/scan_for_hardcoded_credentials.py")
        sys.exit(1)
    
    # Remediate critical files
    results = remediator.remediate_critical_files(scan_report)
    
    if not results:
        print("✅ No files needed remediation!")
        return
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 REMEDIATION SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"Files processed: {total}")
    print(f"Successfully remediated: {successful}")
    print(f"Failed: {total - successful}")
    
    if successful > 0:
        print(f"\n✅ Remediation completed!")
        print(f"📁 Backups saved in: {remediator.backup_dir}")
        
        # Create environment template
        remediator.create_env_template(scan_report)
        
        print(f"\n🔍 Run scan again to verify fixes:")
        print(f"python3 scripts/scan_for_hardcoded_credentials.py")
    
    # Exit with appropriate code
    sys.exit(0 if successful == total else 1)


if __name__ == "__main__":
    main()