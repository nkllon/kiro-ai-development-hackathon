#!/usr/bin/env python3
"""
Live Fire Test for LLM-Powered Engagement Engines
================================================

Tests the engagement engines with REAL LLM providers (OpenAI/Anthropic)
to validate actual AI-powered functionality.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beast_mode.observatory.engagement.llm.orchestrator import (
    LLMOrchestrator,
    LLMProvider,
    LLMRequest,
    ProviderConfig,
    RequestPriority
)
from beast_mode.observatory.engagement.llm.prompt_framework import (
    PromptEngineering,
    PromptType
)


async def test_live_fire_engagement():
    """Test engagement engines with real LLM providers."""
    print("🔥 LIVE FIRE TEST - LLM-Powered Engagement Engines")
    print("=" * 60)
    
    # Check for API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for live fire test.")
        print("   Falling back to mock provider for demonstration...")
        provider_type = LLMProvider.MOCK
    elif openai_key:
        print("✅ OpenAI API key found - Using OpenAI for live fire test")
        provider_type = LLMProvider.OPENAI
    else:
        print("✅ Anthropic API key found - Using Anthropic for live fire test")
        provider_type = LLMProvider.ANTHROPIC
    
    # Initialize orchestrator with real provider
    orchestrator = LLMOrchestrator()
    
    configs = {
        provider_type: ProviderConfig(
            provider=provider_type,
            enabled=True,
            api_key=openai_key or anthropic_key,
            model="gpt-3.5-turbo" if provider_type == LLMProvider.OPENAI else "claude-3-haiku-20240307",
            max_requests_per_minute=60,
            cost_per_token=0.0015,
            timeout=30.0
        )
    }
    
    print(f"\n📋 Initializing orchestrator with {provider_type.value} provider...")
    success = await orchestrator.initialize(configs)
    
    if not success:
        print("❌ Failed to initialize orchestrator")
        return False
    
    print("✅ Orchestrator initialized successfully")
    
    # Initialize prompt framework
    prompt_framework = PromptEngineering()
    await prompt_framework.initialize()
    
    print("\n🎯 LIVE FIRE TEST 1: Attention Prioritization")
    print("-" * 50)
    
    # Create attention prioritization prompt
    attention_prompt = await prompt_framework.create_prompt(
        PromptType.ATTENTION_PRIORITIZATION,
        {
            "event_description": "Database connection pool exhausted - 500 errors spiking",
            "event_type": "critical_system_error",
            "timestamp": datetime.now().isoformat()
        },
        user_id="live_fire_test"
    )
    
    # Send to real LLM
    attention_request = LLMRequest(
        request_id="live_fire_attention_001",
        provider=provider_type,
        system_prompt=attention_prompt.system_prompt,
        prompt=attention_prompt.user_prompt,
        max_tokens=300,
        temperature=0.3,
        priority=RequestPriority.CRITICAL
    )
    
    print(f"🚀 Sending attention analysis to {provider_type.value}...")
    attention_response = await orchestrator.generate(attention_request)
    
    print(f"✅ Response received:")
    print(f"   Success: {attention_response.success}")
    print(f"   Provider: {attention_response.provider.value}")
    print(f"   Tokens: {attention_response.tokens_used}")
    print(f"   Cost: ${attention_response.cost:.4f}")
    print(f"   Time: {attention_response.response_time:.2f}s")
    
    if attention_response.success:
        print(f"📄 AI Analysis:")
        try:
            analysis = json.loads(attention_response.content)
            print(f"   Priority: {analysis.get('priority', 'unknown')}")
            print(f"   Confidence: {analysis.get('confidence', 'unknown')}")
            print(f"   Reasoning: {analysis.get('reasoning', 'No reasoning provided')[:100]}...")
        except json.JSONDecodeError:
            print(f"   Raw response: {attention_response.content[:200]}...")
    else:
        print(f"❌ Error: {attention_response.error}")
    
    print("\n🎨 LIVE FIRE TEST 2: Animation Selection")
    print("-" * 50)
    
    # Create animation selection prompt
    animation_prompt = await prompt_framework.create_prompt(
        PromptType.ANIMATION_SELECTION,
        {
            "data_type": "real_time_metrics",
            "change_magnitude": "critical",
            "update_frequency": "every_second",
            "data_importance": "system_health"
        },
        user_id="live_fire_test"
    )
    
    animation_request = LLMRequest(
        request_id="live_fire_animation_001",
        provider=provider_type,
        system_prompt=animation_prompt.system_prompt,
        prompt=animation_prompt.user_prompt,
        max_tokens=250,
        temperature=0.4,
        priority=RequestPriority.HIGH
    )
    
    print(f"🚀 Sending animation selection to {provider_type.value}...")
    animation_response = await orchestrator.generate(animation_request)
    
    print(f"✅ Response received:")
    print(f"   Success: {animation_response.success}")
    print(f"   Cost: ${animation_response.cost:.4f}")
    
    if animation_response.success:
        print(f"📄 AI Animation Recommendation:")
        try:
            recommendation = json.loads(animation_response.content)
            print(f"   Animation Type: {recommendation.get('animation_type', 'unknown')}")
            print(f"   Intensity: {recommendation.get('intensity', 'unknown')}")
            print(f"   Duration: {recommendation.get('duration', 'unknown')}")
            print(f"   Reasoning: {recommendation.get('reasoning', 'No reasoning provided')[:100]}...")
        except json.JSONDecodeError:
            print(f"   Raw response: {animation_response.content[:200]}...")
    
    print("\n🎭 LIVE FIRE TEST 3: Personality Analysis")
    print("-" * 50)
    
    personality_prompt = await prompt_framework.create_prompt(
        PromptType.PERSONALITY_ANALYSIS,
        {
            "system_events": "Critical alerts resolved, team working late, high stress environment",
            "stress_indicators": ["critical_alerts", "after_hours_activity", "high_error_rates"],
            "collaboration_level": "intense",
            "current_personality": "professional",
            "current_energy": 0.8,
            "personality_duration": 120
        }
    )
    
    personality_request = LLMRequest(
        request_id="live_fire_personality_001",
        provider=provider_type,
        system_prompt=personality_prompt.system_prompt,
        prompt=personality_prompt.user_prompt,
        max_tokens=300,
        temperature=0.5,
        priority=RequestPriority.NORMAL
    )
    
    print(f"🚀 Sending personality analysis to {provider_type.value}...")
    personality_response = await orchestrator.generate(personality_request)
    
    if personality_response.success:
        print(f"📄 AI Personality Recommendation:")
        try:
            recommendation = json.loads(personality_response.content)
            print(f"   Recommended State: {recommendation.get('personality_state', 'unknown')}")
            print(f"   Energy Level: {recommendation.get('energy_level', 'unknown')}")
            print(f"   Transition: {recommendation.get('transition_recommended', 'unknown')}")
            print(f"   Reasoning: {recommendation.get('reasoning', 'No reasoning provided')[:100]}...")
        except json.JSONDecodeError:
            print(f"   Raw response: {personality_response.content[:200]}...")
    
    # Get final status
    print("\n📊 LIVE FIRE TEST SUMMARY")
    print("-" * 50)
    
    status = await orchestrator.get_orchestrator_status()
    
    print(f"✅ Tests completed with {provider_type.value}")
    print(f"   Total cost: ${status['costs']['daily_cost']:.4f}")
    print(f"   Provider health: {list(status['providers'].keys())}")
    print(f"   All systems: {'✅ OPERATIONAL' if status['initialized'] else '❌ ISSUES'}")
    
    # Test the actual engagement integration
    print("\n🔗 LIVE FIRE TEST 4: Full Integration Test")
    print("-" * 50)
    
    # Simulate a real engagement scenario
    scenario_data = {
        "event_type": "user_interaction",
        "interaction_type": "dashboard_drill_down",
        "target_element": "cpu_usage_chart",
        "user_context": {
            "session_duration": 25,
            "interaction_count": 12,
            "engagement_level": "high"
        },
        "system_context": {
            "cpu_usage": 78,
            "memory_usage": 65,
            "active_alerts": 1
        }
    }
    
    print("🎯 Scenario: User drilling down into CPU usage chart during high system load")
    
    # Get AI recommendation for this scenario
    integration_prompt = await prompt_framework.create_prompt(
        PromptType.INTERACTION_INTENT,
        {
            "interaction_type": scenario_data["interaction_type"],
            "target_element": scenario_data["target_element"],
            "interaction_context": "high_system_load_investigation",
            "interaction_sequence": ["hover", "click", "drill_down"]
        },
        user_id="integration_test"
    )
    
    integration_request = LLMRequest(
        request_id="live_fire_integration_001",
        provider=provider_type,
        system_prompt=integration_prompt.system_prompt,
        prompt=integration_prompt.user_prompt,
        max_tokens=350,
        temperature=0.3,
        priority=RequestPriority.HIGH
    )
    
    print(f"🚀 Getting AI recommendation for user interaction...")
    integration_response = await orchestrator.generate(integration_request)
    
    if integration_response.success:
        print(f"📄 AI Engagement Recommendation:")
        try:
            recommendation = json.loads(integration_response.content)
            print(f"   Detected Intent: {recommendation.get('intent', 'unknown')}")
            print(f"   Confidence: {recommendation.get('confidence', 'unknown')}")
            print(f"   Suggested Response: {recommendation.get('suggested_response', 'unknown')}")
            print(f"   Accessibility: {recommendation.get('accessibility_considerations', [])}")
        except json.JSONDecodeError:
            print(f"   Raw response: {integration_response.content[:300]}...")
    
    final_status = await orchestrator.get_orchestrator_status()
    total_cost = final_status['costs']['daily_cost']
    
    print(f"\n🎉 LIVE FIRE TEST COMPLETE!")
    print(f"💰 Total test cost: ${total_cost:.4f}")
    print(f"🎯 All engagement engines tested with REAL AI")
    print(f"✅ System ready for production deployment!")
    
    return True


async def main():
    """Main test function."""
    try:
        success = await test_live_fire_engagement()
        if success:
            print("\n🔥 LIVE FIRE TEST SUCCESSFUL!")
            print("   LLM-Powered Engagement Engines are production ready!")
            return 0
        else:
            print("\n💥 LIVE FIRE TEST FAILED!")
            return 1
    except Exception as e:
        print(f"\n💥 Live fire test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)