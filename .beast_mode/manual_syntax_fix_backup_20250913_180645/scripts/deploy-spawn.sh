#!/bin/bash
# Deploy Beast Mode Spawn to Target Repository
# This script creates the spawn and optionally pushes to GitHub

set -e

SPAWN_TYPE=${1:-"gke-hackathon"}
TARGET_REPO=${2:-"https://github.com/louspringer/gke-ai-microservices-hackathon.git"}
PUSH_TO_GITHUB=${3:-"false"}

echo "🧬 Beast Mode Spawn Deployment"
echo "============================="
echo "Spawn Type: $SPAWN_TYPE"
echo "Target Repository: $TARGET_REPO"
echo "Push to GitHub: $PUSH_TO_GITHUB"
echo ""

case $SPAWN_TYPE in
    "gke-hackathon")
        echo "🚀 Deploying GKE Hackathon Spawn..."
        ./scripts/spawn-gke-hackathon.sh "gke-ai-microservices-hackathon" "../spawns/gke-ai-microservices-hackathon" "$TARGET_REPO"
        SPAWN_DIR="../spawns/gke-ai-microservices-hackathon"
        ;;
    *)
        echo "❌ Unknown spawn type: $SPAWN_TYPE"
        echo "Available spawn types: gke-hackathon"
        exit 1
        ;;
esac

# Optionally push to GitHub
if [ "$PUSH_TO_GITHUB" = "true" ]; then
    echo ""
    echo "📤 Pushing spawn to GitHub..."
    cd "$SPAWN_DIR"
    
    # Check if we have a remote
    if git remote get-url origin &> /dev/null; then
        echo "Pushing to existing remote..."
        git push -u origin main || git push -u origin master
    else
        echo "⚠️  No remote configured. Add remote manually:"
        echo "git remote add origin $TARGET_REPO"
        echo "git push -u origin main"
    fi
fi

echo ""
echo "🎉 Beast Mode Spawn Deployment Complete!"
echo "========================================"
echo "Spawn Location: $SPAWN_DIR"
echo ""
echo "🧬 The spawn contains complete Beast Mode DNA and is ready for:"
echo "- Fresh Kiro instance consumption"
echo "- Hackathon development and demonstration"
echo "- Systematic GKE Autopilot excellence"
echo ""
echo "🚀 To activate the spawn:"
echo "1. cd $SPAWN_DIR"
echo "2. ./scripts/deploy-autopilot.sh your-project-id"
echo "3. Demonstrate systematic superiority!"