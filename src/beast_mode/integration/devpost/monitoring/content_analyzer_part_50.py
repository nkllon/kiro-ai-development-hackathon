from datetime import datetime
from typing import Dict, List, Any

def _analyze_documentation_change(self, file_path: Path, previous_hash: Optional[str], current_hash: str) -> bool:
    """Analyze if documentation change is significant."""
    if not previous_hash:
        return True
    if previous_hash == current_hash:
        return False
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        significant_indicators = ['#\\s+.*', '\\*\\*.*\\*\\*', '!\\[.*\\]\\(.*\\)', '\\[.*\\]\\(.*\\)', '```.*```', '- \\w+', '\\d+\\.\\s+\\w+']
        significant_lines = 0
        total_lines = len(content.splitlines())
        for line in content.splitlines():
            line = line.strip()
            if line and any((re.search(pattern, line) for pattern in significant_indicators)):
                significant_lines += 1
        if total_lines > 0:
            significant_ratio = significant_lines / total_lines
            return significant_ratio > 0.1
        return True
    except Exception as e:
        logger.error(f'Error analyzing documentation change for {file_path}: {e}')
        return True
