"""
Unit tests for GitProvider interface and data models.

These tests validate the core interface definitions, data models,
and utility methods that all providers must implement.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.gitkraken_integration.providers.git_provider import (
    GitProvider,
    GitOperationResult,
    GitOperationStatus,
    BranchInfo,
    CommitInfo,
    FileStatus,
    MergeConflict
)


class TestGitOperationResult:
    """Test GitOperationResult data model"""
    
    def test_successful_result_creation(self):
        """Test creating a successful operation result"""
        result = GitOperationResult(
            success=True,
            status=GitOperationStatus.SUCCESS,
            message="Operation completed successfully",
            provider_used="test_provider",
            execution_time_ms=150
        )
        
        assert result.success is True
        assert result.status == GitOperationStatus.SUCCESS
        assert result.message == "Operation completed successfully"
        assert result.provider_used == "test_provider"
        assert result.execution_time_ms == 150
        assert result.suggestions == []
        assert result.data is None
        assert result.error_code is None
    
    def test_failed_result_creation(self):
        """Test creating a failed operation result"""
        result = GitOperationResult(
            success=False,
            status=GitOperationStatus.FAILURE,
            message="Operation failed",
            error_code="GIT_001",
            suggestions=["Check repository status", "Verify permissions"]
        )
        
        assert result.success is False
        assert result.status == GitOperationStatus.FAILURE
        assert result.error_code == "GIT_001"
        assert len(result.suggestions) == 2
    
    def test_status_success_consistency(self):
        """Test that status is corrected to match success flag"""
        # Success=True but status=FAILURE should be corrected
        result = GitOperationResult(
            success=True,
            status=GitOperationStatus.FAILURE,
            message="Test"
        )
        assert result.status == GitOperationStatus.SUCCESS
        
        # Success=False but status=SUCCESS should be corrected
        result = GitOperationResult(
            success=False,
            status=GitOperationStatus.SUCCESS,
            message="Test"
        )
        assert result.status == GitOperationStatus.FAILURE


class TestBranchInfo:
    """Test BranchInfo data model"""
    
    def test_branch_info_creation(self):
        """Test creating branch information"""
        commit_date = datetime.now()
        branch = BranchInfo(
            name="feature/test-branch",
            is_current=True,
            ahead_count=2,
            behind_count=0,
            last_commit_hash="abc123def456",
            last_commit_message="Add new feature",
            last_commit_date=commit_date,
            last_commit_author="Test Author",
            tracking_branch="origin/feature/test-branch",
            is_dirty=True,
            untracked_files=1,
            modified_files=2,
            staged_files=1
        )
        
        assert branch.name == "feature/test-branch"
        assert branch.is_current is True
        assert branch.ahead_count == 2
        assert branch.behind_count == 0
        assert branch.last_commit_hash == "abc123def456"
        assert branch.last_commit_message == "Add new feature"
        assert branch.last_commit_date == commit_date
        assert branch.last_commit_author == "Test Author"
        assert branch.tracking_branch == "origin/feature/test-branch"
        assert branch.is_dirty is True
        assert branch.untracked_files == 1
        assert branch.modified_files == 2
        assert branch.staged_files == 1


class TestCommitInfo:
    """Test CommitInfo data model"""
    
    def test_commit_info_creation(self):
        """Test creating commit information"""
        commit_date = datetime.now()
        author_date = datetime.now()
        
        commit = CommitInfo(
            hash="abc123def456789",
            short_hash="abc123d",
            message="feat: Add new feature\n\nDetailed description of the feature",
            author_name="Test Author",
            author_email="test@example.com",
            committer_name="Test Committer",
            committer_email="committer@example.com",
            commit_date=commit_date,
            author_date=author_date,
            parent_hashes=["parent123", "parent456"],
            changed_files=["file1.py", "file2.py"],
            insertions=50,
            deletions=10
        )
        
        assert commit.hash == "abc123def456789"
        assert commit.short_hash == "abc123d"
        assert "feat: Add new feature" in commit.message
        assert commit.author_name == "Test Author"
        assert commit.author_email == "test@example.com"
        assert len(commit.parent_hashes) == 2
        assert len(commit.changed_files) == 2
        assert commit.insertions == 50
        assert commit.deletions == 10


class TestFileStatus:
    """Test FileStatus data model"""
    
    def test_file_status_creation(self):
        """Test creating file status information"""
        file_status = FileStatus(
            path="src/test_file.py",
            status="M",
            staged=True,
            working_tree_status="M",
            index_status="M"
        )
        
        assert file_status.path == "src/test_file.py"
        assert file_status.status == "M"
        assert file_status.staged is True
        assert file_status.working_tree_status == "M"
        assert file_status.index_status == "M"


class TestMergeConflict:
    """Test MergeConflict data model"""
    
    def test_merge_conflict_creation(self):
        """Test creating merge conflict information"""
        conflict = MergeConflict(
            file_path="src/conflicted_file.py",
            conflict_type="content",
            our_version="our content",
            their_version="their content",
            base_version="base content",
            resolution_suggestions=["Use ours", "Use theirs", "Manual merge"]
        )
        
        assert conflict.file_path == "src/conflicted_file.py"
        assert conflict.conflict_type == "content"
        assert conflict.our_version == "our content"
        assert conflict.their_version == "their content"
        assert conflict.base_version == "base content"
        assert len(conflict.resolution_suggestions) == 3
    
    def test_merge_conflict_default_suggestions(self):
        """Test merge conflict with default empty suggestions"""
        conflict = MergeConflict(
            file_path="test.py",
            conflict_type="content"
        )
        
        assert conflict.resolution_suggestions == []


class TestGitProviderInterface:
    """Test GitProvider abstract interface"""
    
    def test_cannot_instantiate_abstract_provider(self):
        """Test that GitProvider cannot be instantiated directly"""
        with pytest.raises(TypeError):
            GitProvider()
    
    def test_branch_name_validation(self):
        """Test branch name validation utility method"""
        # Create a concrete implementation for testing
        class TestProvider(GitProvider):
            def get_status(self): pass
            def get_current_branch(self): pass
            def list_branches(self, include_remote=True): pass
            def create_branch(self, name, from_branch="HEAD"): pass
            def switch_branch(self, name, create_if_missing=False): pass
            def delete_branch(self, name, force=False): pass
            def merge_branch(self, source, target=None): pass
            def stage_files(self, files=None): pass
            def unstage_files(self, files=None): pass
            def commit_changes(self, message, files=None): pass
            def get_commit_history(self, branch=None, limit=50): pass
            def push_changes(self, branch=None, remote="origin"): pass
            def pull_changes(self, branch=None, remote="origin"): pass
            def fetch_changes(self, remote="origin"): pass
            def get_merge_conflicts(self): pass
            def resolve_conflict(self, file_path, resolution): pass
            def is_available(self): return True
            def get_provider_name(self): return "test"
            def get_provider_capabilities(self): return {}
            def get_health_status(self): pass
        
        provider = TestProvider()
        
        # Valid branch names
        assert provider.validate_branch_name("feature/test") is True
        assert provider.validate_branch_name("main") is True
        assert provider.validate_branch_name("develop") is True
        assert provider.validate_branch_name("feature-123") is True
        
        # Invalid branch names
        assert provider.validate_branch_name("") is False
        assert provider.validate_branch_name("feature with spaces") is False
        assert provider.validate_branch_name("feature~test") is False
        assert provider.validate_branch_name("feature^test") is False
        assert provider.validate_branch_name("feature:test") is False
        assert provider.validate_branch_name("feature?test") is False
        assert provider.validate_branch_name("feature*test") is False
        assert provider.validate_branch_name("feature[test") is False
        assert provider.validate_branch_name("feature\\test") is False
        assert provider.validate_branch_name("feature..test") is False
        assert provider.validate_branch_name(".feature") is False
        assert provider.validate_branch_name("feature.") is False
        assert provider.validate_branch_name("-feature") is False
        assert provider.validate_branch_name("feature/") is False
    
    def test_commit_message_formatting(self):
        """Test commit message formatting utility method"""
        # Create a concrete implementation for testing
        class TestProvider(GitProvider):
            def get_status(self): pass
            def get_current_branch(self): pass
            def list_branches(self, include_remote=True): pass
            def create_branch(self, name, from_branch="HEAD"): pass
            def switch_branch(self, name, create_if_missing=False): pass
            def delete_branch(self, name, force=False): pass
            def merge_branch(self, source, target=None): pass
            def stage_files(self, files=None): pass
            def unstage_files(self, files=None): pass
            def commit_changes(self, message, files=None): pass
            def get_commit_history(self, branch=None, limit=50): pass
            def push_changes(self, branch=None, remote="origin"): pass
            def pull_changes(self, branch=None, remote="origin"): pass
            def fetch_changes(self, remote="origin"): pass
            def get_merge_conflicts(self): pass
            def resolve_conflict(self, file_path, resolution): pass
            def is_available(self): return True
            def get_provider_name(self): return "test"
            def get_provider_capabilities(self): return {}
            def get_health_status(self): pass
        
        provider = TestProvider()
        
        # Test single line message
        result = provider.format_commit_message("Add new feature")
        assert result == "Add new feature"
        
        # Test long single line message (should be truncated)
        long_message = "A" * 80
        result = provider.format_commit_message(long_message)
        assert len(result) == 72
        
        # Test multi-line message
        multi_line = "Add new feature\nDetailed description"
        result = provider.format_commit_message(multi_line)
        lines = result.split('\n')
        assert lines[0] == "Add new feature"
        assert lines[1] == ""  # Blank line added
        assert lines[2] == "Detailed description"
        
        # Test multi-line message with existing blank line
        multi_line_blank = "Add new feature\n\nDetailed description"
        result = provider.format_commit_message(multi_line_blank)
        lines = result.split('\n')
        assert lines[0] == "Add new feature"
        assert lines[1] == ""
        assert lines[2] == "Detailed description"
        
        # Test empty message
        result = provider.format_commit_message("")
        assert result == ""
        
        # Test whitespace-only message
        result = provider.format_commit_message("   \n  \n  ")
        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__])