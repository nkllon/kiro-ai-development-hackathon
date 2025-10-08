#!/usr/bin/env python3
"""
5D2 Notebook Validation Script

This script validates that the 5D2 Use Cases Exploration Notebook
and its utilities are working correctly.
"""

import sys
import json
from pathlib import Path

def validate_notebook_structure():
    """Validate the notebook structure and utilities."""
    print("🔍 Validating 5D2 Notebook Structure...")
    
    # Check main notebook
    notebook_path = Path("5D2_Complete_Use_Cases_Exploration.ipynb")
    if notebook_path.exists():
        print("✅ Main notebook exists")
        
        # Validate notebook JSON structure
        try:
            with open(notebook_path, 'r') as f:
                notebook_data = json.load(f)
            
            if 'cells' in notebook_data and len(notebook_data['cells']) > 0:
                print(f"✅ Notebook has {len(notebook_data['cells'])} cells")
            else:
                print("❌ Notebook has no cells")
                return False
                
        except json.JSONDecodeError:
            print("❌ Notebook JSON is invalid")
            return False
    else:
        print("❌ Main notebook not found")
        return False
    
    # Check utilities
    utils_dir = Path("notebook_utils")
    if utils_dir.exists():
        print("✅ Utilities directory exists")
        
        required_files = [
            "__init__.py",
            "configuration.py", 
            "use_case_framework.py",
            "interactive_widgets.py",
            "visualization_helpers.py"
        ]
        
        for file_name in required_files:
            file_path = utils_dir / file_name
            if file_path.exists():
                print(f"✅ {file_name} exists")
            else:
                print(f"❌ {file_name} missing")
                return False
    else:
        print("❌ Utilities directory not found")
        return False
    
    # Check demo data
    demo_dir = Path("demo_data")
    if demo_dir.exists():
        print("✅ Demo data directory exists")
        
        required_dirs = ["sample_specs", "mock_results", "performance_baselines"]
        for dir_name in required_dirs:
            dir_path = demo_dir / dir_name
            if dir_path.exists():
                print(f"✅ {dir_name} directory exists")
            else:
                print(f"❌ {dir_name} directory missing")
                return False
    else:
        print("❌ Demo data directory not found")
        return False
    
    return True

def test_utilities():
    """Test the notebook utilities."""
    print("\n🧪 Testing Notebook Utilities...")
    
    try:
        # Test configuration
        from notebook_utils.configuration import NotebookConfiguration
        config = NotebookConfiguration()
        demo_config = config.load_demo_config()
        print("✅ Configuration module works")
        print(f"   Demo mode: {demo_config.get('demo_mode', False)}")
        
        # Test use case framework
        from notebook_utils.use_case_framework import DimensionAnalysisUseCase
        use_case = DimensionAnalysisUseCase()
        result = use_case.execute()
        print("✅ Use case framework works")
        print(f"   Overall score: {result.get('overall_score', 0):.3f}")
        
        # Test interactive widgets
        from notebook_utils.interactive_widgets import InteractiveExplorer
        explorer = InteractiveExplorer()
        print("✅ Interactive widgets module works")
        
        # Test visualization helpers
        from notebook_utils.visualization_helpers import create_quality_dashboard
        dashboard = create_quality_dashboard({'test_dimension': 0.85})
        print("✅ Visualization helpers work")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Utility test error: {e}")
        return False

def main():
    """Main validation function."""
    print("🐺 5D2 NOTEBOOK VALIDATION")
    print("=" * 40)
    
    # Change to notebook directory
    notebook_dir = Path(__file__).parent
    original_cwd = Path.cwd()
    
    try:
        import os
        os.chdir(notebook_dir)
        
        # Add utilities to path
        sys.path.insert(0, str(notebook_dir))
        
        # Run validations
        structure_valid = validate_notebook_structure()
        utilities_valid = test_utilities()
        
        print("\n" + "=" * 40)
        print("📊 VALIDATION RESULTS")
        print("=" * 40)
        
        if structure_valid and utilities_valid:
            print("🎉 ALL VALIDATIONS PASSED!")
            print("✅ Notebook structure is complete")
            print("✅ All utilities are functional")
            print("✅ Ready for demonstration and extension")
            return True
        else:
            print("❌ VALIDATION FAILED")
            if not structure_valid:
                print("❌ Notebook structure issues found")
            if not utilities_valid:
                print("❌ Utility functionality issues found")
            return False
            
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)