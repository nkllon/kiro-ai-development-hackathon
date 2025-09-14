from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

        def enhanced_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            if validate_invariants:
                try:
                    validation_result = self.validate_domain_invariants()
                    if not validation_result.is_valid:
                        raise InvariantViolationException('Domain invariant validation failed', current_state=self.__dict__, context={'errors': validation_result.errors})
                except AttributeError:
                    logger.warning(f"Entity {cls.__name__} doesn't implement validate_domain_invariants")
            if auto_register:
                _auto_register_entity(self, domain_context)
        cls.__init__ = enhanced_init
        _add_complexity_monitoring(cls, max_complexity)
        _add_validation_helpers(cls)
        logger.debug(f'Applied @domain_entity decorator to {cls.__name__}')
        return cls
    return decorator
