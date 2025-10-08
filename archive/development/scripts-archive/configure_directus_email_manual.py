#!/usr/bin/env python3
"""
Directus Email Configuration Helper - Manual Version
Configures Directus to use Google SMTP for email functionality
"""

import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_docker_compose(email: str, app_password: str) -> bool:
    """
    Update docker-compose.yml with email configuration.

    Args:
        email (str): Gmail address
        app_password (str): Gmail app password

    Returns:
        bool: True if update succeeded, False otherwise
    """
    compose_file = Path("deployment/local/docker-compose.yml")
    
    if not compose_file.exists():
        print(f"❌ Docker compose file not found: {compose_file}")
        return False
    
    # Read current content
    content = compose_file.read_text()
    
    # Replace placeholder values
    content = content.replace("your-email@gmail.com", email)
    content = content.replace("your-app-password", app_password)
    
    # Write updated content
    compose_file.write_text(content)
    print(f"✅ Updated {compose_file}")
    return True

def restart_directus() -> bool:
    """
    Restart Directus container to apply new configuration.

    Returns:
        bool: True if restart succeeded, False otherwise.
    """
    print("\n🔄 Restarting Directus container...")
    logging.info("Attempting to restart Directus container...")

    try:
        # Stop and remove current container
        stop_result = subprocess.run(
            ["docker", "compose", "-f", "deployment/local/docker-compose.yml", "stop", "directus"],
            check=True, capture_output=True
        )
        logging.info("Directus container stopped: %s", stop_result.stdout.decode().strip())

        rm_result = subprocess.run(
            ["docker", "compose", "-f", "deployment/local/docker-compose.yml", "rm", "-f", "directus"],
            check=True, capture_output=True
        )
        logging.info("Directus container removed: %s", rm_result.stdout.decode().strip())

        # Start with new configuration
        up_result = subprocess.run(
            ["docker", "compose", "-f", "deployment/local/docker-compose.yml", "up", "-d", "directus"],
            check=True, capture_output=True
        )
        logging.info("Directus container started: %s", up_result.stdout.decode().strip())

        print("✅ Directus restarted successfully")
        return True

    except subprocess.CalledProcessError as e:
        logging.error("Failed to restart Directus: %s", e.stderr.decode().strip() if e.stderr else str(e))
        print(f"❌ Failed to restart Directus: {e}")
        return False

def test_email_configuration() -> bool:
    """
    Test if email configuration is working by checking the Directus health endpoint.

    Returns:
        bool: True if health check passes, False otherwise.
    """
    print("\n🧪 Testing email configuration...")

    import time
    time.sleep(10)  # Wait for container to start

    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8055/server/health"],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            health_data = result.stdout.strip()
            if '"status":"ok"' in health_data:
                print("✅ Email configuration working - Health check passed!")
                return True
            else:
                print(f"⚠️ Health check returned: {health_data}")
                return False
        else:
            print(f"❌ Health check failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def main() -> int:
    """
    Main configuration process.

    Returns:
        int: 0 if successful, 1 otherwise.
    """
    print("🚀 Setting up Directus with Google SMTP")
    print("📧 Manual Configuration Mode")
    print("=" * 50)
    
    # Get email and password from command line arguments
    if len(sys.argv) != 3:
        print("Usage: python3 configure_directus_email_manual.py <gmail-address> <app-password>")
        print("\nExample:")
        print("python3 configure_directus_email_manual.py your-email@gmail.com your16charpassword")
        print("\nTo get your Gmail App Password:")
        print("1. Go to: https://myaccount.google.com/security")
        print("2. Enable 2-Factor Authentication if not already enabled")
        print("3. Go to 'App passwords' and generate a new password for 'Directus'")
        print("4. Copy the 16-character password")
        return 1
    
    email = sys.argv[1]
    app_password = sys.argv[2]
    
    # Validate inputs
    if not email.endswith("@gmail.com"):
        print("❌ Please provide a valid Gmail address")
        return 1
    
    if len(app_password) != 16 or not app_password.replace(' ', '').isalnum():
        print("❌ App password should be 16 characters (letters and numbers only)")
        return 1
    
    print(f"📧 Configuring for: {email}")
    print(f"🔑 Using app password: {'*' * 12}{app_password[-4:]}")
    
    # Update docker-compose.yml
    if not update_docker_compose(email, app_password):
        return 1

    # Restart Directus
    if not restart_directus():
        return 1

    # Test configuration
    if test_email_configuration():
        print("\n🎉 Directus email configuration completed successfully!")
        print("🌐 Access Directus at: http://localhost:8055/admin")
        return 0
    else:
        print("\n⚠️ Configuration applied but health check still failing")
        print("💡 Check Directus logs: docker logs local-directus-1")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
