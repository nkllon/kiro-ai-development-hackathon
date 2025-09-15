#!/usr/bin/env python3
"""
🚀 BEAST MODE REQUIREMENTS FIDELITY TESTER
=========================================
Test each fix to ensure requirements fidelity and compliance.
"""

import os
import sys
import json
import ast
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class BeastModeRequirementsFidelityTester:
    """Requirements fidelity testing framework"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results = []
        self.fidelity_scores = {}
        self.requirements_registry = {}

    def run_requirements_fidelity_tests(self):
        """Run comprehensive requirements fidelity tests"""
        print("🚀 BEAST MODE REQUIREMENTS FIDELITY TESTER")
        print("=" * 60)
        print("🧪 Testing each fix to ensure requirements fidelity")
        print("📊 Validating compliance with original requirements")
        print()

        # Phase 1: Load Requirements Registry
        print("📋 PHASE 1: LOADING REQUIREMENTS REGISTRY")
        print("=" * 50)

        requirements = self.load_requirements_registry()

        # Phase 2: Identify Reimplemented Files
        print("\n🔍 PHASE 2: IDENTIFYING REIMPLEMENTED FILES")
        print("=" * 50)

        reimplemented_files = self.identify_reimplemented_files()

        # Phase 3: Test Each File for Requirements Fidelity
        print("\n🧪 PHASE 3: TESTING REQUIREMENTS FIDELITY")
        print("=" * 50)

        fidelity_results = self.test_requirements_fidelity(
            reimplemented_files, requirements
        )

        # Phase 4: Generate Fidelity Report
        print("\n📊 PHASE 4: GENERATING FIDELITY REPORT")
        print("=" * 50)

        report = self.generate_fidelity_report(fidelity_results, requirements)

        return True

    def load_requirements_registry(self):
        """Load requirements registry from previous analysis"""
        print("📋 Loading requirements registry...")

        # Define core requirements based on our analysis
        requirements = {
            "interface_registry": {
                "requirements": [
                    "Manage interface metadata with proper typing",
                    "Provide registration methods for interfaces",
                    "Support interface discovery and validation",
                    "Maintain interface compliance tracking",
                    "Serialize registry data to JSON",
                    "Support interface status management",
                ],
                "required_methods": [
                    "register",
                    "get_metadata",
                    "validate_interface",
                    "list_interfaces",
                    "save_registry",
                ],
                "required_classes": ["InterfaceRegistry", "InterfaceMetadata"],
                "required_enums": ["InterfaceType", "InterfaceStatus"],
            },
            "reflective_module": {
                "requirements": [
                    "Support introspection and self-awareness",
                    "Register with interface registry automatically",
                    "Provide method signature extraction",
                    "Support domain vocabulary indexing",
                    "Enable runtime type checking",
                    "Support abstract base class pattern",
                ],
                "required_methods": [
                    "introspect",
                    "register_interface",
                    "get_methods",
                    "extract_signatures",
                ],
                "required_classes": [
                    "ReflectiveModule",
                    "DomainService",
                    "InfrastructureService",
                ],
                "required_imports": ["inspect", "abc", "typing"],
            },
            "compliance_system": {
                "requirements": [
                    "Validate interface compliance standards",
                    "Track compliance metrics and scores",
                    "Provide compliance reporting",
                    "Support automated compliance checks",
                    "Categorize compliance levels",
                    "Generate actionable recommendations",
                ],
                "required_methods": [
                    "validate_compliance",
                    "get_compliance_score",
                    "generate_report",
                    "check_standards",
                ],
                "required_classes": ["ComplianceSystem", "ComplianceResult"],
                "required_enums": ["ComplianceLevel"],
            },
            "validation_framework": {
                "requirements": [
                    "Validate input and output data",
                    "Support type checking and validation",
                    "Provide error reporting and handling",
                    "Support custom validation rules",
                    "Maintain validation history",
                    "Enable rule-based validation",
                ],
                "required_methods": [
                    "validate",
                    "check_type",
                    "report_error",
                    "add_rule",
                ],
                "required_classes": [
                    "ValidationFramework",
                    "ValidationRule",
                    "ValidationError",
                ],
                "required_features": [
                    "rule_management",
                    "error_handling",
                    "type_checking",
                ],
            },
            "enhanced_interface_registry": {
                "requirements": [
                    "Extend basic interface registry functionality",
                    "Provide interface usage metrics and tracking",
                    "Support interface performance monitoring",
                    "Enable interface caching and optimization",
                    "Generate interface recommendations",
                    "Support enhanced interface discovery",
                ],
                "required_methods": [
                    "track_interface_usage",
                    "get_interface_performance_report",
                    "optimize_interface_cache",
                    "get_interface_recommendations",
                ],
                "required_classes": ["EnhancedInterfaceRegistry", "InterfaceMetrics"],
                "required_enums": ["InterfaceType", "InterfaceStatus"],
            },
            "proactive_interface_registry": {
                "requirements": [
                    "Provide proactive interface monitoring",
                    "Support interface health checking",
                    "Implement duplicate prevention rules",
                    "Enable proactive interface validation",
                    "Generate interface health reports",
                    "Support preventive interface management",
                ],
                "required_methods": [
                    "run_interface_health_check",
                    "check_duplicate_prevention_rules",
                    "get_interface_health_report",
                    "run_proactive_monitoring",
                ],
                "required_classes": [
                    "ProactiveInterfaceRegistry",
                    "InterfaceHealthCheck",
                    "DuplicatePreventionRule",
                ],
                "required_enums": ["InterfaceType", "InterfaceStatus"],
            },
        }

        print(f"      📊 Requirements loaded:")
        print(
            f"         • Interface Registry: {len(requirements['interface_registry']['requirements'])} requirements"
        )
        print(
            f"         • Reflective Module: {len(requirements['reflective_module']['requirements'])} requirements"
        )
        print(
            f"         • Compliance System: {len(requirements['compliance_system']['requirements'])} requirements"
        )
        print(
            f"         • Validation Framework: {len(requirements['validation_framework']['requirements'])} requirements"
        )

        self.requirements_registry = requirements
        return requirements

    def identify_reimplemented_files(self):
        """Identify files that were reimplemented"""
        print("🔍 Identifying reimplemented files...")

        reimplemented_files = []

        # Check for files that were recently modified (reimplemented)
        for py_file in self.project_root.rglob("src/**/*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if file contains our reimplementation markers
                if (
                    "Requirements-Driven Implementation" in content
                    and "Generated from requirements" in content
                ):

                    # Determine component type
                    component_type = self.determine_component_type(str(py_file))

                    reimplemented_files.append(
                        {
                            "path": str(py_file),
                            "relative_path": str(
                                py_file.relative_to(self.project_root)
                            ),
                            "component_type": component_type,
                            "size": len(content),
                            "content": content,
                        }
                    )

            except Exception as e:
                print(f"      ⚠️  Error reading {py_file}: {e}")

        print(f"      📊 Found {len(reimplemented_files)} reimplemented files")

        # Show reimplemented files by type
        type_counts = {}
        for file_info in reimplemented_files:
            comp_type = file_info["component_type"]
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1

        print(f"      📋 Reimplemented files by type:")
        for comp_type, count in type_counts.items():
            print(f"         • {comp_type}: {count} files")

        return reimplemented_files

    def determine_component_type(self, file_path):
        """Determine component type from file path"""
        file_path_lower = file_path.lower()

        # Check for specific enhanced/proactive types first
        if "enhanced_interface_registry" in file_path_lower:
            return "enhanced_interface_registry"
        elif "proactive_interface_registry" in file_path_lower:
            return "proactive_interface_registry"
        elif "beast_readiness_validator" in file_path_lower:
            return "validation_framework"
        elif "validation" in file_path_lower or "validator" in file_path_lower:
            return "validation_framework"
        elif "reflective" in file_path_lower or "module" in file_path_lower:
            return "reflective_module"
        elif "compliance" in file_path_lower:
            return "compliance_system"
        elif "interface" in file_path_lower or "registry" in file_path_lower:
            return "interface_registry"
        else:
            return "interface_registry"  # Default

    def test_requirements_fidelity(self, reimplemented_files, requirements):
        """Test requirements fidelity for each reimplemented file"""
        print("🧪 Testing requirements fidelity...")

        fidelity_results = []

        for i, file_info in enumerate(reimplemented_files):
            print(
                f"      🧪 Testing {os.path.basename(file_info['path'])} ({i+1}/{len(reimplemented_files)})"
            )

            # Test syntax fidelity
            syntax_test = self.test_syntax_fidelity(file_info)

            # Test requirements compliance
            requirements_test = self.test_requirements_compliance(
                file_info, requirements
            )

            # Test import fidelity
            import_test = self.test_import_fidelity(file_info)

            # Test class structure fidelity
            structure_test = self.test_structure_fidelity(file_info, requirements)

            # Test method implementation fidelity
            method_test = self.test_method_fidelity(file_info, requirements)

            # Calculate overall fidelity score
            fidelity_score = self.calculate_fidelity_score(
                [
                    syntax_test,
                    requirements_test,
                    import_test,
                    structure_test,
                    method_test,
                ]
            )

            result = {
                "file_path": file_info["path"],
                "component_type": file_info["component_type"],
                "syntax_test": syntax_test,
                "requirements_test": requirements_test,
                "import_test": import_test,
                "structure_test": structure_test,
                "method_test": method_test,
                "fidelity_score": fidelity_score,
                "overall_status": "PASS" if fidelity_score >= 80 else "FAIL",
            }

            fidelity_results.append(result)

            status_icon = "✅" if result["overall_status"] == "PASS" else "❌"
            print(
                f"         {status_icon} Fidelity Score: {fidelity_score:.1f}% ({result['overall_status']})"
            )

        return fidelity_results

    def test_syntax_fidelity(self, file_info):
        """Test syntax fidelity"""
        try:
            # Parse AST to validate syntax
            ast.parse(file_info["content"])
            return {"status": "PASS", "score": 100, "message": "Syntax is valid"}
        except SyntaxError as e:
            return {"status": "FAIL", "score": 0, "message": f"Syntax error: {e}"}
        except Exception as e:
            return {"status": "FAIL", "score": 0, "message": f"Parse error: {e}"}

    def test_requirements_compliance(self, file_info, requirements):
        """Test compliance with requirements"""
        component_type = file_info["component_type"]
        content = file_info["content"]

        if component_type not in requirements:
            return {
                "status": "FAIL",
                "score": 0,
                "message": f"Unknown component type: {component_type}",
            }

        req_spec = requirements[component_type]
        compliance_score = 0
        total_checks = len(req_spec["requirements"])

        for requirement in req_spec["requirements"]:
            # Check if requirement is reflected in the code
            if self.requirement_reflected_in_code(requirement, content):
                compliance_score += 1

        # Convert to percentage
        compliance_score = (
            (compliance_score / total_checks) * 100 if total_checks > 0 else 0
        )

        return {
            "status": "PASS" if compliance_score >= 80 else "FAIL",
            "score": compliance_score,
            "message": f"Requirements compliance: {compliance_score:.1f}%",
        }

    def requirement_reflected_in_code(self, requirement, content):
        """Check if a requirement is reflected in the code"""
        # Simple keyword-based checking for requirement reflection
        requirement_keywords = {
            "interface metadata": ["InterfaceMetadata", "metadata"],
            "registration methods": ["register", "registration"],
            "interface discovery": ["list_interfaces", "get_metadata"],
            "validation": ["validate", "validation"],
            "compliance tracking": ["compliance", "score"],
            "JSON serialization": ["json", "serialize"],
            "status management": ["status", "Status"],
            "introspection": ["introspect", "inspect"],
            "method signature": ["signature", "extract_signatures"],
            "type checking": ["type", "Type", "typing"],
            "abstract base class": ["ABC", "abstractmethod"],
            "compliance standards": ["ComplianceLevel", "standards"],
            "metrics and scores": ["score", "metrics"],
            "reporting": ["report", "generate_report"],
            "automated checks": ["validate_compliance", "check"],
            "categorize levels": ["HIGH", "MEDIUM", "LOW", "CRITICAL"],
            "recommendations": ["recommendation", "recommend"],
            "input validation": ["validate", "input"],
            "error reporting": ["error", "report_error"],
            "custom rules": ["rule", "add_rule"],
            "validation history": ["history", "validation_history"],
            "rule-based": ["rule", "ValidationRule"],
        }

        requirement_lower = requirement.lower()
        for keyword, search_terms in requirement_keywords.items():
            if keyword in requirement_lower:
                for term in search_terms:
                    if term in content:
                        return True

        return False

    def test_import_fidelity(self, file_info):
        """Test import fidelity"""
        content = file_info["content"]
        component_type = file_info["component_type"]

        required_imports = {
            "interface_registry": ["typing", "dataclass", "datetime", "enum", "json"],
            "reflective_module": ["typing", "inspect", "abc"],
            "compliance_system": ["typing", "dataclass", "datetime", "enum"],
            "validation_framework": ["typing", "dataclass", "datetime", "enum"],
            "enhanced_interface_registry": [
                "typing",
                "dataclass",
                "datetime",
                "enum",
                "json",
            ],
            "proactive_interface_registry": [
                "typing",
                "dataclass",
                "datetime",
                "enum",
                "json",
            ],
        }

        if component_type not in required_imports:
            return {
                "status": "FAIL",
                "score": 0,
                "message": f"Unknown component type for imports: {component_type}",
            }

        required = required_imports[component_type]
        found_imports = 0

        for imp in required:
            if f"import {imp}" in content or f"from {imp}" in content:
                found_imports += 1

        score = (found_imports / len(required)) * 100

        return {
            "status": "PASS" if score >= 80 else "FAIL",
            "score": score,
            "message": f"Import fidelity: {found_imports}/{len(required)} imports found",
        }

    def test_structure_fidelity(self, file_info, requirements):
        """Test class structure fidelity"""
        content = file_info["content"]
        component_type = file_info["component_type"]

        if component_type not in requirements:
            return {
                "status": "FAIL",
                "score": 0,
                "message": f"Unknown component type: {component_type}",
            }

        req_spec = requirements[component_type]
        structure_score = 0
        total_checks = 0

        # Check required classes
        if "required_classes" in req_spec:
            total_checks += len(req_spec["required_classes"])
            for required_class in req_spec["required_classes"]:
                if f"class {required_class}" in content:
                    structure_score += 1

        # Check required enums
        if "required_enums" in req_spec:
            total_checks += len(req_spec["required_enums"])
            for required_enum in req_spec["required_enums"]:
                if f"class {required_enum}" in content and "Enum" in content:
                    structure_score += 1

        if total_checks == 0:
            return {
                "status": "PASS",
                "score": 100,
                "message": "No specific structure requirements",
            }

        final_score = (structure_score / total_checks) * 100

        return {
            "status": "PASS" if final_score >= 80 else "FAIL",
            "score": final_score,
            "message": f"Structure fidelity: {final_score:.1f}%",
        }

    def test_method_fidelity(self, file_info, requirements):
        """Test method implementation fidelity"""
        content = file_info["content"]
        component_type = file_info["component_type"]

        if component_type not in requirements:
            return {
                "status": "FAIL",
                "score": 0,
                "message": f"Unknown component type: {component_type}",
            }

        req_spec = requirements[component_type]

        if "required_methods" not in req_spec:
            return {
                "status": "PASS",
                "score": 100,
                "message": "No specific method requirements",
            }

        required_methods = req_spec["required_methods"]
        found_methods = 0

        for method in required_methods:
            if f"def {method}(" in content:
                found_methods += 1

        score = (found_methods / len(required_methods)) * 100

        return {
            "status": "PASS" if score >= 80 else "FAIL",
            "score": score,
            "message": f"Method fidelity: {found_methods}/{len(required_methods)} methods found",
        }

    def calculate_fidelity_score(self, test_results):
        """Calculate overall fidelity score"""
        total_score = 0
        total_tests = len(test_results)

        for test_result in test_results:
            total_score += test_result["score"]

        # Average the scores, not sum them
        return total_score / total_tests if total_tests > 0 else 0

    def generate_fidelity_report(self, fidelity_results, requirements):
        """Generate comprehensive fidelity report"""
        print("📊 Generating fidelity report...")

        # Calculate summary statistics
        total_files = len(fidelity_results)
        passed_files = len(
            [r for r in fidelity_results if r["overall_status"] == "PASS"]
        )
        failed_files = total_files - passed_files

        avg_fidelity_score = (
            sum(r["fidelity_score"] for r in fidelity_results) / total_files
            if total_files > 0
            else 0
        )

        # Group by component type
        type_stats = {}
        for result in fidelity_results:
            comp_type = result["component_type"]
            if comp_type not in type_stats:
                type_stats[comp_type] = {"total": 0, "passed": 0, "scores": []}

            type_stats[comp_type]["total"] += 1
            if result["overall_status"] == "PASS":
                type_stats[comp_type]["passed"] += 1
            type_stats[comp_type]["scores"].append(result["fidelity_score"])

        # Calculate type-specific statistics
        for comp_type, stats in type_stats.items():
            stats["pass_rate"] = (
                (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            )
            stats["avg_score"] = (
                sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
            )

        # Generate detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "Requirements Fidelity Testing",
            "scope": "Reimplemented Files",
            "summary": {
                "total_files_tested": total_files,
                "passed_files": passed_files,
                "failed_files": failed_files,
                "overall_pass_rate": (
                    (passed_files / total_files * 100) if total_files > 0 else 0
                ),
                "average_fidelity_score": avg_fidelity_score,
            },
            "component_type_statistics": type_stats,
            "detailed_results": fidelity_results,
            "requirements_registry": requirements,
        }

        # Save report
        os.makedirs(".beast_mode", exist_ok=True)
        with open(".beast_mode/beast_mode_requirements_fidelity_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(
            f"      💾 Fidelity report saved to .beast_mode/beast_mode_requirements_fidelity_report.json"
        )

        # Print summary
        print(f"\n📊 REQUIREMENTS FIDELITY TESTING SUMMARY")
        print("=" * 60)
        print(f"   📁 Total Files Tested: {total_files}")
        print(f"   ✅ Passed Files: {passed_files}")
        print(f"   ❌ Failed Files: {failed_files}")
        print(
            f"   📈 Overall Pass Rate: {(passed_files / total_files * 100):.1f}%"
            if total_files > 0
            else "   📈 Overall Pass Rate: 0.0%"
        )
        print(f"   🎯 Average Fidelity Score: {avg_fidelity_score:.1f}%")

        print(f"\n📋 COMPONENT TYPE STATISTICS")
        print("=" * 40)
        for comp_type, stats in type_stats.items():
            print(f"   {comp_type}:")
            print(f"      📊 Files: {stats['total']} ({stats['passed']} passed)")
            print(f"      📈 Pass Rate: {stats['pass_rate']:.1f}%")
            print(f"      🎯 Avg Score: {stats['avg_score']:.1f}%")

        # Identify top performers and issues
        print(f"\n🏆 TOP PERFORMERS")
        print("=" * 20)
        top_performers = sorted(
            fidelity_results, key=lambda x: x["fidelity_score"], reverse=True
        )[:5]
        for i, result in enumerate(top_performers):
            print(
                f"   {i+1}. {os.path.basename(result['file_path'])} - {result['fidelity_score']:.1f}%"
            )

        if failed_files > 0:
            print(f"\n⚠️  FILES NEEDING ATTENTION")
            print("=" * 30)
            failed_results = [
                r for r in fidelity_results if r["overall_status"] == "FAIL"
            ]
            for result in failed_results[:5]:  # Show top 5 failed files
                print(
                    f"   • {os.path.basename(result['file_path'])} - {result['fidelity_score']:.1f}%"
                )

        return report_data


if __name__ == "__main__":
    tester = BeastModeRequirementsFidelityTester()
    success = tester.run_requirements_fidelity_tests()

    if success:
        print("\n🎉 BEAST MODE REQUIREMENTS FIDELITY TESTING COMPLETE!")
        print("🧪 All files tested for requirements fidelity!")
        sys.exit(0)
    else:
        print("\n❌ BEAST MODE REQUIREMENTS FIDELITY TESTING FAILED")
        print("🔧 Testing encountered errors")
        sys.exit(1)
