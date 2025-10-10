#!/usr/bin/env python3
"""
Visual Regression Testing CLI Script

This script runs visual regression tests for the Observatory dashboard
and can trigger automatic rollbacks if regressions are detected.
"""

import asyncio
import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.observatory.ai_consultation.visual_regression import (
    run_observatory_visual_tests,
    visual_tester,
    rollback_manager
)
from beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load visual regression configuration"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return {}


async def run_tests(
    base_url: str,
    config_path: str,
    update_baselines: bool = False,
    parallel: bool = True,
    rollback_enabled: bool = True
) -> Dict[str, Any]:
    """
    Run visual regression tests
    
    Args:
        base_url: Base URL of Observatory dashboard
        config_path: Path to configuration file
        update_baselines: Whether to update baseline images
        parallel: Whether to run tests in parallel
        rollback_enabled: Whether to enable automatic rollback
        
    Returns:
        Test results summary
    """
    # Load configuration
    config = load_config(config_path)
    if not config:
        logger.warning("Using default configuration")
    
    # Enable visual regression testing
    await feature_flags.set_flag(FeatureFlag.VISUAL_REGRESSION_TESTING.value, True)
    
    if rollback_enabled:
        await feature_flags.set_flag(FeatureFlag.AUTO_ROLLBACK.value, True)
    else:
        await feature_flags.set_flag(FeatureFlag.AUTO_ROLLBACK.value, False)
    
    logger.info(f"Starting visual regression tests for {base_url}")
    logger.info(f"Update baselines: {update_baselines}")
    logger.info(f"Parallel execution: {parallel}")
    logger.info(f"Auto-rollback: {rollback_enabled}")
    
    try:
        # Run the tests
        summary = await run_observatory_visual_tests(
            base_url=base_url,
            update_baselines=update_baselines
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error running visual regression tests: {e}")
        return {
            'error': str(e),
            'total': 0,
            'passed': 0,
            'failed': 0,
            'rollback_triggered': False
        }


def print_summary(summary: Dict[str, Any]) -> None:
    """Print test results summary"""
    print("\n" + "="*60)
    print("VISUAL REGRESSION TEST RESULTS")
    print("="*60)
    
    if 'error' in summary:
        print(f"❌ ERROR: {summary['error']}")
        return
    
    total = summary.get('total', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    error = summary.get('error', 0)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {error}")
    
    if failed > 0:
        print(f"\n🔍 REGRESSIONS DETECTED:")
        for regression in summary.get('regressions', []):
            print(f"  - {regression['test_id']}: {regression['severity']} "
                  f"(similarity: {regression['similarity_score']:.3f})")
    
    if summary.get('rollback_triggered', False):
        rollback_success = summary.get('rollback_success', False)
        if rollback_success:
            print(f"\n🔄 AUTOMATIC ROLLBACK: ✅ SUCCESS")
        else:
            print(f"\n🔄 AUTOMATIC ROLLBACK: ❌ FAILED")
    
    print("="*60)


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Run visual regression tests for Observatory dashboard"
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Base URL of Observatory dashboard (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--config',
        default='config/visual_regression_config.json',
        help='Path to configuration file (default: config/visual_regression_config.json)'
    )
    
    parser.add_argument(
        '--update-baselines',
        action='store_true',
        help='Update baseline images instead of comparing'
    )
    
    parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='Disable parallel test execution'
    )
    
    parser.add_argument(
        '--no-rollback',
        action='store_true',
        help='Disable automatic rollback on regressions'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests
    summary = await run_tests(
        base_url=args.url,
        config_path=args.config,
        update_baselines=args.update_baselines,
        parallel=not args.no_parallel,
        rollback_enabled=not args.no_rollback
    )
    
    # Print results
    print_summary(summary)
    
    # Exit with appropriate code
    if 'error' in summary:
        sys.exit(2)  # Error
    elif summary.get('failed', 0) > 0:
        if summary.get('rollback_triggered', False):
            sys.exit(3)  # Regression with rollback
        else:
            sys.exit(1)  # Regression without rollback
    else:
        sys.exit(0)  # Success


if __name__ == "__main__":
    asyncio.run(main())