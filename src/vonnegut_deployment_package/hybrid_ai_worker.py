#!/usr/bin/env python3
"""
Hybrid AI worker that tries multiple AI services.
Falls back gracefully when one service fails.
"""

import sys
import json
import os
import subprocess
from datetime import datetime

def log_json(event_type, details):
    """Log events in JSON format."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "details": details
    }
    print(json.dumps(log_entry), flush=True)

def try_cursor_agent(prompt):
    """Try using cursor-agent CLI."""
    try:
        log_json("trying_cursor", "Attempting cursor-agent")
        
        # Create a temporary prompt file
        with open("/tmp/cursor_prompt.txt", "w") as f:
            f.write(prompt)
        
        result = subprocess.run([
            "cursor-agent", 
            "--file", "/tmp/cursor_prompt.txt"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log_json("cursor_success", "Cursor agent completed")
            return result.stdout
        else:
            log_json("cursor_failed", f"Exit code: {result.returncode}, Error: {result.stderr[:200]}")
            return None
            
    except Exception as e:
        log_json("cursor_error", str(e))
        return None

def try_openai_cli(prompt):
    """Try using OpenAI CLI if API key is available."""
    try:
        if not os.getenv('OPENAI_API_KEY'):
            log_json("openai_skip", "No OPENAI_API_KEY found")
            return None
            
        log_json("trying_openai", "Attempting OpenAI CLI")
        
        result = subprocess.run([
            'openai', 'api', 'chat.completions.create',
            '-g', 'user', prompt,
            '-m', 'gpt-3.5-turbo',
            '-M', '4000'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            log_json("openai_success", "OpenAI CLI completed")
            # Parse JSON response
            try:
                response_data = json.loads(result.stdout)
                return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            except:
                return result.stdout
        else:
            log_json("openai_failed", f"Exit code: {result.returncode}")
            return None
            
    except Exception as e:
        log_json("openai_error", str(e))
        return None

def main():
    if len(sys.argv) < 2:
        log_json("error", "No prompt provided")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    log_json("worker_start", "Starting hybrid AI worker")
    
    # Try different AI services in order of preference
    services = [
        ("cursor", try_cursor_agent),
        ("openai", try_openai_cli),
    ]
    
    for service_name, service_func in services:
        log_json("attempting_service", service_name)
        result = service_func(prompt)
        
        if result:
            log_json("service_success", service_name)
            print("\n" + "="*50)
            print("AI RESPONSE:")
            print("="*50)
            print(result)
            log_json("worker_complete", f"Completed using {service_name}")
            sys.exit(0)
    
    log_json("all_services_failed", "No AI service was able to complete the request")
    print("ERROR: All AI services failed")
    sys.exit(1)

if __name__ == "__main__":
    main()