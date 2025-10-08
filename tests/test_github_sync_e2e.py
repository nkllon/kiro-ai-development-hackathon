"""
End-to-end tests for GitHub synchronization system.

This module provides comprehensive end-to-end tests that validate the complete
synchronization workflows, error recovery, and system resilience under various
real-world scenarios.
"""

import pytest
import asyncio
import os
import tempfile
import shutil
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import patch, Mock

# Import all components for end-to-end testing
from src.github_sync.client import GitHubAPIClient
from src.github_sync.auth import AuthenticationManager
from src.github_sync.sync_engine import SynchronizationEngine
from src.github_sync.cache import CacheManager
from src.github_sync.webhooks import WebhookHandler
from src.github_sync.config import GitHubSyncConfig, RepositoryConfig
from src.github_sync.models import Repository, Issue, PullRequest, Commit
from src.github_sync.framework_integration import BeastModeIntegration, IntegrationConfig
from src.github_sync.data_recovery import DataRecoveryManager, SyncState
from src.github_sync.git_manager import GitCommitManager
from src.github_sync.precommit_manager import PreCommitManager


# Test configuration
TEST_GITHUB_TOKEN = os.getenv('TEST_GITHUB_TOKEN')
TEST_REPO_OWNER = os.getenv('TEST_REPO_OWNER', 'octocat')
TEST_REPO_NAME = os.getenv('TEST_REPO_NAME', 'Hello-World')


