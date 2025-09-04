#!/usr/bin/env python3
"""
Test script for Git integration in Task Execution Engine
"""

import subprocess
import sys
from datetime import datetime

def run_git_command(command):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(['git'] + command, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def test_git_integration():
    """Test the Git integration functionality"""
    print("🧪 Testing Git Integration for Task Execution Engine")
    print("=" * 60)
    
    # Check if we're in a git repository
    success, output = run_git_command(['status'])
    if not success:
        print("❌ Not in a Git repository. Please run this test from a Git repository.")
        return False
    
    print("✅ Git repository detected")
    
    # Get current branch
    success, current_branch = run_git_command(['branch', '--show-current'])
    if not success:
        print("❌ Could not determine current branch")
        return False
    
    print(f"📍 Current branch: {current_branch}")
    
    # Test dry run first
    print("\n🔍 Testing dry run execution...")
    try:
        from cli import cli
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, ['execute', '--dry-run', '--branch', 'test-git-integration'])
        
        if result.exit_code == 0:
            print("✅ Dry run completed successfully")
            print("Output preview:")
            print(result.output[:500] + "..." if len(result.output) > 500 else result.output)
        else:
            print(f"❌ Dry run failed with exit code {result.exit_code}")
            print(f"Error: {result.output}")
            return False
            
    except Exception as e:
        print(f"❌ Error during dry run test: {e}")
        return False
    
    print("\n✅ Git integration test completed successfully!")
    print("\nTo test full execution with Git integration, run:")
    print("python cli.py execute --branch my-test-branch --simulate")
    
    return True

if __name__ == "__main__":
    success = test_git_integration()
    sys.exit(0 if success else 1)