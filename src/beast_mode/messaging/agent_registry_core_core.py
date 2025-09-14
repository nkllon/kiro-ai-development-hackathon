import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .models import AgentCapabilities, BeastModeMessage, MessageType
from .agent_registry_core_core_core import *
from src.rm_ddd.core.health import ModuleHealth

