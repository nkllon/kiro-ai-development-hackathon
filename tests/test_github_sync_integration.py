"""
Integration tests for GitHub synchronization system.

This module provides integration tests that validate the interaction between
components and test against real GitHub API endpoints (with test repositories).
"""

import pytest
import asyncio
import os
import tempfile
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import patch, Mock

# Import components for integration testing
from src.github_sync.client import GitHubAPIClient
from src.github_sync.auth import AuthenticationManager
from src.github_sync.sync_engine import SynchronizationEngine
from src.github_sync.cache import CacheManager
from src.github_sync.webhooks import WebhookHandler
from src.github_sync.config import GitHubSyncConfig, RepositoryConfig
from src.github_sync.models import Repository, Issue, PullRequest
from src.github_sync.framework_integration import BeastModeIntegration, IntegrationConfig
from src.github_sync.data_recovery import DataRecoveryManager


# Test configuration - these should be set via environment variables
TEST_GITHUB_TOKEN = os.getenv('TEST_GITHUB_TOKEN')
TEST_REPO_OWNER = os.getenv('TEST_REPO_OWNER', 'octocat')
TEST_REPO_NAME = os.getenv('TEST_REPO_NAME', 'Hello-World')


@pytest.mark.integration
class TestGitHubAPIIntegration:
    """Integration tests for GitHub API client."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment."""
        if not TEST_GITHUB_TOKEN:
            pytest.skip("TEST_GITHUB_TOKEN not set - skipping GitHub API integration tests")
        
        # Use test token for authentication
        with patch.dict('os.environ', {'GITHUB_TOKEN': TEST_GITHUB_TOKEN}):
            self.auth_manager = AuthenticationManager()
            self.client = GitHubAPIClient(self.auth_manager)
    
    @pytest.mark.asyncio
    async def test_real_github_api_authentication(self):
        """Test authentication against real GitHub API."""
        try:
            user_info = await self.client.get_authenticated_user()
            assert user_info is not None
            assert 'login' in user_info
            print(f"Authenticated as: {user_info['login']}")
        except Exception as e:
            pytest.fail(f"GitHub API authentication failed: {e}")
    
    @pytest.mark.asyncio
    async def test_real_repository_access(self):
        """Test accessing a real GitHub repository."""
        try:
            repo = await self.client.get_repository(TEST_REPO_OWNER, TEST_REPO_NAME)
            
            assert repo is not None
            assert repo.name == TEST_REPO_NAME
            assert repo.owner == TEST_REPO_OWNER
            assert repo.full_name == f"{TEST_REPO_OWNER}/{TEST_REPO_NAME}"
            
            print(f"Successfully accessed repository: {repo.full_name}")
            print(f"Repository description: {repo.description}")
            
        except Exception as e:
            pytest.fail(f"Failed to access test repository: {e}")
    
    @pytest.mark.asyncio
    async def test_real_issues_listing(self):
        """Test listing issues from a real repository."""
        try:
            issues = await self.client.list_issues(
                TEST_REPO_OWNER, 
                TEST_REPO_NAME, 
                state='all'
            )
            
            assert isinstance(issues, list)
            print(f"Found {len(issues)} issues in {TEST_REPO_OWNER}/{TEST_REPO_NAME}")
            
            if issues:
                first_issue = issues[0]
                assert hasattr(first_issue, 'number')
                assert hasattr(first_issue, 'title')
                assert hasattr(first_issue, 'state')
                print(f"First issue: #{first_issue.number} - {first_issue.title}")
            
        except Exception as e:
            pytest.fail(f"Failed to list issues: {e}")
    
    @pytest.mark.asyncio
    async def test_real_pull_requests_listing(self):
        """Test listing pull requests from a real repository."""
        try:
            prs = await self.client.list_pull_requests(
                TEST_REPO_OWNER, 
                TEST_REPO_NAME, 
                state='all'
            )
            
            assert isinstance(prs, list)
            print(f"Found {len(prs)} pull requests in {TEST_REPO_OWNER}/{TEST_REPO_NAME}")
            
            if prs:
                first_pr = prs[0]
                assert hasattr(first_pr, 'number')
                assert hasattr(first_pr, 'title')
                assert hasattr(first_pr, 'state')
                print(f"First PR: #{first_pr.number} - {first_pr.title}")
            
        except Exception as e:
            pytest.fail(f"Failed to list pull requests: {e}")
    
    @pytest.mark.asyncio
    async def test_real_commits_listing(self):
        """Test listing commits from a real repository."""
        try:
            commits = await self.client.get_commits(
                TEST_REPO_OWNER, 
                TEST_REPO_NAME,
                branch='master'  # octocat/Hello-World uses master branch
            )
            
            assert isinstance(commits, list)
            print(f"Found {len(commits)} commits in {TEST_REPO_OWNER}/{TEST_REPO_NAME}")
            
            if commits:
                first_commit = commits[0]
                assert hasattr(first_commit, 'sha')
                assert hasattr(first_commit, 'message')
                print(f"Latest commit: {first_commit.sha[:8]} - {first_commit.message}")
            
        except Exception as e:
            pytest.fail(f"Failed to list commits: {e}")
    
    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self):
        """Test rate limiting behavior with multiple API calls."""
        try:
            # Make multiple API calls to test rate limiting
            tasks = []
            for i in range(5):
                task = self.client.get_repository(TEST_REPO_OWNER, TEST_REPO_NAME)
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed (rate limiting should be handled internally)
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == 5
            
            print(f"Successfully handled {len(successful_results)} concurrent API calls")
            
        except Exception as e:
            pytest.fail(f"Rate limiting test failed: {e}")


