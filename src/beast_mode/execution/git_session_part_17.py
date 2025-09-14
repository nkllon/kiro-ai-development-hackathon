from datetime import datetime
from typing import Dict, List, Any

    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch
        self.branch_name: Optional[str] = None
        self.changes_made = False
        self.logger = logging.getLogger(__name__)
    