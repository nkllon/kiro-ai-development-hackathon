#!/usr/bin/env python3
"""Test script for Constellation Orchestrator notebook"""

import json
import sys
from typing import List, Dict, Any

# Load notebook
with open('examples/notebook/constellation_orchestrator_demo.ipynb', 'r') as f:
    nb = json.load(f)

# Extract and execute code cells
print("Testing Constellation Orchestrator Notebook")
print("=" * 60)

errors = []
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        code = ''.join(cell['source'])
        if code.strip():
            print(f"\n[Cell {i}] Executing...")
            try:
                exec(code, globals())
                print(f"✅ Cell {i} executed successfully")
            except Exception as e:
                error_msg = f"❌ Cell {i} failed: {type(e).__name__}: {e}"
                print(error_msg)
                errors.append(error_msg)

print("\n" + "=" * 60)
print(f"Test Summary: {len(nb['cells']) - len(errors)}/{len([c for c in nb['cells'] if c['cell_type'] == 'code'])} cells passed")
if errors:
    print("\nErrors encountered:")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)
else:
    print("✅ All cells executed successfully!")
