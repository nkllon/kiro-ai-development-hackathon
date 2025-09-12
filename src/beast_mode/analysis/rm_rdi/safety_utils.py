"""
Safety Utils

This module was extracted from safety.py
as part of RM-DDD compliance refactoring.
"""

import os
import threading
import time
import signal
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
import psutil

class MockPsutil:

    @staticmethod
    def virtual_memory():

        class MockMemory:
            percent = 50.0
        return MockMemory()

    @staticmethod
    def cpu_percent():
        return 25.0

    @staticmethod
    def disk_usage(path):

        class MockDisk:
            percent = 30.0
        return MockDisk()

    @staticmethod
    def Process():
        return MockProcess()
