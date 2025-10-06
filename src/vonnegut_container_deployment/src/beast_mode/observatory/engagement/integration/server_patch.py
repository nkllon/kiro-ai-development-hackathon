"""
Observatory Server Patch - Integration Helper
============================================

Helper script to patch the Observatory server with engagement features.
This can be imported and used to add engagement capabilities to the existing server.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def patch_observatory_server(server_instance, enable_engagement: bool = True):
    """
    Patch an existing Observatory server instance with engagement features.
    
    Args:
        server_instance: The ObservatoryServer instance to patch
        enable_engagement: Whether to enable engagement features
    """
    
    if not enable_engagement:
        logger.info("🎯 Engagement features disabled")
        return None
    
    try:
        from .server_integration import add_engagement_endpoints
        
        # Add engagement endpoints to the server's FastAPI app
        engagement_integration = add_engagement_endpoints(
            server_instance.app, 
            server_instance.config
        )
        
        # Store reference in server instance for access
        server_instance.engagement_integration = engagement_integration
        
        logger.info("✅ Observatory server patched with engagement features")
        return engagement_integration
        
    except Exception as e:
        logger.error(f"❌ Failed to patch Observatory server with engagement: {e}")
        return None


def get_engagement_integration(server_instance) -> Optional[object]:
    """Get the engagement integration from a patched server instance."""
    return getattr(server_instance, 'engagement_integration', None)


# Auto-patch function that can be called during server initialization
def auto_patch_if_enabled(server_instance):
    """
    Automatically patch the server if engagement is enabled in config.
    
    This function checks the server config and automatically applies
    engagement features if they're enabled.
    """
    try:
        # Check if engagement is enabled in config
        engagement_enabled = getattr(
            server_instance.config, 
            'engagement_enabled', 
            True  # Default to enabled
        )
        
        if engagement_enabled:
            return patch_observatory_server(server_instance, True)
        else:
            logger.info("🎯 Engagement features disabled in configuration")
            return None
            
    except Exception as e:
        logger.warning(f"⚠️ Could not determine engagement configuration: {e}")
        # Default to trying to enable engagement
        return patch_observatory_server(server_instance, True)