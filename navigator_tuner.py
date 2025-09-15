#!/usr/bin/env python3
"""
Navigator Tuner
===============

Interactive tuning system for the adaptive navigator.
Like programming a pocket calculator - issue commands to tune behavior.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Real-time navigator tuning and control
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright
from typing import Dict, List, Any, Optional
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class NavigatorTuner:
    """Interactive tuning system for navigation behavior."""

    def __init__(self, cdp_url: str = "http://localhost:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Tuning parameters
        self.tuning_params = {
            "confidence_threshold": 0.7,
            "devpost_priority": 0.9,
            "heuristic_weight": 0.3,
            "pattern_decay": 0.95,
            "max_navigations": 10,
            "wait_timeout": 30000,
            "discovery_enabled": True,
            "learning_rate": 0.1,
        }

        # Pattern registry
        self.patterns = {}
        self.session_stats = {
            "navigations": 0,
            "successes": 0,
            "failures": 0,
            "patterns_discovered": 0,
            "patterns_updated": 0,
        }

        # Command history
        self.command_history = []

        # Load saved tuning
        self._load_tuning_config()

    def _load_tuning_config(self):
        """Load tuning configuration from file."""
        try:
            with open("navigator_tuning.json", "r") as f:
                config = json.load(f)
                self.tuning_params.update(config.get("params", {}))
                self.patterns = config.get("patterns", {})
            print("📊 Loaded tuning configuration")
        except FileNotFoundError:
            print("📊 Starting with default tuning")

    def _save_tuning_config(self):
        """Save tuning configuration to file."""
        try:
            config = {
                "params": self.tuning_params,
                "patterns": self.patterns,
                "last_updated": time.time(),
            }
            with open("navigator_tuning.json", "w") as f:
                json.dump(config, f, indent=2)
            print("💾 Saved tuning configuration")
        except Exception as e:
            print(f"❌ Failed to save tuning: {e}")

    def connect_to_browser(self):
        """Connect to the existing browser session."""
        try:
            self.playwright = sync_playwright().start()

            # Get page info
            response = requests.get(f"{self.cdp_url}/json")
            pages_info = response.json()

            devpost_page_info = None
            for p_info in pages_info:
                if "devpost.com" in p_info.get(
                    "url", ""
                ) and "submission" in p_info.get("url", ""):
                    devpost_page_info = p_info
                    break

            if not devpost_page_info:
                print("❌ No DevPost submission page found")
                return False

            print(f"📄 Target page: {devpost_page_info['title']}")
            print(f"🔗 URL: {devpost_page_info['url']}")

            # Connect to browser
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0]
            pages = self.context.pages

            # Find DevPost page
            self.page = None
            for page in pages:
                if "devpost.com" in page.url and "submission" in page.url:
                    self.page = page
                    break

            if not self.page:
                self.page = pages[0]

            print(f"✅ Connected to: {self.page.url}")
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def execute_command(self, command: str) -> str:
        """Execute a tuning command."""
        self.command_history.append({"command": command, "timestamp": time.time()})

        # Parse command (RPN-style or natural language)
        parts = command.strip().split()
        if not parts:
            return "❌ Empty command"

        cmd = parts[0].lower()

        try:
            if cmd == "help":
                return self._help_command()
            elif cmd == "status":
                return self._status_command()
            elif cmd == "params":
                return self._params_command(parts[1:])
            elif cmd == "set":
                return self._set_command(parts[1:])
            elif cmd == "get":
                return self._get_command(parts[1:])
            elif cmd == "analyze":
                return self._analyze_command()
            elif cmd == "navigate":
                return self._navigate_command(parts[1:])
            elif cmd == "discover":
                return self._discover_command()
            elif cmd == "patterns":
                return self._patterns_command(parts[1:])
            elif cmd == "reset":
                return self._reset_command(parts[1:])
            elif cmd == "save":
                return self._save_command()
            elif cmd == "load":
                return self._load_command()
            elif cmd == "history":
                return self._history_command()
            elif cmd == "stats":
                return self._stats_command()
            elif cmd == "tune":
                return self._tune_command(parts[1:])
            elif cmd == "auto":
                return self._auto_command(parts[1:])
            else:
                return f"❌ Unknown command: {cmd}. Type 'help' for available commands."

        except Exception as e:
            return f"❌ Command error: {e}"

    def _help_command(self) -> str:
        """Show help information."""
        return """
🧠 Navigator Tuner Commands
==========================

Basic Commands:
  help                    - Show this help
  status                  - Show current status
  analyze                 - Analyze current page
  navigate [direction]    - Navigate (forward/back/auto)
  discover                - Discover new patterns

