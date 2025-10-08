#!/usr/bin/env python3
"""
Secure Credentials Helper - Environment Variable Management
==========================================================

Provides secure credential loading for all LLM-generated code and system components.
NEVER hardcode credentials - always use this helper.

Author: Beast Mode Framework
Date: 2025-10-02
Purpose: Prevent hardcoded credentials and provide secure environment variable loading
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
import warnings


logger = logging.getLogger(__name__)


@dataclass
class CredentialConfig:
    """Configuration for credential loading."""
    env_file_paths: List[Path]
    required_vars: List[str]
    optional_vars: Dict[str, str]  # var_name -> default_value
    strict_mode: bool = True


class SecureCredentials:
    """
    Secure credential management using environment variables only.
    
    Features:
    - Loads from ~/.env and project .env files
    - Validates required credentials are present
    - Provides helpful error messages
    - Never stores credentials in memory longer than necessary
    - Supports multiple environment file locations
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize secure credential loader.
        
        Args:
            strict_mode: If True, raises errors for missing required credentials
        """
        self.strict_mode = strict_mode
        self.loaded_files: List[Path] = []
        self._load_all_env_files()
    
    def _load_all_env_files(self) -> None:
        """Load environment variables from all standard locations."""
        env_files = [
            Path.home() / ".env",           # User home directory
            Path.cwd() / ".env",            # Current working directory
            Path.cwd() / "config" / ".env", # Config directory
            Path.cwd() / ".kiro" / ".env"   # Kiro config directory
        ]
        
        for env_file in env_files:
            if env_file.exists():
                self._load_env_file(env_file)
                self.loaded_files.append(env_file)
    
    def _load_env_file(self, env_file: Path) -> None:
        """Load environment variables from a specific file."""
        try:
            with open(env_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' not in line:
                        logger.warning(f"Invalid line in {env_file}:{line_num}: {line}")
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
                        
        except Exception as e:
            logger.error(f"Failed to load {env_file}: {e}")
    
    def get_credential(self, 
                      env_var_name: str, 
                      description: str = None,
                      required: bool = True,
                      default: str = None) -> Optional[str]:
        """
        Get a credential from environment variables with security validation.
        
        Args:
            env_var_name: Name of environment variable
            description: Human-readable description for error messages
            required: Whether this credential is required
            default: Default value if not required and not found
            
        Returns:
            Credential value or None if not required and not found
            
        Raises:
            ValueError: If required credential is missing
        """
        credential = os.getenv(env_var_name)
        
        if credential:
            # Validate credential is not obviously fake/placeholder
            if self._is_placeholder_credential(credential):
                warning_msg = f"Credential {env_var_name} appears to be a placeholder: {credential[:10]}..."
                if self.strict_mode:
                    raise ValueError(f"Invalid credential: {warning_msg}")
                else:
                    warnings.warn(warning_msg)
            
            return credential
        
        # Handle missing credential
        if required:
            error_msg = self._generate_missing_credential_error(env_var_name, description)
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                logger.error(error_msg)
                return default
        
        return default
    
    def _is_placeholder_credential(self, credential: str) -> bool:
        """Check if credential appears to be a placeholder."""
        placeholders = [
            'your_password_here',
            'your_key_here',
            'replace_me',
            'changeme',
            'placeholder',
            'example',
            'test_password',
            'dummy',
            'fake'
        ]
        
        credential_lower = credential.lower()
        return any(placeholder in credential_lower for placeholder in placeholders)
    
    def _generate_missing_credential_error(self, env_var_name: str, description: str = None) -> str:
        """Generate helpful error message for missing credentials."""
        desc = description or env_var_name
        
        error_msg = f"""
🚨 MISSING CREDENTIAL: {desc}

Environment variable '{env_var_name}' is required but not found.

To fix this:
1. Add to ~/.env file:
   echo "{env_var_name}=your_actual_value_here" >> ~/.env

2. Or set in current session:
   export {env_var_name}=your_actual_value_here

3. Or add to your shell profile (~/.bashrc, ~/.zshrc):
   export {env_var_name}=your_actual_value_here

Loaded environment files: {[str(f) for f in self.loaded_files]}

