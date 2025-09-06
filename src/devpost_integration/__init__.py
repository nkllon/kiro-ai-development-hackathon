"""
Devpost Integration Package

Multi-target implementation:
- Hackathon submission demo
- Kiro AI systematic development showcase  
- TiDB-scale architecture example

The Requirements ARE the Solution.
"""

__version__ = "0.1.0"

from .cli import cli
from .project_manager import DevpostProjectManager
from .sync_manager import DevpostSyncManager
from .preview_generator import DevpostPreviewGenerator

__all__ = [
    'cli',
    'DevpostProjectManager', 
    'DevpostSyncManager',
    'DevpostPreviewGenerator'
]