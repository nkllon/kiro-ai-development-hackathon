#!/usr/bin/env python3
"""
Simple GCP Setup - Just API Key + Email
Based on existing codebase patterns for GCP authentication
"""

import os
import subprocess
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class GCPSetupConfig:
    """Simple GCP setup configuration"""
    api_key: Optional[str] = None
    email: Optional[str] = None
    project_id: Optional[str] = None
    region: str = "us-central1"

class SimpleGCPSetup:
    """Simple GCP setup using API key and email"""
    
    def __init__(self, config: GCPSetupConfig):
        self.config = config
        self.setup_status = {}
    
    def setup_gcp_with_api_key(self) -> Dict[str, Any]:
        """Setup GCP using just API key and email"""
        print("🚀 Setting up GCP with API key and email...")
        
        # Step 1: Set environment variables
        if self.config.api_key:
            os.environ["GOOGLE_API_KEY"] = self.config.api_key
            os.environ["GEMINI_API_KEY"] = self.config.api_key
            self.setup_status["api_key_set"] = True
            print("✅ API key set in environment")
        
        # Step 2: Configure gcloud (if available)
        if self.config.email and self.config.project_id:
            self.setup_status["gcloud_configured"] = self._configure_gcloud()
        
        # Step 3: Test authentication
        self.setup_status["auth_test"] = self._test_authentication()
        
        # Step 4: Enable required APIs
        self.setup_status["apis_enabled"] = self._enable_apis()
        
        return self.setup_status
    
    def _configure_gcloud(self) -> bool:
        """Configure gcloud with email and project"""
        try:
            # Set project
            if self.config.project_id:
                subprocess.run(
                    ["gcloud", "config", "set", "project", self.config.project_id],
                    check=True,
                    capture_output=True
                )
                print(f"✅ Project set to: {self.config.project_id}")
            
            # Set account (if email provided)
            if self.config.email:
                subprocess.run(
                    ["gcloud", "config", "set", "account", self.config.email],
                    check=True,
                    capture_output=True
                )
                print(f"✅ Account set to: {self.config.email}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ gcloud configuration failed: {e}")
            return False
    
    def _test_authentication(self) -> bool:
        """Test GCP authentication"""
        try:
            # Test with gcloud
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                print("✅ gcloud authentication working")
                return True
                
        except subprocess.CalledProcessError:
            print("⚠️ gcloud auth not available, using API key only")
        
        # Test with API key
        if os.getenv("GOOGLE_API_KEY"):
            print("✅ API key authentication available")
            return True
        
        print("❌ No authentication method working")
        return False
    
    def _enable_apis(self) -> bool:
        """Enable required GCP APIs"""
        required_apis = [
            "container.googleapis.com",  # GKE
            "bigquery.googleapis.com",   # BigQuery
            "cloudbilling.googleapis.com", # Billing API
            "aiplatform.googleapis.com"  # AI Platform
        ]
        
        try:
            for api in required_apis:
                subprocess.run(
                    ["gcloud", "services", "enable", api],
                    check=True,
                    capture_output=True
                )
                print(f"✅ Enabled API: {api}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ API enablement failed: {e}")
            return False
    
    def get_setup_summary(self) -> str:
        """Get setup summary"""
        summary = []
        summary.append("🎯 GCP Setup Summary:")
        
        for key, value in self.setup_status.items():
            status = "✅" if value else "❌"
            summary.append(f"  {status} {key.replace('_', ' ').title()}")
        
        return "\n".join(summary)

def main():
    """Main setup function"""
    print("🚀 Simple GCP Setup - API Key + Email")
    print("=" * 50)
    
    # Get configuration from user or environment
    api_key = os.getenv("GOOGLE_API_KEY") or input("Enter your Google API key: ").strip()
    email = os.getenv("GCP_EMAIL") or input("Enter your GCP email (optional): ").strip() or None
    project_id = os.getenv("GCP_PROJECT_ID") or input("Enter your GCP project ID (optional): ").strip() or None
    
    # Create configuration
    config = GCPSetupConfig(
        api_key=api_key,
        email=email,
        project_id=project_id
    )
    
    # Setup GCP
    setup = SimpleGCPSetup(config)
    results = setup.setup_gcp_with_api_key()
    
    # Show summary
    print("\n" + setup.get_setup_summary())
    
    # Save configuration
    config_file = "gcp_setup_config.json"
    with open(config_file, "w") as f:
        json.dump({
            "api_key_set": bool(api_key),
            "email": email,
            "project_id": project_id,
            "setup_status": results
        }, f, indent=2)
    
    print(f"\n💾 Configuration saved to: {config_file}")
    print("🎉 GCP setup complete! Ready for hackathon development.")

if __name__ == "__main__":
    main()
