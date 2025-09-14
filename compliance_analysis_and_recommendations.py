#!/usr/bin/env python3
"""
🔍 COMPLIANCE ANALYSIS & RECOMMENDATIONS
========================================

Comprehensive analysis of current compliance state and strategic recommendations
for the next pass to achieve 100% compliance across all metrics.

Author: Beast Mode Framework
Date: 2025-09-13
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

class ComplianceAnalysisAndRecommendations:
    """Comprehensive analysis and strategic recommendations system."""
    
    def __init__(self, target_dir="src"):
        self.target_dir = target_dir
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "file_counts": {},
            "compliance_metrics": {},
            "issues": [],
            "recommendations": [],
            "next_pass_strategy": {}
        }
        
    def analyze_file_counts(self):
        """Analyze file counts and structure."""
        print("📊 Analyzing File Counts and Structure...")
        
        # Total Python files
        result = subprocess.run(['find', self.target_dir, '-name', '*.py'], 
                              capture_output=True, text=True)
        python_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        total_files = len(python_files)
        
        # Files by directory
        dir_counts = {}
        for file_path in python_files:
            if file_path:
                dir_name = os.path.dirname(file_path)
                dir_counts[dir_name] = dir_counts.get(dir_name, 0) + 1
        
        # Size analysis
        large_files = []
        for file_path in python_files:
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = len(f.readlines())
                        if line_count > 200:
                            large_files.append((file_path, line_count))
                except:
                    continue
        
        self.analysis["file_counts"] = {
            "total_python_files": total_files,
            "directory_breakdown": dict(sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "large_files_count": len(large_files),
            "large_files": large_files[:5]  # Top 5 largest
        }
        
        print(f"✅ Total Python files: {total_files}")
        print(f"✅ Large files (>200 lines): {len(large_files)}")
        
    def analyze_compliance_metrics(self):
        """Analyze current compliance metrics."""
        print("\n🔍 Analyzing Compliance Metrics...")
        
        # ReflectiveModule compliance
        result = subprocess.run(['find', self.target_dir, '-name', '*.py', '-exec', 'grep', '-l', 'ReflectiveModule', '{}', ';'], 
                              capture_output=True, text=True)
        rdi_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        rdi_count = len(rdi_files)
        
        # Health monitoring compliance
        result = subprocess.run(['find', self.target_dir, '-name', '*.py', '-exec', 'grep', '-l', 'ModuleHealth', '{}', ';'], 
                              capture_output=True, text=True)
        health_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        health_count = len(health_files)
        
        # Registry integration compliance
        result = subprocess.run(['find', self.target_dir, '-name', '*.py', '-exec', 'grep', '-l', 'register_module', '{}', ';'], 
                              capture_output=True, text=True)
        registry_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        registry_count = len(registry_files)
        
        # Size compliance
        result = subprocess.run(['find', self.target_dir, '-name', '*.py', '-exec', 'wc', '-l', '{}', '+'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            total_lines = int(result.stdout.strip().split('\n')[-1].split()[0])
        else:
            total_lines = 0
            
        # Count files over 200 lines
        large_files = []
        for file_path in self.analysis["file_counts"].get("large_files", []):
            if isinstance(file_path, tuple):
                large_files.append(file_path[0])
        
        total_files = self.analysis["file_counts"]["total_python_files"]
        
        self.analysis["compliance_metrics"] = {
            "rdi_compliance": {
                "files_with_reflective_module": rdi_count,
                "total_files": total_files,
                "percentage": (rdi_count / total_files * 100) if total_files > 0 else 0
            },
            "health_monitoring": {
                "files_with_health_monitoring": health_count,
                "total_files": total_files,
                "percentage": (health_count / total_files * 100) if total_files > 0 else 0
            },
            "registry_integration": {
                "files_with_registry_integration": registry_count,
                "total_files": total_files,
                "percentage": (registry_count / total_files * 100) if total_files > 0 else 0
            },
            "size_compliance": {
                "files_over_200_lines": len(large_files),
                "total_files": total_files,
                "percentage": ((total_files - len(large_files)) / total_files * 100) if total_files > 0 else 0
            }
        }
        
        print(f"✅ RDI Compliance: {rdi_count}/{total_files} ({self.analysis['compliance_metrics']['rdi_compliance']['percentage']:.1f}%)")
        print(f"✅ Health Monitoring: {health_count}/{total_files} ({self.analysis['compliance_metrics']['health_monitoring']['percentage']:.1f}%)")
        print(f"✅ Registry Integration: {registry_count}/{total_files} ({self.analysis['compliance_metrics']['registry_integration']['percentage']:.1f}%)")
        print(f"✅ Size Compliance: {total_files - len(large_files)}/{total_files} ({self.analysis['compliance_metrics']['size_compliance']['percentage']:.1f}%)")
        
    def identify_issues(self):
        """Identify specific compliance issues."""
        print("\n🔍 Identifying Compliance Issues...")
        
        issues = []
        
        # RDI compliance issues
        rdi_pct = self.analysis["compliance_metrics"]["rdi_compliance"]["percentage"]
        if rdi_pct < 95:
            issues.append({
                "type": "RDI Compliance",
                "severity": "HIGH",
                "description": f"Only {rdi_pct:.1f}% of files have ReflectiveModule inheritance",
                "impact": "Critical architectural compliance gap"
            })
        
        # Health monitoring issues
        health_pct = self.analysis["compliance_metrics"]["health_monitoring"]["percentage"]
        if health_pct < 95:
            issues.append({
                "type": "Health Monitoring",
                "severity": "HIGH",
                "description": f"Only {health_pct:.1f}% of files have health monitoring",
                "impact": "Monitoring and observability gaps"
            })
        
        # Registry integration issues
        registry_pct = self.analysis["compliance_metrics"]["registry_integration"]["percentage"]
        if registry_pct < 95:
            issues.append({
                "type": "Registry Integration",
                "severity": "HIGH",
                "description": f"Only {registry_pct:.1f}% of files have registry integration",
                "impact": "Service discovery and dependency management gaps"
            })
        
        # Size compliance issues
        size_pct = self.analysis["compliance_metrics"]["size_compliance"]["percentage"]
        if size_pct < 100:
            issues.append({
                "type": "Size Compliance",
                "severity": "MEDIUM",
                "description": f"Only {size_pct:.1f}% of files are under 200 lines",
                "impact": "Maintainability and readability concerns"
            })
        
        self.analysis["issues"] = issues
        
        for issue in issues:
            print(f"❌ {issue['type']}: {issue['description']}")
            
    def generate_recommendations(self):
        """Generate strategic recommendations for next pass."""
        print("\n💡 Generating Strategic Recommendations...")
        
        recommendations = []
        
        # RDI Compliance recommendations
        rdi_pct = self.analysis["compliance_metrics"]["rdi_compliance"]["percentage"]
        if rdi_pct < 95:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "RDI Compliance",
                "action": "Implement ReflectiveModule inheritance in remaining files",
                "strategy": "Create targeted ReflectiveModule deployment system",
                "estimated_effort": "High",
                "impact": "Architectural compliance"
            })
        
        # Health Monitoring recommendations
        health_pct = self.analysis["compliance_metrics"]["health_monitoring"]["percentage"]
        if health_pct < 95:
            recommendations.append({
                "priority": "HIGH",
                "category": "Health Monitoring",
                "action": "Add health monitoring to remaining files",
                "strategy": "Batch health monitoring implementation",
                "estimated_effort": "Medium",
                "impact": "Observability and monitoring"
            })
        
        # Registry Integration recommendations
        registry_pct = self.analysis["compliance_metrics"]["registry_integration"]["percentage"]
        if registry_pct < 95:
            recommendations.append({
                "priority": "HIGH",
                "category": "Registry Integration",
                "action": "Add registry integration to remaining files",
                "strategy": "Batch registry integration implementation",
                "estimated_effort": "Medium",
                "impact": "Service discovery and dependency management"
            })
        
        # Size Compliance recommendations
        size_pct = self.analysis["compliance_metrics"]["size_compliance"]["percentage"]
        if size_pct < 100:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Size Compliance",
                "action": "Refactor remaining large files",
                "strategy": "Surgical file splitting and optimization",
                "estimated_effort": "Low",
                "impact": "Maintainability"
            })
        
        # Test Suite recommendations
        recommendations.append({
            "priority": "HIGH",
            "category": "Test Suite",
            "action": "Create comprehensive test suite",
            "strategy": "Implement unit, integration, and performance tests",
            "estimated_effort": "High",
            "impact": "Quality assurance and reliability"
        })
        
        self.analysis["recommendations"] = recommendations
        
        for rec in recommendations:
            print(f"💡 {rec['priority']} - {rec['category']}: {rec['action']}")
            
    def create_next_pass_strategy(self):
        """Create strategic plan for next compliance pass."""
        print("\n🎯 Creating Next Pass Strategy...")
        
        # Prioritize by impact and effort
        critical_items = [r for r in self.analysis["recommendations"] if r["priority"] == "CRITICAL"]
        high_items = [r for r in self.analysis["recommendations"] if r["priority"] == "HIGH"]
        medium_items = [r for r in self.analysis["recommendations"] if r["priority"] == "MEDIUM"]
        
        strategy = {
            "phase_1_critical": {
                "focus": "RDI Compliance",
                "target": "Achieve 95%+ ReflectiveModule inheritance",
                "approach": "Targeted deployment system",
                "estimated_duration": "2-3 hours"
            },
            "phase_2_high_priority": {
                "focus": "Health Monitoring & Registry Integration",
                "target": "Achieve 95%+ coverage for both",
                "approach": "Parallel batch implementation",
                "estimated_duration": "1-2 hours"
            },
            "phase_3_quality": {
                "focus": "Test Suite & Size Compliance",
                "target": "100% size compliance, comprehensive tests",
                "approach": "Quality assurance and testing",
                "estimated_duration": "2-4 hours"
            },
            "phase_4_validation": {
                "focus": "Full Compliance Validation",
                "target": "100% across all metrics",
                "approach": "Comprehensive validation and reporting",
                "estimated_duration": "1 hour"
            }
        }
        
        self.analysis["next_pass_strategy"] = strategy
        
        print("✅ Phase 1 (Critical): RDI Compliance - 2-3 hours")
        print("✅ Phase 2 (High Priority): Health & Registry - 1-2 hours")
        print("✅ Phase 3 (Quality): Test Suite & Size - 2-4 hours")
        print("✅ Phase 4 (Validation): Full Compliance - 1 hour")
        
    def generate_report(self):
        """Generate comprehensive analysis report."""
        report_filename = "compliance_analysis_and_recommendations.json"
        with open(report_filename, 'w') as f:
            json.dump(self.analysis, f, indent=2)
        
        print(f"\n📄 Comprehensive analysis saved to: {report_filename}")
        
        # Generate summary
        print("\n" + "="*60)
        print("🎯 COMPLIANCE ANALYSIS SUMMARY")
        print("="*60)
        
        total_files = self.analysis["file_counts"]["total_python_files"]
        rdi_pct = self.analysis["compliance_metrics"]["rdi_compliance"]["percentage"]
        health_pct = self.analysis["compliance_metrics"]["health_monitoring"]["percentage"]
        registry_pct = self.analysis["compliance_metrics"]["registry_integration"]["percentage"]
        size_pct = self.analysis["compliance_metrics"]["size_compliance"]["percentage"]
        
        print(f"📊 Total Files: {total_files:,}")
        print(f"📊 RDI Compliance: {rdi_pct:.1f}%")
        print(f"📊 Health Monitoring: {health_pct:.1f}%")
        print(f"📊 Registry Integration: {registry_pct:.1f}%")
        print(f"📊 Size Compliance: {size_pct:.1f}%")
        
        print(f"\n❌ Issues Identified: {len(self.analysis['issues'])}")
        print(f"💡 Recommendations: {len(self.analysis['recommendations'])}")
        
        print("\n🚀 RECOMMENDED NEXT PASS:")
        print("1. Focus on RDI Compliance (Critical)")
        print("2. Implement Health Monitoring & Registry Integration (High)")
        print("3. Complete Test Suite & Size Compliance (Quality)")
        print("4. Full Validation & Reporting (Validation)")
        
    def run(self):
        """Run complete compliance analysis and recommendations."""
        print("🔍 COMPLIANCE ANALYSIS & RECOMMENDATIONS")
        print("=" * 50)
        print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target directory: {self.target_dir}")
        print()
        
        self.analyze_file_counts()
        self.analyze_compliance_metrics()
        self.identify_issues()
        self.generate_recommendations()
        self.create_next_pass_strategy()
        self.generate_report()
        
        print("\n🎉 COMPLIANCE ANALYSIS COMPLETE!")
        print("Ready for strategic next pass implementation! 💪")

if __name__ == "__main__":
    analyzer = ComplianceAnalysisAndRecommendations()
    analyzer.run()
