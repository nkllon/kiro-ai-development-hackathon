"""Authentication interface definitions.

This module contains interfaces related to authentication and authorization,
focusing solely on OAuth 2.0 and credential management contracts.
"""

from abc import ABC, abstractmethod
from typing import Optional


class AuthManagerInterface(ABC):
    """Interface for authentication managers.
    
    Defines the contract for OAuth 2.0 authentication management
    including token lifecycle and credential handling.
    """
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Perform authentication flow.
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        pass
    
    @abstractmethod
    def get_access_token(self) -> Optional[str]:
        """Get current access token.
        
        Returns:
            Access token if available, None otherwise
        """
        pass
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """Refresh the access token.
        
        Returns:
            True if refresh successful, False otherwise
        """
        pass