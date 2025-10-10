#!/usr/bin/env python3
"""
Remove Hardcoded Redis Passwords
===============================

Scan and replace all hardcoded Redis passwords with environment variable usage.
Security remediation script to eliminate credential exposure.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class PasswordRemediator:
    """Remove hardcoded passwords from codebase."""
    
    def __init__(self):
        self.password_pattern = ros.getenv('REDIS_PASSWORD', '')
        self.replacements_made = 0
        self.files_modified = 0
        self.scan_results = []
    
    def scan_repository(self, root_path: str = ".") -> List[Dict]:
        """Scan repository for hardcoded passwords."""
        print("🔍 Scanning repository for hardcoded Redis passwords...")
        
        results = []
        root = Path(root_path)
        
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache'}
        
        for file_path in root.rglob('*'):
            if file_path.is_file() and not any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                # Only scan text files
                if self.is_text_file(file_path):
                    matches = self.scan_file(file_path)
                    if matches:
                        results.append({
                            'file': str(file_path),
                            'matches': matches
                        })
        
        self.scan_results = results
        return results
    
    def is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file we should scan."""
        text_extensions = {'.py', '.sh', '.md', '.json', '.yaml', '.yml', '.txt', '.env', '.conf'}
        
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Check if file has no extension but might be text
        if not file_path.suffix:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1024)  # Try to read first 1KB
                return True
            except (UnicodeDecodeError, PermissionError):
                return False
        
        return False
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for password occurrences."""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                if re.search(self.password_pattern, line):
                    matches.append({
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'context': self.get_context_type(line)
                    })
        
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"⚠️  Could not read {file_path}: {e}")
        
        return matches
    
    def get_context_type(self, line: str) -> str:
        """Determine the context type of the password usage."""
        line_lower = line.lower()
        
        if 'redis.redis(' in line_lower or 'redis(' in line_lower:
            return 'redis_constructor'
        elif 'redis.from_url(' in line_lower:
            return 'redis_url'
        elif 'redis_password' in line_lower:
            return 'variable_assignment'
        elif 'password=' in line_lower:
            return 'parameter_assignment'
        elif '.conf' in line_lower or 'requirepass' in line_lower:
            return 'config_file'
        elif 'redis-cli' in line_lower:
            return 'cli_command'
        else:
            return 'unknown'
    
    def generate_replacement_suggestions(self) -> Dict[str, List[str]]:
        """Generate replacement suggestions for different contexts."""
        suggestions = {
            'redis_constructor': [
                "# Replace with:",
                "password=os.getenv('REDIS_PASSWORD', '')",
                "# Add at top of file:",
                "import os"
            ],
            'redis_url': [
                "# Replace with:",
                "redis_password = os.getenv('REDIS_PASSWORD', '')",
                "client = redis.from_url(f'redis://:{redis_password}@192.168.1.119:6379')",
                "# Add at top of file:",
                "import os"
            ],
            'variable_assignment': [
                "# Replace with:",
                "REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')",
                "# Add at top of file:",
                "import os"
            ],
            'parameter_assignment': [
                "# Replace with:",
                "'password': os.getenv('REDIS_PASSWORD', '')",
                "# Add at top of file:",
                "import os"
            ],
            'config_file': [
                "# For config files, consider using environment substitution",
                "# or generating config from template with environment variables"
            ],
            'cli_command': [
                "# Replace with:",
                "redis-cli -h 192.168.1.119 -a \"$REDIS_PASSWORD\"",
                "# Ensure REDIS_PASSWORD is set in environment"
            ]
        }
        return suggestions
    
    def create_remediation_plan(self) -> str:
        """Create a detailed remediation plan."""
        if not self.scan_results:
            return "✅ No hardcoded passwords found!"
        
        plan = []
        plan.append("🚨 SECURITY REMEDIATION PLAN")
        plan.append("=" * 50)
        plan.append(f"Found hardcoded passwords in {len(self.scan_results)} files")
        plan.append("")
        
        # Group by context type
        context_counts = {}
        for result in self.scan_results:
            for match in result['matches']:
                context = match['context']
                context_counts[context] = context_counts.get(context, 0) + 1
        
        plan.append("📊 Password Usage by Context:")
        for context, count in sorted(context_counts.items()):
            plan.append(f"  • {context}: {count} occurrences")
        plan.append("")
        
        # Detailed file list
        plan.append("📁 Files requiring remediation:")
        for result in self.scan_results:
            plan.append(f"\n🔧 {result['file']}")
            for match in result['matches']:
                plan.append(f"   Line {match['line_number']}: {match['line_content'][:80]}...")
                plan.append(f"   Context: {match['context']}")
        
        plan.append("\n" + "=" * 50)
        plan.append("🛠️  REMEDIATION STEPS:")
        plan.append("1. Add REDIS_PASSWORD to ~/.env file")
        plan.append("2. Update each file to use os.getenv('REDIS_PASSWORD', '')")
        plan.append("3. Test all Redis connections still work")
        plan.append("4. Remove hardcoded passwords from git history if needed")
        
        suggestions = self.generate_replacement_suggestions()
        plan.append("\n💡 REPLACEMENT PATTERNS:")
        for context, suggestion_list in suggestions.items():
            if context in context_counts:
                plan.append(f"\n{context.upper()}:")
                for suggestion in suggestion_list:
                    plan.append(f"  {suggestion}")
        
        return "\n".join(plan)
    
    def create_env_file_template(self) -> str:
        """Create ~/.env file template."""
        template = [
            "# Redis Configuration for Beast Mode",
            "# Add this to your ~/.env file",
            "",
            "REDIS_PASSWORD=beastmode2025",
            "BEAST_MODE_REDIS_PASSWORD=beastmode2025",
            "",
            "# Redis connection details",
            "REDIS_HOST=192.168.1.119",
            "REDIS_PORT=6379",
            "",
            "# Environment identification",
            "DEVELOPMENT=true",
            "# PRODUCTION=true  # Uncomment for production",
            "",
            "# Beast Mode settings",
            "BEAST_MODE_ENV=development"
        ]
        return "\n".join(template)
    
    def save_remediation_report(self) -> str:
        """Save detailed remediation report."""
        report_file = "redis_password_remediation_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Redis Password Remediation Report\n\n")
            f.write(f"Generated: {os.popen('date').read().strip()}\n\n")
            f.write(self.create_remediation_plan())
            f.write("\n\n## Environment File Template\n\n")
            f.write("```bash\n")
            f.write(self.create_env_file_template())
            f.write("\n```\n")
        
        return report_file


def main():
    """Main remediation function."""
    remediator = PasswordRemediator()
    
    print("🔐 Redis Password Security Remediation")
    print("=" * 50)
    
    # Scan repository
    results = remediator.scan_repository()
    
    if not results:
        print("✅ No hardcoded Redis passwords found!")
        return
    
    print(f"🚨 Found hardcoded passwords in {len(results)} files")
    
    # Create remediation plan
    plan = remediator.create_remediation_plan()
    print("\n" + plan)
    
    # Save detailed report
    report_file = remediator.save_remediation_report()
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Create environment template
    env_template_file = "redis_env_template.txt"
    with open(env_template_file, 'w') as f:
        f.write(remediator.create_env_file_template())
    print(f"📄 Environment template saved to: {env_template_file}")
    
    print("\n🚨 IMMEDIATE ACTION REQUIRED:")
    print("1. Review the remediation report")
    print("2. Add REDIS_PASSWORD to ~/.env")
    print("3. Update files to use environment variables")
    print("4. Test Redis connectivity")
    print("5. Consider rotating the Redis password")


if __name__ == "__main__":
    main()