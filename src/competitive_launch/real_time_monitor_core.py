import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from .models import CompetitorMove, ThreatLevel, MarketTrend
from .real_time_monitor_core_core import *
from src.rm_ddd.core.health import ModuleHealth

