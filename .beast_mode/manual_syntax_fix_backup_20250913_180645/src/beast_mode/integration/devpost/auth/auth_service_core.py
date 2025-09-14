import json
import secrets
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from dataclasses import dataclass
from ..exceptions import DevPostAuthenticationError, DevPostAPIError
import sys
import os
from src.devpost_integration.reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
import logging
from ..api.client import DevPostAPIClient
from ..api.client import DevPostAPIClient
from .auth_service_core_core import *
