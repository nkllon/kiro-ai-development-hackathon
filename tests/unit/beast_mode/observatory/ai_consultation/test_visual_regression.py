"""
Unit tests for Visual Regression Testing System
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from PIL import Image
import numpy as np

from src.beast_mode.observatory.ai_consultation.visual_regression import (
    VisualRegressionTester,
    AutoRollbackManager,
    VisualDiff,
    VisualTestResult,
    VisualTestStatus,
    RegressionSeverity,
    run_observatory_visual_tests
)
from src.beast_mode.observatory.ai_consultation.exceptions import VisualRegressionError


class TestVisualDiff:
    """Test VisualDiff class"""
    
    def test_visual_diff_creation(self):
        """Test creating a VisualDiff object"""
        diff = VisualDiff(
            similarity_score=0.92,
            pixel_diff_count=1500,
            total_pixels=100000,
            diff_percentage=1.5,
            severity=RegressionSeverity.MINOR
        )
        
        assert diff.similarity_score == 0.92
        assert diff.pixel_diff_count == 1500
        assert diff.total_pixels == 100000
        assert diff.diff_percentage == 1.5
        assert diff.severity == RegressionSeverity.MINOR
        assert diff.is_regression == True  # Below 0.95 threshold
    
    def test_visual_diff_no_regression(self):
        """Test VisualDiff with no regression"""
        diff = VisualDiff(
            similarity_score=0.98,
            pixel_diff_count=100,
            total_pixels=100000,
            diff_percentage=0.1,
            severity=RegressionSeverity.MINOR
        )
        
        assert diff.is_regression == False  # Above 0.95 threshold


class TestVisualRegressionTester:
    """Test VisualRegressionTester class"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            baseline_dir = Path(temp_dir) / "baselines"
            output_dir = Path(temp_dir) / "results"
            baseline_dir.mkdir()
            output_dir.mkdir()
            
            yield {
                'baseline_dir': str(baseline_dir),
                'output_dir': str(output_dir)
            }
    
    @pytest.fixture
    def tester(self, temp_dirs):
        """Create VisualRegressionTester instance"""
        return VisualRegressionTester(
            baseline_dir=temp_dirs['baseline_dir'],
            output_dir=temp_dirs['output_dir']
        )
    
    def test_tester_initialization(self, tester):
        """Test tester initialization"""
        assert tester.diff_threshold == 0.95
        assert tester.pixel_threshold == 100
        assert tester.baseline_dir.exists()
        assert tester.output_dir.exists()
    
    def test_determine_severity(self, tester):
        """Test severity determination"""
        # Critical
        severity = tester._determine_severity(25.0, 60000)
        assert severity == RegressionSeverity.CRITICAL
        
        # Major
        severity = tester._determine_severity(15.0, 30000)
        assert severity == RegressionSeverity.MAJOR
        
        # Moderate
        severity = tester._determine_severity(7.0, 8000)
        assert severity == RegressionSeverity.MODERATE
        
        # Minor
        severity = tester._determine_severity(2.0, 1000)
        assert severity == RegressionSeverity.MINOR
    
    def test_enhance_diff_image(self, tester):
        """Test diff image enhancement"""
        # Create test image
        test_array = np.random.randint(0, 50, (100, 100, 3), dtype=np.uint8)
        test_image = Image.fromarray(test_array)
        
        enhanced = tester._enhance_diff_image(test_image)
        
        assert enhanced.size == test_image.size
        assert isinstance(enhanced, Image.Image)
    
    def test_compare_identical_images(self, tester, temp_dirs):
        """Test comparing identical images"""
        # Create identical test images
        test_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        image1 = Image.fromarray(test_array)
        image2 = Image.fromarray(test_array)
        
        path1 = Path(temp_dirs['baseline_dir']) / "test1.png"
        path2 = Path(temp_dirs['output_dir']) / "test2.png"
        
        image1.save(path1)
        image2.save(path2)
        
        diff = tester.compare_images(str(path1), str(path2))
        
        assert diff.similarity_score == 1.0
        assert diff.pixel_diff_count == 0
        assert diff.diff_percentage == 0.0
        assert diff.is_regression == False
    
    def test_compare_different_images(self, tester, temp_dirs):
        """Test comparing different images"""
        # Create different test images
        array1 = np.zeros((100, 100, 3), dtype=np.uint8)  # Black image
        array2 = np.full((100, 100, 3), 255, dtype=np.uint8)  # White image
        
        image1 = Image.fromarray(array1)
        image2 = Image.fromarray(array2)
        
        path1 = Path(temp_dirs['baseline_dir']) / "test1.png"
        path2 = Path(temp_dirs['output_dir']) / "test2.png"
        
        image1.save(path1)
        image2.save(path2)
        
        diff = tester.compare_images(str(path1), str(path2))
        
        assert diff.similarity_score < 0.5  # Very different
        assert diff.pixel_diff_count > 0
        assert diff.diff_percentage > 50.0
        assert diff.is_regression == True
        assert diff.severity == RegressionSeverity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_initialize_driver_missing_selenium(self, tester):
        """Test driver initialization with missing Selenium"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'selenium'")):
            with pytest.raises(VisualRegressionError, match="Selenium not installed"):
                await tester.initialize_driver()
    
    @pytest.mark.asyncio
    async def test_cleanup_driver(self, tester):
        """Test driver cleanup"""
        # Mock driver
        mock_driver = MagicMock()
        tester._driver = mock_driver
        
        await tester.cleanup_driver()
        
        mock_driver.quit.assert_called_once()
        assert tester._driver is None
    
    def test_get_browser_info_no_driver(self, tester):
        """Test getting browser info without driver"""
        info = tester._get_browser_info()
        assert info == {}
    
    def test_get_browser_info_with_driver(self, tester):
        """Test getting browser info with driver"""
        mock_driver = MagicMock()
        mock_driver.capabilities = {
            'browserName': 'chrome',
            'browserVersion': '91.0',
            'platformName': 'linux'
        }
        tester._driver = mock_driver
        
        info = tester._get_browser_info()
        
        assert info['browser_name'] == 'chrome'
        assert info['browser_version'] == '91.0'
        assert info['platform'] == 'linux'
    
    @pytest.mark.asyncio
    async def test_run_test_suite_disabled(self, tester):
        """Test running test suite when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.feature_flags') as mock_flags:
            mock_flags.is_enabled = AsyncMock(return_value=False)
            
            results = await tester.run_test_suite([])
            
            assert results == []
    
    def test_get_test_summary_empty(self, tester):
        """Test getting test summary with no results"""
        summary = tester.get_test_summary()
        
        assert summary['total'] == 0
        assert summary['passed'] == 0
        assert summary['failed'] == 0
        assert summary['error'] == 0


