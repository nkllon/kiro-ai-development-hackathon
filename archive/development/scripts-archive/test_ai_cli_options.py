#!/usr/bin/env python3
"""Test available AI CLI options for worker coordination."""

import subprocess
import os
import json
from datetime import datetime

def test_openai_cli():
    """Test OpenAI CLI."""
    try:
        result = subprocess.run([
            'openai', 'api', 'chat.completions.create',
            '-g', 'user', 'What is 2+2? Respond with just the number.',
            '-m', 'gpt-3.5-turbo',
            '-M', '10'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout, "error": None}
        else:
            return {"status": "failed", "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"status": "error", "output": None, "error": str(e)}

def test_gemini_python():
    """Test Gemini via Python."""
    try:
        import google.generativeai as genai
        
        # Check if API key is available
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {"status": "no_key", "output": None, "error": "No API key found"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("What is 2+2? Respond with just the number.")
        
        return {"status": "success", "output": response.text, "error": None}
    except Exception as e:
        return {"status": "error", "output": None, "error": str(e)}

def test_anthropic_python():
    """Test Anthropic via Python (not CLI since CLI is having credit issues)."""
    try:
        import anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {"status": "no_key", "output": None, "error": "No API key found"}
        
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "What is 2+2? Respond with just the number."}]
        )
        
        return {"status": "success", "output": response.content[0].text, "error": None}
    except Exception as e:
        return {"status": "error", "output": None, "error": str(e)}

def main():
    """Test all available AI CLI options."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    print("Testing AI CLI options...")
    
    # Test OpenAI CLI
    print("Testing OpenAI CLI...")
    results["tests"]["openai_cli"] = test_openai_cli()
    
    # Test Gemini Python
    print("Testing Gemini Python...")
    results["tests"]["gemini_python"] = test_gemini_python()
    
    # Test Anthropic Python
    print("Testing Anthropic Python...")
    results["tests"]["anthropic_python"] = test_anthropic_python()
    
    # Print results
    print("\n" + "="*50)
    print("AI CLI TEST RESULTS")
    print("="*50)
    
    for test_name, result in results["tests"].items():
        status = result["status"]
        print(f"\n{test_name.upper()}: {status}")
        if result["output"]:
            print(f"  Output: {result['output'][:100]}")
        if result["error"]:
            print(f"  Error: {result['error'][:100]}")
    
    # Save results
    with open("ai_cli_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to ai_cli_test_results.json")

if __name__ == "__main__":
    main()