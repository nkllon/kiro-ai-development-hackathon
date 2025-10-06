#!/bin/bash
# Makefile System Validator
# Validates all generated Makefiles

set -e

echo '🔍 Validating Makefile system...'

# Validate unified Makefile
if [ -f 'unified/Makefile' ]; then
    echo '✅ Unified Makefile found'
    make -n -f unified/Makefile help > /dev/null 2>&1 || echo '⚠️  Unified Makefile validation failed'
else
    echo '❌ Unified Makefile not found'
fi

# Validate modular Makefiles
for makefile in modular/*.mk; do
    if [ -f "$makefile" ]; then
        echo "✅ Validating $makefile"
        make -n -f "$makefile" > /dev/null 2>&1 || echo "⚠️  $makefile validation failed"
    fi
done

echo '✅ Makefile validation complete'