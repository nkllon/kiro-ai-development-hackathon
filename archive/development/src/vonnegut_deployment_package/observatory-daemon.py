#!/usr/bin/env python3
"""
Observatory Server Daemon Manager

Provides proper process management for the Beast Mode Observatory server
with PID files, graceful shutdown, and logging.
"""

import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from subprocess import Popen, PIPE
from typing import Optional

import click


class ObservatoryDaemon:
    """Manages the Observatory server as a daemon process."""

    def __init__(self, project_root: str = None):
        if project_root is None:
            # Find project root by looking for setup.py or pyproject.toml
            current = Path(__file__).parent.parent
            while current != current.parent:
                if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
                    project_root = str(current)
                    break
                current = current.parent
            else:
                project_root = str(Path(__file__).parent.parent)

        self.project_root = Path(project_root)
        self.pid_dir = self.project_root / "var" / "run"
        self.log_dir = self.project_root / "var" / "log"
        self.pid_file = self.pid_dir / "observatory.pid"
        self.log_file = self.log_dir / "observatory.log"

        # Ensure directories exist
        self.pid_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def is_running(self) -> bool:
        """Check if the Observatory server is running."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            # PID file exists but process doesn't, clean up
            self.pid_file.unlink(missing_ok=True)
            return False

    def get_pid(self) -> Optional[int]:
        """Get the PID of the running Observatory server."""
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None

    def start(self, host: str = None, port: int = None, daemonize: bool = True):
        """Start the Observatory server."""
        if self.is_running():
            click.echo("Observatory server is already running", err=True)
            return False

        # Load config to get defaults
        config_file = self.project_root / "config" / "observatory.yaml"
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Use config defaults if not provided
            if host is None:
                host = config_data.get('server', {}).get('host', '0.0.0.0')
            if port is None:
                port = config_data.get('server', {}).get('port', 8888)
        else:
            # Fallback defaults
            if host is None:
                host = "0.0.0.0"
            if port is None:
                port = 8888

        # Prepare command
        server_entry = self.project_root / "scripts" / "start-observatory.py"
        cmd = [
            sys.executable,
            str(server_entry),
            "--host", host,
            "--port", str(port),
            "--config", str(config_file) if config_file.exists() else ""
        ]

        if daemonize:
            # Start as daemon
            click.echo(f"🚀 Starting Observatory server as daemon on http://{host}:{port}")

            # Redirect stdout/stderr to log file
            with open(self.log_file, 'a') as log:
                log.write(f"\n=== Observatory Server Started at {time.ctime()} ===\n")
                log.flush()

                process = Popen(
                    cmd,
                    stdout=log,
                    stderr=log,
                    cwd=str(self.project_root),
                    env=dict(os.environ, PYTHONPATH=str(self.project_root / "src")),
                    start_new_session=True
                )

            # Write PID file
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            # Give it a moment to start
            time.sleep(2)

            if self.is_running():
                click.echo(f"✅ Observatory server started (PID: {process.pid})")
                click.echo(f"📊 Dashboard: http://{host}:{port}")
                click.echo(f"📝 Logs: {self.log_file}")
                return True
            else:
                click.echo("❌ Failed to start Observatory server", err=True)
                return False
        else:
            # Start in foreground
            click.echo(f"🚀 Starting Observatory server on http://{host}:{port}")
            os.chdir(str(self.project_root))
            os.environ['PYTHONPATH'] = str(self.project_root / "src")
            os.execvp(sys.executable, cmd)

    def stop(self, force: bool = False):
        """Stop the Observatory server."""
        if not self.is_running():
            click.echo("Observatory server is not running")
            return True

        pid = self.get_pid()
        if pid is None:
            click.echo("Could not determine server PID", err=True)
            return False

        click.echo(f"🛑 Stopping Observatory server (PID: {pid})")

        try:
            if force:
                # SIGKILL - immediate termination
                os.kill(pid, signal.SIGKILL)
                click.echo("💥 Forcefully terminated Observatory server")
            else:
                # SIGTERM - graceful shutdown
                os.kill(pid, signal.SIGTERM)

                # Wait for graceful shutdown
                for _ in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    if not self.is_running():
                        break
                else:
                    click.echo("⚠️  Server didn't stop gracefully, forcing...")
                    os.kill(pid, signal.SIGKILL)

                click.echo("✅ Observatory server stopped")

            # Clean up PID file
            self.pid_file.unlink(missing_ok=True)

            # Log shutdown
            with open(self.log_file, 'a') as log:
                log.write(f"\n=== Observatory Server Stopped at {time.ctime()} ===\n")

            return True

        except ProcessLookupError:
            # Process already dead
            click.echo("Process already terminated")
            self.pid_file.unlink(missing_ok=True)
            return True
        except PermissionError:
            click.echo("Permission denied stopping server", err=True)
            return False

    def restart(self, host: str = "0.0.0.0", port: int = 8888):
        """Restart the Observatory server."""
        click.echo("🔄 Restarting Observatory server...")

        # Stop if running
        if self.is_running():
            if not self.stop():
                return False

        # Start again
        return self.start(host, port, daemonize=True)

    def status(self):
        """Show Observatory server status."""
        if self.is_running():
            pid = self.get_pid()
            click.echo(f"✅ Observatory server is running (PID: {pid})")

            # Show recent log entries
            if self.log_file.exists():
                click.echo("\n📝 Recent log entries:")
                try:
                    with open(self.log_file, 'r') as f:
                        lines = f.readlines()
                        # Show last 5 lines
                        for line in lines[-5:]:
                            click.echo(f"    {line.rstrip()}")
                except Exception as e:
                    click.echo(f"    Error reading log: {e}")
        else:
            click.echo("❌ Observatory server is not running")

    def logs(self, follow: bool = False, lines: int = 50):
        """Show Observatory server logs."""
        if not self.log_file.exists():
            click.echo("No log file found")
            return

        if follow:
            # Follow logs like tail -f
            click.echo("📝 Following Observatory logs (Ctrl+C to stop)...")
            try:
                import subprocess
                subprocess.run(['tail', '-f', str(self.log_file)])
            except KeyboardInterrupt:
                click.echo("\nStopped following logs")
        else:
            # Show last N lines
            try:
                with open(self.log_file, 'r') as f:
                    log_lines = f.readlines()

                if log_lines:
                    click.echo(f"📝 Last {min(lines, len(log_lines))} log entries:")
                    for line in log_lines[-lines:]:
                        click.echo(line.rstrip())
                else:
                    click.echo("Log file is empty")
            except Exception as e:
                click.echo(f"Error reading log file: {e}", err=True)


@click.group()
@click.option('--project-root', help='Project root directory')
@click.pass_context
def cli(ctx, project_root):
    """Observatory Server Daemon Manager"""
    ctx.ensure_object(dict)
    ctx.obj['daemon'] = ObservatoryDaemon(project_root)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8888, type=int, help='Port to bind to')
@click.option('--foreground', is_flag=True, help='Run in foreground')
@click.pass_context
def start(ctx, host, port, foreground):
    """Start the Observatory server."""
    daemon = ctx.obj['daemon']
    success = daemon.start(host, port, daemonize=not foreground)
    sys.exit(0 if success else 1)


@cli.command()
@click.option('--force', is_flag=True, help='Force kill the server')
@click.pass_context
def stop(ctx, force):
    """Stop the Observatory server."""
    daemon = ctx.obj['daemon']
    success = daemon.stop(force)
    sys.exit(0 if success else 1)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8888, type=int, help='Port to bind to')
@click.pass_context
def restart(ctx, host, port):
    """Restart the Observatory server."""
    daemon = ctx.obj['daemon']
    success = daemon.restart(host, port)
    sys.exit(0 if success else 1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show Observatory server status."""
    daemon = ctx.obj['daemon']
    daemon.status()


@cli.command()
@click.option('--follow', '-f', is_flag=True, help='Follow logs in real-time')
@click.option('--lines', '-n', default=50, type=int, help='Number of lines to show')
@click.pass_context
def logs(ctx, follow, lines):
    """Show Observatory server logs."""
    daemon = ctx.obj['daemon']
    daemon.logs(follow, lines)


if __name__ == '__main__':
    cli()