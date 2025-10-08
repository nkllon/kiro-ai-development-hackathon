#!/usr/bin/env python3
"""
Dependency Validator for Beast Mode AI Development Framework

This script validates dependencies for security, compatibility, and licensing.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional
import importlib
from dataclasses import dataclass, asdict
import re

@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    version: str
    license: Optional[str] = None
    security_issues: List[str] = None
    outdated: bool = False
    latest_version: Optional[str] = None

class DependencyValidator:
    """Validates project dependencies."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.security_critical = {
            'cryptography', 'requests', 'pydantic', 'fastapi', 
            'uvicorn', 'redis', 'prometheus-client'
        }
        self.approved_licenses = {
            'MIT', 'BSD', 'Apache', 'Apache-2.0', 'Apache Software License',
            'BSD License', 'MIT License', 'Python Software Foundation License'
        }
        
    def get_installed_packages(self) -> Dict[str, str]:
        """Get list of installed packages with versions."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            packages = json.loads(result.stdout)
            return {pkg['name'].lower(): pkg['version'] for pkg in packages}
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"❌ Error getting installed packages: {e}")
            return {}
    
    def check_security_vulnerabilities(self, packages: Dict[str, str]) -> Dict[str, List[str]]:
        """Check for known security vulnerabilities using safety."""
        vulnerabilities = {}
        
        try:
            # Try to use safety if available
            result = subprocess.run(
                [sys.executable, '-m', 'safety', 'check', '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # No vulnerabilities found
                print("✅ No known security vulnerabilities found")
                return {}
            else:
                # Parse safety output
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        pkg_name = vuln.get('package', '').lower()
                        vuln_id = vuln.get('id', 'unknown')
                        description = vuln.get('advisory', 'No description')
                        
                        if pkg_name not in vulnerabilities:
                            vulnerabilities[pkg_name] = []
                        vulnerabilities[pkg_name].append(f"{vuln_id}: {description}")
                        
                except json.JSONDecodeError:
                    print("⚠️  Could not parse safety output")
                    
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print("⚠️  Safety check not available (install with: pip install safety)")
            
            # Fallback: check for known problematic packages
            known_issues = {
                'pillow': ['CVE-2023-50447: Arbitrary code execution via crafted image'],
                'requests': ['CVE-2023-32681: Proxy-Authorization header leak'],
                'cryptography': ['Various timing attack vulnerabilities in older versions']
            }
            
            for pkg, issues in known_issues.items():
                if pkg in packages:
                    vulnerabilities[pkg] = issues
        
        return vulnerabilities
    
    def check_outdated_packages(self, packages: Dict[str, str]) -> Dict[str, str]:
        """Check for outdated packages."""
        outdated = {}
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            outdated_packages = json.loads(result.stdout)
            for pkg in outdated_packages:
                name = pkg['name'].lower()
                latest = pkg['latest_version']
                outdated[name] = latest
                
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired):
            print("⚠️  Could not check for outdated packages")
        
        return outdated
    
    def get_package_licenses(self, packages: Dict[str, str]) -> Dict[str, str]:
        """Get license information for packages."""
        licenses = {}
        
        try:
            # Try using pip-licenses if available
            result = subprocess.run(
                [sys.executable, '-m', 'pip_licenses', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                license_data = json.loads(result.stdout)
                for pkg in license_data:
                    name = pkg.get('Name', '').lower()
                    license_name = pkg.get('License', 'Unknown')
                    licenses[name] = license_name
            else:
                print("⚠️  pip-licenses not available (install with: pip install pip-licenses)")
                
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback: try to get license from package metadata
            for pkg_name in packages:
                try:
                    module = importlib.import_module(pkg_name.replace('-', '_'))
                    license_info = getattr(module, '__license__', 'Unknown')
                    licenses[pkg_name] = license_info
                except (ImportError, AttributeError):
                    licenses[pkg_name] = 'Unknown'
        
        return licenses
    
    def validate_requirements_files(self) -> Dict[str, List[str]]:
        """Validate requirements files for consistency."""
        issues = {}
        
        req_files = [
            'requirements.txt',
            'requirements-dev.txt',
            'requirements-docs.txt'
        ]
        
        all_requirements = {}
        
        for req_file in req_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        content = f.read()
                    
                    # Parse requirements
                    file_reqs = self._parse_requirements(content)
                    all_requirements[req_file] = file_reqs
                    
                    # Check for issues in this file
                    file_issues = []
                    
                    # Check for unpinned versions
                    for req in file_reqs:
                        if not any(op in req for op in ['==', '>=', '>', '<', '<=', '~=']):
                            file_issues.append(f"Unpinned version: {req}")
                    
                    # Check for security-critical packages
                    for req in file_reqs:
                        pkg_name = re.split(r'[><=!~]', req)[0].strip()
                        if pkg_name.lower() in self.security_critical:
                            if '==' not in req:
                                file_issues.append(f"Security-critical package not pinned: {req}")
                    
                    if file_issues:
                        issues[req_file] = file_issues
                        
                except Exception as e:
                    issues[req_file] = [f"Error reading file: {str(e)}"]
        
        # Check for duplicates across files
        all_packages = set()
        duplicates = set()
        
        for file_reqs in all_requirements.values():
            for req in file_reqs:
                pkg_name = re.split(r'[><=!~]', req)[0].strip().lower()
                if pkg_name in all_packages:
                    duplicates.add(pkg_name)
                all_packages.add(pkg_name)
        
        if duplicates:
            issues['duplicates'] = [f"Duplicate packages: {', '.join(duplicates)}"]
        
        return issues
    
    def _parse_requirements(self, content: str) -> List[str]:
        """Parse requirements from file content."""
        requirements = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments, empty lines, and -r includes
            if not line or line.startswith('#') or line.startswith('-r'):
                continue
            
            # Handle inline comments
            if '#' in line:
                line = line.split('#')[0].strip()
            
            if line:
                requirements.append(line)
        
        return requirements
    
    def check_license_compatibility(self, licenses: Dict[str, str]) -> Dict[str, str]:
        """Check license compatibility."""
        incompatible = {}
        
        for pkg, license_name in licenses.items():
            if license_name == 'Unknown':
                incompatible[pkg] = "License unknown - requires manual review"
            elif not any(approved in license_name for approved in self.approved_licenses):
                # Check for problematic licenses
                problematic = ['GPL', 'AGPL', 'LGPL', 'Copyleft']
                if any(prob in license_name.upper() for prob in problematic):
                    incompatible[pkg] = f"Potentially incompatible license: {license_name}"
        
        return incompatible
    
    def generate_dependency_report(self) -> Dict:
        """Generate comprehensive dependency report."""
        print("🔍 Analyzing dependencies...")
        
        # Get installed packages
        packages = self.get_installed_packages()
        if not packages:
            return {"error": "Could not retrieve installed packages"}
        
        print(f"📦 Found {len(packages)} installed packages")
        
        # Run various checks
        print("🔒 Checking security vulnerabilities...")
        vulnerabilities = self.check_security_vulnerabilities(packages)
        
        print("📅 Checking for outdated packages...")
        outdated = self.check_outdated_packages(packages)
        
        print("📄 Checking licenses...")
        licenses = self.get_package_licenses(packages)
        
        print("📋 Validating requirements files...")
        req_issues = self.validate_requirements_files()
        
        print("⚖️  Checking license compatibility...")
        license_issues = self.check_license_compatibility(licenses)
        
        # Generate summary
        report = {
            "summary": {
                "total_packages": len(packages),
                "security_issues": len(vulnerabilities),
                "outdated_packages": len(outdated),
                "license_issues": len(license_issues),
                "requirements_issues": sum(len(issues) for issues in req_issues.values())
            },
            "security": {
                "vulnerabilities": vulnerabilities,
                "critical_packages_status": self._check_critical_packages(packages, vulnerabilities)
            },
            "maintenance": {
                "outdated_packages": outdated,
                "update_priority": self._prioritize_updates(outdated, vulnerabilities)
            },
            "licensing": {
                "licenses": licenses,
                "compatibility_issues": license_issues,
                "approved_licenses": list(self.approved_licenses)
            },
            "requirements": {
                "file_issues": req_issues,
                "recommendations": self._generate_requirements_recommendations(req_issues)
            },
            "packages": packages
        }
        
        return report
    
    def _check_critical_packages(self, packages: Dict[str, str], vulnerabilities: Dict[str, List[str]]) -> Dict[str, str]:
        """Check status of security-critical packages."""
        status = {}
        
        for pkg in self.security_critical:
            if pkg in packages:
                if pkg in vulnerabilities:
                    status[pkg] = f"VULNERABLE - {packages[pkg]}"
                else:
                    status[pkg] = f"OK - {packages[pkg]}"
            else:
                status[pkg] = "NOT_INSTALLED"
        
        return status
    
    def _prioritize_updates(self, outdated: Dict[str, str], vulnerabilities: Dict[str, List[str]]) -> List[Dict]:
        """Prioritize package updates."""
        priority_updates = []
        
        # High priority: security-critical packages with vulnerabilities
        for pkg in self.security_critical:
            if pkg in vulnerabilities and pkg in outdated:
                priority_updates.append({
                    "package": pkg,
                    "priority": "HIGH",
                    "reason": "Security-critical with known vulnerabilities",
                    "latest_version": outdated[pkg]
                })
        
        # Medium priority: security-critical packages that are outdated
        for pkg in self.security_critical:
            if pkg in outdated and pkg not in vulnerabilities:
                priority_updates.append({
                    "package": pkg,
                    "priority": "MEDIUM",
                    "reason": "Security-critical package outdated",
                    "latest_version": outdated[pkg]
                })
        
        # Low priority: other packages with vulnerabilities
        for pkg in vulnerabilities:
            if pkg not in self.security_critical and pkg in outdated:
                priority_updates.append({
                    "package": pkg,
                    "priority": "MEDIUM",
                    "reason": "Has known vulnerabilities",
                    "latest_version": outdated[pkg]
                })
        
        return priority_updates
    
    def _generate_requirements_recommendations(self, issues: Dict[str, List[str]]) -> List[str]:
        """Generate recommendations for requirements files."""
        recommendations = []
        
        if issues:
            recommendations.append("Pin all security-critical packages to specific versions")
            recommendations.append("Use version ranges (>=) for non-critical packages")
            recommendations.append("Regularly update and test dependency versions")
            recommendations.append("Consider using dependabot for automated updates")
        
        return recommendations
    
    def print_report(self, report: Dict):
        """Print dependency report."""
        print("\n" + "="*60)
        print("📊 DEPENDENCY VALIDATION REPORT")
        print("="*60)
        
        summary = report["summary"]
        print(f"\n📦 Total Packages: {summary['total_packages']}")
        print(f"🔒 Security Issues: {summary['security_issues']}")
        print(f"📅 Outdated Packages: {summary['outdated_packages']}")
        print(f"⚖️  License Issues: {summary['license_issues']}")
        print(f"📋 Requirements Issues: {summary['requirements_issues']}")
        
        # Security section
        if report["security"]["vulnerabilities"]:
            print("\n🚨 SECURITY VULNERABILITIES:")
            for pkg, issues in report["security"]["vulnerabilities"].items():
                print(f"  ❌ {pkg}:")
                for issue in issues:
                    print(f"    • {issue}")
        
        # Critical packages status
        print("\n🔒 SECURITY-CRITICAL PACKAGES:")
        for pkg, status in report["security"]["critical_packages_status"].items():
            emoji = "✅" if "OK" in status else "❌" if "VULNERABLE" in status else "⚠️"
            print(f"  {emoji} {pkg}: {status}")
        
        # Update priorities
        if report["maintenance"]["update_priority"]:
            print("\n📅 PRIORITY UPDATES:")
            for update in report["maintenance"]["update_priority"]:
                priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                emoji = priority_emoji.get(update["priority"], "⚪")
                print(f"  {emoji} {update['package']} -> {update['latest_version']}")
                print(f"    Reason: {update['reason']}")
        
        # License issues
        if report["licensing"]["compatibility_issues"]:
            print("\n⚖️  LICENSE COMPATIBILITY ISSUES:")
            for pkg, issue in report["licensing"]["compatibility_issues"].items():
                print(f"  ⚠️  {pkg}: {issue}")
        
        # Requirements issues
        if report["requirements"]["file_issues"]:
            print("\n📋 REQUIREMENTS FILE ISSUES:")
            for file, issues in report["requirements"]["file_issues"].items():
                print(f"  📄 {file}:")
                for issue in issues:
                    print(f"    • {issue}")
        
        print("\n" + "="*60)
    
    def save_report(self, report: Dict, filename: str = "dependency_validation_report.json"):
        """Save report to file."""
        report_path = self.project_root / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {report_path}")
        return report_path

def main():
    """Main validation process."""
    validator = DependencyValidator()
    
    # Handle command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Beast Mode AI Development Framework - Dependency Validator")
        print("\nUsage: python scripts/dependency_validator.py [OPTIONS]")
        print("\nOptions:")
        print("  --help, -h     Show this help message")
        print("  --report       Save detailed report to file")
        print("  --security     Focus on security checks only")
        return
    
    # Generate report
    report = validator.generate_dependency_report()
    
    if "error" in report:
        print(f"❌ {report['error']}")
        sys.exit(1)
    
    # Print report
    validator.print_report(report)
    
    # Save report if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        validator.save_report(report)
    
    # Exit with appropriate code
    if report["summary"]["security_issues"] > 0:
        print("\n🚨 Security issues found - please address before deployment")
        sys.exit(1)
    elif report["summary"]["license_issues"] > 0:
        print("\n⚠️  License compatibility issues found - please review")
        sys.exit(2)
    else:
        print("\n✅ All dependency checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()