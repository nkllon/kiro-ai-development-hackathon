#!/usr/bin/env python3
"""
Systematic Infrastructure Validation

This script demonstrates the Beast Mode Core Infrastructure Validation Framework
implementing the systematic priority: ALWAYS suspect logging and profiling first.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.beast_mode.infrastructure.validation_framework import (
    CoreInfrastructureValidator,
)


def main():
    """Execute systematic infrastructure validation"""

    print("🔍 BEAST MODE: Systematic Infrastructure Validation")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 ALWAYS suspect logging and profiling infrastructure first")
    print("=" * 60)

    try:
        # Initialize infrastructure validator
        validator = CoreInfrastructureValidator("systematic_infrastructure_validator")

        print("\n🚀 Executing Complete Infrastructure Assessment")
        print("-" * 50)

        # Perform complete systematic validation
        assessment = validator.validate_complete_infrastructure()

        print(f"\n📊 INFRASTRUCTURE ASSESSMENT RESULTS")
        print("=" * 50)
        print(f"Assessment ID: {assessment.assessment_id}")
        print(f"Overall Compliance Score: {assessment.overall_compliance_score:.2f}")
        print(f"Beast Mode Score: {assessment.beast_mode_score:.2f}/10.00")
        print(f"Systematic Readiness: {assessment.systematic_readiness}")

        print(f"\n🚨 Issue Summary:")
        print(f"   • Critical Issues: {assessment.critical_issues}")
        print(f"   • High Priority Issues: {assessment.high_priority_issues}")

        print(f"\n📋 Component Validation Results:")
        for result in assessment.validation_results:
            status_icon = (
                "✅"
                if result.status == "PASS"
                else "⚠️" if result.status == "WARNING" else "❌"
            )
            print(
                f"   {status_icon} {result.component.value.title()}: {result.status} ({result.systematic_compliance_score:.2f})"
            )

            if result.issues:
                print(f"      Issues: {len(result.issues)}")
                for issue in result.issues[:2]:  # Show top 2 issues
                    severity_icon = (
                        "🚨"
                        if issue.severity.value == "critical"
                        else "⚠️" if issue.severity.value == "high" else "ℹ️"
                    )
                    print(
                        f"        {severity_icon} {issue.issue_type}: {issue.description}"
                    )

        # Generate remediation plan
        print(f"\n⚡ SYSTEMATIC REMEDIATION PLAN")
        print("-" * 50)

        remediation_plan = validator.generate_remediation_plan(assessment)

        print(f"Plan Priority: {remediation_plan['overall_priority']}")
        print(f"Estimated Total Time: {remediation_plan['estimated_total_time']}")

        for phase in remediation_plan["phases"]:
            print(
                f"\\n📋 Phase {phase['phase']}: {phase['name']} ({phase['priority']})"
            )
            print(f"   Estimated Time: {phase['estimated_time']}")
            print(f"   Actions:")
            for i, action in enumerate(phase["actions"][:3], 1):  # Show top 3 actions
                print(f"     {i}. {action}")

        # Beast Mode Assessment
        print(f"\n🐺 BEAST MODE INFRASTRUCTURE ASSESSMENT")
        print("-" * 50)

        if assessment.beast_mode_score >= 9.0:
            beast_assessment = (
                "🏆 INFRASTRUCTURE EXCELLENCE: Systematic foundation achieved!"
            )
        elif assessment.beast_mode_score >= 7.0:
            beast_assessment = (
                "🥇 INFRASTRUCTURE PROFICIENCY: Strong systematic foundation!"
            )
        elif assessment.beast_mode_score >= 5.0:
            beast_assessment = "🥈 INFRASTRUCTURE DEVELOPING: Good foundation with systematic improvements needed"
        else:
            beast_assessment = (
                "🥉 INFRASTRUCTURE CRITICAL: Immediate systematic intervention required"
            )

        print(f"Score: {assessment.beast_mode_score:.2f}/10.00")
        print(f"Assessment: {beast_assessment}")

        # Key Insights
        print(f"\n🎯 Key Systematic Insights:")

        # Check if logging was validated first
        logging_result = next(
            (
                r
                for r in assessment.validation_results
                if r.component.value == "logging"
            ),
            None,
        )
        if logging_result:
            if logging_result.status == "PASS":
                print("   ✅ Logging infrastructure: SYSTEMATIC COMPLIANCE VERIFIED")
            else:
                print(
                    "   🚨 Logging infrastructure: SYSTEMATIC ISSUES DETECTED (Priority 1)"
                )

        # Check if profiling was validated second
        profiling_result = next(
            (
                r
                for r in assessment.validation_results
                if r.component.value == "profiling"
            ),
            None,
        )
        if profiling_result:
            if profiling_result.status == "PASS":
                print("   ✅ Profiling infrastructure: SYSTEMATIC COMPLIANCE VERIFIED")
            else:
                print(
                    "   🚨 Profiling infrastructure: SYSTEMATIC ISSUES DETECTED (Priority 2)"
                )

        # Overall systematic readiness
        if assessment.critical_issues == 0 and assessment.high_priority_issues == 0:
            print("   ✅ Infrastructure ready for systematic operations")
        else:
            print(
                "   ⚠️ Infrastructure requires systematic remediation before full operations"
            )

        # Save assessment results
        results_file = (
            Path("logs/infrastructure") / f"assessment_{assessment.assessment_id}.json"
        )
        results_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert assessment to JSON-serializable format
        assessment_data = {
            "assessment_id": assessment.assessment_id,
            "overall_compliance_score": assessment.overall_compliance_score,
            "beast_mode_score": assessment.beast_mode_score,
            "systematic_readiness": assessment.systematic_readiness,
            "critical_issues": assessment.critical_issues,
            "high_priority_issues": assessment.high_priority_issues,
            "validation_results": [
                {
                    "component": result.component.value,
                    "status": result.status,
                    "compliance_score": result.systematic_compliance_score,
                    "issues_count": len(result.issues),
                    "recommendations_count": len(result.recommendations),
                }
                for result in assessment.validation_results
            ],
            "remediation_plan": remediation_plan,
        }

        with open(results_file, "w") as f:
            json.dump(assessment_data, f, indent=2, default=str)

        print(f"\n📄 Assessment results saved: {results_file}")

        # Final systematic wisdom
        print(f"\n🐺 Beast Mode Wisdom:")
        print("   'If you can't see it, you can't fix it systematically'")
        print(
            "   'Logging and profiling are the eyes and ears of systematic development'"
        )
        print("   'Always suspect the infrastructure before the application logic'")

        print(f"\n✅ SYSTEMATIC INFRASTRUCTURE VALIDATION COMPLETE")

        # Exit with appropriate code
        if assessment.critical_issues > 0:
            print("🚨 CRITICAL ISSUES DETECTED - Systematic remediation required")
            sys.exit(1)
        elif assessment.high_priority_issues > 0:
            print(
                "⚠️ HIGH PRIORITY ISSUES DETECTED - Systematic improvements recommended"
            )
            sys.exit(0)
        else:
            print("🏆 INFRASTRUCTURE SYSTEMATIC COMPLIANCE ACHIEVED")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Infrastructure validation failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