class TestAutoRollbackManager:
    """Test AutoRollbackManager class"""
    
    @pytest.fixture
    def rollback_manager(self):
        """Create AutoRollbackManager instance"""
        return AutoRollbackManager(rollback_threshold=RegressionSeverity.MAJOR)
    
    def create_test_result(self, test_id: str, status: VisualTestStatus, severity: RegressionSeverity = None):
        """Helper to create test results"""
        result = VisualTestResult(
            test_id=test_id,
            url="http://test.com",
            viewport_size=(1920, 1080),
            timestamp=None,
            status=status,
            baseline_path="",
            current_path=""
        )
        
        if status == VisualTestStatus.FAILED and severity:
            result.diff = VisualDiff(
                similarity_score=0.8,
                pixel_diff_count=1000,
                total_pixels=100000,
                diff_percentage=1.0,
                severity=severity
            )
        
        return result
    
    @pytest.mark.asyncio
    async def test_evaluate_rollback_disabled(self, rollback_manager):
        """Test rollback evaluation when auto-rollback is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.feature_flags') as mock_flags:
            mock_flags.is_enabled = AsyncMock(return_value=False)
            
            results = [self.create_test_result("test1", VisualTestStatus.FAILED, RegressionSeverity.CRITICAL)]
            should_rollback = await rollback_manager.evaluate_rollback(results)
            
            assert should_rollback is False
    
    @pytest.mark.asyncio
    async def test_evaluate_rollback_critical(self, rollback_manager):
        """Test rollback evaluation with critical regression"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.feature_flags') as mock_flags:
            mock_flags.is_enabled = AsyncMock(return_value=True)
            
            results = [
                self.create_test_result("test1", VisualTestStatus.PASSED),
                self.create_test_result("test2", VisualTestStatus.FAILED, RegressionSeverity.CRITICAL)
            ]
            
            should_rollback = await rollback_manager.evaluate_rollback(results)
            
            assert should_rollback is True
            assert len(rollback_manager.rollback_history) == 1
    
    @pytest.mark.asyncio
    async def test_evaluate_rollback_multiple_major(self, rollback_manager):
        """Test rollback evaluation with multiple major regressions"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.feature_flags') as mock_flags:
            mock_flags.is_enabled = AsyncMock(return_value=True)
            
            results = [
                self.create_test_result("test1", VisualTestStatus.FAILED, RegressionSeverity.MAJOR),
                self.create_test_result("test2", VisualTestStatus.FAILED, RegressionSeverity.MAJOR),
                self.create_test_result("test3", VisualTestStatus.FAILED, RegressionSeverity.MAJOR)
            ]
            
            should_rollback = await rollback_manager.evaluate_rollback(results)
            
            assert should_rollback is True
    
    @pytest.mark.asyncio
    async def test_evaluate_rollback_no_trigger(self, rollback_manager):
        """Test rollback evaluation with no trigger conditions"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.feature_flags') as mock_flags:
            mock_flags.is_enabled = AsyncMock(return_value=True)
            
            results = [
                self.create_test_result("test1", VisualTestStatus.PASSED),
                self.create_test_result("test2", VisualTestStatus.FAILED, RegressionSeverity.MINOR)
            ]
            
            should_rollback = await rollback_manager.evaluate_rollback(results)
            
            assert should_rollback is False
    
    @pytest.mark.asyncio
    async def test_disable_risky_features(self, rollback_manager):
        """Test disabling risky features during rollback"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.feature_flags') as mock_flags:
            mock_flags.set_flag = AsyncMock()
            
            await rollback_manager._disable_risky_features()
            
            # Should have called set_flag for each risky feature
            assert mock_flags.set_flag.call_count >= 3
    
    @pytest.mark.asyncio
    async def test_execute_rollback_success(self, rollback_manager):
        """Test successful rollback execution"""
        with patch.object(rollback_manager, '_disable_risky_features', new_callable=AsyncMock) as mock_disable:
            with patch.object(rollback_manager, '_trigger_deployment_rollback', new_callable=AsyncMock) as mock_rollback:
                mock_disable.return_value = None
                mock_rollback.return_value = True
                
                success = await rollback_manager.execute_rollback()
                
                assert success is True
                mock_disable.assert_called_once()
                mock_rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_rollback_failure(self, rollback_manager):
        """Test failed rollback execution"""
        with patch.object(rollback_manager, '_disable_risky_features', new_callable=AsyncMock) as mock_disable:
            with patch.object(rollback_manager, '_trigger_deployment_rollback', new_callable=AsyncMock) as mock_rollback:
                mock_disable.return_value = None
                mock_rollback.return_value = False
                
                success = await rollback_manager.execute_rollback()
                
                assert success is False


class TestVisualRegressionIntegration:
    """Test visual regression integration functions"""
    
    @pytest.mark.asyncio
    async def test_run_observatory_visual_tests(self):
        """Test running Observatory visual tests"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.visual_tester') as mock_tester:
            with patch('src.beast_mode.observatory.ai_consultation.visual_regression.rollback_manager') as mock_rollback:
                with patch('src.beast_mode.observatory.ai_consultation.visual_regression.with_circuit_breaker') as mock_cb:
                    # Mock test results
                    mock_results = [
                        VisualTestResult(
                            test_id="test1",
                            url="http://test.com",
                            viewport_size=(1920, 1080),
                            timestamp=None,
                            status=VisualTestStatus.PASSED,
                            baseline_path="",
                            current_path=""
                        )
                    ]
                    
                    mock_cb.return_value = mock_results
                    mock_tester.get_test_summary.return_value = {
                        'total': 1,
                        'passed': 1,
                        'failed': 0,
                        'error': 0,
                        'regressions': []
                    }
                    mock_rollback.evaluate_rollback = AsyncMock(return_value=False)
                    mock_tester.cleanup_driver = AsyncMock()
                    
                    summary = await run_observatory_visual_tests()
                    
                    assert summary['total'] == 1
                    assert summary['passed'] == 1
                    assert summary['rollback_triggered'] is False
                    mock_tester.cleanup_driver.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_observatory_visual_tests_with_rollback(self):
        """Test running Observatory visual tests with rollback"""
        with patch('src.beast_mode.observatory.ai_consultation.visual_regression.visual_tester') as mock_tester:
            with patch('src.beast_mode.observatory.ai_consultation.visual_regression.rollback_manager') as mock_rollback:
                with patch('src.beast_mode.observatory.ai_consultation.visual_regression.with_circuit_breaker') as mock_cb:
                    # Mock test results with regression
                    mock_results = [
                        VisualTestResult(
                            test_id="test1",
                            url="http://test.com",
                            viewport_size=(1920, 1080),
                            timestamp=None,
                            status=VisualTestStatus.FAILED,
                            baseline_path="",
                            current_path=""
                        )
                    ]
                    
                    mock_cb.return_value = mock_results
                    mock_tester.get_test_summary.return_value = {
                        'total': 1,
                        'passed': 0,
                        'failed': 1,
                        'error': 0,
                        'regressions': [{'test_id': 'test1', 'severity': 'critical'}]
                    }
                    mock_rollback.evaluate_rollback = AsyncMock(return_value=True)
                    mock_rollback.execute_rollback = AsyncMock(return_value=True)
                    mock_tester.cleanup_driver = AsyncMock()
                    
                    summary = await run_observatory_visual_tests()
                    
                    assert summary['rollback_triggered'] is True
                    assert summary['rollback_success'] is True
                    mock_rollback.execute_rollback.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])