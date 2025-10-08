#!/usr/bin/env python3
"""
Test script for Prompt Engineering Framework functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beast_mode.observatory.engagement.llm.prompt_framework import (
    PromptEngineering,
    PromptType,
    ContextType
)


async def test_prompt_framework():
    """Test Prompt Engineering Framework functionality."""
    print("🚀 Testing Prompt Engineering Framework...")
    
    # Initialize framework
    framework = PromptEngineering()
    
    print("📋 Initializing framework...")
    success = await framework.initialize()
    if not success:
        print("❌ Failed to initialize framework")
        return False
    
    print("✅ Framework initialized successfully")
    
    # Test attention prioritization prompt
    print("\n🎯 Testing attention prioritization prompt...")
    attention_params = {
        "event_description": "High CPU usage detected on server-01",
        "event_type": "performance_alert",
        "timestamp": datetime.now().isoformat()
    }
    
    attention_prompt = await framework.create_prompt(
        PromptType.ATTENTION_PRIORITIZATION,
        attention_params,
        user_id="test_user"
    )
    
    print(f"✅ Attention prompt created:")
    print(f"   Template: {attention_prompt.template_id}")
    print(f"   Context used: {[c.value for c in attention_prompt.context_used]}")
    print(f"   System prompt length: {len(attention_prompt.system_prompt)} chars")
    print(f"   User prompt preview: {attention_prompt.user_prompt[:100]}...")
    
    # Test animation selection prompt
    print("\n🎨 Testing animation selection prompt...")
    animation_params = {
        "data_type": "time_series",
        "change_magnitude": "high",
        "update_frequency": "real_time",
        "data_importance": "critical"
    }
    
    animation_prompt = await framework.create_prompt(
        PromptType.ANIMATION_SELECTION,
        animation_params,
        user_id="test_user"
    )
    
    print(f"✅ Animation prompt created:")
    print(f"   Template: {animation_prompt.template_id}")
    print(f"   Context used: {[c.value for c in animation_prompt.context_used]}")
    print(f"   User prompt preview: {animation_prompt.user_prompt[:100]}...")
    
    # Test personality analysis prompt
    print("\n🎭 Testing personality analysis prompt...")
    personality_params = {
        "system_events": "Multiple alerts triggered, team collaboration increased",
        "stress_indicators": ["high_alert_frequency", "increased_user_activity"],
        "collaboration_level": "high",
        "current_personality": "professional",
        "current_energy": 0.6,
        "personality_duration": 45
    }
    
    personality_prompt = await framework.create_prompt(
        PromptType.PERSONALITY_ANALYSIS,
        personality_params
    )
    
    print(f"✅ Personality prompt created:")
    print(f"   Template: {personality_prompt.template_id}")
    print(f"   Context used: {[c.value for c in personality_prompt.context_used]}")
    print(f"   User prompt preview: {personality_prompt.user_prompt[:100]}...")
    
    # Test interaction intent prompt
    print("\n👆 Testing interaction intent prompt...")
    interaction_params = {
        "interaction_type": "click",
        "target_element": "dashboard_chart_cpu",
        "interaction_context": "user_exploring_performance_data",
        "interaction_sequence": ["hover", "click", "scroll"],
        "user_experience": "advanced",
        "preferred_interactions": ["keyboard", "detailed_views"],
        "current_focus": "performance_monitoring"
    }
    
    interaction_prompt = await framework.create_prompt(
        PromptType.INTERACTION_INTENT,
        interaction_params,
        user_id="test_user"
    )
    
    print(f"✅ Interaction prompt created:")
    print(f"   Template: {interaction_prompt.template_id}")
    print(f"   Context used: {[c.value for c in interaction_prompt.context_used]}")
    print(f"   User prompt preview: {interaction_prompt.user_prompt[:100]}...")
    
    # Test pattern recognition prompt
    print("\n🔍 Testing pattern recognition prompt...")
    pattern_params = {
        "behavior_data": "User checks dashboard every 5 minutes, prefers detailed views",
        "engagement_history": "High engagement during business hours, low on weekends",
        "performance_data": "Consistent response times, occasional spikes during alerts",
        "time_patterns": "Most active 9-11 AM and 2-4 PM"
    }
    
    pattern_prompt = await framework.create_prompt(
        PromptType.PATTERN_RECOGNITION,
        pattern_params,
        user_id="test_user"
    )
    
    print(f"✅ Pattern prompt created:")
    print(f"   Template: {pattern_prompt.template_id}")
    print(f"   Context used: {[c.value for c in pattern_prompt.context_used]}")
    print(f"   User prompt preview: {pattern_prompt.user_prompt[:100]}...")
    
    # Test framework status
    print("\n📊 Testing framework status...")
    status = await framework.get_framework_status()
    
    print(f"   Total templates: {status['templates']['total']}")
    print(f"   Active templates: {status['templates']['active']}")
    print(f"   Context providers: {len(status['context_providers'])}")
    print(f"   Construction stats: {status['construction_stats']}")
    print(f"   Cache size: {status['cache_size']}")
    
    # Test health monitoring
    print("\n🏥 Testing health monitoring...")
    health = framework.get_health_status()
    print(f"   Status: {health['status']}")
    print(f"   Templates: {health['templates']}")
    print(f"   Context providers: {health['context_providers']}")
    print(f"   Constructions: {health['constructions']}")
    
    # Test graceful degradation
    print("\n🛡️ Testing graceful degradation...")
    degradation_result = framework.graceful_degradation()
    print(f"   Degradation status: {degradation_result['status']}")
    print(f"   Actions taken: {len(degradation_result.get('actions_taken', []))}")
    print(f"   Functionality level: {degradation_result.get('functionality_level', 'unknown')}")
    
    print("\n🎉 All tests completed successfully!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_prompt_framework()
        if success:
            print("\n✅ Prompt Engineering Framework is ready for integration!")
            return 0
        else:
            print("\n❌ Prompt Engineering Framework tests failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)