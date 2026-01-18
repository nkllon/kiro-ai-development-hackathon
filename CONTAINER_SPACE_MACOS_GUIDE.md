# Container Disk Space Management for macOS

## 🎯 Goal: Reclaim 50-100+ GB from Container Storage

Container systems on macOS can consume massive amounts of disk space through multiple mechanisms. This guide helps you identify and reclaim that space.

## 📊 Where Container Space Goes on macOS

### Docker Desktop for Mac
The biggest culprit! Docker Desktop stores everything in a **single large disk image**:

```bash
# Main Docker disk image location
~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw
```

This file can grow to **50-200+ GB** and NEVER shrinks automatically!

### Other Container Runtimes
- **OrbStack**: `~/Library/Containers/com.orbstack.OrbStack/`
- **Podman**: `~/.local/share/containers/`
- **Colima**: `~/.colima/`
- **Lima**: `~/.lima/`

## 🔍 Quick Space Assessment

### Check Docker Desktop Disk Usage
```bash
# Check Docker disk image size
du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw

# Check Docker system-wide usage
docker system df

# Detailed breakdown
docker system df -v
```

### Check Container Runtime Space
```bash
# Check all container-related directories
du -sh ~/Library/Containers/com.docker.docker 2>/dev/null
du -sh ~/Library/Containers/com.orbstack.OrbStack 2>/dev/null
du -sh ~/.local/share/containers 2>/dev/null
du -sh ~/.colima 2>/dev/null
du -sh ~/.lima 2>/dev/null
```

## 🧹 Cleanup Commands

### 1. Clean Docker Images, Containers, and Volumes

```bash
# Stop all running containers
docker stop $(docker ps -aq)

# Remove all stopped containers
docker container prune -f

# Remove all unused images (not just dangling)
docker image prune -a -f

# Remove all unused volumes
docker volume prune -f

# Remove all build cache
docker builder prune -a -f

# Nuclear option: Clean EVERYTHING
docker system prune -a --volumes -f
```

**Expected savings**: 10-50 GB

### 2. Shrink Docker.raw (macOS Specific!)

Docker Desktop's disk image **never shrinks automatically**. You must manually reclaim space:

#### Method A: Using Docker Desktop GUI
1. Open Docker Desktop
2. Go to: Settings → Resources → Advanced
3. Click "Disk image location"
4. Note the current size
5. Go to: Troubleshooting (bug icon)
6. Click "Clean / Purge data"
7. **WARNING**: This removes all containers, images, volumes!

#### Method B: Command Line (Safer)
```bash
# 1. Clean up Docker first
docker system prune -a --volumes -f

# 2. Quit Docker Desktop completely
osascript -e 'quit app "Docker"'
killall Docker

# 3. Wait a moment
sleep 5

# 4. Check current size
ls -lh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw

# 5. Create a new, smaller disk image
# NOTE: This requires Docker Desktop to be stopped
# Start Docker Desktop, it will compact on startup
open -a Docker

# Alternative: Use docker disk image shrink (if available in newer versions)
# This may not work on all Docker Desktop versions
```

#### Method C: Manual Disk Image Compaction (Advanced)
```bash
# 1. Backup important containers/volumes first!

# 2. Stop Docker completely
osascript -e 'quit app "Docker"'
killall Docker
sleep 5

# 3. Locate the disk image
cd ~/Library/Containers/com.docker.docker/Data/vms/0/data/

# 4. Check current size
du -sh Docker.raw

# 5. Convert to QCOW2 format (compresses)
# Requires qemu-img (install via: brew install qemu)
qemu-img convert -O qcow2 Docker.raw Docker.qcow2

# 6. Convert back to raw (now compacted)
qemu-img convert -O raw Docker.qcow2 Docker.raw.new

# 7. Replace old with new
mv Docker.raw Docker.raw.backup
mv Docker.raw.new Docker.raw

# 8. Restart Docker
open -a Docker

# 9. Verify everything works, then remove backup
# rm Docker.raw.backup Docker.qcow2
```

**Expected savings**: 20-100 GB

### 3. Reset Docker Desktop Completely

If nothing else works:

```bash
# 1. Export any important containers/volumes first!

# 2. Uninstall Docker Desktop
# Open Docker Desktop → Preferences → Uninstall

# 3. Remove all Docker data manually
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/Library/Application\ Support/Docker\ Desktop
rm -rf ~/Library/Group\ Containers/group.com.docker
rm -rf ~/.docker

# 4. Reinstall Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop/

# 5. Configure with smaller disk size
# Settings → Resources → Disk image size: 64GB instead of default
```

