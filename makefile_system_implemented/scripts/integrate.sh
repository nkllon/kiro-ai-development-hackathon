#!/bin/bash
# Makefile System Integration Script
# Integrates the Makefile system into your project

set -e

echo '🔗 Integrating Makefile system...'

# Create symlinks to unified Makefile
if [ ! -L 'Makefile.unified' ]; then
    ln -s makefile_system/unified/Makefile Makefile.unified
    echo '✅ Created symlink to unified Makefile'
fi

# Create include file for modular Makefiles
cat > makefile_system_include.mk << 'EOF'
# Include all modular Makefiles
include makefile_system/modular/*.mk
EOF
echo '✅ Created modular Makefile include'

echo '✅ Makefile system integration complete'
echo 'Usage:'
echo '  make -f Makefile.unified help'
echo '  make -f Makefile include makefile_system_include.mk'