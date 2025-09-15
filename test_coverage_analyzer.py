#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TEST COVERAGE ANALYZER
=======================================
Analyzes test coverage across the entire repository and provides
detailed recommendations for improving test coverage.
Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test Coverage Analysis and Recommendations
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List


class TestCoverageAnalyzer:
    """Comprehensive test coverage analyzer for the repository."""

    def __init__(self):
        self.analysis_start = datetime.now()
        self.repository_root = Path.cwd()
        self.src_dir = self.repository_root / "src"
        self.tests_dir = self.repository_root / "tests"
        self.coverage_data = {
            "timestamp": self.analysis_start.isoformat(),
            "repository_path": str(self.repository_root),
            "analysis_summary": {},
            "test_structure": {},
            "source_structure": {},
            "coverage_metrics": {},
            "gaps_analysis": {},
            "recommendations": [],
            "action_plan": [],
        }

    def analyze_test_structure(self):
        """Analyze the structure of test files."""
        print("🔍 Analyzing test structure...")
        test_files = []
        test_directories = []
        # Find all test files
        for pattern in ["**/test*.py", "**/*_test.py"]:
            files = list(self.tests_dir.glob(pattern))
            test_files.extend([str(f.relative_to(self.repository_root)) for f in files])
        # Find test directories
        for test_dir in self.tests_dir.rglob("*"):
            if test_dir.is_dir() and test_dir.name.startswith("test"):
                test_directories.append(str(test_dir.relative_to(self.repository_root)))
        # Categorize tests
        test_categories = {
            "unit": [],
            "integration": [],
            "performance": [],
            "end_to_end": [],
            "other": [],
        }
        for test_file in test_files:
            if "/unit/" in test_file:
                test_categories["unit"].append(test_file)
            elif "/integration/" in test_file:
                test_categories["integration"].append(test_file)
            elif "/performance/" in test_file:
                test_categories["performance"].append(test_file)
            elif "e2e" in test_file.lower() or "end_to_end" in test_file:
                test_categories["end_to_end"].append(test_file)
            else:
                test_categories["other"].append(test_file)
        self.coverage_data["test_structure"] = {
            "total_test_files": len(test_files),
            "test_directories": test_directories,
            "test_files": test_files,
            "test_categories": test_categories,
            "test_file_patterns": {
                "test_*.py": len([f for f in test_files if f.endswith("/test_*.py")]),
                "*_test.py": len([f for f in test_files if f.endswith("_test.py")]),
                "other": len(
                    [
                        f
                        for f in test_files
                        if not (f.endswith("/test_*.py") or f.endswith("_test.py"))
                    ]
                ),
            },
        }
        print(
            "📊 Found {len(test_files)} test files across {len(test_directories)} test directories"
        )

    def analyze_source_structure(self):
        """Analyze the structure of source files."""
        print("🔍 Analyzing source structure...")
        source_files = []
        source_directories = []
        # Find all Python source files
        for py_file in self.src_dir.rglob("*.py"):
            source_files.append(str(py_file.relative_to(self.repository_root)))
        # Find source directories
        for src_dir in self.src_dir.rglob("*"):
            if src_dir.is_dir() and not src_dir.name.startswith("__pycache__"):
                source_directories.append(
                    str(src_dir.relative_to(self.repository_root))
                )
        # Categorize source files by domain
        domain_categories = {
            "beast_mode": [],
            "rm_ddd": [],
            "devpost_integration": [],
            "competitive_launch": [],
            "gitkraken_integration": [],
            "hackathon_demo": [],
            "other": [],
        }
        for source_file in source_files:
            if "beast_mode" in source_file:
                domain_categories["beast_mode"].append(source_file)
            elif "rm_ddd" in source_file:
                domain_categories["rm_ddd"].append(source_file)
            elif "devpost_integration" in source_file:
                domain_categories["devpost_integration"].append(source_file)
            elif "competitive_launch" in source_file:
                domain_categories["competitive_launch"].append(source_file)
            elif "gitkraken_integration" in source_file:
                domain_categories["gitkraken_integration"].append(source_file)
            elif "hackathon_demo" in source_file:
                domain_categories["hackathon_demo"].append(source_file)
            else:
                domain_categories["other"].append(source_file)
        self.coverage_data["source_structure"] = {
            "total_source_files": len(source_files),
            "source_directories": source_directories,
            "source_files": source_files,
            "domain_categories": domain_categories,
            "file_size_distribution": self._analyze_file_sizes(source_files),
        }
        print(
            "📊 Found {len(source_files)} source files across {len(source_directories)} directories"
        )

    def _analyze_file_sizes(self, files: List[str]) -> Dict[str, int]:
        """Analyze file size distribution."""
        size_distribution = {
            "small (<100 lines)": 0,
            "medium (100-500 lines)": 0,
            "large (500-1000 lines)": 0,
            "very_large (>1000 lines)": 0,
        }
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = len(f.readlines())
                if lines < 100:
                    size_distribution["small (<100 lines)"] += 1
                elif lines < 500:
                    size_distribution["medium (100-500 lines)"] += 1
                elif lines < 1000:
                    size_distribution["large (500-1000 lines)"] += 1
                else:
                    size_distribution["very_large (>1000 lines)"] += 1
            except Exception:
                continue
        return size_distribution

    def analyze_coverage_gaps(self):
        """Analyze coverage gaps between source and test files."""
        print("🔍 Analyzing coverage gaps...")
        source_files = self.coverage_data["source_structure"]["source_files"]
        test_files = self.coverage_data["test_structure"]["test_files"]
        # Map source files to potential test files
        coverage_mapping = {}
        uncovered_files = []
        for source_file in source_files:
            # Extract module name from source file
            module_name = (
                source_file.replace("src/", "").replace(".py", "").replace("/", ".")
            )
            # Look for corresponding test file
            potential_test_files = []
            for test_file in test_files:
                if module_name.split(".")[-1] in test_file or any(
                    part in test_file for part in module_name.split(".")[-2:]
                ):
                    potential_test_files.append(test_file)
            coverage_mapping[source_file] = {
                "module_name": module_name,
                "potential_test_files": potential_test_files,
                "has_direct_test": len(potential_test_files) > 0,
                "test_coverage_type": self._determine_coverage_type(
                    potential_test_files
                ),
            }
            if not potential_test_files:
                uncovered_files.append(source_file)
        # Analyze coverage by domain
        domain_coverage = {}
        for domain, files in self.coverage_data["source_structure"][
            "domain_categories"
        ].items():
            covered = sum(1 for f in files if coverage_mapping[f]["has_direct_test"])
            total = len(files)
            domain_coverage[domain] = {
                "total_files": total,
                "covered_files": covered,
                "coverage_percentage": (covered / total * 100) if total > 0 else 0,
                "uncovered_files": [
                    f for f in files if not coverage_mapping[f]["has_direct_test"]
                ],
            }
        self.coverage_data["gaps_analysis"] = {
            "coverage_mapping": coverage_mapping,
            "uncovered_files": uncovered_files,
            "domain_coverage": domain_coverage,
            "overall_coverage_percentage": len(
                [f for f in source_files if coverage_mapping[f]["has_direct_test"]]
            )
            / len(source_files)
            * 100,
            "critical_gaps": self._identify_critical_gaps(uncovered_files),
        }
        print(
            "📊 Overall coverage: {self.coverage_data['gaps_analysis']['overall_coverage_percentage']:.1f}%"
        )

    def _determine_coverage_type(self, test_files: List[str]) -> str:
        """Determine the type of test coverage for a source file."""
        if not test_files:
            return "none"
        has_unit = any("unit" in tf for tf in test_files)
        has_integration = any("integration" in tf for tf in test_files)
        has_performance = any("performance" in tf for tf in test_files)
        if has_unit and has_integration:
            return "comprehensive"
        elif has_unit:
            return "unit_only"
        elif has_integration:
            return "integration_only"
        elif has_performance:
            return "performance_only"
        else:
            return "other"

    def _identify_critical_gaps(self, uncovered_files: List[str]) -> List[str]:
        """Identify critical files that need test coverage."""
        critical_patterns = [
            "core",
            "main",
            "cli",
            "api",
            "service",
            "manager",
            "controller",
            "engine",
            "handler",
            "processor",
            "validator",
            "monitor",
        ]
        critical_gaps = []
        for file_path in uncovered_files:
            filename = Path(file_path).name.lower()
            if any(pattern in filename for pattern in critical_patterns):
                critical_gaps.append(file_path)
        return critical_gaps

    def generate_recommendations(self):
        """Generate comprehensive recommendations for improving test coverage."""
        print("🎯 Generating recommendations...")
        recommendations = []
        # Overall coverage recommendations
        overall_coverage = self.coverage_data["gaps_analysis"][
            "overall_coverage_percentage"
        ]
        if overall_coverage < 50:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Overall Coverage",
                    "title": "Achieve Basic Test Coverage",
                    "description": "Current coverage is {overall_coverage:.1f}%. Aim for at least 70% coverage.",
                    "action": "Implement unit tests for all core modules",
                    "impact": "Critical for code quality and maintainability",
                }
            )
        elif overall_coverage < 70:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Overall Coverage",
                    "title": "Improve Test Coverage",
                    "description": "Current coverage is {overall_coverage:.1f}%. Target 80%+ coverage.",
                    "action": "Add integration tests and improve unit test coverage",
                    "impact": "Enhanced reliability and confidence in deployments",
                }
            )
        # Domain-specific recommendations
        for domain, coverage_data in self.coverage_data["gaps_analysis"][
            "domain_coverage"
        ].items():
            if coverage_data["coverage_percentage"] < 60:
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "category": "Domain Coverage - {domain}",
                        "title": "Improve {domain} Test Coverage",
                        "description": "Only {coverage_data['coverage_percentage']:.1f}% of {domain} files have tests.",
                        "action": "Create test files for {len(coverage_data['uncovered_files'])} uncovered files",
                        "impact": "Critical for {domain} module reliability",
                    }
                )
        # Critical gaps recommendations
        critical_gaps = self.coverage_data["gaps_analysis"]["critical_gaps"]
        if critical_gaps:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "category": "Critical Gaps",
                    "title": "Address Critical Test Gaps",
                    "description": "Found {len(critical_gaps)} critical files without tests.",
                    "action": "Implement tests for: {', '.join(critical_gaps[:5])}{'...' if len(critical_gaps) > 5 else ''}",
                    "impact": "Essential for system stability",
                }
            )
        # Test structure recommendations
        test_categories = self.coverage_data["test_structure"]["test_categories"]
        if len(test_categories["integration"]) < len(test_categories["unit"]) * 0.3:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Test Structure",
                    "title": "Increase Integration Test Coverage",
                    "description": "Only {len(test_categories['integration'])} integration tests vs {len(test_categories['unit'])} unit tests.",
                    "action": "Add integration tests for module interactions",
                    "impact": "Better end-to-end validation",
                }
            )
        # File size recommendations
        size_dist = self.coverage_data["source_structure"]["file_size_distribution"]
        large_files = (
            size_dist["large (500-1000 lines)"] + size_dist["very_large (>1000 lines)"]
        )
        if large_files > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Code Quality",
                    "title": "Test Large Files",
                    "description": "Found {large_files} large files that may need comprehensive testing.",
                    "action": "Break down large files or add extensive test coverage",
                    "impact": "Improved maintainability and reliability",
                }
            )
        self.coverage_data["recommendations"] = recommendations
        print("📋 Generated {len(recommendations)} recommendations")

    def generate_action_plan(self):
        """Generate a prioritized action plan for improving test coverage."""
        print("📋 Generating action plan...")
        action_plan = []
        # Sort recommendations by priority
        priority_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        sorted_recommendations = sorted(
            self.coverage_data["recommendations"],
            key=lambda x: priority_order.get(x["priority"], 5),
        )
        # Phase 1: Critical and High Priority
        phase1 = [
            rec
            for rec in sorted_recommendations
            if rec["priority"] in ["CRITICAL", "HIGH"]
        ]
        if phase1:
            action_plan.append(
                {
                    "phase": 1,
                    "name": "Critical Foundation",
                    "duration": "2-3 weeks",
                    "items": phase1,
                    "expected_coverage_improvement": "20-30%",
                }
            )
        # Phase 2: Medium Priority
        phase2 = [rec for rec in sorted_recommendations if rec["priority"] == "MEDIUM"]
        if phase2:
            action_plan.append(
                {
                    "phase": 2,
                    "name": "Quality Enhancement",
                    "duration": "3-4 weeks",
                    "items": phase2,
                    "expected_coverage_improvement": "15-25%",
                }
            )
        # Phase 3: Ongoing Maintenance
        action_plan.append(
            {
                "phase": 3,
                "name": "Continuous Improvement",
                "duration": "Ongoing",
                "items": [
                    {
                        "priority": "LOW",
                        "category": "Maintenance",
                        "title": "Maintain Test Coverage",
                        "description": "Keep test coverage above 80% as new features are added.",
                        "action": "Implement coverage gates in CI/CD pipeline",
                        "impact": "Sustained code quality",
                    }
                ],
                "expected_coverage_improvement": "5-10%",
            }
        )
        self.coverage_data["action_plan"] = action_plan
        print("📋 Generated {len(action_plan)}-phase action plan")

    def generate_summary(self):
        """Generate analysis summary."""
        print("📊 Generating summary...")
        self.coverage_data["analysis_summary"] = {
            "total_source_files": self.coverage_data["source_structure"][
                "total_source_files"
            ],
            "total_test_files": self.coverage_data["test_structure"][
                "total_test_files"
            ],
            "overall_coverage_percentage": self.coverage_data["gaps_analysis"][
                "overall_coverage_percentage"
            ],
            "critical_gaps_count": len(
                self.coverage_data["gaps_analysis"]["critical_gaps"]
            ),
            "recommendations_count": len(self.coverage_data["recommendations"]),
            "analysis_duration": (datetime.now() - self.analysis_start).total_seconds(),
            "top_domains": sorted(
                self.coverage_data["gaps_analysis"]["domain_coverage"].items(),
                key=lambda x: x[1]["total_files"],
                reverse=True,
            )[:5],
        }

    def run_analysis(self):
        """Run the complete coverage analysis."""
        print("🧪 COMPREHENSIVE TEST COVERAGE ANALYSIS")
        print("=" * 60)
        print(
            "Analysis started at: {self.analysis_start.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print()
        self.analyze_test_structure()
        self.analyze_source_structure()
        self.analyze_coverage_gaps()
        self.generate_recommendations()
        self.generate_action_plan()
        self.generate_summary()
        # Save results
        report_file = "test_coverage_analysis_report.json"
        with open(report_file, "w") as f:
            json.dump(self.coverage_data, f, indent=2)
        print("\n📄 Analysis report saved to: {report_file}")
        # Print summary
        self.print_summary()
        return self.coverage_data

    def print_summary(self):
        """Print analysis summary."""
        summary = self.coverage_data["analysis_summary"]
        print("\n" + "=" * 80)
        print("🧪 TEST COVERAGE ANALYSIS SUMMARY")
        print("=" * 80)
        print("📊 Source Files: {summary['total_source_files']}")
        print("📊 Test Files: {summary['total_test_files']}")
        print("📊 Overall Coverage: {summary['overall_coverage_percentage']:.1f}%")
        print("📊 Critical Gaps: {summary['critical_gaps_count']}")
        print("📊 Recommendations: {summary['recommendations_count']}")
        print("⏱️ Analysis Duration: {summary['analysis_duration']:.1f} seconds")
        print("\n📈 TOP DOMAINS BY FILE COUNT:")
        for domain, data in summary["top_domains"]:
            print(
                "   {domain}: {data['total_files']} files ({data['coverage_percentage']:.1f}% covered)"
            )
        print("\n🎯 RECOMMENDATIONS BY PRIORITY:")
        for rec in self.coverage_data["recommendations"]:
            print("   {rec['priority']}: {rec['title']}")
        print("\n📋 ACTION PLAN:")
        for phase in self.coverage_data["action_plan"]:
            print("   Phase {phase['phase']}: {phase['name']} ({phase['duration']})")


if __name__ == "__main__":
    analyzer = TestCoverageAnalyzer()
    results = analyzer.run_analysis()
