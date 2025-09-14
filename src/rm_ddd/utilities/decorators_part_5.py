from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def decorator(cls: Type[T]) -> Type[T]:
        if not issubclass(cls, Entity):
            raise TypeError(f'@domain_entity can only be applied to Entity subclasses, got {cls}')
        cls._domain_context = domain_context
        cls._max_complexity = max_complexity
        cls._validate_invariants = validate_invariants
        cls._auto_register = auto_register
        cls._is_domain_entity = True
        original_init = cls.__init__

        @functools.wraps(original_init)