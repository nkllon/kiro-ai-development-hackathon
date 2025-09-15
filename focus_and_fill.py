#!/usr/bin/env python3
"""
Focus and Fill DevPost Form
===========================

Make sure Chrome is focused and try to fill the form.
"""

import subprocess
import time

def run_applescript(script):
    """Run AppleScript and return the result."""
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e}")
        return None

def focus_chrome():
    """Focus Chrome and make it visible."""
    print("🎯 Focusing Chrome...")
    
    # Activate Chrome
    result = run_applescript('tell application "Google Chrome" to activate')
    
    # Bring to front
    result = run_applescript('tell application "Google Chrome" to set index of front window to 1')
    
    # Make sure it's visible
    result = run_applescript('tell application "Google Chrome" to set visible of front window to true')
    
    print("✅ Chrome focused and visible")

def try_fill_form():
    """Try to fill the form with a simple approach."""
    print("📝 Trying to fill form...")
    
    # Try to fill the first input field
    result = run_applescript('''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
                var inputs = document.querySelectorAll('input, textarea');
                var filled = 0;
                for(var i = 0; i < inputs.length; i++) {
                    if(inputs[i].type === 'text' || inputs[i].tagName === 'TEXTAREA') {
                        if(inputs[i].value === '') {
                            if(filled === 0) {
                                inputs[i].value = 'The Requirements ARE the Solution - Beast Mode Framework';
                                inputs[i].focus();
                                filled++;
                            } else if(filled === 1) {
                                inputs[i].value = 'A revolutionary AI-powered development framework that transforms requirements into executable solutions, demonstrating 20.4% systematic superiority over ad-hoc development approaches.';
                                filled++;
                            } else if(filled === 2) {
                                inputs[i].value = 'https://github.com/nkllon/kiro-ai-development-hackathon';
                                filled++;
                            } else if(filled === 3) {
                                inputs[i].value = 'https://youtube.com/watch?v=demo-video';
                                filled++;
                            }
                        }
                    }
                }
                console.log('Filled ' + filled + ' fields');
            "
        end tell
    end tell
    ''')
    
    if result is None:
        print("❌ Failed to fill form")
    else:
        print("✅ Form filling attempted")

def main():
    print("🎯 Focus and Fill DevPost Form")
    print("=" * 35)
    
    # Focus Chrome
    focus_chrome()
    
    # Wait a moment
    time.sleep(2)
    
    # Try to fill the form
    try_fill_form()
    
    print("\\n💡 Check Chrome to see if the form was filled!")
    print("📝 If not, you can copy-paste the data from the previous output")

if __name__ == "__main__":
    main()
