"""
Code review integration for GitHub synchronization.

This module provides functionality for integrating GitHub code reviews,
including review status, comments, and team member assignments.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from .models import PullRequest
from .client import GitHubAPIClient
from .auth import AuthenticationManager

logger = logging.getLogger(__name__)


@dataclass
class ReviewComment:
    """Represents a code review comment."""
    id: int
    body: str
    author: str
    author_avatar_url: str
    created_at: datetime
    updated_at: datetime
    path: Optional[str] = None
    line: Optional[int] = None
    commit_sha: Optional[str] = None
    in_reply_to_id: Optional[int] = None


@dataclass
class Review:
    """Represents a pull request review."""
    id: int
    state: str  # APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED
    body: Optional[str]
    author: str
    author_avatar_url: str
    submitted_at: datetime
    commit_sha: str
    comments: List[ReviewComment] = field(default_factory=list)


@dataclass
class ReviewSummary:
    """Summary of review status for a pull request."""
    total_reviews: int
    approved_count: int
    changes_requested_count: int
    commented_count: int
    dismissed_count: int
    latest_review_at: Optional[datetime] = None
    required_reviewers: List[str] = field(default_factory=list)
    requested_reviewers: List[str] = field(default_factory=list)
    
    @property
    def approval_status(self) -> str:
        """Get overall approval status."""
        if self.changes_requested_count > 0:
            return "CHANGES_REQUESTED"
        elif self.approved_count > 0:
            return "APPROVED"
        elif self.commented_count > 0:
            return "COMMENTED"
        else:
            return "PENDING"


class CodeReviewIntegration:
    """
    Handles GitHub code review integration.
    
    This class provides functionality for fetching review status,
    displaying comments, and enabling commenting from within the framework.
    """
    
    def __init__(self, api_client: GitHubAPIClient, auth_manager: AuthenticationManager):
        """
        Initialize code review integration.
        
        Args:
            api_client: GitHub API client
            auth_manager: Authentication manager
        """
        self.api_client = api_client
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
    
    async def get_pull_request_reviews(self, owner: str, repo: str, pr_number: int) -> List[Review]:
        """
        Get all reviews for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            List of reviews
        """
        try:
            reviews_data = await self.api_client.get_pull_request_reviews(owner, repo, pr_number)
            reviews = []
            
            for review_data in reviews_data:
                # Get review comments
                comments = await self.get_review_comments(owner, repo, pr_number, review_data['id'])
                
                review = Review(
                    id=review_data['id'],
                    state=review_data['state'],
                    body=review_data.get('body'),
                    author=review_data['user']['login'],
                    author_avatar_url=review_data['user']['avatar_url'],
                    submitted_at=datetime.fromisoformat(review_data['submitted_at'].replace('Z', '+00:00')),
                    commit_sha=review_data['commit_id'],
                    comments=comments
                )
                reviews.append(review)
            
            return reviews
            
        except Exception as e:
            self.logger.error(f"Failed to get PR reviews for {owner}/{repo}#{pr_number}: {e}")
            raise
    
    async def get_review_comments(self, owner: str, repo: str, pr_number: int, review_id: int) -> List[ReviewComment]:
        """
        Get comments for a specific review.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            review_id: Review ID
            
        Returns:
            List of review comments
        """
        try:
            comments_data = await self.api_client.get_review_comments(owner, repo, pr_number, review_id)
            comments = []
            
            for comment_data in comments_data:
                comment = ReviewComment(
                    id=comment_data['id'],
                    body=comment_data['body'],
                    author=comment_data['user']['login'],
                    author_avatar_url=comment_data['user']['avatar_url'],
                    created_at=datetime.fromisoformat(comment_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(comment_data['updated_at'].replace('Z', '+00:00')),
                    path=comment_data.get('path'),
                    line=comment_data.get('line'),
                    commit_sha=comment_data.get('commit_id'),
                    in_reply_to_id=comment_data.get('in_reply_to_id')
                )
                comments.append(comment)
            
            return comments
            
        except Exception as e:
            self.logger.error(f"Failed to get review comments for review {review_id}: {e}")
            raise
    
    async def get_review_summary(self, owner: str, repo: str, pr_number: int) -> ReviewSummary:
        """
        Get a summary of review status for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Review summary
        """
        try:
            reviews = await self.get_pull_request_reviews(owner, repo, pr_number)
            
            # Count reviews by state
            approved_count = sum(1 for r in reviews if r.state == 'APPROVED')
            changes_requested_count = sum(1 for r in reviews if r.state == 'CHANGES_REQUESTED')
            commented_count = sum(1 for r in reviews if r.state == 'COMMENTED')
            dismissed_count = sum(1 for r in reviews if r.state == 'DISMISSED')
            
            # Get latest review timestamp
            latest_review_at = None
            if reviews:
                latest_review_at = max(r.submitted_at for r in reviews)
            
            # Get requested reviewers
            pr_data = await self.api_client.get_pull_request(owner, repo, pr_number)
            requested_reviewers = [r['login'] for r in pr_data.get('requested_reviewers', [])]
            
            return ReviewSummary(
                total_reviews=len(reviews),
                approved_count=approved_count,
                changes_requested_count=changes_requested_count,
                commented_count=commented_count,
                dismissed_count=dismissed_count,
                latest_review_at=latest_review_at,
                requested_reviewers=requested_reviewers
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get review summary for {owner}/{repo}#{pr_number}: {e}")
            raise
    
    async def add_review_comment(self, owner: str, repo: str, pr_number: int, 
                               body: str, commit_sha: str, path: str, line: int) -> ReviewComment:
        """
        Add a review comment to a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            body: Comment body
            commit_sha: Commit SHA
            path: File path
            line: Line number
            
        Returns:
            Created review comment
        """
        try:
            comment_data = {
                'body': body,
                'commit_id': commit_sha,
                'path': path,
                'line': line
            }
            
            response = await self.api_client.create_review_comment(owner, repo, pr_number, comment_data)
            
            return ReviewComment(
                id=response['id'],
                body=response['body'],
                author=response['user']['login'],
                author_avatar_url=response['user']['avatar_url'],
                created_at=datetime.fromisoformat(response['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(response['updated_at'].replace('Z', '+00:00')),
                path=response.get('path'),
                line=response.get('line'),
                commit_sha=response.get('commit_id')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add review comment to {owner}/{repo}#{pr_number}: {e}")
            raise
    
    async def submit_review(self, owner: str, repo: str, pr_number: int, 
                          event: str, body: Optional[str] = None, 
                          comments: Optional[List[Dict[str, Any]]] = None) -> Review:
        """
        Submit a pull request review.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            event: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
            body: Review body
            comments: List of review comments
            
        Returns:
            Created review
        """
        try:
            review_data = {
                'event': event
            }
            
            if body:
                review_data['body'] = body
            
            if comments:
                review_data['comments'] = comments
            
            response = await self.api_client.create_review(owner, repo, pr_number, review_data)
            
            return Review(
                id=response['id'],
                state=response['state'],
                body=response.get('body'),
                author=response['user']['login'],
                author_avatar_url=response['user']['avatar_url'],
                submitted_at=datetime.fromisoformat(response['submitted_at'].replace('Z', '+00:00')),
                commit_sha=response['commit_id']
            )
            
        except Exception as e:
            self.logger.error(f"Failed to submit review for {owner}/{repo}#{pr_number}: {e}")
            raise
    
    async def get_assignees(self, owner: str, repo: str, pr_number: int) -> List[str]:
        """
        Get assignees for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            List of assignee usernames
        """
        try:
            pr_data = await self.api_client.get_pull_request(owner, repo, pr_number)
            return [assignee['login'] for assignee in pr_data.get('assignees', [])]
            
        except Exception as e:
            self.logger.error(f"Failed to get assignees for {owner}/{repo}#{pr_number}: {e}")
            raise
    
    async def assign_reviewers(self, owner: str, repo: str, pr_number: int, 
                             reviewers: List[str]) -> bool:
        """
        Assign reviewers to a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            reviewers: List of reviewer usernames
            
        Returns:
            True if successful
        """
        try:
            await self.api_client.request_reviewers(owner, repo, pr_number, reviewers)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign reviewers to {owner}/{repo}#{pr_number}: {e}")
            raise
    
    def format_review_status(self, summary: ReviewSummary) -> str:
        """
        Format review status for display.
        
        Args:
            summary: Review summary
            
        Returns:
            Formatted status string
        """
        status_emoji = {
            'APPROVED': '✅',
            'CHANGES_REQUESTED': '❌',
            'COMMENTED': '💬',
            'PENDING': '⏳'
        }
        
        emoji = status_emoji.get(summary.approval_status, '❓')
        status_text = summary.approval_status.replace('_', ' ').title()
        
        details = []
        if summary.approved_count > 0:
            details.append(f"{summary.approved_count} approved")
        if summary.changes_requested_count > 0:
            details.append(f"{summary.changes_requested_count} requested changes")
        if summary.commented_count > 0:
            details.append(f"{summary.commented_count} commented")
        
        detail_text = ", ".join(details) if details else "No reviews"
        
        return f"{emoji} {status_text} ({detail_text})"