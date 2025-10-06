#!/usr/bin/env python3
"""
Kiro Output Capturer - Deterministic Tool
==========================================

Simple deterministic tool to properly capture Kiro CLI output and save it to files.
No fancy orchestration - just capture stdout/stderr and save it.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def capture_kiro_output(prompt: str, output_file: str) -> bool:
    """
    Capture Kiro CLI output properly using deterministic approach.
    
    Args:
        prompt: The prompt to send to Kiro
        output_file: Where to save Kiro's response
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        # Create output directory if needed
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use simple approach: let Kiro output to a file directly
        cmd = f'echo "{prompt}" | kiro - > {output_file} 2>&1'
        
        print(f"🔧 Executing: {cmd}")
        
        # Run the command and wait for completion
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,  # Don't capture - let it write to file
            text=True
        )
        
        # Check if output file was created and has content
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"✅ Kiro output captured: {output_file} ({output_path.stat().st_size} bytes)")
            return True
        else:
            print(f"❌ No output captured to {output_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error capturing Kiro output: {e}")
        return False


def main():
    """Test the output capturer with a simple prompt."""
    
    if len(sys.argv) < 2:
        print("Usage: python kiro_output_capturer.py <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    
    # Simple test prompt
    prompt = f"""
Implement task {task_id} for the System Architecture Wiring Diagram.

Create a simple Python class that inherits from ReflectiveModule and implements
the basic functionality for this task.

Please provide the complete implementation with proper imports and error handling.
"""
    
    # Output file
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"kiro_outputs/{task_id}-{timestamp}.txt"
    
    print(f"🔧 Testing Kiro output capture for {task_id}")
    print(f"📝 Output file: {output_file}")
    
    success = capture_kiro_output(prompt, output_file)
    
    if success:
        print("✅ Output capture test successful!")
        # Show first few lines of output
        with open(output_file, 'r') as f:
            lines = f.readlines()[:10]
            print("\n📄 First 10 lines of captured output:")
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line.rstrip()}")
    else:
        print("❌ Output capture test failed!")


if __name__ == "__main__":
    main()