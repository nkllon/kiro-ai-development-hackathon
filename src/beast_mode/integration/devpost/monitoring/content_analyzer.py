"""
Content analysis system for intelligent change detection.

This module provides content-based change detection, media file analysis,
and Git integration for detecting significant changes in project files.
"""

import hashlib
import logging
import mimetypes
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import re

from ....utils.path_normalizer import safe_relative_to

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Analyzes file content for intelligent change detection."""
    
    def __init__(self, project_path: Path):
        """Initialize content analyzer."""
        self.project_path = Path(project_path).resolve()
        self._content_cache: Dict[str, str] = {}
        self._git_repo: Optional['git.Repo'] = None
        
        # Initialize Git repository if available
        if GIT_AVAILABLE:
            try:
                self._git_repo = git.Repo(self.project_path, search_parent_directories=True)
            except (git.InvalidGitRepositoryError, git.GitCommandError):
                logger.debug("No Git repository found or Git not available")
                self._git_repo = None
    
    def analyze_file_change(self, file_path: Path, change_type: str) -> Dict[str, Any]:
        """
        Analyze a file change for significance and metadata.
        
        Args:
            file_path: Path to the changed file
            change_type: Type of change (created, modified, deleted)
            
        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            'is_significant_change': True,
            'content_hash': None,
            'previous_content_hash': None,
            'media_metadata': None,
            'git_info': None,
            'content_type': None
        }
        
        try:
            # Get content type
            analysis['content_type'] = self._get_content_type(file_path)
            
            # Analyze based on file type and change type
            if change_type == 'deleted':
                analysis['content_hash'] = None
                analysis['previous_content_hash'] = self._content_cache.get(str(file_path))
            else:
                # Calculate content hash
                content_hash = self._calculate_content_hash(file_path)
                analysis['content_hash'] = content_hash
                analysis['previous_content_hash'] = self._content_cache.get(str(file_path))
                
                # Check if content actually changed
                if analysis['previous_content_hash'] == content_hash:
                    analysis['is_significant_change'] = False
                else:
                    # Update cache
                    self._content_cache[str(file_path)] = content_hash
                
                # Analyze documentation files for significant changes
                if self._is_documentation_file(file_path):
                    analysis['is_significant_change'] = self._analyze_documentation_change(
                        file_path, analysis['previous_content_hash'], content_hash
                    )
                
                # Analyze media files
                if self._is_media_file(file_path):
                    analysis['media_metadata'] = self._analyze_media_file(file_path)
            
            # Get Git information
            if self._git_repo:
                analysis['git_info'] = self._get_git_info(file_path)
            
        except Exception as e:
            logger.error(f"Error analyzing file change for {file_path}: {e}")
        
        return analysis
    
    def detect_git_releases(self) -> List[Dict[str, Any]]:
        """Detect new Git releases and tags."""
        releases = []
        
        if not self._git_repo:
            return releases
        
        try:
            # Get recent tags
            tags = list(self._git_repo.tags)
            
            # Sort tags by creation date (most recent first)
            tags.sort(key=lambda t: t.commit.committed_datetime, reverse=True)
            
            # Check for new tags (created in last 24 hours)
            recent_threshold = datetime.now().timestamp() - (24 * 60 * 60)
            
            for tag in tags[:10]:  # Check last 10 tags
                tag_date = tag.commit.committed_datetime.timestamp()
                if tag_date > recent_threshold:
                    releases.append({
                        'tag_name': tag.name,
                        'commit_hash': tag.commit.hexsha,
                        'commit_message': tag.commit.message.strip(),
                        'created_at': tag.commit.committed_datetime,
                        'is_release': self._is_release_tag(tag.name)
                    })
            
        except Exception as e:
            logger.error(f"Error detecting Git releases: {e}")
        
        return releases
    
    def get_project_changes_summary(self, since: datetime) -> Dict[str, Any]:
        """Get summary of project changes since a given time."""
        summary = {
            'total_commits': 0,
            'files_changed': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'new_releases': [],
            'significant_files': []
        }
        
        if not self._git_repo:
            return summary
        
        try:
            # Get commits since the given time
            commits = list(self._git_repo.iter_commits(
                since=since.strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            summary['total_commits'] = len(commits)
            
            if commits:
                # Get diff statistics
                latest_commit = commits[0]
                if len(commits) > 1:
                    diff = latest_commit.diff(commits[-1])
                else:
                    # Compare with parent if only one commit
                    if latest_commit.parents:
                        diff = latest_commit.diff(latest_commit.parents[0])
                    else:
                        diff = latest_commit.diff(None)
                
                summary['files_changed'] = len(diff)
                
                # Calculate line changes
                for item in diff:
                    if item.a_blob and item.b_blob:
                        try:
                            # This is a rough estimation
                            summary['lines_added'] += len(item.b_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                            summary['lines_removed'] += len(item.a_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                        except:
                            pass
            
            # Check for new releases
            summary['new_releases'] = self.detect_git_releases()
            
            # Identify significant files (README, docs, config files)
            significant_patterns = ['README', 'CHANGELOG', 'package.json', 'pyproject.toml']
            for commit in commits[:5]:  # Check last 5 commits
                for item in commit.stats.files:
                    file_path = Path(item)
                    if any(pattern.lower() in file_path.name.lower() for pattern in significant_patterns):
                        if str(file_path) not in summary['significant_files']:
                            summary['significant_files'].append(str(file_path))
            
        except Exception as e:
            logger.error(f"Error getting project changes summary: {e}")
        
        return summary
    
    def _calculate_content_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA-256 hash of file content."""
        try:
            if not file_path.exists():
                return None
            
            # For binary files, hash the entire content
            if self._is_binary_file(file_path):
                with open(file_path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
            
            # For text files, normalize line endings and hash
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Normalize line endings
                content = content.replace('\r\n', '\n').replace('\r', '\n')
                return hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        except Exception as e:
            logger.error(f"Error calculating content hash for {file_path}: {e}")
            return None
    
    def _analyze_documentation_change(self, file_path: Path, previous_hash: Optional[str], current_hash: str) -> bool:
        """Analyze if documentation change is significant."""
        if not previous_hash:
            return True  # New file is always significant
        
        if previous_hash == current_hash:
            return False  # No change
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for significant changes
            significant_indicators = [
                r'#\s+.*',  # Headers
                r'\*\*.*\*\*',  # Bold text
                r'!\[.*\]\(.*\)',  # Images
                r'\[.*\]\(.*\)',  # Links
                r'```.*```',  # Code blocks
                r'- \w+',  # List items
                r'\d+\.\s+\w+',  # Numbered lists
            ]
            
            # Count significant content
            significant_lines = 0
            total_lines = len(content.splitlines())
            
            for line in content.splitlines():
                line = line.strip()
                if line and any(re.search(pattern, line) for pattern in significant_indicators):
                    significant_lines += 1
            
            # Consider change significant if it affects substantial content
            if total_lines > 0:
                significant_ratio = significant_lines / total_lines
                return significant_ratio > 0.1  # More than 10% significant content changed
            
            return True
        
        except Exception as e:
            logger.error(f"Error analyzing documentation change for {file_path}: {e}")
            return True  # Default to significant on error
    
    def _analyze_media_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze media file for metadata."""
        if not file_path.exists():
            return None
        
        metadata = {
            'file_size': file_path.stat().st_size,
            'mime_type': mimetypes.guess_type(str(file_path))[0],
            'category': self._get_media_category(file_path)
        }
        
        try:
            # Analyze images with PIL if available
            if PIL_AVAILABLE and metadata['category'] == 'image':
                try:
                    with Image.open(file_path) as img:
                        metadata.update({
                            'width': img.width,
                            'height': img.height,
                            'format': img.format,
                            'mode': img.mode
                        })
                except Exception as e:
                    logger.debug(f"Could not analyze image {file_path}: {e}")
            
            # Analyze videos (basic info)
            elif metadata['category'] == 'video':
                try:
                    # Try to get video info using ffprobe if available
                    result = subprocess.run([
                        'ffprobe', '-v', 'quiet', '-print_format', 'json',
                        '-show_format', '-show_streams', str(file_path)
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        import json
                        video_info = json.loads(result.stdout)
                        if 'format' in video_info:
                            metadata['duration'] = float(video_info['format'].get('duration', 0))
                        if 'streams' in video_info:
                            for stream in video_info['streams']:
                                if stream.get('codec_type') == 'video':
                                    metadata['width'] = stream.get('width')
                                    metadata['height'] = stream.get('height')
                                    break
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    logger.debug(f"Could not analyze video {file_path}")
        
        except Exception as e:
            logger.error(f"Error analyzing media file {file_path}: {e}")
        
        return metadata
    
    def _get_git_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get Git information for a file."""
        if not self._git_repo:
            return None
        
        try:
            # Get relative path from repo root
            repo_root = Path(self._git_repo.working_dir)
            relative_path = safe_relative_to(file_path, repo_root)
            if relative_path is None:
                return None  # File is outside repo
            
            git_info = {}
            
            # Get last commit for this file
            try:
                commits = list(self._git_repo.iter_commits(paths=str(relative_path), max_count=1))
                if commits:
                    last_commit = commits[0]
                    git_info.update({
                        'last_commit_hash': last_commit.hexsha,
                        'last_commit_message': last_commit.message.strip(),
                        'last_commit_author': str(last_commit.author),
                        'last_commit_date': last_commit.committed_datetime
                    })
            except Exception:
                pass
            
            # Check if file is tracked
            try:
                git_info['is_tracked'] = str(relative_path) in [item.a_path for item in self._git_repo.index.diff(None)]
            except Exception:
                git_info['is_tracked'] = False
            
            # Check if file is in staging area
            try:
                git_info['is_staged'] = str(relative_path) in [item.a_path for item in self._git_repo.index.diff('HEAD')]
            except Exception:
                git_info['is_staged'] = False
            
            return git_info if git_info else None
        
        except Exception as e:
            logger.error(f"Error getting Git info for {file_path}: {e}")
            return None
    
    def _get_content_type(self, file_path: Path) -> Optional[str]:
        """Get MIME type of file."""
        return mimetypes.guess_type(str(file_path))[0]
    
    def _is_documentation_file(self, file_path: Path) -> bool:
        """Check if file is a documentation file."""
        doc_patterns = ['readme', 'changelog', 'license', 'contributing', 'docs']
        filename_lower = file_path.name.lower()
        return (
            any(pattern in filename_lower for pattern in doc_patterns) or
            file_path.suffix.lower() in {'.md', '.txt', '.rst', '.adoc'} or
            'docs/' in str(file_path).lower()
        )
    
    def _is_media_file(self, file_path: Path) -> bool:
        """Check if file is a media file."""
        media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.pdf', '.webp', '.svg'}
        return file_path.suffix.lower() in media_extensions
    
    def _get_media_category(self, file_path: Path) -> str:
        """Get media file category."""
        suffix = file_path.suffix.lower()
        if suffix in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}:
            return 'image'
        elif suffix in {'.mp4', '.mov', '.avi', '.webm', '.mkv'}:
            return 'video'
        elif suffix in {'.pdf', '.doc', '.docx'}:
            return 'document'
        else:
            return 'other'
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except Exception:
            return True  # Assume binary if can't read
    
    def _is_release_tag(self, tag_name: str) -> bool:
        """Check if tag name indicates a release."""
        release_patterns = [
            r'^v?\d+\.\d+\.\d+',  # Semantic versioning
            r'^release',  # Release prefix
            r'^r\d+',  # Release number
        ]
        return any(re.match(pattern, tag_name.lower()) for pattern in release_patterns)