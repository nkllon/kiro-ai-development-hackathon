#!/usr/bin/env python3
"""
Test Browser Automation
=======================

Test script for DevPost browser automation implementation.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test browser automation with real DevPost pages
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from devpost_integration.hybrid_integration import DevPostHybridIntegration
from devpost_integration.browser_automation import DevPostBrowserAutomation
from devpost_integration.web_scraping import DevPostWebScraping

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_browser_automation_async():
    """Test async browser automation."""
    print("🧪 Testing Async Browser Automation")
    print("=" * 50)
    
    # Test with a real DevPost hackathon page
    test_url = "https://devpost.com/software/trending"
    
    try:
        async with DevPostHybridIntegration(headless=False) as integration:
            print(f"🌐 Testing with URL: {test_url}")
            
            # Test hackathon data extraction
            result = await integration.extract_hackathon_data_async(test_url)
            
            if result.success:
                print("✅ Async extraction successful!")
                print(f"   Method used: {result.method_used}")
                print(f"   Title: {result.data.title}")
                print(f"   Description: {result.data.description[:100]}...")
                print(f"   Extracted at: {result.extracted_at}")
            else:
                print("❌ Async extraction failed!")
                print(f"   Error: {result.error}")
                
    except Exception as e:
        print(f"❌ Async test failed: {e}")


def test_browser_automation_sync():
    """Test sync browser automation."""
    print("\n🧪 Testing Sync Browser Automation")
    print("=" * 50)
    
    # Test with a real DevPost hackathon page
    test_url = "https://devpost.com/software/trending"
    
    try:
        with DevPostHybridIntegration(headless=False) as integration:
            print(f"🌐 Testing with URL: {test_url}")
            
            # Test hackathon data extraction
            result = integration.extract_hackathon_data_sync(test_url)
            
            if result.success:
                print("✅ Sync extraction successful!")
                print(f"   Method used: {result.method_used}")
                print(f"   Title: {result.data.title}")
                print(f"   Description: {result.data.description[:100]}...")
                print(f"   Extracted at: {result.extracted_at}")
            else:
                print("❌ Sync extraction failed!")
                print(f"   Error: {result.error}")
                
    except Exception as e:
        print(f"❌ Sync test failed: {e}")


def test_web_scraping_fallback():
    """Test web scraping fallback."""
    print("\n🧪 Testing Web Scraping Fallback")
    print("=" * 50)
    
    # Test with a real DevPost hackathon page
    test_url = "https://devpost.com/software/trending"
    
    try:
        with DevPostWebScraping() as scraping:
            print(f"🌐 Testing with URL: {test_url}")
            
            # Test hackathon data extraction
            data = scraping.extract_hackathon_data(test_url)
            
            print("✅ Web scraping extraction successful!")
            print(f"   Title: {data.title}")
            print(f"   Description: {data.description[:100]}...")
            print(f"   Extracted at: {data.extracted_at}")
                
    except Exception as e:
        print(f"❌ Web scraping test failed: {e}")


def test_hackathon_search():
    """Test hackathon search functionality."""
    print("\n🧪 Testing Hackathon Search")
    print("=" * 50)
    
    try:
        with DevPostHybridIntegration() as integration:
            print("🔍 Searching for hackathons...")
            
            # Search for hackathons
            hackathons = integration.search_hackathons(query="ai", limit=5)
            
            print(f"✅ Found {len(hackathons)} hackathons!")
            for i, hackathon in enumerate(hackathons, 1):
                print(f"   {i}. {hackathon['title']}")
                print(f"      URL: {hackathon['url']}")
                print(f"      Description: {hackathon['description'][:50]}...")
                print()
                
    except Exception as e:
        print(f"❌ Hackathon search test failed: {e}")


async def main():
    """Main test function."""
    print("🚀 DevPost Browser Automation Test Suite")
    print("=" * 60)
    
    # Test async browser automation
    await test_browser_automation_async()
    
    # Test sync browser automation
    test_browser_automation_sync()
    
    # Test web scraping fallback
    test_web_scraping_fallback()
    
    # Test hackathon search
    test_hackathon_search()
    
    print("\n🎯 Test Suite Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
