"""
Visual Regression Testing System for Observatory Dashboard

Provides automated visual regression testing using Selenium/Puppeteer to detect
UI changes and trigger immediate rollbacks when regressions are detected.
"""

import asyncio
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import logging
import json

from PIL import Image, ImageChops
import numpy as np

from .exceptions import VisualRegressionError
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker

logger = logging.getLogger(__name__)


class RegressionSeverity(str, Enum):
    """Severity levels for visual regressions"""
    MINOR = "minor"          # Small cosmetic changes
    MODERATE = "moderate"    # Noticeable changes that don't break functionality
    MAJOR = "major"         # Significant changes that may affect usability
    CRITICAL = "critical"   # Changes that break core functionality


class VisualTestStatus(str, Enum):
    """Status of visual regression tests"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class VisualDiff:
    """Visual difference detection result"""
    similarity_score: float  # 0.0 = completely different, 1.0 = identical
    pixel_diff_count: int
    total_pixels: int
    diff_percentage: float
    severity: RegressionSeverity
    diff_image_path: Optional[str] = None
    hotspots: List[Dict[str, Any]] = None  # Areas of significant change
    
    @property
    def is_regression(self) -> bool:
        """Check if this represents a visual regression"""
        return self.similarity_score < 0.95  # 95% similarity threshold


@dataclass
class VisualTestResult:
    """Visual regression test result"""
    test_id: str
    url: str
    viewport_size: Tuple[int, int]
    timestamp: datetime
    status: VisualTestStatus
    baseline_path: str
    current_path: str
    diff: Optional[VisualDiff] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    browser_info: Dict[str, str] = None


class VisualRegressionTester:
    """
    Visual regression testing system using Selenium WebDriver
    
    Captures screenshots of Observatory dashboard and compares them against
    baseline images to detect visual regressions.
    """
    
    def __init__(
        self,
        baseline_dir: str = "tests/visual_regression/baselines",
        output_dir: str = "tests/visual_regression/results",
        diff_threshold: float = 0.95,
        pixel_threshold: int = 100
    ):
        self.baseline_dir = Path(baseline_dir)
        self.output_dir = Path(output_dir)
        self.diff_threshold = diff_threshold
        self.pixel_threshold = pixel_threshold
        
        # Create directories if they don't exist
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self._driver = None
        self._test_results: List[VisualTestResult] = []
    
    async def initialize_driver(self, headless: bool = True) -> None:
        """Initialize Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            
            self._driver = webdriver.Chrome(options=chrome_options)
            self._driver.implicitly_wait(10)
            
            logger.info("Visual regression testing driver initialized")
            
        except ImportError:
            raise VisualRegressionError(
                "Selenium not installed. Run: pip install selenium",
                error_code="SELENIUM_MISSING"
            )
        except Exception as e:
            raise VisualRegressionError(
                f"Failed to initialize WebDriver: {str(e)}",
                error_code="DRIVER_INIT_FAILED"
            )
    
    async def cleanup_driver(self) -> None:
        """Clean up WebDriver resources"""
        if self._driver:
            try:
                self._driver.quit()
                self._driver = None
                logger.info("Visual regression testing driver cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up driver: {e}")
    
    async def capture_screenshot(
        self,
        url: str,
        test_id: str,
        viewport_size: Tuple[int, int] = (1920, 1080),
        wait_for_element: Optional[str] = None,
        wait_timeout: int = 30
    ) -> str:
        """
        Capture screenshot of the specified URL
        
        Args:
            url: URL to capture
            test_id: Unique identifier for this test
            viewport_size: Browser viewport size
            wait_for_element: CSS selector to wait for before capturing
            wait_timeout: Maximum time to wait for element
            
        Returns:
            Path to captured screenshot
        """
        if not self._driver:
            await self.initialize_driver()
        
        try:
            # Set viewport size
            self._driver.set_window_size(*viewport_size)
            
            # Navigate to URL
            self._driver.get(url)
            
            # Wait for specific element if specified
            if wait_for_element:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(self._driver, wait_timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
            
            # Additional wait for dynamic content
            await asyncio.sleep(2)
            
            # Capture screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{test_id}_{timestamp}.png"
            screenshot_path = self.output_dir / filename
            
            self._driver.save_screenshot(str(screenshot_path))
            
            logger.info(f"Screenshot captured: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            raise VisualRegressionError(
                f"Failed to capture screenshot: {str(e)}",
                error_code="SCREENSHOT_FAILED"
            )
    
    def compare_images(self, baseline_path: str, current_path: str) -> VisualDiff:
        """
        Compare two images and detect visual differences
        
        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            
        Returns:
            VisualDiff object with comparison results
        """
        try:
            # Load images
            baseline = Image.open(baseline_path).convert('RGB')
            current = Image.open(current_path).convert('RGB')
            
            # Ensure images are same size
            if baseline.size != current.size:
                logger.warning(f"Image size mismatch: {baseline.size} vs {current.size}")
                current = current.resize(baseline.size, Image.Resampling.LANCZOS)
            
            # Calculate pixel differences
            diff_image = ImageChops.difference(baseline, current)
            
            # Convert to numpy arrays for analysis
            baseline_array = np.array(baseline)
            current_array = np.array(current)
            diff_array = np.array(diff_image)
            
            # Calculate metrics
            total_pixels = baseline_array.shape[0] * baseline_array.shape[1]
            
            # Count pixels with significant differences (threshold > 30 for any RGB channel)
            significant_diff = np.any(diff_array > 30, axis=2)
            pixel_diff_count = np.sum(significant_diff)
            
            diff_percentage = (pixel_diff_count / total_pixels) * 100
            similarity_score = 1.0 - (diff_percentage / 100.0)
            
            # Determine severity
            severity = self._determine_severity(diff_percentage, pixel_diff_count)
            
            # Save diff image if there are significant differences
            diff_image_path = None
            if pixel_diff_count > self.pixel_threshold:
                diff_filename = f"diff_{int(time.time())}.png"
                diff_image_path = str(self.output_dir / diff_filename)
                
                # Enhance diff image for visibility
                enhanced_diff = self._enhance_diff_image(diff_image)
                enhanced_diff.save(diff_image_path)
            
            # Find hotspots (areas of concentrated changes)
            hotspots = self._find_hotspots(significant_diff) if pixel_diff_count > 0 else []
            
            return VisualDiff(
                similarity_score=similarity_score,
                pixel_diff_count=pixel_diff_count,
                total_pixels=total_pixels,
                diff_percentage=diff_percentage,
                severity=severity,
                diff_image_path=diff_image_path,
                hotspots=hotspots
            )
            
        except Exception as e:
            raise VisualRegressionError(
                f"Failed to compare images: {str(e)}",
                error_code="IMAGE_COMPARISON_FAILED"
            )
    
    def _determine_severity(self, diff_percentage: float, pixel_count: int) -> RegressionSeverity:
        """Determine severity of visual regression"""
        if diff_percentage > 20 or pixel_count > 50000:
            return RegressionSeverity.CRITICAL
        elif diff_percentage > 10 or pixel_count > 20000:
            return RegressionSeverity.MAJOR
        elif diff_percentage > 5 or pixel_count > 5000:
            return RegressionSeverity.MODERATE
        else:
            return RegressionSeverity.MINOR
    
    def _enhance_diff_image(self, diff_image: Image.Image) -> Image.Image:
        """Enhance diff image for better visibility"""
        # Convert to numpy array
        diff_array = np.array(diff_image)
        
        # Amplify differences
        enhanced = np.where(diff_array > 10, diff_array * 3, diff_array)
        enhanced = np.clip(enhanced, 0, 255)
        
        return Image.fromarray(enhanced.astype(np.uint8))
    
    def _find_hotspots(self, diff_mask: np.ndarray) -> List[Dict[str, Any]]:
        """Find areas of concentrated visual changes"""
        try:
            from scipy import ndimage
            from skimage.measure import label, regionprops
            
            # Label connected components
            labeled = label(diff_mask)
            regions = regionprops(labeled)
            
            hotspots = []
            for region in regions:
                if region.area > 100:  # Only consider significant regions
                    minr, minc, maxr, maxc = region.bbox
                    hotspots.append({
                        'x': int(minc),
                        'y': int(minr),
                        'width': int(maxc - minc),
                        'height': int(maxr - minr),
                        'area': int(region.area),
                        'centroid': [int(region.centroid[1]), int(region.centroid[0])]
                    })
            
            # Sort by area (largest first)
            hotspots.sort(key=lambda x: x['area'], reverse=True)
            return hotspots[:10]  # Return top 10 hotspots
            
        except ImportError:
            logger.warning("scipy/scikit-image not available for hotspot detection")
            return []
        except Exception as e:
            logger.error(f"Error finding hotspots: {e}")
            return []
    
    async def run_test(
        self,
        url: str,
        test_id: str,
        viewport_size: Tuple[int, int] = (1920, 1080),
        wait_for_element: Optional[str] = None,
        update_baseline: bool = False
    ) -> VisualTestResult:
        """
        Run visual regression test for a specific URL
        
        Args:
            url: URL to test
            test_id: Unique identifier for this test
            viewport_size: Browser viewport size
            wait_for_element: CSS selector to wait for
            update_baseline: Whether to update baseline image
            
        Returns:
            VisualTestResult object
        """
        start_time = time.time()
        
        result = VisualTestResult(
            test_id=test_id,
            url=url,
            viewport_size=viewport_size,
            timestamp=datetime.utcnow(),
            status=VisualVisualTestStatus.RUNNING,
            baseline_path="",
            current_path="",
            browser_info=self._get_browser_info()
        )
        
        try:
            # Capture current screenshot
            current_path = await self.capture_screenshot(
                url, test_id, viewport_size, wait_for_element
            )
            result.current_path = current_path
            
            # Determine baseline path
            baseline_filename = f"{test_id}_baseline.png"
            baseline_path = str(self.baseline_dir / baseline_filename)
            result.baseline_path = baseline_path
            
            if update_baseline or not os.path.exists(baseline_path):
                # Create or update baseline
                import shutil
                shutil.copy2(current_path, baseline_path)
                result.status = VisualTestStatus.PASSED
                logger.info(f"Baseline updated for test: {test_id}")
            else:
                # Compare with existing baseline
                diff = self.compare_images(baseline_path, current_path)
                result.diff = diff
                
                if diff.is_regression:
                    result.status = VisualTestStatus.FAILED
                    logger.warning(f"Visual regression detected in test: {test_id}")
                    logger.warning(f"Similarity: {diff.similarity_score:.3f}, "
                                 f"Diff: {diff.diff_percentage:.2f}%, "
                                 f"Severity: {diff.severity}")
                else:
                    result.status = VisualTestStatus.PASSED
                    logger.info(f"Visual regression test passed: {test_id}")
            
        except Exception as e:
            result.status = VisualTestStatus.ERROR
            result.error_message = str(e)
            logger.error(f"Visual regression test error: {e}")
        
        finally:
            result.execution_time = time.time() - start_time
            self._test_results.append(result)
        
        return result
    
    def _get_browser_info(self) -> Dict[str, str]:
        """Get browser information"""
        if not self._driver:
            return {}
        
        try:
            capabilities = self._driver.capabilities
            return {
                'browser_name': capabilities.get('browserName', 'unknown'),
                'browser_version': capabilities.get('browserVersion', 'unknown'),
                'platform': capabilities.get('platformName', 'unknown'),
                'driver_version': capabilities.get('chrome', {}).get('chromedriverVersion', 'unknown')
            }
        except Exception:
            return {}
    
    async def run_test_suite(
        self,
        test_configs: List[Dict[str, Any]],
        parallel: bool = False,
        max_workers: int = 3
    ) -> List[VisualTestResult]:
        """
        Run a suite of visual regression tests
        
        Args:
            test_configs: List of test configurations
            parallel: Whether to run tests in parallel
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of VisualTestResult objects
        """
        if not await feature_flags.is_enabled(FeatureFlag.VISUAL_REGRESSION_TESTING):
            logger.info("Visual regression testing is disabled")
            return []
        
        logger.info(f"Running visual regression test suite with {len(test_configs)} tests")
        
        if parallel and len(test_configs) > 1:
            # Run tests in parallel
            semaphore = asyncio.Semaphore(max_workers)
            
            async def run_single_test(config):
                async with semaphore:
                    return await self.run_test(**config)
            
            tasks = [run_single_test(config) for config in test_configs]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Test {i} failed with exception: {result}")
                    # Create error result
                    error_result = VisualTestResult(
                        test_id=test_configs[i].get('test_id', f'test_{i}'),
                        url=test_configs[i].get('url', ''),
                        viewport_size=test_configs[i].get('viewport_size', (1920, 1080)),
                        timestamp=datetime.utcnow(),
                        status=VisualTestStatus.ERROR,
                        baseline_path='',
                        current_path='',
                        error_message=str(result)
                    )
                    valid_results.append(error_result)
                else:
                    valid_results.append(result)
            
            return valid_results
        else:
            # Run tests sequentially
            results = []
            for config in test_configs:
                result = await self.run_test(**config)
                results.append(result)
            
            return results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results"""
        if not self._test_results:
            return {'total': 0, 'passed': 0, 'failed': 0, 'error': 0}
        
        summary = {
            'total': len(self._test_results),
            'passed': sum(1 for r in self._test_results if r.status == VisualTestStatus.PASSED),
            'failed': sum(1 for r in self._test_results if r.status == VisualTestStatus.FAILED),
            'error': sum(1 for r in self._test_results if r.status == VisualTestStatus.ERROR),
            'regressions': []
        }
        
        # Collect regression details
        for result in self._test_results:
            if result.status == VisualTestStatus.FAILED and result.diff:
                summary['regressions'].append({
                    'test_id': result.test_id,
                    'url': result.url,
                    'severity': result.diff.severity,
                    'similarity_score': result.diff.similarity_score,
                    'diff_percentage': result.diff.diff_percentage
                })
        
        return summary


class AutoRollbackManager:
    """
    Manages automatic rollback when visual regressions are detected
    """
    
    def __init__(self, rollback_threshold: RegressionSeverity = RegressionSeverity.MAJOR):
        self.rollback_threshold = rollback_threshold
        self.rollback_history: List[Dict[str, Any]] = []
    
    async def evaluate_rollback(self, test_results: List[VisualTestResult]) -> bool:
        """
        Evaluate if rollback should be triggered based on test results
        
        Args:
            test_results: List of visual regression test results
            
        Returns:
            True if rollback should be triggered
        """
        if not await feature_flags.is_enabled(FeatureFlag.AUTO_ROLLBACK):
            logger.info("Auto-rollback is disabled")
            return False
        
        critical_regressions = []
        major_regressions = []
        
        for result in test_results:
            if result.status == VisualTestStatus.FAILED and result.diff:
                if result.diff.severity == RegressionSeverity.CRITICAL:
                    critical_regressions.append(result)
                elif result.diff.severity == RegressionSeverity.MAJOR:
                    major_regressions.append(result)
        
        # Trigger rollback conditions
        should_rollback = (
            len(critical_regressions) > 0 or  # Any critical regression
            len(major_regressions) > 2 or     # More than 2 major regressions
            (len(major_regressions) > 0 and self.rollback_threshold == RegressionSeverity.MAJOR)
        )
        
        if should_rollback:
            logger.error(f"Rollback triggered: {len(critical_regressions)} critical, "
                        f"{len(major_regressions)} major regressions")
            
            rollback_event = {
                'timestamp': datetime.utcnow().isoformat(),
                'trigger': 'visual_regression',
                'critical_count': len(critical_regressions),
                'major_count': len(major_regressions),
                'affected_tests': [r.test_id for r in critical_regressions + major_regressions]
            }
            self.rollback_history.append(rollback_event)
        
        return should_rollback
    
    async def execute_rollback(self) -> bool:
        """
        Execute rollback procedure
        
        Returns:
            True if rollback was successful
        """
        try:
            logger.info("Executing automatic rollback due to visual regressions")
            
            # This would integrate with your deployment system
            # For now, we'll simulate the rollback process
            
            # 1. Disable problematic features via feature flags
            await self._disable_risky_features()
            
            # 2. Trigger deployment rollback (would integrate with your CI/CD)
            rollback_success = await self._trigger_deployment_rollback()
            
            if rollback_success:
                logger.info("Automatic rollback completed successfully")
                return True
            else:
                logger.error("Automatic rollback failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during rollback execution: {e}")
            return False
    
    async def _disable_risky_features(self) -> None:
        """Disable features that might be causing visual regressions"""
        risky_features = [
            FeatureFlag.DOCTOR_STATUS_DISPLAY,
            FeatureFlag.REAL_TIME_CHAT,
            FeatureFlag.QUEUE_STATUS_DISPLAY
        ]
        
        for feature in risky_features:
            await feature_flags.set_flag(feature.value, False)
            logger.info(f"Disabled feature flag: {feature.value}")
    
    async def _trigger_deployment_rollback(self) -> bool:
        """Trigger deployment rollback (placeholder for actual implementation)"""
        # This would integrate with your actual deployment system
        # For example: kubectl rollout undo, docker service rollback, etc.
        
        logger.info("Deployment rollback would be triggered here")
        # Simulate rollback delay
        await asyncio.sleep(1)
        return True


# Global instances
visual_tester = VisualRegressionTester()
rollback_manager = AutoRollbackManager()


async def run_observatory_visual_tests(
    base_url: str = "http://localhost:8000",
    update_baselines: bool = False
) -> Dict[str, Any]:
    """
    Run visual regression tests for Observatory dashboard
    
    Args:
        base_url: Base URL of Observatory dashboard
        update_baselines: Whether to update baseline images
        
    Returns:
        Test summary and rollback decision
    """
    test_configs = [
        {
            'test_id': 'observatory_dashboard',
            'url': f'{base_url}/',
            'wait_for_element': '.dashboard-container',
            'update_baseline': update_baselines
        },
        {
            'test_id': 'observatory_metrics',
            'url': f'{base_url}/metrics',
            'wait_for_element': '.metrics-container',
            'update_baseline': update_baselines
        },
        {
            'test_id': 'observatory_alerts',
            'url': f'{base_url}/alerts',
            'wait_for_element': '.alerts-container',
            'update_baseline': update_baselines
        }
    ]
    
    try:
        # Run visual regression tests with circuit breaker protection
        results = await with_circuit_breaker(
            'visual_regression_tests',
            visual_tester.run_test_suite,
            test_configs,
            parallel=True,
            failure_threshold=2,
            recovery_timeout=300  # 5 minutes
        )
        
        # Get test summary
        summary = visual_tester.get_test_summary()
        
        # Evaluate rollback
        should_rollback = await rollback_manager.evaluate_rollback(results)
        
        if should_rollback:
            rollback_success = await rollback_manager.execute_rollback()
            summary['rollback_triggered'] = True
            summary['rollback_success'] = rollback_success
        else:
            summary['rollback_triggered'] = False
        
        return summary
        
    finally:
        await visual_tester.cleanup_driver()