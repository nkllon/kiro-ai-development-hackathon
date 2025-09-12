from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from ...core.compliance import ValidationResult
from ...domain.entities import Entity
from ...models import DomainBoundaries, DomainException
from ...utilities.decorators import domain_entity
from .value_objects import ProductId, CustomerId, OrderId, Money, EmailAddress, Address, Quantity
from .entities_core_core_validation import *
from .entities_core_core_core import *
