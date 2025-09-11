#!/usr/bin/env python3
"""
Deterministic TOML Editor

Follows the deterministic file editing rules:
- Uses tomlkit for parsing and serializing
- Preserves original structure and formatting
- Validates syntax after editing
- NEVER uses heuristic editors
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import tomlkit
    from tomlkit import document, table, string, array
except ImportError:
    print("Error: tomlkit not available. Install with: uv add tomlkit")
    sys.exit(1)


class DeterministicTOMLEditor:
    """
    Deterministic TOML editor that preserves formatting and structure.
    
    Follows the deterministic file editing rules:
    - Uses tomlkit for parsing and serializing
    - Preserves original structure and formatting
    - Validates syntax after editing
    """
    
    def __init__(self, file_path: str):
        """Initialize with TOML file path."""
        self.file_path = Path(file_path)
        self.data = None
        self._load_file()
    
    def _load_file(self) -> None:
        """Load TOML file using tomlkit."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.data = tomlkit.parse(content)
            print(f"✅ Loaded TOML file: {self.file_path}")
        except Exception as e:
            print(f"❌ Error loading TOML file: {e}")
            sys.exit(1)
    
    def _save_file(self) -> None:
        """Save TOML file using tomlkit (preserves formatting)."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                tomlkit.dump(self.data, f)
            print(f"✅ Saved TOML file: {self.file_path}")
        except Exception as e:
            print(f"❌ Error saving TOML file: {e}")
            sys.exit(1)
    
    def _validate_toml(self) -> bool:
        """Validate TOML syntax after editing."""
        try:
            # Re-parse to validate
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tomlkit.parse(content)
            print("✅ TOML syntax validation passed")
            return True
        except Exception as e:
            print(f"❌ TOML syntax validation failed: {e}")
            return False
    
    def add_console_scripts(self, scripts: Dict[str, str]) -> None:
        """
        Add console scripts to pyproject.toml deterministically.
        
        Args:
            scripts: Dictionary of script_name -> script_entry mappings
        """
        print(f"🔧 Adding console scripts: {list(scripts.keys())}")
        
        # Ensure project.scripts exists
        if 'project' not in self.data:
            self.data['project'] = table()
        
        if 'scripts' not in self.data['project']:
            self.data['project']['scripts'] = table()
        
        # Add new scripts
        for script_name, script_entry in scripts.items():
            self.data['project']['scripts'][script_name] = string(script_entry)
            print(f"  ✅ Added: {script_name} = {script_entry}")
        
        # Save and validate
        self._save_file()
        if not self._validate_toml():
            print("❌ TOML validation failed after adding scripts")
            sys.exit(1)
    
    def remove_console_scripts(self, script_names: List[str]) -> None:
        """
        Remove console scripts from pyproject.toml deterministically.
        
        Args:
            script_names: List of script names to remove
        """
        print(f"🗑️ Removing console scripts: {script_names}")
        
        if 'project' in self.data and 'scripts' in self.data['project']:
            for script_name in script_names:
                if script_name in self.data['project']['scripts']:
                    del self.data['project']['scripts'][script_name]
                    print(f"  ✅ Removed: {script_name}")
                else:
                    print(f"  ⚠️ Not found: {script_name}")
        
        # Save and validate
        self._save_file()
        if not self._validate_toml():
            print("❌ TOML validation failed after removing scripts")
            sys.exit(1)
    
    def list_console_scripts(self) -> Dict[str, str]:
        """List all console scripts in pyproject.toml."""
        if 'project' in self.data and 'scripts' in self.data['project']:
            scripts = {}
            for name, entry in self.data['project']['scripts'].items():
                scripts[name] = str(entry)
            return scripts
        return {}
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information from pyproject.toml."""
        if 'project' in self.data:
            project = {}
            for key, value in self.data['project'].items():
                if isinstance(value, (str, int, float, bool)):
                    project[key] = value
                elif isinstance(value, list):
                    project[key] = [str(item) for item in value]
                else:
                    project[key] = str(value)
            return project
        return {}


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 3:
        print("Usage: python deterministic_toml_editor.py <command> <file> [args...]")
        print("Commands:")
        print("  add-scripts <file> <script_name>=<script_entry> [script_name2]=<script_entry2> ...")
        print("  remove-scripts <file> <script_name> [script_name2] ...")
        print("  list-scripts <file>")
        print("  project-info <file>")
        sys.exit(1)
    
    command = sys.argv[1]
    file_path = sys.argv[2]
    
    editor = DeterministicTOMLEditor(file_path)
    
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
        
        editor.add_console_scripts(scripts)
    
    elif command == "remove-scripts":
        if len(sys.argv) < 4:
            print("Error: remove-scripts requires script names")
            sys.exit(1)
        
        script_names = sys.argv[3:]
        editor.remove_console_scripts(script_names)
    
    elif command == "list-scripts":
        scripts = editor.list_console_scripts()
        if scripts:
            print("Console scripts:")
            for name, entry in scripts.items():
                print(f"  {name} = {entry}")
        else:
            print("No console scripts found")
    
    elif command == "project-info":
        info = editor.get_project_info()
        if info:
            print("Project information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print("No project information found")
    
    else:
        print(f"Error: Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
