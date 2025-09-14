#!/usr/bin/env python3
"""
CI/CD Integration Script for Activity Model Generation

This script provides automated activity model generation for continuous integration
and deployment pipelines.

Features:
- Automated model generation on code changes
- Integration with round-trip system
- Performance monitoring and reporting
- Error handling and notifications
- Artifact management
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from round_trip_engineering.activity_model_integration import (
        ActivityModelIntegration,
    )
except ImportError:
    print("❌ Error: Could not import ActivityModelIntegration")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CIActivityModelGenerator:
    """
    CI/CD integration for activity model generation.
    """

    def __init__(self, output_dir: str = "ci_activity_models", config_file: Optional[str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load configuration
        self.config = self._load_config(config_file)

        # Initialize integration
        self.integration = ActivityModelIntegration(str(self.output_dir))

        # CI/CD environment detection
        self.ci_environment = self._detect_ci_environment()

        logger.info(f"🚀 CI Activity Model Generator initialized")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"🔧 CI Environment: {self.ci_environment}")

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "source_paths": ["src/"],
            "include_round_trip": True,
            "performance_threshold": 30.0,  # seconds
            "error_threshold": 0.1,  # 10% error rate
            "artifacts_to_keep": 10,
            "notifications": {"slack_webhook": None, "email": None},
        }

        if config_file and Path(config_file).exists():
            try:
                with open(config_file, "r") as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"✅ Configuration loaded from: {config_file}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load config file: {e}, using defaults")

        return default_config

    def _detect_ci_environment(self) -> str:
        """Detect the CI/CD environment."""
        ci_vars = {
            "GITHUB_ACTIONS": "GitHub Actions",
            "GITLAB_CI": "GitLab CI",
            "JENKINS_URL": "Jenkins",
            "CIRCLECI": "CircleCI",
            "TRAVIS": "Travis CI",
            "AZURE_PIPELINES": "Azure DevOps",
        }

        for var, name in ci_vars.items():
            if os.getenv(var):
                return name

        return "Local/Unknown"

    def run_generation(
        self,
        source_paths: Optional[List[str]] = None,
        include_round_trip: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Run activity model generation with CI/CD optimizations.

        Args:
            source_paths: Override source paths from config
            include_round_trip: Override round-trip integration from config

        Returns:
            Generation results with CI/CD metadata
        """
        # Use provided values or fall back to config
        source_paths = source_paths or self.config["source_paths"]
        include_round_trip = include_round_trip if include_round_trip is not None else self.config["include_round_trip"]

        start_time = time.time()

        # CI/CD pre-generation setup
        self._setup_ci_environment()

        try:
            # Run generation
            logger.info("🎨 Starting CI/CD activity model generation...")
            results = self.integration.generate_activity_models(source_paths=source_paths, include_round_trip=include_round_trip)

            # Add CI/CD metadata
            results["ci_metadata"] = {
                "environment": self.ci_environment,
                "timestamp": time.time(),
                "config_used": self.config,
                "generation_duration": time.time() - start_time,
            }

            # CI/CD post-generation processing
            self._process_ci_results(results)

            # Performance validation
            self._validate_performance(results)

            # Artifact management
            self._manage_artifacts(results)

            # Generate CI report
            ci_report = self._generate_ci_report(results)
            results["ci_report"] = ci_report

            logger.info("✅ CI/CD activity model generation completed successfully")
            return results

        except Exception as e:
            error_msg = f"CI/CD generation failed: {e}"
            logger.error(error_msg)

            # Create error results
            error_results = {
                "success": False,
                "error": error_msg,
                "ci_metadata": {
                    "environment": self.ci_environment,
                    "timestamp": time.time(),
                    "error": True,
                },
            }

            # Handle CI/CD error
            self._handle_ci_error(error_results)
            return error_results

    def _setup_ci_environment(self):
        """Setup CI/CD environment before generation."""
        logger.info("🔧 Setting up CI/CD environment...")

        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)

        # Set environment variables for CI
        os.environ["CI_ACTIVITY_MODELS"] = "true"
        os.environ["CI_OUTPUT_DIR"] = str(self.output_dir)

        # Create CI metadata file
        ci_metadata = {
            "timestamp": time.time(),
            "environment": self.ci_environment,
            "config": self.config,
        }

        with open(self.output_dir / "ci_metadata.json", "w") as f:
            json.dump(ci_metadata, f, indent=2)

        logger.info("✅ CI/CD environment setup completed")

    def _process_ci_results(self, results: Dict[str, Any]):
        """Process results for CI/CD pipeline."""
        logger.info("🔧 Processing CI/CD results...")

        # Save results to CI artifacts
        results_file = self.output_dir / "generation_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        # Create CI summary
        summary = {
            "status": "success" if results.get("success", True) else "failed",
            "models_generated": results.get("performance_metrics", {}).get("models_generated", 0),
            "errors_count": results.get("performance_metrics", {}).get("errors_count", 0),
            "success_rate": results.get("performance_metrics", {}).get("success_rate", 0),
            "total_time": results.get("performance_metrics", {}).get("total_time", 0),
            "timestamp": time.time(),
        }

        summary_file = self.output_dir / "ci_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info("✅ CI/CD results processing completed")

    def _validate_performance(self, results: Dict[str, Any]):
        """Validate performance against thresholds."""
        logger.info("📊 Validating performance...")

        performance = results.get("performance_metrics", {})
        total_time = performance.get("total_time", 0)
        error_rate = performance.get("errors_count", 0) / max(len(results.get("source_paths", [])), 1)

        # Check time threshold
        if total_time > self.config["performance_threshold"]:
            logger.warning(f"⚠️  Performance threshold exceeded: {total_time:.2f}s > {self.config['performance_threshold']}s")

        # Check error threshold
        if error_rate > self.config["error_threshold"]:
            logger.warning(f"⚠️  Error threshold exceeded: {error_rate:.1%} > {self.config['error_threshold']:.1%}")

        logger.info("✅ Performance validation completed")

    def _manage_artifacts(self, results: Dict[str, Any]):
        """Manage CI/CD artifacts."""
        logger.info("🗂️  Managing CI/CD artifacts...")

        # Keep only recent artifacts
        artifacts_to_keep = self.config["artifacts_to_keep"]

        # List all artifact directories
        artifact_dirs = [d for d in self.output_dir.parent.iterdir() if d.is_dir() and d.name.startswith("ci_activity_models")]

        if len(artifact_dirs) > artifacts_to_keep:
            # Sort by modification time and remove old ones
            artifact_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for old_dir in artifact_dirs[artifacts_to_keep:]:
                try:
                    import shutil

                    shutil.rmtree(old_dir)
                    logger.info(f"🗑️  Removed old artifact directory: {old_dir}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to remove old artifact: {old_dir} - {e}")

        logger.info("✅ Artifact management completed")

    def _generate_ci_report(self, results: Dict[str, Any]) -> str:
        """Generate CI/CD specific report."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("CI/CD ACTIVITY MODEL GENERATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        # CI Environment
        report_lines.append("🔧 CI/CD ENVIRONMENT")
        report_lines.append(f"  Environment: {results['ci_metadata']['environment']}")
        report_lines.append(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['ci_metadata']['timestamp']))}")
        report_lines.append("")

        # Generation Results
        if "performance_metrics" in results:
            perf = results["performance_metrics"]
            report_lines.append("📊 GENERATION RESULTS")
            report_lines.append(f"  Models Generated: {perf.get('models_generated', 0)}")
            report_lines.append(f"  Errors: {perf.get('errors_count', 0)}")
            report_lines.append(f"  Success Rate: {perf.get('success_rate', 0):.1%}")
            report_lines.append(f"  Total Time: {perf.get('total_time', 0):.2f}s")
            report_lines.append("")

        # Performance Validation
        report_lines.append("📈 PERFORMANCE VALIDATION")
        if "performance_metrics" in results:
            perf = results["performance_metrics"]
            total_time = perf.get("total_time", 0)
            error_rate = perf.get("errors_count", 0) / max(len(results.get("source_paths", [])), 1)

            time_status = "✅" if total_time <= self.config["performance_threshold"] else "⚠️"
            error_status = "✅" if error_rate <= self.config["error_threshold"] else "⚠️"

            report_lines.append(f"  {time_status} Time: {total_time:.2f}s (threshold: {self.config['performance_threshold']}s)")
            report_lines.append(f"  {error_status} Error Rate: {error_rate:.1%} (threshold: {self.config['error_threshold']:.1%})")
        else:
            report_lines.append("  ❌ No performance metrics available")
        report_lines.append("")

        # Artifacts
        report_lines.append("🗂️  ARTIFACTS")
        report_lines.append(f"  Output Directory: {self.output_dir.absolute()}")
        report_lines.append(f"  Results File: {self.output_dir / 'generation_results.json'}")
        report_lines.append(f"  Summary File: {self.output_dir / 'ci_summary.json'}")
        report_lines.append(f"  CI Metadata: {self.output_dir / 'ci_metadata.json'}")
        report_lines.append("")

        # Next Steps
        report_lines.append("🚀 NEXT STEPS")
        if results.get("success", True):
            report_lines.append("  ✅ Generation successful - artifacts available for deployment")
            report_lines.append("  📊 Review performance metrics and adjust thresholds if needed")
        else:
            report_lines.append("  ❌ Generation failed - review error logs and fix issues")
            report_lines.append("  🔧 Check configuration and dependencies")
        report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def _handle_ci_error(self, error_results: Dict[str, Any]):
        """Handle CI/CD errors."""
        logger.error("🚨 Handling CI/CD error...")

        # Save error results
        error_file = self.output_dir / "error_results.json"
        with open(error_file, "w") as f:
            json.dump(error_results, f, indent=2)

        # Create error summary
        error_summary = {
            "status": "failed",
            "error": error_results.get("error", "Unknown error"),
            "timestamp": time.time(),
            "environment": self.ci_environment,
        }

        error_summary_file = self.output_dir / "error_summary.json"
        with open(error_summary_file, "w") as f:
            json.dump(error_summary, f, indent=2)

        logger.error("✅ CI/CD error handling completed")


def main():
    """Main CLI interface for CI/CD integration."""
    parser = argparse.ArgumentParser(
        description="CI/CD integration for activity model generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default configuration
  python ci_activity_models.py
  
  # Run with custom config
  python ci_activity_models.py --config ci_config.json
  
  # Run with custom source paths
  python ci_activity_models.py --source-paths src/ tests/ --output-dir custom_output/
  
  # Run without round-trip integration
  python ci_activity_models.py --no-round-trip
        """,
    )

    parser.add_argument("--config", help="Configuration file path")

    parser.add_argument("--source-paths", nargs="+", help="Override source paths from config")

    parser.add_argument("--output-dir", help="Override output directory from config")

    parser.add_argument(
        "--no-round-trip",
        action="store_true",
        help="Disable round-trip system integration",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize CI generator
        output_dir = args.output_dir or "ci_activity_models"
        generator = CIActivityModelGenerator(output_dir=output_dir, config_file=args.config)

        # Run generation
        results = generator.run_generation(source_paths=args.source_paths, include_round_trip=not args.no_round_trip)

        # Display CI report
        if "ci_report" in results:
            print(results["ci_report"])

        # Save CI report to file
        report_file = Path(output_dir) / "ci_report.txt"
        if "ci_report" in results:
            with open(report_file, "w") as f:
                f.write(results["ci_report"])
            logger.info(f"📄 CI report saved to: {report_file}")

        # Exit with appropriate code
        if results.get("success", True):
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("⏹️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Critical CI/CD error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
