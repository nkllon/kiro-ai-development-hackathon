"""
Unit tests for GitAnalyzer component.

Tests the git analysis capabilities including commit analysis,
file change detection, and task mapping functionality.
"""

import pytest
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.beast_mode.compliance.git.analyzer import GitAnalyzer
from src.beast_mode.compliance.models import (
    CommitInfo,
    FileChangeAnalysis,
    ComplianceIssue,
    ComplianceIssueType,
    IssueSeverity
)


class TestGitAnalyzer:
    """Test suite for GitAnalyzer class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            # Create a .git directory to simulate a git repository
            (repo_path / ".git").mkdir()
            yield repo_path
    
    @pytest.fixture
    def git_analyzer(self, temp_repo):
        """Create a GitAnalyzer instance for testing."""
        return GitAnalyzer(str(temp_repo))
    
    @pytest.fixture
    def mock_commit_info(self):
        """Create mock commit info for testing."""
        return CommitInfo(
            commit_hash="abc123",
            author="Test Author",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            message="Test commit message",
            modified_files=["src/test.py"],
            added_files=["src/new.py"],
            deleted_files=["src/old.py"]
        )
    
    def test_init(self, temp_repo):
        """Test GitAnalyzer initialization."""
        analyzer = GitAnalyzer(str(temp_repo))
        
        # Use resolve() to handle symlinks consistently
        assert analyzer.repository_path.resolve() == temp_repo.resolve()
        assert analyzer.get_analyzer_name() == "GitAnalyzer"
        assert analyzer._config["target_branch"] == "main"
        assert analyzer._config["base_branch"] == "origin/master"
    
    def test_get_analyzer_name(self, git_analyzer):
        """Test get_analyzer_name method."""
        assert git_analyzer.get_analyzer_name() == "GitAnalyzer"
    
    def test_get_module_status(self, git_analyzer):
        """Test get_module_status method."""
        status = git_analyzer.get_module_status()
        
        assert status["module_name"] == "GitAnalyzer"
        assert "repository_path" in status
        assert "configuration" in status
        assert "is_healthy" in status
    
    def test_is_healthy_with_valid_repo(self, git_analyzer):
        """Test is_healthy method with valid repository."""
        with patch.object(git_analyzer, '_can_execute_git_commands', return_value=True):
            assert git_analyzer.is_healthy() is True
    
    def test_is_healthy_with_invalid_repo(self):
        """Test is_healthy method with invalid repository."""
        analyzer = GitAnalyzer("/nonexistent/path")
        assert analyzer.is_healthy() is False
    
    def test_get_health_indicators(self, git_analyzer):
        """Test get_health_indicators method."""
        with patch.object(git_analyzer, '_can_execute_git_commands', return_value=True):
            indicators = git_analyzer.get_health_indicators()
            
            assert "repository_accessible" in indicators
            assert "git_repository" in indicators
            assert "git_executable" in indicators
            
            assert indicators["repository_accessible"]["status"] == "healthy"
            assert indicators["git_repository"]["status"] == "healthy"
            assert indicators["git_executable"]["status"] == "healthy"
    
    @patch('subprocess.run')
    def test_get_commits_ahead_of_main_success(self, mock_run, git_analyzer):
        """Test successful retrieval of commits ahead of main."""
        # Create a list to track call order
        call_results = []
        
        # Mock git rev-list command (first call)
        rev_list_result = Mock()
        rev_list_result.returncode = 0
        rev_list_result.stdout = "commit1\ncommit2\ncommit3\n"
        call_results.append(rev_list_result)
        
        # Mock git show commands for each commit
        show_result1 = Mock()
        show_result1.returncode = 0
        show_result1.stdout = "commit1|Author1|1640995200|First commit\nA\tsrc/file1.py\n"
        call_results.append(show_result1)
        
        show_result2 = Mock()
        show_result2.returncode = 0
        show_result2.stdout = "commit2|Author2|1640995300|Second commit\nM\tsrc/file2.py\n"
        call_results.append(show_result2)
        
        show_result3 = Mock()
        show_result3.returncode = 0
        show_result3.stdout = "commit3|Author3|1640995400|Third commit\nD\tsrc/file3.py\n"
        call_results.append(show_result3)
        
        mock_run.side_effect = call_results
        
        commits = git_analyzer.get_commits_ahead_of_main()
        
        assert len(commits) == 3
        assert commits[0].commit_hash == "commit1"
        assert commits[0].author == "Author1"
        assert commits[0].message == "First commit"
        assert "src/file1.py" in commits[0].added_files
    
    @patch('subprocess.run')
    def test_get_commits_ahead_of_main_no_commits(self, mock_run, git_analyzer):
        """Test when no commits are ahead of main."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        
        commits = git_analyzer.get_commits_ahead_of_main()
        
        assert len(commits) == 0
    
    @patch('subprocess.run')
    def test_get_commits_ahead_of_main_git_error(self, mock_run, git_analyzer):
        """Test handling of git command errors."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "fatal: bad revision"
        
        commits = git_analyzer.get_commits_ahead_of_main()
        
        assert len(commits) == 0
    
    def test_analyze_file_changes_with_commits(self, git_analyzer, mock_commit_info):
        """Test file change analysis with provided commits."""
        commits = [mock_commit_info]
        
        with patch.object(git_analyzer, '_get_commit_line_changes', return_value=(10, 5)):
            analysis = git_analyzer.analyze_file_changes(commits)
            
            assert isinstance(analysis, FileChangeAnalysis)
            assert analysis.total_files_changed == 3  # 1 added + 1 modified + 1 deleted
            assert "src/new.py" in analysis.files_added
            assert "src/test.py" in analysis.files_modified
            assert "src/old.py" in analysis.files_deleted
            assert analysis.lines_added == 10
            assert analysis.lines_deleted == 5
    
    def test_analyze_file_changes_without_commits(self, git_analyzer):
        """Test file change analysis without provided commits."""
        with patch.object(git_analyzer, 'get_commits_ahead_of_main', return_value=[]):
            analysis = git_analyzer.analyze_file_changes()
            
            assert isinstance(analysis, FileChangeAnalysis)
            assert analysis.total_files_changed == 0
    
    def test_map_changes_to_tasks_default_patterns(self, git_analyzer):
        """Test mapping file changes to tasks with default patterns."""
        file_changes = FileChangeAnalysis(
            total_files_changed=3,
            files_added=["src/beast_mode/compliance/git/new_analyzer.py"],
            files_modified=["tests/test_compliance.py"],
            files_deleted=["docs/old_doc.md"]
        )
        
        task_mapping = git_analyzer.map_changes_to_tasks(file_changes)
        
        assert "git_analysis" in task_mapping
        assert "tests" in task_mapping
        assert "documentation" in task_mapping
        
        assert "src/beast_mode/compliance/git/new_analyzer.py" in task_mapping["git_analysis"]
        assert "tests/test_compliance.py" in task_mapping["tests"]
        assert "docs/old_doc.md" in task_mapping["documentation"]
    
    def test_map_changes_to_tasks_custom_patterns(self, git_analyzer):
        """Test mapping file changes to tasks with custom patterns."""
        file_changes = FileChangeAnalysis(
            total_files_changed=1,
            files_added=["custom/module.py"],
            files_modified=[],
            files_deleted=[]
        )
        
        custom_patterns = {
            "custom_task": ["custom/*"]
        }
        
        task_mapping = git_analyzer.map_changes_to_tasks(file_changes, custom_patterns)
        
        assert "custom_task" in task_mapping
        assert "custom/module.py" in task_mapping["custom_task"]
    
    def test_analyze_method(self, git_analyzer):
        """Test the analyze method from ComplianceAnalyzer interface."""
        context = {
            "target_branch": "feature-branch",
            "base_branch": "main"
        }
        
        with patch.object(git_analyzer, 'get_commits_ahead_of_main', return_value=[]):
            with patch.object(git_analyzer, 'analyze_file_changes') as mock_analyze:
                mock_analyze.return_value = FileChangeAnalysis(total_files_changed=0)
                
                result = git_analyzer.analyze(context)
                
                assert len(result.commits_analyzed) == 0
                assert len(result.recommendations) > 0
                assert "0 commits" in result.recommendations[0]
    
    def test_analyze_method_with_error(self, git_analyzer):
        """Test the analyze method when an error occurs."""
        context = {}
        
        with patch.object(git_analyzer, 'get_commits_ahead_of_main', side_effect=Exception("Git error")):
            result = git_analyzer.analyze(context)
            
            assert len(result.critical_issues) == 1
            assert result.critical_issues[0].issue_type == ComplianceIssueType.ARCHITECTURAL_VIOLATION
            assert result.critical_issues[0].severity == IssueSeverity.CRITICAL
            assert "Git analysis failed" in result.critical_issues[0].description
    
    @patch('subprocess.run')
    def test_get_commit_hashes_ahead_success(self, mock_run, git_analyzer):
        """Test successful retrieval of commit hashes."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "hash1\nhash2\nhash3\n"
        
        hashes = git_analyzer._get_commit_hashes_ahead("HEAD", "origin/master")
        
        assert hashes == ["hash1", "hash2", "hash3"]
    
    @patch('subprocess.run')
    def test_get_commit_hashes_ahead_timeout(self, mock_run, git_analyzer):
        """Test timeout handling in commit hash retrieval."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
        
        hashes = git_analyzer._get_commit_hashes_ahead("HEAD", "origin/master")
        
        assert hashes == []
    
    @patch('subprocess.run')
    def test_get_commit_info_success(self, mock_run, git_analyzer):
        """Test successful commit info retrieval."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "abc123|Test Author|1640995200|Test message\nA\tsrc/new.py\nM\tsrc/existing.py\n"
        
        commit_info = git_analyzer._get_commit_info("abc123")
        
        assert commit_info is not None
        assert commit_info.commit_hash == "abc123"
        assert commit_info.author == "Test Author"
        assert commit_info.message == "Test message"
        assert "src/new.py" in commit_info.added_files
        assert "src/existing.py" in commit_info.modified_files
    
    @patch('subprocess.run')
    def test_get_commit_info_invalid_format(self, mock_run, git_analyzer):
        """Test handling of invalid commit info format."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "invalid format"
        
        commit_info = git_analyzer._get_commit_info("abc123")
        
        assert commit_info is None
    
    @patch('subprocess.run')
    def test_get_commit_line_changes_success(self, mock_run, git_analyzer):
        """Test successful line change retrieval."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "10\t5\tsrc/file1.py\n3\t2\tsrc/file2.py\n"
        
        added, deleted = git_analyzer._get_commit_line_changes("abc123")
        
        assert added == 13  # 10 + 3
        assert deleted == 7  # 5 + 2
    
    @patch('subprocess.run')
    def test_get_commit_line_changes_error(self, mock_run, git_analyzer):
        """Test error handling in line change retrieval."""
        mock_run.return_value.returncode = 1
        
        added, deleted = git_analyzer._get_commit_line_changes("abc123")
        
        assert added == 0
        assert deleted == 0
    
    @patch('subprocess.run')
    def test_can_execute_git_commands_success(self, mock_run, git_analyzer):
        """Test successful git command execution check."""
        mock_run.return_value.returncode = 0
        
        result = git_analyzer._can_execute_git_commands()
        
        assert result is True
    
    @patch('subprocess.run')
    def test_can_execute_git_commands_failure(self, mock_run, git_analyzer):
        """Test failed git command execution check."""
        mock_run.return_value.returncode = 1
        
        result = git_analyzer._can_execute_git_commands()
        
        assert result is False
    
    def test_get_default_task_patterns(self, git_analyzer):
        """Test default task patterns."""
        patterns = git_analyzer._get_default_task_patterns()
        
        assert "compliance_infrastructure" in patterns
        assert "git_analysis" in patterns
        assert "rdi_validation" in patterns
        assert "rm_validation" in patterns
        assert "reporting" in patterns
        assert "documentation" in patterns
        assert "tests" in patterns
        
        # Check some specific patterns
        assert "src/beast_mode/compliance/*" in patterns["compliance_infrastructure"]
        assert "src/beast_mode/compliance/git/*" in patterns["git_analysis"]
        assert "tests/*" in patterns["tests"]
    
    def test_file_matches_pattern(self, git_analyzer):
        """Test file pattern matching."""
        assert git_analyzer._file_matches_pattern("src/test.py", "src/*.py") is True
        assert git_analyzer._file_matches_pattern("src/test.py", "tests/*.py") is False
        assert git_analyzer._file_matches_pattern("docs/README.md", "*.md") is True
        assert git_analyzer._file_matches_pattern("src/beast_mode/compliance/git/analyzer.py", "src/beast_mode/compliance/git/*") is True
    
    def test_get_primary_responsibility(self, git_analyzer):
        """Test _get_primary_responsibility method."""
        responsibility = git_analyzer._get_primary_responsibility()
        
        assert "git repository" in responsibility.lower()
        assert "compliance" in responsibility.lower()


