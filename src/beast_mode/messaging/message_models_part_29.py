from datetime import datetime
from typing import Dict, List, Any

    def validate_content(cls, v) -> Any:
        """Validate message content is serializable."""
        try:
            json.dumps(v)
            return v
        except (TypeError, ValueError) as e:
            raise ValueError(f'Message content must be JSON serializable: {str(e)}')
