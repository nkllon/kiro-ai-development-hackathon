#!/usr/bin/env python3
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
