#!/usr/bin/env python3
"""
Emergency Session Dump
=====================

Comprehensive session dump with all available information including:
- Stack traces and error logs
- Current system state
- Negotiation protocol status
- All implementation details
- Breadcrumb trails
- Recovery information
"""

import sys
import os
import traceback
import json
import inspect
from pathlib import Path
from datetime import datetime
import subprocess
import platform
from typing import Dict, Any, List, Optional

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class EmergencySessionDumper:
    """Emergency session dumper for comprehensive state preservation"""

    def __init__(self):
        self.dump_timestamp = datetime.now()
        self.dump_id = f"emergency_dump_{self.dump_timestamp.strftime('%Y%m%d_%H%M%S')}"
        self.dump_data = {}

    def create_comprehensive_dump(self) -> str:
        """Create comprehensive session dump"""

        print("🚨 EMERGENCY SESSION DUMP INITIATED")
        print("=" * 60)
        print(f"Dump ID: {self.dump_id}")
        print(f"Timestamp: {self.dump_timestamp}")
        print("=" * 60)

        # Gather all available information
        self._dump_system_info()
        self._dump_python_environment()
        self._dump_current_directory_state()
        self._dump_git_state()
        self._dump_imported_modules()
        self._dump_negotiation_protocol_state()
        self._dump_error_logs()
        self._dump_stack_traces()
        self._dump_file_structure()
        self._dump_recent_commits()
        self._dump_implementation_status()

        # Save the dump
        dump_file = self._save_dump()

        print(f"\n✅ COMPREHENSIVE SESSION DUMP COMPLETED")
        print(f"   Dump File: {dump_file}")
        print(f"   Data Sections: {len(self.dump_data)}")
        print(f"   Total Size: {self._get_dump_size():,} bytes")

        return dump_file

    def _dump_system_info(self):
        """Dump system information"""

        print("📊 Gathering system information...")

        self.dump_data["system_info"] = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "python_build": platform.python_build(),
            "hostname": platform.node(),
            "current_user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
            "current_directory": os.getcwd(),
            "dump_timestamp": self.dump_timestamp.isoformat(),
        }

    def _dump_python_environment(self):
        """Dump Python environment information"""

        print("🐍 Gathering Python environment...")

        self.dump_data["python_environment"] = {
            "executable": sys.executable,
            "path": sys.path,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
                "releaselevel": sys.version_info.releaselevel,
                "serial": sys.version_info.serial,
            },
            "platform": sys.platform,
            "argv": sys.argv,
            "stdin": str(sys.stdin),
            "stdout": str(sys.stdout),
            "stderr": str(sys.stderr),
            "modules_loaded": list(sys.modules.keys()),
            "threading_info": {
                "active_count": getattr(sys, "threading", {}).get(
                    "active_count", "unknown"
                )
            },
            "environment_variables": dict(os.environ),
        }

    def _dump_current_directory_state(self):
        """Dump current directory state"""

        print("📁 Gathering directory state...")

        try:
            current_dir = Path.cwd()
            files = []
            directories = []

            for item in current_dir.iterdir():
                if item.is_file():
                    try:
                        stat = item.stat()
                        files.append(
                            {
                                "name": item.name,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(
                                    stat.st_mtime
                                ).isoformat(),
                                "permissions": oct(stat.st_mode),
                            }
                        )
                    except Exception as e:
                        files.append({"name": item.name, "error": str(e)})
                elif item.is_dir():
                    directories.append(item.name)

            self.dump_data["directory_state"] = {
                "current_directory": str(current_dir),
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories),
            }
        except Exception as e:
            self.dump_data["directory_state"] = {
                "error": f"Failed to gather directory state: {e}",
                "current_directory": str(Path.cwd()),
            }

    def _dump_git_state(self):
        """Dump Git repository state"""

        print("📝 Gathering Git state...")

        try:
            # Git status
            git_status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            # Git log
            git_log = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            # Git branch
            git_branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            # Git remote
            git_remote = subprocess.run(
                ["git", "remote", "-v"], capture_output=True, text=True, cwd=Path.cwd()
            )

            self.dump_data["git_state"] = {
                "status": (
                    git_status.stdout
                    if git_status.returncode == 0
                    else git_status.stderr
                ),
                "recent_commits": (
                    git_log.stdout if git_log.returncode == 0 else git_log.stderr
                ),
                "current_branch": (
                    git_branch.stdout.strip()
                    if git_branch.returncode == 0
                    else "unknown"
                ),
                "remotes": (
                    git_remote.stdout
                    if git_remote.returncode == 0
                    else git_remote.stderr
                ),
                "is_git_repo": git_status.returncode == 0,
            }
        except Exception as e:
            self.dump_data["git_state"] = {
                "error": f"Failed to gather Git state: {e}",
                "is_git_repo": False,
            }

    def _dump_imported_modules(self):
        """Dump information about imported modules"""

        print("📦 Gathering module information...")

        module_info = {}
        for name, module in sys.modules.items():
            try:
                module_info[name] = {
                    "file": getattr(module, "__file__", None),
                    "package": getattr(module, "__package__", None),
                    "version": getattr(module, "__version__", None),
                    "path": getattr(module, "__path__", None),
                }
            except Exception as e:
                module_info[name] = {"error": str(e)}

        self.dump_data["imported_modules"] = module_info

    def _dump_negotiation_protocol_state(self):
        """Dump negotiation protocol implementation state"""

        print("🤝 Gathering negotiation protocol state...")

        try:
            # Check if negotiation protocol files exist
            negotiation_files = [
                "negotiation_protocol.py",
                "interactive_negotiation_cli.py",
                "test_negotiation_protocol.py",
                "demo_negotiation_protocol.py",
            ]

            file_status = {}
            for file in negotiation_files:
                file_path = Path(file)
                if file_path.exists():
                    stat = file_path.stat()
                    file_status[file] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                else:
                    file_status[file] = {"exists": False}

            self.dump_data["negotiation_protocol_state"] = {
                "files": file_status,
                "implementation_status": "COMPLETE - Interactive negotiation with persistent behavior",
                "key_features": [
                    "General-purpose impasse detection and negotiation",
                    "Context-aware solution generation",
                    "Session preservation priority enforcement",
                    "Breadcrumb trail creation for recovery",
                    "Persistent negotiation until clear direction received",
                    "Terminal failure mode handling",
                    "Interactive CLI for human-AI negotiation",
                ],
                "termination_conditions": [
                    "Human provides clear, executable direction",
                    "Human disconnects (Ctrl+D/Ctrl+C)",
                    "Maximum negotiation rounds reached",
                    "Human explicitly exits negotiation",
                ],
            }
        except Exception as e:
            self.dump_data["negotiation_protocol_state"] = {
                "error": f"Failed to gather negotiation protocol state: {e}"
            }

    def _dump_error_logs(self):
        """Dump error logs and exception information"""

        print("❌ Gathering error logs...")

        # Get current exception info if any
        exc_info = sys.exc_info()
        error_info = {}

        if exc_info[0] is not None:
            error_info["current_exception"] = {
                "type": str(exc_info[0]),
                "value": str(exc_info[1]),
                "traceback": traceback.format_exception(*exc_info),
            }

        # Check for recent error files
        error_files = []
        try:
            for file in Path.cwd().glob("*.log"):
                if file.stat().st_mtime > (
                    datetime.now().timestamp() - 3600
                ):  # Last hour
                    error_files.append(
                        {
                            "name": file.name,
                            "size": file.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                file.stat().st_mtime
                            ).isoformat(),
                        }
                    )
        except Exception as e:
            error_files = [{"error": str(e)}]

        self.dump_data["error_logs"] = {
            "current_exception": error_info.get("current_exception"),
            "recent_error_files": error_files,
            "sys_last_traceback": (
                traceback.format_exc()
                if traceback.format_exc() != "NoneType: None\n"
                else None
            ),
        }

    def _dump_stack_traces(self):
        """Dump current stack traces"""

        print("📚 Gathering stack traces...")

        # Get current stack
        current_stack = traceback.format_stack()

        # Get all thread stacks if available
        thread_stacks = {}
        try:
            import threading

            for thread in threading.enumerate():
                thread_stacks[thread.name] = {
                    "ident": thread.ident,
                    "is_alive": thread.is_alive(),
                    "daemon": thread.daemon,
                }
        except Exception as e:
            thread_stacks = {"error": str(e)}

        self.dump_data["stack_traces"] = {
            "current_stack": current_stack,
            "thread_info": thread_stacks,
            "frame_info": self._get_frame_info(),
        }

    def _get_frame_info(self):
        """Get detailed frame information"""

        frame_info = []
        frame = inspect.currentframe()
        depth = 0

        while frame and depth < 20:  # Limit depth to prevent infinite loops
            frame_info.append(
                {
                    "depth": depth,
                    "filename": frame.f_code.co_filename,
                    "function": frame.f_code.co_name,
                    "line_number": frame.f_lineno,
                    "locals": {
                        k: str(v)[:200] for k, v in frame.f_locals.items()
                    },  # Truncate long values
                }
            )
            frame = frame.f_back
            depth += 1

        return frame_info

    def _dump_file_structure(self):
        """Dump project file structure"""

        print("🏗️ Gathering file structure...")

        try:
            project_root = Path.cwd()
            structure = self._get_directory_structure(project_root, max_depth=3)

            self.dump_data["file_structure"] = {
                "root": str(project_root),
                "structure": structure,
                "total_files": self._count_files(project_root),
                "total_directories": self._count_directories(project_root),
            }
        except Exception as e:
            self.dump_data["file_structure"] = {
                "error": f"Failed to gather file structure: {e}"
            }

    def _get_directory_structure(
        self, path: Path, max_depth: int = 3, current_depth: int = 0
    ):
        """Recursively get directory structure"""

        if current_depth >= max_depth:
            return f"[max depth {max_depth} reached]"

        structure = {}

        try:
            for item in sorted(path.iterdir()):
                if item.is_dir() and not item.name.startswith("."):
                    structure[item.name + "/"] = self._get_directory_structure(
                        item, max_depth, current_depth + 1
                    )
                elif item.is_file():
                    try:
                        stat = item.stat()
                        structure[item.name] = {
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    except Exception:
                        structure[item.name] = "error"
        except Exception as e:
            return f"error: {e}"

        return structure

    def _count_files(self, path: Path) -> int:
        """Count total files in directory"""
        count = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    count += 1
        except Exception:
            pass
        return count

    def _count_directories(self, path: Path) -> int:
        """Count total directories in directory"""
        count = 0
        try:
            for item in path.rglob("*"):
                if item.is_dir():
                    count += 1
        except Exception:
            pass
        return count

    def _dump_recent_commits(self):
        """Dump recent Git commits"""

        print("📝 Gathering recent commits...")

        try:
            # Get last 20 commits with full details
            git_log = subprocess.run(
                [
                    "git",
                    "log",
                    "--pretty=format:%H|%an|%ae|%ad|%s",
                    "--date=iso",
                    "-20",
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            if git_log.returncode == 0:
                commits = []
                for line in git_log.stdout.strip().split("\n"):
                    if line:
                        parts = line.split("|", 4)
                        if len(parts) >= 5:
                            commits.append(
                                {
                                    "hash": parts[0],
                                    "author": parts[1],
                                    "email": parts[2],
                                    "date": parts[3],
                                    "message": parts[4],
                                }
                            )

                self.dump_data["recent_commits"] = commits
            else:
                self.dump_data["recent_commits"] = {
                    "error": "Failed to get Git log",
                    "stderr": git_log.stderr,
                }
        except Exception as e:
            self.dump_data["recent_commits"] = {
                "error": f"Failed to gather recent commits: {e}"
            }

    def _dump_implementation_status(self):
        """Dump current implementation status"""

        print("🚀 Gathering implementation status...")

        self.dump_data["implementation_status"] = {
            "negotiation_protocol": {
                "status": "COMPLETE",
                "features": [
                    "General-purpose impasse detection",
                    "Context-aware negotiation options",
                    "Session preservation priority",
                    "Breadcrumb trail creation",
                    "Interactive CLI for human negotiation",
                    "Persistent negotiation behavior",
                    "Terminal failure mode handling",
                ],
                "files_implemented": [
                    "negotiation_protocol.py",
                    "interactive_negotiation_cli.py",
                    "test_negotiation_protocol.py",
                    "demo_negotiation_protocol.py",
                    "demo_persistent_negotiation.py",
                ],
            },
            "fallback_mechanisms": {
                "status": "COMPLETE",
                "features": [
                    "Registry availability system",
                    "Field repair and modification system",
                    "Graceful fallback to human interaction",
                    "Clear human interaction options",
                    "Actionable recommendations",
                ],
            },
            "current_session": {
                "state": "NEGOTIATION_PROTOCOL_IMPLEMENTATION_COMPLETE",
                "last_activity": "Interactive negotiation CLI implementation",
                "next_steps": [
                    "Test interactive negotiation with real human input",
                    "Integrate negotiation protocol into LangGraph workflows",
                    "Add negotiation protocol to field repair system",
                    "Create comprehensive documentation",
                ],
            },
        }

    def _save_dump(self) -> str:
        """Save the comprehensive dump to file"""

        dump_file = f"{self.dump_id}.json"

        try:
            with open(dump_file, "w") as f:
                json.dump(self.dump_data, f, indent=2, default=str)

            return dump_file
        except Exception as e:
            # Fallback: try to save a minimal dump
            fallback_file = f"{self.dump_id}_minimal.txt"
            try:
                with open(fallback_file, "w") as f:
                    f.write(f"EMERGENCY SESSION DUMP - {self.dump_timestamp}\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Error saving full dump: {e}\n")
                    f.write(f"System info: {platform.platform()}\n")
                    f.write(f"Python version: {sys.version}\n")
                    f.write(f"Current directory: {os.getcwd()}\n")
                    f.write(f"Exception: {traceback.format_exc()}\n")
                return fallback_file
            except Exception:
                return "dump_failed"

    def _get_dump_size(self) -> int:
        """Get the size of the dump data"""

        try:
            return len(json.dumps(self.dump_data, default=str))
        except Exception:
            return 0


def main():
    """Main function to create emergency session dump"""

    print("🚨 INITIATING EMERGENCY SESSION DUMP")
    print("=" * 60)
    print("Creating comprehensive session dump with all available information...")
    print("=" * 60)

    dumper = EmergencySessionDumper()
    dump_file = dumper.create_comprehensive_dump()

    print(f"\n📋 DUMP SUMMARY:")
    print(f"   File: {dump_file}")
    print(f"   Timestamp: {dumper.dump_timestamp}")
    print(f"   Sections: {list(dumper.dump_data.keys())}")

    print(f"\n💾 SESSION PRESERVATION COMPLETE")
    print(f"   All available information has been preserved")
    print(f"   Recovery can proceed from this comprehensive state")
    print(f"   Breadcrumb trail established for future reference")

    return dump_file


if __name__ == "__main__":
    try:
        dump_file = main()
        print(f"\n✅ Emergency session dump completed: {dump_file}")
    except Exception as e:
        print(f"\n❌ Fatal error during session dump: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
