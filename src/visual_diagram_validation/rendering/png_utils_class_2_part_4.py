from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class NormalizepngClass:
    """Auto-generated class for functions."""

    def normalize_png(image_data: bytes, target_dpi: int = 300,
    retina_scale: float = 2.0) -> PNGImage:
    """
    Normalize PNG image to standard format with DPI and retina scaling.

    Args:
    image_data: Raw image bytes
    target_dpi: Target DPI for output
    retina_scale: Scaling factor for retina displays

    Returns:
    Normalized PNGImage object
    """
    # Open image from bytes
    with Image.open(io.BytesIO(image_data)) as img:
    # Convert to RGB if necessary (removes alpha channel issues)
    if img.mode != 'RGB':
    # Handle transparency by adding white background
    if img.mode in ('RGBA', 'LA'):
    background = Image.new('RGB', img.size, (255, 255, 255))
    if img.mode == 'RGBA':
    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
    else:
    background.paste(img)
    img = background
    else:
    img = img.convert('RGB')

    # Apply retina scaling
    if retina_scale != 1.0:
    new_width = int(img.width * retina_scale)
    new_height = int(img.height * retina_scale)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Extract metadata before processing
    metadata = PNGProcessor.extract_metadata(image_data)

    # Save with target DPI
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='PNG', dpi=(target_dpi, target_dpi), optimize=True)
    normalized_data = output_buffer.getvalue()

    return PNGImage(
    data=normalized_data,
    width=img.width,
    height=img.height,
    dpi=target_dpi,
    color_mode='RGB',
    metadata=metadata
    )


    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

    @staticmethod