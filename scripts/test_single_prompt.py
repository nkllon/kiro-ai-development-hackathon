#!/usr/bin/env python3
"""
Single Prompt Execution Test
Tests actual Claude CLI execution with one prompt
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any

async def test_single_prompt_execution(prompt_path: str) -> Dict[str, Any]:
    """Test executing a single prompt with Claude CLI"""
    
    print(f"🧪 Testing Single Prompt Execution")
    print(f"📄 Prompt: {prompt_path}")
    print("=" * 50)
    
    # Validate prompt file exists
    prompt_file = Path(prompt_path)
    if not prompt_file.exists():
        print(f"❌ Prompt file not found: {prompt_path}")
        return {"status": "failed", "error": "File not found"}
    
    print(f"✅ Prompt file exists ({prompt_file.stat().st_size} bytes)")
    
    # Prepare output files
    output_dir = Path("logs/test_execution")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prompt_name = prompt_file.stem
    stdout_file = output_dir / f"{prompt_name}_stdout.log"
    stderr_file = output_dir / f"{prompt_name}_stderr.log"
    
    print(f"📝 Output will be saved to:")
    print(f"   stdout: {stdout_file}")
    print(f"   stderr: {stderr_file}")
    
    # Test Claude CLI availability
    print("\n🔍 Testing Claude CLI availability...")
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Claude CLI available: {result.stdout.strip()}")
        else:
            print(f"⚠️  Claude CLI version check returned {result.returncode}")
            print(f"   stderr: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Claude CLI version check timed out")
        return {"status": "failed", "error": "Claude CLI timeout"}
    except FileNotFoundError:
        print("❌ Claude CLI not found in PATH")
        return {"status": "failed", "error": "Claude CLI not found"}
    except Exception as e:
        print(f"❌ Claude CLI test failed: {e}")
        return {"status": "failed", "error": str(e)}
    
    # Execute the prompt
    print(f"\n🚀 Executing prompt with Claude CLI...")
    print(f"   Command: claude < {prompt_path}")
    
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
                    
                    print(f"   Process started (PID: {process.pid})")
                    print("   Waiting for completion...")
                    
                    # Wait for completion with timeout
                    try:
                        return_code = await asyncio.wait_for(
                            process.wait(), 
                            timeout=3600  # 1 hour timeout
                        )
                    except asyncio.TimeoutError:
                        print("❌ Execution timed out (1 hour)")
                        process.terminate()
                        await process.wait()
                        return {"status": "timeout", "error": "Execution timeout"}
    
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return {"status": "failed", "error": str(e)}
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Check results
    print(f"\n📊 Execution Results:")
    print(f"   Return code: {return_code}")
    print(f"   Execution time: {execution_time:.1f}s")
    
    # Check output files
    stdout_size = stdout_file.stat().st_size if stdout_file.exists() else 0
    stderr_size = stderr_file.stat().st_size if stderr_file.exists() else 0
    
    print(f"   stdout size: {stdout_size} bytes")
    print(f"   stderr size: {stderr_size} bytes")
    
    # Show first few lines of output
    if stdout_size > 0:
        print(f"\n📄 First 10 lines of stdout:")
        with open(stdout_file, 'r') as f:
            lines = f.readlines()[:10]
            for i, line in enumerate(lines, 1):
                print(f"   {i:2d}: {line.rstrip()}")
        
        if len(lines) == 10:
            print(f"   ... ({len(open(stdout_file).readlines()) - 10} more lines)")
    
    if stderr_size > 0:
        print(f"\n⚠️  stderr content:")
        with open(stderr_file, 'r') as f:
            stderr_content = f.read()
            print(f"   {stderr_content}")
    
    # Determine success
    if return_code == 0 and stdout_size > 0:
        print(f"\n✅ SUCCESS: Prompt executed successfully")
        status = "success"
    elif return_code != 0:
        print(f"\n❌ FAILED: Non-zero return code ({return_code})")
        status = "failed"
    elif stdout_size == 0:
        print(f"\n⚠️  WARNING: No output generated")
        status = "warning"
    else:
        print(f"\n❓ UNKNOWN: Unexpected result")
        status = "unknown"
    
    return {
        "status": status,
        "return_code": return_code,
        "execution_time": execution_time,
        "stdout_file": str(stdout_file),
        "stderr_file": str(stderr_file),
        "stdout_size": stdout_size,
        "stderr_size": stderr_size
    }

async def main():
    """Main test runner"""
    
    # Default to a simple existing prompt
    default_prompt = "prompts/staging/phase-1b1-stakeholder-extraction.md"
    
    if len(sys.argv) > 1:
        prompt_path = sys.argv[1]
    else:
        prompt_path = default_prompt
        print(f"No prompt specified, using default: {prompt_path}")
    
    result = await test_single_prompt_execution(prompt_path)
    
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    if result["status"] == "success":
        print("✅ Single prompt execution test PASSED")
        print("🚀 Ready for parallel execution testing")
        return 0
    elif result["status"] == "warning":
        print("⚠️  Single prompt execution test completed with warnings")
        print("🔍 Review output files and investigate")
        return 1
    else:
        print("❌ Single prompt execution test FAILED")
        print("🛠️  Fix issues before proceeding")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)