class TestGitAnalyzerIntegration:
    """Integration tests for GitAnalyzer with real git operations."""
    
    @pytest.fixture
    def real_git_repo(self):
        """Create a real git repository for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Initialize git repository
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)
            
            # Create initial commit
            (repo_path / "README.md").write_text("# Test Repository")
            subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
            
            # Create master branch reference
            subprocess.run(["git", "branch", "master"], cwd=repo_path, check=True)
            
            yield repo_path
    
    def test_real_git_operations(self, real_git_repo):
        """Test GitAnalyzer with real git operations."""
        analyzer = GitAnalyzer(str(real_git_repo))
        
        # Create some changes
        (real_git_repo / "src").mkdir()
        (real_git_repo / "src" / "test.py").write_text("print('hello')")
        subprocess.run(["git", "add", "src/test.py"], cwd=real_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "Add test file"], cwd=real_git_repo, check=True)
        
        # Test health check
        assert analyzer.is_healthy() is True
        
        # Test getting commits ahead (should be 1 commit ahead of master)
        commits = analyzer.get_commits_ahead_of_main("HEAD", "master")
        assert len(commits) == 1
        assert commits[0].message == "Add test file"
        assert "src/test.py" in commits[0].added_files
        
        # Test file change analysis
        file_changes = analyzer.analyze_file_changes(commits)
        assert file_changes.total_files_changed == 1
        assert "src/test.py" in file_changes.files_added
        
        # Test task mapping
        task_mapping = analyzer.map_changes_to_tasks(file_changes)
        assert len(task_mapping) > 0


if __name__ == "__main__":
    pytest.main([__file__])