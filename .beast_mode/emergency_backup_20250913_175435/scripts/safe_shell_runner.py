#!/usr/bin/env python3
"""
Safe Shell Runner

This module provides safe alternatives to shell commands that commonly cause dquote issues.
Uses Python subprocess with argument lists instead of shell string construction.
"""

import subprocess
import sys
from typing import List, Optional, Tuple, Union


def run_command_safely(
    cmd_args: list[str],
    description: str = "",
    capture_output: bool = True,
    check: bool = True,
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Run a command safely using subprocess with argument lists

    Args:
        cmd_args: List of command arguments (e.g., ["gh", "pr", "create", "--title", "My PR"])
        description: Human-readable description of what the command does
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise CalledProcessError on non-zero exit code

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        if description:
            print(f"🚀 {description}...")
            print(f"Command: {' '.join(cmd_args)}")

        result = subprocess.run(cmd_args, capture_output=capture_output, text=True, check=check)

        if description:
            print("✅ Command completed successfully!")
            if capture_output and result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")

        return (
            True,
            result.stdout if capture_output else None,
            result.stderr if capture_output else None,
        )

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stderr.strip():
            print(f"Error: {e.stderr.strip()}")
        return (
            False,
            e.stdout if capture_output else None,
            e.stderr if capture_output else None,
        )

    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        return False, None, str(e)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None, str(e)


def create_github_pr(title: str, body: str, base: str = "develop", head: Optional[str] = None) -> bool:
    """
    Create GitHub PR without dquote issues

    Args:
        title: PR title
        body: PR description
        base: Base branch (default: develop)
        head: Head branch (default: current branch)

    Returns:
        True if successful, False otherwise
    """
    cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]

    if head:
        cmd.extend(["--head", head])

    success, stdout, stderr = run_command_safely(cmd, f"Creating GitHub PR: {title}")

    if success and stdout:
        print(f"✅ PR created successfully!")
        print(f"PR URL: {stdout.strip()}")
        return True

    return False


def git_commit_safely(message: str) -> bool:
    """
    Commit changes without dquote issues

    Args:
        message: Commit message

    Returns:
        True if successful, False otherwise
    """
    cmd = ["git", "commit", "-m", message]

    success, stdout, stderr = run_command_safely(cmd, f"Committing changes: {message[:50]}{'...' if len(message) > 50 else ''}")

    return success


def git_push_safely(remote: str = "origin", branch: Optional[str] = None) -> bool:
    """
    Push changes without dquote issues

    Args:
        remote: Remote name (default: origin)
        branch: Branch name (default: current branch)

    Returns:
        True if successful, False otherwise
    """
    cmd = ["git", "push", remote]

    if branch:
        cmd.append(branch)

    success, stdout, stderr = run_command_safely(cmd, f"Pushing to {remote}{f'/{branch}' if branch else ''}")

    return success


def git_add_safely(files: Union[str, list[str]]) -> bool:
    """
    Add files to git without dquote issues

    Args:
        files: File path(s) to add

    Returns:
        True if successful, False otherwise
    """
    if isinstance(files, str):
        files = [files]

    cmd = ["git", "add"] + files

    success, stdout, stderr = run_command_safely(cmd, f"Adding files: {', '.join(files)}")

    return success


def docker_run_safely(
    image: str,
    env_vars: Optional[dict] = None,
    volumes: Optional[list[str]] = None,
    ports: Optional[list[str]] = None,
    command: Optional[list[str]] = None,
) -> bool:
    """
    Run Docker container without dquote issues

    Args:
        image: Docker image name
        env_vars: Environment variables dict
        volumes: Volume mappings list
        ports: Port mappings list
        command: Command to run in container

    Returns:
        True if successful, False otherwise
    """
    cmd = ["docker", "run"]

    # Add environment variables
    if env_vars:
        for key, value in env_vars.items():
            cmd.extend(["-e", f"{key}={value}"])

    # Add volume mappings
    if volumes:
        for volume in volumes:
            cmd.extend(["-v", volume])

    # Add port mappings
    if ports:
        for port in ports:
            cmd.extend(["-p", port])

    # Add image
    cmd.append(image)

    # Add command
    if command:
        cmd.extend(command)

    success, stdout, stderr = run_command_safely(cmd, f"Running Docker container: {image}")

    return success


def quick_recovery_script():
    """
    Quick recovery script template for dquote issues
    """
    print("🚨 Dquote Recovery Script")
    print("=" * 50)
    print()
    print("If you hit dquote issues:")
    print("1. Exit shell immediately: exit or Ctrl+C")
    print("2. Use this script instead of shell commands")
    print("3. Never try to fix dquote in shell")
    print()
    print("Example usage:")
    print("  python scripts/safe_shell_runner.py create-pr 'My PR Title' 'PR description'")
    print("  python scripts/safe_shell_runner.py commit 'Commit message'")
    print("  python scripts/safe_shell_runner.py push")


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        quick_recovery_script()
        return

    command = sys.argv[1].lower()

    if command == "create-pr" and len(sys.argv) >= 4:
        title = sys.argv[2]
        body = sys.argv[3]
        base = sys.argv[4] if len(sys.argv) > 4 else "develop"
        success = create_github_pr(title, body, base)
        sys.exit(0 if success else 1)

    elif command == "commit" and len(sys.argv) >= 3:
        message = sys.argv[2]
        success = git_commit_safely(message)
        sys.exit(0 if success else 1)

    elif command == "push":
        remote = sys.argv[2] if len(sys.argv) > 2 else "origin"
        branch = sys.argv[3] if len(sys.argv) > 3 else None
        success = git_push_safely(remote, branch)
        sys.exit(0 if success else 1)

    elif command == "add" and len(sys.argv) >= 3:
        files = sys.argv[2:]
        success = git_add_safely(files)
        sys.exit(0 if success else 1)

    else:
        quick_recovery_script()
        print(f"\nUnknown command: {command}")
        print("Available commands: create-pr, commit, push, add")


if __name__ == "__main__":
    main()
