#!/usr/bin/env python3
"""
Test script for LLM Orchestrator functionality.
"""

import asyncio
import sys
import os
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


async def test_llm_orchestrator():
    """Test LLM Orchestrator functionality."""
    print("🚀 Testing LLM Orchestrator...")
    
    # Initialize orchestrator
    orchestrator = LLMOrchestrator()
    
    print("📋 Initializing orchestrator...")
    
    # Configure with mock provider
    configs = {
        LLMProvider.MOCK: ProviderConfig(
            provider=LLMProvider.MOCK,
            enabled=True,
            model="mock-gpt-4",
            max_requests_per_minute=100,
            cost_per_token=0.001
        )
    }
    
    success = await orchestrator.initialize(configs)
    if not success:
        print("❌ Failed to initialize orchestrator")
        return False
    
    print("✅ Orchestrator initialized successfully")
    
    # Test attention prioritization request
    print("\n🎯 Testing attention prioritization...")
    attention_request = LLMRequest(
        request_id="attention_test_001",
        provider=LLMProvider.MOCK,
        prompt="""Analyze this event for attention priority:

Event: High CPU usage detected on server-01
Event Type: performance_alert
Timestamp: 2025-10-02T07:30:00Z

System Context:
- CPU Usage: 85%
- Memory Usage: 67%
- Active Users: 3
- Current Alerts: 2

User Context:
- Session Duration: 45 minutes
- Interaction Count: 23
- Engagement Level: high

Determine the priority level (low, medium, high, critical) and provide reasoning.""",
        max_tokens=300,
        temperature=0.3,
        priority=RequestPriority.HIGH
    )
    
    attention_response = await orchestrator.generate(attention_request)
    
    print(f"✅ Attention analysis response:")
    print(f"   Success: {attention_response.success}")
    print(f"   Provider: {attention_response.provider.value}")
    print(f"   Tokens used: {attention_response.tokens_used}")
    print(f"   Cost: ${attention_response.cost:.4f}")
    print(f"   Response time: {attention_response.response_time:.3f}s")
    print(f"   Content preview: {attention_response.content[:100]}...")
    
    # Test animation selection request
    print("\n🎨 Testing animation selection...")
    animation_request = LLMRequest(
        request_id="animation_test_001",
        prompt="""Select appropriate animation for this data update:

Data Characteristics:
- Data Type: time_series
- Change Magnitude: high
- Update Frequency: real_time
- Data Importance: critical

System Performance:
- CPU Usage: 45%
- GPU Available: true
- Performance Budget: 16.67ms

User Context:
- Attention Level: high
- Preferred Complexity: medium
- Accessibility Needs: keyboard_navigation

Recommend animation type, intensity (0.0-1.0), and duration.""",
        max_tokens=250,
        temperature=0.4,
        priority=RequestPriority.NORMAL
    )
    
    animation_response = await orchestrator.generate(animation_request)
    
    print(f"✅ Animation selection response:")
    print(f"   Success: {animation_response.success}")
    print(f"   Content preview: {animation_response.content[:100]}...")
    
    # Test personality analysis request
    print("\n🎭 Testing personality analysis...")
    personality_request = LLMRequest(
        request_id="personality_test_001",
        prompt="""Analyze the current situation for personality adaptation:

System Events:
Multiple alerts triggered, team collaboration increased

Team Context:
- Active Users: 3
- Stress Indicators: high_alert_frequency, increased_user_activity
- Collaboration Level: high

Current Personality:
- State: professional
- Energy Level: 0.6
- Duration: 45 minutes

Observatory Metrics:
- Alert Count: 2
- System Health: good
- Performance Score: 0.85

Recommend personality state and energy level.""",
        max_tokens=300,
        temperature=0.5,
        priority=RequestPriority.NORMAL
    )
    
    personality_response = await orchestrator.generate(personality_request)
    
    print(f"✅ Personality analysis response:")
    print(f"   Success: {personality_response.success}")
    print(f"   Content preview: {personality_response.content[:100]}...")
    
    # Test batch processing
    print("\n📦 Testing batch processing...")
    batch_requests = [
        LLMRequest(
            request_id=f"batch_test_{i:03d}",
            prompt=f"Quick analysis of event {i}: System metric changed by {i*10}%",
            max_tokens=100,
            temperature=0.3
        ) for i in range(1, 4)
    ]
    
    batch_responses = await orchestrator.batch_generate(batch_requests)
    
    print(f"✅ Batch processing completed:")
    print(f"   Requests processed: {len(batch_responses)}")
    print(f"   All successful: {all(r.success for r in batch_responses)}")
    
    # Test orchestrator status
    print("\n📊 Testing orchestrator status...")
    status = await orchestrator.get_orchestrator_status()
    
    print(f"   Initialized: {status['initialized']}")
    print(f"   Active requests: {status['active_requests']}")
    print(f"   Providers: {len(status['providers'])}")
    print(f"   Daily cost: ${status['costs']['daily_cost']:.4f}")
    print(f"   Monthly cost: ${status['costs']['monthly_cost']:.4f}")
    
    # Test health monitoring
    print("\n🏥 Testing health monitoring...")
    health = orchestrator.get_health_status()
    print(f"   Status: {health['status']}")
    print(f"   Providers: {health['providers']}")
    print(f"   Active requests: {health['active_requests']}")
    
    # Test graceful degradation
    print("\n🛡️ Testing graceful degradation...")
    degradation_result = orchestrator.graceful_degradation()
    print(f"   Degradation status: {degradation_result['status']}")
    print(f"   Actions taken: {len(degradation_result.get('actions_taken', []))}")
    print(f"   Functionality level: {degradation_result.get('functionality_level', 'unknown')}")
    
    print("\n🎉 All orchestrator tests completed successfully!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_llm_orchestrator()
        if success:
            print("\n✅ LLM Orchestrator is ready for production!")
            return 0
        else:
            print("\n❌ LLM Orchestrator tests failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)