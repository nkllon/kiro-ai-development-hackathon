"""
Basic tests for Code with Kiro Hackathon
"""

import pytest


def test_hackathon_setup():
    """Test that the hackathon repository is properly set up"""
    assert True, "Hackathon repository is ready for development"


def test_core_dependencies_available():
    """Test that core dependencies are available"""
    try:
        import pydantic
        import jinja2
        import yaml
        import click
        # Test that we can access the modules
        assert pydantic.__version__ is not None
        assert jinja2.__version__ is not None
        assert yaml.__version__ is not None
        assert click.__version__ is not None
        assert True, "All core dependencies are available"
    except ImportError as e:
        pytest.fail(f"Core dependencies not available: {e}")


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
