#!/usr/bin/env python3
"""
Super Whisper Health Monitor Daemon
Monitors Super Whisper process health and restarts when unresponsive.
Checks every 5 seconds.
"""

import subprocess
import time
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/super_whisper_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SuperWhisperMonitor:
    """Monitor and restart Super Whisper when unresponsive."""

    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval
        self.restart_count = 0
        self.last_restart_time = None

    def find_super_whisper_process(self) -> list:
        """Find Super Whisper process(es)."""
        try:
            # Search for Super Whisper process (lowercase superwhisper)
            result = subprocess.run(
                ['pgrep', '-f', 'superwhisper'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                return [int(pid) for pid in pids if pid]

            return []

        except subprocess.TimeoutExpired:
            logger.error("Timeout finding Super Whisper process")
            return []
        except Exception as e:
            logger.error(f"Error finding Super Whisper process: {e}")
            return []

    def is_super_whisper_responding(self) -> bool:
        """Check if Super Whisper is responding."""
        pids = self.find_super_whisper_process()

        if not pids:
            logger.warning("Super Whisper process not found")
            return False

        # Check if process is responsive by checking CPU usage
        # If process exists but is frozen, it might have 0% CPU for extended period
        try:
            for pid in pids:
                # Check if process is still alive
                result = subprocess.run(
                    ['ps', '-p', str(pid), '-o', 'pid,stat,comm'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode != 0:
                    logger.warning(f"Super Whisper process {pid} not found")
                    return False

                # Check process state (Z = zombie, D = uninterruptible sleep)
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        state = parts[1]
                        if 'Z' in state or 'D' in state:
                            logger.warning(f"Super Whisper process {pid} in bad state: {state}")
                            return False

            logger.info(f"✓ Super Whisper OK (PIDs: {pids})")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Timeout checking Super Whisper responsiveness")
            return False
        except Exception as e:
            logger.error(f"Error checking Super Whisper responsiveness: {e}")
            return False

    def kill_super_whisper(self) -> bool:
        """Kill all Super Whisper processes."""
        pids = self.find_super_whisper_process()

        if not pids:
            logger.info("No Super Whisper processes to kill")
            return True

        logger.info(f"Killing Super Whisper processes: {pids}")

        for pid in pids:
            try:
                # Try graceful termination first
                subprocess.run(['kill', str(pid)], timeout=5)
                time.sleep(2)

                # Check if process is still alive
                if self.find_super_whisper_process():
                    # Force kill if still alive
                    logger.warning(f"Force killing Super Whisper process {pid}")
                    subprocess.run(['kill', '-9', str(pid)], timeout=5)
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error killing Super Whisper process {pid}: {e}")
                return False

        # Verify all processes are killed
        remaining = self.find_super_whisper_process()
        if remaining:
            logger.error(f"Failed to kill Super Whisper processes: {remaining}")
            return False

        logger.info("Super Whisper processes killed successfully")
        return True

    def start_super_whisper(self) -> bool:
        """Start Super Whisper application."""
        try:
            logger.info("Starting Super Whisper...")

            # Super Whisper app location (lowercase)
            app_path = "/Applications/superwhisper.app"

            if not Path(app_path).exists():
                logger.error(f"Super Whisper app not found at {app_path}")
                return False

            # Start the application
            subprocess.Popen(
                ['open', app_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait a moment for app to start
            time.sleep(3)

            # Verify it started
            if self.find_super_whisper_process():
                logger.info("Super Whisper started successfully")
                self.restart_count += 1
                self.last_restart_time = datetime.now()
                return True
            else:
                logger.error("Super Whisper failed to start")
                return False

        except Exception as e:
            logger.error(f"Error starting Super Whisper: {e}")
            return False

    def restart_super_whisper(self) -> bool:
        """Kill and restart Super Whisper."""
        logger.info("Restarting Super Whisper...")

        if not self.kill_super_whisper():
            logger.error("Failed to kill Super Whisper")
            return False

        time.sleep(2)

        if not self.start_super_whisper():
            logger.error("Failed to start Super Whisper")
            return False

        logger.info(f"Super Whisper restarted successfully (restart #{self.restart_count})")
        return True

    def run(self):
        """Run the monitoring daemon."""
        logger.info(f"Starting Super Whisper monitor (checking every {self.check_interval}s)")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                if not self.is_super_whisper_responding():
                    logger.warning("Super Whisper not responding - restarting...")

                    if self.restart_super_whisper():
                        logger.info("Super Whisper recovered")
                    else:
                        logger.error("Failed to recover Super Whisper")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Monitor crashed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Super Whisper Health Monitor Daemon'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Check interval in seconds (default: 5)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check Super Whisper status once and exit'
    )
    parser.add_argument(
        '--restart',
        action='store_true',
        help='Restart Super Whisper once and exit'
    )

    args = parser.parse_args()

    monitor = SuperWhisperMonitor(check_interval=args.interval)

    if args.check:
        # Just check status
        if monitor.is_super_whisper_responding():
            print("✅ Super Whisper is responding")
            sys.exit(0)
        else:
            print("❌ Super Whisper is NOT responding")
            sys.exit(1)

    elif args.restart:
        # Just restart once
        if monitor.restart_super_whisper():
            print("✅ Super Whisper restarted successfully")
            sys.exit(0)
        else:
            print("❌ Failed to restart Super Whisper")
            sys.exit(1)

    else:
        # Run daemon
        monitor.run()


if __name__ == '__main__':
    main()