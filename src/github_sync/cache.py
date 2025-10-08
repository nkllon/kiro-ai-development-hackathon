"""
Local cache and data persistence for GitHub synchronization.

This module provides efficient local storage and offline access to GitHub data
with intelligent caching strategies using SQLite backend.
"""

import sqlite3
import json
import logging
import os
import time
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import asdict
from threading import Lock
import hashlib

from .models import Repository, Issue, PullRequest, Commit, SyncResult
from .config import SyncConfig

logger = logging.getLogger(__name__)


class CacheError(Exception):
    """Base exception for cache operations."""
    pass


class CacheManager:
    """
    Local cache manager with SQLite backend for GitHub data.
    
    Provides efficient local storage, offline access, and intelligent
    caching strategies with LRU eviction and cache optimization.
    """
    
    def __init__(self, cache_dir: Optional[str] = None, 
                 max_cache_size_mb: int = 500,
                 retention_days: int = 30):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory for cache files (defaults to ~/.github_sync_cache)
            max_cache_size_mb: Maximum cache size in MB
            retention_days: Number of days to retain cached data
        """
        self.cache_dir = Path(cache_dir or Path.home() / ".github_sync_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / "github_cache.db"
        self.max_cache_size = max_cache_size_mb * 1024 * 1024  # Convert to bytes
        self.retention_days = retention_days
        
        # Thread safety
        self.lock = Lock()
        
        # Initialize database
        self._init_database()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'evictions': 0
        }
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Create repositories table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS repositories (
                        id INTEGER PRIMARY KEY,
                        full_name TEXT UNIQUE NOT NULL,
                        owner TEXT NOT NULL,
                        name TEXT NOT NULL,
                        data TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create issues table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS issues (
                        id INTEGER PRIMARY KEY,
                        repository_id INTEGER NOT NULL,
                        issue_number INTEGER NOT NULL,
                        data TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (repository_id) REFERENCES repositories (id),
                        UNIQUE(repository_id, issue_number)
                    )
                """)
                
                # Create pull_requests table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS pull_requests (
                        id INTEGER PRIMARY KEY,
                        repository_id INTEGER NOT NULL,
                        pr_number INTEGER NOT NULL,
                        data TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (repository_id) REFERENCES repositories (id),
                        UNIQUE(repository_id, pr_number)
                    )
                """)
                
                # Create commits table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS commits (
                        id INTEGER PRIMARY KEY,
                        repository_id INTEGER NOT NULL,
                        sha TEXT NOT NULL,
                        branch TEXT NOT NULL,
                        data TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (repository_id) REFERENCES repositories (id),
                        UNIQUE(repository_id, sha)
                    )
                """)
                
                # Create cache_metadata table for tracking cache statistics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_repos_full_name ON repositories(full_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_issues_repo_number ON issues(repository_id, issue_number)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_prs_repo_number ON pull_requests(repository_id, pr_number)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_commits_repo_sha ON commits(repository_id, sha)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_commits_branch ON commits(repository_id, branch)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON repositories(last_accessed)")
                
                conn.commit()
                logger.info(f"Cache database initialized at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise CacheError(f"Database initialization failed: {e}")
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity verification."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _get_repository_id(self, full_name: str) -> Optional[int]:
        """Get repository ID from cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id FROM repositories WHERE full_name = ?",
                    (full_name,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get repository ID for {full_name}: {e}")
            return None 
   
    def cache_repository_data(self, repo: Repository) -> bool:
        """
        Cache repository data.
        
        Args:
            repo: Repository object to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        with self.lock:
            try:
                repo_data = asdict(repo)
                checksum = self._calculate_checksum(repo_data)
                
                with sqlite3.connect(self.db_path) as conn:
                    # Insert or update repository
                    conn.execute("""
                        INSERT OR REPLACE INTO repositories 
                        (id, full_name, owner, name, data, checksum, updated_at, last_accessed)
                        VALUES (
                            (SELECT id FROM repositories WHERE full_name = ?),
                            ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """, (repo.full_name, repo.full_name, repo.owner, repo.name, 
                         json.dumps(repo_data, default=str), checksum))
                    
                    conn.commit()
                    self.stats['writes'] += 1
                    
                logger.debug(f"Cached repository data for {repo.full_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cache repository {repo.full_name}: {e}")
                return False
    
    def get_cached_repository(self, full_name: str) -> Optional[Repository]:
        """
        Get cached repository data.
        
        Args:
            full_name: Repository full name (owner/name)
            
        Returns:
            Repository object if found, None otherwise
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Update last accessed time
                    conn.execute(
                        "UPDATE repositories SET last_accessed = CURRENT_TIMESTAMP WHERE full_name = ?",
                        (full_name,)
                    )
                    
                    cursor = conn.execute(
                        "SELECT data, checksum FROM repositories WHERE full_name = ?",
                        (full_name,)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        data_json, stored_checksum = result
                        repo_data = json.loads(data_json)
                        
                        # Verify data integrity
                        calculated_checksum = self._calculate_checksum(repo_data)
                        if calculated_checksum != stored_checksum:
                            logger.warning(f"Checksum mismatch for repository {full_name}")
                            return None
                        
                        # Convert datetime strings back to datetime objects
                        if repo_data.get('created_at'):
                            repo_data['created_at'] = datetime.fromisoformat(repo_data['created_at'])
                        if repo_data.get('updated_at'):
                            repo_data['updated_at'] = datetime.fromisoformat(repo_data['updated_at'])
                        if repo_data.get('last_sync'):
                            repo_data['last_sync'] = datetime.fromisoformat(repo_data['last_sync'])
                        
                        self.stats['hits'] += 1
                        return Repository(**repo_data)
                    else:
                        self.stats['misses'] += 1
                        return None
                        
            except Exception as e:
                logger.error(f"Failed to get cached repository {full_name}: {e}")
                self.stats['misses'] += 1
                return None
    
    def cache_issues(self, repo_full_name: str, issues: List[Issue]) -> bool:
        """
        Cache issues for a repository.
        
        Args:
            repo_full_name: Repository full name
            issues: List of Issue objects to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        with self.lock:
            try:
                repo_id = self._get_repository_id(repo_full_name)
                if not repo_id:
                    logger.error(f"Repository {repo_full_name} not found in cache")
                    return False
                
                with sqlite3.connect(self.db_path) as conn:
                    for issue in issues:
                        issue_data = asdict(issue)
                        checksum = self._calculate_checksum(issue_data)
                        
                        conn.execute("""
                            INSERT OR REPLACE INTO issues 
                            (repository_id, issue_number, data, checksum, updated_at, last_accessed)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (repo_id, issue.number, json.dumps(issue_data, default=str), checksum))
                    
                    conn.commit()
                    self.stats['writes'] += len(issues)
                    
                logger.debug(f"Cached {len(issues)} issues for {repo_full_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cache issues for {repo_full_name}: {e}")
                return False    
    
    def get_cached_issues(self, repo_full_name: str, state: Optional[str] = None) -> List[Issue]:
        """
        Get cached issues for a repository.
        
        Args:
            repo_full_name: Repository full name
            state: Optional issue state filter
            
        Returns:
            List of Issue objects
        """
        with self.lock:
            try:
                repo_id = self._get_repository_id(repo_full_name)
                if not repo_id:
                    return []
                
                with sqlite3.connect(self.db_path) as conn:
                    # Update last accessed time
                    conn.execute(
                        "UPDATE issues SET last_accessed = CURRENT_TIMESTAMP WHERE repository_id = ?",
                        (repo_id,)
                    )
                    
                    cursor = conn.execute(
                        "SELECT data, checksum FROM issues WHERE repository_id = ? ORDER BY issue_number",
                        (repo_id,)
                    )
                    
                    issues = []
                    for data_json, stored_checksum in cursor.fetchall():
                        issue_data = json.loads(data_json)
                        
                        # Verify data integrity
                        calculated_checksum = self._calculate_checksum(issue_data)
                        if calculated_checksum != stored_checksum:
                            logger.warning(f"Checksum mismatch for issue in {repo_full_name}")
                            continue
                        
                        # Convert datetime strings back to datetime objects
                        for date_field in ['created_at', 'updated_at', 'closed_at']:
                            if issue_data.get(date_field):
                                issue_data[date_field] = datetime.fromisoformat(issue_data[date_field])
                        
                        # Convert state string to enum
                        if 'state' in issue_data:
                            from .models import IssueState
                            issue_data['state'] = IssueState(issue_data['state'])
                        
                        issue = Issue(**issue_data)
                        
                        # Apply state filter if specified
                        if state is None or issue.state.value == state:
                            issues.append(issue)
                    
                    self.stats['hits'] += len(issues) if issues else 0
                    if not issues:
                        self.stats['misses'] += 1
                    
                    return issues
                    
            except Exception as e:
                logger.error(f"Failed to get cached issues for {repo_full_name}: {e}")
                self.stats['misses'] += 1
                return []
    
    def cache_pull_requests(self, repo_full_name: str, pull_requests: List[PullRequest]) -> bool:
        """
        Cache pull requests for a repository.
        
        Args:
            repo_full_name: Repository full name
            pull_requests: List of PullRequest objects to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        with self.lock:
            try:
                repo_id = self._get_repository_id(repo_full_name)
                if not repo_id:
                    logger.error(f"Repository {repo_full_name} not found in cache")
                    return False
                
                with sqlite3.connect(self.db_path) as conn:
                    for pr in pull_requests:
                        pr_data = asdict(pr)
                        checksum = self._calculate_checksum(pr_data)
                        
                        conn.execute("""
                            INSERT OR REPLACE INTO pull_requests 
                            (repository_id, pr_number, data, checksum, updated_at, last_accessed)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (repo_id, pr.number, json.dumps(pr_data, default=str), checksum))
                    
                    conn.commit()
                    self.stats['writes'] += len(pull_requests)
                    
                logger.debug(f"Cached {len(pull_requests)} pull requests for {repo_full_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cache pull requests for {repo_full_name}: {e}")
                return False
    
    def get_cached_pull_requests(self, repo_full_name: str, state: Optional[str] = None) -> List[PullRequest]:
        """
        Get cached pull requests for a repository.
        
        Args:
            repo_full_name: Repository full name
            state: Optional PR state filter
            
        Returns:
            List of PullRequest objects
        """
        with self.lock:
            try:
                repo_id = self._get_repository_id(repo_full_name)
                if not repo_id:
                    return []
                
                with sqlite3.connect(self.db_path) as conn:
                    # Update last accessed time
                    conn.execute(
                        "UPDATE pull_requests SET last_accessed = CURRENT_TIMESTAMP WHERE repository_id = ?",
                        (repo_id,)
                    )
                    
                    cursor = conn.execute(
                        "SELECT data, checksum FROM pull_requests WHERE repository_id = ? ORDER BY pr_number",
                        (repo_id,)
                    )
                    
                    pull_requests = []
                    for data_json, stored_checksum in cursor.fetchall():
                        pr_data = json.loads(data_json)
                        
                        # Verify data integrity
                        calculated_checksum = self._calculate_checksum(pr_data)
                        if calculated_checksum != stored_checksum:
                            logger.warning(f"Checksum mismatch for PR in {repo_full_name}")
                            continue
                        
                        # Convert datetime strings back to datetime objects
                        for date_field in ['created_at', 'updated_at', 'merged_at', 'closed_at']:
                            if pr_data.get(date_field):
                                pr_data[date_field] = datetime.fromisoformat(pr_data[date_field])
                        
                        # Convert state string to enum
                        if 'state' in pr_data:
                            from .models import PullRequestState
                            pr_data['state'] = PullRequestState(pr_data['state'])
                        
                        pr = PullRequest(**pr_data)
                        
                        # Apply state filter if specified
                        if state is None or pr.state.value == state:
                            pull_requests.append(pr)
                    
                    self.stats['hits'] += len(pull_requests) if pull_requests else 0
                    if not pull_requests:
                        self.stats['misses'] += 1
                    
                    return pull_requests
                    
            except Exception as e:
                logger.error(f"Failed to get cached pull requests for {repo_full_name}: {e}")
                self.stats['misses'] += 1
                return []  
  
    def cache_commits(self, repo_full_name: str, commits: List[Commit]) -> bool:
        """
        Cache commits for a repository.
        
        Args:
            repo_full_name: Repository full name
            commits: List of Commit objects to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        with self.lock:
            try:
                repo_id = self._get_repository_id(repo_full_name)
                if not repo_id:
                    logger.error(f"Repository {repo_full_name} not found in cache")
                    return False
                
                with sqlite3.connect(self.db_path) as conn:
                    for commit in commits:
                        commit_data = asdict(commit)
                        checksum = self._calculate_checksum(commit_data)
                        
                        conn.execute("""
                            INSERT OR REPLACE INTO commits 
                            (repository_id, sha, branch, data, checksum, updated_at, last_accessed)
                            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (repo_id, commit.sha, commit.branch, 
                             json.dumps(commit_data, default=str), checksum))
                    
                    conn.commit()
                    self.stats['writes'] += len(commits)
                    
                logger.debug(f"Cached {len(commits)} commits for {repo_full_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cache commits for {repo_full_name}: {e}")
                return False
    
    def get_cached_commits(self, repo_full_name: str, branch: Optional[str] = None, 
                          limit: Optional[int] = None) -> List[Commit]:
        """
        Get cached commits for a repository.
        
        Args:
            repo_full_name: Repository full name
            branch: Optional branch filter
            limit: Optional limit on number of commits
            
        Returns:
            List of Commit objects
        """
        with self.lock:
            try:
                repo_id = self._get_repository_id(repo_full_name)
                if not repo_id:
                    return []
                
                with sqlite3.connect(self.db_path) as conn:
                    # Build query based on filters
                    query = "SELECT data, checksum FROM commits WHERE repository_id = ?"
                    params = [repo_id]
                    
                    if branch:
                        query += " AND branch = ?"
                        params.append(branch)
                    
                    query += " ORDER BY updated_at DESC"
                    
                    if limit:
                        query += " LIMIT ?"
                        params.append(limit)
                    
                    # Update last accessed time
                    update_query = "UPDATE commits SET last_accessed = CURRENT_TIMESTAMP WHERE repository_id = ?"
                    update_params = [repo_id]
                    if branch:
                        update_query += " AND branch = ?"
                        update_params.append(branch)
                    
                    conn.execute(update_query, update_params)
                    
                    cursor = conn.execute(query, params)
                    
                    commits = []
                    for data_json, stored_checksum in cursor.fetchall():
                        commit_data = json.loads(data_json)
                        
                        # Verify data integrity
                        calculated_checksum = self._calculate_checksum(commit_data)
                        if calculated_checksum != stored_checksum:
                            logger.warning(f"Checksum mismatch for commit in {repo_full_name}")
                            continue
                        
                        # Convert datetime strings back to datetime objects
                        if commit_data.get('committed_at'):
                            commit_data['committed_at'] = datetime.fromisoformat(commit_data['committed_at'])
                        
                        commits.append(Commit(**commit_data))
                    
                    self.stats['hits'] += len(commits) if commits else 0
                    if not commits:
                        self.stats['misses'] += 1
                    
                    return commits
                    
            except Exception as e:
                logger.error(f"Failed to get cached commits for {repo_full_name}: {e}")
                self.stats['misses'] += 1
                return []
    
    def invalidate_cache(self, repo_full_name: str, data_type: Optional[str] = None) -> bool:
        """
        Invalidate cache for a repository or specific data type.
        
        Args:
            repo_full_name: Repository full name
            data_type: Optional data type to invalidate ('issues', 'pull_requests', 'commits')
                      If None, invalidates all data for the repository
            
        Returns:
            True if invalidated successfully, False otherwise
        """
        with self.lock:
            try:
                repo_id = self._get_repository_id(repo_full_name)
                if not repo_id:
                    return False
                
                with sqlite3.connect(self.db_path) as conn:
                    if data_type is None:
                        # Invalidate all data for repository
                        conn.execute("DELETE FROM issues WHERE repository_id = ?", (repo_id,))
                        conn.execute("DELETE FROM pull_requests WHERE repository_id = ?", (repo_id,))
                        conn.execute("DELETE FROM commits WHERE repository_id = ?", (repo_id,))
                        conn.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
                        logger.info(f"Invalidated all cache data for {repo_full_name}")
                    elif data_type == 'issues':
                        conn.execute("DELETE FROM issues WHERE repository_id = ?", (repo_id,))
                        logger.info(f"Invalidated issues cache for {repo_full_name}")
                    elif data_type == 'pull_requests':
                        conn.execute("DELETE FROM pull_requests WHERE repository_id = ?", (repo_id,))
                        logger.info(f"Invalidated pull requests cache for {repo_full_name}")
                    elif data_type == 'commits':
                        conn.execute("DELETE FROM commits WHERE repository_id = ?", (repo_id,))
                        logger.info(f"Invalidated commits cache for {repo_full_name}")
                    else:
                        logger.warning(f"Unknown data type for invalidation: {data_type}")
                        return False
                    
                    conn.commit()
                    return True
                    
            except Exception as e:
                logger.error(f"Failed to invalidate cache for {repo_full_name}: {e}")
                return False    

    def optimize_cache_storage(self) -> Dict[str, Any]:
        """
        Optimize cache storage by cleaning up old data and managing size.
        
        Returns:
            Dictionary with optimization results
        """
        with self.lock:
            try:
                optimization_result = {
                    'cleaned_repositories': 0,
                    'cleaned_issues': 0,
                    'cleaned_pull_requests': 0,
                    'cleaned_commits': 0,
                    'space_freed_mb': 0,
                    'total_size_mb': 0
                }
                
                # Get current cache size
                initial_size = self.get_cache_size()
                optimization_result['initial_size_mb'] = initial_size / (1024 * 1024)
                
                with sqlite3.connect(self.db_path) as conn:
                    # Clean up old data based on retention policy
                    cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                    cutoff_str = cutoff_date.isoformat()
                    
                    # Clean old repositories
                    cursor = conn.execute(
                        "DELETE FROM repositories WHERE last_accessed < ? RETURNING id",
                        (cutoff_str,)
                    )
                    cleaned_repos = cursor.fetchall()
                    optimization_result['cleaned_repositories'] = len(cleaned_repos)
                    
                    # Clean old issues
                    cursor = conn.execute(
                        "DELETE FROM issues WHERE last_accessed < ?",
                        (cutoff_str,)
                    )
                    optimization_result['cleaned_issues'] = cursor.rowcount
                    
                    # Clean old pull requests
                    cursor = conn.execute(
                        "DELETE FROM pull_requests WHERE last_accessed < ?",
                        (cutoff_str,)
                    )
                    optimization_result['cleaned_pull_requests'] = cursor.rowcount
                    
                    # Clean old commits
                    cursor = conn.execute(
                        "DELETE FROM commits WHERE last_accessed < ?",
                        (cutoff_str,)
                    )
                    optimization_result['cleaned_commits'] = cursor.rowcount
                    
                    # If cache is still too large, perform LRU eviction
                    current_size = self.get_cache_size()
                    if current_size > self.max_cache_size:
                        evicted = self._perform_lru_eviction(conn, current_size - self.max_cache_size)
                        optimization_result.update(evicted)
                    
                    # Vacuum database to reclaim space
                    conn.execute("VACUUM")
                    conn.commit()
                
                # Calculate space freed
                final_size = self.get_cache_size()
                optimization_result['total_size_mb'] = final_size / (1024 * 1024)
                optimization_result['space_freed_mb'] = (initial_size - final_size) / (1024 * 1024)
                
                logger.info(f"Cache optimization completed: freed {optimization_result['space_freed_mb']:.2f} MB")
                return optimization_result
                
            except Exception as e:
                logger.error(f"Cache optimization failed: {e}")
                return {'error': str(e)}
    
    def _perform_lru_eviction(self, conn: sqlite3.Connection, target_size: int) -> Dict[str, int]:
        """
        Perform LRU eviction to free up the target amount of space.
        
        Args:
            conn: Database connection
            target_size: Target size to free in bytes
            
        Returns:
            Dictionary with eviction statistics
        """
        eviction_stats = {
            'evicted_repositories': 0,
            'evicted_issues': 0,
            'evicted_pull_requests': 0,
            'evicted_commits': 0
        }
        
        try:
            # Evict least recently accessed data
            # Start with commits (usually largest volume)
            cursor = conn.execute("""
                DELETE FROM commits WHERE id IN (
                    SELECT id FROM commits ORDER BY last_accessed ASC LIMIT ?
                )
            """, (target_size // 1000,))  # Rough estimate
            eviction_stats['evicted_commits'] = cursor.rowcount
            
            # Check if we need to evict more
            current_size = self.get_cache_size()
            if current_size > self.max_cache_size:
                # Evict old issues
                cursor = conn.execute("""
                    DELETE FROM issues WHERE id IN (
                        SELECT id FROM issues ORDER BY last_accessed ASC LIMIT 100
                    )
                """)
                eviction_stats['evicted_issues'] = cursor.rowcount
                
                # Evict old pull requests
                cursor = conn.execute("""
                    DELETE FROM pull_requests WHERE id IN (
                        SELECT id FROM pull_requests ORDER BY last_accessed ASC LIMIT 50
                    )
                """)
                eviction_stats['evicted_pull_requests'] = cursor.rowcount
            
            self.stats['evictions'] += sum(eviction_stats.values())
            
        except Exception as e:
            logger.error(f"LRU eviction failed: {e}")
        
        return eviction_stats
    
    def get_cache_size(self) -> int:
        """
        Get current cache size in bytes.
        
        Returns:
            Cache size in bytes
        """
        try:
            return os.path.getsize(self.db_path)
        except OSError:
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Get table counts
                    stats = dict(self.stats)
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM repositories")
                    stats['total_repositories'] = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM issues")
                    stats['total_issues'] = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM pull_requests")
                    stats['total_pull_requests'] = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM commits")
                    stats['total_commits'] = cursor.fetchone()[0]
                    
                    # Calculate hit rate
                    total_requests = stats['hits'] + stats['misses']
                    stats['hit_rate'] = (stats['hits'] / total_requests * 100) if total_requests > 0 else 0
                    
                    # Cache size
                    stats['cache_size_mb'] = self.get_cache_size() / (1024 * 1024)
                    stats['max_cache_size_mb'] = self.max_cache_size / (1024 * 1024)
                    
                    return stats
                    
            except Exception as e:
                logger.error(f"Failed to get cache stats: {e}")
                return dict(self.stats)
    
    def clear_cache(self) -> bool:
        """
        Clear all cached data.
        
        Returns:
            True if cleared successfully, False otherwise
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM commits")
                    conn.execute("DELETE FROM pull_requests")
                    conn.execute("DELETE FROM issues")
                    conn.execute("DELETE FROM repositories")
                    conn.execute("DELETE FROM cache_metadata")
                    conn.execute("VACUUM")
                    conn.commit()
                
                # Reset statistics
                self.stats = {
                    'hits': 0,
                    'misses': 0,
                    'writes': 0,
                    'evictions': 0
                }
                
                logger.info("Cache cleared successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
                return False
    
    def close(self):
        """Close cache manager and clean up resources."""
        # Perform final optimization
        self.optimize_cache_storage()
        logger.info("Cache manager closed")


class CacheOptimizationResult:
    """Result of cache optimization operation."""
    
    def __init__(self, **kwargs):
        self.cleaned_repositories = kwargs.get('cleaned_repositories', 0)
        self.cleaned_issues = kwargs.get('cleaned_issues', 0)
        self.cleaned_pull_requests = kwargs.get('cleaned_pull_requests', 0)
        self.cleaned_commits = kwargs.get('cleaned_commits', 0)
        self.space_freed_mb = kwargs.get('space_freed_mb', 0)
        self.total_size_mb = kwargs.get('total_size_mb', 0)
        self.error = kwargs.get('error')
    
    def __str__(self):
        if self.error:
            return f"Cache optimization failed: {self.error}"
        
        return (f"Cache optimization: freed {self.space_freed_mb:.2f} MB, "
                f"cleaned {self.cleaned_repositories} repos, "
                f"{self.cleaned_issues} issues, "
                f"{self.cleaned_pull_requests} PRs, "
                f"{self.cleaned_commits} commits")