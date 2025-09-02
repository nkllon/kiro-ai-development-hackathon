#!/bin/bash
# GKE Turns 10 Hackathon - Quick Start Script
# One command to rule them all!

echo "🏆 GKE Turns 10 Hackathon - Quick Start"
echo "========================================"
echo "Building Multi-Enterprise Billing Management System"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3 first."
    exit 1
fi

# Check if gcloud is available
if ! command -v gcloud &> /dev/null; then
    echo "⚠️  gcloud CLI not found. Installing..."
    curl https://sdk.cloud.google.com | bash
    source ~/.bashrc
fi

echo "🚀 Starting GCP Auto Setup..."
echo "This will:"
echo "  • Generate billing account with $300 credits"
echo "  • Create GCP project"
echo "  • Generate service account keys"
echo "  • Enable all required APIs"
echo "  • Create GKE cluster"
echo "  • Setup billing exports"
echo ""

# Run the auto setup
python3 scripts/gcp_auto_setup.py

echo ""
echo "🎉 Setup Complete! You're ready for the hackathon!"
echo ""
echo "🎯 Next Steps:"
echo "1. Deploy Bank of Anthos on your GKE cluster"
echo "2. Build your AI-powered billing agents"
echo "3. Create your hackathon submission!"
echo ""
echo "Good luck with the GKE Turns 10 Hackathon! 🏆"
