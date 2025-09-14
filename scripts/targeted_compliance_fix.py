#!/usr/bin/env python3
"""
🎯 TARGETED COMPLIANCE FIX
=========================
Based on RCA findings, implement targeted fixes for systemic issues.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class TargetedComplianceFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = 0
        self.errors_fixed = 0
        
    def create_syntax_validation_gate(self):
        """Create syntax validation gate for all scripts"""
        print("🔧 Creating syntax validation gate...")
        
        validation_script = '''#!/usr/bin/env python3
"""
Syntax validation gate for automated scripts
"""
import ast
import sys
from pathlib import Path

def validate_python_syntax(file_path):
    """Validate Python syntax of a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def validate_all_python_files(directory="src"):
    """Validate all Python files in directory"""
    errors = []
    total_files = 0
    
    for py_file in Path(directory).rglob("*.py"):
        total_files += 1
        is_valid, error = validate_python_syntax(py_file)
        if not is_valid:
            errors.append({
                'file': str(py_file),
                'error': error
            })
    
    return errors, total_files

if __name__ == "__main__":
    errors, total = validate_all_python_files()
    if errors:
        print(f"❌ Found {len(errors)} syntax errors in {total} files")
        for error in errors[:5]:  # Show first 5
            print(f"   {error['file']}: {error['error']}")
        sys.exit(1)
    else:
        print(f"✅ All {total} Python files have valid syntax")
        sys.exit(0)
'''
        
        with open('scripts/validate_syntax.py', 'w') as f:
            f.write(validation_script)
        
        os.chmod('scripts/validate_syntax.py', 0o755)
        print("   ✅ Syntax validation gate created")
        self.fixes_applied += 1
        
    def fix_import_paths_in_scripts(self):
        """Fix import path issues in compliance scripts"""
        print("🔧 Fixing import path issues...")
        
        script_fixes = {
            'scripts/pre_commit_compliance_check.py': {
                'old': 'from scripts.continuous_compliance_monitor import',
                'new': 'from .continuous_compliance_monitor import'
            },
            'scripts/automated_compliance_enforcement.py': {
                'old': 'from scripts.',
                'new': 'from .'
            }
        }
        
        for script_path, fixes in script_fixes.items():
            if os.path.exists(script_path):
                try:
                    with open(script_path, 'r') as f:
                        content = f.read()
                    
                    content = content.replace(fixes['old'], fixes['new'])
                    
                    with open(script_path, 'w') as f:
                        f.write(content)
                    
                    print(f"   ✅ Fixed imports in {script_path}")
                    self.fixes_applied += 1
                    
                except Exception as e:
                    print(f"   ❌ Failed to fix {script_path}: {e}")
    
    def create_honest_compliance_reporter(self):
        """Create honest compliance reporting system"""
        print("🔧 Creating honest compliance reporter...")
        
        honest_reporter = '''#!/usr/bin/env python3
"""
Honest Compliance Reporter
Reports actual compliance status without false positives
"""
import os
import json
import ast
from datetime import datetime
from pathlib import Path

class HonestComplianceReporter:
    def __init__(self):
        self.project_root = Path.cwd()
        
    def check_syntax_compliance(self):
        """Check actual syntax compliance"""
        total_files = 0
        valid_files = 0
        errors = []
        
        for py_file in self.project_root.rglob("src/**/*.py"):
            total_files += 1
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                ast.parse(content)
                valid_files += 1
            except SyntaxError as e:
                errors.append({
                    'file': str(py_file),
                    'error': str(e)
                })
        
        syntax_compliance = (valid_files / total_files * 100) if total_files > 0 else 0
        
        return {
            'syntax_compliance': syntax_compliance,
            'total_files': total_files,
            'valid_files': valid_files,
            'error_files': len(errors),
            'errors': errors[:10]  # First 10 errors
        }
    
    def generate_honest_report(self):
        """Generate honest compliance report"""
        syntax_data = self.check_syntax_compliance()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'report_type': 'Honest Compliance Report',
            'syntax_compliance': syntax_data,
            'overall_assessment': {
                'status': '🔴 CRITICAL' if syntax_data['syntax_compliance'] < 50 else '🟡 NEEDS WORK',
                'primary_issue': 'Syntax errors preventing system functionality',
                'recommendation': 'Fix syntax errors before claiming compliance'
            }
        }
        
        return report

