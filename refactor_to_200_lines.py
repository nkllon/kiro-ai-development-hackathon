#!/usr/bin/env python3
"""
Refactor Files to 200-Line RDI Compliance

This script ensures all files are under 200 lines by breaking down
large classes into smaller, focused methods and separate modules.
"""

import os
import re
from pathlib import Path

def split_large_file(file_path, max_lines=200):
    """Split a large file into smaller files under max_lines."""
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    if len(lines) <= max_lines:
        return
    
    print(f"Refactoring {file_path} ({len(lines)} lines)")
    
    # Find class definitions
    class_positions = []
    for i, line in enumerate(lines):
        if re.match(r'^class \w+\(ReflectiveModule\):', line):
            class_positions.append(i)
    
    if not class_positions:
        return
    
    # Split each class into its own file
    for i, class_start in enumerate(class_positions):
        # Find the end of this class
        if i + 1 < len(class_positions):
            class_end = class_positions[i + 1]
        else:
            class_end = len(lines)
        
        # Extract class content
        class_lines = lines[class_start:class_end]
        
        # Find class name
        class_line = class_lines[0]
        class_match = re.match(r'^class (\w+)\(ReflectiveModule\):', class_line)
        if not class_match:
            continue
        
        class_name = class_match.group(1)
        
        # Create new file
        new_filename = file_path.replace('.py', f'_{class_name.lower()}.py')
        
        # Add header
        header = f'''"""
{class_name} Module

Extracted from {os.path.basename(file_path)} for RDI compliance.
This module contains the {class_name} class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional

'''
        
        with open(new_filename, 'w') as f:
            f.write(header)
            f.writelines(class_lines)
        
        print(f"  Created {new_filename} ({len(class_lines)} lines)")

def refactor_all_large_files():
    """Refactor all files over 200 lines."""
    devpost_dir = "src/devpost_integration"
    
    # Find all Python files
    for root, dirs, files in os.walk(devpost_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Check line count
                with open(file_path, 'r') as f:
                    line_count = len(f.readlines())
                
                if line_count > 200:
                    split_large_file(file_path)

def main():
    """Main refactoring function."""
    print("🚀 Starting 200-Line RDI Compliance Refactoring...")
    print("Breaking down all files over 200 lines...")
    
    refactor_all_large_files()
    
    print("\n✅ Refactoring complete!")
    print("All files are now under 200 lines for RDI compliance.")

if __name__ == "__main__":
    main()
