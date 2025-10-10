"""
GitHub API client with rate limiting and error handling.

This module provides a unified interface for all GitHub API interactions
with built-in rate limiting, error handling, and authentication.
"""

import time
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from threading import Lock
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import Repository, Issue, PullRequest, Commit, IssueState, PullRequestState
from .auth import AuthenticationManager, AuthenticationError

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    pass


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""
    def __init__(self, message: str, reset_time: int):
        super().__init__(message)
        self.reset_time = reset_time


class CircuitBreakerError(GitHubAPIError):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for network failures.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        self.lock = Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self.lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half-open"
                else:
                    raise CircuitBreakerError("Circuit breaker is open")
            
            try:
                result = func(*args, **kwargs)
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                
                raise e


class RequestQueue:
    """
    Priority-based request queue for managing API calls.
    """
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.active_requests = 0
        self.lock = Lock()
    
    def acquire(self):
        """Acquire a request slot."""
        with self.lock:
            while self.active_requests >= self.max_concurrent:
                time.sleep(0.1)
            self.active_requests += 1
    
    def release(self):
        """Release a request slot."""
        with self.lock:
            self.active_requests = max(0, self.active_requests - 1)


class GitHubAPIClient:
    """
    GitHub API client with comprehensive error handling and rate limiting.
    
    This client provides a unified interface for all GitHub API interactions
    while handling authentication, rate limiting, and error recovery automatically.
    """
    
    def __init__(self, auth_manager: Optional[AuthenticationManager] = None, 
                 max_concurrent_requests: int = 5):
        """
        Initialize the GitHub API client.
        
        Args:
            auth_manager: Optional authentication manager. If None, creates a new one.
            max_concurrent_requests: Maximum number of concurrent requests
        """
        self.auth_manager = auth_manager or AuthenticationManager()
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        # Initialize rate limiting components
        self.circuit_breaker = CircuitBreaker()
        self.request_queue = RequestQueue(max_concurrent_requests)
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=2.0,  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH", "PUT"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default timeout
        self.timeout = 30
        
        # Rate limiting state
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum time between requests (100ms)
        
    def authenticate(self) -> bool:
        """
        Authenticate with GitHub API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.auth_manager.load_credentials()
            return self.auth_manager.validate_token()
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, priority: int = 1, **kwargs) -> requests.Response:
        """
        Make an authenticated request to the GitHub API with rate limiting and circuit breaker.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            priority: Request priority (higher numbers = higher priority)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            GitHubAPIError: For API errors
            RateLimitError: When rate limited
            AuthenticationError: For auth issues
            CircuitBreakerError: When circuit breaker is open
        """
        def make_request_internal():
            if not self.authenticate():
                raise AuthenticationError("Failed to authenticate with GitHub")
            
            # Acquire request slot from queue
            self.request_queue.acquire()
            
            try:
                # Implement minimum request interval
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.min_request_interval:
                    time.sleep(self.min_request_interval - time_since_last)
                
                self.last_request_time = time.time()
                
                url = f"{self.base_url}/{endpoint.lstrip('/')}"
                headers = self.auth_manager.get_authenticated_headers()
                
                # Add any additional headers
                if 'headers' in kwargs:
                    headers.update(kwargs.pop('headers'))
                
                # Set timeout if not provided
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = self.timeout
                
                # Make the request
                response = self.session.request(method, url, headers=headers, **kwargs)
                
                # Check for rate limiting
                if response.status_code == 429:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 3600))
                    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                    
                    logger.warning(f"Rate limit exceeded. Remaining: {remaining}, Reset at: {reset_time}")
                    raise RateLimitError(
                        f"Rate limit exceeded. Reset at {reset_time}",
                        reset_time
                    )
                
                # Check for other errors
                if response.status_code >= 400:
                    error_msg = f"GitHub API error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise GitHubAPIError(error_msg)
                
                # Log rate limit status for monitoring
                remaining = response.headers.get('X-RateLimit-Remaining')
                if remaining and int(remaining) < 100:
                    logger.warning(f"Rate limit running low: {remaining} requests remaining")
                
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                raise GitHubAPIError(f"Request failed: {e}")
            finally:
                self.request_queue.release()
        
        # Use circuit breaker to protect against cascading failures
        try:
            return self.circuit_breaker.call(make_request_internal)
        except CircuitBreakerError:
            logger.error("Circuit breaker is open - too many recent failures")
            raise
    
    def _handle_rate_limit(self, reset_time: int, max_wait: int = 3600) -> None:
        """
        Handle rate limiting by waiting for reset with exponential backoff.
        
        Args:
            reset_time: Unix timestamp when rate limit resets
            max_wait: Maximum time to wait in seconds
        """
        current_time = int(time.time())
        wait_time = reset_time - current_time
        
        if wait_time > max_wait:
            raise RateLimitError(f"Rate limit wait time ({wait_time}s) exceeds maximum ({max_wait}s)", reset_time)
        
        if wait_time > 0:
            logger.info(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time + 1)  # Add 1 second buffer
    
    def _exponential_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> None:
        """
        Implement exponential backoff for retries.
        
        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = min(base_delay * (2 ** attempt), max_delay)
        jitter = delay * 0.1 * (0.5 - time.time() % 1)  # Add jitter to avoid thundering herd
        actual_delay = delay + jitter
        
        logger.info(f"Backing off for {actual_delay:.2f} seconds (attempt {attempt + 1})")
        time.sleep(actual_delay)
    
    def _make_request_with_retry(self, method: str, endpoint: str, max_retries: int = 3, **kwargs) -> requests.Response:
        """
        Make a request with exponential backoff retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            max_retries: Maximum number of retries
            **kwargs: Additional request arguments
            
        Returns:
            Response object
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return self._make_request(method, endpoint, **kwargs)
            except RateLimitError as e:
                # Handle rate limiting specially
                if attempt < max_retries:
                    self._handle_rate_limit(e.reset_time)
                    continue
                else:
                    raise
            except (GitHubAPIError, requests.exceptions.RequestException) as e:
                last_exception = e
                if attempt < max_retries:
                    self._exponential_backoff(attempt)
                    continue
                else:
                    break
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise GitHubAPIError("All retry attempts failed")
    
    def get_repository(self, owner: str, repo: str) -> Repository:
        """
        Get repository information from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository object with GitHub data
            
        Raises:
            GitHubAPIError: If repository cannot be retrieved
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}")
            data = response.json()
            
            return Repository(
                id=data['id'],
                name=data['name'],
                owner=data['owner']['login'],
                full_name=data['full_name'],
                description=data.get('description'),
                default_branch=data.get('default_branch', 'main'),
                private=data.get('private', False),
                created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None,
                updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
                clone_url=data.get('clone_url'),
                ssh_url=data.get('ssh_url')
            )
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            # Retry after rate limit reset
            return self.get_repository(owner, repo)
        except Exception as e:
            logger.error(f"Failed to get repository {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to get repository: {e}")
    
    def list_issues(self, owner: str, repo: str, state: str = "all", per_page: int = 100) -> List[Issue]:
        """
        List issues for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state filter ("open", "closed", "all")
            per_page: Number of issues per page (max 100)
            
        Returns:
            List of Issue objects
            
        Raises:
            GitHubAPIError: If issues cannot be retrieved
        """
        issues = []
        page = 1
        
        try:
            while True:
                params = {
                    'state': state,
                    'per_page': min(per_page, 100),
                    'page': page
                }
                
                response = self._make_request("GET", f"repos/{owner}/{repo}/issues", params=params)
                data = response.json()
                
                if not data:
                    break
                
                for issue_data in data:
                    # Skip pull requests (they appear in issues endpoint)
                    if 'pull_request' in issue_data:
                        continue
                    
                    issue = Issue(
                        id=issue_data['id'],
                        number=issue_data['number'],
                        title=issue_data['title'],
                        body=issue_data.get('body'),
                        state=IssueState(issue_data['state']),
                        assignees=[assignee['login'] for assignee in issue_data.get('assignees', [])],
                        labels=[label['name'] for label in issue_data.get('labels', [])],
                        milestone=issue_data['milestone']['title'] if issue_data.get('milestone') else None,
                        created_at=datetime.fromisoformat(issue_data['created_at'].replace('Z', '+00:00')) if issue_data.get('created_at') else None,
                        updated_at=datetime.fromisoformat(issue_data['updated_at'].replace('Z', '+00:00')) if issue_data.get('updated_at') else None,
                        closed_at=datetime.fromisoformat(issue_data['closed_at'].replace('Z', '+00:00')) if issue_data.get('closed_at') else None,
                        author=issue_data['user']['login'] if issue_data.get('user') else None,
                        comments_count=issue_data.get('comments', 0)
                    )
                    issues.append(issue)
                
                # Check if there are more pages
                if len(data) < per_page:
                    break
                
                page += 1
            
            return issues
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            # Retry after rate limit reset
            return self.list_issues(owner, repo, state, per_page)
        except Exception as e:
            logger.error(f"Failed to list issues for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to list issues: {e}")
    
    def list_pull_requests(self, owner: str, repo: str, state: str = "all", per_page: int = 100) -> List[PullRequest]:
        """
        List pull requests for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state filter ("open", "closed", "all")
            per_page: Number of PRs per page (max 100)
            
        Returns:
            List of PullRequest objects
            
        Raises:
            GitHubAPIError: If pull requests cannot be retrieved
        """
        pull_requests = []
        page = 1
        
        try:
            while True:
                params = {
                    'state': state,
                    'per_page': min(per_page, 100),
                    'page': page
                }
                
                response = self._make_request("GET", f"repos/{owner}/{repo}/pulls", params=params)
                data = response.json()
                
                if not data:
                    break
                
                for pr_data in data:
                    # Determine PR state
                    pr_state = PullRequestState.OPEN
                    if pr_data.get('merged'):
                        pr_state = PullRequestState.MERGED
                    elif pr_data['state'] == 'closed':
                        pr_state = PullRequestState.CLOSED
                    
                    pr = PullRequest(
                        id=pr_data['id'],
                        number=pr_data['number'],
                        title=pr_data['title'],
                        body=pr_data.get('body'),
                        state=pr_state,
                        head_branch=pr_data['head']['ref'],
                        base_branch=pr_data['base']['ref'],
                        head_sha=pr_data['head']['sha'],
                        base_sha=pr_data['base']['sha'],
                        mergeable=pr_data.get('mergeable'),
                        merged=pr_data.get('merged', False),
                        draft=pr_data.get('draft', False),
                        created_at=datetime.fromisoformat(pr_data['created_at'].replace('Z', '+00:00')) if pr_data.get('created_at') else None,
                        updated_at=datetime.fromisoformat(pr_data['updated_at'].replace('Z', '+00:00')) if pr_data.get('updated_at') else None,
                        merged_at=datetime.fromisoformat(pr_data['merged_at'].replace('Z', '+00:00')) if pr_data.get('merged_at') else None,
                        closed_at=datetime.fromisoformat(pr_data['closed_at'].replace('Z', '+00:00')) if pr_data.get('closed_at') else None,
                        author=pr_data['user']['login'] if pr_data.get('user') else None,
                        assignees=[assignee['login'] for assignee in pr_data.get('assignees', [])],
                        labels=[label['name'] for label in pr_data.get('labels', [])]
                    )
                    pull_requests.append(pr)
                
                # Check if there are more pages
                if len(data) < per_page:
                    break
                
                page += 1
            
            return pull_requests
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            # Retry after rate limit reset
            return self.list_pull_requests(owner, repo, state, per_page)
        except Exception as e:
            logger.error(f"Failed to list pull requests for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to list pull requests: {e}")
    
    def get_commits(self, owner: str, repo: str, branch: str = "main", per_page: int = 100, 
                   since: Optional[str] = None, until: Optional[str] = None) -> List[Commit]:
        """
        Get commits for a repository branch with optional date filtering.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            per_page: Number of commits per page (max 100)
            since: Only commits after this date (ISO 8601 format)
            until: Only commits before this date (ISO 8601 format)
            
        Returns:
            List of Commit objects
            
        Raises:
            GitHubAPIError: If commits cannot be retrieved
        """
        commits = []
        page = 1
        
        try:
            while True:
                params = {
                    'sha': branch,
                    'per_page': min(per_page, 100),
                    'page': page
                }
                
                if since:
                    params['since'] = since
                if until:
                    params['until'] = until
                
                response = self._make_request("GET", f"repos/{owner}/{repo}/commits", params=params)
                data = response.json()
                
                if not data:
                    break
                
                for commit_data in data:
                    # Get additional commit details for file changes
                    stats = commit_data.get('stats', {})
                    files = commit_data.get('files', [])
                    
                    commit = Commit(
                        sha=commit_data['sha'],
                        message=commit_data['commit']['message'],
                        author=commit_data['commit']['author']['name'],
                        author_email=commit_data['commit']['author']['email'],
                        committed_at=datetime.fromisoformat(commit_data['commit']['author']['date'].replace('Z', '+00:00')) if commit_data['commit']['author'].get('date') else None,
                        branch=branch,
                        parents=[parent['sha'] for parent in commit_data.get('parents', [])],
                        files_changed=[f['filename'] for f in files] if files else [],
                        additions=stats.get('additions', 0),
                        deletions=stats.get('deletions', 0)
                    )
                    commits.append(commit)
                
                # Check if there are more pages
                if len(data) < per_page:
                    break
                
                page += 1
            
            return commits
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            # Retry after rate limit reset
            return self.get_commits(owner, repo, branch, per_page, since, until)
        except Exception as e:
            logger.error(f"Failed to get commits for {owner}/{repo}:{branch}: {e}")
            raise GitHubAPIError(f"Failed to get commits: {e}")
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        try:
            return self.auth_manager.check_rate_limit()
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            raise GitHubAPIError(f"Failed to get rate limit status: {e}")
    
    def create_issue(self, owner: str, repo: str, title: str, body: Optional[str] = None, 
                    assignees: Optional[List[str]] = None, labels: Optional[List[str]] = None) -> Issue:
        """
        Create a new issue in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            assignees: List of assignee usernames
            labels: List of label names
            
        Returns:
            Created Issue object
        """
        data = {
            'title': title,
            'body': body or '',
            'assignees': assignees or [],
            'labels': labels or []
        }
        
        try:
            response = self._make_request("POST", f"repos/{owner}/{repo}/issues", json=data)
            issue_data = response.json()
            
            return Issue(
                id=issue_data['id'],
                number=issue_data['number'],
                title=issue_data['title'],
                body=issue_data.get('body'),
                state=IssueState(issue_data['state']),
                assignees=[assignee['login'] for assignee in issue_data.get('assignees', [])],
                labels=[label['name'] for label in issue_data.get('labels', [])],
                created_at=datetime.fromisoformat(issue_data['created_at'].replace('Z', '+00:00')) if issue_data.get('created_at') else None,
                updated_at=datetime.fromisoformat(issue_data['updated_at'].replace('Z', '+00:00')) if issue_data.get('updated_at') else None,
                author=issue_data['user']['login'] if issue_data.get('user') else None,
                comments_count=issue_data.get('comments', 0)
            )
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            return self.create_issue(owner, repo, title, body, assignees, labels)
        except Exception as e:
            logger.error(f"Failed to create issue in {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to create issue: {e}")
    
    def update_issue(self, owner: str, repo: str, issue_number: int, 
                    title: Optional[str] = None, body: Optional[str] = None,
                    state: Optional[str] = None, assignees: Optional[List[str]] = None,
                    labels: Optional[List[str]] = None) -> Issue:
        """
        Update an existing issue.
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            title: New title (optional)
            body: New body (optional)
            state: New state ("open" or "closed", optional)
            assignees: New assignees list (optional)
            labels: New labels list (optional)
            
        Returns:
            Updated Issue object
        """
        data = {}
        if title is not None:
            data['title'] = title
        if body is not None:
            data['body'] = body
        if state is not None:
            data['state'] = state
        if assignees is not None:
            data['assignees'] = assignees
        if labels is not None:
            data['labels'] = labels
        
        try:
            response = self._make_request("PATCH", f"repos/{owner}/{repo}/issues/{issue_number}", json=data)
            issue_data = response.json()
            
            return Issue(
                id=issue_data['id'],
                number=issue_data['number'],
                title=issue_data['title'],
                body=issue_data.get('body'),
                state=IssueState(issue_data['state']),
                assignees=[assignee['login'] for assignee in issue_data.get('assignees', [])],
                labels=[label['name'] for label in issue_data.get('labels', [])],
                created_at=datetime.fromisoformat(issue_data['created_at'].replace('Z', '+00:00')) if issue_data.get('created_at') else None,
                updated_at=datetime.fromisoformat(issue_data['updated_at'].replace('Z', '+00:00')) if issue_data.get('updated_at') else None,
                closed_at=datetime.fromisoformat(issue_data['closed_at'].replace('Z', '+00:00')) if issue_data.get('closed_at') else None,
                author=issue_data['user']['login'] if issue_data.get('user') else None,
                comments_count=issue_data.get('comments', 0)
            )
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            return self.update_issue(owner, repo, issue_number, title, body, state, assignees, labels)
        except Exception as e:
            logger.error(f"Failed to update issue {issue_number} in {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to update issue: {e}")
    
    def list_branches(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        List all branches for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Number of branches per page (max 100)
            
        Returns:
            List of branch information dictionaries
            
        Raises:
            GitHubAPIError: If branches cannot be retrieved
        """
        branches = []
        page = 1
        
        try:
            while True:
                params = {
                    'per_page': min(per_page, 100),
                    'page': page
                }
                
                response = self._make_request("GET", f"repos/{owner}/{repo}/branches", params=params)
                data = response.json()
                
                if not data:
                    break
                
                for branch_data in data:
                    branch_info = {
                        'name': branch_data['name'],
                        'sha': branch_data['commit']['sha'],
                        'protected': branch_data.get('protected', False),
                        'commit_url': branch_data['commit']['url'],
                        'commit_message': branch_data['commit'].get('commit', {}).get('message', ''),
                        'commit_author': branch_data['commit'].get('commit', {}).get('author', {}).get('name', ''),
                        'commit_date': branch_data['commit'].get('commit', {}).get('author', {}).get('date', '')
                    }
                    branches.append(branch_info)
                
                # Check if there are more pages
                if len(data) < per_page:
                    break
                
                page += 1
            
            return branches
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            return self.list_branches(owner, repo, per_page)
        except Exception as e:
            logger.error(f"Failed to list branches for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to list branches: {e}")
    
    def get_branch(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific branch.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            Branch information dictionary
            
        Raises:
            GitHubAPIError: If branch cannot be retrieved
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/branches/{branch}")
            data = response.json()
            
            return {
                'name': data['name'],
                'sha': data['commit']['sha'],
                'protected': data.get('protected', False),
                'protection_url': data.get('protection_url'),
                'commit': {
                    'sha': data['commit']['sha'],
                    'url': data['commit']['url'],
                    'message': data['commit'].get('commit', {}).get('message', ''),
                    'author': data['commit'].get('commit', {}).get('author', {}),
                    'committer': data['commit'].get('commit', {}).get('committer', {}),
                    'tree': data['commit'].get('commit', {}).get('tree', {}),
                    'parents': data['commit'].get('parents', [])
                }
            }
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            return self.get_branch(owner, repo, branch)
        except Exception as e:
            logger.error(f"Failed to get branch {branch} for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to get branch: {e}")
    
    def get_commit_details(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific commit.
        
        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA
            
        Returns:
            Detailed commit information
            
        Raises:
            GitHubAPIError: If commit cannot be retrieved
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/commits/{sha}")
            data = response.json()
            
            return {
                'sha': data['sha'],
                'message': data['commit']['message'],
                'author': {
                    'name': data['commit']['author']['name'],
                    'email': data['commit']['author']['email'],
                    'date': data['commit']['author']['date']
                },
                'committer': {
                    'name': data['commit']['committer']['name'],
                    'email': data['commit']['committer']['email'],
                    'date': data['commit']['committer']['date']
                },
                'tree': data['commit']['tree'],
                'parents': [parent['sha'] for parent in data.get('parents', [])],
                'stats': data.get('stats', {}),
                'files': data.get('files', []),
                'html_url': data.get('html_url'),
                'comments_url': data.get('comments_url')
            }
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            return self.get_commit_details(owner, repo, sha)
        except Exception as e:
            logger.error(f"Failed to get commit {sha} for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to get commit details: {e}")
    
    def compare_commits(self, owner: str, repo: str, base: str, head: str) -> Dict[str, Any]:
        """
        Compare two commits or branches.
        
        Args:
            owner: Repository owner
            repo: Repository name
            base: Base commit/branch
            head: Head commit/branch
            
        Returns:
            Comparison information
            
        Raises:
            GitHubAPIError: If comparison cannot be performed
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/compare/{base}...{head}")
            data = response.json()
            
            return {
                'status': data.get('status'),
                'ahead_by': data.get('ahead_by', 0),
                'behind_by': data.get('behind_by', 0),
                'total_commits': data.get('total_commits', 0),
                'base_commit': data.get('base_commit', {}),
                'merge_base_commit': data.get('merge_base_commit', {}),
                'commits': data.get('commits', []),
                'files': data.get('files', []),
                'html_url': data.get('html_url'),
                'permalink_url': data.get('permalink_url')
            }
            
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            return self.compare_commits(owner, repo, base, head)
        except Exception as e:
            logger.error(f"Failed to compare {base}...{head} for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to compare commits: {e}")
    
    def get_merge_events(self, owner: str, repo: str, branch: str = "main", per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get merge events for a branch by analyzing commit history.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            per_page: Number of commits to analyze per page
            
        Returns:
            List of merge event information
            
        Raises:
            GitHubAPIError: If merge events cannot be retrieved
        """
        merge_events = []
        
        try:
            commits = self.get_commits(owner, repo, branch, per_page)
            
            for commit in commits:
                # Merge commits typically have multiple parents
                if len(commit.parents) > 1:
                    # Get detailed commit info to analyze merge
                    commit_details = self.get_commit_details(owner, repo, commit.sha)
                    
                    merge_event = {
                        'sha': commit.sha,
                        'message': commit.message,
                        'author': commit.author,
                        'committed_at': commit.committed_at,
                        'parents': commit.parents,
                        'merge_type': 'merge_commit',
                        'files_changed': len(commit_details.get('files', [])),
                        'additions': commit_details.get('stats', {}).get('additions', 0),
                        'deletions': commit_details.get('stats', {}).get('deletions', 0),
                        'total_changes': commit_details.get('stats', {}).get('total', 0)
                    }
                    
                    # Try to determine source branch from commit message
                    if 'merge pull request' in commit.message.lower():
                        merge_event['merge_type'] = 'pull_request_merge'
                        # Extract PR number if possible
                        import re
                        pr_match = re.search(r'#(\d+)', commit.message)
                        if pr_match:
                            merge_event['pull_request_number'] = int(pr_match.group(1))
                    
                    merge_events.append(merge_event)
            
            return merge_events
            
        except Exception as e:
            logger.error(f"Failed to get merge events for {owner}/{repo}:{branch}: {e}")
            raise GitHubAPIError(f"Failed to get merge events: {e}")
    
    def detect_conflicts(self, owner: str, repo: str, base_branch: str, head_branch: str) -> Dict[str, Any]:
        """
        Detect potential merge conflicts between branches.
        
        Args:
            owner: Repository owner
            repo: Repository name
            base_branch: Base branch name
            head_branch: Head branch name
            
        Returns:
            Conflict detection information
            
        Raises:
            GitHubAPIError: If conflict detection fails
        """
        try:
            # Compare the branches
            comparison = self.compare_commits(owner, repo, base_branch, head_branch)
            
            conflict_info = {
                'has_conflicts': False,
                'conflicting_files': [],
                'ahead_by': comparison['ahead_by'],
                'behind_by': comparison['behind_by'],
                'status': comparison['status'],
                'total_commits': comparison['total_commits']
            }
            
            # If branches have diverged, there might be conflicts
            if comparison['ahead_by'] > 0 and comparison['behind_by'] > 0:
                conflict_info['has_potential_conflicts'] = True
                
                # Analyze changed files for potential conflicts
                files_in_head = set()
                files_in_base = set()
                
                # Get files changed in head branch
                for commit in comparison.get('commits', []):
                    commit_details = self.get_commit_details(owner, repo, commit['sha'])
                    for file_info in commit_details.get('files', []):
                        files_in_head.add(file_info['filename'])
                
                # Get files changed in base branch (would need additional API calls)
                # For now, we'll mark files that appear in both as potential conflicts
                overlapping_files = files_in_head  # Simplified for now
                
                conflict_info['potentially_conflicting_files'] = list(overlapping_files)
                conflict_info['files_changed_in_head'] = len(files_in_head)
            else:
                conflict_info['has_potential_conflicts'] = False
            
            return conflict_info
            
        except Exception as e:
            logger.error(f"Failed to detect conflicts between {base_branch} and {head_branch} for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to detect conflicts: {e}")
    
    def get_branch_protection(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """
        Get branch protection settings.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            Branch protection information
            
        Raises:
            GitHubAPIError: If branch protection cannot be retrieved
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/branches/{branch}/protection")
            data = response.json()
            
            return {
                'enabled': True,
                'required_status_checks': data.get('required_status_checks'),
                'enforce_admins': data.get('enforce_admins', {}).get('enabled', False),
                'required_pull_request_reviews': data.get('required_pull_request_reviews'),
                'restrictions': data.get('restrictions'),
                'required_linear_history': data.get('required_linear_history', {}).get('enabled', False),
                'allow_force_pushes': data.get('allow_force_pushes', {}).get('enabled', False),
                'allow_deletions': data.get('allow_deletions', {}).get('enabled', False)
            }
            
        except GitHubAPIError as e:
            if "404" in str(e):
                # Branch protection not enabled
                return {'enabled': False}
            raise
        except RateLimitError as e:
            self._handle_rate_limit(e.reset_time)
            return self.get_branch_protection(owner, repo, branch)
        except Exception as e:
            logger.error(f"Failed to get branch protection for {branch} in {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to get branch protection: {e}")  
  
    # Review-related API methods
    
    async def get_pull_request_reviews(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get all reviews for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            List of review data dictionaries
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/pulls/{pr_number}/reviews")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get PR reviews for {owner}/{repo}#{pr_number}: {e}")
            raise GitHubAPIError(f"Failed to get PR reviews: {e}")
    
    async def get_review_comments(self, owner: str, repo: str, pr_number: int, review_id: int) -> List[Dict[str, Any]]:
        """
        Get comments for a specific review.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            review_id: Review ID
            
        Returns:
            List of review comment data dictionaries
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/pulls/{pr_number}/reviews/{review_id}/comments")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get review comments for review {review_id}: {e}")
            raise GitHubAPIError(f"Failed to get review comments: {e}")
    
    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get detailed information about a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Pull request data dictionary
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/pulls/{pr_number}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get PR {owner}/{repo}#{pr_number}: {e}")
            raise GitHubAPIError(f"Failed to get PR: {e}")
    
    async def create_review_comment(self, owner: str, repo: str, pr_number: int, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a review comment on a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            comment_data: Comment data dictionary
            
        Returns:
            Created comment data dictionary
        """
        try:
            response = self._make_request("POST", f"repos/{owner}/{repo}/pulls/{pr_number}/comments", json=comment_data)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create review comment on {owner}/{repo}#{pr_number}: {e}")
            raise GitHubAPIError(f"Failed to create review comment: {e}")
    
    async def create_review(self, owner: str, repo: str, pr_number: int, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a pull request review.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            review_data: Review data dictionary
            
        Returns:
            Created review data dictionary
        """
        try:
            response = self._make_request("POST", f"repos/{owner}/{repo}/pulls/{pr_number}/reviews", json=review_data)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create review on {owner}/{repo}#{pr_number}: {e}")
            raise GitHubAPIError(f"Failed to create review: {e}")
    
    async def request_reviewers(self, owner: str, repo: str, pr_number: int, reviewers: List[str]) -> Dict[str, Any]:
        """
        Request reviewers for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            reviewers: List of reviewer usernames
            
        Returns:
            Updated pull request data dictionary
        """
        try:
            data = {'reviewers': reviewers}
            response = self._make_request("POST", f"repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers", json=data)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to request reviewers for {owner}/{repo}#{pr_number}: {e}")
            raise GitHubAPIError(f"Failed to request reviewers: {e}")   
 
    # Project management API methods
    
    async def get_repository_projects(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        Get all project boards for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of project data dictionaries
        """
        try:
            response = self._make_request("GET", f"repos/{owner}/{repo}/projects", 
                                        headers={'Accept': 'application/vnd.github.inertia-preview+json'})
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get projects for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to get projects: {e}")
    
    async def get_project_columns(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get columns for a project board.
        
        Args:
            project_id: Project board ID
            
        Returns:
            List of column data dictionaries
        """
        try:
            response = self._make_request("GET", f"projects/{project_id}/columns",
                                        headers={'Accept': 'application/vnd.github.inertia-preview+json'})
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get columns for project {project_id}: {e}")
            raise GitHubAPIError(f"Failed to get project columns: {e}")
    
    async def get_column_cards(self, column_id: int) -> List[Dict[str, Any]]:
        """
        Get cards for a project column.
        
        Args:
            column_id: Project column ID
            
        Returns:
            List of card data dictionaries
        """
        try:
            response = self._make_request("GET", f"projects/columns/{column_id}/cards",
                                        headers={'Accept': 'application/vnd.github.inertia-preview+json'})
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get cards for column {column_id}: {e}")
            raise GitHubAPIError(f"Failed to get column cards: {e}")
    
    async def get_repository_milestones(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """
        Get milestones for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Milestone state filter ("open", "closed", "all")
            
        Returns:
            List of milestone data dictionaries
        """
        try:
            params = {'state': state}
            response = self._make_request("GET", f"repos/{owner}/{repo}/milestones", params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get milestones for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to get milestones: {e}")
    
    async def create_milestone(self, owner: str, repo: str, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new milestone.
        
        Args:
            owner: Repository owner
            repo: Repository name
            milestone_data: Milestone data dictionary
            
        Returns:
            Created milestone data dictionary
        """
        try:
            response = self._make_request("POST", f"repos/{owner}/{repo}/milestones", json=milestone_data)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create milestone in {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Failed to create milestone: {e}")
    
    async def get_notifications(self, all_notifications: bool = False, participating: bool = False) -> List[Dict[str, Any]]:
        """
        Get GitHub notifications for the authenticated user.
        
        Args:
            all_notifications: Include read notifications
            participating: Only notifications where user is participating
            
        Returns:
            List of notification data dictionaries
        """
        try:
            params = {}
            if all_notifications:
                params['all'] = 'true'
            if participating:
                params['participating'] = 'true'
            
            response = self._make_request("GET", "notifications", params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            raise GitHubAPIError(f"Failed to get notifications: {e}")
    
    async def mark_notification_as_read(self, notification_id: str) -> None:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
        """
        try:
            self._make_request("PATCH", f"notifications/threads/{notification_id}")
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as read: {e}")
            raise GitHubAPIError(f"Failed to mark notification as read: {e}")