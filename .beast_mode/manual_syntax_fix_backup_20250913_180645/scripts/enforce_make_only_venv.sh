#!/bin/bash
# Enforce Make-only execution model for virtual environment
# This script sets up permissions so that tools can only be run through make
set -e

echo "🔐 Setting up Make-only permission model for virtual environment..."

# Get the virtual environment path
VENV_PATH=".venv"
if [ ! -d ""VENV_PAT"H" ]; then
	echo "❌ Virtual environment not found at "VENV_PAT"H"
	exit 1
fi

echo "📦 Creating backup of original tools..."

# Backup original tools
cp ""VENV_PATH"/bin/pytest" ""VENV_PATH"/bin/pytest.original"
cp ""VENV_PATH"/bin/flake8" ""VENV_PATH"/bin/flake8.original"
cp ""VENV_PATH"/bin/black" ""VENV_PATH"/bin/black.original"
cp ""VENV_PATH"/bin/mypy" ""VENV_PATH"/bin/mypy.original"

echo "🔄 Replacing tools with wrappers..."

# Create pytest wrapper
cat >""VENV_PATH"/bin/pytest" <<'EOF'
#!/usr/bin/env python3
"""
pytest wrapper - only allows execution through make
"""
import os
import sys
import psutil

def check_parent_process():
    """Check if we're being called by make"""
    try:
        current_pid = os.getpid()
        parent = psutil.Process(current_pid).parent()
        
        # Check if parent is make
        if parent and parent.name() == 'make':
            return True
            
        # Check grandparent too (in case make calls a shell)
        if parent:
            grandparent = parent.parent()
            if grandparent and grandparent.name() == 'make':
                return True
                
        return False
    except Exception:
        return False

def main():
    if not check_parent_process():
        print("❌ ERROR: pytest can only be executed through make")
        print("✅ Use: make test")
        print("📋 Available test targets:")
        print("   - make test")
        print("   - make test-all")
        print("   - make test-python")
        print("   - make test-model-driven")
        sys.exit(1)
    
    # Execute original pytest
    original_pytest = os.path.join(os.path.dirname(__file__), "pytest.original")
    os.execv(original_pytest, [original_pytest] + sys.argv[1:])

if __name__ == "__main__":
    main()
EOF

# Create flake8 wrapper
cat >""VENV_PATH"/bin/flake8" <<'EOF'
#!/usr/bin/env python3
"""
flake8 wrapper - only allows execution through make
"""
import os
import sys
import psutil

def check_parent_process():
    """Check if we're being called by make"""
    try:
        current_pid = os.getpid()
        parent = psutil.Process(current_pid).parent()
        
        if parent and parent.name() == 'make':
            return True
            
        if parent:
            grandparent = parent.parent()
            if grandparent and grandparent.name() == 'make':
                return True
                
        return False
    except Exception:
        return False

def main():
    if not check_parent_process():
        print("❌ ERROR: flake8 can only be executed through make")
        print("✅ Use: make lint")
        sys.exit(1)
    
    # Execute original flake8
    original_flake8 = os.path.join(os.path.dirname(__file__), "flake8.original")
    os.execv(original_flake8, [original_flake8] + sys.argv[1:])

if __name__ == "__main__":
    main()
EOF

# Create black wrapper
cat >""VENV_PATH"/bin/black" <<'EOF'
#!/usr/bin/env python3
"""
black wrapper - only allows execution through make
"""
import os
import sys
import psutil

def check_parent_process():
    """Check if we're being called by make"""
    try:
        current_pid = os.getpid()
        parent = psutil.Process(current_pid).parent()
        
        if parent and parent.name() == 'make':
            return True
            
        if parent:
            grandparent = parent.parent()
            if grandparent and grandparent.name() == 'make':
                return True
                
        return False
    except Exception:
        return False

def main():
    if not check_parent_process():
        print("❌ ERROR: black can only be executed through make")
        print("✅ Use: make format")
        sys.exit(1)
    
    # Execute original black
    original_black = os.path.join(os.path.dirname(__file__), "black.original")
    os.execv(original_black, [original_black] + sys.argv[1:])

if __name__ == "__main__":
    main()
EOF

# Create mypy wrapper
cat >""VENV_PATH"/bin/mypy" <<'EOF'
#!/usr/bin/env python3
"""
mypy wrapper - only allows execution through make
"""
import os
import sys
import psutil

def check_parent_process():
    """Check if we're being called by make"""
    try:
        current_pid = os.getpid()
        parent = psutil.Process(current_pid).parent()
        
        if parent and parent.name() == 'make':
            return True
            
        if parent:
            grandparent = parent.parent()
            if grandparent and grandparent.name() == 'make':
                return True
                
        return False
    except Exception:
        return False

def main():
    if not check_parent_process():
        print("❌ ERROR: mypy can only be executed through make")
        print("✅ Use: make type-safety")
        sys.exit(1)
    
    # Execute original mypy
    original_mypy = os.path.join(os.path.dirname(__file__), "mypy.original")
    os.execv(original_mypy, [original_mypy] + sys.argv[1:])

if __name__ == "__main__":
    main()
EOF

# Make wrappers executable
chmod +x ""VENV_PATH"/bin/pytest"
chmod +x ""VENV_PATH"/bin/flake8"
chmod +x ""VENV_PATH"/bin/black"
chmod +x ""VENV_PATH"/bin/mypy"

echo "✅ Make-only permission model set up for virtual environment!"
echo "🔒 Tools are now restricted to Make-only execution:"
echo "   - pytest → make test"
echo "   - flake8 → make lint"
echo "   - black → make format"
echo "   - mypy → make type-safety"
echo ""
echo "🔄 To restore original behavior: ./scripts/restore_tools_venv.sh"
echo ""
echo "🧪 Test it:"
echo "   ❌ pytest --version (should fail)"
echo "   ✅ make test (should work)"
