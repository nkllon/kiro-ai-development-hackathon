from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self) -> Any:
        self.agents: Dict[str, Agent] = {}
        self.logger = logging.getLogger(__name__)
    