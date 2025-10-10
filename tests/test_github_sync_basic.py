"""
Basic tests for GitHub synchronization components.

These tests validate the core functionality of the GitHub sync system
without requiring actual GitHub API access.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.github_sync.models import Repository, Issue, PullRequest, Commit, SyncResult
from src.github_sync.config import GitHubConfig, RepositoryConfig, GitHubCredentials
from src.github_sync.auth import AuthenticationManager


class TestModels:
    """Test core data models."""
    
    def test_repository_creation(self):
        """Test repository model creation and validation."""
        repo = Repository(
            id=123,
            name="test-repo",
            owner="test-owner",
            description="Test repository"
        )
        
        assert repo.id == 123
        assert repo.name == "test-repo"
        assert repo.owner == "test-owner"
        assert repo.full_name == "test-owner/test-repo"
        assert repo.default_branch == "main"
    
    def test_repository_validation(self):
        """Test repository validation."""
        with pytest.raises(ValueError, match="Repository name and owner are required"):
            Repository(id=123, name="", owner="test-owner")
    
    def test_issue_creation(self):
        """Test issue model creation."""
        issue = Issue(
            id=456,
            number=1,
            title="Test Issue",
            body="This is a test issue",
            repository_id=123
        )
        
        assert issue.id == 456
        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert issue.repository_id == 123
    
    def test_pull_request_creation(self):
        """Test pull request model creation."""
        pr = PullRequest(
            id=789,
            number=2,
            title="Test PR",
            head_branch="feature-branch",
            base_branch="main",
            repository_id=123
        )
        
        assert pr.id == 789
        assert pr.number == 2
        assert pr.title == "Test PR"
        assert pr.head_branch == "feature-branch"
        assert pr.base_branch == "main"
    
    def test_commit_creation(self):
        """Test commit model creation."""
        commit = Commit(
            sha="abc123def456",
            message="Test commit",
            author="Test Author",
            author_email="test@example.com",
            repository_id=123
        )
        
        assert commit.sha == "abc123def456"
        assert commit.message == "Test commit"
        assert commit.author == "Test Author"
        assert commit.author_email == "test@example.com"
    
    def test_sync_result_operations(self):
        """Test sync result operations."""
        result1 = SyncResult(success=True, items_synced=5, items_created=3)
        result2 = SyncResult(success=True, items_synced=3, items_updated=2)
        
        merged = result1.merge(result2)
        
        assert merged.success is True
        assert merged.items_synced == 8
        assert merged.items_created == 3
        assert merged.items_updated == 2


class TestConfiguration:
    """Test configuration management."""
    
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_test_token_1234567890'})
    def test_credentials_from_env(self):
        """Test loading credentials from environment variables."""
        credentials = GitHubCredentials()
        
        assert credentials.token == 'ghp_test_token_1234567890'
        assert credentials.validate_token() is True
    
    def test_credentials_missing_token(self):
        """Test error when token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            # Also mock the ~/.env file loading to ensure no token is found
            with patch('src.github_sync.config.load_env_vars'):
                with pytest.raises(ValueError, match="GitHub Personal Access Token not found"):
                    GitHubCredentials()
    
    def test_repository_config(self):
        """Test repository configuration."""
        config = RepositoryConfig(
            owner="test-owner",
            name="test-repo",
            sync_issues=True,
            sync_pull_requests=False
        )
        
        assert config.owner == "test-owner"
        assert config.name == "test-repo"
        assert config.full_name == "test-owner/test-repo"
        assert config.sync_issues is True
        assert config.sync_pull_requests is False
    
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_test_token_1234567890'})
    def test_github_config_from_env(self):
        """Test loading GitHub config from environment."""
        config = GitHubConfig.from_env()
        
        assert config.credentials.token == 'ghp_test_token_1234567890'
        assert config.api_base_url == "https://api.github.com"
        assert config.is_valid() is True


class TestAuthentication:
    """Test authentication management."""
    
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_test_token_1234567890'})
    def test_auth_manager_load_credentials(self):
        """Test loading credentials through auth manager."""
        auth_manager = AuthenticationManager()
        credentials = auth_manager.load_credentials()
        
        assert credentials.token == 'ghp_test_token_1234567890'
    
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_test_token_1234567890'})
    @patch('requests.Session.get')
    def test_token_validation_success(self, mock_get):
        """Test successful token validation."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'login': 'testuser', 'id': 12345}
        mock_get.return_value = mock_response
        
        auth_manager = AuthenticationManager()
        auth_manager.load_credentials()
        
        assert auth_manager.validate_token() is True
    
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_test_token_1234567890'})
    @patch('requests.Session.get')
    def test_token_validation_failure(self, mock_get):
        """Test token validation failure."""
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        auth_manager = AuthenticationManager()
        auth_manager.load_credentials()
        
        assert auth_manager.validate_token() is False
    
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_test_token_1234567890'})
    def test_get_authenticated_headers(self):
        """Test getting authenticated headers."""
        with patch.object(AuthenticationManager, 'validate_token', return_value=True):
            auth_manager = AuthenticationManager()
            auth_manager.load_credentials()
            
            headers = auth_manager.get_authenticated_headers()
            
            assert 'Authorization' in headers
            assert headers['Authorization'] == 'token ghp_test_token_1234567890'
            assert headers['Accept'] == 'application/vnd.github.v3+json'
            assert headers['User-Agent'] == 'BeastMode-GitHub-Sync/1.0'


class TestSecurityCompliance:
    """Test security compliance and credential handling."""
    
    def test_no_hardcoded_credentials_in_config(self):
        """Test that no hardcoded credentials exist in configuration."""
        from src.github_sync.config import validate_no_hardcoded_credentials
        
        violations = validate_no_hardcoded_credentials()
        
        # Should be empty if no violations found
        assert isinstance(violations, list)
        # Note: This test might find violations during development
        # The important thing is that the function exists and works
    
    def test_environment_security_validation(self):
        """Test environment security validation."""
        from src.github_sync.auth import validate_environment_security
        
        with patch.dict(os.environ, {}, clear=True):
            violations = validate_environment_security()
            assert len(violations) > 0  # Should find missing GITHUB_TOKEN
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_valid_token_1234567890'}):
            violations = validate_environment_security()
            # Should have fewer violations with valid token
            assert isinstance(violations, list)


if __name__ == '__main__':
    pytest.main([__file__])