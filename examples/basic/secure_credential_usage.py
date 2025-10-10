#!/usr/bin/env python3
"""
Secure Credential Usage Examples
================================

Examples showing how LLM-generated code should handle credentials securely.
NEVER hardcode credentials - always use the secure credentials helper.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from security.secure_credentials import (
    get_secure_credentials,
    get_redis_password,
    get_openai_api_key,
    validate_environment_setup
)


def example_redis_connection():
    """Example: Secure Redis connection."""
    print("🔧 Example: Redis Connection")
    
    try:
        # ✅ CORRECT: Use secure credentials helper
        creds = get_secure_credentials()
        redis_config = creds.get_redis_config()
        
        print(f"Redis Host: {redis_config['host']}")
        print(f"Redis Port: {redis_config['port']}")
        print(f"Redis Password: {'*' * len(redis_config['password'])}")
        
        # Example Redis connection (would use actual redis library)
        print("✅ Redis connection configured securely")
        
    except ValueError as e:
        print(f"❌ Redis configuration failed: {e}")


def example_llm_api_usage():
    """Example: Secure LLM API key usage."""
    print("\n🤖 Example: LLM API Usage")
    
    # ✅ CORRECT: Use secure credentials helper
    openai_key = get_openai_api_key()
    if openai_key:
        print(f"OpenAI API Key: {openai_key[:10]}...")
        # Would use with OpenAI client
        print("✅ OpenAI API key loaded securely")
    else:
        print("⚠️  OpenAI API key not found (optional)")


def example_custom_credential():
    """Example: Custom credential loading."""
    print("\n🔑 Example: Custom Credential")
    
    creds = get_secure_credentials(strict_mode=False)
    
    # ✅ CORRECT: Use environment variable with helpful error
    api_key = creds.get_credential(
        'CUSTOM_API_KEY',
        'Custom service API key',
        required=False,
        default=None
    )
    
    if api_key:
        print(f"Custom API Key: {api_key[:10]}...")
    else:
        print("⚠️  Custom API key not found")


def example_validation():
    """Example: Credential validation."""
    print("\n✅ Example: Credential Validation")
    
    # Validate specific credentials are present
    creds = get_secure_credentials(strict_mode=False)
    required_creds = ['REDIS_PASSWORD']
    
    if creds.validate_all_credentials(required_creds):
        print("✅ All required credentials validated")
    else:
        print("❌ Credential validation failed")


def bad_examples():
    """Examples of what NOT to do."""
    print("\n❌ BAD EXAMPLES (DO NOT DO THIS):")
    
    print("# NEVER hardcode credentials:")
    print("# redis_password = get_redis_password()  # ❌ NEVER DO THIS")
    print("# api_key = 'hardcoded_key_here'      # ❌ NEVER DO THIS")
    
    print("\n# NEVER use default credential values:")
    print("# password = os.getenv('PASSWORD', 'default_pass')  # ❌ NEVER DO THIS")
    
    print("\n# NEVER put credentials in config files:")
    print("# config = {'password': 'secret123'}  # ❌ NEVER DO THIS")


def main():
    """Main example function."""
    print("🔐 Secure Credential Usage Examples")
    print("=" * 50)
    
    # First validate environment
    if not validate_environment_setup():
        print("\n💡 To fix missing credentials, add them to ~/.env:")
        print("echo 'REDIS_PASSWORD=your_actual_password' >> ~/.env")
        print("echo 'OPENAI_API_KEY=your_actual_key' >> ~/.env")
        return
    
    # Run examples
    example_redis_connection()
    example_llm_api_usage()
    example_custom_credential()
    example_validation()
    bad_examples()
    
    print("\n✅ All examples completed!")
    print("Remember: NEVER hardcode credentials in source code!")


if __name__ == "__main__":
    main()