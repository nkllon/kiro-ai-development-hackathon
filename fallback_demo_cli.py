#!/usr/bin/env python3
"""
Fallback Demo CLI
=================

Interactive CLI to demonstrate the fallback mechanisms when the system
cannot perform field modifications due to registry issues.
"""

import sys
import os
from pathlib import Path
import tempfile
import subprocess

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from field_repair_modification_system import (
    create_field_modification_system,
    FieldModificationRequest,
    FieldModificationFallbackResult
)
from datetime import datetime


def simulate_registry_failure():
    """Simulate a registry failure scenario"""
    
    print("🎭 SIMULATING REGISTRY FAILURE SCENARIO")
    print("=" * 50)
    
    # Create temporary directory without Git
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Working in: {temp_dir}")
        print("   (This directory has no Git repository)")
        
        print("\n🚀 Attempting to initialize field modification system...")
        
        try:
            result = create_field_modification_system(repo_path=temp_dir)
            
            if isinstance(result, FieldModificationFallbackResult):
                print("\n🆘 FALLBACK TRIGGERED - HUMAN INTERACTION REQUIRED")
                print("=" * 50)
                
                return handle_fallback_interaction(result)
            else:
                print("✅ System initialized successfully (unexpected)")
                return True
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False


def handle_fallback_interaction(fallback_result: FieldModificationFallbackResult):
    """Handle interactive fallback scenario"""
    
    print(f"\n📋 FALLBACK DETAILS:")
    print(f"   Reason: {fallback_result.fallback_reason}")
    print(f"   System Status: {fallback_result.system_status}")
    print(f"   Can Retry: {fallback_result.can_retry}")
    
    if fallback_result.registry_details:
        print(f"\n🔍 REGISTRY STATUS:")
        for registry, details in fallback_result.registry_details.items():
            status = "✅ Available" if details.get('available', False) else "❌ Unavailable"
            health = details.get('health_score', 0)
            print(f"   {registry}: {status} (Health: {health:.1%})")
            if 'error' in details:
                print(f"      Error: {details['error']}")
    
    print(f"\n👤 HUMAN OPTIONS:")
    for i, option in enumerate(fallback_result.human_options, 1):
        print(f"   {i}. {option}")
    
    print(f"\n💡 RECOMMENDED: {fallback_result.recommended_action}")
    
    # Interactive choice
    while True:
        try:
            choice = input("\n🤔 Your choice (1-4, or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("👋 Exiting fallback scenario")
                return False
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(fallback_result.human_options):
                selected_option = fallback_result.human_options[choice_num - 1]
                print(f"\n✅ You chose: {selected_option}")
                
                return simulate_human_action(selected_option, fallback_result)
            else:
                print("❌ Invalid choice. Please enter 1-4 or 'q'")
                
        except ValueError:
            print("❌ Please enter a valid number or 'q'")
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            return False


def simulate_human_action(choice: str, fallback_result: FieldModificationFallbackResult):
    """Simulate the human's chosen action"""
    
    print(f"\n🎬 SIMULATING: {choice}")
    print("-" * 30)
    
    if "Fix registry issue and retry" in choice:
        print("👤 Human Action: Fixing registry issue...")
        print("   1. Initializing Git repository")
        print("   2. Setting up basic configuration")
        print("   3. Testing registry connectivity")
        print("   4. Retrying field modification")
        
        # Simulate success after fix
        print("\n✅ Registry issue resolved!")
        print("🔄 Retrying field modification...")
        print("✅ Field modification successful!")
        
        return True
        
    elif "Provide manual override" in choice:
        print("👤 Human Action: Providing manual override...")
        print("   1. Human reviews the proposed changes")
        print("   2. Human confirms override is safe")
        print("   3. System applies changes with human approval")
        
        print("\n⚠️  Manual override applied (human responsibility)")
        print("✅ Field modification completed with override")
        
        return True
        
    elif "Abandon" in choice:
        print("👤 Human Action: Abandoning field modification...")
        print("   1. Human decides the risk is too high")
        print("   2. System cancels the modification")
        print("   3. No changes applied")
        
        print("\n🚫 Field modification abandoned by human choice")
        print("ℹ️  System remains in original state")
        
        return True
        
    elif "Investigate" in choice:
        print("👤 Human Action: Investigating registry problems...")
        print("   1. Human examines system logs")
        print("   2. Human checks registry configurations")
        print("   3. Human identifies root cause")
        print("   4. Human implements fix")
        
        print("\n🔍 Investigation completed")
        print("🛠️  Root cause identified and fixed")
        print("🔄 System ready for retry")
        
        return True
    
    else:
        print(f"❓ Unknown action: {choice}")
        return False


def demo_healthy_scenario():
    """Demo what happens when registries are healthy"""
    
    print("\n🎭 DEMONSTRATING HEALTHY SCENARIO")
    print("=" * 50)
    
    # Create temporary directory with Git
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Working in: {temp_dir}")
        
        # Initialize Git
        try:
            subprocess.run(['git', 'init'], cwd=temp_dir, check=True, capture_output=True)
            print("✅ Git repository initialized")
        except subprocess.CalledProcessError:
            print("⚠️  Git not available, using mock")
        
        print("\n🚀 Attempting to initialize field modification system...")
        
        try:
            field_system = create_field_modification_system(repo_path=temp_dir)
            
            if hasattr(field_system, 'request_field_modification'):
                print("✅ Field modification system initialized successfully!")
                
                # Create a test request
                request = FieldModificationRequest(
                    modification_id="demo_001",
                    component_name="demo_component",
                    modification_type="enhancement",
                    description="Demo field modification",
                    code_changes={"demo.py": "print('Hello from field modification!')"},
                    safety_level="medium",
                    git_sync_required=True,
                    permanent_persistence=False,
                    created_at=datetime.now(),
                    requested_by="demo_user"
                )
                
                print("\n🔧 Attempting field modification...")
                result = field_system.request_field_modification(request)
                
                if isinstance(result, FieldModificationFallbackResult):
                    print("⚠️  Fallback triggered even in healthy scenario")
                    return False
                else:
                    print("✅ Field modification completed successfully!")
                    return True
            else:
                print("✅ System initialized (no modification attempted)")
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def main():
    """Main CLI interface"""
    
    print("🆘 FALLBACK MECHANISM DEMO CLI")
    print("=" * 50)
    print("This demo shows how the system falls back to human interaction")
    print("when it cannot resolve registry issues autonomously.")
    print("=" * 50)
    
    while True:
        print("\n📋 Choose a demo scenario:")
        print("   1. Simulate registry failure (fallback scenario)")
        print("   2. Demonstrate healthy scenario")
        print("   3. Exit")
        
        try:
            choice = input("\n🤔 Your choice (1-3): ").strip()
            
            if choice == '1':
                success = simulate_registry_failure()
                print(f"\n📊 Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
                
            elif choice == '2':
                success = demo_healthy_scenario()
                print(f"\n📊 Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
                
            elif choice == '3':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
