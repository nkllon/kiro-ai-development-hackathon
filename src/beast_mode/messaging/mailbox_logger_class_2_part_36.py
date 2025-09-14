from src.rm_ddd.core.registry import register_module

def _write_to_file(self, log_line: str) -> None:
    """Synchronous file write operation"""
    if self.current_log_handle:
        self.current_log_handle.write(log_line)
        self.current_log_handle.flush()
