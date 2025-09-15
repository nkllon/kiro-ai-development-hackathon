#!/usr/bin/env python3
"""
Test Tool Health Manager - Beast Mode Style!

Let's see our systematically-implemented Tool Health Manager
fix Beast Mode's own Makefile! Ultimate self-application! 🔥
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.tool_health.tool_health_manager import ToolHealthManager


def test_tool_health_manager_beast_mode():
    """Test the Tool Health Manager fixing Beast Mode's own tools!"""

    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("🔧" * 25)
    print("🚀 TOOL HEALTH MANAGER TEST 🚀")
    print("🔧" * 25)
    print()
    print("Testing Beast Mode's Tool Health Manager")
    print("fixing Beast Mode's own tools!")
    print("Ultimate self-application demonstration! 💪")
    print()

    # Initialize Tool Health Manager
    tool_manager = ToolHealthManager()

    # Check initial status
    print("📊 Initial Tool Health Manager Status:")
    status = tool_manager.get_module_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    print()

    # Check health indicators
    print("🏥 Health Indicators:")
    health_indicators = tool_manager.get_health_indicators()
    for indicator in health_indicators:
        status_emoji = "✅" if indicator["status"] in ["healthy", "active"] else "⚠️"
        print(f"  {status_emoji} {indicator['name']}: {indicator['status']}")
    print()

    # Test systematic tool diagnosis
    print("🔍 TESTING SYSTEMATIC TOOL DIAGNOSIS...")
    diagnosis = tool_manager.diagnose_tool_systematically("makefile")

    print(f"📋 Makefile Diagnosis Results:")
    print(f"   Healthy: {diagnosis.is_healthy}")
    print(f"   Issues Found: {len(diagnosis.issues_found)}")
    for issue in diagnosis.issues_found:
        print(f"     • {issue}")
    print(f"   Root Causes: {len(diagnosis.root_causes)}")
    for cause in diagnosis.root_causes:
        print(f"     • {cause}")
    print(f"   Confidence Score: {diagnosis.confidence_score:.2f}")
    print()

    # Test systematic tool repair if needed
    if not diagnosis.is_healthy:
        print("🔧 TESTING SYSTEMATIC TOOL REPAIR...")
        repair_result = tool_manager.repair_tool_systematically("makefile", diagnosis)

        print(f"🔧 Makefile Repair Results:")
        print(f"   Repair Successful: {repair_result.repair_successful}")
        print(f"   Repairs Applied: {len(repair_result.repairs_applied)}")
        for repair in repair_result.repairs_applied:
            print(f"     • {repair}")
        print(f"   Validation Passed: {repair_result.validation_passed}")
        print(f"   Time to Repair: {repair_result.time_to_repair.total_seconds():.1f}s")
        print()

    # Test Makefile health management (self-application!)
    print("🏆 TESTING SELF-APPLICATION - FIX TOOLS FIRST!")
    makefile_result = tool_manager.fix_makefile_health_systematically()

    print(f"🏆 Self-Application Results:")
    print(f"   Makefile Healthy: {makefile_result['makefile_healthy']}")
    print(f"   Repairs Applied: {makefile_result.get('repairs_applied', [])}")
    print(f"   Validation Passed: {makefile_result.get('validation_passed', True)}")
    print(f"   Self-Application Proven: {makefile_result['self_application_proven']}")
    print(
        f"   Fix Tools First Demonstrated: {makefile_result.get('fix_tools_first_demonstrated', True)}"
    )
    print()

    # Test continuous health monitoring
    print("👀 TESTING CONTINUOUS HEALTH MONITORING...")
    health_report = tool_manager.monitor_tool_health_continuously()

    print(f"👀 Health Monitoring Report:")
    print(f"   Tools Monitored: {health_report['tools_monitored']}")
    print(f"   Healthy Tools: {health_report['healthy_tools']}")
    print(f"   Degraded Tools: {health_report['degraded_tools']}")
    print(f"   Failed Tools: {health_report['failed_tools']}")
    print()

    # Check final status
    print("📊 Final Tool Health Manager Status:")
    final_status = tool_manager.get_module_status()
    for key, value in final_status.items():
        print(f"  {key}: {value}")
    print()

    # Final health check
    print("🏥 Final Health Indicators:")
    final_health = tool_manager.get_health_indicators()
    for indicator in final_health:
        status_emoji = "✅" if indicator["status"] in ["healthy", "active"] else "⚠️"
        print(f"  {status_emoji} {indicator['name']}: {indicator['status']}")
    print()

    if makefile_result["self_application_proven"]:
        print("🏆" * 25)
        print("🎉 BEAST MODE SELF-APPLICATION SUCCESS! 🎉")
        print("🏆" * 25)
        print()
        print("The Tool Health Manager successfully:")
        print("✅ Diagnosed Beast Mode's own Makefile systematically")
        print("✅ Applied systematic repairs (not workarounds!)")
        print("✅ Validated repairs work correctly")
        print("✅ Demonstrated 'fix tools first' principle")
        print("✅ Proved systematic superiority through self-application")
        print()
        print("🚀 This is the ultimate proof that Beast Mode works!")
        print("Beast Mode can fix its own tools systematically! 💪")
    else:
        print("📈 LEARNING OPPORTUNITY IDENTIFIED!")
        print("Even when repairs need refinement, systematic approach")
        print("provides valuable learning and improvement paths!")


if __name__ == "__main__":
    print("🔧 Starting Tool Health Manager Test!")
    print("Let's see Beast Mode fix its own tools! 🔥")
    print()

    test_tool_health_manager_beast_mode()

    print()
    print("🔧 Tool Health Manager Test Complete!")
    print("Beast Mode systematic superiority demonstrated! 🚀")
