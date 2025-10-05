#!/usr/bin/env python3
"""
Single Prompt Execution Test

Tests end-to-end execution with one prompt to validate:
- Claude CLI integration
- Subprocess execution
- stdin handling
- stdout/stderr capture
- Status tracking
- File logging

Usage: python scripts/test_single_prompt.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime


async def test_single_prompt():
    """Execute single prompt and validate results"""

    print("=" * 80)
    print("SINGLE PROMPT EXECUTION TEST")
    print("=" * 80)

    # Configuration
    test_prompt = "phase-1a-constellation-inventory"
    prompts_dir = Path("prompts/staging")
    prompt_file = prompts_dir / f"{test_prompt}.md"

    # Output configuration
    logs_dir = Path(".kiro/test-execution-logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    output_file = logs_dir / f"{test_prompt}.out"
    error_file = logs_dir / f"{test_prompt}.err"
    status_file = Path(".kiro/test-execution-status.json")

    # Verify prompt exists
    if not prompt_file.exists():
        print(f"❌ Prompt file not found: {prompt_file}")
        return False

    print(f"\n📝 Test Prompt: {test_prompt}")
    print(f"📂 Prompt File: {prompt_file}")
    print(f"📊 Output File: {output_file}")
    print(f"📊 Error File: {error_file}")
    print(f"📊 Status File: {status_file}")

    # Initialize status
    status = {
        "execution_id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "started_at": datetime.now().isoformat(),
        "status": "running",
        "prompt": test_prompt,
        "prompt_file": str(prompt_file),
        "output_file": str(output_file),
        "error_file": str(error_file),
    }

    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)

    print("\n🚀 Starting execution...")
    print("⏱️  This will take 2-3 hours for constellation inventory prompt")
    print("💡 You can monitor progress by checking the output file:")
    print(f"   tail -f {output_file}\n")

    start_time = datetime.now()

    try:
        # Execute Claude with prompt
        with open(prompt_file, 'r') as stdin_file:
            with open(output_file, 'w') as stdout_file:
                with open(error_file, 'w') as stderr_file:
                    print(f"🔄 Executing: claude < {prompt_file}")
                    print(f"⏰ Started: {start_time.strftime('%H:%M:%S')}\n")

                    proc = await asyncio.create_subprocess_exec(
                        "claude",
                        stdin=stdin_file,
                        stdout=stdout_file,
                        stderr=stderr_file,
                    )

                    # Wait for completion
                    returncode = await proc.wait()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60

        # Update status
        status["completed_at"] = end_time.isoformat()
        status["duration_min"] = duration
        status["returncode"] = returncode
        status["status"] = "completed" if returncode == 0 else "failed"

        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)

        print("\n" + "=" * 80)
        print("EXECUTION COMPLETE")
        print("=" * 80)
        print(f"⏱️  Duration: {duration:.1f} minutes ({duration/60:.1f} hours)")
        print(f"🔄 Return Code: {returncode}")
        print(f"📊 Status: {status['status']}")

        # Check outputs
        output_size = output_file.stat().st_size if output_file.exists() else 0
        error_size = error_file.stat().st_size if error_file.exists() else 0

        print(f"\n📂 Output File: {output_file} ({output_size:,} bytes)")
        print(f"📂 Error File: {error_file} ({error_size:,} bytes)")

        if returncode == 0:
            print("\n✅ TEST PASSED")
            print("\n📝 Next steps:")
            print("  1. Review output file to validate content")
            print("  2. Check that expected artifacts were created")
            print("  3. If satisfied, proceed with parallel execution")
            return True
        else:
            print("\n❌ TEST FAILED")
            print("\n📝 Check error file for details:")
            print(f"   cat {error_file}")
            return False

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60

        status["completed_at"] = end_time.isoformat()
        status["duration_min"] = duration
        status["status"] = "failed"
        status["error"] = str(e)

        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)

        print(f"\n❌ EXECUTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run single prompt test"""
    print("🧪 Single Prompt Execution Test\n")
    print("This test will:")
    print("  1. Execute phase-1a-constellation-inventory.md")
    print("  2. Capture output to .kiro/test-execution-logs/")
    print("  3. Track status in .kiro/test-execution-status.json")
    print("  4. Validate end-to-end execution works\n")

    response = input("⚠️  This will take 2-3 hours. Continue? [y/N]: ")
    if response.lower() != 'y':
        print("❌ Test cancelled")
        return 1

    result = asyncio.run(test_single_prompt())
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
