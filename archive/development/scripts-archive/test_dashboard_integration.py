#!/usr/bin/env python3
"""
Test Dashboard Integration

Tests the integration of engagement features with the Observatory dashboard.
Validates that the dashboard template includes engagement components and scripts.
"""

import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_dashboard_template_integration():
    """Test that the dashboard template includes engagement features."""
    logger.info("🧪 Testing dashboard template integration...")
    
    try:
        dashboard_path = Path("src/beast_mode/observatory/templates/dashboard.html")
        
        if not dashboard_path.exists():
            logger.error(f"❌ Dashboard template not found: {dashboard_path}")
            return False
        
        # Read dashboard template
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for engagement script includes
        required_scripts = [
            'engagement_controls.js',
            'engagement_charts.js'
        ]
        
        for script in required_scripts:
            if script not in content:
                logger.error(f"❌ Missing script: {script}")
                return False
            logger.info(f"✅ Found script: {script}")
        
        # Check for engagement CSS classes
        required_css_classes = [
            'engagement-chart',
            'engagement-controls-section',
            'engagement-metrics-grid',
            'personality-indicator'
        ]
        
        for css_class in required_css_classes:
            if css_class not in content:
                logger.error(f"❌ Missing CSS class: {css_class}")
                return False
            logger.info(f"✅ Found CSS class: {css_class}")
        
        # Check for engagement HTML elements
        required_elements = [
            'engagementControlsSection',
            'liveSessionDuration',
            'liveInteractionCount',
            'liveEngagementScore',
            'livePersonalityMood'
        ]
        
        for element in required_elements:
            if element not in content:
                logger.error(f"❌ Missing HTML element: {element}")
                return False
            logger.info(f"✅ Found HTML element: {element}")
        
        # Check for personality controls
        personality_moods = ['calm', 'focused', 'celebratory', 'energetic']
        for mood in personality_moods:
            if f"setPersonality('{mood}')" not in content:
                logger.error(f"❌ Missing personality control: {mood}")
                return False
            logger.info(f"✅ Found personality control: {mood}")
        
        logger.info("✅ Dashboard template integration test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard template integration test failed: {e}")
        return False


def test_engagement_scripts_exist():
    """Test that engagement JavaScript files exist."""
    logger.info("🧪 Testing engagement scripts exist...")
    
    try:
        script_files = [
            "src/beast_mode/observatory/static/engagement_controls.js",
            "src/beast_mode/observatory/static/engagement_charts.js"
        ]
        
        for script_file in script_files:
            script_path = Path(script_file)
            
            if not script_path.exists():
                logger.error(f"❌ Script file not found: {script_file}")
                return False
            
            # Check file size (should not be empty)
            if script_path.stat().st_size == 0:
                logger.error(f"❌ Script file is empty: {script_file}")
                return False
            
            logger.info(f"✅ Script file exists and has content: {script_file}")
        
        logger.info("✅ Engagement scripts exist test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Engagement scripts exist test failed: {e}")
        return False


def test_engagement_controls_functionality():
    """Test that engagement controls JavaScript has required functionality."""
    logger.info("🧪 Testing engagement controls functionality...")
    
    try:
        controls_path = Path("src/beast_mode/observatory/static/engagement_controls.js")
        
        if not controls_path.exists():
            logger.error(f"❌ Engagement controls file not found: {controls_path}")
            return False
        
        # Read engagement controls file
        with open(controls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required classes and functions
        required_items = [
            'class EngagementControls',
            'setupEngagementSocket',
            'setupAttentionTracking',
            'setupInteractionTracking',
            'recordInteraction',
            'triggerPersonalityTransition',
            'updateMetricsDisplay',
            'calculateEngagementScore',
            'window.setPersonality',
            'window.updateLiveEngagementMetrics'
        ]
        
        for item in required_items:
            if item not in content:
                logger.error(f"❌ Missing functionality: {item}")
                return False
            logger.info(f"✅ Found functionality: {item}")
        
        logger.info("✅ Engagement controls functionality test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Engagement controls functionality test failed: {e}")
        return False


def test_engagement_charts_functionality():
    """Test that engagement charts JavaScript has required functionality."""
    logger.info("🧪 Testing engagement charts functionality...")
    
    try:
        charts_path = Path("src/beast_mode/observatory/static/engagement_charts.js")
        
        if not charts_path.exists():
            logger.error(f"❌ Engagement charts file not found: {charts_path}")
            return False
        
        # Read engagement charts file
        with open(charts_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required classes and functions
        required_items = [
            'class EngagementCharts',
            'initAttentionChart',
            'initInteractionChart',
            'initPersonalityChart',
            'initEngagementHealthChart',
            'updateChartsWithLiveData',
            'exportChart',
            'handleChartClick'
        ]
        
        for item in required_items:
            if item not in content:
                logger.error(f"❌ Missing functionality: {item}")
                return False
            logger.info(f"✅ Found functionality: {item}")
        
        # Check for Chart.js integration
        chart_types = ['line', 'bar', 'doughnut']
        for chart_type in chart_types:
            if f"type: '{chart_type}'" not in content:
                logger.error(f"❌ Missing chart type: {chart_type}")
                return False
            logger.info(f"✅ Found chart type: {chart_type}")
        
        logger.info("✅ Engagement charts functionality test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Engagement charts functionality test failed: {e}")
        return False


def main():
    """Run all dashboard integration tests."""
    logger.info("🚀 Starting Dashboard Integration Tests")
    
    tests = [
        ("Dashboard Template Integration", test_dashboard_template_integration),
        ("Engagement Scripts Exist", test_engagement_scripts_exist),
        ("Engagement Controls Functionality", test_engagement_controls_functionality),
        ("Engagement Charts Functionality", test_engagement_charts_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} Test")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
                
        except Exception as e:
            logger.error(f"💥 {test_name} test CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All dashboard integration tests PASSED!")
        return 0
    else:
        logger.error(f"💥 {total - passed} tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)