
def validate_ubiquitous_language(obj: Any, term_mapping: Dict[str, str]) -> ValidationResult:
    """Validate ubiquitous language usage."""
    result = ValidationResult(is_valid=True)
    class_name = obj.__class__.__name__
    if class_name.lower() not in [term.lower() for term in term_mapping.values()]:
        result.add_warning(f"Class name '{class_name}' not found in ubiquitous language mapping")
    return result
