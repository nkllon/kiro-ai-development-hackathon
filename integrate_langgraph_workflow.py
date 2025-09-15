#!/usr/bin/env python3
"""
LangGraph Workflow Integration
=============================

Integration script to demonstrate the LangGraph DevPost automation workflow.
This replaces the old step_navigator.py with a more robust, orchestrated approach.
"""

import sys
import time
from typing import Optional
from datetime import datetime

from langgraph_devpost_workflow import DevPostWorkflow, create_devpost_workflow
from langgraph_devpost_state import get_state_summary


def run_langgraph_devpost_automation(
    mode: str = "interactive",
    user_data_dir: str = "/tmp/devpost-browser",
    workflow_id: Optional[str] = None
) -> bool:
    """
    Run the complete DevPost automation using LangGraph workflow.
    
    Args:
        mode: Automation mode ("interactive", "automatic", "guided")
        user_data_dir: Browser data directory for session preservation
        workflow_id: Optional custom workflow ID
        
    Returns:
        True if successful, False otherwise
    """
    
    print("🚀 LangGraph DevPost Automation")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Mode: {mode}")
    print(f"📁 Data Directory: {user_data_dir}")
    print("=" * 60)
    
    try:
        # Create the workflow
        workflow = create_devpost_workflow(workflow_id)
        
        # Run the workflow
        result = workflow.run_workflow(
            user_data_dir=user_data_dir,
            automation_mode=mode
        )
        
        if result["success"]:
            print("\n🎉 Automation completed successfully!")
            
            # Display summary
            summary = result.get("summary", {})
            print("\n📊 Final Summary:")
            print("-" * 40)
            for key, value in summary.items():
                print(f"{key:25}: {value}")
            
            # Check quality score
            quality_score = summary.get("quality_score")
            if quality_score and quality_score >= 0.8:
                print(f"\n✅ High quality submission! Score: {quality_score:.2f}")
            elif quality_score:
                print(f"\n⚠️ Submission completed with score: {quality_score:.2f}")
                print("   Manual review recommended.")
            
            return True
            
        else:
            print(f"\n❌ Automation failed: {result['error']}")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Automation interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return False


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="LangGraph DevPost Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python integrate_langgraph_workflow.py
  
  # Automatic mode
  python integrate_langgraph_workflow.py --mode automatic
  
  # Custom data directory
  python integrate_langgraph_workflow.py --data-dir /custom/path
  
  # With custom workflow ID
  python integrate_langgraph_workflow.py --workflow-id my_workflow_123
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["interactive", "automatic", "guided"],
        default="interactive",
        help="Automation mode (default: interactive)"
    )
    
    parser.add_argument(
        "--data-dir",
        default="/tmp/devpost-browser",
        help="Browser data directory (default: /tmp/devpost-browser)"
    )
    
    parser.add_argument(
        "--workflow-id",
        help="Custom workflow ID (default: auto-generated)"
    )
    
    args = parser.parse_args()
    
    # Run the automation
    success = run_langgraph_devpost_automation(
        mode=args.mode,
        user_data_dir=args.data_dir,
        workflow_id=args.workflow_id
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
