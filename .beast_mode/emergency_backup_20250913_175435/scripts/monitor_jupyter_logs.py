#!/usr/bin/env python3
"""
Jupyter Notebook Monitor
Monitors Jupyter server logs and notebook execution in real-time
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def monitor_jupyter_logs():
    """Monitor Jupyter server logs and notebook activity"""
    print("🔍 Jupyter Notebook Monitor Started")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 Monitoring Jupyter server on port 8889")
    print("📓 Watching notebook: gemini_billing_analysis.ipynb")
    print("=" * 50)

    # Check if Jupyter is running
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8889/api/status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            print("✅ Jupyter server is running on port 8889")
        else:
            print("❌ Jupyter server not responding on port 8889")
    except Exception as e:
        print(f"⚠️  Could not check Jupyter status: {e}")

    # Monitor notebook file for changes
    notebook_path = Path(
        "data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
    )
    last_modified = notebook_path.stat().st_mtime if notebook_path.exists() else 0

    print("\n🔄 Monitoring for notebook activity...")
    print("Press Ctrl+C to stop monitoring")

    try:
        while True:
            # Check if notebook file was modified
            if notebook_path.exists():
                current_modified = notebook_path.stat().st_mtime
                if current_modified > last_modified:
                    print(f"\n📝 Notebook modified at {datetime.now().strftime('%H:%M:%S')}")
                    last_modified = current_modified

            # Check for kernel activity (simplified)
            try:
                result = subprocess.run(
                    ["curl", "-s", "http://localhost:8889/api/kernels"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if result.returncode == 0 and "kernels" in result.stdout:
                    print(f"🟢 Kernel active at {datetime.now().strftime('%H:%M:%S')}")
            except Exception:  # noqa: E722
                pass

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
        print("=" * 50)
        print("📊 Summary:")
        print("- Jupyter server was running on port 8889")
        print("- Notebook monitoring was active")
        print("- Use Ctrl+C in the Jupyter terminal to stop the server")


def check_notebook_status():
    """Check the current status of the notebook"""
    notebook_path = Path(
        "data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
    )

    if not notebook_path.exists():
        print("❌ Notebook file not found!")
        return False

    print(f"✅ Notebook found: {notebook_path}")
    print(f"📏 Size: {notebook_path.stat().st_size} bytes")
    print(f"🕒 Last modified: {datetime.fromtimestamp(notebook_path.stat().st_mtime)}")

    # Check if it's a valid JSON
    try:
        import json

        with open(notebook_path) as f:
            data = json.load(f)
        print(f"✅ Valid JSON notebook with {len(data.get('cells', []))} cells")
        return True
    except Exception as e:
        print(f"❌ Invalid notebook JSON: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Jupyter Notebook Monitor")
    print("=" * 50)

    # Check notebook status first
    if check_notebook_status():
        print("\n🚀 Starting monitoring...")
        monitor_jupyter_logs()
    else:
        print("❌ Cannot start monitoring - notebook issues detected")
        sys.exit(1)
