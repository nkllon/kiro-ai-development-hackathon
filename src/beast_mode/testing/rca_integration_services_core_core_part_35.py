from src.rm_ddd.core.health import ModuleHealth

def _extract_error_pattern(self, error_message: str) -> str:
    """Extract error pattern from error message"""
    pattern = error_message.lower()
    pattern = re.sub('/[^\\s]+', '<path>', pattern)
    pattern = re.sub('line \\d+', 'line <num>', pattern)
    pattern = re.sub('\\d+', '<num>', pattern)
    pattern = re.sub("'[^']*'", '<value>', pattern)
    pattern = re.sub('"[^"]*"', '<value>', pattern)
    return pattern