**Expected savings**: 50-150 GB

## 🎯 Targeting Specific Waste

### Find Largest Docker Images
```bash
# Sort images by size
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k 3 -h

# Find images over 1GB
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | grep GB
```

### Find Orphaned Volumes
```bash
# List all volumes with their size (requires jq)
docker volume ls -q | xargs -I {} docker volume inspect {} | \
  jq -r '.[] | "\(.Name)\t\(.Mountpoint)"' | \
  xargs -I {} sh -c 'echo -n "{}  "; du -sh $(echo {} | cut -f2)'

# Remove specific volume
docker volume rm volume_name
```

### Find Old Build Cache
```bash
# Show build cache usage
docker buildx du

# Clean build cache older than 7 days
docker builder prune --filter "until=168h" -f
```

### Find Stopped Containers Using Space
```bash
# List stopped containers with size
docker ps -as --filter "status=exited"

# Remove specific container
docker rm container_id_or_name
```

## 🔧 Alternative Container Runtimes for macOS

If Docker Desktop is too bloated, consider alternatives:

### OrbStack (Recommended)
- Much more efficient than Docker Desktop
- Typically uses 70% less disk space
- Compatible with Docker CLI

```bash
# Install
brew install orbstack

# Check usage
du -sh ~/Library/Containers/com.orbstack.OrbStack
```

### Colima
- Lightweight Docker Desktop alternative
- Uses Lima VMs

```bash
# Install
brew install colima docker

# Start with custom disk size
colima start --disk 60

# Check disk usage
du -sh ~/.colima
```

### Podman
- Daemonless container engine
- More efficient storage

```bash
# Install
brew install podman

# Initialize with custom disk
podman machine init --disk-size 60

# Check usage
du -sh ~/.local/share/containers
```

## 🚨 macOS-Specific Container Issues

### Issue 1: Docker.raw Never Shrinks
**Problem**: Even after deleting containers/images, Docker.raw stays large.

**Solution**: Must manually compact (see Method C above) or reset Docker.

### Issue 2: Time Machine Backing Up Docker.raw
**Problem**: Time Machine backs up the huge Docker.raw file.

**Solution**: Exclude from Time Machine:
```bash
# Exclude Docker from Time Machine
tmutil addexclusion ~/Library/Containers/com.docker.docker
```

### Issue 3: Multiple Container Runtimes
**Problem**: Having Docker Desktop, OrbStack, Podman all installed.

**Solution**: Pick one and remove the others:
```bash
# Check what's installed
ls -d ~/Library/Containers/com.docker.docker 2>/dev/null
ls -d ~/Library/Containers/com.orbstack.OrbStack 2>/dev/null
ls -d ~/.local/share/containers 2>/dev/null
ls -d ~/.colima 2>/dev/null
```

## 📊 Expected Savings Breakdown

| Cleanup Action | Typical Savings | Difficulty |
|----------------|-----------------|------------|
| `docker system prune -a --volumes` | 10-50 GB | Easy |
| Shrink Docker.raw | 20-100 GB | Medium |
| Remove unused container runtimes | 10-50 GB | Easy |
| Reset Docker Desktop | 50-150 GB | Medium |
| Switch to OrbStack/Colima | 30-100 GB | Medium |
| **TOTAL POTENTIAL** | **50-200+ GB** | - |

## 🛡️ Prevention Strategies

### 1. Set Disk Limits
```bash
# Docker Desktop: Settings → Resources → Disk image size
# Set to reasonable limit (e.g., 64 GB instead of 200 GB)
```

### 2. Regular Cleanup Script
```bash
#!/bin/bash
# Save as: ~/bin/docker-cleanup.sh

echo "🧹 Docker cleanup starting..."

# Stop old containers
docker container prune -f

# Remove dangling images
docker image prune -f

# Remove old build cache (>7 days)
docker builder prune --filter "until=168h" -f

# Show current usage
echo ""
echo "📊 Current Docker disk usage:"
docker system df

# Show Docker.raw size
echo ""
echo "💾 Docker.raw size:"
du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw 2>/dev/null || echo "Not found"
```

