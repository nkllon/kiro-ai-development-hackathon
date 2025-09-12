from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4
from ...core.compliance import ValidationResult
from ...domain.value_objects import ImmutableValueObject
from ...utilities.decorators import value_object
import re
import re
from .value_objects_core import *
from .value_objects_validation import *