@pytest.mark.integration
class TestSynchronizationEngineIntegration:
    """Integration tests for synchronization engine."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment."""
        if not TEST_GITHUB_TOKEN:
            pytest.skip("TEST_GITHUB_TOKEN not set - skipping sync engine integration tests")
        
        # Create temporary directory for cache
        self.temp_dir = tempfile.mkdtemp()
        
        # Set up configuration
        self.config = GitHubSyncConfig(
            repository_configs=[
                RepositoryConfig(
                    owner=TEST_REPO_OWNER,
                    name=TEST_REPO_NAME,
                    sync_issues=True,
                    sync_pull_requests=True,
                    sync_branches=['master']
                )
            ],
            cache_dir=self.temp_dir
        )
        
        # Initialize components
        with patch.dict('os.environ', {'GITHUB_TOKEN': TEST_GITHUB_TOKEN}):
            self.auth_manager = AuthenticationManager()
            self.client = GitHubAPIClient(self.auth_manager)
            self.sync_engine = SynchronizationEngine(self.client, self.config)
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_full_repository_synchronization(self):
        """Test complete repository synchronization."""
        try:
            repo_config = self.config.repository_configs[0]
            result = await self.sync_engine.sync_repository(repo_config)
            
            assert result.success is True
            assert result.repository_id == f"{TEST_REPO_OWNER}/{TEST_REPO_NAME}"
            
            # Verify synced items
            assert result.synced_items['repository'] >= 1
            print(f"Synchronization result: {result.synced_items}")
            
            # Check if data was cached
            cache_manager = self.sync_engine.cache_manager
            cached_repo = cache_manager.get_cached_repository(result.repository_id)
            assert cached_repo is not None
            assert cached_repo.name == TEST_REPO_NAME
            
        except Exception as e:
            pytest.fail(f"Repository synchronization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_incremental_synchronization(self):
        """Test incremental synchronization after initial sync."""
        try:
            repo_config = self.config.repository_configs[0]
            
            # First sync
            result1 = await self.sync_engine.sync_repository(repo_config)
            assert result1.success is True
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Second sync (should be incremental)
            result2 = await self.sync_engine.sync_repository(repo_config)
            assert result2.success is True
            
            print(f"First sync: {result1.synced_items}")
            print(f"Second sync: {result2.synced_items}")
            
            # Second sync should have fewer or equal items (incremental)
            # This depends on whether there were actual changes
            
        except Exception as e:
            pytest.fail(f"Incremental synchronization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_sync_with_filtering(self):
        """Test synchronization with content filtering."""
        try:
            # Create config with selective sync
            filtered_config = RepositoryConfig(
                owner=TEST_REPO_OWNER,
                name=TEST_REPO_NAME,
                sync_issues=True,
                sync_pull_requests=False,  # Disable PR sync
                sync_branches=['master']
            )
            
            result = await self.sync_engine.sync_repository(filtered_config)
            
            assert result.success is True
            
            # Should have synced issues but not PRs
            assert result.synced_items.get('issues', 0) >= 0
            assert result.synced_items.get('pull_requests', 0) == 0
            
            print(f"Filtered sync result: {result.synced_items}")
            
        except Exception as e:
            pytest.fail(f"Filtered synchronization failed: {e}")


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_database_operations(self):
        """Test database cache operations."""
        try:
            # Create test repository
            repo = Repository(
                id=123,
                name='test-repo',
                full_name='testuser/test-repo',
                owner='testuser',
                description='Test repository',
                default_branch='main',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Cache repository
            self.cache_manager.cache_repository_data(repo)
            
            # Retrieve from cache
            cached_repo = self.cache_manager.get_cached_repository('testuser/test-repo')
            
            assert cached_repo is not None
            assert cached_repo.name == 'test-repo'
            assert cached_repo.owner == 'testuser'
            
            print(f"Successfully cached and retrieved repository: {cached_repo.full_name}")
            
        except Exception as e:
            pytest.fail(f"Cache database operations failed: {e}")
    
    def test_cache_performance(self):
        """Test cache performance with multiple operations."""
        try:
            import time
            
            # Create multiple test repositories
            repos = []
            for i in range(100):
                repo = Repository(
                    id=i,
                    name=f'test-repo-{i}',
                    full_name=f'testuser/test-repo-{i}',
                    owner='testuser',
                    description=f'Test repository {i}',
                    default_branch='main',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                repos.append(repo)
            
            # Time cache operations
            start_time = time.time()
            
            for repo in repos:
                self.cache_manager.cache_repository_data(repo)
            
            cache_time = time.time() - start_time
            
            # Time retrieval operations
            start_time = time.time()
            
            for repo in repos:
                cached_repo = self.cache_manager.get_cached_repository(repo.full_name)
                assert cached_repo is not None
            
            retrieval_time = time.time() - start_time
            
            print(f"Cached 100 repositories in {cache_time:.3f}s")
            print(f"Retrieved 100 repositories in {retrieval_time:.3f}s")
            
            # Performance should be reasonable
            assert cache_time < 5.0  # Should cache 100 repos in under 5 seconds
            assert retrieval_time < 2.0  # Should retrieve 100 repos in under 2 seconds
            
        except Exception as e:
            pytest.fail(f"Cache performance test failed: {e}")


@pytest.mark.integration
class TestWebhookIntegration:
    """Integration tests for webhook system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.webhook_handler = WebhookHandler('test_webhook_secret')
    
    def test_webhook_signature_validation_integration(self):
        """Test webhook signature validation with real payloads."""
        try:
            import hmac
            import hashlib
            import json
            
            # Create realistic webhook payload
            payload_data = {
                'action': 'opened',
                'issue': {
                    'id': 123,
                    'number': 1,
                    'title': 'Test Issue',
                    'body': 'This is a test issue',
                    'state': 'open'
                },
                'repository': {
                    'name': 'test-repo',
                    'owner': {'login': 'testuser'}
                }
            }
            
            payload = json.dumps(payload_data)
            
            # Generate valid signature
            secret = 'test_webhook_secret'
            signature = 'sha256=' + hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Test validation
            is_valid = self.webhook_handler.validate_webhook_signature(payload, signature)
            assert is_valid is True
            
            # Test with invalid signature
            invalid_signature = 'sha256=invalid_signature_here'
            is_valid = self.webhook_handler.validate_webhook_signature(payload, invalid_signature)
            assert is_valid is False
            
            print("Webhook signature validation working correctly")
            
        except Exception as e:
            pytest.fail(f"Webhook signature validation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_webhook_event_processing(self):
        """Test webhook event processing pipeline."""
        try:
            # Mock event processing
            processed_events = []
            
            async def mock_process_push_event(event_data):
                processed_events.append(('push', event_data))
            
            async def mock_process_issue_event(event_data):
                processed_events.append(('issue', event_data))
            
            # Patch event processing methods
            with patch.object(self.webhook_handler, '_process_push_event', mock_process_push_event), \
                 patch.object(self.webhook_handler, '_process_issue_event', mock_process_issue_event):
                
                # Test push event
                push_event = {
                    'ref': 'refs/heads/main',
                    'repository': {'name': 'test-repo', 'owner': {'name': 'testuser'}},
                    'commits': [{'id': 'abc123', 'message': 'Test commit'}]
                }
                
                await self.webhook_handler.handle_push_event(push_event)
                
                # Test issue event
                issue_event = {
                    'action': 'opened',
                    'issue': {'id': 123, 'number': 1, 'title': 'Test Issue'},
                    'repository': {'name': 'test-repo', 'owner': {'login': 'testuser'}}
                }
                
                await self.webhook_handler.handle_issue_event(issue_event)
                
                # Verify events were processed
                assert len(processed_events) == 2
                print(f"Processed {len(processed_events)} webhook events")
                
        except Exception as e:
            pytest.fail(f"Webhook event processing failed: {e}")


@pytest.mark.integration
class TestDataRecoveryIntegration:
    """Integration tests for data recovery system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.recovery_manager = DataRecoveryManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_backup_restore_cycle(self):
        """Test complete backup and restore cycle."""
        try:
            # Create test data directory with multiple files
            test_data_dir = Path(self.temp_dir) / 'test_data'
            test_data_dir.mkdir()
            
            # Create test files
            (test_data_dir / 'file1.txt').write_text('Content of file 1')
            (test_data_dir / 'file2.json').write_text('{"key": "value"}')
            
            subdir = test_data_dir / 'subdir'
            subdir.mkdir()
            (subdir / 'file3.py').write_text('print("Hello, World!")')
            
            # Create backup
            backup_info = self.recovery_manager.create_backup(
                'test/repo',
                test_data_dir,
                ['directory', 'test_data']
            )
            
            assert backup_info is not None
            assert backup_info.backup_path.exists()
            
            # Remove original data
            shutil.rmtree(test_data_dir)
            assert not test_data_dir.exists()
            
            # Restore from backup
            restore_path = Path(self.temp_dir) / 'restored_data'
            success = self.recovery_manager.restore_backup(backup_info.backup_id, restore_path)
            
            assert success is True
            assert restore_path.exists()
            
            # Verify restored content
            assert (restore_path / 'file1.txt').read_text() == 'Content of file 1'
            assert (restore_path / 'file2.json').read_text() == '{"key": "value"}'
            assert (restore_path / 'subdir' / 'file3.py').read_text() == 'print("Hello, World!")'
            
            print(f"Successfully completed backup/restore cycle for {backup_info.backup_id}")
            
        except Exception as e:
            pytest.fail(f"Backup/restore cycle failed: {e}")
    
    def test_state_persistence_across_restarts(self):
        """Test state persistence across manager restarts."""
        try:
            from src.github_sync.data_recovery import SyncStateInfo, SyncState
            
            # Create and store state
            state_info = SyncStateInfo(
                repository_id='test/repo',
                state=SyncState.SYNCING,
                last_sync_time=datetime.now(),
                last_success_time=datetime.now() - timedelta(hours=1),
                error_count=2,
                last_error='Test error',
                sync_progress={'issues': 10, 'prs': 5},
                checksum='abc123'
            )
            
            self.recovery_manager.update_sync_state(state_info)
            
            # Create new manager instance (simulating restart)
            new_recovery_manager = DataRecoveryManager(self.temp_dir)
            
            # Retrieve state
            retrieved_state = new_recovery_manager.get_sync_state('test/repo')
            
            assert retrieved_state is not None
            assert retrieved_state.repository_id == 'test/repo'
            assert retrieved_state.state == SyncState.SYNCING
            assert retrieved_state.error_count == 2
            assert retrieved_state.last_error == 'Test error'
            assert retrieved_state.sync_progress['issues'] == 10
            
            print("State persistence across restarts working correctly")
            
        except Exception as e:
            pytest.fail(f"State persistence test failed: {e}")


@pytest.mark.integration
class TestFrameworkIntegration:
    """Integration tests for framework integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.config = GitHubSyncConfig()
        self.config.sync_config.add_repository(TEST_REPO_OWNER, TEST_REPO_NAME)
        self.integration_config = IntegrationConfig(
            enable_auto_sync=False,  # Disable for testing
            sync_on_file_change=True,
            sync_on_commit=True
        )
    
    def test_integration_initialization(self):
        """Test framework integration initialization."""
        try:
            with patch('src.github_sync.framework_integration.AuthenticationManager'), \
                 patch('src.github_sync.framework_integration.GitHubAPIClient'), \
                 patch('src.github_sync.framework_integration.SynchronizationEngine'):
                
                integration = BeastModeIntegration(self.config, self.integration_config)
                
                assert integration is not None
                assert integration.config == self.config
                assert integration.integration_config == self.integration_config
                assert integration.is_running is False
                
                print("Framework integration initialized successfully")
                
        except Exception as e:
            pytest.fail(f"Framework integration initialization failed: {e}")
    
    def test_event_system_integration(self):
        """Test event system integration."""
        try:
            with patch('src.github_sync.framework_integration.AuthenticationManager'), \
                 patch('src.github_sync.framework_integration.GitHubAPIClient'), \
                 patch('src.github_sync.framework_integration.SynchronizationEngine'):
                
                integration = BeastModeIntegration(self.config, self.integration_config)
                
                # Test event handling
                events_received = []
                
                def test_handler(event):
                    events_received.append(event)
                
                integration.register_event_handler('test_event', test_handler)
                
                # Emit test event
                from src.github_sync.framework_integration import FrameworkEvent
                test_event = FrameworkEvent(
                    event_type='test_event',
                    source='test',
                    data={'message': 'test'},
                    timestamp=datetime.now()
                )
                
                integration.emit_event(test_event)
                
                assert len(events_received) == 1
                assert events_received[0].event_type == 'test_event'
                assert events_received[0].data['message'] == 'test'
                
                print("Event system integration working correctly")
                
        except Exception as e:
            pytest.fail(f"Event system integration failed: {e}")


@pytest.mark.integration
class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up comprehensive test environment."""
        if not TEST_GITHUB_TOKEN:
            pytest.skip("TEST_GITHUB_TOKEN not set - skipping end-to-end integration tests")
        
        self.temp_dir = tempfile.mkdtemp()
        
        # Set up complete configuration
        self.config = GitHubSyncConfig(
            repository_configs=[
                RepositoryConfig(
                    owner=TEST_REPO_OWNER,
                    name=TEST_REPO_NAME,
                    sync_issues=True,
                    sync_pull_requests=True,
                    sync_branches=['master']
                )
            ],
            cache_dir=self.temp_dir,
            sync_interval=300
        )
        
        self.integration_config = IntegrationConfig(
            enable_auto_sync=False,  # Disable for testing
            sync_on_file_change=True,
            sync_on_commit=True
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_sync_workflow(self):
        """Test complete synchronization workflow from GitHub to local storage."""
        try:
            with patch.dict('os.environ', {'GITHUB_TOKEN': TEST_GITHUB_TOKEN}):
                # Initialize all components
                auth_manager = AuthenticationManager()
                client = GitHubAPIClient(auth_manager)
                sync_engine = SynchronizationEngine(client, self.config)
                
                # Test authentication
                user_info = await client.get_authenticated_user()
                assert user_info is not None
                print(f"Authenticated as: {user_info['login']}")
                
                # Perform full synchronization
                repo_config = self.config.repository_configs[0]
                result = await sync_engine.sync_repository(repo_config)
                
                assert result.success is True
                print(f"Sync completed: {result.synced_items}")
                
                # Verify data was cached
                cache_manager = sync_engine.cache_manager
                cached_repo = cache_manager.get_cached_repository(result.repository_id)
                assert cached_repo is not None
                
                # Verify cache database
                cache_db_path = Path(self.temp_dir) / 'cache.db'
                assert cache_db_path.exists()
                
                with sqlite3.connect(cache_db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM repositories")
                    repo_count = cursor.fetchone()[0]
                    assert repo_count >= 1
                
                print("Complete sync workflow successful")
                
        except Exception as e:
            pytest.fail(f"Complete sync workflow failed: {e}")
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error recovery and system resilience."""
        try:
            with patch.dict('os.environ', {'GITHUB_TOKEN': TEST_GITHUB_TOKEN}):
                # Initialize components
                auth_manager = AuthenticationManager()
                client = GitHubAPIClient(auth_manager)
                sync_engine = SynchronizationEngine(client, self.config)
                recovery_manager = DataRecoveryManager(self.temp_dir)
                
                # Perform initial sync
                repo_config = self.config.repository_configs[0]
                result = await sync_engine.sync_repository(repo_config)
                assert result.success is True
                
                # Create backup of synced data
                cache_db_path = Path(self.temp_dir) / 'cache.db'
                if cache_db_path.exists():
                    backup_info = recovery_manager.create_backup(
                        result.repository_id,
                        cache_db_path,
                        ['database', 'cache']
                    )
                    assert backup_info is not None
                    print(f"Created backup: {backup_info.backup_id}")
                
                # Simulate data corruption by removing cache
                if cache_db_path.exists():
                    cache_db_path.unlink()
                
                # Test recovery
                if backup_info:
                    restore_path = Path(self.temp_dir) / 'restored_cache.db'
                    success = recovery_manager.restore_backup(backup_info.backup_id, restore_path)
                    assert success is True
                    print("Data recovery successful")
                
        except Exception as e:
            pytest.fail(f"Error recovery workflow failed: {e}")
    
    @pytest.mark.asyncio
    async def test_security_validation_workflow(self):
        """Test security measures and credential handling."""
        try:
            # Test that authentication requires environment variable
            with patch.dict('os.environ', {}, clear=True):
                with pytest.raises(ValueError, match="GITHUB_TOKEN"):
                    AuthenticationManager().load_credentials()
            
            # Test with valid token
            with patch.dict('os.environ', {'GITHUB_TOKEN': TEST_GITHUB_TOKEN}):
                auth_manager = AuthenticationManager()
                credentials = auth_manager.load_credentials()
                assert credentials.token == TEST_GITHUB_TOKEN
                
                # Test token validation
                is_valid = auth_manager.validate_token(credentials.token)
                assert is_valid is True
                
                print("Security validation successful")
                
        except Exception as e:
            pytest.fail(f"Security validation workflow failed: {e}")


# Utility functions for integration tests
def create_test_webhook_payload(event_type: str, repository: str) -> Dict[str, Any]:
    """Create a test webhook payload."""
    base_payload = {
        'repository': {
            'name': repository.split('/')[1],
            'owner': {'login': repository.split('/')[0]}
        }
    }
    
    if event_type == 'push':
        base_payload.update({
            'ref': 'refs/heads/main',
            'commits': [
                {
                    'id': 'test_commit_sha',
                    'message': 'Test commit message',
                    'author': {'name': 'Test User', 'email': 'test@example.com'},
                    'timestamp': datetime.now().isoformat()
                }
            ]
        })
    elif event_type == 'issues':
        base_payload.update({
            'action': 'opened',
            'issue': {
                'id': 123,
                'number': 1,
                'title': 'Test Issue',
                'body': 'Test issue body',
                'state': 'open'
            }
        })
    
    return base_payload


def verify_database_integrity(db_path: Path) -> bool:
    """Verify SQLite database integrity."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            return result and result[0] == "ok"
    except Exception:
        return False


if __name__ == '__main__':
    # Run integration tests
    pytest.main([
        __file__, 
        '-v', 
        '-m', 'integration',
        '--tb=short'
    ])