#!/usr/bin/env python3
"""
Trace Chrome activity using DTrace to see what URLs are being accessed
without needing the debugging port enabled.
"""

import subprocess
import time
import json
import os
from datetime import datetime

class ChromeActivityTracer:
    def __init__(self):
        self.trace_data = []
        self.start_time = None
        
    def start_tracing(self, duration=10):
        """Start tracing Chrome network activity for specified duration"""
        print(f"🔍 TRACING CHROME ACTIVITY FOR {duration} SECONDS...")
        print("   This will show what URLs Chrome is accessing")
        print("   (You may need to enter your password for DTrace)")
        
        self.start_time = time.time()
        
        # DTrace script to monitor Chrome network activity
        dtrace_script = """
        syscall::connect:entry
        /execname == "Google Chrome"/
        {
            printf("%s|%d|%s|%s\\n", 
                timestamp, 
                pid, 
                execname, 
                copyinstr(arg1));
        }
        
        syscall::read:entry
        /execname == "Google Chrome"/
        {
            printf("READ|%s|%d|%s\\n", 
                timestamp, 
                pid, 
                execname);
        }
        """
        
        # Write DTrace script to temporary file
        with open('/tmp/chrome_trace.d', 'w') as f:
            f.write(dtrace_script)
        
        try:
            # Run DTrace for the specified duration
            cmd = ['sudo', 'dtrace', '-s', '/tmp/chrome_trace.d', '-q']
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Let it run for the specified duration
            time.sleep(duration)
            process.terminate()
            
            stdout, stderr = process.communicate()
            
            if stderr and "dtrace: system integrity protection" in stderr:
                print("❌ DTrace blocked by System Integrity Protection")
                print("   Try: sudo csrutil disable (requires reboot)")
                return False
                
            if stdout:
                print("📊 CHROME ACTIVITY DETECTED:")
                for line in stdout.strip().split('\n'):
                    if line:
                        print(f"   {line}")
                        self.trace_data.append(line)
            else:
                print("⚠️ No Chrome activity detected during trace period")
                
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ DTrace failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⏹️ Trace interrupted by user")
            return False
        finally:
            # Clean up
            if os.path.exists('/tmp/chrome_trace.d'):
                os.remove('/tmp/chrome_trace.d')
    
    def get_chrome_processes(self):
        """Get information about running Chrome processes"""
        print("🔍 FINDING CHROME PROCESSES...")
        
        try:
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True
            )
            
            chrome_processes = []
            for line in result.stdout.split('\n'):
                if 'Google Chrome' in line and 'Helper' not in line:
                    parts = line.split()
                    if len(parts) > 10:
                        pid = parts[1]
                        chrome_processes.append({
                            'pid': pid,
                            'command': ' '.join(parts[10:])
                        })
            
            print(f"✅ Found {len(chrome_processes)} Chrome processes:")
            for proc in chrome_processes:
                print(f"   PID {proc['pid']}: {proc['command'][:80]}...")
                
            return chrome_processes
            
        except Exception as e:
            print(f"❌ Failed to get Chrome processes: {e}")
            return []
    
    def analyze_network_connections(self):
        """Analyze Chrome's network connections"""
        print("🌐 ANALYZING CHROME NETWORK CONNECTIONS...")
        
        try:
            result = subprocess.run(
                ['lsof', '-i', '-P'], 
                capture_output=True, 
                text=True
            )
            
            chrome_connections = []
            for line in result.stdout.split('\n'):
                if 'Google Chrome' in line and ('TCP' in line or 'UDP' in line):
                    chrome_connections.append(line.strip())
            
            if chrome_connections:
                print(f"✅ Found {len(chrome_connections)} Chrome network connections:")
                for conn in chrome_connections:
                    print(f"   {conn}")
            else:
                print("⚠️ No Chrome network connections found")
                
            return chrome_connections
            
        except Exception as e:
            print(f"❌ Failed to analyze network connections: {e}")
            return []

def main():
    tracer = ChromeActivityTracer()
    
    print("🚀 CHROME ACTIVITY TRACER")
    print("=" * 50)
    
    # Get Chrome processes first
    processes = tracer.get_chrome_processes()
    
    if not processes:
        print("❌ No Chrome processes found. Is Chrome running?")
        return
    
    # Analyze network connections
    connections = tracer.analyze_network_connections()
    
    # Start tracing activity
    print("\n🎯 STARTING ACTIVITY TRACE...")
    print("   (Navigate around in Chrome to see activity)")
    
    success = tracer.start_tracing(duration=15)
    
    if success and tracer.trace_data:
        print(f"\n📈 TRACE COMPLETE - Captured {len(tracer.trace_data)} events")
        
        # Save trace data
        trace_file = f"chrome_activity_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(trace_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'processes': processes,
                'connections': connections,
                'trace_data': tracer.trace_data
            }, f, indent=2)
        
        print(f"💾 Trace data saved to: {trace_file}")
    else:
        print("❌ No activity captured during trace")

if __name__ == "__main__":
    main()

