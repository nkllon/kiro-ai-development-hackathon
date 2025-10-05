#!/bin/bash
# Observatory Dependency Sync Validation Hook
# Validates that pyproject.toml and requirements.txt are in sync

set -e

echo "🔍 Validating dependency sync..."

# Check if required files exist
if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    echo "   Run: make requirements"
    exit 1
fi

# Check if python and toml module are available
if ! python3 -c "import toml" 2>/dev/null; then
    echo "❌ Python toml module not available"
    echo "   Install with: pip install toml"
    exit 1
fi

# Extract dependencies from pyproject.toml
echo "📋 Extracting dependencies from pyproject.toml..."
PYPROJECT_DEPS=$(python3 -c "
import toml
import sys

try:
    data = toml.load('pyproject.toml')
    if 'project' not in data or 'dependencies' not in data['project']:
        print('❌ pyproject.toml missing project.dependencies section', file=sys.stderr)
        sys.exit(1)
    
    deps = data['project']['dependencies']
    for dep in sorted(deps):
        # Extract package name (before any version specifiers)
        pkg_name = dep.split('>=')[0].split('==')[0].split('~=')[0].split('>')[0].split('<')[0].strip()
        print(pkg_name)
except Exception as e:
    print(f'❌ Error parsing pyproject.toml: {e}', file=sys.stderr)
    sys.exit(1)
")

if [ $? -ne 0 ]; then
    echo "$PYPROJECT_DEPS"
    exit 1
fi

# Count dependencies
DEP_COUNT=$(echo "$PYPROJECT_DEPS" | wc -l | tr -d ' ')
echo "📊 Found $DEP_COUNT dependencies in pyproject.toml"

# Check each dependency exists in requirements.txt
echo "🔍 Checking requirements.txt for all dependencies..."
MISSING=()
while IFS= read -r dep; do
    if [ -n "$dep" ]; then
        # Check for package name at start of line (with version specifiers or extras)
        if ! grep -q "^${dep}[>=<~!\[]" requirements.txt; then
            MISSING+=("$dep")
        fi
    fi
done <<< "$PYPROJECT_DEPS"

# Check for critical ML dependencies specifically
CRITICAL_DEPS=("numpy" "scikit-learn" "pandas" "scipy")
MISSING_CRITICAL=()

for dep in "${CRITICAL_DEPS[@]}"; do
    if ! grep -q "^${dep}[>=<~!\[]" requirements.txt; then
        MISSING_CRITICAL+=("$dep")
    fi
done

# Report results
if [ ${#MISSING[@]} -gt 0 ]; then
    echo "❌ Dependencies in pyproject.toml but not in requirements.txt:"
    for dep in "${MISSING[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "🔧 Fix with: make requirements"
    exit 1
fi

if [ ${#MISSING_CRITICAL[@]} -gt 0 ]; then
    echo "⚠️  Critical ML dependencies missing from requirements.txt:"
    for dep in "${MISSING_CRITICAL[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "🔧 Add to pyproject.toml dependencies and run: make requirements"
    exit 1
fi

# Check if requirements.txt has the auto-generated header
if ! head -n 5 requirements.txt | grep -q "auto-generated from pyproject.toml"; then
    echo "⚠️  requirements.txt missing auto-generated header"
    echo "   This may indicate manual editing"
    echo "🔧 Regenerate with: make requirements"
    exit 1
fi

# Validate requirements.txt format
echo "📝 Validating requirements.txt format..."
INVALID_LINES=$(grep -n "^[^#]" requirements.txt | grep -v "[>=<~!]" | head -5)
if [ -n "$INVALID_LINES" ]; then
    echo "⚠️  Potentially invalid lines in requirements.txt:"
    echo "$INVALID_LINES"
    echo "🔧 Regenerate with: make requirements"
fi

echo "✅ Dependency sync validated successfully"
echo "📊 All $DEP_COUNT dependencies properly synchronized"
exit 0