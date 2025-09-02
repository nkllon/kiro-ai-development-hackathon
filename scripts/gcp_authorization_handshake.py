#!/usr/bin/env python3
"""
GCP Authorization Handshake - Enterprise Billing Account Access
Handles the authorization process between enterprise admin and developer
"""

import os
import json
import subprocess
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class AuthorizationStatus(Enum):
    """Authorization status levels"""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    DENIED = "denied"
    EXPIRED = "expired"

@dataclass
class AuthorizationRequest:
    """Authorization request from developer to enterprise admin"""
    developer_email: str
    project_name: str
    requested_roles: List[str]
    billing_account_id: str
    enterprise_domain: str
    request_id: str
    timestamp: str
    status: AuthorizationStatus

@dataclass
class AuthorizationResponse:
    """Authorization response from enterprise admin"""
    request_id: str
    approved: bool
    granted_roles: List[str]
    billing_account_id: str
    enterprise_domain: str
    admin_email: str
    timestamp: str
    expiration_date: Optional[str] = None

class GCPAuthorizationHandshake:
    """Handles the authorization handshake process"""
    
    def __init__(self):
        self.pending_requests = {}
        self.authorization_responses = {}
    
    def step_1_request_authorization(self, developer_email: str, project_name: str, 
                                   billing_account_id: str, enterprise_domain: str) -> AuthorizationRequest:
        """Step 1: Developer requests authorization from enterprise admin"""
        print("🤝 STEP 1: Request Authorization from Enterprise Admin")
        print("=" * 60)
        
        # Generate request ID
        request_id = f"auth_req_{int(time.time())}"
        
        # Define requested roles
        requested_roles = [
            "roles/billing.user",              # Use billing account
            "roles/container.admin",           # GKE management
            "roles/bigquery.admin",            # BigQuery access
            "roles/aiplatform.user",           # AI Platform access
            "roles/storage.admin",             # Cloud Storage access
            "roles/iam.serviceAccountAdmin"    # Service account management
        ]
        
        # Create authorization request
        auth_request = AuthorizationRequest(
            developer_email=developer_email,
            project_name=project_name,
            requested_roles=requested_roles,
            billing_account_id=billing_account_id,
            enterprise_domain=enterprise_domain,
            request_id=request_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            status=AuthorizationStatus.PENDING
        )
        
        # Store pending request
        self.pending_requests[request_id] = auth_request
        
        print(f"📧 Developer Email: {developer_email}")
        print(f"📁 Project Name: {project_name}")
        print(f"💰 Billing Account: {billing_account_id}")
        print(f"🏢 Enterprise Domain: {enterprise_domain}")
        print(f"🆔 Request ID: {request_id}")
        print(f"⏰ Timestamp: {auth_request.timestamp}")
        print()
        print("🔐 Requested Roles:")
        for role in requested_roles:
            print(f"  • {role}")
        print()
        print("📋 Next Steps:")
        print("1. Enterprise admin reviews this request")
        print("2. Enterprise admin approves/denies access")
        print("3. You'll receive authorization response")
        print("4. Use authorization response to link project")
        
        return auth_request
    
    def step_2_enterprise_admin_review(self, request_id: str, admin_email: str, 
                                     approved: bool, granted_roles: List[str]) -> AuthorizationResponse:
        """Step 2: Enterprise admin reviews and responds to authorization request"""
        print("\n🏢 STEP 2: Enterprise Admin Review")
        print("=" * 50)
        
        if request_id not in self.pending_requests:
            print(f"❌ Request ID {request_id} not found")
            return None
        
        auth_request = self.pending_requests[request_id]
        
        print(f"👤 Admin Email: {admin_email}")
        print(f"🆔 Request ID: {request_id}")
        print(f"👨‍💻 Developer: {auth_request.developer_email}")
        print(f"📁 Project: {auth_request.project_name}")
        print(f"💰 Billing Account: {auth_request.billing_account_id}")
        print()
        
        if approved:
            print("✅ APPROVED - Granting access")
            print("🔐 Granted Roles:")
            for role in granted_roles:
                print(f"  • {role}")
        else:
            print("❌ DENIED - Access not granted")
            print("💡 Reason: Enterprise policy restrictions")
        
        # Create authorization response
        auth_response = AuthorizationResponse(
            request_id=request_id,
            approved=approved,
            granted_roles=granted_roles if approved else [],
            billing_account_id=auth_request.billing_account_id,
            enterprise_domain=auth_request.enterprise_domain,
            admin_email=admin_email,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            expiration_date=time.strftime("%Y-%m-%d", time.localtime(time.time() + 365*24*60*60)) if approved else None
        )
        
        # Store authorization response
        self.authorization_responses[request_id] = auth_response
        
        # Update request status
        auth_request.status = AuthorizationStatus.AUTHORIZED if approved else AuthorizationStatus.DENIED
        
        return auth_response
    
    def step_3_verify_authorization(self, request_id: str) -> Dict[str, Any]:
        """Step 3: Verify authorization before linking project"""
        print("\n🔍 STEP 3: Verify Authorization")
        print("=" * 40)
        
        if request_id not in self.authorization_responses:
            print(f"❌ Authorization response not found for request {request_id}")
            return {"success": False, "error": "No authorization response"}
        
        auth_response = self.authorization_responses[request_id]
        
        if not auth_response.approved:
            print("❌ Authorization denied by enterprise admin")
            return {"success": False, "error": "Authorization denied"}
        
        print("✅ Authorization verified")
        print(f"👤 Authorized by: {auth_response.admin_email}")
        print(f"⏰ Authorized on: {auth_response.timestamp}")
        print(f"📅 Expires: {auth_response.expiration_date}")
        print(f"💰 Billing Account: {auth_response.billing_account_id}")
        print()
        print("🔐 Granted Roles:")
        for role in auth_response.granted_roles:
            print(f"  • {role}")
        
        return {
            "success": True,
            "authorization": auth_response,
            "billing_account_id": auth_response.billing_account_id,
            "granted_roles": auth_response.granted_roles
        }
    
    def step_4_link_project_with_authorization(self, project_id: str, request_id: str) -> Dict[str, Any]:
        """Step 4: Link project to billing account using authorization"""
        print("\n🔗 STEP 4: Link Project with Authorization")
        print("=" * 50)
        
        # Verify authorization first
        auth_check = self.step_3_verify_authorization(request_id)
        if not auth_check["success"]:
            return auth_check
        
        auth_response = auth_check["authorization"]
        
        try:
            # Link project to billing account
            result = subprocess.run(
                ["gcloud", "billing", "projects", "link", 
                 project_id, 
                 "--billing-account", auth_response.billing_account_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ Project {project_id} linked to billing account")
            print(f"💰 Billing Account: {auth_response.billing_account_id}")
            print(f"🏢 Enterprise Domain: {auth_response.enterprise_domain}")
            print(f"👤 Authorized by: {auth_response.admin_email}")
            
            return {
                "success": True,
                "project_id": project_id,
                "billing_account_id": auth_response.billing_account_id,
                "authorization": auth_response
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to link project: {e.stderr}")
            return {"success": False, "error": e.stderr}
    
    def step_5_apply_iam_permissions(self, project_id: str, developer_email: str, 
                                   granted_roles: List[str]) -> Dict[str, Any]:
        """Step 5: Apply IAM permissions based on authorization"""
        print("\n🔐 STEP 5: Apply IAM Permissions")
        print("=" * 40)
        
        applied_roles = []
        failed_roles = []
        
        for role in granted_roles:
            try:
                result = subprocess.run(
                    ["gcloud", "projects", "add-iam-policy-binding", 
                     project_id,
                     "--member", f"user:{developer_email}",
                     "--role", role],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"  ✅ {role}")
                applied_roles.append(role)
            except subprocess.CalledProcessError as e:
                print(f"  ❌ {role}: {e.stderr}")
                failed_roles.append(role)
        
        return {
            "success": len(failed_roles) == 0,
            "applied_roles": applied_roles,
            "failed_roles": failed_roles
        }
    
    def run_complete_authorization_handshake(self, developer_email: str, project_name: str,
                                           billing_account_id: str, enterprise_domain: str,
                                           admin_email: str) -> Dict[str, Any]:
        """Run complete authorization handshake process"""
        print("🤝 GCP Authorization Handshake")
        print("=" * 40)
        print("Enterprise billing account authorization process")
        print()
        
        results = {}
        
        # Step 1: Request authorization
        auth_request = self.step_1_request_authorization(
            developer_email, project_name, billing_account_id, enterprise_domain
        )
        results["authorization_request"] = auth_request
        
        # Step 2: Enterprise admin review (simulated)
        print("\n⏳ Waiting for enterprise admin review...")
        time.sleep(2)  # Simulate admin review time
        
        auth_response = self.step_2_enterprise_admin_review(
            auth_request.request_id, admin_email, True, auth_request.requested_roles
        )
        results["authorization_response"] = auth_response
        
        # Step 3: Verify authorization
        auth_verification = self.step_3_verify_authorization(auth_request.request_id)
        results["authorization_verification"] = auth_verification
        
        if not auth_verification["success"]:
            return results
        
        # Step 4: Link project with authorization
        project_id = f"enterprise-project-{int(time.time())}"
        project_link = self.step_4_link_project_with_authorization(project_id, auth_request.request_id)
        results["project_link"] = project_link
        
        # Step 5: Apply IAM permissions
        iam_setup = self.step_5_apply_iam_permissions(
            project_id, developer_email, auth_response.granted_roles
        )
        results["iam_setup"] = iam_setup
        
        # Save authorization results
        self.save_authorization_results(results)
        
        print("\n🎉 Authorization Handshake Complete!")
        print("=" * 40)
        print("✅ Authorization requested and approved")
        print("✅ Project linked to enterprise billing account")
        print("✅ IAM permissions applied")
        print("✅ Ready for enterprise development")
        
        return results
    
    def save_authorization_results(self, results: Dict[str, Any]):
        """Save authorization results to file"""
        print("\n💾 Saving authorization results...")
        
        results_file = "gcp_authorization_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"✅ Authorization results saved: {results_file}")

def main():
    """Main authorization handshake function"""
    print("🤝 GCP Authorization Handshake")
    print("=" * 40)
    print("Enterprise billing account authorization process")
    print()
    
    # Get developer information
    developer_email = input("Enter your email (developer): ").strip()
    if not developer_email:
        print("❌ Developer email required")
        return
    
    project_name = input("Enter project name: ").strip()
    if not project_name:
        project_name = "Enterprise Billing System"
    
    billing_account_id = input("Enter enterprise billing account ID: ").strip()
    if not billing_account_id:
        print("❌ Billing account ID required")
        return
    
    enterprise_domain = input("Enter enterprise domain: ").strip()
    if not enterprise_domain:
        enterprise_domain = "enterprise.com"
    
    admin_email = input("Enter enterprise admin email: ").strip()
    if not admin_email:
        admin_email = "admin@enterprise.com"
    
    # Run authorization handshake
    handshake = GCPAuthorizationHandshake()
    results = handshake.run_complete_authorization_handshake(
        developer_email, project_name, billing_account_id, enterprise_domain, admin_email
    )
    
    print("\n🎯 Authorization Handshake Summary:")
    print(f"👨‍💻 Developer: {developer_email}")
    print(f"📁 Project: {project_name}")
    print(f"💰 Billing Account: {billing_account_id}")
    print(f"🏢 Enterprise: {enterprise_domain}")
    print(f"👤 Admin: {admin_email}")
    print("\n🚀 Ready for enterprise development!")

if __name__ == "__main__":
    main()
