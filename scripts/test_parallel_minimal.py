#!/usr/bin/env python3
"""
Minimal Parallel Execution Test
Tests concurrent execution of 2-3 prompts
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

async def execute_prompt_async(prompt_path: str, agent_id: int) -> Dict[str, Any]:
    """Execute a single prompt asynchronously"""
    
    prompt_file = Path(prompt_path)
    if not prompt_file.exists():
        return {
            "agent_id": agent_id,
            "prompt": prompt_path,
            "status": "failed",
            "error": "File not found"
        }
    
    # Prepare output files
    output_dir = Path("logs/test_parallel")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prompt_name = prompt_file.stem
    stdout_file = output_dir / f"agent{agent_id}_{prompt_name}_stdout.log"
    stderr_file = output_dir / f"agent{agent_id}_{prompt_name}_stderr.log"
    
    print(f"🤖 Agent {agent_id}: Starting {prompt_name}")
    
    start_time = time.time()
    
    try:
        with open(prompt_file, 'r') as stdin_file:
            with open(stdout_file, 'w') as stdout_f:
                with open(stderr_file, 'w') as stderr_f:
                    
                    process = await asyncio.create_subprocess_exec(
                        "claude",
                        stdin=stdin_file,
                        stdout=stdout_f,
                        stderr=stderr_f
                    )
                    
                    # Wait for completion with timeout
                    try:
                        return_code = await asyncio.wait_for(
                            process.wait(), 
                            timeout=1800  # 30 minute timeout per prompt
                        )
                    except asyncio.TimeoutError:
                        print(f"❌ Agent {agent_id}: Timeout")
                        process.terminate()
                        await process.wait()
                        return {
                            "agent_id": agent_id,
                            "prompt": prompt_path,
                            "status": "timeout",
                            "error": "Execution timeout"
                        }
    
    except Exception as e:
        print(f"❌ Agent {agent_id}: Failed - {e}")
        return {
            "agent_id": agent_id,
            "prompt": prompt_path,
            "status": "failed",
            "error": str(e)
        }
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Check output
    stdout_size = stdout_file.stat().st_size if stdout_file.exists() else 0
    stderr_size = stderr_file.stat().st_size if stderr_file.exists() else 0
    
    if return_code == 0 and stdout_size > 0:
        status = "success"
        print(f"✅ Agent {agent_id}: Completed {prompt_name} in {execution_time:.1f}s")
    else:
        status = "failed"
        print(f"❌ Agent {agent_id}: Failed {prompt_name} (rc={return_code}, out={stdout_size})")
    
    return {
        "agent_id": agent_id,
        "prompt": prompt_path,
        "status": status,
        "return_code": return_code,
        "execution_time": execution_time,
        "stdout_file": str(stdout_file),
        "stderr_file": str(stderr_file),
        "stdout_size": stdout_size,
        "stderr_size": stderr_size
    }

async def test_parallel_execution(prompt_paths: List[str], max_agents: int = 3) -> Dict[str, Any]:
    """Test parallel execution of multiple prompts"""
    
    print(f"🧪 Testing Parallel Execution")
    print(f"📄 Prompts: {len(prompt_paths)}")
    print(f"🤖 Max agents: {max_agents}")
    print("=" * 50)
    
    # Validate all prompt files exist
    valid_prompts = []
    for prompt_path in prompt_paths:
        if Path(prompt_path).exists():
            valid_prompts.append(prompt_path)
            print(f"✅ {prompt_path}")
        else:
            print(f"❌ {prompt_path} - NOT FOUND")
    
    if not valid_prompts:
        print("❌ No valid prompts found")
        return {"status": "failed", "error": "No valid prompts"}
    
    print(f"\n🚀 Executing {len(valid_prompts)} prompts in parallel...")
    
    # Create semaphore to limit concurrent executions
    semaphore = asyncio.Semaphore(max_agents)
    
    async def execute_with_semaphore(prompt_path: str, agent_id: int):
        async with semaphore:
            return await execute_prompt_async(prompt_path, agent_id)
    
    # Start all executions
    start_time = time.time()
    
    tasks = [
        execute_with_semaphore(prompt_path, i + 1)
        for i, prompt_path in enumerate(valid_prompts)
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Process results
    successful = 0
    failed = 0
    total_execution_time = 0
    
    print(f"\n📊 Execution Results:")
    print(f"   Total wall time: {total_time:.1f}s")
    
    for result in results:
        if isinstance(result, Exception):
            print(f"   ❌ Exception: {result}")
            failed += 1
        elif result["status"] == "success":
            successful += 1
            total_execution_time += result["execution_time"]
            print(f"   ✅ Agent {result['agent_id']}: {result['execution_time']:.1f}s")
        else:
            failed += 1
            print(f"   ❌ Agent {result['agent_id']}: {result['status']}")
    
    # Calculate efficiency
    if successful > 0:
        avg_execution_time = total_execution_time / successful
        theoretical_sequential_time = avg_execution_time * len(valid_prompts)
        speedup = theoretical_sequential_time / total_time if total_time > 0 else 0
        
        print(f"\n📈 Performance Analysis:")
        print(f"   Average execution time: {avg_execution_time:.1f}s")
        print(f"   Theoretical sequential: {theoretical_sequential_time:.1f}s")
        print(f"   Actual parallel time: {total_time:.1f}s")
        print(f"   Speedup: {speedup:.1f}x")
        print(f"   Efficiency: {(speedup / max_agents) * 100:.1f}%")
    
    return {
        "status": "success" if failed == 0 else "partial" if successful > 0 else "failed",
        "total_prompts": len(valid_prompts),
        "successful": successful,
        "failed": failed,
        "total_time": total_time,
        "results": [r for r in results if not isinstance(r, Exception)]
    }

async def main():
    """Main test runner"""
    
    # Default test prompts (use existing ones)
    default_prompts = [
        "prompts/staging/phase-1b1-stakeholder-extraction.md",
        "prompts/staging/phase-1c-cms-dependency-discovery.md",
        "prompts/staging/phase-1d-ontology-gap-analysis.md"
    ]
    
    # Check which prompts actually exist
    existing_prompts = [p for p in default_prompts if Path(p).exists()]
    
    if len(existing_prompts) < 2:
        print("❌ Need at least 2 existing prompts for parallel test")
        print("Available prompts:")
        for prompt in default_prompts:
            exists = "✅" if Path(prompt).exists() else "❌"
            print(f"  {exists} {prompt}")
        return 1
    
    # Use first 2-3 existing prompts
    test_prompts = existing_prompts[:3]
    
    print(f"Testing with {len(test_prompts)} prompts:")
    for prompt in test_prompts:
        print(f"  📄 {prompt}")
    
    result = await test_parallel_execution(test_prompts, max_agents=2)
    
    print("\n" + "=" * 50)
    print("🏁 PARALLEL TEST SUMMARY")
    print("=" * 50)
    
    if result["status"] == "success":
        print("✅ Parallel execution test PASSED")
        print(f"   All {result['successful']} prompts completed successfully")
        print("🚀 Ready for full orchestrator testing")
        return 0
    elif result["status"] == "partial":
        print("⚠️  Parallel execution test PARTIAL SUCCESS")
        print(f"   {result['successful']} succeeded, {result['failed']} failed")
        print("🔍 Review failed executions before proceeding")
        return 1
    else:
        print("❌ Parallel execution test FAILED")
        print(f"   All {result['failed']} prompts failed")
        print("🛠️  Fix issues before proceeding")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)