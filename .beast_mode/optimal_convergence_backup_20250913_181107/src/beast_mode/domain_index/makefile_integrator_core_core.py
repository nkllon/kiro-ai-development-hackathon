import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from .base import DomainSystemComponent
from .interfaces import MakefileIntegratorInterface
from .models import Domain, MakeTarget, ExecutionResult, ValidationResult
from .exceptions import MakefileIntegrationError, MakefileNotFoundError, MakeTargetExecutionError
from .config import get_config
from .makefile_integrator_core_core_core import *
from .makefile_integrator_core_core_processing import *
from .makefile_integrator_core_core_validation import *
