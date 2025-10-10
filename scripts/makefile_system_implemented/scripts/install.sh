#!/bin/bash
# Makefile System Installation Script
# Installs the Makefile system in your project

set -e

echo '📦 Installing Makefile system...'

# Check if make is available
if ! command -v make &> /dev/null; then
    echo '❌ make is not installed. Please install make first.'
    exit 1
fi

# Create makefile_system directory
mkdir -p makefile_system

# Copy all generated files
cp -r unified makefile_system/
cp -r modular makefile_system/
cp -r projections makefile_system/
cp -r documentation makefile_system/
cp -r validation makefile_system/
cp -r scripts makefile_system/

# Make scripts executable
chmod +x makefile_system/scripts/*.sh
chmod +x makefile_system/validation/*.sh

echo '✅ Makefile system installation complete'