Parameter Commands:
  params                  - Show all parameters
  set <param> <value>     - Set parameter value
  get <param>             - Get parameter value
  tune <param> <delta>    - Adjust parameter by delta

Pattern Commands:
  patterns                - Show learned patterns
  patterns clear          - Clear all patterns
  patterns save           - Save patterns
  patterns load           - Load patterns

System Commands:
  reset                   - Reset to defaults
  save                    - Save configuration
  load                    - Load configuration
  history                 - Show command history
  stats                   - Show session statistics
  auto [steps]            - Run automatic navigation

Examples:
  set confidence_threshold 0.8
  tune devpost_priority 0.1
  navigate forward
  auto 5
  patterns clear
        """

    def _status_command(self) -> str:
        """Show current status."""
        if not self.page:
            return "❌ Not connected to browser"

        return f"""
📊 Navigator Status
==================
Page: {self.page.title()}
URL: {self.page.url}
Confidence Threshold: {self.tuning_params['confidence_threshold']}
DevPost Priority: {self.tuning_params['devpost_priority']}
Patterns: {len(self.patterns)}
Session Stats: {self.session_stats['navigations']} navs, {self.session_stats['successes']} successes
        """

    def _params_command(self, args: List[str]) -> str:
        """Show or modify parameters."""
        if not args:
            # Show all parameters
            result = "📊 Current Parameters:\n"
            for param, value in self.tuning_params.items():
                result += f"  {param}: {value}\n"
            return result
        else:
            param = args[0]
            if param in self.tuning_params:
                return f"{param}: {self.tuning_params[param]}"
            else:
                return f"❌ Unknown parameter: {param}"

    def _set_command(self, args: List[str]) -> str:
        """Set parameter value."""
        if len(args) < 2:
            return "❌ Usage: set <param> <value>"

        param = args[0]
        value_str = args[1]

        if param not in self.tuning_params:
            return f"❌ Unknown parameter: {param}"

        try:
            # Try to convert to appropriate type
            old_value = self.tuning_params[param]
            if isinstance(old_value, bool):
                value = value_str.lower() in ["true", "1", "yes", "on"]
            elif isinstance(old_value, int):
                value = int(value_str)
            elif isinstance(old_value, float):
                value = float(value_str)
            else:
                value = value_str

            self.tuning_params[param] = value
            return f"✅ Set {param}: {old_value} → {value}"

        except ValueError:
            return f"❌ Invalid value for {param}: {value_str}"

    def _get_command(self, args: List[str]) -> str:
        """Get parameter value."""
        if not args:
            return "❌ Usage: get <param>"

        param = args[0]
        if param in self.tuning_params:
            return f"{param}: {self.tuning_params[param]}"
        else:
            return f"❌ Unknown parameter: {param}"

    def _analyze_command(self) -> str:
        """Analyze current page."""
        if not self.page:
            return "❌ Not connected to browser"

        try:
            # Get navigation elements
            steps_navigation = self.page.query_selector_all("#steps-navigation a.step")
            buttons = self.page.query_selector_all(
                "button, input[type='button'], input[type='submit']"
            )
            links = self.page.query_selector_all("a:not(.step)")

            result = f"""
🔍 Page Analysis
================
Title: {self.page.title()}
URL: {self.page.url}

Navigation Elements:
  Step Links: {len(steps_navigation)}
  Buttons: {len(buttons)}
  Other Links: {len(links)}

