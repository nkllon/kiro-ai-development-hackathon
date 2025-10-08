#!/usr/bin/env python3
"""
Validate critical ML dependencies can be imported.
This script is run during Docker build to ensure all required dependencies are available.
"""

import sys

def validate_imports():
    """Validate that all critical ML dependencies can be imported."""
    failures = []
    
    # Test numpy
    try:
        import numpy
        print("✓ numpy imported successfully")
    except ImportError as e:
        failures.append(f"numpy: {e}")
    
    # Test sklearn
    try:
        import sklearn
        print("✓ sklearn imported successfully")
    except ImportError as e:
        failures.append(f"sklearn: {e}")
    
    # Test pandas
    try:
        import pandas
        print("✓ pandas imported successfully")
    except ImportError as e:
        failures.append(f"pandas: {e}")
    
    # Test scipy
    try:
        import scipy
        print("✓ scipy imported successfully")
    except ImportError as e:
        failures.append(f"scipy: {e}")
    
    if failures:
        print("\n❌ Import validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    
    print("\n✅ All critical dependencies validated successfully")

if __name__ == "__main__":
    validate_imports()