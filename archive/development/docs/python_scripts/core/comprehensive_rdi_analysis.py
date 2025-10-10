#!/usr/bin/env python3
"""
Comprehensive RDI Analysis
=========================

Full RDI (Requirements-Design-Implementation) compliance analysis
of the entire repository with focus on what was touched.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

def analyze_file_rdi_compliance(file_path: str) -> Dict[str, Any]:
    """Analyze a single file for RDI compliance."""
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        line_count = len(lines)
        
        # RDI Size Compliance (200 line limit)
        size_compliant = line_count <= 200
        size_violation = max(0, line_count - 200)
        
        # Analyze structure
        class_count = 0
        function_count = 0
        import_count = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('class '):
                class_count += 1
            elif stripped.startswith('def '):
                function_count += 1
            elif stripped.startswith('import ') or stripped.startswith('from '):
                import_count += 1
            elif stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                comment_lines += 1
        
        # Calculate complexity metrics
        complexity_score = (class_count * 10) + (function_count * 2) + (line_count * 0.1)
        
        return {
            "file_path": file_path,
            "line_count": line_count,
            "size_compliant": size_compliant,
            "size_violation": size_violation,
            "class_count": class_count,
            "function_count": function_count,
            "import_count": import_count,
            "comment_lines": comment_lines,
            "complexity_score": complexity_score,
            "rdi_score": 100 if size_compliant else max(0, 100 - (size_violation * 2))
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {e}"}

def analyze_consolidated_modules() -> Dict[str, Any]:
    """Analyze the consolidated navigator modules."""
    print("🔍 ANALYZING CONSOLIDATED NAVIGATOR MODULES")
    print("=" * 50)
    
    modules = [
        "smart_devpost_navigator_v2.py",
        "src/navigator_consolidated/__init__.py",
        "src/navigator_consolidated/core_navigator.py",
        "src/navigator_consolidated/event_handler.py",
        "src/navigator_consolidated/step_detector.py",
        "src/navigator_consolidated/form_processor.py",
        "src/navigator_consolidated/interactive_mode.py"
    ]
    
    results = {}
    total_lines = 0
    compliant_files = 0
    
    for module in modules:
        analysis = analyze_file_rdi_compliance(module)
        results[module] = analysis
        
        if "error" not in analysis:
            total_lines += analysis["line_count"]
            if analysis["size_compliant"]:
                compliant_files += 1
                print(f"✅ {module}: {analysis['line_count']} lines (RDI compliant)")
            else:
                print(f"❌ {module}: {analysis['line_count']} lines (RDI violation)")
        else:
            print(f"⚠️ {module}: {analysis['error']}")
    
    return {
        "modules": results,
        "total_lines": total_lines,
        "compliant_files": compliant_files,
        "total_files": len(modules),
        "compliance_rate": (compliant_files / len(modules)) * 100
    }

def analyze_rm_ddd_patterns() -> Dict[str, Any]:
    """Analyze RM-DDD (Reflective Module - Domain Driven Design) patterns."""
    print("\n🧬 ANALYZING RM-DDD PATTERNS")
    print("=" * 35)
    
    # Check for ReflectiveModule implementations
    reflective_module_files = []
    domain_service_files = []
    bounded_context_files = []
    
    # Search for patterns
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        if 'ReflectiveModule' in content:
                            reflective_module_files.append(file_path)
                        if 'DomainService' in content:
                            domain_service_files.append(file_path)
                        if 'BoundedContext' in content:
                            bounded_context_files.append(file_path)
                            
                except Exception:
                    continue
    
    print(f"✅ ReflectiveModule implementations: {len(reflective_module_files)}")
    print(f"✅ DomainService implementations: {len(domain_service_files)}")
    print(f"✅ BoundedContext implementations: {len(bounded_context_files)}")
    
    return {
        "reflective_modules": reflective_module_files,
        "domain_services": domain_service_files,
        "bounded_contexts": bounded_context_files,
        "rm_ddd_score": min(100, (len(reflective_module_files) + len(domain_service_files) + len(bounded_context_files)) * 20)
    }

def analyze_interface_compliance() -> Dict[str, Any]:
    """Analyze interface compliance patterns."""
    print("\n🔌 ANALYZING INTERFACE COMPLIANCE")
    print("=" * 40)
    
    interface_methods = [
        'get_interface_metadata',
        'health_check',
        'register_module',
        'get_health_status',
        'graceful_degradation'
    ]
    
    compliance_results = {}
    
    for method in interface_methods:
        implementing_files = []
        
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if method in content:
                                implementing_files.append(file_path)
                    except Exception:
                        continue
        
        compliance_results[method] = {
            "implementing_files": implementing_files,
            "count": len(implementing_files)
        }
        
        print(f"✅ {method}: {len(implementing_files)} implementations")
    
    return compliance_results

def generate_rdi_report(consolidated_analysis: Dict, rm_ddd_analysis: Dict, interface_analysis: Dict) -> str:
    """Generate comprehensive RDI report."""
    report = []
    report.append("# 🚨 COMPREHENSIVE RDI ANALYSIS REPORT")
    report.append("=" * 50)
    report.append(f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Analyzer:** Beast Mode Framework")
    report.append("")
    
    # Consolidated Modules Analysis
    report.append("## 📊 CONSOLIDATED MODULES ANALYSIS")
    report.append("")
    report.append(f"**Total Files:** {consolidated_analysis['total_files']}")
    report.append(f"**Compliant Files:** {consolidated_analysis['compliant_files']}")
    report.append(f"**Compliance Rate:** {consolidated_analysis['compliance_rate']:.1f}%")
    report.append(f"**Total Lines:** {consolidated_analysis['total_lines']}")
    report.append("")
    
    # RDI Compliance Status
    if consolidated_analysis['compliance_rate'] == 100:
        report.append("✅ **RDI SIZE COMPLIANCE: PERFECT**")
    elif consolidated_analysis['compliance_rate'] >= 80:
        report.append("⚠️ **RDI SIZE COMPLIANCE: GOOD**")
    else:
        report.append("❌ **RDI SIZE COMPLIANCE: NEEDS IMPROVEMENT**")
    
    report.append("")
    
    # RM-DDD Analysis
    report.append("## 🧬 RM-DDD PATTERN ANALYSIS")
    report.append("")
    report.append(f"**ReflectiveModule Implementations:** {len(rm_ddd_analysis['reflective_modules'])}")
    report.append(f"**DomainService Implementations:** {len(rm_ddd_analysis['domain_services'])}")
    report.append(f"**BoundedContext Implementations:** {len(rm_ddd_analysis['bounded_contexts'])}")
    report.append(f"**RM-DDD Score:** {rm_ddd_analysis['rm_ddd_score']}/100")
    report.append("")
    
    # Interface Compliance
    report.append("## 🔌 INTERFACE COMPLIANCE ANALYSIS")
    report.append("")
    total_implementations = sum(method['count'] for method in interface_analysis.values())
    report.append(f"**Total Interface Implementations:** {total_implementations}")
    report.append("")
    
    for method, data in interface_analysis.items():
        report.append(f"- **{method}:** {data['count']} implementations")
    
    report.append("")
    
    # Overall Assessment
    overall_score = (consolidated_analysis['compliance_rate'] + rm_ddd_analysis['rm_ddd_score']) / 2
    report.append("## 🎯 OVERALL RDI ASSESSMENT")
    report.append("")
    report.append(f"**Overall RDI Score:** {overall_score:.1f}/100")
    report.append("")
    
    if overall_score >= 90:
        report.append("🎉 **EXCELLENT RDI COMPLIANCE**")
    elif overall_score >= 70:
        report.append("✅ **GOOD RDI COMPLIANCE**")
    elif overall_score >= 50:
        report.append("⚠️ **FAIR RDI COMPLIANCE**")
    else:
        report.append("❌ **POOR RDI COMPLIANCE**")
    
    return "\n".join(report)

def main():
    """Run comprehensive RDI analysis."""
    print("🚨 COMPREHENSIVE RDI ANALYSIS")
    print("=" * 40)
    print("Analyzing RDI and RM-DDD compliance")
    print()
    
    # Run analyses
    consolidated_analysis = analyze_consolidated_modules()
    rm_ddd_analysis = analyze_rm_ddd_patterns()
    interface_analysis = analyze_interface_compliance()
    
    # Generate report
    report = generate_rdi_report(consolidated_analysis, rm_ddd_analysis, interface_analysis)
    
    # Save report
    with open("COMPREHENSIVE_RDI_ANALYSIS_REPORT.md", "w") as f:
        f.write(report)
    
    print("\n📊 ANALYSIS COMPLETE")
    print("=" * 25)
    print(f"✅ Consolidated modules compliance: {consolidated_analysis['compliance_rate']:.1f}%")
    print(f"✅ RM-DDD pattern score: {rm_ddd_analysis['rm_ddd_score']}/100")
    print(f"✅ Total interface implementations: {sum(method['count'] for method in interface_analysis.values())}")
    print(f"✅ Report saved: COMPREHENSIVE_RDI_ANALYSIS_REPORT.md")
    
    return True

if __name__ == "__main__":
    main()


