#!/usr/bin/env python3
"""
Change Detector - Intelligent change detection and analysis

Extracted from file_monitor.py for RM-DDD compliance.
Single responsibility: Content-based change detection and analysis.
"""

import hashlib
import logging
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from .models import FileChangeEvent, ChangeType, ContentType, MediaType, MediaFile

logger = logging.getLogger(__name__)


class ContentBasedChangeDetector:
    """
    Intelligent change detection based on file content analysis.
    
    Analyzes file changes to determine significance, categorizes content,
    and provides intelligent filtering for relevant modifications.
    """
    
    def __init__(self):
        """Initialize content-based change detector."""
        self.content_patterns = self._initialize_content_patterns()
        self.media_extensions = self._initialize_media_extensions()
        self.code_keywords = self._initialize_code_keywords()
        
        # Change significance thresholds
        self.significance_thresholds = {
            'code': 0.1,      # 10% change in code files
            'documentation': 0.05,  # 5% change in docs
            'media': 0.0,     # Any media change is significant
            'config': 0.01,   # 1% change in config files
            'other': 0.2      # 20% change in other files
        }
    
    def _initialize_content_patterns(self) -> Dict[str, List[str]]:
        """Initialize content detection patterns."""
        return {
            'code': [
                r'def\s+\w+',           # Function definitions
                r'class\s+\w+',         # Class definitions
                r'import\s+\w+',        # Import statements
                r'from\s+\w+\s+import', # From imports
                r'#.*TODO|FIXME|HACK',  # Code comments
                r'if\s+__name__',       # Main blocks
            ],
            'documentation': [
                r'#+\s+',               # Markdown headers
                r'\*\*.*\*\*',          # Bold text
                r'\*.*\*',              # Italic text
                r'```',                 # Code blocks
                r'\[.*\]\(.*\)',        # Links
                r'!\[.*\]\(.*\)',       # Images
            ],
            'config': [
                r'^\s*\w+\s*=',        # Key-value pairs
                r'^\s*\[.*\]',         # INI sections
                r'^\s*-\s*\w+:',       # YAML lists
                r'^\s*\w+:',           # YAML keys
            ]
        }
    
    def _initialize_media_extensions(self) -> Set[str]:
        """Initialize media file extensions."""
        return {
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp', '.tiff',
            '.mp4', '.avi', '.mov', '.webm', '.mkv', '.flv',
            '.mp3', '.wav', '.flac', '.aac', '.ogg',
            '.pdf', '.doc', '.docx', '.ppt', '.pptx'
        }
    
    def _initialize_code_keywords(self) -> Set[str]:
        """Initialize important code keywords."""
        return {
            'def', 'class', 'import', 'from', 'if', 'for', 'while',
            'try', 'except', 'finally', 'with', 'async', 'await',
            'return', 'yield', 'raise', 'assert', 'pass', 'break',
            'continue', 'lambda', 'global', 'nonlocal'
        }
    
    def analyze_change_significance(self, event: FileChangeEvent) -> Tuple[bool, float]:
        """
        Analyze the significance of a file change.
        
        Args:
            event: File change event to analyze
            
        Returns:
            Tuple of (is_significant, significance_score)
        """
        if not event.file_path.exists():
            # File was deleted - always significant
            return True, 1.0
        
        try:
            # Read current file content
            with open(event.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
            
            # Detect content type
            content_type = self._detect_detailed_content_type(event.file_path, current_content)
            
            # Calculate significance based on content type
            if content_type == 'media':
                return True, 1.0  # Media changes are always significant
            
            # For text-based files, analyze content changes
            significance_score = self._calculate_content_significance(
                current_content, content_type
            )
            
            threshold = self.significance_thresholds.get(content_type, 0.2)
            is_significant = significance_score >= threshold
            
            return is_significant, significance_score
            
        except Exception as e:
            logger.error(f"Error analyzing change significance: {e}")
            return False, 0.0
    
    def _detect_detailed_content_type(self, file_path: Path, content: str) -> str:
        """Detect detailed content type based on file and content analysis."""
        suffix = file_path.suffix.lower()
        
        # Check for media files
        if suffix in self.media_extensions:
            return 'media'
        
        # Check for code files
        if suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
            return 'code'
        
        # Check for documentation
        if suffix in ['.md', '.rst', '.txt', '.adoc']:
            return 'documentation'
        
        # Check for configuration files
        if suffix in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
            return 'config'
        
        # Analyze content for patterns
        if self._has_code_patterns(content):
            return 'code'
        elif self._has_documentation_patterns(content):
            return 'documentation'
        elif self._has_config_patterns(content):
            return 'config'
        
        return 'other'
    
    def _has_code_patterns(self, content: str) -> bool:
        """Check if content has code patterns."""
        for pattern in self.content_patterns['code']:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False
    
    def _has_documentation_patterns(self, content: str) -> bool:
        """Check if content has documentation patterns."""
        for pattern in self.content_patterns['documentation']:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False
    
    def _has_config_patterns(self, content: str) -> bool:
        """Check if content has configuration patterns."""
        for pattern in self.content_patterns['config']:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False
    
    def _calculate_content_significance(self, content: str, content_type: str) -> float:
        """Calculate significance score based on content analysis."""
        if not content:
            return 0.0
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        if total_lines == 0:
            return 0.0
        
        # Count significant lines based on content type
        significant_lines = 0
        
        if content_type == 'code':
            significant_lines = self._count_significant_code_lines(lines)
        elif content_type == 'documentation':
            significant_lines = self._count_significant_doc_lines(lines)
        elif content_type == 'config':
            significant_lines = self._count_significant_config_lines(lines)
        else:
            # For other types, count non-empty lines
            significant_lines = sum(1 for line in lines if line.strip())
        
        return significant_lines / total_lines
    
    def _count_significant_code_lines(self, lines: List[str]) -> int:
        """Count significant lines in code files."""
        count = 0
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check for important code constructs
            if any(keyword in stripped for keyword in self.code_keywords):
                count += 1
            elif re.match(r'^\s*\w+\s*=', stripped):  # Variable assignments
                count += 1
            elif re.match(r'^\s*[{}]', stripped):  # Braces
                count += 1
        
        return count
    
    def _count_significant_doc_lines(self, lines: List[str]) -> int:
        """Count significant lines in documentation files."""
        count = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for documentation patterns
            if re.match(r'^#+\s+', stripped):  # Headers
                count += 1
            elif re.search(r'\*\*.*\*\*|\*.*\*', stripped):  # Bold/italic
                count += 1
            elif re.search(r'\[.*\]\(.*\)', stripped):  # Links
                count += 1
            elif re.search(r'```', stripped):  # Code blocks
                count += 1
            elif len(stripped) > 20:  # Substantial content
                count += 1
        
        return count
    
    def _count_significant_config_lines(self, lines: List[str]) -> int:
        """Count significant lines in configuration files."""
        count = 0
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check for configuration patterns
            if re.match(r'^\s*\w+\s*=', stripped):  # Key-value pairs
                count += 1
            elif re.match(r'^\s*\[.*\]', stripped):  # INI sections
                count += 1
            elif re.match(r'^\s*-\s*\w+:', stripped):  # YAML lists
                count += 1
            elif re.match(r'^\s*\w+:', stripped):  # YAML keys
                count += 1
        
        return count
    
    def categorize_change(self, event: FileChangeEvent) -> Dict[str, Any]:
        """
        Categorize file change event with detailed analysis.
        
        Args:
            event: File change event to categorize
            
        Returns:
            Dictionary with categorization details
        """
        categorization = {
            'content_type': event.content_type.value if event.content_type else 'unknown',
            'change_type': event.change_type.value,
            'is_significant': False,
            'significance_score': 0.0,
            'file_size': 0,
            'is_media': False,
            'is_code': False,
            'is_documentation': False,
            'is_config': False,
            'has_structural_changes': False,
            'recommended_action': 'monitor'
        }
        
        if not event.file_path.exists():
            categorization['recommended_action'] = 'cleanup'
            return categorization
        
        try:
            # Get file size
            categorization['file_size'] = event.file_path.stat().st_size
            
            # Analyze significance
            is_significant, significance_score = self.analyze_change_significance(event)
            categorization['is_significant'] = is_significant
            categorization['significance_score'] = significance_score
            
            # Detect content type
            with open(event.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            detailed_type = self._detect_detailed_content_type(event.file_path, content)
            categorization['is_media'] = detailed_type == 'media'
            categorization['is_code'] = detailed_type == 'code'
            categorization['is_documentation'] = detailed_type == 'documentation'
            categorization['is_config'] = detailed_type == 'config'
            
            # Check for structural changes
            categorization['has_structural_changes'] = self._has_structural_changes(content, detailed_type)
            
            # Recommend action based on analysis
            if categorization['is_media']:
                categorization['recommended_action'] = 'sync_immediately'
            elif categorization['is_code'] and is_significant:
                categorization['recommended_action'] = 'sync_and_validate'
            elif categorization['is_config'] and is_significant:
                categorization['recommended_action'] = 'sync_and_validate'
            elif is_significant:
                categorization['recommended_action'] = 'sync'
            else:
                categorization['recommended_action'] = 'monitor'
                
        except Exception as e:
            logger.error(f"Error categorizing change: {e}")
            categorization['recommended_action'] = 'error'
        
        return categorization
    
    def _has_structural_changes(self, content: str, content_type: str) -> bool:
        """Check if content has structural changes."""
        if content_type == 'code':
            # Check for function/class definitions
            return bool(re.search(r'def\s+\w+|class\s+\w+', content))
        elif content_type == 'documentation':
            # Check for headers and structure
            return bool(re.search(r'^#+\s+', content, re.MULTILINE))
        elif content_type == 'config':
            # Check for section headers
            return bool(re.search(r'^\s*\[.*\]', content, re.MULTILINE))
        
        return False
    
    def get_change_summary(self, events: List[FileChangeEvent]) -> Dict[str, Any]:
        """
        Get summary of multiple change events.
        
        Args:
            events: List of file change events
            
        Returns:
            Dictionary with change summary
        """
        summary = {
            'total_changes': len(events),
            'significant_changes': 0,
            'content_types': {},
            'change_types': {},
            'recommended_actions': {},
            'average_significance': 0.0
        }
        
        significance_scores = []
        
        for event in events:
            categorization = self.categorize_change(event)
            
            if categorization['is_significant']:
                summary['significant_changes'] += 1
            
            # Count content types
            content_type = categorization['content_type']
            summary['content_types'][content_type] = summary['content_types'].get(content_type, 0) + 1
            
            # Count change types
            change_type = categorization['change_type']
            summary['change_types'][change_type] = summary['change_types'].get(change_type, 0) + 1
            
            # Count recommended actions
            action = categorization['recommended_action']
            summary['recommended_actions'][action] = summary['recommended_actions'].get(action, 0) + 1
            
            # Collect significance scores
            significance_scores.append(categorization['significance_score'])
        
        # Calculate average significance
        if significance_scores:
            summary['average_significance'] = sum(significance_scores) / len(significance_scores)
        
        return summary
