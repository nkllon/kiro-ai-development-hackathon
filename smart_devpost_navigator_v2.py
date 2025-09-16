#!/usr/bin/env python3
"""
Smart DevPost Navigator V2 - RDI Compliant
==========================================

REFACTORED: Split from 757 lines to 200 lines for RDI compliance.
Main functionality moved to src/navigator_consolidated/ modules.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: RDI compliant wrapper for consolidated navigator modules
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.navigator_consolidated.core_navigator import SmartDevPostNavigatorV2 as CoreNavigator


class SmartDevPostNavigatorV2:
    """RDI Compliant wrapper for Smart DevPost Navigator V2."""

    def __init__(self):
        """Initialize with core navigator."""
        self.core_navigator = CoreNavigator()

    def start_navigation(self, base_url: str, project_data: dict = None):
        """Start intelligent navigation through DevPost submission."""
        return self.core_navigator.start_navigation(base_url, project_data)

    # Delegate all other methods to core navigator
    def __getattr__(self, name):
        """Delegate unknown methods to core navigator."""
        return getattr(self.core_navigator, name)


def main():
    """Main function - RDI compliant wrapper."""
    print("🧠 Smart DevPost Navigator V2 - RDI Compliant")
    print("=" * 50)

    # Load project data
    try:
        with open("sample_project_data.json", "r") as f:
            project_data = json.load(f)
        print(f"📊 Loaded project data: {len(project_data)} fields")
    except Exception as e:
        print(f"⚠️ Could not load project data: {e}")
        project_data = {}

    # Start navigation
    base_url = "https://devpost.com/submit-to/25444-code-with-kiro-hackathon/manage/submissions/784734-untitled/project-overview"

    navigator = SmartDevPostNavigatorV2()
    navigator.start_navigation(base_url, project_data)


if __name__ == "__main__":
    main()

