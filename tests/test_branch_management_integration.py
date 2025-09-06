"""
Integration tests for enhanced branch management operations.

These tests validate the branch management functionality against a real git repository.
"""

import os
import pytest
from src.gitkraken_integration.providers.standard_git_provider import StandardGitProvider
from src.gitkraken_integration.providers.git_provider import GitOperationStatus


class TestBranchManagementIntegration:
    """Integration tests for branch management operations"""
    
    def test_get_branch_details_current_branch(self):
        """Test getting details for the current branch"""
        provider = StandardGitProvider(".")
        
        # First get the current branch name
        current_result = provider.get_current_branch()
        assert current_result.success is True
        current_branch = current_result.data["branch"]
        
        # Skip if in detached HEAD state
        if "HEAD detached" in current_branch:
            pytest.skip("Repository is in detached HEAD state")
        
        # Get details for current branch
        result = provider.get_branch_details(current_branch)
        
        assert result.success is True
        assert result.status == GitOperationStatus.SUCCESS
        assert result.data["branch"]["name"] == current_branch
        assert result.data["branch"]["is_current"] is True
        assert isinstance(result.data["branch"]["last_commit_hash"], str)
        assert len(result.data["branch"]["last_commit_hash"]) >= 7
        assert isinstance(result.data["branch"]["last_commit_message"], str)
        assert isinstance(result.data["branch"]["last_commit_author"], str)
        assert isinstance(result.data["short_hash"], str)
        assert isinstance(result.data["author_email"], str)
    
    def test_get_branch_details_nonexistent(self):
        """Test getting details for non-existent branch"""
        provider = StandardGitProvider(".")
        result = provider.get_branch_details("definitely-does-not-exist-branch-12345")
        
        assert result.success is False
        assert result.error_code == "GIT_BRANCH_NOT_FOUND"
        assert "does not exist" in result.message
        assert len(result.suggestions) > 0
    
    def test_compare_branches_with_main(self):
        """Test comparing current branch with main/master"""
        provider = StandardGitProvider(".")
        
        # Get current branch
        current_result = provider.get_current_branch()
        assert current_result.success is True
        current_branch = current_result.data["branch"]
        
        # Skip if in detached HEAD state
        if "HEAD detached" in current_branch:
            pytest.skip("Repository is in detached HEAD state")
        
        # Try to find main or master branch
        branches_result = provider.list_branches(include_remote=False)
        assert branches_result.success is True
        
        branch_names = [b["name"] for b in branches_result.data["branches"]]
        
        target_branch = None
        if "main" in branch_names:
            target_branch = "main"
        elif "master" in branch_names:
            target_branch = "master"
        
        if target_branch and target_branch != current_branch:
            result = provider.compare_branches(current_branch, target_branch)
            
            assert result.success is True
            assert result.status == GitOperationStatus.SUCCESS
            assert result.data["branch1"] == current_branch
            assert result.data["branch2"] == target_branch
            assert result.data["relationship"] in ["identical", "diverged", f"{current_branch} is ahead", f"{current_branch} is behind"]
            assert isinstance(result.data["ahead_count"], int)
            assert isinstance(result.data["behind_count"], int)
            assert isinstance(result.data["can_fast_forward"], bool)
            assert isinstance(result.data["commits_ahead"], list)
            assert isinstance(result.data["commits_behind"], list)
        else:
            pytest.skip(f"No suitable target branch found for comparison with {current_branch}")
    
    def test_compare_branches_identical(self):
        """Test comparing a branch with itself"""
        provider = StandardGitProvider(".")
        
        # Get current branch
        current_result = provider.get_current_branch()
        assert current_result.success is True
        current_branch = current_result.data["branch"]
        
        # Skip if in detached HEAD state
        if "HEAD detached" in current_branch:
            pytest.skip("Repository is in detached HEAD state")
        
        result = provider.compare_branches(current_branch, current_branch)
        
        assert result.success is True
        assert result.data["relationship"] == "identical"
        assert result.data["ahead_count"] == 0
        assert result.data["behind_count"] == 0
        assert result.data["can_fast_forward"] is False
        assert len(result.data["commits_ahead"]) == 0
        assert len(result.data["commits_behind"]) == 0
    
    def test_compare_branches_nonexistent(self):
        """Test comparing with non-existent branch"""
        provider = StandardGitProvider(".")
        
        # Get current branch
        current_result = provider.get_current_branch()
        assert current_result.success is True
        current_branch = current_result.data["branch"]
        
        # Skip if in detached HEAD state
        if "HEAD detached" in current_branch:
            pytest.skip("Repository is in detached HEAD state")
        
        result = provider.compare_branches(current_branch, "definitely-does-not-exist-branch-12345")
        
        assert result.success is False
        assert result.error_code == "GIT_COMPARE_BRANCHES_FAILED"
        assert len(result.suggestions) > 0
    
    def test_branch_name_validation_comprehensive(self):
        """Test comprehensive branch name validation"""
        provider = StandardGitProvider(".")
        
        # Valid branch names
        valid_names = [
            "feature/new-feature",
            "bugfix/issue-123",
            "hotfix/critical-fix",
            "develop",
            "main",
            "master",
            "release/v1.0.0",
            "feature-branch",
            "feature_branch",
            "123-numeric-start",
            "branch-with-numbers-123"
        ]
        
        for name in valid_names:
            assert provider.validate_branch_name(name) is True, f"'{name}' should be valid"
        
        # Invalid branch names
        invalid_names = [
            "",  # Empty
            "feature with spaces",  # Spaces
            "feature~branch",  # Tilde
            "feature^branch",  # Caret
            "feature:branch",  # Colon
            "feature?branch",  # Question mark
            "feature*branch",  # Asterisk
            "feature[branch",  # Square bracket
            "feature\\branch",  # Backslash
            "feature..branch",  # Double dot
            ".feature",  # Starts with dot
            "feature.",  # Ends with dot
            "-feature",  # Starts with dash
            "feature/",  # Ends with slash
            "feature//branch",  # Double slash
            "feature branch name",  # Multiple spaces
            "feature\tbranch",  # Tab character
            "feature\nbranch"  # Newline character
        ]
        
        for name in invalid_names:
            assert provider.validate_branch_name(name) is False, f"'{name}' should be invalid"
    
    def test_commit_message_formatting_comprehensive(self):
        """Test comprehensive commit message formatting"""
        provider = StandardGitProvider(".")
        
        # Test cases for commit message formatting
        test_cases = [
            # (input, expected_output)
            ("Simple message", "Simple message"),
            ("", ""),
            ("   ", ""),
            ("Message with trailing spaces   ", "Message with trailing spaces"),
            ("A" * 50, "A" * 50),  # Normal length
            ("A" * 80, "A" * 72),  # Should be truncated
            ("A" * 100, "A" * 72),  # Should be truncated
            ("First line\nSecond line", "First line\n\nSecond line"),  # Add blank line
            ("First line\n\nSecond line", "First line\n\nSecond line"),  # Keep existing blank line
            ("First line\nSecond line\nThird line", "First line\n\nSecond line\nThird line"),
            ("Multi\nline\nmessage\nwith\nmany\nlines", "Multi\n\nline\nmessage\nwith\nmany\nlines")
        ]
        
        for input_msg, expected in test_cases:
            result = provider.format_commit_message(input_msg)
            assert result == expected, f"Input: '{input_msg}' -> Expected: '{expected}' -> Got: '{result}'"
    
    def test_provider_capabilities_branch_management(self):
        """Test that provider reports branch management capabilities correctly"""
        provider = StandardGitProvider(".")
        capabilities = provider.get_provider_capabilities()
        
        # Branch management should be supported
        assert capabilities["branch_management"] is True
        
        # Enhanced features should not be supported in standard provider
        assert capabilities["visual_merge_tools"] is False
        assert capabilities["enhanced_ui"] is False
        assert capabilities["api_integration"] is False
        assert capabilities["advanced_analytics"] is False


if __name__ == "__main__":
    # Run integration tests
    test_class = TestBranchManagementIntegration()
    
    try:
        test_class.test_get_branch_details_current_branch()
        print("✅ Get branch details integration test passed")
        
        test_class.test_get_branch_details_nonexistent()
        print("✅ Get nonexistent branch details test passed")
        
        test_class.test_compare_branches_with_main()
        print("✅ Compare branches integration test passed")
        
        test_class.test_compare_branches_identical()
        print("✅ Compare identical branches test passed")
        
        test_class.test_compare_branches_nonexistent()
        print("✅ Compare with nonexistent branch test passed")
        
        test_class.test_branch_name_validation_comprehensive()
        print("✅ Comprehensive branch name validation test passed")
        
        test_class.test_commit_message_formatting_comprehensive()
        print("✅ Comprehensive commit message formatting test passed")
        
        test_class.test_provider_capabilities_branch_management()
        print("✅ Provider capabilities test passed")
        
        print("\n🎉 All branch management integration tests passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        raise