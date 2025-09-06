"""
Unit tests for enhanced branch management operations in StandardGitProvider.

These tests validate the advanced branch management functionality including
branch details, renaming, upstream tracking, and branch comparison.
"""

import pytest
import subprocess
from unittest.mock import Mock, patch
from datetime import datetime

from src.gitkraken_integration.providers.standard_git_provider import StandardGitProvider
from src.gitkraken_integration.providers.git_provider import GitOperationStatus


class TestBranchManagement:
    """Test enhanced branch management operations"""
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_branch_details_success(self, mock_exists, mock_run):
        """Test getting detailed branch information"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # get_branch_details mocks
            Mock(stdout="ref: refs/heads/feature-branch\n", returncode=0),  # show-ref
            Mock(stdout="abc123|abc123d|Add new feature|John Doe|john@example.com|2024-01-15 10:30:00 +0000\n", returncode=0),  # show
            Mock(stdout="origin\n", returncode=0),  # config remote
            Mock(stdout="refs/heads/feature-branch\n", returncode=0),  # config merge
            Mock(stdout="2\t1\n", returncode=0),  # ahead/behind counts
            Mock(stdout="main\n", returncode=0)  # current branch
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.get_branch_details("feature-branch")
        
        assert result.success is True
        assert result.data["branch"]["name"] == "feature-branch"
        assert result.data["branch"]["last_commit_hash"] == "abc123"
        assert result.data["branch"]["last_commit_message"] == "Add new feature"
        assert result.data["branch"]["last_commit_author"] == "John Doe"
        assert result.data["branch"]["tracking_branch"] == "origin/feature-branch"
        assert result.data["ahead_count"] == 2
        assert result.data["behind_count"] == 1
        assert result.data["short_hash"] == "abc123d"
        assert result.data["author_email"] == "john@example.com"
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_branch_details_not_found(self, mock_exists, mock_run):
        """Test getting details for non-existent branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # get_branch_details mocks
            subprocess.CalledProcessError(1, "git show-ref", stderr="fatal: branch 'nonexistent' not found")
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.get_branch_details("nonexistent")
        
        assert result.success is False
        assert result.error_code == "GIT_BRANCH_NOT_FOUND"
        assert "does not exist" in result.message
        assert any("list_branches()" in suggestion for suggestion in result.suggestions)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_rename_branch_success(self, mock_exists, mock_run):
        """Test successful branch renaming"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # rename_branch mocks
            Mock(stdout="ref: refs/heads/old-branch\n", returncode=0),  # show-ref (branch exists)
            Mock(stdout="", returncode=0)  # branch -m (rename)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.rename_branch("old-branch", "new-branch")
        
        assert result.success is True
        assert result.data["old_name"] == "old-branch"
        assert result.data["new_name"] == "new-branch"
        assert "Renamed branch" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_rename_branch_invalid_name(self, mock_exists, mock_run):
        """Test renaming branch with invalid new name"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.rename_branch("old-branch", "invalid name")
        
        assert result.success is False
        assert result.error_code == "GIT_INVALID_BRANCH_NAME"
        assert "Invalid new branch name" in result.message
        assert len(result.suggestions) > 0
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_rename_branch_source_not_found(self, mock_exists, mock_run):
        """Test renaming non-existent branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # rename_branch mocks
            subprocess.CalledProcessError(1, "git show-ref", stderr="fatal: branch 'nonexistent' not found")
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.rename_branch("nonexistent", "new-name")
        
        assert result.success is False
        assert result.error_code == "GIT_BRANCH_NOT_FOUND"
        assert "does not exist" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_rename_branch_target_exists(self, mock_exists, mock_run):
        """Test renaming branch when target name already exists"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # rename_branch mocks
            Mock(stdout="ref: refs/heads/old-branch\n", returncode=0),  # show-ref (branch exists)
            subprocess.CalledProcessError(128, "git branch", stderr="fatal: A branch named 'existing-branch' already exists.")
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.rename_branch("old-branch", "existing-branch")
        
        assert result.success is False
        assert result.error_code == "GIT_RENAME_BRANCH_FAILED"
        assert any("already exists" in suggestion for suggestion in result.suggestions)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_set_upstream_branch_success(self, mock_exists, mock_run):
        """Test setting upstream branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # set_upstream_branch mock
            Mock(stdout="", returncode=0)  # branch --set-upstream-to
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.set_upstream_branch("feature-branch", "origin/feature-branch")
        
        assert result.success is True
        assert result.data["branch_name"] == "feature-branch"
        assert result.data["upstream"] == "origin/feature-branch"
        assert "Set upstream" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_set_upstream_branch_upstream_not_found(self, mock_exists, mock_run):
        """Test setting upstream to non-existent branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # set_upstream_branch mock
            subprocess.CalledProcessError(1, "git branch", stderr="error: the requested upstream branch 'origin/nonexistent' does not exist")
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.set_upstream_branch("feature-branch", "origin/nonexistent")
        
        assert result.success is False
        assert result.error_code == "GIT_SET_UPSTREAM_FAILED"
        assert any("does not exist" in suggestion for suggestion in result.suggestions)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_unset_upstream_branch_success(self, mock_exists, mock_run):
        """Test unsetting upstream branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # unset_upstream_branch mock
            Mock(stdout="", returncode=0)  # branch --unset-upstream
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.unset_upstream_branch("feature-branch")
        
        assert result.success is True
        assert result.data["branch_name"] == "feature-branch"
        assert "Unset upstream" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_unset_upstream_branch_no_upstream(self, mock_exists, mock_run):
        """Test unsetting upstream when none is set"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # unset_upstream_branch mock
            subprocess.CalledProcessError(1, "git branch", stderr="error: No upstream branch found for 'feature-branch'")
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.unset_upstream_branch("feature-branch")
        
        assert result.success is False
        assert result.error_code == "GIT_UNSET_UPSTREAM_FAILED"
        assert any("no upstream" in suggestion.lower() for suggestion in result.suggestions)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_compare_branches_ahead(self, mock_exists, mock_run):
        """Test comparing branches where branch1 is ahead"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # compare_branches mocks
            Mock(stdout="2\n", returncode=0),  # ahead count
            Mock(stdout="0\n", returncode=0),  # behind count
            Mock(stdout="abc123|Add feature A|John Doe|2024-01-15 10:30:00\ndef456|Add feature B|Jane Doe|2024-01-14 15:20:00\n", returncode=0)  # commits ahead
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.compare_branches("feature-branch", "main")
        
        assert result.success is True
        assert result.data["relationship"] == "feature-branch is ahead"
        assert result.data["ahead_count"] == 2
        assert result.data["behind_count"] == 0
        assert result.data["can_fast_forward"] is True
        assert len(result.data["commits_ahead"]) == 2
        assert len(result.data["commits_behind"]) == 0
        assert result.data["commits_ahead"][0]["hash"] == "abc123"
        assert result.data["commits_ahead"][0]["message"] == "Add feature A"
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_compare_branches_behind(self, mock_exists, mock_run):
        """Test comparing branches where branch1 is behind"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # compare_branches mocks
            Mock(stdout="0\n", returncode=0),  # ahead count
            Mock(stdout="3\n", returncode=0),  # behind count
            Mock(stdout="xyz789|Fix bug C|Alice Smith|2024-01-16 09:15:00\n", returncode=0)  # commits behind
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.compare_branches("feature-branch", "main")
        
        assert result.success is True
        assert result.data["relationship"] == "feature-branch is behind"
        assert result.data["ahead_count"] == 0
        assert result.data["behind_count"] == 3
        assert result.data["can_fast_forward"] is False
        assert len(result.data["commits_ahead"]) == 0
        assert len(result.data["commits_behind"]) == 1
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_compare_branches_identical(self, mock_exists, mock_run):
        """Test comparing identical branches"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # compare_branches mocks
            Mock(stdout="0\n", returncode=0),  # ahead count
            Mock(stdout="0\n", returncode=0)   # behind count
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.compare_branches("branch1", "branch2")
        
        assert result.success is True
        assert result.data["relationship"] == "identical"
        assert result.data["ahead_count"] == 0
        assert result.data["behind_count"] == 0
        assert result.data["can_fast_forward"] is False
        assert len(result.data["commits_ahead"]) == 0
        assert len(result.data["commits_behind"]) == 0
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_compare_branches_diverged(self, mock_exists, mock_run):
        """Test comparing diverged branches"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # compare_branches mocks
            Mock(stdout="2\n", returncode=0),  # ahead count
            Mock(stdout="1\n", returncode=0),  # behind count
            Mock(stdout="abc123|Feature commit|John Doe|2024-01-15 10:30:00\n", returncode=0),  # commits ahead
            Mock(stdout="def456|Main commit|Jane Doe|2024-01-14 15:20:00\n", returncode=0)   # commits behind
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.compare_branches("feature-branch", "main")
        
        assert result.success is True
        assert result.data["relationship"] == "diverged"
        assert result.data["ahead_count"] == 2
        assert result.data["behind_count"] == 1
        assert result.data["can_fast_forward"] is False
        assert len(result.data["commits_ahead"]) == 1
        assert len(result.data["commits_behind"]) == 1
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_compare_branches_invalid_branch(self, mock_exists, mock_run):
        """Test comparing with non-existent branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # compare_branches mock
            subprocess.CalledProcessError(128, "git rev-list", stderr="fatal: bad revision 'nonexistent'")
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.compare_branches("feature-branch", "nonexistent")
        
        assert result.success is False
        assert result.error_code == "GIT_COMPARE_BRANCHES_FAILED"
        assert any("do not exist" in suggestion for suggestion in result.suggestions)


if __name__ == "__main__":
    # Run a quick test
    test_class = TestBranchManagement()
    
    try:
        test_class.test_get_branch_details_success()
        print("✅ Get branch details test passed")
        
        test_class.test_rename_branch_success()
        print("✅ Rename branch test passed")
        
        test_class.test_set_upstream_branch_success()
        print("✅ Set upstream test passed")
        
        test_class.test_compare_branches_ahead()
        print("✅ Compare branches test passed")
        
        print("\n🎉 All branch management tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise