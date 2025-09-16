#!/usr/bin/env python3
import os
import psutil

# Get current process info
current_pid = os.getpid()
parent_pid = os.getppid()

print(f"Current PID: {current_pid}")
print(f"Parent PID: {parent_pid}")

# Find shell processes
shell_pids = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] in ['bash', 'zsh', 'sh', 'fish']:
            shell_pids.append(proc.info['pid'])
            print(f"Shell found: PID {proc.info['pid']} - {proc.info['name']}")
    except:
        pass

print(f"All shell PIDs: {shell_pids}")

