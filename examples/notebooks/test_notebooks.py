#!/usr/bin/env python3
"""
Test script for Jupyter notebooks.
Validates that all notebooks can be loaded and have proper structure.
"""

import sys
import os
from pathlib import Path
import nbformat
from nbformat.validator import validate
import json

def test_notebook(notebook_path: Path) -> dict:
    """Test a single notebook for validity."""
    result = {
        'name': notebook_path.name,
        'path': str(notebook_path),
        'valid': False,
        'cells': 0,
        'markdown_cells': 0,
        'code_cells': 0,
        'errors': []
    }
    
    try:
        # Load the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Validate notebook format
        validate(nb)
        
        # Count cells
        result['cells'] = len(nb.cells)
        result['markdown_cells'] = len([c for c in nb.cells if c.cell_type == 'markdown'])
        result['code_cells'] = len([c for c in nb.cells if c.cell_type == 'code'])
        
        # Check for basic structure
        if result['cells'] == 0:
            result['errors'].append("No cells found")
        
        if result['markdown_cells'] == 0:
            result['errors'].append("No markdown cells found")
            
        # Check first cell is markdown (should be title/overview)
        if nb.cells and nb.cells[0].cell_type != 'markdown':
            result['errors'].append("First cell should be markdown (title/overview)")
        
        # Check for overview content
        if nb.cells and nb.cells[0].cell_type == 'markdown':
            first_cell = nb.cells[0].source
            if 'Overview' not in first_cell and 'overview' not in first_cell:
                result['errors'].append("First cell should contain overview")
        
        result['valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"Failed to load/validate: {str(e)}")
    
    return result

def main():
    """Test all notebooks in the current directory."""
    print("🧪 Testing Jupyter Notebooks")
    print("=" * 50)
    
    # Find all notebook files
    notebook_dir = Path('.')
    notebooks = list(notebook_dir.glob('*.ipynb'))
    
    if not notebooks:
        print("❌ No notebooks found in current directory")
        return 1
    
    print(f"📓 Found {len(notebooks)} notebooks to test")
    
    results = []
    for notebook_path in sorted(notebooks):
        print(f"\n🔍 Testing {notebook_path.name}...")
        result = test_notebook(notebook_path)
        results.append(result)
        
        if result['valid']:
            print(f"✅ {notebook_path.name}")
            print(f"   📊 {result['cells']} total cells ({result['markdown_cells']} markdown, {result['code_cells']} code)")
        else:
            print(f"❌ {notebook_path.name}")
            for error in result['errors']:
                print(f"   ⚠️  {error}")
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    
    valid_count = len([r for r in results if r['valid']])
    total_count = len(results)
    
    print(f"✅ Valid notebooks: {valid_count}/{total_count}")
    
    if valid_count < total_count:
        print(f"❌ Invalid notebooks: {total_count - valid_count}")
        print("\nInvalid notebooks:")
        for result in results:
            if not result['valid']:
                print(f"  - {result['name']}: {', '.join(result['errors'])}")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅" if result['valid'] else "❌"
        print(f"{status} {result['name']}: {result['cells']} cells ({result['markdown_cells']}M, {result['code_cells']}C)")
    
    return 0 if valid_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())