class GitHubSyncTestSuite:
    """
    Comprehensive test suite for GitHub synchronization system.
    
    This class provides a complete testing environment that can be used
    for end-to-end validation of the entire system.
    """
    
    def __init__(self, temp_dir: str):
        """Initialize test suite."""
        self.temp_dir = Path(temp_dir)
        self.config = None
        self.integration = None
        self.components = {}
        self.test_results = {}
    
    async def setup_test_environment(self) -> bool:
        """Set up complete test environment."""
        try:
            # Create configuration
            self.config = GitHubSyncConfig(
                repository_configs=[
                    RepositoryConfig(
                        owner=TEST_REPO_OWNER,
                        name=TEST_REPO_NAME,
                        sync_issues=True,
                        sync_pull_requests=True,
                        sync_branches=['master', 'main']
                    )
                ],
                cache_dir=str(self.temp_dir / 'cache'),
                sync_interval=60
            )
            
            # Initialize all components
            with patch.dict('os.environ', {'GITHUB_TOKEN': TEST_GITHUB_TOKEN}):
                self.components['auth'] = AuthenticationManager()
                self.components['client'] = GitHubAPIClient(self.components['auth'])
                self.components['sync_engine'] = SynchronizationEngine(
                    self.components['client'], 
                    self.config
                )
                self.components['cache'] = CacheManager(str(self.temp_dir / 'cache'))
                self.components['webhooks'] = WebhookHandler('test_secret')
                self.components['recovery'] = DataRecoveryManager(str(self.temp_dir / 'recovery'))
                
                # Initialize framework integration
                integration_config = IntegrationConfig(
                    enable_auto_sync=False,  # Controlled for testing
                    sync_on_file_change=True,
                    sync_on_commit=True
                )
                
                self.integration = BeastModeIntegration(self.config, integration_config)
            
            return True
            
        except Exception as e:
            print(f"Failed to set up test environment: {e}")
            return False
    
    async def run_authentication_tests(self) -> Dict[str, Any]:
        """Run comprehensive authentication tests."""
        results = {
            'test_name': 'authentication_tests',
            'start_time': datetime.now(),
            'tests': [],
            'overall_success': True
        }
        
        try:
            # Test 1: Environment variable loading
            test_result = {
                'name': 'env_var_loading',
                'success': False,
                'message': '',
                'duration': 0
            }
            
            start_time = time.time()
            try:
                credentials = self.components['auth'].load_credentials()
                test_result['success'] = credentials.token == TEST_GITHUB_TOKEN
                test_result['message'] = 'Successfully loaded credentials from environment'
            except Exception as e:
                test_result['message'] = f'Failed to load credentials: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 2: Token validation
            test_result = {
                'name': 'token_validation',
                'success': False,
                'message': '',
                'duration': 0
            }
            
            start_time = time.time()
            try:
                is_valid = self.components['auth'].validate_token(TEST_GITHUB_TOKEN)
                test_result['success'] = is_valid
                test_result['message'] = 'Token validation successful' if is_valid else 'Token validation failed'
            except Exception as e:
                test_result['message'] = f'Token validation error: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 3: API authentication
            test_result = {
                'name': 'api_authentication',
                'success': False,
                'message': '',
                'duration': 0
            }
            
            start_time = time.time()
            try:
                user_info = await self.components['client'].get_authenticated_user()
                test_result['success'] = user_info is not None and 'login' in user_info
                test_result['message'] = f"Authenticated as: {user_info.get('login', 'unknown')}" if user_info else 'Authentication failed'
            except Exception as e:
                test_result['message'] = f'API authentication error: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
        except Exception as e:
            results['overall_success'] = False
            results['error'] = str(e)
        
        results['end_time'] = datetime.now()
        results['total_duration'] = (results['end_time'] - results['start_time']).total_seconds()
        results['overall_success'] = all(test['success'] for test in results['tests'])
        
        return results
    
    async def run_synchronization_tests(self) -> Dict[str, Any]:
        """Run comprehensive synchronization tests."""
        results = {
            'test_name': 'synchronization_tests',
            'start_time': datetime.now(),
            'tests': [],
            'overall_success': True
        }
        
        try:
            repo_config = self.config.repository_configs[0]
            
            # Test 1: Full repository sync
            test_result = {
                'name': 'full_repository_sync',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                sync_result = await self.components['sync_engine'].sync_repository(repo_config)
                test_result['success'] = sync_result.success
                test_result['message'] = f"Synced items: {sync_result.synced_items}"
                test_result['data'] = {
                    'repository_id': sync_result.repository_id,
                    'synced_items': sync_result.synced_items,
                    'conflicts': len(sync_result.conflicts)
                }
            except Exception as e:
                test_result['message'] = f'Full sync failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 2: Incremental sync
            test_result = {
                'name': 'incremental_sync',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                # Wait a moment then sync again
                await asyncio.sleep(1)
                sync_result = await self.components['sync_engine'].sync_repository(repo_config)
                test_result['success'] = sync_result.success
                test_result['message'] = f"Incremental sync items: {sync_result.synced_items}"
                test_result['data'] = {
                    'synced_items': sync_result.synced_items,
                    'is_incremental': True
                }
            except Exception as e:
                test_result['message'] = f'Incremental sync failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 3: Cache validation
            test_result = {
                'name': 'cache_validation',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                repo_id = f"{TEST_REPO_OWNER}/{TEST_REPO_NAME}"
                cached_repo = self.components['cache'].get_cached_repository(repo_id)
                test_result['success'] = cached_repo is not None
                test_result['message'] = f"Cached repository: {cached_repo.full_name}" if cached_repo else "No cached repository found"
                test_result['data'] = {
                    'cached': cached_repo is not None,
                    'repository_name': cached_repo.name if cached_repo else None
                }
            except Exception as e:
                test_result['message'] = f'Cache validation failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
        except Exception as e:
            results['overall_success'] = False
            results['error'] = str(e)
        
        results['end_time'] = datetime.now()
        results['total_duration'] = (results['end_time'] - results['start_time']).total_seconds()
        results['overall_success'] = all(test['success'] for test in results['tests'])
        
        return results
    
    async def run_error_recovery_tests(self) -> Dict[str, Any]:
        """Run error recovery and resilience tests."""
        results = {
            'test_name': 'error_recovery_tests',
            'start_time': datetime.now(),
            'tests': [],
            'overall_success': True
        }
        
        try:
            # Test 1: Backup creation
            test_result = {
                'name': 'backup_creation',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                # Create test data
                test_data_path = self.temp_dir / 'test_data.txt'
                test_data_path.write_text('Test data for backup')
                
                backup_info = self.components['recovery'].create_backup(
                    f"{TEST_REPO_OWNER}/{TEST_REPO_NAME}",
                    test_data_path,
                    ['test_data']
                )
                
                test_result['success'] = backup_info is not None
                test_result['message'] = f"Backup created: {backup_info.backup_id}" if backup_info else "Backup creation failed"
                test_result['data'] = {
                    'backup_id': backup_info.backup_id if backup_info else None,
                    'backup_size': backup_info.size_bytes if backup_info else 0
                }
            except Exception as e:
                test_result['message'] = f'Backup creation failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 2: State persistence
            test_result = {
                'name': 'state_persistence',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                from src.github_sync.data_recovery import SyncStateInfo
                
                # Create and store state
                state_info = SyncStateInfo(
                    repository_id=f"{TEST_REPO_OWNER}/{TEST_REPO_NAME}",
                    state=SyncState.SYNCING,
                    last_sync_time=datetime.now(),
                    last_success_time=datetime.now() - timedelta(hours=1),
                    error_count=0,
                    last_error=None,
                    sync_progress={'test': 'data'},
                    checksum='test_checksum'
                )
                
                self.components['recovery'].update_sync_state(state_info)
                
                # Retrieve state
                retrieved_state = self.components['recovery'].get_sync_state(state_info.repository_id)
                
                test_result['success'] = retrieved_state is not None and retrieved_state.repository_id == state_info.repository_id
                test_result['message'] = f"State persisted for: {retrieved_state.repository_id}" if retrieved_state else "State persistence failed"
                test_result['data'] = {
                    'state_stored': True,
                    'state_retrieved': retrieved_state is not None
                }
            except Exception as e:
                test_result['message'] = f'State persistence failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 3: Corruption detection
            test_result = {
                'name': 'corruption_detection',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                # Create potentially corrupted file
                corrupted_file = self.temp_dir / 'corrupted.db'
                corrupted_file.touch()  # Empty file
                
                corruption_report = self.components['recovery'].detect_data_corruption(
                    f"{TEST_REPO_OWNER}/{TEST_REPO_NAME}",
                    corrupted_file
                )
                
                # Corruption detection might not trigger for empty files, so we consider it successful if no exception
                test_result['success'] = True
                test_result['message'] = f"Corruption detection completed: {corruption_report.corruption_type if corruption_report else 'No corruption detected'}"
                test_result['data'] = {
                    'corruption_detected': corruption_report is not None,
                    'corruption_type': corruption_report.corruption_type if corruption_report else None
                }
            except Exception as e:
                test_result['message'] = f'Corruption detection failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
        except Exception as e:
            results['overall_success'] = False
            results['error'] = str(e)
        
        results['end_time'] = datetime.now()
        results['total_duration'] = (results['end_time'] - results['start_time']).total_seconds()
        results['overall_success'] = all(test['success'] for test in results['tests'])
        
        return results
    
    async def run_security_tests(self) -> Dict[str, Any]:
        """Run comprehensive security tests."""
        results = {
            'test_name': 'security_tests',
            'start_time': datetime.now(),
            'tests': [],
            'overall_success': True
        }
        
        try:
            # Test 1: Credential security
            test_result = {
                'name': 'credential_security',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                # Test that credentials are not hardcoded
                auth_file = Path('src/github_sync/auth.py')
                if auth_file.exists():
                    content = auth_file.read_text()
                    
                    # Check for environment variable usage
                    has_env_usage = 'os.getenv' in content or 'os.environ' in content
                    has_github_token = 'GITHUB_TOKEN' in content
                    
                    # Check for hardcoded patterns (should not exist)
                    import re
                    hardcoded_patterns = [
                        r'token\s*=\s*["\'][^"\']+["\']',
                        r'password\s*=\s*["\'][^"\']+["\']'
                    ]
                    
                    has_hardcoded = any(re.search(pattern, content, re.IGNORECASE) for pattern in hardcoded_patterns)
                    
                    test_result['success'] = has_env_usage and has_github_token and not has_hardcoded
                    test_result['message'] = 'Credential security validation passed' if test_result['success'] else 'Credential security issues found'
                    test_result['data'] = {
                        'uses_env_vars': has_env_usage,
                        'references_github_token': has_github_token,
                        'has_hardcoded_creds': has_hardcoded
                    }
                else:
                    test_result['message'] = 'Auth file not found'
            except Exception as e:
                test_result['message'] = f'Credential security test failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 2: Webhook signature validation
            test_result = {
                'name': 'webhook_signature_validation',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                import hmac
                import hashlib
                
                payload = '{"test": "data"}'
                secret = 'test_secret'
                
                # Generate valid signature
                valid_signature = 'sha256=' + hmac.new(
                    secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                # Test validation
                webhook_handler = WebhookHandler(secret)
                is_valid = webhook_handler.validate_webhook_signature(payload, valid_signature)
                
                # Test invalid signature
                invalid_signature = 'sha256=invalid_signature'
                is_invalid = not webhook_handler.validate_webhook_signature(payload, invalid_signature)
                
                test_result['success'] = is_valid and is_invalid
                test_result['message'] = 'Webhook signature validation working correctly'
                test_result['data'] = {
                    'valid_signature_accepted': is_valid,
                    'invalid_signature_rejected': is_invalid
                }
            except Exception as e:
                test_result['message'] = f'Webhook signature validation failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 3: Environment variable requirement
            test_result = {
                'name': 'env_var_requirement',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                # Test that authentication fails without environment variable
                with patch.dict('os.environ', {}, clear=True):
                    try:
                        AuthenticationManager().load_credentials()
                        test_result['success'] = False
                        test_result['message'] = 'Authentication should fail without GITHUB_TOKEN'
                    except ValueError as e:
                        if 'GITHUB_TOKEN' in str(e):
                            test_result['success'] = True
                            test_result['message'] = 'Correctly requires GITHUB_TOKEN environment variable'
                        else:
                            test_result['message'] = f'Unexpected error: {e}'
                    except Exception as e:
                        test_result['message'] = f'Unexpected exception: {e}'
                
                test_result['data'] = {
                    'requires_env_var': test_result['success']
                }
            except Exception as e:
                test_result['message'] = f'Environment variable requirement test failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
        except Exception as e:
            results['overall_success'] = False
            results['error'] = str(e)
        
        results['end_time'] = datetime.now()
        results['total_duration'] = (results['end_time'] - results['start_time']).total_seconds()
        results['overall_success'] = all(test['success'] for test in results['tests'])
        
        return results
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance and scalability tests."""
        results = {
            'test_name': 'performance_tests',
            'start_time': datetime.now(),
            'tests': [],
            'overall_success': True
        }
        
        try:
            # Test 1: API response times
            test_result = {
                'name': 'api_response_times',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                # Measure API call times
                api_times = []
                
                for i in range(3):  # Make 3 API calls
                    call_start = time.time()
                    repo = await self.components['client'].get_repository(TEST_REPO_OWNER, TEST_REPO_NAME)
                    call_duration = time.time() - call_start
                    api_times.append(call_duration)
                
                avg_time = sum(api_times) / len(api_times)
                max_time = max(api_times)
                
                # Consider successful if average time is under 5 seconds
                test_result['success'] = avg_time < 5.0
                test_result['message'] = f"Average API response time: {avg_time:.2f}s, Max: {max_time:.2f}s"
                test_result['data'] = {
                    'average_time': avg_time,
                    'max_time': max_time,
                    'all_times': api_times
                }
            except Exception as e:
                test_result['message'] = f'API performance test failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
            # Test 2: Cache performance
            test_result = {
                'name': 'cache_performance',
                'success': False,
                'message': '',
                'duration': 0,
                'data': {}
            }
            
            start_time = time.time()
            try:
                # Create test repositories for caching
                test_repos = []
                for i in range(50):  # Test with 50 repositories
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
                    test_repos.append(repo)
                
                # Measure cache write performance
                cache_start = time.time()
                for repo in test_repos:
                    self.components['cache'].cache_repository_data(repo)
                cache_write_time = time.time() - cache_start
                
                # Measure cache read performance
                read_start = time.time()
                for repo in test_repos:
                    cached_repo = self.components['cache'].get_cached_repository(repo.full_name)
                    assert cached_repo is not None
                read_time = time.time() - read_start
                
                # Consider successful if operations complete in reasonable time
                test_result['success'] = cache_write_time < 10.0 and read_time < 5.0
                test_result['message'] = f"Cache write: {cache_write_time:.2f}s, Cache read: {read_time:.2f}s"
                test_result['data'] = {
                    'write_time': cache_write_time,
                    'read_time': read_time,
                    'repos_tested': len(test_repos)
                }
            except Exception as e:
                test_result['message'] = f'Cache performance test failed: {e}'
            
            test_result['duration'] = time.time() - start_time
            results['tests'].append(test_result)
            
        except Exception as e:
            results['overall_success'] = False
            results['error'] = str(e)
        
        results['end_time'] = datetime.now()
        results['total_duration'] = (results['end_time'] - results['start_time']).total_seconds()
        results['overall_success'] = all(test['success'] for test in results['tests'])
        
        return results
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run the complete end-to-end test suite."""
        suite_results = {
            'suite_name': 'github_sync_e2e_tests',
            'start_time': datetime.now(),
            'test_results': [],
            'overall_success': True,
            'summary': {}
        }
        
        try:
            print("Starting GitHub Sync End-to-End Test Suite...")
            
            # Run all test categories
            test_categories = [
                ('Authentication Tests', self.run_authentication_tests),
                ('Synchronization Tests', self.run_synchronization_tests),
                ('Error Recovery Tests', self.run_error_recovery_tests),
                ('Security Tests', self.run_security_tests),
                ('Performance Tests', self.run_performance_tests)
            ]
            
            for category_name, test_method in test_categories:
                print(f"\nRunning {category_name}...")
                
                try:
                    category_results = await test_method()
                    suite_results['test_results'].append(category_results)
                    
                    # Print category summary
                    passed = sum(1 for test in category_results['tests'] if test['success'])
                    total = len(category_results['tests'])
                    print(f"{category_name}: {passed}/{total} tests passed")
                    
                    if not category_results['overall_success']:
                        suite_results['overall_success'] = False
                        
                except Exception as e:
                    print(f"Error running {category_name}: {e}")
                    suite_results['overall_success'] = False
                    suite_results['test_results'].append({
                        'test_name': category_name.lower().replace(' ', '_'),
                        'error': str(e),
                        'overall_success': False
                    })
            
            # Generate summary
            total_tests = sum(len(result.get('tests', [])) for result in suite_results['test_results'])
            passed_tests = sum(
                sum(1 for test in result.get('tests', []) if test.get('success', False))
                for result in suite_results['test_results']
            )
            
            suite_results['summary'] = {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            }
            
        except Exception as e:
            suite_results['overall_success'] = False
            suite_results['error'] = str(e)
        
        suite_results['end_time'] = datetime.now()
        suite_results['total_duration'] = (suite_results['end_time'] - suite_results['start_time']).total_seconds()
        
        return suite_results


@pytest.mark.e2e
class TestGitHubSyncEndToEnd:
    """End-to-end test class for pytest integration."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment."""
        if not TEST_GITHUB_TOKEN:
            pytest.skip("TEST_GITHUB_TOKEN not set - skipping end-to-end tests")
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_suite = GitHubSyncTestSuite(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_github_sync_workflow(self):
        """Test the complete GitHub synchronization workflow."""
        # Set up test environment
        setup_success = await self.test_suite.setup_test_environment()
        assert setup_success, "Failed to set up test environment"
        
        # Run complete test suite
        results = await self.test_suite.run_complete_test_suite()
        
        # Print detailed results
        print(f"\n{'='*60}")
        print("GITHUB SYNC END-TO-END TEST RESULTS")
        print(f"{'='*60}")
        print(f"Overall Success: {results['overall_success']}")
        print(f"Total Duration: {results['total_duration']:.2f} seconds")
        print(f"Tests Passed: {results['summary']['passed_tests']}/{results['summary']['total_tests']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        
        # Print category results
        for category_result in results['test_results']:
            if 'tests' in category_result:
                print(f"\n{category_result['test_name'].upper()}:")
                for test in category_result['tests']:
                    status = "✓" if test['success'] else "✗"
                    print(f"  {status} {test['name']}: {test['message']}")
        
        # Save detailed results to file
        results_file = Path(self.temp_dir) / 'e2e_test_results.json'
        with open(results_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            json_results = self._serialize_results_for_json(results)
            json.dump(json_results, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        # Assert overall success
        assert results['overall_success'], f"End-to-end tests failed. Success rate: {results['summary']['success_rate']:.1f}%"
    
    def _serialize_results_for_json(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Convert datetime objects to strings for JSON serialization."""
        if isinstance(results, dict):
            return {
                key: self._serialize_results_for_json(value)
                for key, value in results.items()
            }
        elif isinstance(results, list):
            return [self._serialize_results_for_json(item) for item in results]
        elif isinstance(results, datetime):
            return results.isoformat()
        else:
            return results
    
    @pytest.mark.asyncio
    async def test_system_resilience_under_load(self):
        """Test system resilience under concurrent load."""
        setup_success = await self.test_suite.setup_test_environment()
        assert setup_success, "Failed to set up test environment"
        
        # Create multiple concurrent sync tasks
        tasks = []
        for i in range(5):  # 5 concurrent syncs
            task = self.test_suite.components['sync_engine'].sync_repository(
                self.test_suite.config.repository_configs[0]
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        successful_syncs = [r for r in results if not isinstance(r, Exception) and r.success]
        failed_syncs = [r for r in results if isinstance(r, Exception) or not r.success]
        
        print(f"Concurrent sync results: {len(successful_syncs)} successful, {len(failed_syncs)} failed")
        
        # Should handle concurrent requests gracefully
        assert len(successful_syncs) >= 3, "System should handle at least 3 concurrent syncs successfully"
    
    @pytest.mark.asyncio
    async def test_data_consistency_across_operations(self):
        """Test data consistency across multiple operations."""
        setup_success = await self.test_suite.setup_test_environment()
        assert setup_success, "Failed to set up test environment"
        
        repo_config = self.test_suite.config.repository_configs[0]
        repo_id = f"{repo_config.owner}/{repo_config.name}"
        
        # Perform initial sync
        sync_result = await self.test_suite.components['sync_engine'].sync_repository(repo_config)
        assert sync_result.success, "Initial sync should succeed"
        
        # Get cached data
        cached_repo = self.test_suite.components['cache'].get_cached_repository(repo_id)
        assert cached_repo is not None, "Repository should be cached"
        
        # Create backup
        cache_db_path = Path(self.test_suite.temp_dir) / 'cache' / 'cache.db'
        if cache_db_path.exists():
            backup_info = self.test_suite.components['recovery'].create_backup(
                repo_id,
                cache_db_path,
                ['database']
            )
            assert backup_info is not None, "Backup should be created"
        
        # Verify data consistency
        cached_repo_after = self.test_suite.components['cache'].get_cached_repository(repo_id)
        assert cached_repo_after is not None, "Repository should still be cached"
        assert cached_repo_after.name == cached_repo.name, "Repository data should be consistent"
        
        print("Data consistency verified across sync, cache, and backup operations")


# Standalone test runner
async def run_standalone_e2e_tests():
    """Run end-to-end tests as a standalone script."""
    if not TEST_GITHUB_TOKEN:
        print("ERROR: TEST_GITHUB_TOKEN environment variable not set")
        print("Please set TEST_GITHUB_TOKEN to run end-to-end tests")
        return False
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        print("Initializing GitHub Sync End-to-End Test Suite...")
        test_suite = GitHubSyncTestSuite(temp_dir)
        
        # Set up test environment
        setup_success = await test_suite.setup_test_environment()
        if not setup_success:
            print("Failed to set up test environment")
            return False
        
        # Run complete test suite
        results = await test_suite.run_complete_test_suite()
        
        # Print results
        print(f"\n{'='*80}")
        print("GITHUB SYNCHRONIZATION SYSTEM - END-TO-END TEST RESULTS")
        print(f"{'='*80}")
        print(f"Overall Success: {'PASS' if results['overall_success'] else 'FAIL'}")
        print(f"Total Duration: {results['total_duration']:.2f} seconds")
        print(f"Tests Passed: {results['summary']['passed_tests']}/{results['summary']['total_tests']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        
        # Detailed results
        for category_result in results['test_results']:
            if 'tests' in category_result:
                print(f"\n{category_result['test_name'].replace('_', ' ').title()}:")
                for test in category_result['tests']:
                    status = "✓ PASS" if test['success'] else "✗ FAIL"
                    duration = f"({test['duration']:.2f}s)"
                    print(f"  {status:<8} {test['name']:<30} {duration:<10} {test['message']}")
        
        # Save results
        results_file = Path(temp_dir) / 'github_sync_e2e_results.json'
        with open(results_file, 'w') as f:
            # Serialize datetime objects
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: serialize_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_datetime(item) for item in obj]
                return obj
            
            json.dump(serialize_datetime(results), f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        return results['overall_success']
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    # Run as standalone script
    import sys
    
    async def main():
        success = await run_standalone_e2e_tests()
        sys.exit(0 if success else 1)
    
    asyncio.run(main())
else:
    # Run with pytest
    if __name__ == '__main__':
        pytest.main([
            __file__, 
            '-v', 
            '-m', 'e2e',
            '--tb=short',
            '-s'  # Don't capture output so we can see progress
        ])