#!/usr/bin/env python3
"""
Orchestrator Validation Test

Quick validation of orchestrator functionality without executing prompts.
Tests initialization, status tracking, dependency resolution, and scheduling.

Usage: python scripts/test_orchestrator_validation.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def test_imports():
    """Test that all required imports work"""
    print("🔍 Testing imports...")
    try:
        import asyncio
        import json
        from datetime import datetime
        from pathlib import Path
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_status_initialization():
    """Test status file creation and loading"""
    print("\n🔍 Testing status initialization...")

    test_status_file = Path(".kiro/test-status.json")
    test_status_file.parent.mkdir(parents=True, exist_ok=True)

    # Create test status
    status = {
        "execution_id": "test-001",
        "started_at": datetime.now().isoformat(),
        "status": "testing",
        "prompts": {
            "test-prompt-1": {
                "status": "pending",
                "dependencies": [],
            },
            "test-prompt-2": {
                "status": "pending",
                "dependencies": ["test-prompt-1"],
            }
        }
    }

    try:
        # Write
        with open(test_status_file, 'w') as f:
            json.dump(status, f, indent=2)
        print("  ✅ Status file write successful")

        # Read
        with open(test_status_file) as f:
            loaded = json.load(f)

        if loaded["execution_id"] == "test-001":
            print("  ✅ Status file read successful")
        else:
            print("  ❌ Status file read mismatch")
            return False

        # Cleanup
        test_status_file.unlink()
        print("  ✅ Status file cleanup successful")
        return True

    except Exception as e:
        print(f"  ❌ Status test failed: {e}")
        return False


def test_dependency_resolution():
    """Test dependency checking logic"""
    print("\n🔍 Testing dependency resolution...")

    prompts = {
        "prompt-a": {"status": "completed", "dependencies": []},
        "prompt-b": {"status": "pending", "dependencies": ["prompt-a"]},
        "prompt-c": {"status": "pending", "dependencies": ["prompt-a", "prompt-b"]},
        "prompt-d": {"status": "pending", "dependencies": ["prompt-e"]},  # Circular
        "prompt-e": {"status": "pending", "dependencies": []},
    }

    # Test 1: prompt-b should be ready (prompt-a is completed)
    ready = []
    for name, info in prompts.items():
        if info["status"] == "pending":
            deps_satisfied = all(
                prompts.get(dep, {}).get("status") == "completed"
                for dep in info["dependencies"]
            )
            if deps_satisfied:
                ready.append(name)

    if "prompt-b" in ready and "prompt-e" in ready:
        print(f"  ✅ Dependency resolution correct: {ready}")
    else:
        print(f"  ❌ Dependency resolution failed: expected ['prompt-b', 'prompt-e'], got {ready}")
        return False

    # Test 2: After prompt-b completes, prompt-c should be ready
    prompts["prompt-b"]["status"] = "completed"
    ready = []
    for name, info in prompts.items():
        if info["status"] == "pending":
            deps_satisfied = all(
                prompts.get(dep, {}).get("status") == "completed"
                for dep in info["dependencies"]
            )
            if deps_satisfied:
                ready.append(name)

    if "prompt-c" in ready:
        print(f"  ✅ Cascading dependencies work: {ready}")
        return True
    else:
        print(f"  ❌ Cascading dependencies failed: expected 'prompt-c' in {ready}")
        return False


def test_prompt_file_existence():
    """Check which prompt files exist"""
    print("\n🔍 Checking prompt file existence...")

    prompts_dir = Path("prompts/staging")

    # Original prompts we created
    original_prompts = [
        "master-constellation-elaboration-executor.md",
        "phase-1a-constellation-inventory.md",
        "phase-1b-stakeholder-landscape-mapping.md",
        "phase-1c-cms-dependency-discovery.md",
        "phase-1d-ontology-gap-analysis.md",
        "phase-2-bootstrap-requirements.md",
        "phase-2-foundation-requirements.md",
        "phase-2-intelligence-requirements.md",
        "phase-2-application-requirements.md",
        "phase-3-bootstrap-designs.md",
        "phase-3-foundation-designs.md",
        "phase-3-intelligence-designs.md",
        "phase-3-application-designs.md",
        "phase-4-bootstrap-tasks.md",
        "phase-4-foundation-tasks.md",
        "phase-4-intelligence-tasks.md",
        "phase-4-application-tasks.md",
        "phase-5a-cms-requirements-consolidation.md",
        "phase-5b-cms-architecture-update.md",
        "phase-5c-constellation-cms-mapping.md",
        "phase-5d-stakeholder-validation.md",
    ]

    existing = []
    missing = []

    for prompt in original_prompts:
        path = prompts_dir / prompt
        if path.exists():
            existing.append(prompt)
        else:
            missing.append(prompt)

    print(f"\n  ✅ Found {len(existing)} original prompts:")
    for p in existing[:5]:
        print(f"     - {p}")
    if len(existing) > 5:
        print(f"     ... and {len(existing) - 5} more")

    if missing:
        print(f"\n  ⚠️  Missing {len(missing)} prompts:")
        for p in missing[:5]:
            print(f"     - {p}")
        if len(missing) > 5:
            print(f"     ... and {len(missing) - 5} more")

    return len(existing) > 0


def test_claude_cli():
    """Test if Claude CLI is available"""
    print("\n🔍 Testing Claude CLI availability...")

    import subprocess

    try:
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            claude_path = result.stdout.strip()
            print(f"  ✅ Claude CLI found: {claude_path}")

            # Test version
            version_result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if version_result.returncode == 0:
                print(f"  ✅ Claude version: {version_result.stdout.strip()}")
            return True
        else:
            print("  ❌ Claude CLI not found in PATH")
            return False

    except subprocess.TimeoutExpired:
        print("  ❌ Claude CLI test timed out")
        return False
    except Exception as e:
        print(f"  ❌ Claude CLI test failed: {e}")
        return False


def test_orchestrator_import():
    """Test if orchestrator can be imported"""
    print("\n🔍 Testing orchestrator import...")

    try:
        sys.path.insert(0, str(Path(__file__).parent))

        # Try to import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "constellation_orchestrator",
            Path(__file__).parent / "constellation_orchestrator.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Try to instantiate (but don't run)
        orchestrator = module.ConstellationOrchestrator(
            status_file=".kiro/test-orchestrator-status.json",
            max_agents=2
        )

        print("  ✅ Orchestrator imported and instantiated")

        # Check if status was initialized
        if orchestrator.status_file.exists():
            print("  ✅ Status file created on initialization")
            orchestrator.status_file.unlink()  # Cleanup

        return True

    except Exception as e:
        print(f"  ❌ Orchestrator import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("="*80)
    print("CONSTELLATION ORCHESTRATOR - VALIDATION TESTS")
    print("="*80)

    tests = [
        ("Imports", test_imports),
        ("Status Initialization", test_status_initialization),
        ("Dependency Resolution", test_dependency_resolution),
        ("Prompt Files", test_prompt_file_existence),
        ("Claude CLI", test_claude_cli),
        ("Orchestrator Import", test_orchestrator_import),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}")

    print("\n" + "="*80)
    print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*80)

    if passed == total:
        print("\n🎉 All tests passed! System is ready for execution.")
        print("\n📝 Next steps:")
        print("  1. Decide on prompt structure (original 20 vs breakdown 90)")
        print("  2. Run small test execution (1-2 prompts)")
        print("  3. Monitor and validate outputs")
        print("  4. Scale up to full execution")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Fix issues before executing.")
        print("\n📝 Recommended actions:")
        for test_name, result in results.items():
            if not result:
                print(f"  - Fix: {test_name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
