#!/usr/bin/env python3
"""
Test Scenarios - Test scenario definitions
=========================================

Extracted from sophisticated_indirect_verification.py for RDI compliance.
Contains test scenario definitions for verification.
"""

from typing import Any, Dict, List


def create_test_scenarios() -> List[Dict[str, Any]]:
    """Create test scenarios for verification"""
    return [
        {
            "name": "Low Confidence Scenario",
            "initial_state": {
                "session_recovery": {
                    "confidence": 0.15,
                    "similarity_type": "unknown",
                },
                "session_save_data": {
                    "current_page_data": {
                        "url": "https://devpost.com/test1",
                        "title": "Test Page 1",
                        "pageText": "This is test page 1",
                        "navigation": [{"text": "Submit", "type": "submit"}],
                        "buttons": [{"text": "Submit", "type": "submit"}],
                    }
                },
            },
        },
        {
            "name": "Medium Confidence Scenario",
            "initial_state": {
                "session_recovery": {
                    "confidence": 0.25,
                    "similarity_type": "devpost_known",
                },
                "session_save_data": {
                    "current_page_data": {
                        "url": "https://devpost.com/test2",
                        "title": "Test Page 2",
                        "pageText": "This is test page 2 with more content",
                        "navigation": [
                            {"text": "Submit", "type": "submit"},
                            {"text": "Cancel", "type": "button"},
                        ],
                        "buttons": [
                            {"text": "Submit", "type": "submit"},
                            {"text": "Cancel", "type": "button"},
                        ],
                    }
                },
            },
        },
        {
            "name": "High Confidence Scenario",
            "initial_state": {
                "session_recovery": {
                    "confidence": 0.35,
                    "similarity_type": "exact",
                },
                "session_save_data": {
                    "current_page_data": {
                        "url": "https://devpost.com/test3",
                        "title": "Test Page 3",
                        "pageText": "This is test page 3 with comprehensive content for testing",
                        "navigation": [
                            {"text": "Submit", "type": "submit"},
                            {"text": "Save", "type": "button"},
                            {"text": "Cancel", "type": "button"},
                        ],
                        "buttons": [
                            {"text": "Submit", "type": "submit"},
                            {"text": "Save", "type": "button"},
                            {"text": "Cancel", "type": "button"},
                        ],
                    }
                },
            },
        },
    ]
