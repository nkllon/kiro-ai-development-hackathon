from datetime import datetime
from typing import Dict, List, Any

def __init__(self) -> Any:
    self.logger = logging.getLogger(__name__)
    self.alert_rules: Dict[str, AlertRule] = {}
    self.active_alerts: Dict[str, Alert] = {}
    self.alert_history: List[Alert] = []
    self.last_evaluation: Dict[str, datetime] = {}
    self.last_alert_time: Dict[str, datetime] = {}
    self.alerting_active = False
    self.alerting_task: Optional[asyncio.Task] = None
    self.alert_handlers: List[Callable] = []
