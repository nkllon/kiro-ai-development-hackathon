from src.rm_ddd.core.health import ModuleHealth

def _check_process_running(self, process_name: str) -> ValidationResult:
    """Check if a process is running"""
    start_time = time.time()
    try:
        result = subprocess.run(['pgrep', '-f', process_name], capture_output=True, text=True)
        duration_ms = (time.time() - start_time) * 1000
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return ValidationResult(name=f'Process running: {process_name}', passed=True, message=f"Process {process_name} is running (PIDs: {', '.join(pids)})", duration_ms=duration_ms, details={'pids': pids})
        else:
            return ValidationResult(name=f'Process running: {process_name}', passed=False, message=f'Process {process_name} is not running', duration_ms=duration_ms)
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return ValidationResult(name=f'Process running: {process_name}', passed=False, message=f'Process check failed: {str(e)}', duration_ms=duration_ms)
