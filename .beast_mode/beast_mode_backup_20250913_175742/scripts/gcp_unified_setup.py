#!/usr/bin/env python3
"""
GCP Unified Setup - Single Script with Proper State Management
Eliminates the state management nightmare with one clean script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gcp_state_manager import GCPStateManager, SetupType, SetupState
import json
import time

class GCPUnifiedSetup:
    """Unified GCP setup with proper state management"""
    
    def __init__(self):
        self.state_manager = GCPStateManager()
        self.setup_type = None
        self.configuration = {}
    
    def choose_setup_type(self) -> SetupType:
        """Choose setup type"""
        print("🎯 GCP Setup - Choose Your Scenario")
        print("=" * 40)
        print("1. Personal/Startup (Hackathon) - Create billing account with your payment method")
        print("2. Enterprise (Simple) - Use existing enterprise billing account")
        print("3. Enterprise (Full Authorization) - Complete authorization handshake")
        print()
        
        choice = input("Enter choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            return SetupType.PERSONAL
        elif choice == "2":
            return SetupType.ENTERPRISE
        elif choice == "3":
            return SetupType.AUTHORIZATION
        else:
            print("❌ Invalid choice")
            return self.choose_setup_type()
    
    def get_configuration(self, setup_type: SetupType) -> dict:
        """Get configuration based on setup type"""
        config = {}
        
        if setup_type == SetupType.PERSONAL:
            print("\n🎯 Personal/Startup Configuration")
            print("=" * 40)
            config["project_name"] = input("Enter project name: ").strip() or "hackathon-project"
            config["region"] = input("Enter region (default: us-central1): ").strip() or "us-central1"
            config["zone"] = input("Enter zone (default: us-central1-a): ").strip() or "us-central1-a"
            
        elif setup_type == SetupType.ENTERPRISE:
            print("\n🎯 Enterprise Configuration")
            print("=" * 40)
            config["billing_account_id"] = input("Enter enterprise billing account ID: ").strip()
            if not config["billing_account_id"]:
                print("❌ Billing account ID required")
                return self.get_configuration(setup_type)
            
            config["project_name"] = input("Enter project name: ").strip() or "enterprise-project"
            config["enterprise_domain"] = input("Enter enterprise domain: ").strip() or "enterprise.com"
            config["authorized_user"] = input("Enter your email: ").strip()
            if not config["authorized_user"]:
                print("❌ Authorized user email required")
                return self.get_configuration(setup_type)
                
        elif setup_type == SetupType.AUTHORIZATION:
            print("\n🎯 Enterprise Authorization Configuration")
            print("=" * 50)
            config["billing_account_id"] = input("Enter enterprise billing account ID: ").strip()
            if not config["billing_account_id"]:
                print("❌ Billing account ID required")
                return self.get_configuration(setup_type)
            
            config["project_name"] = input("Enter project name: ").strip() or "enterprise-project"
            config["enterprise_domain"] = input("Enter enterprise domain: ").strip() or "enterprise.com"
            config["developer_email"] = input("Enter your email (developer): ").strip()
            if not config["developer_email"]:
                print("❌ Developer email required")
                return self.get_configuration(setup_type)
            
            config["admin_email"] = input("Enter enterprise admin email: ").strip() or "admin@enterprise.com"
        
        return config
    
    def execute_step(self, step_id: str, step_name: str) -> dict:
        """Execute a setup step"""
        print(f"\n🚀 Executing: {step_name}")
        print("=" * 50)
        
        try:
            # Start step
            if not self.state_manager.start_step(step_id):
                return {"success": False, "error": "Failed to start step"}
            
            # Execute step based on step_id
            if step_id == "create_billing":
                result = self._create_billing_account()
            elif step_id == "create_project":
                result = self._create_project()
            elif step_id == "link_billing":
                result = self._link_billing_account()
            elif step_id == "enable_apis":
                result = self._enable_apis()
            elif step_id == "create_gke":
                result = self._create_gke_cluster()
            elif step_id == "setup_billing":
                result = self._setup_billing_exports()
            elif step_id == "verify_billing":
                result = self._verify_billing_account()
            elif step_id == "setup_iam":
                result = self._setup_iam_permissions()
            elif step_id == "request_auth":
                result = self._request_authorization()
            elif step_id == "admin_review":
                result = self._admin_review()
            elif step_id == "verify_auth":
                result = self._verify_authorization()
            elif step_id == "link_project":
                result = self._link_project_with_auth()
            elif step_id == "apply_iam":
                result = self._apply_iam_permissions()
            else:
                result = {"success": False, "error": f"Unknown step: {step_id}"}
            
            # Complete or fail step
            if result["success"]:
                self.state_manager.complete_step(step_id, result)
                print(f"✅ Completed: {step_name}")
            else:
                self.state_manager.fail_step(step_id, result["error"])
                print(f"❌ Failed: {step_name} - {result['error']}")
            
            return result
            
        except Exception as e:
            self.state_manager.fail_step(step_id, str(e))
            print(f"❌ Exception in {step_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_billing_account(self) -> dict:
        """Create billing account (simulated)"""
        print("💰 Creating billing account...")
        time.sleep(1)  # Simulate work
        return {"success": True, "billing_account_id": "01ABCD-EFGHIJ-KLMNOP"}
    
    def _create_project(self) -> dict:
        """Create project (simulated)"""
        print("🏗️ Creating project...")
        time.sleep(1)  # Simulate work
        return {"success": True, "project_id": f"project-{int(time.time())}"}
    
    def _link_billing_account(self) -> dict:
        """Link project to billing account (simulated)"""
        print("🔗 Linking project to billing account...")
        time.sleep(1)  # Simulate work
        return {"success": True, "linked": True}
    
    def _enable_apis(self) -> dict:
        """Enable required APIs (simulated)"""
        print("🔧 Enabling APIs...")
        time.sleep(2)  # Simulate work
        return {"success": True, "apis_enabled": 8}
    
    def _create_gke_cluster(self) -> dict:
        """Create GKE cluster (simulated)"""
        print("🚀 Creating GKE cluster...")
        time.sleep(3)  # Simulate work
        return {"success": True, "cluster_name": "hackathon-cluster"}
    
    def _setup_billing_exports(self) -> dict:
        """Setup billing exports (simulated)"""
        print("📊 Setting up billing exports...")
        time.sleep(1)  # Simulate work
        return {"success": True, "exports_configured": True}
    
    def _verify_billing_account(self) -> dict:
        """Verify billing account access (simulated)"""
        print("🔍 Verifying billing account access...")
        time.sleep(1)  # Simulate work
        return {"success": True, "access_verified": True}
    
    def _setup_iam_permissions(self) -> dict:
        """Setup IAM permissions (simulated)"""
        print("🔐 Setting up IAM permissions...")
        time.sleep(1)  # Simulate work
        return {"success": True, "permissions_set": True}
    
    def _request_authorization(self) -> dict:
        """Request authorization (simulated)"""
        print("🤝 Requesting authorization...")
        time.sleep(1)  # Simulate work
        return {"success": True, "request_id": f"req_{int(time.time())}"}
    
    def _admin_review(self) -> dict:
        """Admin review (simulated)"""
        print("🏢 Admin reviewing request...")
        time.sleep(2)  # Simulate work
        return {"success": True, "approved": True}
    
    def _verify_authorization(self) -> dict:
        """Verify authorization (simulated)"""
        print("🔍 Verifying authorization...")
        time.sleep(1)  # Simulate work
        return {"success": True, "authorized": True}
    
    def _link_project_with_auth(self) -> dict:
        """Link project with authorization (simulated)"""
        print("🔗 Linking project with authorization...")
        time.sleep(1)  # Simulate work
        return {"success": True, "linked_with_auth": True}
    
    def _apply_iam_permissions(self) -> dict:
        """Apply IAM permissions (simulated)"""
        print("🔐 Applying IAM permissions...")
        time.sleep(1)  # Simulate work
        return {"success": True, "permissions_applied": True}
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 GCP Unified Setup")
        print("=" * 30)
        print("Single script with proper state management")
        print()
        
        # Choose setup type
        self.setup_type = self.choose_setup_type()
        
        # Get configuration
        self.configuration = self.get_configuration(self.setup_type)
        
        # Create session
        session_id = self.state_manager.create_session(self.setup_type, self.configuration)
        print(f"\n✅ Created setup session: {session_id}")
        
        # Execute steps
        while True:
            next_step = self.state_manager.get_next_step()
            if not next_step:
                break
            
            result = self.execute_step(next_step.step_id, next_step.step_name)
            if not result["success"]:
                print(f"\n❌ Setup failed at step: {next_step.step_name}")
                print("🔄 Would you like to rollback? (y/n): ", end="")
                if input().lower() == 'y':
                    self.state_manager.rollback_session()
                break
        
        # Check if setup is complete
        if self.state_manager.is_session_complete():
            print("\n🎉 Setup Complete!")
            print("=" * 30)
            print("✅ All steps completed successfully")
            print("✅ GCP environment ready for development")
        else:
            print("\n⚠️ Setup Incomplete")
            print("=" * 30)
            print("Some steps failed or were not completed")
        
        # Show final status
        status = self.state_manager.get_session_status()
        print(f"\n📊 Final Status:")
        print(json.dumps(status, indent=2))

def main():
    """Main setup function"""
    setup = GCPUnifiedSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
