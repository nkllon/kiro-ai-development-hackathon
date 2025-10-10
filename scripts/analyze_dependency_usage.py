#!/usr/bin/env python3
"""
Analyze Dependency Usage

Helper script to analyze whether packages flagged by Dependabot are actually
used in the codebase. This helps determine appropriate dismissal reasons.

Usage:
    python3 scripts/analyze_dependency_usage.py <package-name>
    python3 scripts/analyze_dependency_usage.py --all

Examples:
    python3 scripts/analyze_dependency_usage.py python-jose
    python3 scripts/analyze_dependency_usage.py --all
"""

import argparse
import glob
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

class DependencyAnalyzer:
    """Analyzes dependency usage in the codebase."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.source_dirs = ["src", "scripts", "examples", "tests"]
        self.requirement_files = [
            "pyproject.toml",
            "requirements.txt", 
            "requirements-*.txt"
        ]
    
    def find_requirement_files(self) -> List[Path]:
        """Find all requirement files in the project."""
        files = []
        
        for pattern in self.requirement_files:
            matches = list(self.project_root.glob(pattern))
            files.extend(matches)
        
        return files
    
    def check_package_in_requirements(self, package_name: str) -> List[Tuple[Path, str]]:
        """Check if package is listed in any requirement files."""
        found_in = []
        requirement_files = self.find_requirement_files()
        
        for req_file in requirement_files:
            try:
                with open(req_file, 'r') as f:
                    content = f.read()
                    
                # Look for package name (case insensitive, handle various formats)
                patterns = [
                    rf'^{re.escape(package_name)}[>=<!\s]',  # Direct dependency
                    rf'^{re.escape(package_name)}$',         # Exact match
                    rf'"{re.escape(package_name)}"',         # Quoted in pyproject.toml
                    rf"'{re.escape(package_name)}'",         # Single quoted
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                    if matches:
                        found_in.append((req_file, matches[0]))
                        break
                        
            except Exception as e:
                print(f"Warning: Could not read {req_file}: {e}")
        
        return found_in
    
    def check_package_imports(self, package_name: str) -> List[Tuple[Path, int, str]]:
        """Check if package is imported in source code."""
        imports_found = []
        
        # Common import patterns
        import_patterns = [
            rf'^import {re.escape(package_name)}',
            rf'^from {re.escape(package_name)} import',
            rf'^import {re.escape(package_name)}\.', 
            rf'^from {re.escape(package_name)}\.',
        ]
        
        # Handle common package name variations
        variations = [package_name]
        if '-' in package_name:
            variations.append(package_name.replace('-', '_'))
        if '_' in package_name:
            variations.append(package_name.replace('_', '-'))
        
        for source_dir in self.source_dirs:
            source_path = self.project_root / source_dir
            if not source_path.exists():
                continue
                
            for py_file in source_path.rglob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        
                        for variation in variations:
                            for pattern in import_patterns:
                                var_pattern = pattern.replace(re.escape(package_name), re.escape(variation))
                                if re.match(var_pattern, line, re.IGNORECASE):
                                    imports_found.append((py_file, line_num, line))
                                    
                except Exception as e:
                    print(f"Warning: Could not read {py_file}: {e}")
        
        return imports_found
    
    def check_package_usage(self, package_name: str) -> List[Tuple[Path, int, str]]:
        """Check for package usage beyond imports (function calls, etc.)."""
        usage_found = []
        
        # Look for common usage patterns
        usage_patterns = [
            rf'{re.escape(package_name)}\.',  # package.function()
            rf'{re.escape(package_name)}\(',  # package()
        ]
        
        # Handle variations
        variations = [package_name]
        if '-' in package_name:
            variations.append(package_name.replace('-', '_'))
        if '_' in package_name:
            variations.append(package_name.replace('_', '-'))
        
        for source_dir in self.source_dirs:
            source_path = self.project_root / source_dir
            if not source_path.exists():
                continue
                
            for py_file in source_path.rglob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        for variation in variations:
                            for pattern in usage_patterns:
                                var_pattern = pattern.replace(re.escape(package_name), re.escape(variation))
                                if re.search(var_pattern, line, re.IGNORECASE):
                                    usage_found.append((py_file, line_num, line.strip()))
                                    
                except Exception as e:
                    print(f"Warning: Could not read {py_file}: {e}")
        
        return usage_found
    
    def analyze_package(self, package_name: str) -> Dict:
        """Complete analysis of a package's usage."""
        print(f"🔍 Analyzing package: {package_name}")
        print("=" * 50)
        
        # Check requirements
        in_requirements = self.check_package_in_requirements(package_name)
        print(f"\n📋 Found in requirement files: {len(in_requirements)}")
        for req_file, match in in_requirements:
            print(f"  {req_file}: {match}")
        
        # Check imports
        imports = self.check_package_imports(package_name)
        print(f"\n📥 Import statements found: {len(imports)}")
        for file_path, line_num, line in imports[:10]:  # Show first 10
            print(f"  {file_path}:{line_num}: {line}")
        if len(imports) > 10:
            print(f"  ... and {len(imports) - 10} more")
        
        # Check usage
        usage = self.check_package_usage(package_name)
        print(f"\n🔧 Usage patterns found: {len(usage)}")
        for file_path, line_num, line in usage[:10]:  # Show first 10
            print(f"  {file_path}:{line_num}: {line}")
        if len(usage) > 10:
            print(f"  ... and {len(usage) - 10} more")
        
        # Risk assessment
        print(f"\n🎯 Risk Assessment:")
        if not in_requirements:
            print("  ✅ NOT_USED: Package not in any requirement files")
            risk_level = "inaccurate"
        elif not imports and not usage:
            print("  ✅ NOT_USED: Package listed but never imported or used")
            risk_level = "not_used"
        elif imports or usage:
            print("  ⚠️  USED: Package is actively used in codebase")
            print("     → Requires careful analysis of vulnerability impact")
            risk_level = "needs_analysis"
        else:
            print("  ❓ UNCLEAR: Unable to determine usage")
            risk_level = "unclear"
        
        return {
            "package": package_name,
            "in_requirements": len(in_requirements) > 0,
            "requirement_files": [str(f) for f, _ in in_requirements],
            "imports_count": len(imports),
            "usage_count": len(usage),
            "risk_level": risk_level,
            "imports": [(str(f), l, line) for f, l, line in imports],
            "usage": [(str(f), l, line) for f, l, line in usage]
        }
    
    def get_all_dependencies(self) -> Set[str]:
        """Extract all package names from requirement files."""
        packages = set()
        requirement_files = self.find_requirement_files()
        
        for req_file in requirement_files:
            try:
                with open(req_file, 'r') as f:
                    content = f.read()
                
                # Extract package names from different formats
                if req_file.name == "pyproject.toml":
                    # Handle pyproject.toml format
                    matches = re.findall(r'"([a-zA-Z0-9_-]+)"', content)
                    packages.update(matches)
                else:
                    # Handle requirements.txt format
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before version specifiers)
                            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                            if match:
                                packages.add(match.group(1))
                                
            except Exception as e:
                print(f"Warning: Could not parse {req_file}: {e}")
        
        return packages

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Analyze dependency usage")
    parser.add_argument("package", nargs="?", help="Package name to analyze")
    parser.add_argument("--all", action="store_true", 
                       help="Analyze all dependencies")
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer()
    
    if args.all:
        print("🔍 Analyzing all dependencies...")
        dependencies = analyzer.get_all_dependencies()
        print(f"Found {len(dependencies)} dependencies")
        
        results = []
        for package in sorted(dependencies):
            if package:  # Skip empty strings
                result = analyzer.analyze_package(package)
                results.append(result)
                print()  # Blank line between packages
        
        # Summary
        print("\n📊 SUMMARY")
        print("=" * 50)
        not_used = [r for r in results if r['risk_level'] in ['not_used', 'inaccurate']]
        needs_analysis = [r for r in results if r['risk_level'] == 'needs_analysis']
        
        print(f"Not used: {len(not_used)} packages")
        for result in not_used:
            print(f"  {result['package']} ({result['risk_level']})")
        
        print(f"\nNeeds analysis: {len(needs_analysis)} packages")
        for result in needs_analysis:
            print(f"  {result['package']} (imports: {result['imports_count']}, usage: {result['usage_count']})")
    
    elif args.package:
        analyzer.analyze_package(args.package)
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())