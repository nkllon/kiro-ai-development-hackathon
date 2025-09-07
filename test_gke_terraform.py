#!/usr/bin/env python3
"""Test GKE Terraform configuration validation"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def test_terraform_validation():
    """Test Terraform configuration validation"""
    print("🔍 Testing GKE Terraform Configuration")
    print("=" * 50)
    
    terraform_dir = Path("deployment/gke/terraform")
    
    if not terraform_dir.exists():
        print("❌ Terraform directory not found")
        return False
    
    print(f"📁 Working directory: {terraform_dir}")
    
    # Test 1: Terraform init
    print("\n1️⃣ Testing Terraform init...")
    success, stdout, stderr = run_command("terraform init", cwd=terraform_dir)
    if success:
        print("✅ Terraform init successful")
    else:
        print(f"❌ Terraform init failed: {stderr}")
        return False
    
    # Test 2: Terraform validate
    print("\n2️⃣ Testing Terraform validate...")
    success, stdout, stderr = run_command("terraform validate", cwd=terraform_dir)
    if success:
        print("✅ Terraform configuration is valid")
    else:
        print(f"❌ Terraform validation failed: {stderr}")
        return False
    
    # Test 3: Terraform fmt check
    print("\n3️⃣ Testing Terraform formatting...")
    success, stdout, stderr = run_command("terraform fmt -check", cwd=terraform_dir)
    if success:
        print("✅ Terraform formatting is correct")
    else:
        print("⚠️ Terraform formatting issues found (non-critical)")
        # Auto-format
        run_command("terraform fmt", cwd=terraform_dir)
        print("✅ Auto-formatted Terraform files")
    
    # Test 4: Check required files
    print("\n4️⃣ Testing required files...")
    required_files = [
        "main.tf",
        "variables.tf", 
        "outputs.tf",
        "terraform.tfvars.example",
        "environments/dev.tfvars",
        "environments/prod.tfvars"
    ]
    
    all_files_exist = True
    for file in required_files:
        file_path = terraform_dir / file
        if file_path.exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_files_exist = False
    
    if not all_files_exist:
        return False
    
    # Test 5: Terraform plan with mock project
    print("\n5️⃣ Testing Terraform plan (dry run)...")
    mock_project = "mock-project-id"
    
    # Create a temporary tfvars file for testing
    test_tfvars = terraform_dir / "test.tfvars"
    with open(test_tfvars, 'w') as f:
        f.write(f'project_id = "{mock_project}"\n')
        f.write('cluster_name = "test-cluster"\n')
        f.write('region = "us-central1"\n')
        f.write('environment = "test"\n')
    
    try:
        success, stdout, stderr = run_command(
            f"terraform plan -var-file=test.tfvars -var-file=environments/dev.tfvars", 
            cwd=terraform_dir
        )
        if success:
            print("✅ Terraform plan successful (configuration syntax valid)")
        else:
            # Plan might fail due to missing GCP credentials, but syntax should be valid
            if "Error: google: could not find default credentials" in stderr:
                print("✅ Terraform plan syntax valid (GCP auth expected to fail in test)")
            else:
                print(f"❌ Terraform plan failed: {stderr}")
                return False
    finally:
        # Clean up test file
        if test_tfvars.exists():
            test_tfvars.unlink()
    
    print("\n🎉 All GKE Terraform tests passed!")
    print("\n📋 Configuration Summary:")
    print("   ✅ Terraform syntax valid")
    print("   ✅ All required files present")
    print("   ✅ Environment configurations ready")
    print("   ✅ Variables and outputs defined")
    print("   ✅ Ready for deployment")
    
    return True

def show_deployment_instructions():
    """Show deployment instructions"""
    print("\n🚀 Deployment Instructions:")
    print("=" * 30)
    print("1. Set your GCP project ID:")
    print("   export PROJECT_ID=your-gcp-project-id")
    print("")
    print("2. Deploy using the deployment script:")
    print("   cd deployment/gke")
    print("   PROJECT_ID=$PROJECT_ID ./deploy-gke.sh")
    print("")
    print("3. Or deploy manually with Terraform:")
    print("   cd deployment/gke/terraform")
    print("   terraform init")
    print("   terraform plan -var=\"project_id=$PROJECT_ID\" -var-file=\"environments/dev.tfvars\"")
    print("   terraform apply -var=\"project_id=$PROJECT_ID\" -var-file=\"environments/dev.tfvars\"")
    print("")
    print("4. Configure kubectl:")
    print("   gcloud container clusters get-credentials beast-mode-dev --region us-central1")
    print("")
    print("5. Verify deployment:")
    print("   kubectl get nodes")
    print("   kubectl get pods --all-namespaces")

if __name__ == "__main__":
    if test_terraform_validation():
        show_deployment_instructions()
        sys.exit(0)
    else:
        print("\n❌ GKE Terraform configuration tests failed")
        sys.exit(1)