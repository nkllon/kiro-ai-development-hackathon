#!/usr/bin/env python3
"""
Python-based Claude worker that bypasses CLI credit issues.
Uses the Anthropic Python SDK directly.
"""

import sys
import json
import os
from datetime import datetime
import anthropic

def log_json(event_type, details):
    """Log events in JSON format."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "details": details
    }
    print(json.dumps(log_entry), flush=True)

def main():
    if len(sys.argv) < 2:
        log_json("error", "No prompt provided")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    try:
        # Initialize Claude client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            log_json("error", "ANTHROPIC_API_KEY not found")
            sys.exit(1)
        
        log_json("worker_start", "Initializing Claude Python worker")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        log_json("api_request", "Sending request to Claude")
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Fast, cost-effective model
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        log_json("api_response", "Received response from Claude")
        
        # Output the response content
        for content_block in response.content:
            if content_block.type == "text":
                print(content_block.text)
        
        log_json("worker_complete", "Task completed successfully")
        
    except Exception as e:
        log_json("error", f"Worker failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()