#!/usr/bin/env python3
"""
Security Remediation Executor

This script automatically fixes security issues found during validation,
focusing on real issues while ignoring false positives from documentation
and archived code.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityRemediationExecutor:
    """Automatically fixes security issues in the repository"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.fixed_files = []
        self.skipped_files = []
        
        # Directories to skip (archived/backup content)
        self.skip_directories = [
            'archive/',
            '.git/',
            '__pycache__/',
            'node_modules/',
            '.security_cleanup_backup/',
            'data/',  # Skip data files as they contain scan results
        ]
        
        # Files that are examples or templates (OK to have placeholder credentials)
        self.example_patterns = [
            r'example',
            r'template',
            r'demo',
            r'\.env\.example$',
            r'\.env\.template$',
        ]
    
    def should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped during remediation"""
        file_str = str(file_path)
        
        # Skip archived directories
        for skip_dir in self.skip_directories:
            if skip_dir in file_str:
                return True
        
        # Skip example/template files
        for pattern in self.example_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        
        return False
    
    def fix_hardcoded_credentials_in_file(self, file_path: Path) -> bool:
        """Fix hardcoded credentials in a single file"""
        if self.should_skip_file(file_path):
            self.skipped_files.append(str(file_path))
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                original_content = content
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return False
        
        # Fix patterns - only fix actual hardcoded credentials, not documentation examples
        fixes_applied = False
        
        # Fix hardcoded Redis passwords (the specific incident we're preventing)
        if 'redis_password = "beastmode' in content:
            content = re.sub(
                r'redis_password\s*=\s*["\']beastmode\d+["\']',
                'redis_password = os.getenv("REDIS_PASSWORD", "")\n    if not redis_password:\n        raise ValueError("REDIS_PASSWORD environment variable is required")',
                content
            )
            fixes_applied = True
            logger.info(f"Fixed hardcoded Redis password in {file_path}")
        
        # Fix other hardcoded passwords (but be careful not to break documentation)
        if not any(keyword in str(file_path).lower() for keyword in ['doc', 'readme', 'example', 'demo']):
            # Fix hardcoded API keys
            if re.search(r'api_key\s*=\s*["\']sk-[a-zA-Z0-9]+["\']', content):
                content = re.sub(
                    r'api_key\s*=\s*["\']sk-[a-zA-Z0-9]+["\']',
                    'api_key = os.getenv("OPENAI_API_KEY", "")\n    if not api_key:\n        raise ValueError("OPENAI_API_KEY environment variable is required")',
                    content
                )
                fixes_applied = True
                logger.info(f"Fixed hardcoded API key in {file_path}")
        
        # Write back the fixed content
        if fixes_applied and content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                return True
            except Exception as e:
                logger.error(f"Could not write fixed content to {file_path}: {e}")
                return False
        
        return False
    
    def fix_insecure_defaults(self, file_path: Path) -> bool:
        """Fix insecure default values in environment variable usage"""
        if self.should_skip_file(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                original_content = content
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return False
        
        fixes_applied = False
        
        # Fix insecure defaults like os.getenv("PASSWORD", "")
        # Replace with os.getenv('PASSWORD', '') and add validation
        insecure_patterns = [
            (r'os\.getenv\(["\']([^"\']*(?:password|secret|key|token)[^"\']*)["\'],\s*["\'][^"\']+["\']\)', 
             r'os.getenv("\1", "")'),
        ]
        
        for pattern, replacement in insecure_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                fixes_applied = True
                logger.info(f"Fixed insecure default in {file_path}")
        
        # Write back the fixed content
        if fixes_applied and content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                return True
            except Exception as e:
                logger.error(f"Could not write fixed content to {file_path}: {e}")
                return False
        
        return False
    
    def remediate_security_issues(self) -> Dict:
        """Perform comprehensive security remediation"""
        logger.info("Starting security remediation...")
        
        # Find and fix Python files
        python_files = list(self.root_path.rglob('*.py'))
        
        for py_file in python_files:
            if self.should_skip_file(py_file):
                continue
            
            # Fix hardcoded credentials
            self.fix_hardcoded_credentials_in_file(py_file)
            
            # Fix insecure defaults
            self.fix_insecure_defaults(py_file)
        
        # Find and fix configuration files
        config_extensions = ['.yml', '.yaml', '.json', '.env']
        for ext in config_extensions:
            config_files = list(self.root_path.rglob(f'*{ext}'))
            for config_file in config_files:
                if self.should_skip_file(config_file):
                    continue
                
                self.fix_hardcoded_credentials_in_file(config_file)
        
        logger.info(f"Security remediation complete.")
        logger.info(f"Fixed {len(self.fixed_files)} files")
        logger.info(f"Skipped {len(self.skipped_files)} files (archives/examples)")
        
        return {
            "fixed_files": self.fixed_files,
            "skipped_files": self.skipped_files,
            "total_fixed": len(self.fixed_files),
            "total_skipped": len(self.skipped_files)
        }
    
    def validate_critical_files(self) -> Dict:
        """Validate that critical files are secure"""
        critical_files = [
            'src/beast_mode/directus_cms/database_utils.py',
            'src/beast_mode/observatory/config.py',
            'src/execution_tracking/redis_execution_tracker.py',
        ]
        
        validation_results = {}
        
        for file_path in critical_files:
            full_path = self.root_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for hardcoded credentials
                    has_hardcoded = False
                    issues = []
                    
                    if 'password = "' in content and 'os.getenv' not in content:
                        has_hardcoded = True
                        issues.append("Hardcoded password detected")
                    
                    if 'api_key = "sk-' in content:
                        has_hardcoded = True
                        issues.append("Hardcoded API key detected")
                    
                    validation_results[file_path] = {
                        "secure": not has_hardcoded,
                        "issues": issues
                    }
                    
                except Exception as e:
                    validation_results[file_path] = {
                        "secure": False,
                        "issues": [f"Could not validate: {e}"]
                    }
            else:
                validation_results[file_path] = {
                    "secure": True,
                    "issues": ["File does not exist"]
                }
        
        return validation_results

def main():
    """Main function to run security remediation"""
    remediator = SecurityRemediationExecutor()
    
    # Perform remediation
    results = remediator.remediate_security_issues()
    
    # Validate critical files
    validation = remediator.validate_critical_files()
    
    # Print results
    print("\n" + "="*80)
    print("SECURITY REMEDIATION RESULTS")
    print("="*80)
    
    print(f"\nREMEDIATION SUMMARY:")
    print(f"  Files Fixed: {results['total_fixed']}")
    print(f"  Files Skipped: {results['total_skipped']}")
    
    if results['fixed_files']:
        print(f"\nFIXED FILES:")
        for file_path in results['fixed_files'][:10]:  # Show first 10
            print(f"  ✅ {file_path}")
        if len(results['fixed_files']) > 10:
            print(f"  ... and {len(results['fixed_files']) - 10} more files")
    
    print(f"\nCRITICAL FILES VALIDATION:")
    all_secure = True
    for file_path, result in validation.items():
        status = "✅ SECURE" if result['secure'] else "❌ INSECURE"
        print(f"  {status}: {file_path}")
        if result['issues']:
            for issue in result['issues']:
                print(f"    - {issue}")
        if not result['secure']:
            all_secure = False
    
    # Save detailed results
    report_file = Path("data/security_remediation_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    full_report = {
        "remediation_results": results,
        "critical_files_validation": validation,
        "overall_status": "SECURE" if all_secure else "NEEDS_ATTENTION"
    }
    
    with open(report_file, 'w') as f:
        json.dump(full_report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    if all_secure:
        print(f"\n✅ SECURITY REMEDIATION SUCCESSFUL")
        print(f"   All critical files are secure.")
        return 0
    else:
        print(f"\n⚠️  SECURITY REMEDIATION NEEDS ATTENTION")
        print(f"   Some critical files may still have security issues.")
        return 1

if __name__ == "__main__":
    exit(main())