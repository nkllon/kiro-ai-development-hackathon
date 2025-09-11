"""
Devpost Integration Package

Multi-target implementation:
- Hackathon submission demo
- Kiro AI systematic development showcase  
- TiDB-scale architecture example

The Requirements ARE the Solution.
"""

__version__ = "0.1.0"

from .project_manager import DevpostProjectManager
from .sync_manager import DevpostSyncManager
from .preview_generator import DevpostPreviewGenerator
from .api_client import DevPostAPIClient
from .auth_service import DevPostAuthService
from .config import DevpostConfig

__all__ = [
    'DevpostProjectManager', 
    'DevpostSyncManager',
    'DevpostPreviewGenerator',
    'DevPostAPIClient',
    'DevPostAuthService',
    'DevpostConfig'
]