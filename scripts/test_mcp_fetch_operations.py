#!/usr/bin/env python3
"""
MCP Fetch Operations Test Script
Tests the fetch functionality from the MCP fetch server.
"""

import json
import sys
import time
from typing import Dict, Any, List


def test_fetch_simple_webpage() -> Dict[str, Any]:
    """Test fetching a simple webpage."""
    result = {
        "test": "fetch_simple_webpage",
        "status": "unknown",
        "details": {}
    }
    
    try:
        # Test with a simple, reliable webpage
        test_url = "https://httpbin.org/json"
        
        print(f"Testing fetch with URL: {test_url}")
        print("This should return a JSON response from httpbin.org")
        
        # Note: We can't directly call MCP tools from this script
        # This is a template for manual testing
        result["status"] = "manual_test_required"
        result["details"] = {
            "test_url": test_url,
            "expected": "JSON response with slideshow data",
            "instructions": "Use MCP fetch tool to fetch this URL"
        }
        
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)
    
    return result


def test_fetch_with_parameters() -> Dict[str, Any]:
    """Test fetch with various parameters."""
    result = {
        "test": "fetch_with_parameters",
        "status": "unknown",
        "details": {}
    }
    
    test_cases = [
        {
            "name": "Basic HTML page",
            "url": "https://httpbin.org/html",
            "expected": "HTML content",
            "parameters": {"raw": False}
        },
        {
            "name": "Raw HTML content",
            "url": "https://httpbin.org/html", 
            "expected": "Raw HTML without markdown conversion",
            "parameters": {"raw": True}
        },
        {
            "name": "Limited content length",
            "url": "https://httpbin.org/json",
            "expected": "Truncated JSON content",
            "parameters": {"max_length": 200}
        },
        {
            "name": "JSON API endpoint",
            "url": "https://jsonplaceholder.typicode.com/posts/1",
            "expected": "JSON post data",
            "parameters": {"raw": False}
        }
    ]
    
    result["status"] = "manual_test_required"
    result["details"] = {
        "test_cases": test_cases,
        "instructions": "Use MCP fetch tool with these URLs and parameters"
    }
    
    return result


def test_fetch_error_handling() -> Dict[str, Any]:
    """Test fetch error handling with invalid URLs."""
    result = {
        "test": "fetch_error_handling", 
        "status": "unknown",
        "details": {}
    }
    
    error_test_cases = [
        {
            "name": "Invalid URL",
            "url": "not-a-valid-url",
            "expected_error": "Invalid URL format"
        },
        {
            "name": "Non-existent domain",
            "url": "https://this-domain-definitely-does-not-exist-12345.com",
            "expected_error": "DNS resolution failure or connection timeout"
        },
        {
            "name": "404 Not Found",
            "url": "https://httpbin.org/status/404",
            "expected_error": "HTTP 404 error"
        },
        {
            "name": "500 Server Error",
            "url": "https://httpbin.org/status/500", 
            "expected_error": "HTTP 500 error"
        }
    ]
    
    result["status"] = "manual_test_required"
    result["details"] = {
        "error_test_cases": error_test_cases,
        "instructions": "Test these URLs to verify proper error handling"
    }
    
    return result


def test_fetch_content_types() -> Dict[str, Any]:
    """Test fetch with different content types."""
    result = {
        "test": "fetch_content_types",
        "status": "unknown", 
        "details": {}
    }
    
    content_type_tests = [
        {
            "name": "JSON content",
            "url": "https://httpbin.org/json",
            "content_type": "application/json",
            "expected": "Properly formatted JSON"
        },
        {
            "name": "HTML content",
            "url": "https://httpbin.org/html",
            "content_type": "text/html",
            "expected": "HTML converted to markdown (unless raw=True)"
        },
        {
            "name": "Plain text",
            "url": "https://httpbin.org/robots.txt",
            "content_type": "text/plain",
            "expected": "Plain text content"
        },
        {
            "name": "XML content",
            "url": "https://httpbin.org/xml",
            "content_type": "application/xml",
            "expected": "XML content"
        }
    ]
    
    result["status"] = "manual_test_required"
    result["details"] = {
        "content_type_tests": content_type_tests,
        "instructions": "Test these URLs to verify content type handling"
    }
    
    return result


def generate_fetch_test_commands() -> List[str]:
    """Generate example commands for testing MCP fetch."""
    commands = [
        # Basic fetch tests
        'echo "Fetch a simple JSON endpoint" | tee fetch-test-json.log | kiro -',
        'echo "Please use the MCP fetch tool to get: https://httpbin.org/json" | tee fetch-test-json.log | kiro -',
        
        # HTML content test
        'echo "Fetch HTML content and convert to markdown" | tee fetch-test-html.log | kiro -',
        'echo "Please use MCP fetch to get: https://httpbin.org/html" | tee fetch-test-html.log | kiro -',
        
        # Raw content test
        'echo "Fetch raw HTML without markdown conversion" | tee fetch-test-raw.log | kiro -',
        'echo "Please use MCP fetch with raw=true for: https://httpbin.org/html" | tee fetch-test-raw.log | kiro -',
        
        # Limited length test
        'echo "Fetch with limited content length" | tee fetch-test-limited.log | kiro -',
        'echo "Please use MCP fetch with max_length=200 for: https://httpbin.org/json" | tee fetch-test-limited.log | kiro -',
        
        # Error handling tests
        'echo "Test error handling with invalid URL" | tee fetch-test-error.log | kiro -',
        'echo "Please use MCP fetch to test error handling with: not-a-valid-url" | tee fetch-test-error.log | kiro -',
        
        # Real-world API test
        'echo "Fetch from a real API endpoint" | tee fetch-test-api.log | kiro -',
        'echo "Please use MCP fetch to get: https://jsonplaceholder.typicode.com/posts/1" | tee fetch-test-api.log | kiro -'
    ]
    
    return commands


