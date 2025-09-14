from datetime import datetime
from typing import Dict, List, Any

def _write_to_file(self, log_line: str) -> None:
    """Synchronous file write operation"""
    if self.current_log_handle:
        self.current_log_handle.write(log_line)
        self.current_log_handle.flush()
