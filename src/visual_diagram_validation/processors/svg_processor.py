import io
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw
import re
from ..core.interfaces import ProcessorInterface
from ..core.models import PNGImage
from ..rendering.png_utils import PNGProcessor
from .svg_processor_utils import *
from .svg_processor_processing import *
from .svg_processor_services import *
from .svg_processor_core import *
from src.rm_ddd.core.health import ModuleHealth

