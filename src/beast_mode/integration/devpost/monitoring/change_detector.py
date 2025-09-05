"""
Intelligent change detection for Devpost integration.

This module provides content-based change detection, media file categorization,
and Git integration for detecting releases and tags.
"""

import hashlib
import logging
import mimetypes
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

from ..models import FileChangeEvent, ChangeType


logger = logging.getLogger(__name__)


@dataclass
class ContentChange:
    """Represents a content-based change in a file."""
    file_path: Path
    change_type: str  # 'content', 'metadata', 'structure'
    old_hash: Optional[str]
    new_hash: Optional[str]
    significance: float  # 0.0 to 1.0, higher means more significant
    description: str


@dataclass
class MediaFileInfo:
    """Information about a media file."""
    file_path: Path
    media_type: str  # 'image', 'video', 'audio', 'document'
    mime_type: str
    file_size: int
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    is_demo_material: bool = False


@dataclass
class GitChange:
    """Represents a Git-related change."""
    change_type: str  # 'tag', 'release', 'commit'
    ref_name: str
    commit_hash: str
    message: str
    timestamp: datetime
    affects_project: bool = True


class ChangeDetector:
    """
    Intelligent change detection system.
    
    Provides content-based change detection for documentation files,
    media file detection and categorization, and Git integration
    for detecting releases and tags.
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize the change detector.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path).resolve()
        self._file_hashes: Dict[str, str] = {}
        self._media_cache: Dict[str, MediaFileInfo] = {}
        self._git_refs_cache: Dict[str, str] = {}
        
        # Documentation file patterns
        self._doc_patterns = {
            'readme': re.compile(r'readme.*\.(md|txt|rst)$', re.IGNORECASE),
            'changelog': re.compile(r'(changelog|changes|history).*\.(md|txt|rst)$', re.IGNORECASE),
            'license': re.compile(r'licen[sc]e.*\.(md|txt|rst)?$', re.IGNORECASE),
            'contributing': re.compile(r'contributing.*\.(md|txt|rst)$', re.IGNORECASE),
            'docs': re.compile(r'.*\.(md|rst)$', re.IGNORECASE),
        }
        
        # Media file extensions
        self._media_extensions = {
            'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'},
            'video': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'},
            'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'},
            'document': {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'}
        }
        
        # Demo material indicators
        self._demo_indicators = {
            'screenshot', 'demo', 'preview', 'example', 'sample',
            'mockup', 'wireframe', 'prototype', 'showcase'
        }
        
        logger.info(f"Initialized change detector for {self.project_path}")
    
    def detect_content_changes(self, file_path: Path) -> Optional[ContentChange]:
        """
        Detect content-based changes in a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            ContentChange object if significant changes detected, None otherwise
        """
        try:
            if not file_path.exists():
                # File was deleted
                old_hash = self._file_hashes.pop(str(file_path), None)
                if old_hash:
                    return ContentChange(
                        file_path=file_path,
                        change_type='content',
                        old_hash=old_hash,
                        new_hash=None,
                        significance=1.0,
                        description="File deleted"
                    )
                return None
            
            # Calculate current hash
            new_hash = self._calculate_file_hash(file_path)
            old_hash = self._file_hashes.get(str(file_path))
            
            if old_hash == new_hash:
                return None  # No change
            
            # Update hash cache
            self._file_hashes[str(file_path)] = new_hash
            
            if old_hash is None:
                # New file
                significance = self._calculate_significance(file_path, is_new=True)
                return ContentChange(
                    file_path=file_path,
                    change_type='content',
                    old_hash=None,
                    new_hash=new_hash,
                    significance=significance,
                    description="New file created"
                )
            
            # File modified - analyze significance
            significance = self._analyze_change_significance(file_path, old_hash, new_hash)
            change_type = self._determine_change_type(file_path)
            description = self._generate_change_description(file_path, change_type, significance)
            
            return ContentChange(
                file_path=file_path,
                change_type=change_type,
                old_hash=old_hash,
                new_hash=new_hash,
                significance=significance,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Error detecting content changes for {file_path}: {e}")
            return None
    
    def categorize_media_file(self, file_path: Path) -> Optional[MediaFileInfo]:
        """
        Categorize and analyze a media file.
        
        Args:
            file_path: Path to the media file
            
        Returns:
            MediaFileInfo object with file details
        """
        try:
            if not file_path.exists():
                return None
            
            # Check cache first
            cache_key = str(file_path)
            if cache_key in self._media_cache:
                cached_info = self._media_cache[cache_key]
                # Verify file hasn't changed
                if cached_info.file_size == file_path.stat().st_size:
                    return cached_info
            
            # Determine media type
            media_type = self._get_media_type(file_path)
            if not media_type:
                return None
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Get file size
            file_size = file_path.stat().st_size
            
            # Check if it's demo material
            is_demo_material = self._is_demo_material(file_path)
            
            # Get additional metadata based on type
            dimensions = None
            duration = None
            
            if media_type == 'image':
                dimensions = self._get_image_dimensions(file_path)
            elif media_type in ('video', 'audio'):
                duration = self._get_media_duration(file_path)
            
            media_info = MediaFileInfo(
                file_path=file_path,
                media_type=media_type,
                mime_type=mime_type,
                file_size=file_size,
                dimensions=dimensions,
                duration=duration,
                is_demo_material=is_demo_material
            )
            
            # Cache the result
            self._media_cache[cache_key] = media_info
            
            return media_info
            
        except Exception as e:
            logger.error(f"Error categorizing media file {file_path}: {e}")
            return None
    
    def detect_git_changes(self) -> List[GitChange]:
        """
        Detect Git-related changes (tags, releases, commits).
        
        Returns:
            List of GitChange objects representing recent changes
        """
        changes = []
        
        try:
            if not self._is_git_repository():
                return changes
            
            # Check for new tags
            changes.extend(self._detect_new_tags())
            
            # Check for new commits on main branches
            changes.extend(self._detect_new_commits())
            
            return changes
            
        except Exception as e:
            logger.error(f"Error detecting Git changes: {e}")
            return changes
    
    def is_documentation_file(self, file_path: Path) -> bool:
        """Check if file is a documentation file."""
        filename = file_path.name.lower()
        
        for pattern_name, pattern in self._doc_patterns.items():
            if pattern.match(filename):
                return True
        
        # Check if in docs directory
        parts = file_path.parts
        if any(part.lower() in ('docs', 'documentation', 'doc') for part in parts):
            return file_path.suffix.lower() in {'.md', '.rst', '.txt'}
        
        return False
    
    def is_media_file(self, file_path: Path) -> bool:
        """Check if file is a media file."""
        return self._get_media_type(file_path) is not None
    
    def get_file_significance(self, file_path: Path) -> float:
        """
        Calculate the significance of a file for the project.
        
        Returns:
            Float between 0.0 and 1.0, higher means more significant
        """
        try:
            filename = file_path.name.lower()
            
            # High significance files
            if filename in ('readme.md', 'readme.txt', 'readme.rst'):
                return 1.0
            if filename in ('package.json', 'pyproject.toml', 'setup.py'):
                return 0.9
            if filename.startswith('changelog') or filename.startswith('changes'):
                return 0.8
            
            # Documentation files
            if self.is_documentation_file(file_path):
                return 0.7
            
            # Media files (especially demo materials)
            if self.is_media_file(file_path):
                if self._is_demo_material(file_path):
                    return 0.8
                return 0.5
            
            # Source code files
            if file_path.suffix in {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}:
                return 0.4
            
            # Configuration files
            if file_path.suffix in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'}:
                return 0.3
            
            return 0.1
            
        except Exception as e:
            logger.error(f"Error calculating file significance for {file_path}: {e}")
            return 0.1
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _calculate_significance(self, file_path: Path, is_new: bool = False) -> float:
        """Calculate the significance of a file change."""
        base_significance = self.get_file_significance(file_path)
        
        if is_new:
            # New files are generally more significant
            return min(1.0, base_significance * 1.2)
        
        return base_significance
    
    def _analyze_change_significance(self, file_path: Path, old_hash: str, new_hash: str) -> float:
        """Analyze the significance of a content change."""
        base_significance = self.get_file_significance(file_path)
        
        # For now, we'll use the base significance
        # In the future, we could analyze the actual content differences
        return base_significance
    
    def _determine_change_type(self, file_path: Path) -> str:
        """Determine the type of change based on file characteristics."""
        if self.is_documentation_file(file_path):
            return 'documentation'
        elif self.is_media_file(file_path):
            return 'media'
        elif file_path.suffix in {'.json', '.yaml', '.yml', '.toml'}:
            return 'metadata'
        else:
            return 'content'
    
    def _generate_change_description(self, file_path: Path, change_type: str, significance: float) -> str:
        """Generate a human-readable description of the change."""
        filename = file_path.name
        
        if significance >= 0.8:
            level = "Major"
        elif significance >= 0.5:
            level = "Moderate"
        else:
            level = "Minor"
        
        return f"{level} {change_type} change in {filename}"
    
    def _get_media_type(self, file_path: Path) -> Optional[str]:
        """Determine the media type of a file."""
        suffix = file_path.suffix.lower()
        
        for media_type, extensions in self._media_extensions.items():
            if suffix in extensions:
                return media_type
        
        return None
    
    def _is_demo_material(self, file_path: Path) -> bool:
        """Check if file appears to be demo/showcase material."""
        filename_lower = file_path.name.lower()
        path_lower = str(file_path).lower()
        
        return any(indicator in filename_lower or indicator in path_lower 
                  for indicator in self._demo_indicators)
    
    def _get_image_dimensions(self, file_path: Path) -> Optional[Tuple[int, int]]:
        """Get image dimensions if possible."""
        try:
            # Try to use PIL if available
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    return img.size
            except ImportError:
                pass
            
            # Fallback: try to parse basic formats
            return self._parse_image_dimensions_basic(file_path)
            
        except Exception as e:
            logger.debug(f"Could not get dimensions for {file_path}: {e}")
            return None
    
    def _parse_image_dimensions_basic(self, file_path: Path) -> Optional[Tuple[int, int]]:
        """Basic image dimension parsing without external libraries."""
        try:
            with open(file_path, 'rb') as f:
                # PNG format
                if file_path.suffix.lower() == '.png':
                    f.seek(16)
                    width = int.from_bytes(f.read(4), 'big')
                    height = int.from_bytes(f.read(4), 'big')
                    return (width, height)
                
                # JPEG format (simplified)
                elif file_path.suffix.lower() in ('.jpg', '.jpeg'):
                    # This is a very basic JPEG parser
                    # For production use, consider using PIL or similar
                    return None
            
        except Exception:
            pass
        
        return None
    
    def _get_media_duration(self, file_path: Path) -> Optional[float]:
        """Get media duration if possible."""
        try:
            # Try using ffprobe if available
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 
                'format=duration', '-of', 'csv=p=0', str(file_path)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                duration_str = result.stdout.strip()
                if duration_str:
                    return float(duration_str)
                    
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, ValueError):
            pass
        
        return None
    
    def _is_git_repository(self) -> bool:
        """Check if project is in a Git repository."""
        try:
            result = subprocess.run([
                'git', 'rev-parse', '--git-dir'
            ], cwd=self.project_path, capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _detect_new_tags(self) -> List[GitChange]:
        """Detect new Git tags."""
        changes = []
        
        try:
            # Get current tags
            result = subprocess.run([
                'git', 'tag', '-l', '--sort=-version:refname'
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return changes
            
            current_tags = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            cached_tags = set(self._git_refs_cache.get('tags', '').split('\n')) if self._git_refs_cache.get('tags') else set()
            
            new_tags = current_tags - cached_tags
            
            for tag in new_tags:
                if not tag:
                    continue
                
                # Get tag info
                tag_info = self._get_tag_info(tag)
                if tag_info:
                    changes.append(tag_info)
            
            # Update cache
            self._git_refs_cache['tags'] = '\n'.join(current_tags)
            
        except Exception as e:
            logger.error(f"Error detecting new tags: {e}")
        
        return changes
    
    def _detect_new_commits(self) -> List[GitChange]:
        """Detect new commits on main branches."""
        changes = []
        
        try:
            # Get recent commits on current branch
            result = subprocess.run([
                'git', 'log', '--oneline', '--since=1 hour ago', '-n', '10'
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return changes
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split(' ', 1)
                if len(parts) >= 2:
                    commit_hash = parts[0]
                    message = parts[1]
                    
                    # Get commit timestamp
                    timestamp = self._get_commit_timestamp(commit_hash)
                    
                    changes.append(GitChange(
                        change_type='commit',
                        ref_name='HEAD',
                        commit_hash=commit_hash,
                        message=message,
                        timestamp=timestamp,
                        affects_project=True
                    ))
            
        except Exception as e:
            logger.error(f"Error detecting new commits: {e}")
        
        return changes
    
    def _get_tag_info(self, tag: str) -> Optional[GitChange]:
        """Get information about a Git tag."""
        try:
            # Get tag commit hash
            result = subprocess.run([
                'git', 'rev-list', '-n', '1', tag
            ], cwd=self.project_path, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            commit_hash = result.stdout.strip()
            
            # Get tag message (if annotated)
            result = subprocess.run([
                'git', 'tag', '-l', '--format=%(contents)', tag
            ], cwd=self.project_path, capture_output=True, text=True, timeout=5)
            
            message = result.stdout.strip() if result.returncode == 0 else f"Tag {tag}"
            
            # Get commit timestamp
            timestamp = self._get_commit_timestamp(commit_hash)
            
            return GitChange(
                change_type='tag',
                ref_name=tag,
                commit_hash=commit_hash,
                message=message,
                timestamp=timestamp,
                affects_project=True
            )
            
        except Exception as e:
            logger.error(f"Error getting tag info for {tag}: {e}")
            return None
    
    def _get_commit_timestamp(self, commit_hash: str) -> datetime:
        """Get timestamp for a commit."""
        try:
            result = subprocess.run([
                'git', 'show', '-s', '--format=%ct', commit_hash
            ], cwd=self.project_path, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                timestamp = int(result.stdout.strip())
                return datetime.fromtimestamp(timestamp)
                
        except Exception as e:
            logger.error(f"Error getting commit timestamp for {commit_hash}: {e}")
        
        return datetime.now()