```bash
# Make executable
chmod +x ~/bin/docker-cleanup.sh

# Run weekly via cron
# Add to crontab: 0 2 * * 0 ~/bin/docker-cleanup.sh
```

### 3. Use .dockerignore
```bash
# In your project root
cat > .dockerignore << 'EOF'
node_modules
.git
.env
*.log
.DS_Store
__pycache__
*.pyc
.venv
EOF
```

### 4. Multi-stage Docker Builds
```dockerfile
# Use multi-stage builds to reduce final image size
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Final stage - only production dependencies
FROM node:18-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## 🔍 Comprehensive Analysis Script

Save this as `analyze_container_space.sh`:

```bash
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
        SIZE=$(du -sk "$dir" | cut -f1)
        TOTAL=$((TOTAL + SIZE))
    fi
done

# Convert to GB
TOTAL_GB=$(echo "scale=2; $TOTAL / 1024 / 1024" | bc)
echo "  Total: ${TOTAL_GB} GB"
echo ""

# Recommendations
echo "💡 Recommendations:"
if [ -f ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw ]; then
    DOCKER_RAW_SIZE=$(du -sk ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw | cut -f1)
    DOCKER_RAW_GB=$(echo "scale=2; $DOCKER_RAW_SIZE / 1024 / 1024" | bc)
    if (( $(echo "$DOCKER_RAW_GB > 50" | bc -l) )); then
        echo "  ⚠️  Docker.raw is ${DOCKER_RAW_GB} GB - consider shrinking"
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
```

```bash
# Make executable
chmod +x analyze_container_space.sh

# Run it
./analyze_container_space.sh
```

## 🚀 Quick Action Plan

### Immediate (5 minutes)
```bash
# 1. Check current usage
docker system df
du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw

# 2. Clean up containers, images, volumes
docker system prune -a --volumes -f

# Expected savings: 10-50 GB
```

### Short-term (30 minutes)
```bash
# 3. Shrink Docker.raw (requires restart)
osascript -e 'quit app "Docker"'
# Wait for Docker to fully quit, then start it again
open -a Docker

# OR use Docker Desktop GUI:
# Settings → Troubleshooting → Clean / Purge data

# Expected savings: 20-100 GB
```

### Long-term (1-2 hours)
```bash
# 4. Consider switching to OrbStack (more efficient)
brew install orbstack

# 5. Set up automated cleanup
# Create cleanup script (see above)
# Schedule weekly via cron or launchd

# Expected savings: 30-100 GB + ongoing efficiency
```

## 📝 Tracking Your Cleanup

Create a cleanup log:

```bash
cat > ~/container_cleanup_log.txt << EOF
Container Cleanup Log
=====================
Date: $(date)

Before Cleanup:
---------------
Docker.raw size: $(du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw 2>/dev/null | cut -f1 || echo "N/A")
Total container space: $(./analyze_container_space.sh | grep "Total:" | awk '{print $2}')

Actions Taken:
--------------
- [ ] docker system prune -a --volumes -f
- [ ] Shrank Docker.raw
- [ ] Removed unused container runtimes
- [ ] Switched to OrbStack/Colima
- [ ] Set disk limits
- [ ] Added to Time Machine exclusions

After Cleanup:
--------------
Docker.raw size: 
Total container space: 
Space reclaimed: 

Notes:
------

EOF

# Edit the log after cleanup
open ~/container_cleanup_log.txt
```

## 🔗 Related Files in This Project

Based on your workspace, you have:
- `docker-compose.yml` - Main compose configuration
- `docker-compose.redis.yml` - Redis services
- `docker-compose.jaeger.yml` - Jaeger tracing
- `docker-compose.directus-fixed.yml` - Directus CMS
- `Dockerfile` - Container build configuration
- `docker-entrypoint.sh` - Container startup script

To clean up project-specific containers:

```bash
# Stop and remove all project containers
docker-compose down --volumes --remove-orphans

# Remove project images
docker images | grep kiro | awk '{print $3}' | xargs docker rmi -f

# Rebuild clean when needed
docker-compose build --no-cache
```

---

**Remember**: On macOS, Docker Desktop's `Docker.raw` file is the #1 space consumer and it NEVER shrinks automatically. You must manually compact it or reset Docker Desktop to reclaim space!

**Expected Total Savings**: 50-200+ GB
**Time Investment**: 30 minutes to 2 hours depending on method
**Monthly Savings**: $0 (local storage)






