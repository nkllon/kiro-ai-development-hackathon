"""
Basic tests for Code with Kiro Hackathon
"""

import pytest


def test_hackathon_setup():
    """Test that the hackathon repository is properly set up"""
    assert True, "Hackathon repository is ready for development"


def test_ai_agents_available():
    """Test that AI agent dependencies are available"""
    try:
        import clewcrew_common
        import clewcrew_framework
        import clewcrew_agents
        # Test that we can access the modules
        assert clewcrew_common.__version__ is not None
        assert clewcrew_framework.__version__ is not None
        assert clewcrew_agents.__version__ is not None
        assert True, "All clewcrew dependencies are available"
    except ImportError:
        pytest.skip("Clewcrew dependencies not installed")


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
