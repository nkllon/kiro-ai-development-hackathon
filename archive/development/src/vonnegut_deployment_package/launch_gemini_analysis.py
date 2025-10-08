#!/usr/bin/env python3
"""
🚀 Launch Gemini GCP Billing Analysis Notebook

Simple launcher for the Gemini analysis notebook with proper environment setup.
"""

import subprocess
import sys
from pathlib import Path


def launch_gemini_analysis() -> bool:
    """Launch the Gemini analysis notebook with proper environment"""
    try:
        notebook_path = Path(
            "data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
        )

        if not notebook_path.exists():
            print("❌ Notebook not found. Creating it...")
            # Create the notebook first
            result = subprocess.run(
                ["uv", "run", "python", "scripts/create_proper_notebook.py"],
            )
            if result.returncode != 0:
                return False

        print("🚀 Launching Gemini GCP Billing Analysis Notebook...")
        print(f"📓 Notebook: {notebook_path.absolute()}")
        print("🌐 Jupyter will be available at: http://localhost:8888")
        print("🐍 Using UV Python environment with all dependencies")
        print("\n💡 Features:")
        print("  - 🤖 Gemini LLM analysis with LangGraph/LangChain")
        print("  - 📊 Interactive visualizations")
        print("  - 💰 Cost optimization recommendations")
        print("  - 🔮 Cost forecasting")
        print("  - 🎯 Actionable insights")
        print("  - 🔐 1Password credential integration")

        # Launch Jupyter with explicit environment
        result = subprocess.run(
            ["uv", "run", "jupyter", "notebook", "--no-browser", "--port=8888"],
            cwd=notebook_path.parent,
        )

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Failed to launch notebook: {e}")
        return False


def main() -> None:
    """Main function to launch Gemini analysis"""
    print("🚀 Gemini GCP Billing Analysis Launcher")
    print("=" * 50)

    success = launch_gemini_analysis()

    if success:
        print("\n✅ Gemini analysis notebook launched successfully!")
        print("\n📝 Next steps:")
        print("1. Open http://localhost:8888 in your browser")
        print("2. Click on gemini_billing_analysis.ipynb")
        print("3. Run all cells to see the analysis")
        print("4. The notebook will automatically use the UV Python environment")
    else:
        print("\n❌ Failed to launch Gemini analysis notebook")
        sys.exit(1)


if __name__ == "__main__":
    main()
