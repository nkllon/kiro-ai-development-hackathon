#!/usr/bin/env python3
"""
Simple Orphaned Solution Scanner
===============================

Simplified version to test the core functionality.
"""

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def scan_for_orphaned_solutions() -> Dict[str, Any]:
    """Simple scan for orphaned solutions."""
    print("🔍 Simple Orphaned Solution Scan")
    print("=" * 40)
    
    # Find Python files with classes
    implementations = []
    source_dirs = [Path("src"), Path("scripts")]
    
    for source_dir in source_dirs:
        if not source_dir.exists():
            continue
            
        print(f"📁 Scanning {source_dir}...")
        
        for py_file in source_dir.rglob("*.py"):
            # Skip test files and __init__.py
            if "test_" in py_file.name or py_file.name == "__init__.py":
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Simple checks
                line_count = len(content.splitlines())
                if line_count < 20:  # Skip very small files
                    continue
                
                # Look for classes or many functions
                has_classes = "class " in content
                function_count = content.count("def ")
                
                if has_classes or function_count >= 3:
                    implementations.append({
                        "file": str(py_file),
                        "module": str(py_file.relative_to(Path.cwd())).replace('/', '.').replace('.py', ''),
                        "lines": line_count,
                        "has_classes": has_classes,
                        "function_count": function_count
                    })
                    print(f"  ✅ Found: {py_file} ({line_count} lines, classes: {has_classes}, functions: {function_count})")
            
            except Exception as e:
                print(f"  ❌ Error analyzing {py_file}: {e}")
    
    # Find specifications
    specs = []
    spec_dir = Path(".kiro/specs")
    
    if spec_dir.exists():
        print(f"\n📋 Scanning specifications in {spec_dir}...")
        for spec_path in spec_dir.iterdir():
            if spec_path.is_dir():
                specs.append({
                    "name": spec_path.name,
                    "path": str(spec_path),
                    "has_requirements": (spec_path / "requirements.md").exists(),
                    "has_design": (spec_path / "design.md").exists(),
                    "has_tasks": (spec_path / "tasks.md").exists()
                })
                print(f"  📋 Spec: {spec_path.name}")
    
    # Simple matching - look for implementations without obvious specs
    orphaned = []
    
    for impl in implementations:
        module_name = impl["module"]
        
        # Simple heuristic: check if any spec name is similar to module name
        has_matching_spec = False
        for spec in specs:
            spec_words = set(spec["name"].lower().replace('-', ' ').replace('_', ' ').split())
            module_words = set(module_name.lower().replace('.', ' ').replace('_', ' ').split())
            
            # If there's any word overlap, consider it matched
            if spec_words & module_words:
                has_matching_spec = True
                break
        
        if not has_matching_spec:
            orphaned.append(impl)
    
    # Generate report
    report = {
        "scan_timestamp": datetime.now().isoformat(),
        "total_implementations": len(implementations),
        "total_specifications": len(specs),
        "orphaned_solutions": len(orphaned),
        "coverage_percentage": ((len(implementations) - len(orphaned)) / max(len(implementations), 1)) * 100,
        "implementations": implementations,
        "specifications": specs,
        "orphaned": orphaned
    }
    
    return report


def main():
    """Main entry point."""
    report = scan_for_orphaned_solutions()
    
    print(f"\n📊 Results:")
    print(f"   Total Implementations: {report['total_implementations']}")
    print(f"   Total Specifications: {report['total_specifications']}")
    print(f"   Orphaned Solutions: {report['orphaned_solutions']}")
    print(f"   Coverage: {report['coverage_percentage']:.1f}%")
    
    if report['orphaned']:
        print(f"\n🚨 Orphaned Solutions Found:")
        for orphan in report['orphaned'][:10]:  # Show first 10
            print(f"   - {orphan['file']} ({orphan['lines']} lines)")
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(f"reports/simple_orphaned_scan_{timestamp}.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Report saved: {report_file}")
    
    return report


if __name__ == "__main__":
    main()