def run_diagnostic_tests() -> Dict[str, Any]:
    """Run all diagnostic tests for MCP fetch functionality."""
    print("🌐 MCP Fetch Operations Test Suite")
    print("=" * 50)
    
    tests = [
        test_fetch_simple_webpage,
        test_fetch_with_parameters,
        test_fetch_error_handling,
        test_fetch_content_types
    ]
    
    results = {}
    
    for test_func in tests:
        print(f"\n🧪 Running: {test_func.__name__}")
        result = test_func()
        results[result["test"]] = result
        
        status_emoji = {
            "success": "✅",
            "manual_test_required": "📋",
            "error": "❌",
            "unknown": "❓"
        }
        
        print(f"  Status: {status_emoji.get(result['status'], '❓')} {result['status']}")
        
        if result.get("details", {}).get("error"):
            print(f"  Error: {result['details']['error']}")
        
        # Show test details for manual tests
        if result["status"] == "manual_test_required":
            details = result["details"]
            if "test_cases" in details:
                print(f"  Test cases: {len(details['test_cases'])}")
            elif "error_test_cases" in details:
                print(f"  Error test cases: {len(details['error_test_cases'])}")
            elif "content_type_tests" in details:
                print(f"  Content type tests: {len(details['content_type_tests'])}")
    
    # Generate test commands
    print(f"\n" + "=" * 50)
    print("📋 Manual Test Commands")
    print("=" * 50)
    
    commands = generate_fetch_test_commands()
    for i, command in enumerate(commands, 1):
        print(f"\n{i}. {command}")
    
    print(f"\n" + "=" * 50)
    print("✨ Test suite complete - manual testing required")
    
    return results


def show_fetch_examples():
    """Show practical examples of using MCP fetch."""
    examples = [
        {
            "title": "Basic JSON API Fetch",
            "description": "Fetch JSON data from a REST API",
            "url": "https://jsonplaceholder.typicode.com/posts/1",
            "parameters": {},
            "expected": "JSON object with post data"
        },
        {
            "title": "HTML to Markdown Conversion", 
            "description": "Fetch HTML and convert to readable markdown",
            "url": "https://httpbin.org/html",
            "parameters": {"raw": False},
            "expected": "HTML content converted to markdown format"
        },
        {
            "title": "Raw HTML Content",
            "description": "Fetch raw HTML without conversion",
            "url": "https://httpbin.org/html",
            "parameters": {"raw": True},
            "expected": "Raw HTML source code"
        },
        {
            "title": "Limited Content Length",
            "description": "Fetch with content length limit",
            "url": "https://httpbin.org/json",
            "parameters": {"max_length": 500},
            "expected": "Truncated content up to 500 characters"
        },
        {
            "title": "GitHub API Example",
            "description": "Fetch repository information from GitHub API",
            "url": "https://api.github.com/repos/microsoft/vscode",
            "parameters": {},
            "expected": "Repository metadata in JSON format"
        }
    ]
    
    print("🌐 MCP Fetch Tool Examples")
    print("=" * 40)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   Description: {example['description']}")
        print(f"   URL: {example['url']}")
        if example['parameters']:
            print(f"   Parameters: {example['parameters']}")
        print(f"   Expected: {example['expected']}")
        
        # Generate Kiro command
        prompt = f"Please use the MCP fetch tool to get: {example['url']}"
        if example['parameters']:
            param_str = ", ".join([f"{k}={v}" for k, v in example['parameters'].items()])
            prompt += f" with parameters: {param_str}"
        
        print(f"   Command: echo \"{prompt}\" | tee fetch-example-{i}.log | kiro -")


def main():
    """Main function to run MCP fetch tests."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python test_mcp_fetch_operations.py [options]")
            print("Options:")
            print("  --examples    Show practical fetch examples")
            print("  --json        Output test results in JSON format")
            return
        elif sys.argv[1] == "--examples":
            show_fetch_examples()
            return
        elif sys.argv[1] == "--json":
            results = {}
            for test_func in [test_fetch_simple_webpage, test_fetch_with_parameters, 
                             test_fetch_error_handling, test_fetch_content_types]:
                result = test_func()
                results[result["test"]] = result
            print(json.dumps(results, indent=2))
            return
    
    # Default: run diagnostic tests
    run_diagnostic_tests()


if __name__ == "__main__":
    main()