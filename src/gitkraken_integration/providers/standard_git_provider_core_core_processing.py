"""
Standard Git Provider Core Core Processing

This module was extracted from standard_git_provider_core_core.py
as part of RM-DDD compliance refactoring.
"""

import subprocess
import json
import re
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from .git_provider import GitProvider, GitOperationResult, GitOperationStatus, BranchInfo, CommitInfo, FileStatus, MergeConflict
from src.rm_ddd.core.health import ModuleHealth


class ParsestatusoutputClass:
    """Auto-generated class for functions."""

    def _parse_status_output(self, output: str) -> List[FileStatus]:
    """Parse git status --porcelain output into FileStatus objects"""
    files = []
    for line in output.strip().split('\n'):
    if not line:
    continue
    if len(line) < 3:
    continue
    index_status = line[0]
    working_tree_status = line[1]
    file_path = line[3:]
    if index_status == '?' and working_tree_status == '?':
    status = '??'
    staged = False
    elif index_status != ' ':
    status = index_status
    staged = True
    else:
    status = working_tree_status
    staged = False
    files.append(FileStatus(path=file_path, status=status, staged=staged, working_tree_status=working_tree_status, index_status=index_status))
    return files

    def _parse_branch_output(self, output: str) -> List[BranchInfo]:
    """Parse git branch output into BranchInfo objects"""
    branches = []
    for line in output.strip().split('\n'):
    if not line.strip():
    continue
    is_current = line.startswith('*')
    line = line[2:] if is_current else line[2:]
    parts = line.split()
    if len(parts) < 2:
    continue
    branch_name = parts[0]
    commit_hash = parts[1]
    tracking_branch = None
    if '[' in line and ']' in line:
    tracking_match = re.search('\\[([^\\]]+)\\]', line)
    if tracking_match:
    tracking_info = tracking_match.group(1)
    if ':' in tracking_info:
    tracking_branch = tracking_info.split(':')[0]
    else:
    tracking_branch = tracking_info
    commit_message = ''
    bracket_end = line.find(']')
    if bracket_end != -1:
    commit_message = line[bracket_end + 1:].strip()
    else:
    message_start = line.find(commit_hash) + len(commit_hash)
    commit_message = line[message_start:].strip()
    commit_date, commit_author = self._get_commit_details(commit_hash)
    ahead_behind = self._get_ahead_behind_counts(branch_name) if is_current else {'ahead': 0, 'behind': 0}
    branches.append(BranchInfo(name=branch_name, is_current=is_current, ahead_count=ahead_behind['ahead'], behind_count=ahead_behind['behind'], last_commit_hash=commit_hash, last_commit_message=commit_message, last_commit_date=commit_date, last_commit_author=commit_author, tracking_branch=tracking_branch))
    return branches

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

