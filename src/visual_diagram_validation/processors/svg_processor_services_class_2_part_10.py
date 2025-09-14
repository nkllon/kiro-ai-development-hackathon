from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _parse_dimension(self, dim_str: str) -> float:
        """Parse dimension string (e.g., '100px', '50%', '2in') to pixels."""
        if not dim_str:
            return 100.0
        numeric_part = re.sub('[^0-9.]', '', dim_str)
        try:
            value = float(numeric_part) if numeric_part else 100.0
            if 'in' in dim_str:
                value *= 96
            elif 'cm' in dim_str:
                value *= 37.8
            elif 'mm' in dim_str:
                value *= 3.78
            elif 'pt' in dim_str:
                value *= 1.33
            return value
        except ValueError:
            return 100.0
