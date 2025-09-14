#!/usr/bin/env python3
"""
Deterministic TOML Editor

Uses proper TOML parsing and serialization to avoid heuristic editing issues.
Follows the deterministic file editing rules.
"""

import tomllib
import tomli_w
from pathlib import Path
import sys
from typing import Dict, Any, List


def load_toml(file_path: str) -> Dict[str, Any]:
    """Load TOML file using deterministic parser."""
    with open(file_path, 'rb') as f:
        return tomllib.load(f)


def save_toml(file_path: str, data: Dict[str, Any]) -> None:
    """Save TOML file using deterministic serializer."""
    with open(file_path, 'wb') as f:
        tomli_w.dump(data, f)


def add_console_scripts(file_path: str, scripts: Dict[str, str]) -> None:
    """Add console scripts to pyproject.toml deterministically."""
    data = load_toml(file_path)
    
    # Ensure project.scripts exists
    if 'project' not in data:
        data['project'] = {}
    if 'scripts' not in data['project']:
        data['project']['scripts'] = {}
    
    # Add new scripts
    for script_name, script_entry in scripts.items():
        data['project']['scripts'][script_name] = script_entry
    
    # Save back to file
    save_toml(file_path, data)
    print(f"✅ Added console scripts to {file_path}: {list(scripts.keys())}")


def remove_console_scripts(file_path: str, script_names: List[str]) -> None:
    """Remove console scripts from pyproject.toml deterministically."""
    data = load_toml(file_path)
    
    if 'project' in data and 'scripts' in data['project']:
        for script_name in script_names:
            if script_name in data['project']['scripts']:
                del data['project']['scripts'][script_name]
                print(f"✅ Removed console script: {script_name}")
    
    # Save back to file
    save_toml(file_path, data)


def list_console_scripts(file_path: str) -> Dict[str, str]:
    """List all console scripts in pyproject.toml."""
    data = load_toml(file_path)
    
    if 'project' in data and 'scripts' in data['project']:
        return data['project']['scripts']
    return {}


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 3:
        print("Usage: python toml_editor.py <command> <file> [args...]")
        print("Commands:")
        print("  add-scripts <file> <script_name>=<script_entry> [script_name2]=<script_entry2> ...")
        print("  remove-scripts <file> <script_name> [script_name2] ...")
        print("  list-scripts <file>")
        sys.exit(1)
    
    command = sys.argv[1]
    file_path = sys.argv[2]
    
    if command == "add-scripts":
        if len(sys.argv) < 4:
            print("Error: add-scripts requires script definitions")
            sys.exit(1)
        
        scripts = {}
        for arg in sys.argv[3:]:
            if '=' not in arg:
                print(f"Error: Invalid script definition: {arg}")
                sys.exit(1)
            script_name, script_entry = arg.split('=', 1)
            scripts[script_name] = script_entry
        
        add_console_scripts(file_path, scripts)
    
    elif command == "remove-scripts":
        if len(sys.argv) < 4:
            print("Error: remove-scripts requires script names")
            sys.exit(1)
        
        script_names = sys.argv[3:]
        remove_console_scripts(file_path, script_names)
    
    elif command == "list-scripts":
        scripts = list_console_scripts(file_path)
        if scripts:
            print("Console scripts:")
            for name, entry in scripts.items():
                print(f"  {name} = {entry}")
        else:
            print("No console scripts found")
    
    else:
        print(f"Error: Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
