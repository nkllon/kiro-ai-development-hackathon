import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .message_history_services_services import *
from .message_history_services_core import *
from src.rm_ddd.core.health import ModuleHealth

