"""
Intelligent caching strategies for GitHub synchronization.

This module provides advanced caching strategies including LRU eviction,
cache versioning, and partial cache invalidation for efficient updates.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from .cache import CacheManager
from .models import Repository, Issue, PullRequest, Commit

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategy types."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on usage patterns


class CachePriority(Enum):
    """Cache priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    priority: CachePriority
    ttl_seconds: Optional[int] = None
    version: int = 1
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired based on TTL."""
        if self.ttl_seconds is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()
    
    @property
    def idle_seconds(self) -> float:
        """Get idle time since last access in seconds."""
        return (datetime.now() - self.last_accessed).total_seconds()


class IntelligentCacheManager:
    """
    Intelligent cache manager with advanced caching strategies.
    
    Provides LRU eviction, cache versioning, partial invalidation,
    and adaptive caching based on usage patterns.
    """
    
    def __init__(self, cache_manager: CacheManager, 
                 strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        """
        Initialize intelligent cache manager.
        
        Args:
            cache_manager: Base cache manager
            strategy: Caching strategy to use
        """
        self.cache_manager = cache_manager
        self.strategy = strategy
        
        # Cache metadata for intelligent strategies
        self.access_patterns: Dict[str, List[datetime]] = {}
        self.priority_map: Dict[str, CachePriority] = {}
        self.version_map: Dict[str, int] = {}
        
        # Strategy-specific settings
        self.ttl_settings = {
            'repositories': 3600,  # 1 hour
            'issues': 1800,        # 30 minutes
            'pull_requests': 1800, # 30 minutes
            'commits': 7200        # 2 hours
        }
        
        # Adaptive learning parameters
        self.learning_window_hours = 24
        self.min_access_threshold = 3
    
    def get_cache_priority(self, data_type: str, repo_name: str) -> CachePriority:
        """
        Determine cache priority based on data type and usage patterns.
        
        Args:
            data_type: Type of data (repositories, issues, etc.)
            repo_name: Repository name
            
        Returns:
            Cache priority level
        """
        key = f"{data_type}:{repo_name}"
        
        # Check if we have a manually set priority
        if key in self.priority_map:
            return self.priority_map[key]
        
        # Determine priority based on access patterns
        access_history = self.access_patterns.get(key, [])
        recent_accesses = [
            access for access in access_history
            if (datetime.now() - access).total_seconds() < self.learning_window_hours * 3600
        ]
        
        if len(recent_accesses) >= self.min_access_threshold * 3:
            return CachePriority.CRITICAL
        elif len(recent_accesses) >= self.min_access_threshold * 2:
            return CachePriority.HIGH
        elif len(recent_accesses) >= self.min_access_threshold:
            return CachePriority.MEDIUM
        else:
            return CachePriority.LOW
    
    def record_access(self, data_type: str, repo_name: str):
        """
        Record access for adaptive learning.
        
        Args:
            data_type: Type of data accessed
            repo_name: Repository name
        """
        key = f"{data_type}:{repo_name}"
        
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        
        self.access_patterns[key].append(datetime.now())
        
        # Keep only recent access history
        cutoff_time = datetime.now() - timedelta(hours=self.learning_window_hours * 2)
        self.access_patterns[key] = [
            access for access in self.access_patterns[key]
            if access > cutoff_time
        ]
    
    def should_cache(self, data_type: str, repo_name: str, data_size: int) -> bool:
        """
        Determine if data should be cached based on intelligent strategies.
        
        Args:
            data_type: Type of data
            repo_name: Repository name
            data_size: Size of data in bytes
            
        Returns:
            True if data should be cached
        """
        priority = self.get_cache_priority(data_type, repo_name)
        
        # Always cache critical and high priority data
        if priority in [CachePriority.CRITICAL, CachePriority.HIGH]:
            return True
        
        # For medium priority, consider size
        if priority == CachePriority.MEDIUM:
            return data_size < 1024 * 1024  # Cache if less than 1MB
        
        # For low priority, be more selective
        if priority == CachePriority.LOW:
            return data_size < 100 * 1024  # Cache if less than 100KB
        
        return False
    
    def get_ttl(self, data_type: str, repo_name: str) -> int:
        """
        Get TTL for data based on type and usage patterns.
        
        Args:
            data_type: Type of data
            repo_name: Repository name
            
        Returns:
            TTL in seconds
        """
        base_ttl = self.ttl_settings.get(data_type, 3600)
        priority = self.get_cache_priority(data_type, repo_name)
        
        # Adjust TTL based on priority
        if priority == CachePriority.CRITICAL:
            return base_ttl * 4  # Keep longer
        elif priority == CachePriority.HIGH:
            return base_ttl * 2
        elif priority == CachePriority.MEDIUM:
            return base_ttl
        else:
            return base_ttl // 2  # Shorter TTL for low priority
    
    def cache_repository_intelligently(self, repo: Repository) -> bool:
        """
        Cache repository with intelligent strategies.
        
        Args:
            repo: Repository to cache
            
        Returns:
            True if cached successfully
        """
        # Record access for learning
        self.record_access('repositories', repo.full_name)
        
        # Check if we should cache this repository
        repo_size = len(str(repo.__dict__))  # Rough size estimate
        if not self.should_cache('repositories', repo.full_name, repo_size):
            logger.debug(f"Skipping cache for repository {repo.full_name} based on strategy")
            return False
        
        # Cache with version tracking
        version = self.version_map.get(f"repo:{repo.full_name}", 1)
        self.version_map[f"repo:{repo.full_name}"] = version + 1
        
        return self.cache_manager.cache_repository_data(repo)
    
    def cache_issues_intelligently(self, repo_name: str, issues: List[Issue]) -> bool:
        """
        Cache issues with intelligent strategies.
        
        Args:
            repo_name: Repository name
            issues: List of issues to cache
            
        Returns:
            True if cached successfully
        """
        # Record access for learning
        self.record_access('issues', repo_name)
        
        # Filter issues based on priority and recency
        filtered_issues = self._filter_issues_by_priority(issues)
        
        if not filtered_issues:
            logger.debug(f"No issues to cache for {repo_name} after filtering")
            return True
        
        # Cache with version tracking
        version = self.version_map.get(f"issues:{repo_name}", 1)
        self.version_map[f"issues:{repo_name}"] = version + 1
        
        return self.cache_manager.cache_issues(repo_name, filtered_issues)
    
    def _filter_issues_by_priority(self, issues: List[Issue]) -> List[Issue]:
        """Filter issues based on priority and recency."""
        if not issues:
            return issues
        
        # Sort by priority: open issues first, then by update time
        sorted_issues = sorted(issues, key=lambda x: (
            x.state.value != 'open',  # Open issues first
            -(x.updated_at.timestamp() if x.updated_at else 0)  # Most recent first
        ))
        
        # Limit based on strategy
        if self.strategy == CacheStrategy.ADAPTIVE:
            # Keep top 100 issues for adaptive strategy
            return sorted_issues[:100]
        elif self.strategy == CacheStrategy.LRU:
            # Keep top 50 issues for LRU
            return sorted_issues[:50]
        else:
            return sorted_issues
    
    def cache_pull_requests_intelligently(self, repo_name: str, prs: List[PullRequest]) -> bool:
        """
        Cache pull requests with intelligent strategies.
        
        Args:
            repo_name: Repository name
            prs: List of pull requests to cache
            
        Returns:
            True if cached successfully
        """
        # Record access for learning
        self.record_access('pull_requests', repo_name)
        
        # Filter PRs based on priority and recency
        filtered_prs = self._filter_prs_by_priority(prs)
        
        if not filtered_prs:
            logger.debug(f"No pull requests to cache for {repo_name} after filtering")
            return True
        
        # Cache with version tracking
        version = self.version_map.get(f"prs:{repo_name}", 1)
        self.version_map[f"prs:{repo_name}"] = version + 1
        
        return self.cache_manager.cache_pull_requests(repo_name, filtered_prs)
    
    def _filter_prs_by_priority(self, prs: List[PullRequest]) -> List[PullRequest]:
        """Filter pull requests based on priority and recency."""
        if not prs:
            return prs
        
        # Sort by priority: open PRs first, then by update time
        sorted_prs = sorted(prs, key=lambda x: (
            x.state.value not in ['open', 'merged'],  # Open and merged PRs first
            -(x.updated_at.timestamp() if x.updated_at else 0)  # Most recent first
        ))
        
        # Limit based on strategy
        if self.strategy == CacheStrategy.ADAPTIVE:
            return sorted_prs[:50]  # Keep top 50 PRs
        elif self.strategy == CacheStrategy.LRU:
            return sorted_prs[:25]  # Keep top 25 PRs
        else:
            return sorted_prs
    
    def partial_invalidate(self, repo_name: str, changed_items: Set[str]) -> bool:
        """
        Perform partial cache invalidation for efficient updates.
        
        Args:
            repo_name: Repository name
            changed_items: Set of changed item identifiers
            
        Returns:
            True if invalidation successful
        """
        try:
            # Determine what needs to be invalidated based on changed items
            invalidate_issues = any(item.startswith('issue:') for item in changed_items)
            invalidate_prs = any(item.startswith('pr:') for item in changed_items)
            invalidate_commits = any(item.startswith('commit:') for item in changed_items)
            
            success = True
            
            if invalidate_issues:
                success &= self.cache_manager.invalidate_cache(repo_name, 'issues')
                logger.debug(f"Partially invalidated issues cache for {repo_name}")
            
            if invalidate_prs:
                success &= self.cache_manager.invalidate_cache(repo_name, 'pull_requests')
                logger.debug(f"Partially invalidated pull requests cache for {repo_name}")
            
            if invalidate_commits:
                success &= self.cache_manager.invalidate_cache(repo_name, 'commits')
                logger.debug(f"Partially invalidated commits cache for {repo_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Partial invalidation failed for {repo_name}: {e}")
            return False
    
    def migrate_cache_version(self, from_version: int, to_version: int) -> bool:
        """
        Migrate cache data between versions.
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            True if migration successful
        """
        try:
            logger.info(f"Migrating cache from version {from_version} to {to_version}")
            
            # For now, simple migration strategy is to clear cache
            # In a real implementation, this would handle data transformation
            if to_version > from_version:
                self.cache_manager.clear_cache()
                logger.info("Cache cleared for version migration")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Cache migration failed: {e}")
            return False
    
    def get_cache_efficiency_metrics(self) -> Dict[str, Any]:
        """
        Get cache efficiency metrics for monitoring.
        
        Returns:
            Dictionary with efficiency metrics
        """
        base_stats = self.cache_manager.get_cache_stats()
        
        # Calculate additional intelligent metrics
        total_repositories = len(self.access_patterns)
        active_repositories = len([
            key for key, accesses in self.access_patterns.items()
            if any((datetime.now() - access).total_seconds() < 3600 for access in accesses)
        ])
        
        efficiency_metrics = {
            'base_stats': base_stats,
            'strategy': self.strategy.value,
            'total_tracked_repositories': total_repositories,
            'active_repositories_last_hour': active_repositories,
            'cache_versions': len(self.version_map),
            'priority_distribution': self._get_priority_distribution(),
            'adaptive_learning_effectiveness': self._calculate_learning_effectiveness()
        }
        
        return efficiency_metrics
    
    def _get_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of cache priorities."""
        distribution = {priority.name: 0 for priority in CachePriority}
        
        for key in self.access_patterns.keys():
            data_type, repo_name = key.split(':', 1)
            priority = self.get_cache_priority(data_type, repo_name)
            distribution[priority.name] += 1
        
        return distribution
    
    def _calculate_learning_effectiveness(self) -> float:
        """Calculate effectiveness of adaptive learning."""
        if not self.access_patterns:
            return 0.0
        
        # Simple effectiveness metric based on prediction accuracy
        # In a real implementation, this would track prediction vs actual access patterns
        total_patterns = len(self.access_patterns)
        patterns_with_recent_access = len([
            key for key, accesses in self.access_patterns.items()
            if len(accesses) > 0
        ])
        
        return (patterns_with_recent_access / total_patterns * 100) if total_patterns > 0 else 0.0
    
    def optimize_with_strategy(self) -> Dict[str, Any]:
        """
        Optimize cache using the configured strategy.
        
        Returns:
            Optimization results
        """
        if self.strategy == CacheStrategy.ADAPTIVE:
            return self._optimize_adaptive()
        elif self.strategy == CacheStrategy.LRU:
            return self._optimize_lru()
        elif self.strategy == CacheStrategy.TTL:
            return self._optimize_ttl()
        else:
            return self.cache_manager.optimize_cache_storage()
    
    def _optimize_adaptive(self) -> Dict[str, Any]:
        """Optimize cache using adaptive strategy."""
        # Update priorities based on recent access patterns
        updated_priorities = 0
        
        for key, accesses in self.access_patterns.items():
            old_priority = self.priority_map.get(key, CachePriority.LOW)
            data_type, repo_name = key.split(':', 1)
            new_priority = self.get_cache_priority(data_type, repo_name)
            
            if old_priority != new_priority:
                self.priority_map[key] = new_priority
                updated_priorities += 1
        
        # Perform base optimization
        base_result = self.cache_manager.optimize_cache_storage()
        base_result['updated_priorities'] = updated_priorities
        base_result['strategy'] = 'adaptive'
        
        return base_result
    
    def _optimize_lru(self) -> Dict[str, Any]:
        """Optimize cache using LRU strategy."""
        # Base optimization handles LRU eviction
        result = self.cache_manager.optimize_cache_storage()
        result['strategy'] = 'lru'
        return result
    
    def _optimize_ttl(self) -> Dict[str, Any]:
        """Optimize cache using TTL strategy."""
        # TTL-based cleanup is handled in base optimization
        result = self.cache_manager.optimize_cache_storage()
        result['strategy'] = 'ttl'
        return result