#!/usr/bin/env python3
"""
CMS Architecture Specification Validation Script
================================================

Validates the CMS architecture specification for DAG execution readiness
according to Beast Mode Framework standards and systematic development governance.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Ensure CMS architecture spec is ready for systematic implementation
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


class CMSArchitectureSpecValidator:
    """Validates CMS architecture specification for DAG execution readiness."""
    
    def __init__(self, spec_path: str = ".kiro/specs/cms-architecture"):
        self.spec_path = Path(spec_path)
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "spec_path": str(self.spec_path),
            "validations": {},
            "overall_status": "UNKNOWN",
            "readiness_score": 0.0,
            "issues": [],
            "recommendations": []
        }
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🔍 Starting CMS Architecture Specification Validation...")
        print(f"📁 Spec Path: {self.spec_path}")
        print("=" * 60)
        
        # Run all validation checks
        self.validate_file_structure()
        self.validate_requirements()
        self.validate_design()
        self.validate_tasks()
        self.validate_dag_config()
        self.validate_rm_ddd_compliance()
        self.validate_interface_governance()
        self.validate_quality_gates()
        
        # Calculate overall readiness
        self.calculate_readiness_score()
        
        # Generate report
        self.generate_validation_report()
        
        return self.validation_results
    
    def validate_file_structure(self) -> bool:
        """Validate required specification files exist."""
        print("📋 Validating File Structure...")
        
        required_files = [
            "requirements.md",
            "design.md", 
            "tasks.md",
            "dag-config.yml"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_name in required_files:
            file_path = self.spec_path / file_name
            if file_path.exists():
                existing_files.append(file_name)
                print(f"  ✅ {file_name}")
            else:
                missing_files.append(file_name)
                print(f"  ❌ {file_name} - MISSING")
        
        validation_passed = len(missing_files) == 0
        
        self.validation_results["validations"]["file_structure"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "existing_files": existing_files,
            "missing_files": missing_files,
            "score": len(existing_files) / len(required_files)
        }
        
        if missing_files:
            self.validation_results["issues"].append(
                f"Missing required files: {', '.join(missing_files)}"
            )
        
        return validation_passed
    
    def validate_requirements(self) -> bool:
        """Validate requirements.md completeness."""
        print("📝 Validating Requirements...")
        
        requirements_file = self.spec_path / "requirements.md"
        if not requirements_file.exists():
            self.validation_results["validations"]["requirements"] = {
                "status": "FAILED",
                "reason": "requirements.md not found",
                "score": 0.0
            }
            return False
        
        content = requirements_file.read_text()
        
        # Check for required sections
        required_sections = [
            "Stakeholder Requirements",
            "Functional Requirements", 
            "Non-Functional Requirements",
            "Integration Requirements",
            "Compliance and Governance Requirements",
            "Success Criteria"
        ]
        
        found_sections = []
        missing_sections = []
        
        for section in required_sections:
            if section.lower() in content.lower():
                found_sections.append(section)
                print(f"  ✅ {section}")
            else:
                missing_sections.append(section)
                print(f"  ❌ {section} - MISSING")
        
        # Check for stakeholder-specific requirements
        stakeholders = ["Developer", "DevOps", "CFO", "CTO", "Architect"]
        found_stakeholders = []
        
        for stakeholder in stakeholders:
            if stakeholder.lower() in content.lower():
                found_stakeholders.append(stakeholder)
        
        validation_passed = len(missing_sections) == 0
        completeness_score = len(found_sections) / len(required_sections)
        stakeholder_score = len(found_stakeholders) / len(stakeholders)
        
        self.validation_results["validations"]["requirements"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "found_sections": found_sections,
            "missing_sections": missing_sections,
            "found_stakeholders": found_stakeholders,
            "completeness_score": completeness_score,
            "stakeholder_coverage": stakeholder_score,
            "score": (completeness_score + stakeholder_score) / 2
        }
        
        if missing_sections:
            self.validation_results["issues"].append(
                f"Missing requirement sections: {', '.join(missing_sections)}"
            )
        
        return validation_passed
    
    def validate_design(self) -> bool:
        """Validate design.md completeness."""
        print("🏗️ Validating Design...")
        
        design_file = self.spec_path / "design.md"
        if not design_file.exists():
            self.validation_results["validations"]["design"] = {
                "status": "FAILED",
                "reason": "design.md not found",
                "score": 0.0
            }
            return False
        
        content = design_file.read_text()
        
        # Check for required design sections
        required_sections = [
            "System Architecture",
            "Component Architecture",
            "Stakeholder-Specific Design",
            "Data Model Design",
            "Security Design",
            "Performance Design",
            "Integration Design",
            "Monitoring and Observability Design",
            "Deployment Design"
        ]
        
        found_sections = []
        missing_sections = []
        
        for section in required_sections:
            if section.lower() in content.lower():
                found_sections.append(section)
                print(f"  ✅ {section}")
            else:
                missing_sections.append(section)
                print(f"  ❌ {section} - MISSING")
        
        # Check for architecture diagrams (mermaid)
        has_diagrams = "```mermaid" in content
        print(f"  {'✅' if has_diagrams else '❌'} Architecture Diagrams (Mermaid)")
        
        validation_passed = len(missing_sections) == 0 and has_diagrams
        completeness_score = len(found_sections) / len(required_sections)
        
        self.validation_results["validations"]["design"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "found_sections": found_sections,
            "missing_sections": missing_sections,
            "has_diagrams": has_diagrams,
            "completeness_score": completeness_score,
            "score": completeness_score * (1.1 if has_diagrams else 0.9)
        }
        
        if missing_sections:
            self.validation_results["issues"].append(
                f"Missing design sections: {', '.join(missing_sections)}"
            )
        
        if not has_diagrams:
            self.validation_results["issues"].append(
                "No architecture diagrams found in design.md"
            )
        
        return validation_passed
    
    def validate_tasks(self) -> bool:
        """Validate tasks.md completeness and structure."""
        print("📋 Validating Tasks...")
        
        tasks_file = self.spec_path / "tasks.md"
        if not tasks_file.exists():
            self.validation_results["validations"]["tasks"] = {
                "status": "FAILED",
                "reason": "tasks.md not found",
                "score": 0.0
            }
            return False
        
        content = tasks_file.read_text()
        
        # Check for required task structure
        required_elements = [
            "Phase 1:",
            "Phase 2:",
            "Dependencies:",
            "Acceptance Criteria:",
            "Deliverables:",
            "Success Criteria"
        ]
        
        found_elements = []
        missing_elements = []
        
        for element in required_elements:
            if element.lower() in content.lower():
                found_elements.append(element)
                print(f"  ✅ {element}")
            else:
                missing_elements.append(element)
                print(f"  ❌ {element} - MISSING")
        
        # Count tasks and phases
        task_count = content.lower().count("task ")
        phase_count = content.lower().count("phase ")
        
        print(f"  📊 Tasks Found: {task_count}")
        print(f"  📊 Phases Found: {phase_count}")
        
        validation_passed = len(missing_elements) == 0 and task_count >= 10
        completeness_score = len(found_elements) / len(required_elements)
        
        self.validation_results["validations"]["tasks"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "found_elements": found_elements,
            "missing_elements": missing_elements,
            "task_count": task_count,
            "phase_count": phase_count,
            "completeness_score": completeness_score,
            "score": completeness_score * (1.1 if task_count >= 20 else 1.0)
        }
        
        if missing_elements:
            self.validation_results["issues"].append(
                f"Missing task elements: {', '.join(missing_elements)}"
            )
        
        if task_count < 10:
            self.validation_results["issues"].append(
                f"Insufficient task breakdown: {task_count} tasks (minimum 10 required)"
            )
        
        return validation_passed
    
    def validate_dag_config(self) -> bool:
        """Validate DAG configuration file."""
        print("🔗 Validating DAG Configuration...")
        
        dag_file = self.spec_path / "dag-config.yml"
        if not dag_file.exists():
            self.validation_results["validations"]["dag_config"] = {
                "status": "FAILED",
                "reason": "dag-config.yml not found",
                "score": 0.0
            }
            return False
        
        try:
            with open(dag_file, 'r') as f:
                dag_config = yaml.safe_load(f)
        except Exception as e:
            self.validation_results["validations"]["dag_config"] = {
                "status": "FAILED",
                "reason": f"YAML parsing error: {e}",
                "score": 0.0
            }
            return False
        
        # Check required DAG structure
        required_keys = [
            "metadata",
            "execution", 
            "validation",
            "monitoring",
            "tasks",
            "edges",
            "success_criteria"
        ]
        
        found_keys = []
        missing_keys = []
        
        for key in required_keys:
            if key in dag_config:
                found_keys.append(key)
                print(f"  ✅ {key}")
            else:
                missing_keys.append(key)
                print(f"  ❌ {key} - MISSING")
        
        # Validate tasks structure
        tasks = dag_config.get("tasks", [])
        task_count = len(tasks)
        
        # Check for circular dependencies
        has_circular_deps = self.check_circular_dependencies(dag_config)
        
        print(f"  📊 DAG Tasks: {task_count}")
        print(f"  🔄 Circular Dependencies: {'❌ FOUND' if has_circular_deps else '✅ NONE'}")
        
        validation_passed = (
            len(missing_keys) == 0 and 
            task_count >= 10 and 
            not has_circular_deps
        )
        
        completeness_score = len(found_keys) / len(required_keys)
        
        self.validation_results["validations"]["dag_config"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "found_keys": found_keys,
            "missing_keys": missing_keys,
            "task_count": task_count,
            "has_circular_dependencies": has_circular_deps,
            "completeness_score": completeness_score,
            "score": completeness_score * (0.5 if has_circular_deps else 1.0)
        }
        
        if missing_keys:
            self.validation_results["issues"].append(
                f"Missing DAG config keys: {', '.join(missing_keys)}"
            )
        
        if has_circular_deps:
            self.validation_results["issues"].append(
                "Circular dependencies detected in DAG configuration"
            )
        
        return validation_passed
    
    def check_circular_dependencies(self, dag_config: Dict[str, Any]) -> bool:
        """Check for circular dependencies in DAG."""
        tasks = dag_config.get("tasks", [])
        edges = dag_config.get("edges", [])
        
        # Build adjacency list
        graph = {}
        for task in tasks:
            task_id = task.get("id", "")
            graph[task_id] = []
        
        for edge in edges:
            from_task = edge.get("from", "")
            to_task = edge.get("to", "")
            if from_task in graph:
                graph[from_task].append(to_task)
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True
        
        return False
    
    def validate_rm_ddd_compliance(self) -> bool:
        """Validate RM-DDD compliance requirements."""
        print("🏛️ Validating RM-DDD Compliance...")
        
        # Check if ReflectiveModule pattern is mentioned
        design_file = self.spec_path / "design.md"
        requirements_file = self.spec_path / "requirements.md"
        
        reflective_module_mentioned = False
        beast_mode_mentioned = False
        health_monitoring_mentioned = False
        
        for file_path in [design_file, requirements_file]:
            if file_path.exists():
                content = file_path.read_text().lower()
                if "reflectivemodule" in content or "reflective module" in content:
                    reflective_module_mentioned = True
                if "beast mode" in content:
                    beast_mode_mentioned = True
                if "health monitoring" in content or "/health" in content:
                    health_monitoring_mentioned = True
        
        print(f"  {'✅' if reflective_module_mentioned else '❌'} ReflectiveModule Pattern")
        print(f"  {'✅' if beast_mode_mentioned else '❌'} Beast Mode Framework")
        print(f"  {'✅' if health_monitoring_mentioned else '❌'} Health Monitoring")
        
        compliance_score = sum([
            reflective_module_mentioned,
            beast_mode_mentioned, 
            health_monitoring_mentioned
        ]) / 3
        
        validation_passed = compliance_score >= 0.67
        
        self.validation_results["validations"]["rm_ddd_compliance"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "reflective_module_mentioned": reflective_module_mentioned,
            "beast_mode_mentioned": beast_mode_mentioned,
            "health_monitoring_mentioned": health_monitoring_mentioned,
            "compliance_score": compliance_score,
            "score": compliance_score
        }
        
        if not reflective_module_mentioned:
            self.validation_results["recommendations"].append(
                "Add ReflectiveModule pattern compliance to design"
            )
        
        if not beast_mode_mentioned:
            self.validation_results["recommendations"].append(
                "Ensure Beast Mode Framework integration is documented"
            )
        
        return validation_passed
    
    def validate_interface_governance(self) -> bool:
        """Validate interface governance compliance."""
        print("🔌 Validating Interface Governance...")
        
        # Check if interface registry is mentioned
        design_file = self.spec_path / "design.md"
        interface_governance_mentioned = False
        
        if design_file.exists():
            content = design_file.read_text().lower()
            interface_governance_mentioned = (
                "interface" in content and 
                ("registry" in content or "governance" in content)
            )
        
        print(f"  {'✅' if interface_governance_mentioned else '❌'} Interface Governance")
        
        # Check if interface registry exists
        interface_registry_exists = Path("src/rm_ddd/core/interface_registry.py").exists()
        print(f"  {'✅' if interface_registry_exists else '❌'} Interface Registry Exists")
        
        validation_passed = interface_governance_mentioned and interface_registry_exists
        score = (interface_governance_mentioned + interface_registry_exists) / 2
        
        self.validation_results["validations"]["interface_governance"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "interface_governance_mentioned": interface_governance_mentioned,
            "interface_registry_exists": interface_registry_exists,
            "score": score
        }
        
        if not interface_governance_mentioned:
            self.validation_results["recommendations"].append(
                "Add interface governance documentation to design"
            )
        
        return validation_passed
    
    def validate_quality_gates(self) -> bool:
        """Validate quality gate requirements."""
        print("🚪 Validating Quality Gates...")
        
        # Check for quality requirements in specifications
        requirements_file = self.spec_path / "requirements.md"
        quality_gates_mentioned = False
        test_coverage_mentioned = False
        
        if requirements_file.exists():
            content = requirements_file.read_text().lower()
            quality_gates_mentioned = "quality" in content and "gate" in content
            test_coverage_mentioned = "test coverage" in content or "90%" in content
        
        print(f"  {'✅' if quality_gates_mentioned else '❌'} Quality Gates")
        print(f"  {'✅' if test_coverage_mentioned else '❌'} Test Coverage Requirements")
        
        validation_passed = quality_gates_mentioned and test_coverage_mentioned
        score = (quality_gates_mentioned + test_coverage_mentioned) / 2
        
        self.validation_results["validations"]["quality_gates"] = {
            "status": "PASSED" if validation_passed else "FAILED",
            "quality_gates_mentioned": quality_gates_mentioned,
            "test_coverage_mentioned": test_coverage_mentioned,
            "score": score
        }
        
        if not quality_gates_mentioned:
            self.validation_results["recommendations"].append(
                "Add quality gate requirements to specification"
            )
        
        if not test_coverage_mentioned:
            self.validation_results["recommendations"].append(
                "Add test coverage requirements (>90%) to specification"
            )
        
        return validation_passed
    
    def calculate_readiness_score(self) -> float:
        """Calculate overall readiness score."""
        validations = self.validation_results["validations"]
        
        # Weight different validation categories
        weights = {
            "file_structure": 0.15,
            "requirements": 0.20,
            "design": 0.20,
            "tasks": 0.15,
            "dag_config": 0.15,
            "rm_ddd_compliance": 0.10,
            "interface_governance": 0.05,
            "quality_gates": 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for category, weight in weights.items():
            if category in validations:
                score = validations[category].get("score", 0.0)
                total_score += score * weight
                total_weight += weight
        
        readiness_score = total_score / total_weight if total_weight > 0 else 0.0
        self.validation_results["readiness_score"] = readiness_score
        
        # Determine overall status
        if readiness_score >= 0.9:
            self.validation_results["overall_status"] = "READY"
        elif readiness_score >= 0.7:
            self.validation_results["overall_status"] = "MOSTLY_READY"
        elif readiness_score >= 0.5:
            self.validation_results["overall_status"] = "NEEDS_WORK"
        else:
            self.validation_results["overall_status"] = "NOT_READY"
        
        return readiness_score
    
    def generate_validation_report(self) -> None:
        """Generate comprehensive validation report."""
        print("\n" + "=" * 60)
        print("📊 CMS ARCHITECTURE SPECIFICATION VALIDATION REPORT")
        print("=" * 60)
        
        # Overall status
        status = self.validation_results["overall_status"]
        score = self.validation_results["readiness_score"]
        
        status_emoji = {
            "READY": "🟢",
            "MOSTLY_READY": "🟡", 
            "NEEDS_WORK": "🟠",
            "NOT_READY": "🔴"
        }
        
        print(f"\n{status_emoji.get(status, '⚪')} Overall Status: {status}")
        print(f"📈 Readiness Score: {score:.2%}")
        
        # Validation breakdown
        print(f"\n📋 Validation Breakdown:")
        validations = self.validation_results["validations"]
        
        for category, result in validations.items():
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            score = result.get("score", 0.0)
            print(f"  {status_icon} {category.replace('_', ' ').title()}: {score:.2%}")
        
        # Issues
        issues = self.validation_results["issues"]
        if issues:
            print(f"\n⚠️ Issues Found ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        # Recommendations
        recommendations = self.validation_results["recommendations"]
        if recommendations:
            print(f"\n💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Next steps
        print(f"\n🚀 Next Steps:")
        if status == "READY":
            print("  ✅ Specification is ready for DAG execution!")
            print("  🎯 Run: make dag-execute")
        elif status == "MOSTLY_READY":
            print("  🔧 Address minor issues and recommendations")
            print("  🎯 Consider proceeding with DAG execution")
        else:
            print("  🛠️ Address critical issues before DAG execution")
            print("  📝 Update specification files as needed")
        
        print("\n" + "=" * 60)


def main():
    """Main validation function."""
    validator = CMSArchitectureSpecValidator()
    results = validator.validate_all()
    
    # Save results to file
    results_file = Path("cms_architecture_validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Validation results saved to: {results_file}")
    
    # Exit with appropriate code
    status = results["overall_status"]
    if status in ["READY", "MOSTLY_READY"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()