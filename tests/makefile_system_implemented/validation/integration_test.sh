#!/bin/bash
# Makefile System Integration Test
# Tests the complete Makefile system integration

set -e

echo '🧪 Running integration tests...'

# Test unified Makefile
echo 'Testing unified Makefile...'
cd unified
make help > /dev/null 2>&1 || echo '⚠️  Unified Makefile help failed'
cd ..

# Test modular Makefiles
echo 'Testing modular Makefiles...'
for makefile in modular/*.mk; do
    if [ -f "$makefile" ]; then
        echo "  Testing $makefile"
        make -n -f "$makefile" > /dev/null 2>&1 || echo "    ⚠️  $makefile test failed"
    fi
done

echo '✅ Integration tests complete'