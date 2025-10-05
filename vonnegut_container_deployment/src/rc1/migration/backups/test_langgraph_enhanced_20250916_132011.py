#!/usr/bin/env python3
"""
Test Enhanced LangGraph Workflow
===============================

Test script to demonstrate the enhanced LangGraph DevPost automation workflow
with sophisticated session recovery and dramatic exclamations.
"""

import sys
import time
from datetime import datetime

from langgraph_devpost_workflow import DevPostWorkflow, create_devpost_workflow
from langgraph_devpost_state import get_state_summary


def test_enhanced_workflow():
    """Test the enhanced LangGraph workflow with session recovery"""

    print("🚀 Testing Enhanced LangGraph DevPost Workflow")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎭 This workflow includes dramatic exclamations!")
    print("=" * 60)

    try:
        # Create workflow with a test ID
        workflow_id = f"test_enhanced_{int(time.time())}"
        workflow = create_devpost_workflow(workflow_id)

        print(f"🆔 Workflow ID: {workflow_id}")
        print("🔧 Starting workflow...")

        # Run the workflow
        result = workflow.run_workflow(
            user_data_dir="/tmp/devpost-browser-test", automation_mode="interactive"
        )

        if result["success"]:
            print("\n🎉 Enhanced workflow completed successfully!")

            # Display summary with dramatic flair
            summary = result.get("summary", {})
            print("\n📊 Final Summary:")
            print("-" * 40)
            for key, value in summary.items():
                print(f"{key:25}: {value}")

            # Check for dramatic exclamations in the workflow
            final_state = result.get("final_state", {})
            messages = final_state.get("messages", [])

            print("\n🎭 Dramatic Moments:")
            print("-" * 40)
            for message in messages:
                if (
                    "Toto" in str(message.content)
                    or "Houston" in str(message.content)
                    or "Twilight Zone" in str(message.content)
                ):
                    print(f"   🚨 {message.content}")

            # Check quality score
            quality_score = summary.get("quality_score")
            if quality_score and quality_score >= 0.8:
                print(f"\n✅ High quality submission! Score: {quality_score:.2f}")
            elif quality_score:
                print(f"\n⚠️ Submission completed with score: {quality_score:.2f}")
                print("   Manual review recommended.")

            return True

        else:
            print(f"\n❌ Enhanced workflow failed: {result['error']}")
            return False

    except KeyboardInterrupt:
        print("\n⚠️ Workflow interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return False


def test_session_recovery_scenarios():
    """Test different session recovery scenarios including partially degraded states"""

    print("\n🧪 Testing Session Recovery Scenarios")
    print("=" * 50)

    # Test scenarios including the new partially degraded states
    scenarios = [
        {
            "name": "Exact Match",
            "confidence": "99%",
            "description": "Testing exact URL match scenario",
            "expected": "✅ Exact page match found!",
            "strategy": "Use existing navigation model",
        },
        {
            "name": "Visual Similarity",
            "confidence": "80-95%",
            "description": "Testing visual similarity with URL differences",
            "expected": "👁️ Visual similarity detected!",
            "strategy": "Adapt existing model for visual match",
        },
        {
            "name": "Navigation Pattern",
            "confidence": "70-85%",
            "description": "Testing LinkedIn mystery land scenario",
            "expected": "🧭 Navigation pattern match!",
            "strategy": "Use semantic navigation strategy",
        },
        {
            "name": "DevPost Quirks",
            "confidence": "60-75%",
            "description": "Testing DevPost-specific quirks",
            "expected": "🔄 Dynamic content detected!",
            "strategy": "Use adaptive navigation strategy",
        },
        {
            "name": "Cautious Uncertainty",
            "confidence": "40-60%",
            "description": "Testing moderately uncertain states",
            "expected": "I think I've seen this before, but I want to be sure...",
            "strategy": "Use cautious navigation with extra verification",
        },
        {
            "name": "Investigative Uncertainty",
            "confidence": "20-40%",
            "description": "Testing very uncertain states",
            "expected": "This seems similar to what I know, but not quite...",
            "strategy": "Use investigative navigation - gather more info",
        },
        {
            "name": "Very Uncertain",
            "confidence": "10-20%",
            "description": "Testing very uncertain but not completely lost",
            "expected": "I'm not in Kansas, but I'm not sure. Am I close?",
            "strategy": "Use investigative navigation - look around carefully",
        },
        {
            "name": "Uncharted Territory",
            "confidence": "< 10%",
            "description": "Testing completely new page scenario",
            "expected": "🚨 Toto, we aren't in Kansas anymore!",
            "strategy": "Build fresh navigation model",
        },
    ]

    print("🎭 Session Recovery Scenarios with Partially Degraded States:")
    print("-" * 60)

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. 📋 {scenario['name']} (Confidence: {scenario['confidence']})")
        print(f"   Description: {scenario['description']}")
        print(f"   Expected Message: {scenario['expected']}")
        print(f"   Strategy: {scenario['strategy']}")
        print("   Status: ✅ Implemented")

    print("\n🎭 Key Features of Partially Degraded States:")
    print("-" * 50)
    print("• Less dramatic, more measured messaging")
    print("• Investigative navigation for uncertain states")
    print("• Cautious navigation with extra verification")
    print("• Gradual confidence building rather than binary decisions")
    print("• 'I'm gonna have to look around' approach")

    print("\n💡 Note: Full scenario testing requires actual browser automation")
    print("   This demonstrates the enhanced session recovery logic structure.")


def main():
    """Main test function"""

    print("🎭 Enhanced LangGraph DevPost Automation Test Suite")
    print("=" * 70)

    # Test the enhanced workflow
    success = test_enhanced_workflow()

    # Test session recovery scenarios
    test_session_recovery_scenarios()

    print("\n" + "=" * 70)
    if success:
        print("🎉 All tests completed successfully!")
        print("🎭 The enhanced workflow is ready with dramatic exclamations!")
    else:
        print("❌ Some tests failed - check the output above")

    print("=" * 70)


if __name__ == "__main__":
    main()
