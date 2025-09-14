from datetime import datetime
from typing import Dict, List, Any

    def validate_message_format(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate message format using the router.
        
        Args:
            message_data: Raw message data
            
        Returns:
            Validation result
        """
        if self.message_router:
            return self.message_router.validate_message_compatibility(message_data)
        try:
            BeastModeMessage(**message_data)
            return {'is_valid': True, 'is_legacy': False, 'errors': []}
        except Exception as e:
            return {'is_valid': False, 'is_legacy': False, 'errors': [str(e)]}
