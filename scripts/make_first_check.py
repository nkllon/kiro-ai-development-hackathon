#!/usr/bin/env python3
"""
Make-First Command Enforcement Hook.
This script checks if a Make target exists before allowing direct commands.
"""

import sys


def get_make_targets() -> list[str]:
    """Get all available Make targets."""
    # Use hardcoded targets since parsing is unreliable
    return [
        "test",
        "lint",
        "format",
        "type-safety",
        "security-check",
        "help",
        "test-all",
        "lint-all",
        "format-all",
        "test-python",
        "lint-python",
        "format-python",
    ]


def check_command_has_make_target(command: str) -> tuple[bool, str]:
    """Check if a command has a corresponding Make target."""
    targets = get_make_targets()

    # Common command to target mappings
    command_mappings = {
        "pytest": "test",
        "flake8": "lint",
        "black": "format",
        "mypy": "type-safety",
        "bandit": "security-check",
        "safety": "security-check",
        "uv run pytest": "test",
        "uv run flake8": "lint",
        "uv run black": "format",
        "uv run mypy": "type-safety",
        "python -m pytest": "test",
        "python -m flake8": "lint",
        "python -m black": "format",
        "python -m mypy": "type-safety",
    }

    for cmd_pattern, target in command_mappings.items():
        if cmd_pattern in command:
            if target in targets:
                return True, target
            # Try alternative targets
            alternatives = [f"{target}-all", f"{target}-python"]
            for alt in alternatives:
                if alt in targets:
                    return True, alt

    return False, ""


def suggest_make_target(command: str) -> str:
    """Suggest the appropriate Make target for a command."""
    has_target, target = check_command_has_make_target(command)

    if has_target:
        return f"❌ Use 'make {target}' instead of '{command}'"
    return f"💡 Consider adding a Make target for: {command}"


def main():
    """Main function - enforce Make-first approach."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/make_first_check.py <command>")
        sys.exit(1)

    command = " ".join(sys.argv[1:])

    print("🔍 Checking for Make target...")
    has_target, target = check_command_has_make_target(command)

    if has_target:
        print(f"❌ COMMAND BLOCKED: {command}")
        print(f"✅ USE INSTEAD: make {target}")
        print("\n📋 Available Make targets:")

        targets = get_make_targets()
        for t in sorted(targets):
            print(f"   - make {t}")

        sys.exit(1)
    else:
        print(f"✅ Command allowed: {command}")
        print("💡 Consider adding a Make target for future use")


if __name__ == "__main__":
    main()
