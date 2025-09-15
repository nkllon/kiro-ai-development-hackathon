#!/bin/bash
# Makefile System Update Script
# Updates the Makefile system with latest changes

set -e

echo '🔄 Updating Makefile system...'

# Run the model generation
python3 src/makefile_system_model.py

# Run the implementation
python3 src/makefile_system_implementation.py

echo '✅ Makefile system update complete'