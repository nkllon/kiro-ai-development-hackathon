"""
Manager Processing

This module was extracted from manager.py
as part of RM-DDD compliance refactoring.
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from ..models import DevpostProject, ProjectMetadata, DevpostConfig, ProjectConnection, SyncStatus, ValidationResult
from ..interfaces import ProjectManagerInterface
from ..config import DevpostConfigManager
from ....core.exceptions import ConfigurationError, ValidationError
import tomllib
import tomli as tomllib
from src.rm_ddd.core.health import ModuleHealth


def _parse_readme_content(self, content: str, path: Path) -> Dict[str, Any]:
    """Parse README content to extract metadata."""
    lines = content.split('\n')
    metadata = {'path': path}
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            metadata['title'] = line[2:].strip()
            break
        elif line.startswith('=') and len(line) > 3:
            prev_idx = lines.index(line) - 1
            if prev_idx >= 0:
                metadata['title'] = lines[prev_idx].strip()
            break
    title_found = False
    description_lines = []
    in_description_section = False
    for i, line in enumerate(lines):
        line = line.strip()
        if not title_found:
            if line.startswith('# ') or (line.startswith('=') and len(line) > 3):
                title_found = True
            continue
        if line.lower().startswith('## description'):
            in_description_section = True
            continue
        if line.startswith('##') and (not line.lower().startswith('## description')):
            if in_description_section:
                break
            continue
        if line:
            description_lines.append(line)
        elif in_description_section and (not line):
            continue
    if description_lines:
        full_description = ' '.join(description_lines)
        sentences = re.split('[.!?]+', full_description)
        if sentences and sentences[0].strip():
            metadata['tagline'] = sentences[0].strip()
        metadata['description'] = full_description
    return metadata
