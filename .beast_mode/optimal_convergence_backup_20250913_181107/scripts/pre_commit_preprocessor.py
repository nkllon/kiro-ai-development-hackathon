#!/usr/bin/env python3
"""
Pre-commit Preprocessor

Runs all code quality tools BEFORE commit to ensure pre-commit hooks always pass.
This eliminates the need for multiple commits due to formatting issues.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PreCommitPreprocessor:
    """Preprocesses code before commit to ensure quality gates pass"""

    def __init__(self) -> None:
        self.project_root = Path(__file__).parent.parent
        self.python_files = list(self.project_root.rglob("*.py"))
        self.yaml_files = list(self.project_root.rglob("*.yaml")) + list(self.project_root.rglob("*.yml"))
        self.json_files = list(self.project_root.rglob("*.json"))
        self.md_files = list(self.project_root.rglob("*.md"))

    def run_black_formatting(self) -> bool:
        """Run Black formatting on all Python files"""
        logger.info("🎨 Running Black formatting...")
        try:
            result = subprocess.run(
                ["uv", "run", "black", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("✅ Black formatting completed successfully")
                return True
            else:
                logger.error(f"❌ Black formatting failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Black formatting failed with exception: {e}")
            return False

    def run_ruff_formatting(self) -> bool:
        """Run Ruff formatting on all Python files"""
        logger.info("🎯 Running Ruff formatting...")
        try:
            result = subprocess.run(
                ["uv", "run", "ruff", "format", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("✅ Ruff formatting completed successfully")
                return True
            else:
                logger.error(f"❌ Ruff formatting failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Ruff formatting failed with exception: {e}")
            return False

    def run_yaml_formatting(self) -> bool:
        """Run yamlfix on YAML files"""
        logger.info("📝 Running YAML formatting...")
        try:
            # Check if yamlfix is available
            result = subprocess.run(
                ["uv", "run", "yamlfix", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Run yamlfix on all YAML files
                for yaml_file in self.yaml_files:
                    subprocess.run(
                        ["uv", "run", "yamlfix", str(yaml_file)],
                        cwd=self.project_root,
                        timeout=60,
                    )
                logger.info("✅ YAML formatting completed successfully")
                return True
            else:
                logger.info("ℹ️ yamlfix not available, skipping YAML formatting")
                return True

        except Exception as e:
            logger.info(f"ℹ️ YAML formatting not available: {e}")
            return True

    def run_json_formatting(self) -> bool:
        """Format JSON files with proper indentation"""
        logger.info("📊 Running JSON formatting...")
        try:
            import json

            for json_file in self.json_files:
                if json_file.name in ["uv.lock", "package-lock.json"]:
                    continue  # Skip lock files

                try:
                    with open(json_file, "r") as f:
                        data = json.load(f)

                    with open(json_file, "w") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                except Exception as e:
                    logger.warning(f"⚠️ Could not format {json_file}: {e}")

            logger.info("✅ JSON formatting completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ JSON formatting failed: {e}")
            return False

    def run_markdown_formatting(self) -> bool:
        """Format Markdown files"""
        logger.info("📖 Running Markdown formatting...")
        try:
            # Check if mdformat is available
            result = subprocess.run(
                ["uv", "run", "mdformat", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Run mdformat on all Markdown files
                for md_file in self.md_files:
                    subprocess.run(
                        ["uv", "run", "mdformat", str(md_file)],
                        cwd=self.project_root,
                        timeout=60,
                    )
                logger.info("✅ Markdown formatting completed successfully")
                return True
            else:
                logger.info("ℹ️ mdformat not available, skipping Markdown formatting")
                return True

        except Exception as e:
            logger.info(f"ℹ️ Markdown formatting not available: {e}")
            return True

    def run_all_preprocessing(self) -> bool:
        """Run all preprocessing steps"""
        logger.info("🚀 Starting pre-commit preprocessing...")

        steps = [
            ("Black formatting", self.run_black_formatting),
            ("Ruff formatting", self.run_ruff_formatting),
            ("YAML formatting", self.run_yaml_formatting),
            ("JSON formatting", self.run_json_formatting),
            ("Markdown formatting", self.run_markdown_formatting),
        ]

        all_passed = True

        for step_name, step_func in steps:
            logger.info(f"🎯 Running {step_name}...")
            if not step_func():
                logger.error(f"❌ {step_name} failed")
                all_passed = False
            else:
                logger.info(f"✅ {step_name} passed")

        if all_passed:
            logger.info("🎉 All preprocessing steps completed successfully!")
            logger.info("💡 Your pre-commit hooks should now pass without issues")
        else:
            logger.error("❌ Some preprocessing steps failed")
            logger.error("🔧 Fix the issues above before committing")

        return all_passed

    def create_git_hook(self) -> bool:
        """Create a git pre-commit hook that runs this preprocessor"""
        hook_content = """#!/bin/bash
# Git pre-commit hook that runs preprocessing
echo "🚀 Running pre-commit preprocessing..."

# Run the preprocessor
python scripts/pre_commit_preprocessor.py

if [ $? -eq 0 ]; then
    echo "✅ Preprocessing completed successfully"
    echo "🔄 Staging any reformatted files..."
    git add .
    exit 0
else
    echo "❌ Preprocessing failed"
    echo "🔧 Fix the issues above before committing"
    exit 1
fi
"""

        hook_path = self.project_root / ".git" / "hooks" / "pre-commit"
        hook_path.parent.mkdir(parents=True, exist_ok=True)

        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make the hook executable
        hook_path.chmod(0o755)

        logger.info(f"✅ Created git pre-commit hook: {hook_path}")
        return True


def main() -> None:
    """Main entry point"""
    preprocessor = PreCommitPreprocessor()

    if len(sys.argv) > 1 and sys.argv[1] == "--create-hook":
        preprocessor.create_git_hook()
        return

    success = preprocessor.run_all_preprocessing()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
