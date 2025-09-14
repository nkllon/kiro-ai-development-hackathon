from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, auto_merge: bool = False, auto_revert_on_failure: bool = False):
        self.task_manager = TaskManager()
        self.agent_manager = AgentManager()
        self.git_session: Optional[GitSession] = None
        self.auto_merge = auto_merge
        self.auto_revert_on_failure = auto_revert_on_failure
        self.logger = logging.getLogger(__name__)
    