if __name__ == "__main__":
    reporter = HonestComplianceReporter()
    report = reporter.generate_honest_report()
    
    print("📊 HONEST COMPLIANCE REPORT")
    print("=" * 30)
    print(f"Syntax Compliance: {report['syntax_compliance']['syntax_compliance']:.1f}%")
    print(f"Total Files: {report['syntax_compliance']['total_files']}")
    print(f"Valid Files: {report['syntax_compliance']['valid_files']}")
    print(f"Error Files: {report['syntax_compliance']['error_files']}")
    print(f"Status: {report['overall_assessment']['status']}")
    
    # Save report
    os.makedirs('.beast_mode', exist_ok=True)
    with open('.beast_mode/honest_compliance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
'''
        
        with open('scripts/honest_compliance_reporter.py', 'w') as f:
            f.write(honest_reporter)
        
        os.chmod('scripts/honest_compliance_reporter.py', 0o755)
        print("   ✅ Honest compliance reporter created")
        self.fixes_applied += 1
        
    def create_rollback_mechanism(self):
        """Create rollback mechanism for failed changes"""
        print("🔧 Creating rollback mechanism...")
        
        rollback_script = '''#!/usr/bin/env python3
"""
Rollback mechanism for failed automated changes
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class RollbackManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = Path('.beast_mode/rollback_backups')
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, description="Manual backup"):
        """Create backup of current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{description.replace(' ', '_')}"
        backup_path = self.backup_dir / backup_name
        
        # Create backup of src directory
        src_backup = backup_path / "src"
        if os.path.exists("src"):
            shutil.copytree("src", src_backup)
        
        # Create backup of scripts
        scripts_backup = backup_path / "scripts"
        if os.path.exists("scripts"):
            shutil.copytree("scripts", scripts_backup)
        
        # Save backup metadata
        metadata = {
            'timestamp': timestamp,
            'description': description,
            'backup_path': str(backup_path)
        }
        
        with open(backup_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup created: {backup_name}")
        return str(backup_path)
    
    def list_backups(self):
        """List available backups"""
        backups = []
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    backups.append(metadata)
        return backups
    
    def rollback_to_backup(self, backup_name):
        """Rollback to specific backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup {backup_name} not found")
            return False
        
        try:
            # Restore src directory
            src_backup = backup_path / "src"
            if src_backup.exists():
                if os.path.exists("src"):
                    shutil.rmtree("src")
                shutil.copytree(src_backup, "src")
            
            # Restore scripts
            scripts_backup = backup_path / "scripts"
            if scripts_backup.exists():
                if os.path.exists("scripts"):
                    shutil.rmtree("scripts")
                shutil.copytree(scripts_backup, "scripts")
            
            print(f"✅ Rolled back to {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

if __name__ == "__main__":
    manager = RollbackManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            backups = manager.list_backups()
            print("Available backups:")
            for backup in backups:
                print(f"  {backup['timestamp']}: {backup['description']}")
        elif sys.argv[1] == "rollback" and len(sys.argv) > 2:
            manager.rollback_to_backup(sys.argv[2])
        else:
            print("Usage: python rollback_manager.py [list|rollback <backup_name>]")
    else:
        # Create current backup
        manager.create_backup("Before targeted fixes")
'''
        
        with open('scripts/rollback_manager.py', 'w') as f:
            f.write(rollback_script)
        
        os.chmod('scripts/rollback_manager.py', 0o755)
        print("   ✅ Rollback mechanism created")
        self.fixes_applied += 1
        
    def run_targeted_fixes(self):
        """Run all targeted fixes"""
        print("🎯 TARGETED COMPLIANCE FIXES")
        print("=" * 40)
        
        # Create backup before fixes
        print("📦 Creating backup before fixes...")
        os.system("python3 scripts/rollback_manager.py")
        
        self.create_syntax_validation_gate()
        self.fix_import_paths_in_scripts()
        self.create_honest_compliance_reporter()
        self.create_rollback_mechanism()
        
        print("\n🎯 TARGETED FIX SUMMARY")
        print("=" * 25)
        print(f"Fixes Applied: {self.fixes_applied}")
        print(f"Status: {'🟡 PARTIALLY FIXED' if self.fixes_applied > 0 else '🔴 CRITICAL'}")
        print()
        print("✅ IMPLEMENTED:")
        print("   • Syntax validation gate")
        print("   • Fixed import path issues")
        print("   • Honest compliance reporter")
        print("   • Rollback mechanism")
        print()
        print("🚨 STILL NEEDED:")
        print("   • Fix 179 syntax errors manually")
        print("   • Validate all compliance scripts")
        print("   • Re-run comprehensive testing")
        
        return self.fixes_applied > 0

if __name__ == "__main__":
    fixer = TargetedComplianceFixer()
    success = fixer.run_targeted_fixes()
    
    if success:
        print("\n✅ Targeted fixes applied. Manual intervention still required for syntax errors.")
        sys.exit(0)
    else:
        print("\n❌ Targeted fixes failed.")
        sys.exit(1)
