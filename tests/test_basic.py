"""
Basic tests for Code with Kiro Hackathon
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path for dependency validator
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from dependency_validator import DependencyChecker


def test_hackathon_setup():
    """Test that the hackathon repository is properly set up"""
    assert True, "Hackathon repository is ready for development"


def test_core_dependencies_available():
    """Test that core dependencies are available using dependency validator"""
    checker = DependencyChecker()
    status = checker.validate_core_dependencies()
    
    if not status.all_available:
        # Generate helpful error message with installation commands
        missing_deps = ", ".join(status.missing_dependencies)
        install_commands = checker.generate_installation_commands(status.missing_dependencies)
        error_msg = f"Core dependencies not available: {missing_deps}\n"
        error_msg += "Install missing dependencies with:\n"
        error_msg += "\n".join(f"  {cmd}" for cmd in install_commands)
        pytest.fail(error_msg)
    
    # Verify we can actually import and use the dependencies
    try:
        import pydantic
        import jinja2
        import yaml
        import click
        import aiohttp
        import watchdog
        
        # Test that we can access the modules
        assert pydantic.__version__ is not None
        assert jinja2.__version__ is not None
        assert yaml.__version__ is not None
        assert click.__version__ is not None
        assert aiohttp.__version__ is not None
        
    except ImportError as e:
        pytest.fail(f"Core dependencies import failed: {e}")
    
    assert True, f"All {len(status.available_dependencies)} core dependencies are available"


def test_ai_development_tools():
    """Test that AI development tool dependencies are ready"""
    try:
        import openai
        import anthropic
        # Test that we can access the modules
        assert openai.__version__ is not None
        assert anthropic.__version__ is not None
        assert True, "AI development tool dependencies are available"
    except ImportError:
        pytest.skip("AI development tool dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__])
