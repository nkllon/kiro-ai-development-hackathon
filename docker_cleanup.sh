#!/bin/bash
# Docker cleanup script for macOS
# Safely removes unused containers, images, volumes, and build cache

set -e  # Exit on error

echo "🧹 Docker Cleanup Script for macOS"
echo "=================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "📊 Current Docker disk usage:"
docker system df
echo ""

# Calculate current Docker.raw size
if [ -f ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw ]; then
    BEFORE_SIZE=$(du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw | cut -f1)
    echo "💾 Current Docker.raw size: $BEFORE_SIZE"
    echo ""
fi

# Prompt for confirmation
read -p "⚠️  This will remove ALL unused containers, images, volumes, and build cache. Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

echo ""
echo "🗑️  Removing stopped containers..."
docker container prune -f

echo ""
echo "🗑️  Removing unused images..."
docker image prune -a -f

echo ""
echo "🗑️  Removing unused volumes..."
docker volume prune -f

echo ""
echo "🗑️  Removing build cache..."
docker builder prune -a -f

echo ""
echo "✅ Cleanup complete!"
echo ""

echo "📊 New Docker disk usage:"
docker system df
echo ""

# Show Docker.raw size after cleanup
if [ -f ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw ]; then
    AFTER_SIZE=$(du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw | cut -f1)
    echo "💾 Docker.raw size after cleanup: $AFTER_SIZE (was: $BEFORE_SIZE)"
    echo ""
    echo "⚠️  NOTE: Docker.raw may not shrink immediately. To reclaim space:"
    echo "   1. Quit Docker Desktop completely"
    echo "   2. Restart Docker Desktop"
    echo "   OR"
    echo "   Use Docker Desktop → Settings → Troubleshooting → Clean / Purge data"
    echo ""
fi

echo "📖 For more cleanup options, see: CONTAINER_SPACE_MACOS_GUIDE.md"






