#!/usr/bin/env python3
"""
GCP Quick Start - Minimal Setup for Hackathon
Just provide API key and email, everything else is automated
"""

import os
import subprocess
import json
from typing import Optional

def quick_gcp_setup(api_key: str, email: Optional[str] = None, project_id: Optional[str] = None):
    """
    Quick GCP setup with minimal requirements
    
    Args:
        api_key: Your Google API key
        email: Your GCP email (optional)
        project_id: Your GCP project ID (optional)
    """
    print("🚀 GCP Quick Start for GKE Hackathon")
    print("=" * 40)
    
    # Set API key
    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GEMINI_API_KEY"] = api_key
    print("✅ API key configured")
    
    # Configure gcloud if email/project provided
    if email and project_id:
        try:
            subprocess.run(["gcloud", "config", "set", "project", project_id], check=True)
            subprocess.run(["gcloud", "config", "set", "account", email], check=True)
            print(f"✅ gcloud configured: {email} -> {project_id}")
        except subprocess.CalledProcessError:
            print("⚠️ gcloud not available, using API key only")
    
    # Test authentication
    auth_working = test_authentication()
    
    # Enable APIs if gcloud is working
    if auth_working:
        enable_apis()
    
    print("\n🎉 GCP Quick Start Complete!")
    print("Ready to build your multi-enterprise billing system! 🚀")

def test_authentication() -> bool:
    """Test if authentication is working"""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            print("✅ Authentication working")
            return True
    except subprocess.CalledProcessError:
        pass
    
    if os.getenv("GOOGLE_API_KEY"):
        print("✅ API key authentication available")
        return True
    
    print("❌ Authentication not working")
    return False

def enable_apis():
    """Enable required APIs for our billing system"""
    apis = [
        "container.googleapis.com",      # GKE
        "bigquery.googleapis.com",       # BigQuery
        "cloudbilling.googleapis.com",   # Billing API
        "aiplatform.googleapis.com",     # AI Platform
        "cloudresourcemanager.googleapis.com"  # Resource Manager
    ]
    
    print("🔧 Enabling required APIs...")
    for api in apis:
        try:
            subprocess.run(
                ["gcloud", "services", "enable", api],
                check=True,
                capture_output=True
            )
            print(f"  ✅ {api}")
        except subprocess.CalledProcessError:
            print(f"  ❌ {api}")

def main():
    """Interactive quick start"""
    print("🎯 GCP Quick Start for GKE Turns 10 Hackathon")
    print("Building Multi-Enterprise Billing Management System")
    print("=" * 60)
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = input("Enter your Google API key: ").strip()
        if not api_key:
            print("❌ API key required")
            return
    
    # Get optional email and project
    email = input("Enter your GCP email (optional): ").strip() or None
    project_id = input("Enter your GCP project ID (optional): ").strip() or None
    
    # Run quick setup
    quick_gcp_setup(api_key, email, project_id)
    
    print("\n🎯 Next Steps:")
    print("1. Deploy Bank of Anthos on GKE")
    print("2. Build your AI-powered billing agents")
    print("3. Create your hackathon submission!")
    print("\nGood luck with the GKE Turns 10 Hackathon! 🏆")

if __name__ == "__main__":
    main()
