import io
import math
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw
import numpy as np
from .base_analyzer import BaseQualityAnalyzer
from ..core.models import PNGImage, Severity, ActionType, BoundingBox
from .contrast_analyzer_core_core_core import *
