"""
Packer Systo - Systematic improvements for HashiCorp Packer

This package provides systematic improvements to HashiCorp Packer through:
- Intelligent delusion detection and pattern recognition
- Automatic recovery engines for common build failures
- Multi-dimensional validation with confidence scoring
- Enhanced error messages and diagnostics
- Systematic build optimization and caching

The package applies Beast Mode Framework principles to make Packer
easier to understand, leverage, and use for all skill levels.
"""

__version__ = "0.1.0"
__author__ = "Packer Systo Team"
__email__ = "team@packer-systo.dev"
__license__ = "MIT"

# Core API exports
from .core.api import PackerSysto
from .core.config import PackerConfig, SystoConfig
from .core.models import (
    AnalysisResult,
    BuildResult,
    DelusionPattern,
    ValidationCertificate,
    ValidationReport,
)
from .core.exceptions import (
    PackerSystoError,
    DelusionDetectionError,
    RecoveryEngineError,
    ValidationError,
)

# CLI exports
from .cli.main import main as cli_main

# Integration exports
from .integrations.ansible import AnsiblePackerModule
from .integrations.fabric import FabricTaskCollection
from .integrations.cicd import CICDPlugin

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Core API
    "PackerSysto",
    "PackerConfig", 
    "SystoConfig",
    
    # Models
    "AnalysisResult",
    "BuildResult",
    "DelusionPattern",
    "ValidationCertificate",
    "ValidationReport",
    
    # Exceptions
    "PackerSystoError",
    "DelusionDetectionError", 
    "RecoveryEngineError",
    "ValidationError",
    
    # CLI
    "cli_main",
    
    # Integrations
    "AnsiblePackerModule",
    "FabricTaskCollection",
    "CICDPlugin",
]

# Package metadata for systematic tracking
PACKAGE_INFO = {
    "name": "packer-systo",
    "version": __version__,
    "description": "Systematic improvements for HashiCorp Packer",
    "features": [
        "delusion_detection",
        "recovery_engine", 
        "multi_dimensional_validation",
        "systematic_diagnostics",
        "performance_optimization",
        "security_validation",
        "ecosystem_integration",
    ],
    "supported_python": ["3.9", "3.10", "3.11", "3.12"],
    "beast_mode_compatible": True,
    "ghostbusters_integration": True,
}

def get_package_info() -> dict:
    """Get comprehensive package information for systematic tracking."""
    return PACKAGE_INFO.copy()

def get_version() -> str:
    """Get the current package version."""
    return __version__

def get_features() -> list[str]:
    """Get list of available features."""
    return PACKAGE_INFO["features"].copy()

# Systematic initialization
def _initialize_systematic_logging():
    """Initialize systematic logging for the package."""
    import logging
    import structlog
    
    # Configure structured logging for systematic observability
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Initialize systematic components
_initialize_systematic_logging()

# Systematic compatibility check
def _check_systematic_compatibility():
    """Check compatibility with Beast Mode Framework and Ghostbusters."""
    import sys
    
    # Check Python version compatibility
    if sys.version_info < (3, 9):
        raise RuntimeError(
            f"Packer Systo requires Python 3.9 or higher. "
            f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
        )
    
    # Check for optional systematic dependencies
    try:
        import structlog
        import rich
        import pydantic
    except ImportError as e:
        raise RuntimeError(
            f"Missing required systematic dependency: {e.name}. "
            f"Please install with: pip install packer-systo[all]"
        )

# Perform compatibility check on import
_check_systematic_compatibility()

# Systematic banner for CLI usage
SYSTEMATIC_BANNER = """
🐺 Packer Systo - Systematic Packer Improvements 🚀

Beast Mode Framework Principles:
• NO BLAME. ONLY LEARNING AND FIXING.
• SYSTEMATIC COLLABORATION ENGAGED
• EVERYONE WINS with systematic approaches

Features:
• 🧠 Intelligent delusion detection
• 🛠️  Automatic recovery engines  
• 📊 Multi-dimensional validation
• ⚡ Performance optimization
• 🛡️  Security validation
• 🔄 Ecosystem integration

Version: {version}
Ready for systematic domination! 💪
""".format(version=__version__)

def print_banner():
    """Print the systematic banner for CLI usage."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        console.print(Panel(SYSTEMATIC_BANNER, title="🐺 Systo Ready! 🐺", border_style="bold green"))
    except ImportError:
        print(SYSTEMATIC_BANNER)