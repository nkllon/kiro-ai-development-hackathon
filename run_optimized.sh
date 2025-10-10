#!/bin/bash
# Performance Optimization Script
# Run this script to apply performance optimizations

echo "🚀 Applying Beast Mode Framework Performance Optimizations..."

# Source performance configuration
if [ -f .performance_config ]; then
    source .performance_config
    echo "✅ Performance configuration loaded"
fi

# Set Python optimizations
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Clean Python cache
echo "🧹 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Run with optimizations
echo "⚡ Running with performance optimizations..."
python3 -O "$@"
