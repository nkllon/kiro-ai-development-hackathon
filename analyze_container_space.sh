#!/bin/bash
# Comprehensive container space analysis for macOS

echo "🔍 Container Disk Space Analysis for macOS"
echo "=========================================="
echo ""

# Check Docker Desktop
if [ -d ~/Library/Containers/com.docker.docker ]; then
    echo "📦 Docker Desktop:"
    echo "  Total size: $(du -sh ~/Library/Containers/com.docker.docker | cut -f1)"
    if [ -f ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw ]; then
        echo "  Docker.raw: $(du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw | cut -f1)"
    fi
    echo ""
fi

# Check OrbStack
if [ -d ~/Library/Containers/com.orbstack.OrbStack ]; then
    echo "🌐 OrbStack:"
    echo "  Total size: $(du -sh ~/Library/Containers/com.orbstack.OrbStack | cut -f1)"
    echo ""
fi

# Check Podman
if [ -d ~/.local/share/containers ]; then
    echo "🐳 Podman:"
    echo "  Total size: $(du -sh ~/.local/share/containers | cut -f1)"
    echo ""
fi

# Check Colima
if [ -d ~/.colima ]; then
    echo "🦙 Colima:"
    echo "  Total size: $(du -sh ~/.colima | cut -f1)"
    echo ""
fi

# Check Lima
if [ -d ~/.lima ]; then
    echo "🦙 Lima:"
    echo "  Total size: $(du -sh ~/.lima | cut -f1)"
    echo ""
fi

# Docker system usage
if command -v docker &> /dev/null; then
    echo "📊 Docker System Usage:"
    docker system df 2>/dev/null || echo "  Docker not running"
    echo ""
fi

# Calculate total container space
echo "💾 Total Container-Related Space:"
TOTAL=0
for dir in \
    ~/Library/Containers/com.docker.docker \
    ~/Library/Containers/com.orbstack.OrbStack \
    ~/.local/share/containers \
    ~/.colima \
    ~/.lima; do
    if [ -d "$dir" ]; then
        SIZE=$(du -sk "$dir" 2>/dev/null | cut -f1)
        TOTAL=$((TOTAL + SIZE))
    fi
done

# Convert to GB
if command -v bc &> /dev/null; then
    TOTAL_GB=$(echo "scale=2; $TOTAL / 1024 / 1024" | bc)
    echo "  Total: ${TOTAL_GB} GB"
else
    # Fallback if bc is not available
    TOTAL_GB=$((TOTAL / 1024 / 1024))
    echo "  Total: ~${TOTAL_GB} GB"
fi
echo ""

# Recommendations
echo "💡 Recommendations:"
if [ -f ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw ]; then
    DOCKER_RAW_SIZE=$(du -sk ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw 2>/dev/null | cut -f1)
    if command -v bc &> /dev/null; then
        DOCKER_RAW_GB=$(echo "scale=2; $DOCKER_RAW_SIZE / 1024 / 1024" | bc)
        if (( $(echo "$DOCKER_RAW_GB > 50" | bc -l) )); then
            echo "  ⚠️  Docker.raw is ${DOCKER_RAW_GB} GB - consider shrinking"
        fi
    else
        DOCKER_RAW_GB=$((DOCKER_RAW_SIZE / 1024 / 1024))
        if [ $DOCKER_RAW_GB -gt 50 ]; then
            echo "  ⚠️  Docker.raw is ~${DOCKER_RAW_GB} GB - consider shrinking"
        fi
    fi
fi

# Check for multiple runtimes
RUNTIME_COUNT=0
[ -d ~/Library/Containers/com.docker.docker ] && RUNTIME_COUNT=$((RUNTIME_COUNT + 1))
[ -d ~/Library/Containers/com.orbstack.OrbStack ] && RUNTIME_COUNT=$((RUNTIME_COUNT + 1))
[ -d ~/.local/share/containers ] && RUNTIME_COUNT=$((RUNTIME_COUNT + 1))
[ -d ~/.colima ] && RUNTIME_COUNT=$((RUNTIME_COUNT + 1))

if [ $RUNTIME_COUNT -gt 1 ]; then
    echo "  ⚠️  Multiple container runtimes detected - consider removing unused ones"
fi

echo ""
echo "🧹 To clean up, run:"
echo "  docker system prune -a --volumes -f"
echo ""
echo "📖 For detailed cleanup guide, see: CONTAINER_SPACE_MACOS_GUIDE.md"






