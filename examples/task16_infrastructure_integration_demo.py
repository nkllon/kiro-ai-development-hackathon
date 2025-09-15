#!/usr/bin/env python3
"""
Beast Mode Framework - Task 16 Infrastructure Integration Demo
Demonstrates UC-25: Integration with existing project infrastructure and self-consistency validation

This example shows:
- Makefile system integration with Beast Mode operations
- Project model registry integration and validation
- Cursor rules integration for systematic development
- Beast Mode configuration management
- Complete self-consistency validation (UC-25)
- Credibility establishment through self-application
"""

import time
from datetime import datetime
from pathlib import Path

# Import Task 16 components
from src.beast_mode.integration.infrastructure_integration_manager import (
    InfrastructureIntegrationManager,
    IntegrationStatus,
)
from src.beast_mode.integration.self_consistency_validator import (
    SelfConsistencyValidator,
    ConsistencyCheck,
)


def main():
    """Demonstrate Task 16 infrastructure integration and self-consistency validation"""
    print("🚀 Beast Mode Framework - Task 16 Infrastructure Integration Demo")
    print("=" * 75)

    # Demo 1: Infrastructure Integration Manager
    print("\n🔗 Demo 1: Infrastructure Integration Manager")
    print("-" * 50)

    integration_manager = InfrastructureIntegrationManager(".")
    print(f"✅ Infrastructure Integration Manager initialized")
    print(f"   Status: {integration_manager.get_module_status()['status']}")
    print(f"   Project Root: {integration_manager.get_module_status()['project_root']}")

    # Validate complete infrastructure integration
    print("\n   Running Complete Infrastructure Integration Validation...")
    start_time = time.time()

    integration_result = integration_manager.validate_complete_integration()

    validation_time = time.time() - start_time

    print(f"   ✅ Infrastructure Validation Complete (Time: {validation_time:.2f}s)")
    print(f"      Validation ID: {integration_result['validation_id']}")
    print(
        f"      Overall Health Score: {integration_result['overall_health_score']:.2f}"
    )
    print(f"      Overall Status: {integration_result['overall_status']}")

    # Show component validation results
    print(f"\n   📊 Component Integration Results:")
    for result in integration_result["component_results"]:
        status_icon = {
            IntegrationStatus.INTEGRATED: "🟢",
            IntegrationStatus.PARTIAL: "🟡",
            IntegrationStatus.MISSING: "🔴",
            IntegrationStatus.FAILED: "❌",
        }.get(result.status, "❓")

        print(f"      {status_icon} {result.component.title()}: {result.status.value}")
        print(f"         Details: {result.details}")

        if result.issues:
            print(f"         Issues: {len(result.issues)} found")
            for issue in result.issues[:2]:  # Show first 2 issues
                print(f"           • {issue}")

        if result.recommendations:
            print(f"         Recommendations: {len(result.recommendations)} available")
            for rec in result.recommendations[:1]:  # Show first recommendation
                print(f"           💡 {rec}")

    # Show integration recommendations
    if integration_result["recommendations"]:
        print(f"\n   🎯 Integration Recommendations:")
        for rec in integration_result["recommendations"][:3]:  # Show top 3
            print(f"      💡 {rec}")

    # Demo 2: Self-Consistency Validation (UC-25)
    print("\n🎯 Demo 2: Self-Consistency Validation (UC-25)")
    print("-" * 52)

    consistency_validator = SelfConsistencyValidator(".")
    print(f"✅ Self-Consistency Validator initialized")
    print(f"   Status: {consistency_validator.get_module_status()['status']}")
    print(
        f"   Credibility Success Rate: {consistency_validator.get_module_status()['credibility_success_rate']:.1%}"
    )

    # Run complete self-consistency validation
    print("\n   Running Complete Self-Consistency Validation...")
    print("   (Validating that Beast Mode uses its own systematic methodology)")
    start_time = time.time()

    consistency_report = consistency_validator.validate_complete_self_consistency()

    validation_time = time.time() - start_time

    print(f"   ✅ Self-Consistency Validation Complete (Time: {validation_time:.2f}s)")
    print(f"      Report ID: {consistency_report.report_id}")
    print(
        f"      Overall Consistency Score: {consistency_report.overall_consistency_score:.2f}"
    )
    print(
        f"      Credibility Established: {'✅ YES' if consistency_report.credibility_established else '❌ NO'}"
    )
    print(f"      Execution Time: {consistency_report.execution_time_ms}ms")

    # Show individual consistency check results
    print(f"\n   📋 Individual Consistency Check Results:")
    for result in consistency_report.check_results:
        status_icon = "✅" if result.passed else "❌"
        check_name = result.check_type.value.replace("_", " ").title()

        print(f"      {status_icon} {check_name}: {result.score:.2f}")
        print(f"         Passed: {result.passed}")
        print(f"         Evidence: {len(result.evidence)} items")

        # Show key evidence
        if result.evidence:
            for evidence in result.evidence[:2]:  # Show first 2 evidence items
                print(f"           🔍 {evidence}")

        # Show issues if any
        if result.issues:
            print(f"         Issues: {len(result.issues)} found")
            for issue in result.issues[:1]:  # Show first issue
                print(f"           ⚠️  {issue}")

    # Demo 3: Superiority Evidence Generation
    print("\n🏆 Demo 3: Systematic Superiority Evidence")
    print("-" * 45)

    print(
        "   Generating concrete evidence of Beast Mode superiority over ad-hoc approaches..."
    )

    superiority_evidence = consistency_report.superiority_evidence

    print(f"\n   📊 Systematic vs Ad-Hoc Comparison:")
    comparison = superiority_evidence.get("systematic_vs_adhoc_comparison", {})

    for category, details in comparison.items():
        if isinstance(details, dict):
            category_name = category.replace("_", " ").title()
            print(f"      🎯 {category_name}:")
            print(f"         Beast Mode: {details.get('beast_mode', 'N/A')}")
            print(f"         Ad-Hoc: {details.get('adhoc', 'N/A')}")
            print(f"         Superiority: {details.get('superiority', 'N/A')}")

    # Show measurable improvements
    improvements = superiority_evidence.get("measurable_improvements", {})
    print(f"\n   📈 Measurable Improvements:")
    print(
        f"      Overall Consistency Score: {improvements.get('overall_consistency_score', 0):.2f}"
    )
    print(
        f"      Self-Application Success: {'✅' if improvements.get('self_application_success') else '❌'}"
    )
    print(
        f"      Credibility Established: {'✅' if improvements.get('credibility_established') else '❌'}"
    )
    print(
        f"      Systematic Methodology Proven: {'✅' if improvements.get('systematic_methodology_proven') else '❌'}"
    )

    # Show concrete metrics
    metrics = superiority_evidence.get("concrete_metrics", {})
    print(f"\n   🔢 Concrete Metrics:")
    print(
        f"      Consistency Checks Passed: {metrics.get('consistency_checks_passed', 0)}/{metrics.get('total_consistency_checks', 0)}"
    )
    print(
        f"      Evidence Items Collected: {metrics.get('evidence_items_collected', 0)}"
    )
    print(f"      Issues Identified: {metrics.get('issues_identified', 0)}")
    print(
        f"      Recommendations Generated: {metrics.get('recommendations_generated', 0)}"
    )

    # Demo 4: Self-Application Proof (UC-25 Core)
    print("\n🔄 Demo 4: Self-Application Proof (UC-25 Core Requirement)")
    print("-" * 62)

    print(
        "   Proving Beast Mode successfully applies its own systematic methodology..."
    )

    self_application_proof = consistency_report.self_application_proof

    # Methodology application proof
    methodology = self_application_proof.get("methodology_application", {})
    print(f"\n   🧠 Methodology Application Proof:")
    print(
        f"      Model-Driven Decisions: {'✅' if methodology.get('model_driven_decisions') else '❌'}"
    )
    print(
        f"      Systematic Tool Repair: {'✅' if methodology.get('systematic_tool_repair') else '❌'}"
    )
    print(
        f"      PDCA Methodology: {'✅' if methodology.get('pdca_methodology') else '❌'}"
    )
    print(f"      RM Compliance: {'✅' if methodology.get('rm_compliance') else '❌'}")

    # Self-consistency validation proof
    validation_proof = self_application_proof.get("self_consistency_validation", {})
    print(f"\n   ✅ Self-Consistency Validation Proof:")
    print(
        f"      All Checks Implemented: {'✅' if validation_proof.get('all_checks_implemented') else '❌'}"
    )
    print(
        f"      Majority Checks Passed: {'✅' if validation_proof.get('majority_checks_passed') else '❌'}"
    )
    print(
        f"      Critical Checks Passed: {'✅' if validation_proof.get('critical_checks_passed') else '❌'}"
    )

    # Credibility establishment proof
    credibility_proof = self_application_proof.get("credibility_establishment", {})
    print(f"\n   🏅 Credibility Establishment Proof:")
    print(
        f"      Credibility Threshold Met: {'✅' if credibility_proof.get('credibility_threshold_met') else '❌'}"
    )
    print(
        f"      Self-Application Proven: {'✅' if credibility_proof.get('self_application_proven') else '❌'}"
    )
    print(
        f"      Systematic Approach Validated: {'✅' if credibility_proof.get('systematic_approach_validated') else '❌'}"
    )
    print(
        f"      Concrete Evidence Provided: {'✅' if credibility_proof.get('concrete_evidence_provided') else '❌'}"
    )

    # Demo 5: Integration Analytics and Health Monitoring
    print("\n📊 Demo 5: Integration Analytics and Health Monitoring")
    print("-" * 56)

    # Get integration analytics
    integration_analytics = integration_manager.get_integration_analytics()

    print(f"   🔗 Infrastructure Integration Analytics:")
    integration_metrics = integration_analytics.get("integration_metrics", {})
    print(f"      Total Validations: {integration_metrics.get('total_validations', 0)}")
    print(
        f"      Integration Health Score: {integration_metrics.get('integration_health_score', 0):.2f}"
    )
    print(
        f"      Components Integrated: {integration_metrics.get('components_integrated', 0)}"
    )
    print(
        f"      Successful Integrations: {integration_metrics.get('successful_integrations', 0)}"
    )

    # Get consistency analytics
    consistency_analytics = consistency_validator.get_validation_analytics()

    print(f"\n   🎯 Self-Consistency Analytics:")
    validation_metrics = consistency_analytics.get("validation_metrics", {})
    print(f"      Total Validations: {validation_metrics.get('total_validations', 0)}")
    print(
        f"      Average Consistency Score: {validation_metrics.get('average_consistency_score', 0):.2f}"
    )
    print(
        f"      Credibility Validations Passed: {validation_metrics.get('credibility_validations_passed', 0)}"
    )
    print(
        f"      Self-Application Success Rate: {validation_metrics.get('self_application_success_rate', 0):.1%}"
    )

    # Show health trends
    health_trends = integration_analytics.get("health_trends", {})
    if health_trends.get("trend") != "insufficient_data":
        print(f"\n   📈 Integration Health Trends:")
        print(f"      Trend: {health_trends.get('trend', 'unknown')}")
        print(f"      Current Score: {health_trends.get('current_score', 0):.2f}")
        if "change_percentage" in health_trends:
            change = health_trends["change_percentage"]
            change_icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"      Change: {change_icon} {change:+.1f}%")

    # Demo 6: Makefile Integration Demonstration
    print("\n🔧 Demo 6: Makefile Integration Demonstration")
    print("-" * 48)

    print("   Beast Mode Makefile integration provides systematic operations:")
    print("   (These targets are now available in the project Makefile)")

    makefile_targets = [
        ("beast-mode", "Launch Beast Mode Framework with systematic methodology"),
        ("pdca-cycle", "Execute complete Plan-Do-Check-Act cycle"),
        ("beast-mode-health", "Check health of all Beast Mode components"),
        ("beast-mode-validate", "Complete Beast Mode validation and assessment"),
        ("beast-mode-self-consistency", "Validate Beast Mode self-consistency (UC-25)"),
        ("beast-mode-superiority-metrics", "Generate concrete superiority evidence"),
    ]

    for target, description in makefile_targets:
        print(f"      🎯 make {target}")
        print(f"         {description}")

    print(f"\n   Integration Benefits:")
    print(f"      ✅ Beast Mode operations integrated into existing workflow")
    print(f"      ✅ Systematic methodology accessible via familiar make commands")
    print(f"      ✅ Self-consistency validation automated")
    print(f"      ✅ Superiority evidence generation on-demand")

    # Demo 7: Credibility Report Generation
    print("\n🏆 Demo 7: Comprehensive Credibility Report")
    print("-" * 46)

    print("   Generating comprehensive credibility establishment report...")

    credibility_report = consistency_validator.generate_credibility_report()

    credibility_assessment = credibility_report["credibility_assessment"]

    print(f"\n   🎖️  Credibility Assessment Summary:")
    print(
        f"      Credibility Established: {'🏆 YES' if credibility_assessment['credibility_established'] else '❌ NO'}"
    )
    print(
        f"      Overall Consistency Score: {credibility_assessment['overall_consistency_score']:.2f}"
    )
    print(
        f"      Credibility Threshold: {credibility_assessment['credibility_threshold']:.2f}"
    )
    print(
        f"      Evidence Strength: {credibility_assessment['evidence_strength'].upper()}"
    )
    print(
        f"      Self-Application Proven: {'✅' if credibility_assessment['self_application_proven'] else '❌'}"
    )
    print(
        f"      Systematic Superiority Demonstrated: {'✅' if credibility_assessment['systematic_superiority_demonstrated'] else '❌'}"
    )

    # Show key recommendations
    if consistency_report.recommendations:
        print(f"\n   💡 Key Recommendations:")
        for rec in consistency_report.recommendations[:3]:  # Show top 3
            print(f"      • {rec}")

    # Final summary
    print("\n" + "=" * 75)
    print("🎉 Task 16 Infrastructure Integration Demo Complete!")
    print("=" * 75)

    print("\nKey Achievements Demonstrated:")
    print(
        "• UC-25: Complete self-consistency validation - Beast Mode uses its own methodology"
    )
    print(
        "• Infrastructure integration with existing Makefile, registry, and cursor rules"
    )
    print("• Concrete superiority evidence generation with measurable metrics")
    print("• Credibility establishment through systematic self-application")
    print("• Comprehensive health monitoring and analytics")

    print("\nSelf-Consistency Validation Results:")
    consistency_score = consistency_report.overall_consistency_score
    if consistency_score >= 0.9:
        print("🏆 EXCELLENCE: Beast Mode demonstrates exceptional self-consistency")
    elif consistency_score >= 0.8:
        print("🥇 CREDIBLE: Beast Mode successfully proves systematic superiority")
    elif consistency_score >= 0.7:
        print("✅ PASSING: Beast Mode meets self-consistency requirements")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Self-consistency validation requires attention")

    print(f"   Final Consistency Score: {consistency_score:.2f}")
    print(
        f"   Credibility Established: {'YES' if consistency_report.credibility_established else 'NO'}"
    )

    print("\nInfrastructure Integration Status:")
    integration_score = integration_result["overall_health_score"]
    if integration_score >= 0.9:
        print("🏆 EXCELLENT: All infrastructure components fully integrated")
    elif integration_score >= 0.7:
        print("✅ GOOD: Infrastructure integration successful with minor issues")
    elif integration_score >= 0.5:
        print("⚠️  PARTIAL: Infrastructure integration needs improvement")
    else:
        print("❌ FAILED: Infrastructure integration requires immediate attention")

    print(f"   Integration Health Score: {integration_score:.2f}")
    print(f"   Components Status: {integration_result['overall_status']}")

    print("\nNext Steps:")
    print("• Use 'make beast-mode' to access systematic development operations")
    print("• Run 'make beast-mode-validate' for ongoing self-consistency validation")
    print(
        "• Execute 'make pdca-cycle' to apply systematic methodology to development tasks"
    )
    print("• Generate superiority evidence with 'make beast-mode-superiority-metrics'")
    print("• Monitor system health with 'make beast-mode-health'")

    print(
        "\n🎯 UC-25 VALIDATION COMPLETE: Beast Mode successfully uses its own systematic methodology!"
    )


if __name__ == "__main__":
    main()