⚠️  NEVER hardcode credentials in source code!
"""
        return error_msg.strip()
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration from environment variables."""
        return {
            'host': self.get_credential('REDIS_HOST', 'Redis host', required=False, default='localhost'),
            'port': int(self.get_credential('REDIS_PORT', 'Redis port', required=False, default='6379')),
            'password': self.get_credential('REDIS_PASSWORD', 'Redis password', required=True),
            'db': int(self.get_credential('REDIS_DB', 'Redis database', required=False, default='0'))
        }
    
    def get_llm_config(self) -> Dict[str, Optional[str]]:
        """Get LLM API configuration from environment variables."""
        return {
            'openai_api_key': self.get_credential('OPENAI_API_KEY', 'OpenAI API key', required=False),
            'anthropic_api_key': self.get_credential('ANTHROPIC_API_KEY', 'Anthropic API key', required=False),
            'google_api_key': self.get_credential('GOOGLE_API_KEY', 'Google API key', required=False)
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration from environment variables."""
        return {
            'host': self.get_credential('DATABASE_HOST', 'Database host', required=False, default='localhost'),
            'port': int(self.get_credential('DATABASE_PORT', 'Database port', required=False, default='5432')),
            'name': self.get_credential('DATABASE_NAME', 'Database name', required=True),
            'user': self.get_credential('DATABASE_USER', 'Database user', required=True),
            'password': self.get_credential('DATABASE_PASSWORD', 'Database password', required=True)
        }
    
    def get_directus_config(self) -> Dict[str, Any]:
        """Get Directus CMS configuration from environment variables."""
        return {
            'url': self.get_credential('DIRECTUS_URL', 'Directus URL', required=False, default='http://localhost:8055'),
            'admin_email': self.get_credential('DIRECTUS_ADMIN_EMAIL', 'Directus admin email', required=False, default='admin@example.com'),
            'admin_password': self.get_credential('DIRECTUS_ADMIN_PASSWORD', 'Directus admin password', required=True)
        }
    
    def validate_all_credentials(self, required_credentials: List[str]) -> bool:
        """
        Validate that all required credentials are present and valid.
        
        Args:
            required_credentials: List of environment variable names that must be present
            
        Returns:
            True if all credentials are valid, False otherwise
        """
        missing_credentials = []
        invalid_credentials = []
        
        for cred_name in required_credentials:
            try:
                credential = self.get_credential(cred_name, f"Required credential {cred_name}")
                if credential and self._is_placeholder_credential(credential):
                    invalid_credentials.append(cred_name)
            except ValueError:
                missing_credentials.append(cred_name)
        
        if missing_credentials or invalid_credentials:
            error_msg = "❌ CREDENTIAL VALIDATION FAILED:\n"
            
            if missing_credentials:
                error_msg += f"Missing: {', '.join(missing_credentials)}\n"
            
            if invalid_credentials:
                error_msg += f"Invalid/Placeholder: {', '.join(invalid_credentials)}\n"
            
            error_msg += "\nPlease update your ~/.env file with valid credentials."
            
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                logger.error(error_msg)
                return False
        
        return True
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about the current environment configuration."""
        return {
            'loaded_files': [str(f) for f in self.loaded_files],
            'environment_vars_loaded': len([k for k in os.environ.keys() if not k.startswith('_')]),
            'strict_mode': self.strict_mode,
            'home_env_exists': (Path.home() / ".env").exists(),
            'project_env_exists': (Path.cwd() / ".env").exists()
        }


# Global instance for easy access
_secure_credentials = None

def get_secure_credentials(strict_mode: bool = True) -> SecureCredentials:
    """Get global secure credentials instance."""
    global _secure_credentials
    if _secure_credentials is None:
        _secure_credentials = SecureCredentials(strict_mode=strict_mode)
    return _secure_credentials


# Convenience functions for common use cases
def get_redis_password() -> str:
    """Get Redis password from environment variables."""
    creds = get_secure_credentials()
    return creds.get_credential('REDIS_PASSWORD', 'Redis password')


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment variables."""
    creds = get_secure_credentials(strict_mode=False)
    return creds.get_credential('OPENAI_API_KEY', 'OpenAI API key', required=False)


def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment variables."""
    creds = get_secure_credentials(strict_mode=False)
    return creds.get_credential('ANTHROPIC_API_KEY', 'Anthropic API key', required=False)


def get_directus_password() -> str:
    """Get Directus CMS admin password from environment variables."""
    creds = get_secure_credentials()
    return creds.get_credential('DIRECTUS_ADMIN_PASSWORD', 'Directus CMS admin password')


def validate_environment_setup() -> bool:
    """Validate that environment is properly configured with credentials."""
    creds = get_secure_credentials(strict_mode=False)
    
    # Check for common required credentials
    required = ['REDIS_PASSWORD']
    optional = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'DIRECTUS_ADMIN_PASSWORD']
    
    print("🔍 Validating environment setup...")
    
    # Check required credentials
    missing_required = []
    for cred in required:
        try:
            value = creds.get_credential(cred, f"Required: {cred}")
            if value:
                print(f"✅ {cred}: Found")
            else:
                missing_required.append(cred)
        except ValueError:
            missing_required.append(cred)
    
    # Check optional credentials
    for cred in optional:
        value = creds.get_credential(cred, f"Optional: {cred}", required=False)
        if value:
            print(f"✅ {cred}: Found")
        else:
            print(f"⚠️  {cred}: Not found (optional)")
    
    if missing_required:
        print(f"❌ Missing required credentials: {', '.join(missing_required)}")
        print("Please add them to ~/.env file")
        return False
    
    print("✅ Environment validation passed!")
    return True


if __name__ == "__main__":
    # Run validation when script is executed directly
    validate_environment_setup()