import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from difflib import SequenceMatcher
from src.beast_mode.core.reflective_module import ReflectiveModule
from .validation_core_core import *
from .validation_core_validation import *
from src.rm_ddd.core.health import ModuleHealth

