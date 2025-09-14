
def validate_schema(self, domain_dict: Dict[str, Any]) -> List[str]:
    """Validate domain dictionary against schema"""
    try:
        import jsonschema
        jsonschema.validate(domain_dict, self.domain_schema)
        return []
    except ImportError:
        return self._basic_schema_validation(domain_dict)
    except jsonschema.ValidationError as e:
        return [str(e)]
