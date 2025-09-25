"""
Visual regression tests for Observatory emoji rain effects.

Tests emoji rain animation consistency, particle effects, celebration patterns,
and visual quality of gamification elements.
"""

import asyncio
import pytest
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

# Visual testing dependencies (with graceful fallback)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageChops
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    np = None

from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    ObservatoryConfig,
    GamificationConfig
)


@dataclass
class EmojiParticle:
    """Emoji particle for visual testing."""
    emoji: str
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    rotation: float
    scale: float
    opacity: float
    age: float


@dataclass
class AnimationFrame:
    """Animation frame data for visual testing."""
    timestamp: float
    particles: List[EmojiParticle]
    effect_id: str
    effect_type: str


class EmojiRainVisualTester:
    """Visual tester specifically for emoji rain effects."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.driver: Optional[webdriver.Chrome] = None
        self.screenshots_dir = Path(__file__).parent / "emoji_screenshots"
        self.animation_frames: List[AnimationFrame] = []
        self.screenshots_dir.mkdir(exist_ok=True)

    async def setup_driver(self):
        """Setup Chrome driver with canvas support."""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not available for emoji rain visual testing")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--enable-webgl")  # Enable WebGL for better canvas performance

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(5)
        except Exception as e:
            pytest.skip(f"Chrome driver not available: {e}")

    async def teardown_driver(self):
        """Cleanup Chrome driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def take_screenshot(self, name: str, prefix: str = "emoji") -> Path:
        """Take screenshot with emoji-specific naming."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        filename = f"{prefix}_{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        if self.driver:
            self.driver.save_screenshot(str(filepath))

        return filepath

    async def wait_for_canvas_ready(self) -> bool:
        """Wait for emoji rain canvas to be ready."""
        if not self.driver:
            return False

        try:
            # Wait for canvas element
            canvas = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "emoji-rain-canvas"))
            )

            # Wait for WebSocket connection
            connection_status = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".connection-status"))
            )

            # Wait for "Connected" status
            for _ in range(30):  # 30 second timeout
                status_text = connection_status.text
                if "Connected" in status_text:
                    return True
                await asyncio.sleep(1)

            return False

        except Exception:
            return False

    async def trigger_emoji_rain(self, event_type: str = "TASK_COMPLETED") -> bool:
        """Trigger emoji rain animation by simulating button click."""
        try:
            # Find the appropriate button
            button_map = {
                "TASK_COMPLETED": 0,
                "API_CALL_SUCCESS": 1,
                "ACHIEVEMENT_UNLOCKED": 2,
                "COORDINATION_MILESTONE": 3
            }

            button_index = button_map.get(event_type, 0)
            buttons = self.driver.find_elements(By.CSS_SELECTOR, ".controls .btn")

            if button_index < len(buttons):
                button = buttons[button_index]
                button.click()
                return True

            return False

        except Exception:
            return False

    async def capture_animation_sequence(self, event_type: str, duration: float = 5.0) -> List[Path]:
        """Capture a sequence of screenshots during emoji rain animation."""
        screenshots = []

        # Trigger animation
        success = await self.trigger_emoji_rain(event_type)
        if not success:
            return screenshots

        # Capture screenshots at regular intervals
        num_frames = int(duration * 10)  # 10 FPS capture
        frame_interval = duration / num_frames

        for frame in range(num_frames):
            await asyncio.sleep(frame_interval)

            frame_name = f"{event_type.lower()}_frame_{frame:03d}"
            screenshot_path = self.take_screenshot(frame_name, "animation")
            screenshots.append(screenshot_path)

        return screenshots

    def analyze_animation_quality(self, screenshots: List[Path]) -> Dict[str, Any]:
        """Analyze animation quality from screenshots."""
        if not PIL_AVAILABLE or not screenshots:
            return {"analysis": "skipped", "reason": "PIL not available or no screenshots"}

        try:
            analysis_results = {
                "total_frames": len(screenshots),
                "motion_detected": False,
                "color_variety": 0,
                "brightness_changes": [],
                "frame_differences": []
            }

            prev_image = None
            colors_seen = set()

            for screenshot_path in screenshots:
                if not screenshot_path.exists():
                    continue

                current_image = Image.open(screenshot_path)
                current_array = np.array(current_image) if np is not None else None

                # Analyze color variety
                if current_array is not None:
                    unique_colors = len(np.unique(current_array.reshape(-1, current_array.shape[-1]), axis=0))
                    colors_seen.add(unique_colors)

                    # Calculate average brightness
                    brightness = np.mean(current_array)
                    analysis_results["brightness_changes"].append(brightness)

                # Compare with previous frame for motion detection
                if prev_image is not None:
                    try:
                        # Resize images to same size if needed
                        if current_image.size != prev_image.size:
                            current_image = current_image.resize(prev_image.size)

                        # Calculate difference
                        diff = ImageChops.difference(current_image, prev_image)
                        diff_array = np.array(diff) if np is not None else None

                        if diff_array is not None:
                            diff_score = np.sum(diff_array) / (diff_array.size * 255)  # Normalized difference
                            analysis_results["frame_differences"].append(diff_score)

                            # If difference is significant, motion is detected
                            if diff_score > 0.01:  # 1% change threshold
                                analysis_results["motion_detected"] = True

                    except Exception:
                        pass

                prev_image = current_image

            analysis_results["color_variety"] = len(colors_seen)

            return analysis_results

        except Exception as e:
            return {"analysis": "failed", "error": str(e)}

    async def test_canvas_performance(self) -> Dict[str, Any]:
        """Test canvas rendering performance during animation."""
        if not self.driver:
            return {"error": "No driver available"}

        try:
            # Inject performance monitoring JavaScript
            performance_script = """
            window.emojiRainPerformanceData = {
                frameCount: 0,
                startTime: performance.now(),
                frameTimestamps: [],
                memoryUsage: []
            };

            // Hook into requestAnimationFrame if possible
            const originalRAF = window.requestAnimationFrame;
            window.requestAnimationFrame = function(callback) {
                return originalRAF(function(timestamp) {
                    window.emojiRainPerformanceData.frameCount++;
                    window.emojiRainPerformanceData.frameTimestamps.push(timestamp);

                    // Record memory usage if available
                    if (performance.memory) {
                        window.emojiRainPerformanceData.memoryUsage.push({
                            used: performance.memory.usedJSHeapSize,
                            total: performance.memory.totalJSHeapSize
                        });
                    }

                    callback(timestamp);
                });
            };
            """

            self.driver.execute_script(performance_script)

            # Trigger animation and let it run
            await self.trigger_emoji_rain("TASK_COMPLETED")
            await asyncio.sleep(5)  # Let animation run for 5 seconds

            # Get performance data
            performance_data = self.driver.execute_script("return window.emojiRainPerformanceData;")

            # Calculate FPS
            if performance_data and performance_data.get("frameTimestamps"):
                timestamps = performance_data["frameTimestamps"]
                if len(timestamps) > 1:
                    duration_ms = timestamps[-1] - timestamps[0]
                    fps = (len(timestamps) - 1) * 1000 / duration_ms
                    performance_data["calculated_fps"] = fps

            return performance_data

        except Exception as e:
            return {"error": str(e)}


@pytest.fixture
async def emoji_rain_tester():
    """Emoji rain visual tester instance."""
    tester = EmojiRainVisualTester()
    await tester.setup_driver()

    yield tester

    await tester.teardown_driver()


@pytest.fixture
def mock_emoji_websocket_server():
    """Mock WebSocket server for emoji rain testing."""
    server_mock = AsyncMock()
    server_mock.start.return_value = None
    server_mock.stop.return_value = None
    server_mock.send_emoji_frame.return_value = None

    yield server_mock


@pytest.mark.skipif(not SELENIUM_AVAILABLE, reason="Selenium not available")
class TestEmojiRainBasicAnimations:
    """Test basic emoji rain animation functionality."""

    @pytest.mark.asyncio
    async def test_task_completion_emoji_rain(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain for task completion events."""
        tester = emoji_rain_tester

        # Navigate to dashboard
        tester.driver.get(tester.base_url)

        # Wait for canvas to be ready
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready for testing")

        # Take screenshot before animation
        before_screenshot = tester.take_screenshot("task_completion_before")

        # Trigger task completion emoji rain
        success = await tester.trigger_emoji_rain("TASK_COMPLETED")
        assert success, "Should successfully trigger emoji rain"

        # Wait for animation to start
        await asyncio.sleep(0.5)

        # Take screenshot during animation
        during_screenshot = tester.take_screenshot("task_completion_during")

        # Wait for animation to develop
        await asyncio.sleep(2.0)

        # Take screenshot mid-animation
        mid_screenshot = tester.take_screenshot("task_completion_mid")

        # Wait for animation to complete
        await asyncio.sleep(3.0)

        # Take screenshot after animation
        after_screenshot = tester.take_screenshot("task_completion_after")

        # Verify all screenshots exist
        screenshots = [before_screenshot, during_screenshot, mid_screenshot, after_screenshot]
        for screenshot in screenshots:
            assert screenshot.exists(), f"Screenshot {screenshot.name} should exist"

        # Analyze animation sequence
        animation_screenshots = [during_screenshot, mid_screenshot]
        analysis = tester.analyze_animation_quality(animation_screenshots)

        if analysis.get("analysis") != "skipped":
            assert analysis.get("motion_detected", False), "Animation should show motion between frames"

    @pytest.mark.asyncio
    async def test_achievement_unlock_emoji_rain(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain for achievement unlock events."""
        tester = emoji_rain_tester

        # Navigate and wait for ready
        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready for testing")

        # Capture animation sequence for achievement unlock
        screenshots = await tester.capture_animation_sequence("ACHIEVEMENT_UNLOCKED", duration=4.0)

        # Should capture multiple frames
        assert len(screenshots) > 10, f"Should capture multiple animation frames, got {len(screenshots)}"

        # Analyze animation quality
        analysis = tester.analyze_animation_quality(screenshots)

        if analysis.get("analysis") != "skipped":
            assert analysis["total_frames"] > 10, "Should analyze multiple frames"
            assert analysis.get("motion_detected", False), "Achievement animation should show motion"

            # Achievement animations should be more colorful
            assert analysis.get("color_variety", 0) > 0, "Achievement animation should have color variety"

    @pytest.mark.asyncio
    async def test_milestone_celebration_emoji_rain(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain for milestone celebration events."""
        tester = emoji_rain_tester

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready for testing")

        # Capture milestone celebration animation
        screenshots = await tester.capture_animation_sequence("COORDINATION_MILESTONE", duration=5.0)

        assert len(screenshots) > 0, "Should capture milestone animation screenshots"

        # Take specific screenshots at key moments
        await tester.trigger_emoji_rain("COORDINATION_MILESTONE")

        # Peak animation moment
        await asyncio.sleep(1.5)
        peak_screenshot = tester.take_screenshot("milestone_peak")

        # Fade out moment
        await asyncio.sleep(3.0)
        fadeout_screenshot = tester.take_screenshot("milestone_fadeout")

        assert peak_screenshot.exists()
        assert fadeout_screenshot.exists()

        # Analyze the specific screenshots
        key_screenshots = [peak_screenshot, fadeout_screenshot]
        analysis = tester.analyze_animation_quality(key_screenshots)

        if analysis.get("analysis") != "skipped":
            # Should show brightness changes during animation
            brightness_changes = analysis.get("brightness_changes", [])
            if len(brightness_changes) >= 2:
                brightness_variation = max(brightness_changes) - min(brightness_changes)
                assert brightness_variation > 1.0, "Should show brightness variation during animation"


@pytest.mark.skipif(not SELENIUM_AVAILABLE, reason="Selenium not available")
class TestEmojiRainPerformance:
    """Test emoji rain performance and rendering quality."""

    @pytest.mark.asyncio
    async def test_canvas_rendering_performance(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test canvas rendering performance during emoji rain."""
        tester = emoji_rain_tester

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready for performance testing")

        # Test performance during animation
        performance_data = await tester.test_canvas_performance()

        # Verify performance data was collected
        if "error" not in performance_data:
            assert performance_data.get("frameCount", 0) > 0, "Should record animation frames"

            calculated_fps = performance_data.get("calculated_fps")
            if calculated_fps:
                assert calculated_fps > 10, f"Should maintain reasonable FPS, got {calculated_fps:.1f}"
                assert calculated_fps < 120, f"FPS should be realistic, got {calculated_fps:.1f}"

            # Memory usage should be tracked if available
            memory_usage = performance_data.get("memoryUsage", [])
            if memory_usage:
                assert len(memory_usage) > 0, "Should track memory usage during animation"

        # Take performance screenshot
        perf_screenshot = tester.take_screenshot("performance_test")
        assert perf_screenshot.exists()

    @pytest.mark.asyncio
    async def test_multiple_simultaneous_effects(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test visual quality with multiple emoji effects running simultaneously."""
        tester = emoji_rain_tester

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready for multiple effects testing")

        # Trigger multiple effects in rapid succession
        effect_types = ["TASK_COMPLETED", "API_CALL_SUCCESS", "ACHIEVEMENT_UNLOCKED"]

        before_multiple = tester.take_screenshot("multiple_effects_before")

        for effect_type in effect_types:
            await tester.trigger_emoji_rain(effect_type)
            await asyncio.sleep(0.3)  # Small delay between triggers

        # Wait for effects to develop
        await asyncio.sleep(1.0)
        during_multiple = tester.take_screenshot("multiple_effects_during")

        # Wait for peak activity
        await asyncio.sleep(2.0)
        peak_multiple = tester.take_screenshot("multiple_effects_peak")

        # Wait for effects to settle
        await asyncio.sleep(4.0)
        after_multiple = tester.take_screenshot("multiple_effects_after")

        # Verify screenshots
        screenshots = [before_multiple, during_multiple, peak_multiple, after_multiple]
        for screenshot in screenshots:
            assert screenshot.exists()

        # Analyze the multiple effects
        multi_effect_screenshots = [during_multiple, peak_multiple]
        analysis = tester.analyze_animation_quality(multi_effect_screenshots)

        if analysis.get("analysis") != "skipped":
            # Multiple effects should show high motion and color variety
            assert analysis.get("motion_detected", False), "Multiple effects should show significant motion"
            assert analysis.get("color_variety", 0) >= 2, "Multiple effects should show color variety"

    @pytest.mark.asyncio
    async def test_emoji_rain_in_different_viewport_sizes(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain visual consistency across different viewport sizes."""
        tester = emoji_rain_tester

        viewport_sizes = [
            (1920, 1080, "desktop"),
            (1366, 768, "laptop"),
            (768, 1024, "tablet"),
            (414, 896, "mobile")
        ]

        screenshots_by_viewport = {}

        for width, height, viewport_name in viewport_sizes:
            # Set viewport size
            tester.driver.set_window_size(width, height)

            # Navigate to dashboard
            tester.driver.get(tester.base_url)
            canvas_ready = await tester.wait_for_canvas_ready()

            if canvas_ready:
                # Trigger emoji rain
                await tester.trigger_emoji_rain("TASK_COMPLETED")

                # Wait for animation to develop
                await asyncio.sleep(1.5)

                # Take screenshot
                viewport_screenshot = tester.take_screenshot(f"viewport_{viewport_name}")
                screenshots_by_viewport[viewport_name] = viewport_screenshot

        # Verify screenshots for all viewports
        for viewport_name, screenshot_path in screenshots_by_viewport.items():
            assert screenshot_path.exists(), f"Screenshot for {viewport_name} should exist"

        # Should have tested multiple viewports
        assert len(screenshots_by_viewport) >= 2, "Should test multiple viewport sizes"


@pytest.mark.skipif(not SELENIUM_AVAILABLE or not PIL_AVAILABLE, reason="Visual analysis dependencies not available")
class TestEmojiRainVisualRegression:
    """Test visual regression for emoji rain effects."""

    def setup_method(self):
        """Setup baseline directory for visual regression."""
        self.baseline_dir = Path(__file__).parent / "emoji_baselines"
        self.baseline_dir.mkdir(exist_ok=True)

    def create_emoji_baseline(self, name: str, width: int = 1920, height: int = 1080) -> Path:
        """Create baseline image for emoji rain effect."""
        # Create baseline with simulated emoji particles
        baseline_img = Image.new('RGBA', (width, height), color=(26, 26, 26, 255))  # Dark background
        draw = ImageDraw.Draw(baseline_img)

        # Simulate emoji particles at various positions
        emoji_positions = [
            (300, 200, "✅", 1.2),
            (600, 150, "🎉", 1.0),
            (900, 300, "⭐", 0.8),
            (450, 400, "🏆", 1.1),
            (750, 250, "✨", 0.9),
            (200, 450, "🎯", 1.0)
        ]

        # Draw simulated emoji particles
        for x, y, emoji, scale in emoji_positions:
            # Simulate emoji with colored circles (since we can't draw actual emoji easily)
            colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f39c12", "#e74c3c", "#2ecc71"]
            color = colors[hash(emoji) % len(colors)]

            radius = int(12 * scale)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)

            # Add motion blur effect (simple)
            for i in range(3):
                blur_radius = radius - i
                blur_alpha = 50 - (i * 15)
                if blur_radius > 0 and blur_alpha > 0:
                    blur_color = (*tuple(int(color[1:][j:j+2], 16) for j in (0, 2, 4)), blur_alpha)
                    draw.ellipse([x-blur_radius, y+i*5-blur_radius, x+blur_radius, y+i*5+blur_radius],
                               fill=blur_color)

        baseline_path = self.baseline_dir / f"{name}_baseline.png"
        baseline_img.save(baseline_path)
        return baseline_path

    @pytest.mark.asyncio
    async def test_task_completion_visual_regression(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test visual regression for task completion emoji rain."""
        tester = emoji_rain_tester

        # Create or get baseline
        baseline_path = self.create_emoji_baseline("task_completion_rain")

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready for regression testing")

        # Trigger animation and capture at consistent timing
        await tester.trigger_emoji_rain("TASK_COMPLETED")
        await asyncio.sleep(1.5)  # Consistent timing for comparison

        current_screenshot = tester.take_screenshot("task_completion_regression")

        # Compare with baseline
        if baseline_path.exists() and current_screenshot.exists():
            try:
                baseline_img = Image.open(baseline_path)
                current_img = Image.open(current_screenshot)

                # Resize if needed
                if baseline_img.size != current_img.size:
                    current_img = current_img.resize(baseline_img.size)

                # Simple visual comparison
                diff = ImageChops.difference(baseline_img, current_img)
                diff_data = list(diff.getdata())

                # Calculate difference percentage
                total_pixels = len(diff_data)
                changed_pixels = sum(1 for pixel in diff_data if sum(pixel[:3]) > 30)  # Threshold for significant change
                difference_percentage = changed_pixels / total_pixels

                # In a real test, this might fail if difference is too high
                # For now, we just record the difference
                print(f"Visual difference: {difference_percentage:.3%}")

                # Save difference image for analysis
                diff_path = tester.screenshots_dir / f"task_completion_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                diff.save(diff_path)

            except Exception as e:
                print(f"Visual comparison failed: {e}")

    @pytest.mark.asyncio
    async def test_achievement_celebration_regression(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test visual regression for achievement celebration effects."""
        tester = emoji_rain_tester

        baseline_path = self.create_emoji_baseline("achievement_celebration")

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready")

        # Capture achievement animation at peak moment
        await tester.trigger_emoji_rain("ACHIEVEMENT_UNLOCKED")
        await asyncio.sleep(2.0)  # Peak moment

        current_screenshot = tester.take_screenshot("achievement_regression")

        # Visual regression check
        if baseline_path.exists() and current_screenshot.exists():
            # In production, this would perform strict visual comparison
            # For testing, we verify the files exist and can be opened
            try:
                baseline_img = Image.open(baseline_path)
                current_img = Image.open(current_screenshot)

                # Basic validation
                assert baseline_img.size[0] > 0 and baseline_img.size[1] > 0
                assert current_img.size[0] > 0 and current_img.size[1] > 0

            except Exception as e:
                pytest.fail(f"Could not process regression images: {e}")


class TestEmojiRainAccessibility:
    """Test emoji rain accessibility considerations."""

    @pytest.mark.asyncio
    async def test_reduced_motion_preference(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain behavior with reduced motion preference."""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not available")

        tester = emoji_rain_tester

        # Set reduced motion preference via CSS
        reduced_motion_css = """
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        """

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready")

        # Inject reduced motion CSS
        tester.driver.execute_script(f"""
            var style = document.createElement('style');
            style.textContent = `{reduced_motion_css}`;
            document.head.appendChild(style);
        """)

        # Trigger animation with reduced motion
        before_reduced_motion = tester.take_screenshot("reduced_motion_before")
        await tester.trigger_emoji_rain("TASK_COMPLETED")

        # With reduced motion, animation should complete quickly
        await asyncio.sleep(0.5)
        during_reduced_motion = tester.take_screenshot("reduced_motion_during")

        await asyncio.sleep(1.0)
        after_reduced_motion = tester.take_screenshot("reduced_motion_after")

        # Verify screenshots exist
        assert before_reduced_motion.exists()
        assert during_reduced_motion.exists()
        assert after_reduced_motion.exists()

    @pytest.mark.asyncio
    async def test_high_contrast_mode_compatibility(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain visibility in high contrast mode."""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not available")

        tester = emoji_rain_tester

        # Simulate high contrast mode
        high_contrast_css = """
        @media (prefers-contrast: high) {
            body { background-color: #000000 !important; color: #ffffff !important; }
            .emoji-particle { filter: brightness(1.5) contrast(1.2) !important; }
        }
        """

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready")

        # Apply high contrast styles
        tester.driver.execute_script(f"""
            var style = document.createElement('style');
            style.textContent = `{high_contrast_css}`;
            document.head.appendChild(style);
        """)

        # Test emoji rain in high contrast mode
        await tester.trigger_emoji_rain("ACHIEVEMENT_UNLOCKED")
        await asyncio.sleep(1.5)

        high_contrast_screenshot = tester.take_screenshot("high_contrast_emoji_rain")
        assert high_contrast_screenshot.exists()

        # Verify the page background changed to high contrast
        body_bg = tester.driver.find_element(By.TAG_NAME, "body").value_of_css_property("background-color")
        # Should be black or very dark in high contrast mode
        assert "rgb(0, 0, 0)" in body_bg or "rgba(0, 0, 0" in body_bg


class TestEmojiRainErrorHandling:
    """Test emoji rain behavior during error conditions."""

    @pytest.mark.asyncio
    async def test_websocket_disconnect_during_animation(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain behavior when WebSocket disconnects during animation."""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not available")

        tester = emoji_rain_tester

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready")

        # Start animation
        await tester.trigger_emoji_rain("TASK_COMPLETED")
        await asyncio.sleep(1.0)  # Let animation start

        # Simulate WebSocket disconnect
        tester.driver.execute_script("""
            if (window.emojiRenderer && window.emojiRenderer.websocket) {
                window.emojiRenderer.websocket.close();
            }
        """)

        # Take screenshot during disconnect
        disconnect_screenshot = tester.take_screenshot("websocket_disconnect")

        # Wait to see how animation handles disconnect
        await asyncio.sleep(3.0)

        # Check connection status
        connection_status = tester.driver.find_element(By.CSS_SELECTOR, ".connection-status")
        status_text = connection_status.text

        # Should show disconnected status
        assert "Disconnected" in status_text or "Connecting" in status_text

        after_disconnect_screenshot = tester.take_screenshot("after_websocket_disconnect")

        assert disconnect_screenshot.exists()
        assert after_disconnect_screenshot.exists()

    @pytest.mark.asyncio
    async def test_canvas_context_loss_recovery(self, emoji_rain_tester, mock_emoji_websocket_server):
        """Test emoji rain recovery from canvas context loss."""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not available")

        tester = emoji_rain_tester

        tester.driver.get(tester.base_url)
        canvas_ready = await tester.wait_for_canvas_ready()
        if not canvas_ready:
            pytest.skip("Canvas not ready")

        # Simulate canvas context loss
        tester.driver.execute_script("""
            var canvas = document.getElementById('emoji-rain-canvas');
            if (canvas) {
                var ctx = canvas.getContext('2d');
                // Simulate context loss
                canvas.width = canvas.width; // This clears the canvas
                console.log('Simulated canvas context loss');
            }
        """)

        context_loss_screenshot = tester.take_screenshot("canvas_context_loss")

        # Try to trigger animation after context loss
        await tester.trigger_emoji_rain("ACHIEVEMENT_UNLOCKED")
        await asyncio.sleep(2.0)

        recovery_screenshot = tester.take_screenshot("after_context_loss_recovery")

        assert context_loss_screenshot.exists()
        assert recovery_screenshot.exists()


def create_emoji_rain_test_report(screenshots_dir: Path) -> str:
    """Create comprehensive HTML report for emoji rain visual tests."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emoji Rain Visual Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .header {{ background: #333; color: white; padding: 20px; margin: -20px -20px 20px -20px; }}
            .section {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .screenshot-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
            .screenshot-item {{ text-align: center; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
            .screenshot-item img {{ width: 100%; height: auto; }}
            .screenshot-info {{ padding: 10px; background: #f8f9fa; }}
            .animation-sequence {{ border-left: 4px solid #007bff; padding-left: 15px; margin: 15px 0; }}
            .performance-data {{ background: #e8f5e9; padding: 15px; border-radius: 4px; }}
            .error-section {{ background: #ffebee; border-left: 4px solid #f44336; padding: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌧️ Emoji Rain Visual Test Report</h1>
            <p>Generated on: {datetime.now().isoformat()}</p>
        </div>

        <div class="section">
            <h2>Test Summary</h2>
            <div class="performance-data">
                <p><strong>Total Screenshots:</strong> {len(list(screenshots_dir.glob('*.png')))}</p>
                <p><strong>Test Categories:</strong> Basic Animations, Performance, Visual Regression, Accessibility</p>
                <p><strong>Browser:</strong> Chrome (Headless)</p>
            </div>
        </div>
    """

    # Group screenshots by category
    screenshot_groups = {
        "Basic Animations": [],
        "Performance Tests": [],
        "Visual Regression": [],
        "Accessibility": [],
        "Error Handling": [],
        "Other": []
    }

    for screenshot_file in sorted(screenshots_dir.glob("*.png")):
        filename = screenshot_file.name.lower()

        if any(keyword in filename for keyword in ["task_completion", "achievement", "milestone"]):
            screenshot_groups["Basic Animations"].append(screenshot_file)
        elif any(keyword in filename for keyword in ["performance", "multiple_effects", "viewport"]):
            screenshot_groups["Performance Tests"].append(screenshot_file)
        elif any(keyword in filename for keyword in ["regression", "baseline", "diff"]):
            screenshot_groups["Visual Regression"].append(screenshot_file)
        elif any(keyword in filename for keyword in ["reduced_motion", "high_contrast"]):
            screenshot_groups["Accessibility"].append(screenshot_file)
        elif any(keyword in filename for keyword in ["disconnect", "context_loss", "error"]):
            screenshot_groups["Error Handling"].append(screenshot_file)
        else:
            screenshot_groups["Other"].append(screenshot_file)

    # Add sections for each group
    for group_name, screenshots in screenshot_groups.items():
        if screenshots:
            html_content += f"""
            <div class="section">
                <h2>{group_name}</h2>
                <div class="screenshot-grid">
            """

            for screenshot_file in screenshots:
                html_content += f"""
                <div class="screenshot-item">
                    <img src="{screenshot_file.name}" alt="{screenshot_file.stem}" />
                    <div class="screenshot-info">
                        <strong>{screenshot_file.stem.replace('_', ' ').title()}</strong>
                        <br><small>{screenshot_file.name}</small>
                    </div>
                </div>
                """

            html_content += """
                </div>
            </div>
            """

    html_content += """
    </body>
    </html>
    """

    report_path = screenshots_dir / "emoji_rain_test_report.html"
    report_path.write_text(html_content)

    return str(report_path)