Step Navigation Details:
"""

            for i, step in enumerate(steps_navigation[:5], 1):
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                href = step.get_attribute("href") or ""
                result += f"  {i}. {text} [{classes}] -> {href}\n"

            return result

        except Exception as e:
            return f"❌ Analysis failed: {e}"

    def _navigate_command(self, args: List[str]) -> str:
        """Navigate in specified direction."""
        if not self.page:
            return "❌ Not connected to browser"

        direction = args[0] if args else "auto"

        try:
            if direction == "forward":
                return self._navigate_forward()
            elif direction == "back":
                return self._navigate_back()
            elif direction == "auto":
                return self._navigate_auto()
            else:
                return f"❌ Unknown direction: {direction}"

        except Exception as e:
            return f"❌ Navigation failed: {e}"

    def _navigate_forward(self) -> str:
        """Navigate forward."""
        try:
            # Look for next step
            next_links = self.page.query_selector_all("a.step.next")
            if next_links:
                next_links[0].click()
                self.page.wait_for_load_state("networkidle")
                self.session_stats["navigations"] += 1
                self.session_stats["successes"] += 1
                return f"✅ Navigated forward to: {self.page.title()}"

            # Look for high confidence forward elements
            buttons = self.page.query_selector_all(
                "button, input[type='button'], input[type='submit']"
            )
            for button in buttons:
                text = button.text_content().strip().lower()
                if any(
                    word in text for word in ["next", "continue", "proceed", "forward"]
                ):
                    button.click()
                    self.page.wait_for_load_state("networkidle")
                    self.session_stats["navigations"] += 1
                    self.session_stats["successes"] += 1
                    return f"✅ Navigated forward to: {self.page.title()}"

            return "❌ No forward navigation found"

        except Exception as e:
            self.session_stats["failures"] += 1
            return f"❌ Forward navigation failed: {e}"

    def _navigate_back(self) -> str:
        """Navigate backward."""
        try:
            # Look for previous step
            prev_links = self.page.query_selector_all("a.step.previous")
            if prev_links:
                prev_links[0].click()
                self.page.wait_for_load_state("networkidle")
                self.session_stats["navigations"] += 1
                self.session_stats["successes"] += 1
                return f"✅ Navigated back to: {self.page.title()}"

            return "❌ No backward navigation found"

        except Exception as e:
            self.session_stats["failures"] += 1
            return f"❌ Backward navigation failed: {e}"

    def _navigate_auto(self) -> str:
        """Automatic navigation using learned patterns."""
        try:
            # Get all navigation elements
            all_elements = []

            # DevPost steps
            steps = self.page.query_selector_all("#steps-navigation a.step")
            for step in steps:
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                all_elements.append(
                    {
                        "element": step,
                        "text": text,
                        "classes": classes,
                        "type": "step",
                        "confidence": self._calculate_confidence(step, "step"),
                    }
                )

            # Buttons
            buttons = self.page.query_selector_all(
                "button, input[type='button'], input[type='submit']"
            )
            for button in buttons:
                text = button.text_content().strip()
                all_elements.append(
                    {
                        "element": button,
                        "text": text,
                        "type": "button",
                        "confidence": self._calculate_confidence(button, "button"),
                    }
                )

            # Find best element
            if not all_elements:
                return "❌ No navigation elements found"

            # Sort by confidence
            all_elements.sort(key=lambda x: x["confidence"], reverse=True)
            best = all_elements[0]

            if best["confidence"] < self.tuning_params["confidence_threshold"]:
                return f"❌ No high confidence navigation found (best: {best['confidence']:.2f})"

            # Execute navigation
            best["element"].click()
            self.page.wait_for_load_state("networkidle")
            self.session_stats["navigations"] += 1
            self.session_stats["successes"] += 1

            return f"✅ Auto-navigated: {best['text']} (confidence: {best['confidence']:.2f}) → {self.page.title()}"

        except Exception as e:
            self.session_stats["failures"] += 1
            return f"❌ Auto navigation failed: {e}"

    def _calculate_confidence(self, element, element_type: str) -> float:
        """Calculate confidence score for element."""
        confidence = 0.0

        try:
            text = element.text_content().strip().lower()
            classes = element.get_attribute("class") or ""

            # DevPost-specific patterns
            if element_type == "step":
                if "next" in classes or "next" in text:
                    confidence = 0.9
                elif "previous" in classes or "prev" in text:
                    confidence = 0.9
                elif "current" in classes:
                    confidence = 0.1
                elif "completed" in classes:
                    confidence = 0.3
                else:
                    confidence = 0.7

            # General patterns
            elif any(
                word in text for word in ["next", "continue", "proceed", "forward"]
            ):
                confidence = 0.8
            elif any(word in text for word in ["back", "previous", "return"]):
                confidence = 0.8
            elif "submit" in text or "save" in text:
                confidence = 0.7
            else:
                confidence = 0.3

            # Apply DevPost priority
            if "devpost.com" in self.page.url:
                confidence *= self.tuning_params["devpost_priority"]

        except Exception as e:
            confidence = 0.0

        return min(1.0, confidence)

    def _discover_command(self) -> str:
        """Discover new patterns."""
        if not self.page:
            return "❌ Not connected to browser"

        try:
            # Discover DevPost patterns
            patterns_found = 0

            # Step navigation patterns
            steps = self.page.query_selector_all("#steps-navigation a.step")
            if steps:
                pattern_key = "devpost_steps"
                if pattern_key not in self.patterns:
                    self.patterns[pattern_key] = {
                        "selector": "#steps-navigation a.step",
                        "confidence": 0.9,
                        "success_count": 0,
                        "last_seen": time.time(),
                    }
                    patterns_found += 1

            # Next/Previous patterns
            next_links = self.page.query_selector_all("a.step.next")
            if next_links:
                pattern_key = "devpost_next"
                if pattern_key not in self.patterns:
                    self.patterns[pattern_key] = {
                        "selector": "a.step.next",
                        "confidence": 0.95,
                        "success_count": 0,
                        "last_seen": time.time(),
                    }
                    patterns_found += 1

            self.session_stats["patterns_discovered"] += patterns_found
            return f"✅ Discovered {patterns_found} new patterns. Total: {len(self.patterns)}"

        except Exception as e:
            return f"❌ Discovery failed: {e}"

    def _patterns_command(self, args: List[str]) -> str:
        """Manage patterns."""
        if not args:
            # Show patterns
            if not self.patterns:
                return "📚 No patterns learned yet"

            result = "📚 Learned Patterns:\n"
            for key, pattern in self.patterns.items():
                result += f"  {key}: {pattern['selector']} (confidence: {pattern['confidence']:.2f})\n"
            return result

        elif args[0] == "clear":
            self.patterns.clear()
            return "✅ Cleared all patterns"

        elif args[0] == "save":
            self._save_tuning_config()
            return "✅ Patterns saved"

        elif args[0] == "load":
            self._load_tuning_config()
            return "✅ Patterns loaded"

        else:
            return "❌ Unknown pattern command"

    def _tune_command(self, args: List[str]) -> str:
        """Tune parameter by delta."""
        if len(args) < 2:
            return "❌ Usage: tune <param> <delta>"

        param = args[0]
        delta_str = args[1]

        if param not in self.tuning_params:
            return f"❌ Unknown parameter: {param}"

        try:
            delta = float(delta_str)
            old_value = self.tuning_params[param]
            new_value = old_value + delta
            self.tuning_params[param] = new_value
            return f"✅ Tuned {param}: {old_value} → {new_value} (Δ{delta:+.2f})"

        except ValueError:
            return f"❌ Invalid delta: {delta_str}"

    def _auto_command(self, args: List[str]) -> str:
        """Run automatic navigation for specified steps."""
        steps = int(args[0]) if args else 5

        result = f"🤖 Running auto navigation for {steps} steps:\n"

        for i in range(steps):
            nav_result = self._navigate_auto()
            result += f"  Step {i+1}: {nav_result}\n"

            if "❌" in nav_result:
                break

        return result

    def _reset_command(self, args: List[str]) -> str:
        """Reset configuration."""
        self.tuning_params = {
            "confidence_threshold": 0.7,
            "devpost_priority": 0.9,
            "heuristic_weight": 0.3,
            "pattern_decay": 0.95,
            "max_navigations": 10,
            "wait_timeout": 30000,
            "discovery_enabled": True,
            "learning_rate": 0.1,
        }
        self.patterns.clear()
        self.session_stats = {
            "navigations": 0,
            "successes": 0,
            "failures": 0,
            "patterns_discovered": 0,
            "patterns_updated": 0,
        }
        return "✅ Reset to defaults"

    def _save_command(self) -> str:
        """Save configuration."""
        self._save_tuning_config()
        return "✅ Configuration saved"

    def _load_command(self) -> str:
        """Load configuration."""
        self._load_tuning_config()
        return "✅ Configuration loaded"

    def _history_command(self) -> str:
        """Show command history."""
        if not self.command_history:
            return "📜 No commands in history"

        result = "📜 Command History:\n"
        for i, cmd in enumerate(self.command_history[-10:], 1):
            result += f"  {i}. {cmd['command']}\n"
        return result

    def _stats_command(self) -> str:
        """Show session statistics."""
        return f"""
📊 Session Statistics
====================
Navigations: {self.session_stats['navigations']}
Successes: {self.session_stats['successes']}
Failures: {self.session_stats['failures']}
Success Rate: {(self.session_stats['successes'] / max(1, self.session_stats['navigations'])) * 100:.1f}%
Patterns Discovered: {self.session_stats['patterns_discovered']}
Patterns Updated: {self.session_stats['patterns_updated']}
Total Patterns: {len(self.patterns)}
        """

    def interactive_mode(self):
        """Run interactive tuning mode."""
        print("🧠 Navigator Tuner - Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("=" * 50)

        if not self.connect_to_browser():
            print("❌ Failed to connect to browser")
            return

        while True:
            try:
                command = input("\n🎛️  tuner> ").strip()

                if command.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if command:
                    result = self.execute_command(command)
                    print(result)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        if self.playwright:
            self.playwright.stop()


def main():
    """Main function."""
    tuner = NavigatorTuner()
    tuner.interactive_mode()


if __name__ == "__main__":
    main()
