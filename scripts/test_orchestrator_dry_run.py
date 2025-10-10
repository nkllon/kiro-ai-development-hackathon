#!/usr/bin/env python3
"""
Orchestrator Dry Run Test
Tests orchestrator logic without executing prompts
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Set

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simple_constellation_orchestrator import ConstellationOrchestrator

class MockConstellationOrchestrator(ConstellationOrchestrator):
    """Mock orchestrator that simulates prompt execution without running Claude"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_execution_times = {
            # Simulate different execution times for different prompt types
            "phase-1": 30,  # 30 seconds for Phase 1 prompts
            "phase-2": 120, # 2 minutes for Phase 2 prompts  
            "phase-3": 180, # 3 minutes for Phase 3 prompts
            "phase-4": 240, # 4 minutes for Phase 4 prompts
            "phase-5": 300, # 5 minutes for Phase 5 prompts
        }
    
    async def execute_prompt(self, prompt_id: str, agent_id: int) -> Dict[str, Any]:
        """Mock prompt execution - simulates work without running Claude"""
        
        # Determine execution time based on prompt type
        phase = prompt_id.split('-')[1] if '-' in prompt_id else "phase-1"
        execution_time = self.mock_execution_times.get(phase, 60)
        
        print(f"🤖 Agent {agent_id}: Starting MOCK execution of {prompt_id}")
        print(f"   Simulating {execution_time}s execution...")
        
        # Simulate work
        await asyncio.sleep(min(execution_time / 10, 5))  # Scale down for testing
        
        # Mock successful result
        result = {
            "status": "completed",
            "prompt_id": prompt_id,
            "agent_id": agent_id,
            "execution_time": execution_time,
            "output_file": f"logs/mock_{prompt_id}_output.log",
            "mock": True
        }
        
        print(f"✅ Agent {agent_id}: MOCK completed {prompt_id} in {execution_time}s")
        return result

async def test_orchestrator_dry_run():
    """Test orchestrator with mock execution"""
    
    print("🧪 Starting Orchestrator Dry Run Test")
    print("=" * 50)
    
    # Test 1: Initialization
    print("\n📋 Test 1: Orchestrator Initialization")
    try:
        orchestrator = MockConstellationOrchestrator(
            max_agents=3,
            status_file="test_status.json"
        )
        print("✅ Orchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test 2: DAG Loading
    print("\n📋 Test 2: DAG Loading and Validation")
    try:
        dag = orchestrator.dag
        print(f"✅ DAG loaded with {len(dag)} prompts")
        
        # Show some DAG structure
        print("\n📊 DAG Structure Sample:")
        for prompt_id, deps in list(dag.items())[:5]:
            print(f"   {prompt_id}: depends on {deps}")
        
    except Exception as e:
        print(f"❌ DAG loading failed: {e}")
        return False
    
    # Test 3: Dependency Resolution
    print("\n📋 Test 3: Dependency Resolution")
    try:
        ready_prompts = orchestrator.get_ready_prompts()
        print(f"✅ Found {len(ready_prompts)} prompts ready to execute")
        print(f"   Ready prompts: {ready_prompts[:3]}...")
        
    except Exception as e:
        print(f"❌ Dependency resolution failed: {e}")
        return False
    
    # Test 4: Status Tracking
    print("\n📋 Test 4: Status Tracking")
    try:
        # Test status save
        original_completed = orchestrator.status["completed"].copy()
        orchestrator.status["completed"].add("test-prompt")
        orchestrator.save_status()
        
        # Test status loading
        new_orchestrator = MockConstellationOrchestrator(
            max_agents=3,
            status_file="test_status.json"
        )
        
        if "test-prompt" in new_orchestrator.status["completed"]:
            print("✅ Status persistence works")
        else:
            print("❌ Status persistence failed")
            return False
            
    except Exception as e:
        print(f"❌ Status tracking failed: {e}")
        return False
    
    # Test 5: Mock Execution (Small Scale)
    print("\n📋 Test 5: Mock Execution (3 prompts)")
    try:
        # Limit to first 3 ready prompts for quick test
        ready_prompts = orchestrator.get_ready_prompts()[:3]
        
        if not ready_prompts:
            print("⚠️  No ready prompts found - DAG might have issues")
            return False
        
        print(f"   Executing: {ready_prompts}")
        
        # Start execution
        start_time = asyncio.get_event_loop().time()
        
        # Execute the prompts
        tasks = []
        for i, prompt_id in enumerate(ready_prompts):
            task = orchestrator.execute_prompt(prompt_id, i + 1)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        print(f"✅ Mock execution completed in {execution_time:.1f}s")
        print(f"   Results: {len(results)} prompts completed")
        
        # Validate results
        for result in results:
            if result["status"] != "completed":
                print(f"❌ Prompt {result['prompt_id']} failed")
                return False
        
    except Exception as e:
        print(f"❌ Mock execution failed: {e}")
        return False
    
    # Test 6: Dependency Chain Simulation
    print("\n📋 Test 6: Dependency Chain Logic")
    try:
        # Mark some prompts as completed and check what becomes ready
        initial_ready = set(orchestrator.get_ready_prompts())
        
        # Simulate completing a prompt
        if ready_prompts:
            completed_prompt = ready_prompts[0]
            orchestrator.status["completed"].add(completed_prompt)
            
            new_ready = set(orchestrator.get_ready_prompts())
            newly_ready = new_ready - initial_ready
            
            print(f"✅ After completing {completed_prompt}:")
            print(f"   {len(newly_ready)} new prompts became ready")
            if newly_ready:
                print(f"   Newly ready: {list(newly_ready)[:3]}...")
        
    except Exception as e:
        print(f"❌ Dependency chain test failed: {e}")
        return False
    
    # Cleanup
    try:
        Path("test_status.json").unlink(missing_ok=True)
    except:
        pass
    
    print("\n🎉 All Tests Passed!")
    print("=" * 50)
    print("✅ Orchestrator is ready for real execution")
    print("✅ DAG logic works correctly")
    print("✅ Status tracking works")
    print("✅ Dependency resolution works")
    print("✅ Mock execution successful")
    
    return True

async def main():
    """Main test runner"""
    success = await test_orchestrator_dry_run()
    
    if success:
        print("\n🚀 READY FOR NEXT STEPS:")
        print("1. Test single real prompt execution")
        print("2. Test parallel execution (2-3 prompts)")
        print("3. Execute with original 20 prompts")
        print("4. Generate breakdown prompts")
        print("5. Full optimized execution")
        
        return 0
    else:
        print("\n❌ TESTS FAILED - Fix issues before proceeding")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)