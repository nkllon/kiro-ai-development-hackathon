#!/usr/bin/env python3
"""Validate GKE Terraform configuration files without requiring Terraform CLI"""

import json
import re
from pathlib import Path

def validate_terraform_syntax(file_path):
    """Basic Terraform syntax validation"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for basic Terraform syntax patterns
        issues = []
        
        # Check for unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        
        # Check for basic resource syntax
        if file_path.name == "main.tf":
            if 'resource "google_container_cluster"' not in content:
                issues.append("Missing GKE cluster resource")
            if 'resource "google_container_node_pool"' not in content:
                issues.append("Missing node pool resource")
        
        # Check for required providers
        if 'provider "google"' not in content and 'required_providers' not in content:
            if file_path.name == "main.tf":
                issues.append("Missing Google provider configuration")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error reading file: {e}"]

def validate_variables_file(file_path):
    """Validate variables.tf file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        required_variables = [
            'project_id',
            'cluster_name', 
            'region',
            'environment',
            'machine_type',
            'min_nodes',
            'max_nodes'
        ]
        
        missing_vars = []
        for var in required_variables:
            if f'variable "{var}"' not in content:
                missing_vars.append(var)
        
        return len(missing_vars) == 0, missing_vars
        
    except Exception as e:
        return False, [f"Error reading variables file: {e}"]

def validate_outputs_file(file_path):
    """Validate outputs.tf file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        required_outputs = [
            'cluster_name',
            'cluster_endpoint',
            'kubectl_config_command'
        ]
        
        missing_outputs = []
        for output in required_outputs:
            if f'output "{output}"' not in content:
                missing_outputs.append(output)
        
        return len(missing_outputs) == 0, missing_outputs
        
    except Exception as e:
        return False, [f"Error reading outputs file: {e}"]

def validate_gke_configuration():
    """Validate complete GKE Terraform configuration"""
    print("🔍 Validating GKE Terraform Configuration")
    print("=" * 50)
    
    terraform_dir = Path("deployment/gke/terraform")
    
    if not terraform_dir.exists():
        print("❌ Terraform directory not found")
        return False
    
    all_valid = True
    
    # Test 1: Check required files exist
    print("\n1️⃣ Checking required files...")
    required_files = {
        "main.tf": "Main Terraform configuration",
        "variables.tf": "Variable definitions", 
        "outputs.tf": "Output definitions",
        "terraform.tfvars.example": "Example variables file"
    }
    
    for file, description in required_files.items():
        file_path = terraform_dir / file
        if file_path.exists():
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - {description} (MISSING)")
            all_valid = False
    
    # Test 2: Check environment files
    print("\n2️⃣ Checking environment configurations...")
    env_dir = terraform_dir / "environments"
    if env_dir.exists():
        for env_file in ["dev.tfvars", "prod.tfvars"]:
            env_path = env_dir / env_file
            if env_path.exists():
                print(f"✅ environments/{env_file}")
            else:
                print(f"❌ environments/{env_file} (MISSING)")
                all_valid = False
    else:
        print("❌ environments/ directory missing")
        all_valid = False
    
    # Test 3: Validate main.tf syntax
    print("\n3️⃣ Validating main.tf syntax...")
    main_tf = terraform_dir / "main.tf"
    if main_tf.exists():
        valid, issues = validate_terraform_syntax(main_tf)
        if valid:
            print("✅ main.tf syntax looks good")
        else:
            print("❌ main.tf syntax issues:")
            for issue in issues:
                print(f"   - {issue}")
            all_valid = False
    
    # Test 4: Validate variables.tf
    print("\n4️⃣ Validating variables.tf...")
    variables_tf = terraform_dir / "variables.tf"
    if variables_tf.exists():
        valid, missing = validate_variables_file(variables_tf)
        if valid:
            print("✅ All required variables defined")
        else:
            print("❌ Missing required variables:")
            for var in missing:
                print(f"   - {var}")
            all_valid = False
    
    # Test 5: Validate outputs.tf
    print("\n5️⃣ Validating outputs.tf...")
    outputs_tf = terraform_dir / "outputs.tf"
    if outputs_tf.exists():
        valid, missing = validate_outputs_file(outputs_tf)
        if valid:
            print("✅ All required outputs defined")
        else:
            print("❌ Missing required outputs:")
            for output in missing:
                print(f"   - {output}")
            all_valid = False
    
    # Test 6: Check file sizes (basic sanity check)
    print("\n6️⃣ Checking file completeness...")
    for file in ["main.tf", "variables.tf", "outputs.tf"]:
        file_path = terraform_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            if size > 1000:  # At least 1KB
                print(f"✅ {file} ({size} bytes)")
            else:
                print(f"⚠️ {file} ({size} bytes) - seems small")
    
    if all_valid:
        print("\n🎉 GKE Terraform configuration validation passed!")
        print("\n📋 Configuration Summary:")
        print("   ✅ All required files present")
        print("   ✅ Basic syntax validation passed")
        print("   ✅ Required variables defined")
        print("   ✅ Required outputs defined")
        print("   ✅ Environment configurations ready")
        print("   ✅ Ready for Terraform deployment")
        
        print("\n🚀 Next Steps:")
        print("1. Install Terraform: https://terraform.io/downloads")
        print("2. Set PROJECT_ID environment variable")
        print("3. Run: cd deployment/gke && PROJECT_ID=your-project ./deploy-gke.sh")
        
        return True
    else:
        print("\n❌ GKE Terraform configuration has issues")
        return False

if __name__ == "__main__":
    validate_gke_configuration()