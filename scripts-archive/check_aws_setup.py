#!/usr/bin/env python3
"""
AWS Setup Checker
Verifies AWS CLI and credentials are properly configured
"""

import subprocess
import sys
import json

def run_command(cmd, capture=True):
    """Run shell command and return output"""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, timeout=10)
            return result.returncode == 0, "", ""
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_aws_cli():
    """Check if AWS CLI is installed"""
    print("Checking AWS CLI installation...")
    success, stdout, stderr = run_command("aws --version")
    
    if success:
        print(f"  ✓ AWS CLI installed: {stdout.strip()}")
        return True
    else:
        print("  ✗ AWS CLI not found")
        print("\n  Install with:")
        print("    brew install awscli")
        print("  Or:")
        print("    pip3 install awscli")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("\nChecking AWS credentials...")
    success, stdout, stderr = run_command("aws sts get-caller-identity")
    
    if success:
        try:
            identity = json.loads(stdout)
            print("  ✓ AWS credentials valid")
            print(f"    Account: {identity.get('Account', 'Unknown')}")
            print(f"    User ARN: {identity.get('Arn', 'Unknown')}")
            return True
        except json.JSONDecodeError:
            print("  ✗ Unexpected response format")
            return False
    else:
        print("  ✗ AWS credentials not configured or invalid")
        print("\n  Configure with:")
        print("    aws configure")
        print("\n  You'll need:")
        print("    - AWS Access Key ID")
        print("    - AWS Secret Access Key")
        print("    - Default region (e.g., us-east-1)")
        return False

def check_s3_access():
    """Check if user has S3 access"""
    print("\nChecking S3 access...")
    success, stdout, stderr = run_command("aws s3 ls")
    
    if success:
        buckets = [line.strip() for line in stdout.split('\n') if line.strip()]
        print(f"  ✓ S3 access confirmed")
        if buckets:
            print(f"    Found {len(buckets)} bucket(s):")
            for bucket in buckets[:5]:  # Show first 5
                print(f"      - {bucket}")
            if len(buckets) > 5:
                print(f"      ... and {len(buckets) - 5} more")
        else:
            print("    No existing buckets found")
        return True
    else:
        print("  ✗ Cannot access S3")
        if "AccessDenied" in stderr:
            print("\n  Your AWS user may not have S3 permissions")
            print("  Required permissions:")
            print("    - s3:ListBucket")
            print("    - s3:PutObject")
            print("    - s3:GetObject")
        return False

def suggest_bucket_creation():
    """Suggest creating a new bucket"""
    print("\nS3 Bucket Setup:")
    print("-" * 60)
    
    bucket_name = input("Enter a name for your archive bucket (or press Enter to skip): ").strip()
    
    if not bucket_name:
        print("Skipped bucket creation")
        return
    
    # Validate bucket name
    if not all(c.isalnum() or c in ['-', '.'] for c in bucket_name):
        print("  ✗ Invalid bucket name. Use only: letters, numbers, hyphens, dots")
        return
    
    if len(bucket_name) < 3 or len(bucket_name) > 63:
        print("  ✗ Bucket name must be 3-63 characters long")
        return
    
    print(f"\nCreating bucket: {bucket_name}")
    
    # Get region
    region = input("Enter AWS region [us-east-1]: ").strip() or "us-east-1"
    
    # Create bucket
    if region == "us-east-1":
        cmd = f"aws s3 mb s3://{bucket_name}"
    else:
        cmd = f"aws s3 mb s3://{bucket_name} --region {region}"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(f"  ✓ Bucket created: s3://{bucket_name}")
        print(f"\nYou can now use this bucket for archiving:")
        print(f"  ./auto_archive.sh {bucket_name}")
        print(f"  python3 archive_old_screenshots.py {bucket_name}")
    else:
        print(f"  ✗ Failed to create bucket")
        if "BucketAlreadyExists" in stderr or "BucketAlreadyOwnedByYou" in stderr:
            print("  Bucket name already taken. Try a different name.")
        else:
            print(f"  Error: {stderr}")

def main():
    print("=" * 60)
    print("AWS SETUP CHECKER")
    print("=" * 60)
    print()
    
    # Check AWS CLI
    if not check_aws_cli():
        print("\n❌ Setup incomplete. Install AWS CLI first.")
        sys.exit(1)
    
    # Check credentials
    if not check_aws_credentials():
        print("\n❌ Setup incomplete. Configure AWS credentials first.")
        sys.exit(1)
    
    # Check S3 access
    s3_ok = check_s3_access()
    
    print("\n" + "=" * 60)
    
    if s3_ok:
        print("✅ AWS is properly configured!")
        print("\nYou're ready to start archiving:")
        print("  1. Quick analysis:     python3 quick_analysis.py")
        print("  2. Archive screenshots: python3 archive_old_screenshots.py <bucket-name>")
        print("  3. Archive all large files: ./auto_archive.sh <bucket-name>")
        
        # Offer to create bucket
        create = input("\nCreate a new S3 bucket for archiving? (yes/no): ").strip().lower()
        if create == 'yes':
            suggest_bucket_creation()
    else:
        print("⚠️  AWS is configured but S3 access may be limited")
        print("Contact your AWS administrator to grant S3 permissions")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
