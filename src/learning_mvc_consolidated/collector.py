#!/usr/bin/env python3
"""
🎯 TELEMETRY COLLECTOR MODULE
============================
Telemetry collection for Learning MVC System.
Extracted from learning_mvc_system.py for better organization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

import json
import time
from dataclasses import asdict
from typing import Any, Dict, List

from playwright.sync_api import Page

from .telemetry import TelemetryEvent


class TelemetryCollector:
    """Comprehensive telemetry collection."""

    def __init__(self) -> None:
        self.events: List[TelemetryEvent] = []
        self.start_time = time.time()

    def log_event(
        self,
        event_type: str,
        page: Page,
        data: Dict[str, Any],
        success: bool = True,
        error: str = None,
    ):
        """Log a telemetry event."""
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type=event_type,
            page_url=page.url,
            page_title=page.title(),
            data=data,
            success=success,
            error=error,
        )
        self.events.append(event)
        # Real-time logging
        status = "✅" if success else "❌"
        print(f"{status} {event_type}: {page.url} | {data.get('summary', '')}")
        if error:
            print(f"   Error: {error}")

    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary."""
        total_events = len(self.events)
        successful_events = len([e for e in self.events if e.success])
        failed_events = total_events - successful_events
        event_types = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": successful_events / total_events if total_events > 0 else 0,
            "event_types": event_types,
            "session_duration": time.time() - self.start_time,
        }

    def save_telemetry(self, filename: str = None):
        """Save telemetry to file."""
        if not filename:
            timestamp = int(time.time())
            filename = f"telemetry_{timestamp}.json"
        # Convert to serializable format
        telemetry_data = {
            "summary": self.get_summary(),
            "events": [asdict(event) for event in self.events],
        }
        with open(filename, "w") as f:
            json.dump(telemetry_data, f, indent=2)
        print(f"📊 Telemetry saved: {filename}")
        return filename

