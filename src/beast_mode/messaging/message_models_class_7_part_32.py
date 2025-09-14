from src.rm_ddd.core.registry import register_module

def to_dict(self) -> Dict[str, Any]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Convert message to dictionary for serialization."""
    data = self.dict()
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, Enum):
            data[key] = value.value
        elif isinstance(value, list) and value and hasattr(value[0], 'value'):
            data[key] = [item.value if hasattr(item, 'value') else item for item in value]
    return data
