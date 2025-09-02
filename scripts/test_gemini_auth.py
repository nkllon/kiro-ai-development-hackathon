#!/usr/bin/env python3
"""
Test Google Cloud authentication for Gemini API
"""

import os
import subprocess


def test_gemini_auth():
    """Test Gemini API authentication using Google Cloud"""
    print("🔐 Testing Gemini API authentication...")

    # Check if gcloud is available
    try:
        result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ gcloud not available")
            return False
        print("✅ gcloud is available")
    except Exception as e:
        print(f"❌ gcloud not found: {e}")
        return False

    # Check if authenticated
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list"],
            capture_output=True,
            text=True,
        )
        if "ACTIVE" not in result.stdout:
            print("❌ Not authenticated with gcloud")
            return False
        print("✅ gcloud is authenticated")
    except Exception as e:
        print(f"❌ Authentication check failed: {e}")
        return False

    # Get access token
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True,
        )
        access_token = result.stdout.strip()

        if access_token:
            print("✅ Successfully got access token")
            print(f"Token length: {len(access_token)} characters")

            # Set environment variable
            os.environ["GOOGLE_API_KEY"] = access_token
            print("✅ Set GOOGLE_API_KEY environment variable")

            return True
        print("❌ No access token returned")
        return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get access token: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_gemini_auth()
    if success:
        print("\n🎉 Gemini API authentication ready!")
    else:
        print("\n❌ Gemini API authentication failed")
