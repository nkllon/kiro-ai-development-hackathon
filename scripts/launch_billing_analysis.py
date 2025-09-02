#!/usr/bin/env python3
"""
🚀 Launch Billing Analysis Jupyter Notebook

Launch Jupyter notebook with billing analysis data.
"""

import subprocess
import sys
from pathlib import Path


def launch_jupyter_analysis():
    """Launch Jupyter notebook with billing analysis"""
    try:
        # Check if billing data exists
        data_dir = Path("data/billing_reports/analysis_data")
        if not data_dir.exists():
            print("❌ Billing analysis data not found. Run the billing reporter first.")
            return False

        # Check for required files
        required_files = [
            "daily_billing_data.csv",
            "daily_summary.csv",
            "billing_analysis_template.ipynb",
        ]

        missing_files = []
        for file in required_files:
            if not (data_dir / file).exists():
                missing_files.append(file)

        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            print("Please run the billing reporter first: python scripts/gcp_billing_daily_reporter.py")
            return False

        print("🚀 Launching Jupyter Notebook with billing analysis...")
        print(f"📁 Data directory: {data_dir.absolute()}")
        print("📊 Available files:")
        for file in data_dir.glob("*"):
            print(f"  - {file.name}")

        # Change to the data directory and launch Jupyter
        print("\n🌐 Starting Jupyter notebook...")
        print("📝 You can now open the billing_analysis_template.ipynb file")
        print("🔗 Jupyter will be available at: http://localhost:8888")

        # Launch Jupyter
        result = subprocess.run(
            ["jupyter", "notebook", "--notebook-dir", str(data_dir.absolute())],
            cwd=data_dir,
        )

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Failed to launch Jupyter: {e}")
        return False


def main():
    """Main function to launch Jupyter analysis"""
    print("🚀 GCP Billing Analysis Launcher")
    print("=" * 50)

    success = launch_jupyter_analysis()

    if success:
        print("\n✅ Jupyter notebook launched successfully!")
    else:
        print("\n❌ Failed to launch Jupyter notebook")
        sys.exit(1)


if __name__ == "__main__":
    main()
