#!/usr/bin/env python3
"""
Test the execution strategy system to verify local vs cloud agent limits
"""

import sys
import os

sys.path.append("src")

from beast_mode.self_refactoring.execution_strategy import (
    ExecutionStrategySelector,
    ExecutionType,
)


def test_execution_strategy():
    """Test that execution strategies have correct agent limits"""

    print("🧪 Testing Beast Mode Execution Strategy System")
    print("=" * 50)

    selector = ExecutionStrategySelector()

    # Test local strategy (should be 1 agent)
    print("\n📍 Testing Local Strategy:")
    local_strategy = selector.get_local_strategy()
    print(f"   Execution Type: {local_strategy.execution_type.value}")
    print(f"   Max Concurrent Agents: {local_strategy.max_concurrent_agents}")
    print(
        f"   Memory Limit: {local_strategy.resource_allocation['memory_limit_mb']} MB"
    )

    assert local_strategy.execution_type == ExecutionType.LOCAL
    assert (
        local_strategy.max_concurrent_agents == 1
    ), f"Expected 1 agent for local, got {local_strategy.max_concurrent_agents}"

    # Test cloud strategy (should be 4 agents)
    print("\n☁️ Testing Cloud Strategy:")
    cloud_strategy = selector.get_cloud_strategy()
    print(f"   Execution Type: {cloud_strategy.execution_type.value}")
    print(f"   Max Concurrent Agents: {cloud_strategy.max_concurrent_agents}")
    print(
        f"   Memory Limit: {cloud_strategy.resource_allocation['memory_limit_mb']} MB"
    )

    assert cloud_strategy.execution_type == ExecutionType.CLOUD
    assert (
        cloud_strategy.max_concurrent_agents == 4
    ), f"Expected 4 agents for cloud, got {cloud_strategy.max_concurrent_agents}"

    # Test strategy selection logic
    print("\n🎯 Testing Strategy Selection Logic:")

    # Small task count should select local (1 agent)
    strategy = selector.select_strategy(task_count=1, complexity_score=0.2)
    print(
        f"   1 task, low complexity → {strategy.execution_type.value} ({strategy.max_concurrent_agents} agents)"
    )
    assert strategy.execution_type == ExecutionType.LOCAL

    # Large task count should select cloud (4 agents)
    strategy = selector.select_strategy(task_count=5, complexity_score=0.3)
    print(
        f"   5 tasks, medium complexity → {strategy.execution_type.value} ({strategy.max_concurrent_agents} agents)"
    )
    assert strategy.execution_type == ExecutionType.CLOUD

    # High complexity should select cloud (4 agents)
    strategy = selector.select_strategy(task_count=2, complexity_score=0.8)
    print(
        f"   2 tasks, high complexity → {strategy.execution_type.value} ({strategy.max_concurrent_agents} agents)"
    )
    assert strategy.execution_type == ExecutionType.CLOUD

    # No local resources should force cloud (4 agents)
    strategy = selector.select_strategy(
        task_count=1, complexity_score=0.1, local_resources_available=False
    )
    print(
        f"   1 task, no local resources → {strategy.execution_type.value} ({strategy.max_concurrent_agents} agents)"
    )
    assert strategy.execution_type == ExecutionType.CLOUD

    print("\n✅ All execution strategy tests passed!")
    print("\n📋 Summary:")
    print("   • Local execution: 1 agent (conservative for local resources)")
    print("   • Cloud execution: 4 agents (scalable for cloud resources)")
    print("   • Strategy selection works based on task count and complexity")
    print("   • Proper fallback to cloud when local resources unavailable")


if __name__ == "__main__":
    test_execution_strategy()
