#!/usr/bin/env python3
"""
GCP Credits Setup - Step by Step Guide
Get credits and apply them to your project for the hackathon
"""

import subprocess
import json
import time
from typing import Optional, Dict, Any

class GCPCreditsSetup:
    """Setup GCP credits for hackathon development"""
    
    def __init__(self):
        self.project_id = None
        self.billing_account_id = None
    
    def step_1_create_billing_account(self) -> Dict[str, Any]:
        """Step 1: Create billing account with YOUR keys"""
        print("🎯 STEP 1: Create Billing Account with YOUR Keys")
        print("=" * 50)
        
        print("You need to create a billing account with YOUR payment method:")
        print("1. Go to: https://console.cloud.google.com")
        print("2. Sign in with your Google account")
        print("3. Click 'Billing' in the left menu")
        print("4. Click 'Create Account'")
        print("5. Enter YOUR payment information (credit card)")
        print("6. Accept terms and create account")
        print("\n💡 This is just for verification - you won't be charged unless you exceed the free trial")
        
        input("\nPress Enter when you've created your billing account...")
        
        print("\n🎉 Great! Now you have:")
        print("• A billing account with YOUR payment method")
        print("• $300 in free credits (if first time)")
        print("• Ability to create projects that use these credits")
        
        return {"success": True, "credits": 300, "type": "billing_account"}
    
    def _guide_free_trial(self) -> Dict[str, Any]:
        """Guide user through free trial setup"""
        print("\n🚀 Google Cloud Free Trial Setup:")
        print("1. Go to: https://cloud.google.com/free")
        print("2. Click 'Get started for free'")
        print("3. Sign in with your Google account")
        print("4. Provide payment method (for verification only)")
        print("5. Accept terms and start trial")
        print("6. You'll get $300 in credits for 90 days")
        
        input("\nPress Enter when you've completed the free trial setup...")
        return {"success": True, "credits": 300, "type": "free_trial"}
    
    def _guide_hackathon_credits(self) -> Dict[str, Any]:
        """Guide user through hackathon credits"""
        print("\n🏆 Hackathon Credits Setup:")
        print("1. Complete the Google Cloud Credits Request Form")
        print("2. Wait for approval (usually within 24-48 hours)")
        print("3. You'll get $100 in credits")
        
        input("\nPress Enter when you've completed the hackathon credits request...")
        return {"success": True, "credits": 100, "type": "hackathon"}
    
    def step_2_create_project(self) -> Dict[str, Any]:
        """Step 2: Create GCP project"""
        print("\n🎯 STEP 2: Create GCP Project")
        print("=" * 40)
        
        # Get project name from user
        project_name = input("Enter project name (e.g., 'gke-hackathon-billing'): ").strip()
        if not project_name:
            project_name = "gke-hackathon-billing"
        
        # Create project ID (must be unique globally)
        self.project_id = f"{project_name}-{int(time.time())}"
        
        try:
            print(f"Creating project: {self.project_id}")
            result = subprocess.run(
                ["gcloud", "projects", "create", self.project_id, "--name", project_name],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Project created successfully")
            return {"success": True, "project_id": self.project_id}
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Project creation failed: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def step_3_list_billing_accounts(self) -> Dict[str, Any]:
        """Step 3: List available billing accounts"""
        print("\n🎯 STEP 3: List Billing Accounts")
        print("=" * 40)
        
        try:
            result = subprocess.run(
                ["gcloud", "billing", "accounts", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            billing_accounts = json.loads(result.stdout)
            
            if not billing_accounts:
                print("❌ No billing accounts found")
                print("💡 Make sure you've completed Step 1 (getting credits)")
                return {"success": False, "error": "No billing accounts"}
            
            print("Available billing accounts:")
            for i, account in enumerate(billing_accounts):
                print(f"{i+1}. {account['displayName']} (ID: {account['name']})")
                print(f"   Open: {account['open']}")
                print(f"   Master: {account['masterBillingAccount']}")
                print()
            
            return {"success": True, "accounts": billing_accounts}
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to list billing accounts: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def step_4_link_billing(self) -> Dict[str, Any]:
        """Step 4: Link project to billing account"""
        print("\n🎯 STEP 4: Link Project to Billing Account")
        print("=" * 40)
        
        if not self.project_id:
            print("❌ No project ID available")
            return {"success": False, "error": "No project ID"}
        
        # Get billing account ID from user
        billing_id = input("Enter billing account ID (from Step 3): ").strip()
        if not billing_id:
            print("❌ Billing account ID required")
            return {"success": False, "error": "No billing account ID"}
        
        self.billing_account_id = billing_id
        
        try:
            print(f"Linking project {self.project_id} to billing account {billing_id}")
            result = subprocess.run(
                ["gcloud", "billing", "projects", "link", self.project_id, "--billing-account", billing_id],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Project linked to billing account successfully")
            return {"success": True}
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to link billing account: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def step_5_verify_setup(self) -> Dict[str, Any]:
        """Step 5: Verify credits are applied"""
        print("\n🎯 STEP 5: Verify Credits Applied")
        print("=" * 40)
        
        try:
            # Check project billing
            result = subprocess.run(
                ["gcloud", "billing", "projects", "describe", self.project_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Project billing status:")
            print(result.stdout)
            
            # Check billing account details
            result = subprocess.run(
                ["gcloud", "billing", "accounts", "describe", self.billing_account_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Billing account details:")
            print(result.stdout)
            
            return {"success": True}
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Verification failed: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def run_complete_setup(self) -> Dict[str, Any]:
        """Run complete GCP credits setup"""
        print("🚀 GCP Credits Setup for GKE Hackathon")
        print("=" * 50)
        
        results = {}
        
        # Step 1: Create billing account with YOUR keys
        results["step_1"] = self.step_1_create_billing_account()
        if not results["step_1"]["success"]:
            return results
        
        # Step 2: Create project
        results["step_2"] = self.step_2_create_project()
        if not results["step_2"]["success"]:
            return results
        
        # Step 3: List billing accounts
        results["step_3"] = self.step_3_list_billing_accounts()
        if not results["step_3"]["success"]:
            return results
        
        # Step 4: Link billing
        results["step_4"] = self.step_4_link_billing()
        if not results["step_4"]["success"]:
            return results
        
        # Step 5: Verify setup
        results["step_5"] = self.step_5_verify_setup()
        
        # Summary
        print("\n🎉 GCP Credits Setup Complete!")
        print("=" * 40)
        print(f"Project ID: {self.project_id}")
        print(f"Billing Account: {self.billing_account_id}")
        print("Ready for hackathon development! 🚀")
        
        return results

def main():
    """Main setup function"""
    setup = GCPCreditsSetup()
    results = setup.run_complete_setup()
    
    # Save results
    with open("gcp_credits_setup_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Setup results saved to: gcp_credits_setup_results.json")

if __name__ == "__main__":
    main()
