"""Configuration management interface definitions.

This module contains interfaces related to configuration management,
focusing solely on configuration loading and validation contracts.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ConfigManagerInterface(ABC):
    """Interface for configuration management.
    
    Defines the contract for loading, validating, and accessing
    configuration data from various sources.
    """
    
    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from all sources.
        
        Returns:
            Merged configuration dictionary
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration against schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        pass