#!/usr/bin/env python3
"""
🚀 BEAST MODE MANUAL SYNTAX FIXER
================================
Sophisticated manual fixing of remaining 194 syntax errors for full compliance.
"""

import os
import sys
import json
import ast
import re
import shutil
from datetime import datetime
from pathlib import Path

class BeastModeManualSyntaxFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = 0
        self.files_fixed = 0
        self.target_compliance = 95.0
        
    def create_beast_mode_backup(self):
        """Create Beast Mode backup before manual fixes"""
        print("🚀 Creating Beast Mode backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f".beast_mode/manual_syntax_fix_backup_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup critical directories
        for dir_name in ["src", "scripts"]:
            if os.path.exists(dir_name):
                shutil.copytree(dir_name, backup_dir / dir_name)
        
        print(f"   ✅ Beast Mode backup created: {backup_dir}")
        return str(backup_dir)
    
    def identify_syntax_errors(self):
        """Identify all syntax errors with detailed analysis"""
        print("🔍 Identifying syntax errors with detailed analysis...")
        
        syntax_errors = []
        
        for py_file in self.project_root.rglob("src/**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                error_info = {
                    'file': str(py_file),
                    'error': str(e),
                    'line': e.lineno if hasattr(e, 'lineno') else None,
                    'text': e.text if hasattr(e, 'text') else None,
                    'offset': e.offset if hasattr(e, 'offset') else None,
                    'msg': e.msg if hasattr(e, 'msg') else str(e)
                }
                syntax_errors.append(error_info)
        
        print(f"   📊 Found {len(syntax_errors)} syntax errors")
        return syntax_errors
    
    def categorize_errors(self, syntax_errors):
        """Categorize errors by type for targeted fixing"""
        print("📋 Categorizing errors by type...")
        
        categories = {
            'expected_indented_block': [],
            'unindent_mismatch': [],
            'invalid_syntax': [],
            'unexpected_indent': [],
            'unexpected_unindent': [],
            'eol_while_scanning': [],
            'unterminated_string': [],
            'missing_colon': [],
            'bracket_mismatch': [],
            'other': []
        }
        
        for error in syntax_errors:
            error_msg = error['msg'].lower()
            
            if 'expected an indented block' in error_msg:
                categories['expected_indented_block'].append(error)
            elif 'unindent does not match' in error_msg:
                categories['unindent_mismatch'].append(error)
            elif 'invalid syntax' in error_msg:
                categories['invalid_syntax'].append(error)
            elif 'unexpected indent' in error_msg:
                categories['unexpected_indent'].append(error)
            elif 'unexpected unindent' in error_msg:
                categories['unexpected_unindent'].append(error)
            elif 'eol while scanning string literal' in error_msg:
                categories['eol_while_scanning'].append(error)
            elif 'unterminated string' in error_msg:
                categories['unterminated_string'].append(error)
            elif 'expected \':\'' in error_msg:
                categories['missing_colon'].append(error)
            elif any(char in error_msg for char in ['(', ')', '[', ']', '{', '}']):
                categories['bracket_mismatch'].append(error)
            else:
                categories['other'].append(error)
        
        # Print categorization summary
        for category, errors in categories.items():
            if errors:
                print(f"      {category}: {len(errors)} errors")
        
        return categories
    
    def fix_expected_indented_block_errors(self, errors):
        """Fix expected indented block errors"""
        print("🔧 Fixing expected indented block errors...")
        
        fixes_applied = 0
        for error in errors:
            file_path = error['file']
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                error_line = error['line'] - 1 if error['line'] else 0
                if error_line < len(lines):
                    line_content = lines[error_line]
                    
                    # Check if previous line ends with colon
                    if error_line > 0:
                        prev_line = lines[error_line - 1]
                        if prev_line.strip().endswith(':'):
                            # Determine proper indentation
                            base_indent = len(prev_line) - len(prev_line.lstrip())
                            new_indent = base_indent + 4
                            
                            # Add pass statement with proper indentation
                            lines.insert(error_line + 1, ' ' * new_indent + 'pass\n')
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.writelines(lines)
                            
                            fixes_applied += 1
                            print(f"      ✅ Fixed: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")
        
        return fixes_applied
    
    def fix_unindent_mismatch_errors(self, errors):
        """Fix unindent mismatch errors"""
        print("🔧 Fixing unindent mismatch errors...")
        
        fixes_applied = 0
        for error in errors:
            file_path = error['file']
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                error_line = error['line'] - 1 if error['line'] else 0
                if error_line < len(lines):
                    # Find proper indentation level by looking at context
                    proper_indent = 0
                    
                    # Look backwards for a line with proper indentation
                    for i in range(error_line - 1, -1, -1):
                        if lines[i].strip() and not lines[i].startswith('#'):
                            if lines[i].strip().endswith(':'):
                                # Block start, use +4
                                proper_indent = len(lines[i]) - len(lines[i].lstrip()) + 4
                            else:
                                # Same level
                                proper_indent = len(lines[i]) - len(lines[i].lstrip())
                            break
                    
                    # Fix the indentation
                    if lines[error_line].strip():
                        lines[error_line] = ' ' * proper_indent + lines[error_line].lstrip()
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        
                        fixes_applied += 1
                        print(f"      ✅ Fixed: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")
        
        return fixes_applied
    
    def fix_unexpected_indent_errors(self, errors):
        """Fix unexpected indent errors"""
        print("🔧 Fixing unexpected indent errors...")
        
        fixes_applied = 0
        for error in errors:
            file_path = error['file']
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                error_line = error['line'] - 1 if error['line'] else 0
                if error_line < len(lines):
                    # Find proper indentation by looking at previous lines
                    proper_indent = 0
                    
                    for i in range(error_line - 1, -1, -1):
                        if lines[i].strip() and not lines[i].startswith('#'):
                            proper_indent = len(lines[i]) - len(lines[i].lstrip())
                            break
                    
                    # Fix the indentation
                    if lines[error_line].strip():
                        lines[error_line] = ' ' * proper_indent + lines[error_line].lstrip()
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        
                        fixes_applied += 1
                        print(f"      ✅ Fixed: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")
        
        return fixes_applied
    
    def fix_missing_colon_errors(self, errors):
        """Fix missing colon errors"""
        print("🔧 Fixing missing colon errors...")
        
        fixes_applied = 0
        for error in errors:
            file_path = error['file']
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                error_line = error['line'] - 1 if error['line'] else 0
                if error_line < len(lines):
                    line_content = lines[error_line]
                    
                    # Check if line needs a colon
                    if re.match(r'^\s*(if|for|while|def|class|try|except|finally|with|async def)\s+', line_content):
                        if not line_content.rstrip().endswith(':'):
                            lines[error_line] = line_content.rstrip() + ':\n'
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.writelines(lines)
                            
                            fixes_applied += 1
                            print(f"      ✅ Fixed: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")
        
        return fixes_applied
    
    def fix_eol_string_errors(self, errors):
        """Fix EOL while scanning string literal errors"""
        print("🔧 Fixing EOL while scanning string literal errors...")
        
        fixes_applied = 0
        for error in errors:
            file_path = error['file']
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix common string literal issues
                original_content = content
                
                # Fix unterminated strings by adding closing quotes
                content = re.sub(r'(\'[^\']*$)', r'\1\'', content)
                content = re.sub(r'(\"[^\"]*$)', r'\1"', content)
                
                # Fix triple quotes
                content = re.sub(r'(\'\'\'[^\'\'\']*$)', r'\1\'\'\'', content)
                content = re.sub(r'(\"\"\"[^\"\"\"]*$)', r'\1\"\"\"', content)
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fixes_applied += 1
                    print(f"      ✅ Fixed: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")
        
        return fixes_applied
    
    def fix_invalid_syntax_errors(self, errors):
        """Fix invalid syntax errors with pattern matching"""
        print("🔧 Fixing invalid syntax errors...")
        
        fixes_applied = 0
        for error in errors:
            file_path = error['file']
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix common invalid syntax patterns
                fixes = [
                    # Fix double colons
                    (r'::+', ':'),
                    # Fix missing spaces around operators
                    (r'(\w)([=+\-*/])(\w)', r'\1 \2 \3'),
                    # Fix missing spaces after commas
                    (r',(\w)', r', \1'),
                    # Fix common bracket issues
                    (r'\(\s*\)', '()'),
                    (r'\[\s*\]', '[]'),
                    (r'\{\s*\}', '{}'),
                    # Fix trailing commas in function calls
                    (r',\s*\)', ')'),
                    (r',\s*\]', ']'),
                    (r',\s*\}', '}'),
                ]
                
                for pattern, replacement in fixes:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fixes_applied += 1
                    print(f"      ✅ Fixed: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")
        
        return fixes_applied
    
    def apply_comprehensive_fixes(self, categories):
        """Apply comprehensive fixes to all error categories"""
        print("🚀 Applying comprehensive Beast Mode fixes...")
        
        total_fixes = 0
        
        # Fix errors by category
        if categories['expected_indented_block']:
            fixes = self.fix_expected_indented_block_errors(categories['expected_indented_block'])
            total_fixes += fixes
        
        if categories['unindent_mismatch']:
            fixes = self.fix_unindent_mismatch_errors(categories['unindent_mismatch'])
            total_fixes += fixes
        
        if categories['unexpected_indent']:
            fixes = self.fix_unexpected_indent_errors(categories['unexpected_indent'])
            total_fixes += fixes
        
        if categories['missing_colon']:
            fixes = self.fix_missing_colon_errors(categories['missing_colon'])
            total_fixes += fixes
        
        if categories['eol_while_scanning']:
            fixes = self.fix_eol_string_errors(categories['eol_while_scanning'])
            total_fixes += fixes
        
        if categories['invalid_syntax']:
            fixes = self.fix_invalid_syntax_errors(categories['invalid_syntax'])
            total_fixes += fixes
        
        return total_fixes
    
    def validate_fixes(self):
        """Validate all fixes and measure compliance"""
        print("✅ Validating Beast Mode fixes...")
        
        total_files = 0
        valid_files = 0
        remaining_errors = []
        
        for py_file in self.project_root.rglob("src/**/*.py"):
            total_files += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                valid_files += 1
            except SyntaxError as e:
                remaining_errors.append({
                    'file': str(py_file),
                    'error': str(e)
                })
        
        compliance_percentage = (valid_files / total_files * 100) if total_files > 0 else 0
        
        print(f"   📊 Total Files: {total_files}")
        print(f"   ✅ Valid Files: {valid_files}")
        print(f"   ❌ Error Files: {len(remaining_errors)}")
        print(f"   📈 Compliance: {compliance_percentage:.1f}%")
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'error_files': len(remaining_errors),
            'compliance_percentage': compliance_percentage,
            'remaining_errors': remaining_errors[:10]  # Sample of remaining errors
        }
    
    def run_beast_mode_manual_fixes(self):
        """Run complete Beast Mode manual syntax fixing process"""
        print("🚀 BEAST MODE MANUAL SYNTAX FIXING")
        print("=" * 50)
        print(f"🎯 Target Compliance: {self.target_compliance}%")
        print()
        
        # Create backup
        backup_dir = self.create_beast_mode_backup()
        
        # Get initial compliance
        initial_validation = self.validate_fixes()
        initial_compliance = initial_validation['compliance_percentage']
        initial_errors = initial_validation['error_files']
        
        print(f"📊 Initial Compliance: {initial_compliance:.1f}%")
        print(f"📊 Initial Errors: {initial_errors}")
        print()
        
        if initial_compliance >= self.target_compliance:
            print("🎉 TARGET ALREADY ACHIEVED!")
            return True
        
        # Identify and categorize syntax errors
        syntax_errors = self.identify_syntax_errors()
        categories = self.categorize_errors(syntax_errors)
        
        # Apply comprehensive fixes
        total_fixes = self.apply_comprehensive_fixes(categories)
        
        # Validate fixes
        final_validation = self.validate_fixes()
        final_compliance = final_validation['compliance_percentage']
        final_errors = final_validation['error_files']
        
        # Calculate improvement
        improvement = final_compliance - initial_compliance
        gap_remaining = self.target_compliance - final_compliance
        
        print("\n📊 BEAST MODE MANUAL FIX RESULTS")
        print("=" * 40)
        print(f"📈 Initial Compliance: {initial_compliance:.1f}%")
        print(f"📈 Final Compliance: {final_compliance:.1f}%")
        print(f"📈 Improvement: +{improvement:.1f}%")
        print(f"🎯 Gap Remaining: {gap_remaining:.1f}%")
        print(f"🔧 Fixes Applied: {total_fixes}")
        print(f"📊 Final Errors: {final_errors}")
        print(f"💾 Backup Location: {backup_dir}")
        
        # Determine success
        if final_compliance >= self.target_compliance:
            success_status = "🎉 CONVERGENCE ACHIEVED!"
        elif final_compliance >= self.target_compliance - 2.0:
            success_status = "🟡 NEAR_CONVERGENCE"
        elif improvement > 5.0:
            success_status = "🟢 SIGNIFICANT_PROGRESS"
        elif improvement > 0.0:
            success_status = "🔄 PROGRESS"
        else:
            success_status = "❌ NO_PROGRESS"
        
        print(f"🎯 Success Status: {success_status}")
        
        # Save comprehensive report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'target_compliance': self.target_compliance,
            'initial_compliance': initial_compliance,
            'final_compliance': final_compliance,
            'improvement': improvement,
            'gap_remaining': gap_remaining,
            'fixes_applied': total_fixes,
            'success_status': success_status,
            'backup_location': backup_dir,
            'error_categories': {k: len(v) for k, v in categories.items() if v}
        }
        
        os.makedirs('.beast_mode', exist_ok=True)
        with open('.beast_mode/beast_mode_manual_syntax_fix_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"💾 Comprehensive report saved to .beast_mode/beast_mode_manual_syntax_fix_report.json")
        
        return final_compliance >= self.target_compliance

if __name__ == "__main__":
    fixer = BeastModeManualSyntaxFixer()
    success = fixer.run_beast_mode_manual_fixes()
    
    if success:
        print("\n🎉 BEAST MODE MANUAL SYNTAX FIXING SUCCESSFUL!")
        sys.exit(0)
    else:
        print("\n🔄 BEAST MODE MANUAL SYNTAX FIXING IN PROGRESS")
        sys.exit(1)

