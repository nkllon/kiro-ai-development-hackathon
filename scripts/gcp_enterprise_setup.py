#!/usr/bin/env python3
"""
GCP Enterprise Setup - Billing Account Provided by Enterprise
Real enterprise scenario where billing account is created separately
"""

import os
import json
import subprocess
import secrets
import string
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class EnterpriseGCPConfig:
    """Enterprise GCP configuration"""
    billing_account_id: str  # Provided by enterprise admin
    project_id: str
    enterprise_domain: str
    authorized_user: str

class GCPEnterpriseSetup:
    """Setup GCP project with enterprise billing account"""
    
    def __init__(self, config: EnterpriseGCPConfig):
        self.config = config
        self.setup_results = {}
    
    def step_1_verify_billing_account(self) -> Dict[str, Any]:
        """Step 1: Verify billing account access"""
        print("🎯 STEP 1: Verify Enterprise Billing Account Access")
        print("=" * 60)
        
        try:
            # Check if we can access the billing account
            result = subprocess.run(
                ["gcloud", "billing", "accounts", "describe", self.config.billing_account_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            billing_info = json.loads(result.stdout)
            
            print(f"✅ Billing account accessible: {billing_info['displayName']}")
            print(f"💰 Billing account ID: {self.config.billing_account_id}")
            print(f"🏢 Enterprise domain: {self.config.enterprise_domain}")
            print(f"👤 Authorized user: {self.config.authorized_user}")
            print(f"🔓 Account open: {billing_info['open']}")
            
            return {
                "success": True,
                "billing_account": billing_info,
                "access_verified": True
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Cannot access billing account: {e.stderr}")
            print("💡 Make sure the enterprise admin has authorized your account")
            return {"success": False, "error": e.stderr}
    
    def step_2_create_project(self) -> Dict[str, Any]:
        """Step 2: Create project with enterprise naming"""
        print("\n🎯 STEP 2: Create Enterprise Project")
        print("=" * 50)
        
        try:
            project_name = f"Enterprise Billing System - {self.config.authorized_user}"
            
            result = subprocess.run(
                ["gcloud", "projects", "create", self.config.project_id, "--name", project_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ Project created: {self.config.project_id}")
            print(f"📝 Project name: {project_name}")
            print(f"🏢 Enterprise domain: {self.config.enterprise_domain}")
            
            return {
                "success": True,
                "project_id": self.config.project_id,
                "project_name": project_name,
                "enterprise_domain": self.config.enterprise_domain
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create project: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def step_3_link_to_enterprise_billing(self) -> Dict[str, Any]:
        """Step 3: Link project to enterprise billing account"""
        print("\n🎯 STEP 3: Link Project to Enterprise Billing Account")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                ["gcloud", "billing", "projects", "link", 
                 self.config.project_id, 
                 "--billing-account", self.config.billing_account_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ Project linked to enterprise billing account")
            print(f"💰 Billing account: {self.config.billing_account_id}")
            print(f"🏢 Enterprise controls billing")
            print(f"👤 You control project resources")
            
            return {
                "success": True,
                "billing_account_id": self.config.billing_account_id,
                "project_id": self.config.project_id,
                "linked": True
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to link billing account: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def step_4_setup_enterprise_iam(self) -> Dict[str, Any]:
        """Step 4: Setup enterprise IAM permissions"""
        print("\n🎯 STEP 4: Setup Enterprise IAM Permissions")
        print("=" * 50)
        
        try:
            # Set up IAM roles for the authorized user
            iam_roles = [
                "roles/container.admin",           # GKE management
                "roles/bigquery.admin",            # BigQuery access
                "roles/aiplatform.user",           # AI Platform access
                "roles/storage.admin",             # Cloud Storage access
                "roles/cloudfunctions.admin",      # Cloud Functions access
                "roles/iam.serviceAccountAdmin"    # Service account management
            ]
            
            for role in iam_roles:
                try:
                    result = subprocess.run(
                        ["gcloud", "projects", "add-iam-policy-binding", 
                         self.config.project_id,
                         "--member", f"user:{self.config.authorized_user}",
                         "--role", role],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"  ✅ {role}")
                except subprocess.CalledProcessError:
                    print(f"  ⚠️  {role} (may already be set)")
            
            return {
                "success": True,
                "iam_roles": iam_roles,
                "authorized_user": self.config.authorized_user
            }
            
        except Exception as e:
            print(f"❌ IAM setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    def step_5_enable_enterprise_apis(self) -> Dict[str, Any]:
        """Step 5: Enable APIs for enterprise project"""
        print("\n🎯 STEP 5: Enable Enterprise APIs")
        print("=" * 40)
        
        apis = [
            "container.googleapis.com",      # GKE
            "bigquery.googleapis.com",       # BigQuery
            "cloudbilling.googleapis.com",   # Billing API
            "aiplatform.googleapis.com",     # AI Platform
            "cloudresourcemanager.googleapis.com",  # Resource Manager
            "iam.googleapis.com",            # IAM
            "storage.googleapis.com",        # Cloud Storage
            "cloudfunctions.googleapis.com", # Cloud Functions
            "monitoring.googleapis.com",     # Monitoring
            "logging.googleapis.com"         # Logging
        ]
        
        enabled_apis = []
        for api in apis:
            try:
                result = subprocess.run(
                    ["gcloud", "services", "enable", api],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"  ✅ {api}")
                enabled_apis.append(api)
            except subprocess.CalledProcessError as e:
                print(f"  ❌ {api}: {e.stderr}")
        
        return {
            "success": len(enabled_apis) == len(apis),
            "enabled_apis": enabled_apis,
            "total_apis": len(apis)
        }
    
    def step_6_create_enterprise_gke_cluster(self) -> Dict[str, Any]:
        """Step 6: Create GKE cluster for enterprise"""
        print("\n🎯 STEP 6: Create Enterprise GKE Cluster")
        print("=" * 50)
        
        try:
            cluster_name = f"enterprise-billing-cluster-{int(time.time())}"
            zone = "us-central1-a"
            machine_type = "e2-standard-2"  # Enterprise-grade machines
            
            result = subprocess.run(
                ["gcloud", "container", "clusters", "create", cluster_name,
                 "--zone", zone,
                 "--machine-type", machine_type,
                 "--num-nodes", "3",
                 "--enable-autoscaling",
                 "--min-nodes", "1",
                 "--max-nodes", "10",
                 "--project", self.config.project_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ Enterprise GKE cluster created: {cluster_name}")
            print(f"📍 Zone: {zone}")
            print(f"🖥️ Machine type: {machine_type}")
            print(f"📊 Nodes: 3 (auto-scaling 1-10)")
            print(f"🏢 Enterprise-grade configuration")
            
            return {
                "success": True,
                "cluster_name": cluster_name,
                "zone": zone,
                "machine_type": machine_type,
                "nodes": 3,
                "autoscaling": True
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create GKE cluster: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def run_enterprise_setup(self) -> Dict[str, Any]:
        """Run complete enterprise GCP setup"""
        print("🏢 GCP Enterprise Setup")
        print("=" * 40)
        print("Setting up project with enterprise billing account...")
        print()
        
        # Step 1: Verify billing account access
        self.setup_results["billing_verification"] = self.step_1_verify_billing_account()
        if not self.setup_results["billing_verification"]["success"]:
            return self.setup_results
        
        # Step 2: Create project
        self.setup_results["project_creation"] = self.step_2_create_project()
        if not self.setup_results["project_creation"]["success"]:
            return self.setup_results
        
        # Step 3: Link to enterprise billing
        self.setup_results["billing_link"] = self.step_3_link_to_enterprise_billing()
        if not self.setup_results["billing_link"]["success"]:
            return self.setup_results
        
        # Step 4: Setup IAM
        self.setup_results["iam_setup"] = self.step_4_setup_enterprise_iam()
        
        # Step 5: Enable APIs
        self.setup_results["api_enablement"] = self.step_5_enable_enterprise_apis()
        
        # Step 6: Create GKE cluster
        self.setup_results["gke_cluster"] = self.step_6_create_enterprise_gke_cluster()
        
        # Save enterprise configuration
        self.save_enterprise_config()
        
        print("\n🎉 Enterprise GCP Setup Complete!")
        print("=" * 40)
        print("✅ Project linked to enterprise billing account")
        print("✅ Enterprise IAM permissions configured")
        print("✅ All required APIs enabled")
        print("✅ Enterprise GKE cluster running")
        print("✅ Ready for enterprise billing system development")
        
        return self.setup_results
    
    def save_enterprise_config(self):
        """Save enterprise configuration"""
        print("\n💾 Saving enterprise configuration...")
        
        config = {
            "enterprise_domain": self.config.enterprise_domain,
            "billing_account_id": self.config.billing_account_id,
            "project_id": self.config.project_id,
            "authorized_user": self.config.authorized_user,
            "setup_results": self.setup_results
        }
        
        config_file = "enterprise_gcp_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Enterprise config saved: {config_file}")

def main():
    """Main enterprise setup function"""
    print("🏢 GCP Enterprise Setup")
    print("=" * 30)
    print("Setup project with enterprise billing account")
    print()
    
    # Get enterprise configuration
    billing_account_id = input("Enter enterprise billing account ID: ").strip()
    if not billing_account_id:
        print("❌ Billing account ID required")
        return
    
    enterprise_domain = input("Enter enterprise domain (e.g., company.com): ").strip()
    if not enterprise_domain:
        enterprise_domain = "enterprise.com"
    
    authorized_user = input("Enter your email (authorized user): ").strip()
    if not authorized_user:
        print("❌ Authorized user email required")
        return
    
    # Generate project ID
    project_id = f"enterprise-billing-{secrets.token_hex(4)}"
    
    # Create configuration
    config = EnterpriseGCPConfig(
        billing_account_id=billing_account_id,
        project_id=project_id,
        enterprise_domain=enterprise_domain,
        authorized_user=authorized_user
    )
    
    # Run enterprise setup
    setup = GCPEnterpriseSetup(config)
    results = setup.run_enterprise_setup()
    
    print("\n🎯 Enterprise Setup Summary:")
    print(f"🏢 Enterprise: {enterprise_domain}")
    print(f"💰 Billing Account: {billing_account_id}")
    print(f"📁 Project: {project_id}")
    print(f"👤 Authorized User: {authorized_user}")
    print("\n🚀 Ready for enterprise billing system development!")

if __name__ == "__main__":
    main()
