"""Comprehensive security tests for Google Calendar MCP authentication.

This module tests all security aspects of credential handling, token management,
and authentication security following Beast Mode framework patterns.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from cryptography.fernet import Fernet

from src.beast_mode.mcp_integrations.google_calendar.auth_manager import GoogleAuthManager
from src.beast_mode.mcp_integrations.google_calendar.models import TokenInfo


class TestAuthenticationSecurity(unittest.TestCase):
    """Test suite for authentication security features."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.credentials_file = os.path.join(self.temp_dir, "credentials.json")
        
        # Create valid test credentials
        self.test_credentials = {
            "installed": {
                "client_id": "test-client-id.apps.googleusercontent.com",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "project_id": "test-project-123"
            }
        }
        
        # Write test credentials
        with open(self.credentials_file, 'w') as f:
            json.dump(self.test_credentials, f)
        
        # Set proper permissions
        os.chmod(self.credentials_file, 0o600)
        
        # Create auth manager
        self.config = {
            "credentials_file": self.credentials_file,
            "scopes": ["https://www.googleapis.com/auth/calendar"]
        }
        self.auth_manager = GoogleAuthManager(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_credentials_file_permissions_validation(self):
        """Test that credentials file permissions are properly validated."""
        # Test with correct permissions (600)
        os.chmod(self.credentials_file, 0o600)
        self.assertTrue(self.auth_manager._validate_credentials_file())
        
        # Test with incorrect permissions (644)
        os.chmod(self.credentials_file, 0o644)
        # Should still pass because it auto-fixes permissions
        self.assertTrue(self.auth_manager._validate_credentials_file())
        
        # Verify permissions were fixed
        file_mode = os.stat(self.credentials_file).st_mode & 0o777
        self.assertEqual(file_mode, 0o600)
        
        # Test with overly permissive permissions (666)
        os.chmod(self.credentials_file, 0o666)
        self.assertTrue(self.auth_manager._validate_credentials_file())
        
        # Verify permissions were fixed
        file_mode = os.stat(self.credentials_file).st_mode & 0o777
        self.assertEqual(file_mode, 0o600)
    
    def test_credentials_file_content_validation(self):
        """Test that credentials file content is properly validated."""
        # Test with missing file
        os.remove(self.credentials_file)
        self.assertFalse(self.auth_manager._validate_credentials_file())
        
        # Test with empty file
        with open(self.credentials_file, 'w') as f:
            f.write("")
        os.chmod(self.credentials_file, 0o600)
        self.assertFalse(self.auth_manager._validate_credentials_file())
        
        # Test with invalid JSON
        with open(self.credentials_file, 'w') as f:
            f.write("invalid json")
        os.chmod(self.credentials_file, 0o600)
        self.assertFalse(self.auth_manager._validate_credentials_file())
        
        # Test with missing required fields
        invalid_credentials = {
            "installed": {
                "client_id": "test-id"
                # Missing other required fields
            }
        }
        with open(self.credentials_file, 'w') as f:
            json.dump(invalid_credentials, f)
        os.chmod(self.credentials_file, 0o600)
        self.assertFalse(self.auth_manager._validate_credentials_file())
        
        # Test with non-HTTPS URLs
        invalid_credentials = {
            "installed": {
                "client_id": "test-client-id.apps.googleusercontent.com",
                "client_secret": "test-client-secret",
                "auth_uri": "http://accounts.google.com/o/oauth2/auth",  # HTTP instead of HTTPS
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        with open(self.credentials_file, 'w') as f:
            json.dump(invalid_credentials, f)
        os.chmod(self.credentials_file, 0o600)
        self.assertFalse(self.auth_manager._validate_credentials_file())
    
    def test_token_encryption_and_storage(self):
        """Test that tokens are properly encrypted and stored securely."""
        # Create test token info
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        
        # Save tokens
        self.auth_manager._save_tokens()
        
        # Verify files were created with correct permissions
        token_file = Path(self.temp_dir) / "tokens.encrypted"
        key_file = Path(self.temp_dir) / "token.key"
        
        self.assertTrue(token_file.exists())
        self.assertTrue(key_file.exists())
        
        # Check file permissions
        token_mode = token_file.stat().st_mode & 0o777
        key_mode = key_file.stat().st_mode & 0o777
        self.assertEqual(token_mode, 0o600)
        self.assertEqual(key_mode, 0o600)
        
        # Verify tokens are encrypted (not plain text)
        with open(token_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Should not contain plain text tokens
        self.assertNotIn(b"test-access-token", encrypted_data)
        self.assertNotIn(b"test-refresh-token", encrypted_data)
        
        # Verify we can decrypt and load tokens
        self.auth_manager.token_info = None
        self.auth_manager._load_existing_tokens()
        
        self.assertIsNotNone(self.auth_manager.token_info)
        self.assertEqual(self.auth_manager.token_info.access_token, "test-access-token")
        self.assertEqual(self.auth_manager.token_info.refresh_token, "test-refresh-token")
    
    def test_token_file_corruption_handling(self):
        """Test handling of corrupted token files."""
        # Create valid tokens first
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        self.auth_manager._save_tokens()
        
        token_file = Path(self.temp_dir) / "tokens.encrypted"
        
        # Corrupt the token file
        with open(token_file, 'wb') as f:
            f.write(b"corrupted data")
        
        # Should handle corruption gracefully
        self.auth_manager.token_info = None
        self.auth_manager._load_existing_tokens()
        
        # Should not have loaded corrupted tokens
        self.assertIsNone(self.auth_manager.token_info)
    
    def test_encryption_key_validation(self):
        """Test that encryption keys are properly validated."""
        # Create invalid key file
        key_file = Path(self.temp_dir) / "token.key"
        with open(key_file, 'wb') as f:
            f.write(b"invalid key data")
        key_file.chmod(0o600)
        
        # Should handle invalid key gracefully
        self.auth_manager._load_existing_tokens()
        self.assertIsNone(self.auth_manager.token_info)
    
    def test_token_security_validation(self):
        """Test the token security validation method."""
        # Test with no tokens (should pass)
        self.assertTrue(self.auth_manager.validate_token_security())
        
        # Create tokens with correct permissions
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        self.auth_manager._save_tokens()
        
        # Should pass with correct permissions
        self.assertTrue(self.auth_manager.validate_token_security())
        
        # Test with incorrect permissions
        token_file = Path(self.temp_dir) / "tokens.encrypted"
        token_file.chmod(0o644)
        
        # Should fail with incorrect permissions
        self.assertFalse(self.auth_manager.validate_token_security())
    
    def test_sensitive_data_cleanup(self):
        """Test that sensitive data is properly cleaned up."""
        # Create tokens
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        self.auth_manager._save_tokens()
        
        # Verify files exist
        token_file = Path(self.temp_dir) / "tokens.encrypted"
        key_file = Path(self.temp_dir) / "token.key"
        self.assertTrue(token_file.exists())
        self.assertTrue(key_file.exists())
        
        # Clean up sensitive data
        self.assertTrue(self.auth_manager.cleanup_sensitive_data())
        
        # Verify files are removed
        self.assertFalse(token_file.exists())
        self.assertFalse(key_file.exists())
        
        # Verify in-memory tokens are cleared
        self.assertIsNone(self.auth_manager.token_info)
    
    def test_credential_rotation(self):
        """Test credential rotation functionality."""
        # Create new credentials file
        new_credentials_file = os.path.join(self.temp_dir, "new_credentials.json")
        new_credentials = {
            "installed": {
                "client_id": "new-client-id.apps.googleusercontent.com",
                "client_secret": "new-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "project_id": "new-project-456"
            }
        }
        
        with open(new_credentials_file, 'w') as f:
            json.dump(new_credentials, f)
        os.chmod(new_credentials_file, 0o600)
        
        # Test rotation
        old_credentials_file = self.auth_manager.credentials_file
        self.assertTrue(self.auth_manager.rotate_credentials(new_credentials_file))
        
        # Verify credentials file was updated
        self.assertEqual(self.auth_manager.credentials_file, new_credentials_file)
        
        # Test rotation with invalid file
        invalid_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid")
        
        # Should fail and restore old credentials
        self.assertFalse(self.auth_manager.rotate_credentials(invalid_file))
        self.assertEqual(self.auth_manager.credentials_file, new_credentials_file)
    
    @patch('requests.post')
    def test_token_refresh_retry_logic(self, mock_post):
        """Test token refresh retry logic with various failure scenarios."""
        # Set up token info
        token_info = TokenInfo(
            access_token="old-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.utcnow() - timedelta(minutes=1),  # Expired
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        
        # Test successful refresh after retries
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new-access-token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        
        # First call fails with timeout, second succeeds
        mock_post.side_effect = [
            Exception("Timeout"),
            mock_response
        ]
        
        with patch('time.sleep'):  # Speed up test
            result = self.auth_manager.refresh_token(max_retries=2)
        
        self.assertTrue(result)
        self.assertEqual(self.auth_manager.token_info.access_token, "new-access-token")
        self.assertEqual(mock_post.call_count, 2)
    
    @patch('requests.post')
    def test_token_refresh_invalid_grant_handling(self, mock_post):
        """Test handling of invalid_grant error during token refresh."""
        # Set up token info
        token_info = TokenInfo(
            access_token="old-access-token",
            refresh_token="invalid-refresh-token",
            expires_at=datetime.utcnow() - timedelta(minutes=1),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        
        # Mock invalid_grant response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'invalid_grant'}
        mock_response.content = b'{"error": "invalid_grant"}'
        
        mock_post.return_value = mock_response
        
        result = self.auth_manager.refresh_token()
        
        # Should fail and clear tokens
        self.assertFalse(result)
        self.assertIsNone(self.auth_manager.token_info)
    
    def test_https_only_validation(self):
        """Test that only HTTPS URLs are accepted in credentials."""
        # Test with HTTP URLs (should fail)
        http_credentials = {
            "installed": {
                "client_id": "test-client-id.apps.googleusercontent.com",
                "client_secret": "test-client-secret",
                "auth_uri": "http://accounts.google.com/o/oauth2/auth",
                "token_uri": "http://oauth2.googleapis.com/token"
            }
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(http_credentials, f)
        os.chmod(self.credentials_file, 0o600)
        
        self.assertFalse(self.auth_manager._validate_credentials_file())
    
    def test_token_never_logged_in_plain_text(self):
        """Test that tokens are never logged in plain text."""
        with patch.object(self.auth_manager.logger, 'info') as mock_log_info, \
             patch.object(self.auth_manager.logger, 'error') as mock_log_error, \
             patch.object(self.auth_manager.logger, 'warning') as mock_log_warning:
            
            # Create and save tokens
            token_info = TokenInfo(
                access_token="secret-access-token",
                refresh_token="secret-refresh-token",
                expires_at=datetime.utcnow() + timedelta(hours=1),
                scopes=["https://www.googleapis.com/auth/calendar"]
            )
            self.auth_manager.token_info = token_info
            self.auth_manager._save_tokens()
            
            # Check all log calls
            all_calls = (mock_log_info.call_args_list + 
                        mock_log_error.call_args_list + 
                        mock_log_warning.call_args_list)
            
            for call in all_calls:
                args, kwargs = call
                # Check message
                if args:
                    message = str(args[0])
                    self.assertNotIn("secret-access-token", message)
                    self.assertNotIn("secret-refresh-token", message)
                
                # Check extra data
                if 'extra' in kwargs:
                    extra_str = str(kwargs['extra'])
                    self.assertNotIn("secret-access-token", extra_str)
                    self.assertNotIn("secret-refresh-token", extra_str)
    
    def test_directory_permissions_security(self):
        """Test that credentials directory has proper permissions."""
        # Create tokens to ensure directory exists
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        self.auth_manager._save_tokens()
        
        # Check directory permissions
        credentials_dir = Path(self.temp_dir)
        dir_mode = credentials_dir.stat().st_mode & 0o777
        
        # Directory should not be world-readable/writable
        self.assertEqual(dir_mode & 0o077, 0, f"Directory permissions too permissive: {oct(dir_mode)}")
    
    def test_atomic_file_operations(self):
        """Test that file operations are atomic to prevent corruption."""
        # Create initial tokens
        token_info = TokenInfo(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.auth_manager.token_info = token_info
        
        # Mock file write to fail after creating temp file
        original_rename = Path.rename
        
        def failing_rename(self, target):
            if str(self).endswith('.tmp'):
                raise OSError("Simulated failure")
            return original_rename(self, target)
        
        with patch.object(Path, 'rename', failing_rename):
            # This should fail but not leave temp files
            with self.assertRaises(OSError):
                self.auth_manager._save_tokens()
        
        # Verify no temp files are left behind
        temp_files = list(Path(self.temp_dir).glob("*.tmp"))
        self.assertEqual(len(temp_files), 0, f"Temp files left behind: {temp_files}")


if __name__ == '__main__':
    unittest.main()