import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError
from .models import BeastModeMessage, MessageType, AgentCapabilities
import uuid
import uuid
from .compatibility_processing import *
from .compatibility_validation import *
from .compatibility_core import *
