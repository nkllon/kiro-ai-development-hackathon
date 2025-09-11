"""
Hackathon Demo Framework

A systematic approach to hackathon submission readiness and demo presentation excellence.
Integrates with Beast Mode framework to demonstrate systematic development principles
while maximizing hackathon success probability.
"""

from .controller import HackathonDemoController
from .models import (
    HackathonConfig,
    JudgingCriterion,
    DemoPackage,
    DemoScript,
    JudgeMaterials
)

__version__ = "1.0.0"
__all__ = [
    "HackathonDemoController",
    "HackathonConfig", 
    "JudgingCriterion",
    "DemoPackage",
    "DemoScript",
    "JudgeMaterials"
]