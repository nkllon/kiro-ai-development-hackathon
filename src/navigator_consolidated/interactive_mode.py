#!/usr/bin/env python3
"""
Interactive Mode - Manual control interface
==========================================

Extracted from smart_devpost_navigator_v2.py for RDI compliance.
Handles interactive mode for manual navigation control.
"""

from typing import Any, Dict, List, Optional


class InteractiveMode:
    """Handles interactive mode for manual control."""

    def __init__(self, navigator):
        self.navigator = navigator

    def start(self):
        """Start interactive mode for manual control."""
        print("\n🎮 Interactive Mode")
        print("=" * 20)
        print("Commands: next, prev, extract, screenshot, fill, quit")

        while True:
            try:
                command = input("🔧 Command: ").strip().lower()

                if command == "quit":
                    break
                elif command == "next":
                    next_step = self.navigator.step_detector.find_next_step()
                    if next_step:
                        self.navigator.step_detector.navigate_to_step(next_step)
                    else:
                        print("❌ No next step found")
                elif command == "extract":
                    form_data = self.navigator.form_processor.extract_current_form()
                    if form_data:
                        self.navigator.form_processor.save_form_data(form_data)
                elif command == "screenshot":
                    self.navigator.take_step_screenshot()
                elif command == "fill":
                    form_data = self.navigator.form_processor.extract_current_form()
                    if form_data:
                        self.navigator.form_processor.fill_current_form(form_data)
                else:
                    print("❌ Unknown command")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

