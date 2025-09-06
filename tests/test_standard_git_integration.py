"""
Integration tests for StandardGitProvider with actual git repository.

These tests run against the actual git repository to ensure the provider
works correctly in real scenarios.
"""

import os
import pytest
from src.gitkraken_integration.providers.standard_git_provider import StandardGitProvider
from src.gitkraken_integration.providers.git_provider import GitOperationStatus


class TestStandardGitIntegration:
    """Integration tests for StandardGitProvider"""
    
    def test_provider_initialization_with_current_repo(self):
        """Test provider initialization with current repository"""
        # This should work since we're in a git repository
        provider = StandardGitProvider(".")
        
        assert provider.repo_path == "."
        assert provider.git_executable is not None
        assert provider.is_available() is True
    
    def test_get_status_current_repo(self):
        """Test getting status of current repository"""
        provider = StandardGitProvider(".")
        result = provider.get_status()
        
        assert result.success is True
        assert result.status == GitOperationStatus.SUCCESS
        assert result.provider_used == "Standard Git"
        assert "branch" in result.data
        assert "files" in result.data
        assert "clean" in result.data
        assert isinstance(result.data["total_files"], int)
        assert isinstance(result.data["staged_files"], int)
        assert isinstance(result.data["modified_files"], int)
        assert isinstance(result.data["untracked_files"], int)
    
    def test_get_current_branch_current_repo(self):
        """Test getting current branch of current repository"""
        provider = StandardGitProvider(".")
        result = provider.get_current_branch()
        
        assert result.success is True
        assert result.status == GitOperationStatus.SUCCESS
        assert "branch" in result.data
        assert isinstance(result.data["branch"], str)
        assert len(result.data["branch"]) > 0
    
    def test_list_branches_current_repo(self):
        """Test listing branches of current repository"""
        provider = StandardGitProvider(".")
        result = provider.list_branches()
        
        assert result.success is True
        assert result.status == GitOperationStatus.SUCCESS
        assert "branches" in result.data
        assert "total_count" in result.data
        assert "local_count" in result.data
        assert "remote_count" in result.data
        assert isinstance(result.data["branches"], list)
        assert result.data["total_count"] > 0
        
        # Check that at least one branch is marked as current
        branches = result.data["branches"]
        current_branches = [b for b in branches if b.get("is_current", False)]
        assert len(current_branches) >= 1
    
    def test_provider_capabilities(self):
        """Test provider capabilities"""
        provider = StandardGitProvider(".")
        capabilities = provider.get_provider_capabilities()
        
        expected_capabilities = [
            "branch_management",
            "commit_operations", 
            "remote_operations",
            "conflict_resolution",
            "visual_merge_tools",
            "enhanced_ui",
            "api_integration",
            "advanced_analytics"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
            assert isinstance(capabilities[capability], bool)
        
        # Standard git should have basic capabilities but not enhanced ones
        assert capabilities["branch_management"] is True
        assert capabilities["commit_operations"] is True
        assert capabilities["remote_operations"] is True
        assert capabilities["conflict_resolution"] is True
        assert capabilities["visual_merge_tools"] is False
        assert capabilities["enhanced_ui"] is False
        assert capabilities["api_integration"] is False
        assert capabilities["advanced_analytics"] is False
    
    def test_health_status_current_repo(self):
        """Test health status of current repository"""
        provider = StandardGitProvider(".")
        result = provider.get_health_status()
        
        assert result.success is True
        assert result.status == GitOperationStatus.SUCCESS
        assert "git_version" in result.data
        assert "repository_accessible" in result.data
        assert "remote_accessible" in result.data
        assert "git_executable" in result.data
        assert "repo_path" in result.data
        
        assert result.data["repository_accessible"] is True
        assert "git version" in result.data["git_version"]
        assert result.data["git_executable"] is not None
        assert result.data["repo_path"] == "."
    
    def test_branch_name_validation(self):
        """Test branch name validation"""
        provider = StandardGitProvider(".")
        
        # Valid names
        assert provider.validate_branch_name("feature/test") is True
        assert provider.validate_branch_name("main") is True
        assert provider.validate_branch_name("develop") is True
        assert provider.validate_branch_name("feature-123") is True
        assert provider.validate_branch_name("hotfix/bug-fix") is True
        
        # Invalid names
        assert provider.validate_branch_name("") is False
        assert provider.validate_branch_name("feature with spaces") is False
        assert provider.validate_branch_name("feature~test") is False
        assert provider.validate_branch_name("feature^test") is False
        assert provider.validate_branch_name(".feature") is False
        assert provider.validate_branch_name("feature.") is False
        assert provider.validate_branch_name("-feature") is False
        assert provider.validate_branch_name("feature/") is False
    
    def test_commit_message_formatting(self):
        """Test commit message formatting"""
        provider = StandardGitProvider(".")
        
        # Test various message formats
        short_message = "Add new feature"
        formatted = provider.format_commit_message(short_message)
        assert formatted == short_message
        
        # Test long message (should be truncated)
        long_message = "A" * 80
        formatted = provider.format_commit_message(long_message)
        assert len(formatted) == 72
        
        # Test multi-line message
        multi_line = "Add new feature\nDetailed description of the feature"
        formatted = provider.format_commit_message(multi_line)
        lines = formatted.split('\n')
        assert lines[0] == "Add new feature"
        assert lines[1] == ""  # Blank line added
        assert lines[2] == "Detailed description of the feature"
    
    def test_placeholder_methods_return_not_implemented(self):
        """Test that placeholder methods return NOT_IMPLEMENTED"""
        provider = StandardGitProvider(".")
        
        # These methods should return NOT_IMPLEMENTED until implemented in later tasks
        placeholder_methods = [
            ("stage_files", []),
            ("unstage_files", []),
            ("commit_changes", ["test message"]),
            ("get_commit_history", []),
            ("push_changes", []),
            ("pull_changes", []),
            ("fetch_changes", []),
            ("get_merge_conflicts", []),
            ("resolve_conflict", ["file.py", "ours"])
        ]
        
        for method_name, args in placeholder_methods:
            method = getattr(provider, method_name)
            result = method(*args)
            
            assert result.success is False
            assert result.error_code == "NOT_IMPLEMENTED"
            assert "not yet implemented" in result.message


if __name__ == "__main__":
    # Run a quick integration test
    test_class = TestStandardGitIntegration()
    
    try:
        test_class.test_provider_initialization_with_current_repo()
        print("✅ Provider initialization test passed")
        
        test_class.test_get_status_current_repo()
        print("✅ Get status test passed")
        
        test_class.test_get_current_branch_current_repo()
        print("✅ Get current branch test passed")
        
        test_class.test_list_branches_current_repo()
        print("✅ List branches test passed")
        
        test_class.test_provider_capabilities()
        print("✅ Provider capabilities test passed")
        
        test_class.test_health_status_current_repo()
        print("✅ Health status test passed")
        
        test_class.test_branch_name_validation()
        print("✅ Branch name validation test passed")
        
        test_class.test_commit_message_formatting()
        print("✅ Commit message formatting test passed")
        
        test_class.test_placeholder_methods_return_not_implemented()
        print("✅ Placeholder methods test passed")
        
        print("\n🎉 All integration tests passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise