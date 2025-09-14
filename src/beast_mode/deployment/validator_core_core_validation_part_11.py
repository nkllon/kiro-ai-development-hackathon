from src.rm_ddd.core.health import ModuleHealth

def _check_dns_resolution(self, hostname: str, name: str) -> ValidationResult:
    """Check DNS resolution"""
    start_time = time.time()
    try:
        socket.gethostbyname(hostname)
        duration_ms = (time.time() - start_time) * 1000
        return ValidationResult(name=name, passed=True, message=f'DNS resolution successful for {hostname}', duration_ms=duration_ms)
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return ValidationResult(name=name, passed=False, message=f'DNS resolution failed for {hostname}: {str(e)}', duration_ms=duration_ms)
