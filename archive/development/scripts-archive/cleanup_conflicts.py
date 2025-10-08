import os
import re

def clean_conflict_markers(file_path):
    """Clean up git conflict markers by keeping the HEAD version."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Remove conflict markers and keep HEAD version
        # Pattern: <<<<<<< HEAD\n(content)\n=======\n(other content)\n>>>>>>> branch
        pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n.*?\n>>>>>>> [^\n]+'
        cleaned = re.sub(pattern, r'\1', content, flags=re.DOTALL)
        
        # Handle simpler cases where there's no content between markers
        pattern2 = r'<<<<<<< HEAD\n=======\n.*?\n>>>>>>> [^\n]+'
        cleaned = re.sub(pattern2, '', cleaned, flags=re.DOTALL)
        
        # Handle cases where HEAD section is empty
        pattern3 = r'<<<<<<< HEAD\n=======\n(.*?)\n>>>>>>> [^\n]+'
        cleaned = re.sub(pattern3, r'\1', cleaned, flags=re.DOTALL)
        
        if content != cleaned:
            with open(file_path, 'w') as f:
                f.write(cleaned)
            print(f"Cleaned conflict markers in: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Process files with conflict markers
files_to_clean = [
    './docs/readme/project/README.md',
    './docs/README.md', 
    './src/beast_mode/hubris_prevention/enforcement/humility_enforcer.py',
    './src/beast_mode/integration/devpost/api/client.py',
    './src/beast_mode/resilience/graceful_degradation_manager.py',
    './src/beast_mode/billing/gcp_integration.py',
    './src/spec_reconciliation/beast_mode_system_backup.py'
]

for file_path in files_to_clean:
    if os.path.exists(file_path):
        clean_conflict_markers(file_path)
