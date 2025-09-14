        class Order(Entity[str]):
            pass
    """

    def decorator(cls: Type[T]) -> Type[T]:
        cls._ubiquitous_language_mapping = term_mapping
        cls._enforce_naming = enforce_naming
        cls._validate_consistency = validate_consistency
        cls._has_ubiquitous_language = True
        if enforce_naming:
            _validate_ubiquitous_language_naming(cls, term_mapping)
        if validate_consistency:
            _add_language_consistency_validation(cls, term_mapping)
        logger.debug(f'Applied @ubiquitous_language decorator to {cls.__name__}')
        return cls
    return decorator

def _auto_register_entity(entity_instance: Any, domain_context: str):
    """Auto-register entity with bounded context."""
    try:
        logger.debug(f'Auto-registered entity {entity_instance.__class__.__name__} in context {domain_context}')
    except Exception as e:
        logger.warning(f'Failed to auto-register entity: {e}')

def _auto_register_aggregate(aggregate_instance: Any, domain_context: str):
    """Auto-register aggregate with bounded context."""
    try:
        logger.debug(f'Auto-registered aggregate {aggregate_instance.__class__.__name__} in context {domain_context}')
    except Exception as e:
        logger.warning(f'Failed to auto-register aggregate: {e}')

def _add_complexity_monitoring(cls: Type, max_complexity: int):
    """Add complexity monitoring to a class."""

    def check_complexity(self):
        """Check if class complexity exceeds limits."""
        current_complexity = len([m for m in dir(self) if not m.startswith('_')])
        if current_complexity > max_complexity:
            logger.warning(f'Class {cls.__name__} complexity ({current_complexity}) exceeds limit ({max_complexity})')
        return current_complexity
    cls._check_complexity = check_complexity

def _wrap_aggregate_methods(cls: Type, max_size: int):
    """Wrap aggregate methods to enforce size limits."""

    def check_aggregate_size(self):
        """Check aggregate size limits."""
        current_size = getattr(self, '_aggregate_size', 0)
        if current_size > max_size:
            raise DomainException(f'Aggregate size ({current_size}) exceeds limit ({max_size})', error_code='AGGREGATE_SIZE_EXCEEDED')
        return current_size
    cls._check_aggregate_size = check_aggregate_size

def _add_boundary_validation(cls: Type):
    """Add boundary validation to aggregate root."""

    def validate_boundaries(self) -> ValidationResult:
        """Validate aggregate boundaries."""
        result = ValidationResult(is_valid=True)
        try:
            if hasattr(self, 'validate_domain_invariants'):
                invariant_result = self.validate_domain_invariants()
                result.merge(invariant_result)
        except Exception as e:
            result.add_error(f'Boundary validation failed: {str(e)}')
        return result
    cls._validate_boundaries = validate_boundaries

def _enforce_statelessness(cls: Type):
    """Enforce statelessness for domain services."""
    original_setattr = cls.__setattr__

    def stateless_setattr(self, name: str, value: Any):
        if hasattr(self, '_initializing') or name.startswith('_'):
            original_setattr(self, name, value)
        else:
            raise DomainException(f"Cannot modify attribute '{name}' on stateless domain service", error_code='STATELESS_VIOLATION')
    cls.__setattr__ = stateless_setattr
    original_init = cls.__init__

    @functools.wraps(original_init)
    def stateless_init(self, *args, **kwargs):
        self._initializing = True
        original_init(self, *args, **kwargs)
        del self._initializing
    cls.__init__ = stateless_init

def _add_purity_validation(cls: Type):
    """Add domain purity validation."""

    def validate_purity(self) -> ValidationResult:
        """Validate that service contains only domain logic."""
        result = ValidationResult(is_valid=True)
        for attr_name in dir(self):
            if not attr_name.startswith('_'):
                attr_value = getattr(self, attr_name)
                if hasattr(attr_value, '__module__'):
                    module_name = attr_value.__module__
                    if any((infra_pattern in module_name.lower() for infra_pattern in ['sqlalchemy', 'django', 'flask', 'requests', 'boto3'])):
                        result.add_error(f'Domain service has infrastructure dependency: {module_name}')
        return result
    cls._validate_purity = validate_purity

def _enforce_immutability(cls: Type):
    """Enforce immutability for value objects."""
    original_setattr = cls.__setattr__

    def immutable_setattr(self, name: str, value: Any):
        if not hasattr(self, '_initialized') or name.startswith('_'):
            original_setattr(self, name, value)
        else:
            raise DomainException(f"Cannot modify attribute '{name}' on immutable value object", error_code='IMMUTABILITY_VIOLATION')
    cls.__setattr__ = immutable_setattr
    original_init = cls.__init__

    @functools.wraps(original_init)
    def immutable_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._initialized = True
    cls.__init__ = immutable_init

def _add_creation_validation(cls: Type):
    """Add creation-time validation for value objects."""
    original_init = cls.__init__

    @functools.wraps(original_init)
    def validating_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        if hasattr(self, 'validate'):
            validation_result = self.validate()
            if not validation_result.is_valid:
                raise ValidationException(validation_result.errors, context={'class': cls.__name__, 'args': args, 'kwargs': kwargs})
    cls.__init__ = validating_init

def _add_significance_validation(cls: Type):
    """Add business significance validation for domain events."""

    def validate_significance(self) -> ValidationResult:
        """Validate that event represents significant business occurrence."""
        result = ValidationResult(is_valid=True)
        try:
            event_data = self.get_event_data()
            if not event_data:
                result.add_warning('Event has no data - may not be significant')
        except Exception as e:
            result.add_error(f'Cannot validate event significance: {str(e)}')
        return result
    cls._validate_significance = validate_significance

def _add_auto_timestamping(cls: Type):
    """Add automatic timestamping for domain events."""
    original_init = cls.__init__

    @functools.wraps(original_init)
    def timestamping_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        if not hasattr(self, 'timestamp') or not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now()
    cls.__init__ = timestamping_init

def _add_language_consistency_validation(cls: Type, term_mapping: Dict[str, str]):
    """Add language consistency validation."""

    def validate_language_consistency(self) -> ValidationResult:
        """Validate consistency with ubiquitous language."""
        result = ValidationResult(is_valid=True)
        class_name = self.__class__.__name__
        if class_name in term_mapping:
            definition = term_mapping[class_name]
            logger.debug(f'Validating {class_name} against definition: {definition}')
        return result
    cls._validate_language_consistency = validate_language_consistency

def is_domain_entity(cls: Type) -> bool:
    """Check if a class has the @domain_entity decorator applied."""
    return getattr(cls, '_is_domain_entity', False)

def is_aggregate_root(cls: Type) -> bool:
    """Check if a class has the @aggregate_root decorator applied."""
    return getattr(cls, '_is_aggregate_root', False)

def is_domain_service(cls: Type) -> bool:
    """Check if a class has the @domain_service decorator applied."""
    return getattr(cls, '_is_domain_service', False)

def is_value_object(cls: Type) -> bool:
    """Check if a class has the @value_object decorator applied."""
    return getattr(cls, '_is_value_object', False)

def is_domain_event(cls: Type) -> bool:
    """Check if a class has the @domain_event decorator applied."""
    return getattr(cls, '_is_domain_event', False)

def has_ubiquitous_language(cls: Type) -> bool:
    """Check if a class has the @ubiquitous_language decorator applied."""
    return getattr(cls, '_has_ubiquitous_language', False)

def get_domain_context(cls: Type) -> Optional[str]:
    """Get the domain context for a decorated class."""
    return getattr(cls, '_domain_context', None)

def get_ubiquitous_language_mapping(cls: Type) -> Dict[str, str]:
    """Get the ubiquitous language mapping for a decorated class."""
    return getattr(cls, '_ubiquitous_language_mapping', {})

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

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, AggregateRoot):
        raise TypeError(f'@aggregate_root can only be applied to AggregateRoot subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._max_aggregate_size = max_size
    cls._max_complexity = max_complexity
    cls._validate_boundaries = validate_boundaries
    cls._auto_register = auto_register
    cls._is_aggregate_root = True
    _wrap_aggregate_methods(cls, max_size)
    if validate_boundaries:
        _add_boundary_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    if auto_register:
        original_init = cls.__init__

        @functools.wraps(original_init)
        def enhanced_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            _auto_register_aggregate(self, domain_context)
        cls.__init__ = enhanced_init
    logger.debug(f'Applied @aggregate_root decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, DomainService):
        raise TypeError(f'@domain_service can only be applied to DomainService subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._is_stateless = stateless
    cls._max_complexity = max_complexity
    cls._validate_purity = validate_purity
    cls._is_domain_service = True
    if stateless:
        _enforce_statelessness(cls)
    if validate_purity:
        _add_purity_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @domain_service decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, ValueObject):
        raise TypeError(f'@value_object can only be applied to ValueObject subclasses, got {cls}')
    cls._is_immutable = immutable
    cls._validate_on_creation = validate_on_creation
    cls._max_complexity = max_complexity
    cls._is_value_object = True
    if immutable:
        _enforce_immutability(cls)
    if validate_on_creation:
        _add_creation_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @value_object decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, DomainEvent):
        raise TypeError(f'@domain_event can only be applied to DomainEvent subclasses, got {cls}')
    cls._event_version = event_version
    cls._validate_significance = validate_significance
    cls._auto_timestamp = auto_timestamp
    cls._is_domain_event = True
    if validate_significance:
        _add_significance_validation(cls)
    if auto_timestamp:
        _add_auto_timestamping(cls)
    logger.debug(f'Applied @domain_event decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    cls._ubiquitous_language_mapping = term_mapping
    cls._enforce_naming = enforce_naming
    cls._validate_consistency = validate_consistency
    cls._has_ubiquitous_language = True
    if enforce_naming:
        _validate_ubiquitous_language_naming(cls, term_mapping)
    if validate_consistency:
        _add_language_consistency_validation(cls, term_mapping)
    logger.debug(f'Applied @ubiquitous_language decorator to {cls.__name__}')
    return cls

def stateless_setattr(self, name: str, value: Any):
    if hasattr(self, '_initializing') or name.startswith('_'):
        original_setattr(self, name, value)
    else:
        raise DomainException(f"Cannot modify attribute '{name}' on stateless domain service", error_code='STATELESS_VIOLATION')

@functools.wraps(original_init)
def stateless_init(self, *args, **kwargs):
    self._initializing = True
    original_init(self, *args, **kwargs)
    del self._initializing

def immutable_setattr(self, name: str, value: Any):
    if not hasattr(self, '_initialized') or name.startswith('_'):
        original_setattr(self, name, value)
    else:
        raise DomainException(f"Cannot modify attribute '{name}' on immutable value object", error_code='IMMUTABILITY_VIOLATION')

@functools.wraps(original_init)
def immutable_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    self._initialized = True

@functools.wraps(original_init)
def validating_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if hasattr(self, 'validate'):
        validation_result = self.validate()
        if not validation_result.is_valid:
            raise ValidationException(validation_result.errors, context={'class': cls.__name__, 'args': args, 'kwargs': kwargs})

@functools.wraps(original_init)
def timestamping_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if not hasattr(self, 'timestamp') or not self.timestamp:
        from datetime import datetime
        self.timestamp = datetime.now()

@functools.wraps(original_init)
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

@functools.wraps(original_init)
def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)

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

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, AggregateRoot):
        raise TypeError(f'@aggregate_root can only be applied to AggregateRoot subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._max_aggregate_size = max_size
    cls._max_complexity = max_complexity
    cls._validate_boundaries = validate_boundaries
    cls._auto_register = auto_register
    cls._is_aggregate_root = True
    _wrap_aggregate_methods(cls, max_size)
    if validate_boundaries:
        _add_boundary_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    if auto_register:
        original_init = cls.__init__

        @functools.wraps(original_init)
        def enhanced_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            _auto_register_aggregate(self, domain_context)
        cls.__init__ = enhanced_init
    logger.debug(f'Applied @aggregate_root decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, DomainService):
        raise TypeError(f'@domain_service can only be applied to DomainService subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._is_stateless = stateless
    cls._max_complexity = max_complexity
    cls._validate_purity = validate_purity
    cls._is_domain_service = True
    if stateless:
        _enforce_statelessness(cls)
    if validate_purity:
        _add_purity_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @domain_service decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, ValueObject):
        raise TypeError(f'@value_object can only be applied to ValueObject subclasses, got {cls}')
    cls._is_immutable = immutable
    cls._validate_on_creation = validate_on_creation
    cls._max_complexity = max_complexity
    cls._is_value_object = True
    if immutable:
        _enforce_immutability(cls)
    if validate_on_creation:
        _add_creation_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @value_object decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, DomainEvent):
        raise TypeError(f'@domain_event can only be applied to DomainEvent subclasses, got {cls}')
    cls._event_version = event_version
    cls._validate_significance = validate_significance
    cls._auto_timestamp = auto_timestamp
    cls._is_domain_event = True
    if validate_significance:
        _add_significance_validation(cls)
    if auto_timestamp:
        _add_auto_timestamping(cls)
    logger.debug(f'Applied @domain_event decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    cls._ubiquitous_language_mapping = term_mapping
    cls._enforce_naming = enforce_naming
    cls._validate_consistency = validate_consistency
    cls._has_ubiquitous_language = True
    if enforce_naming:
        _validate_ubiquitous_language_naming(cls, term_mapping)
    if validate_consistency:
        _add_language_consistency_validation(cls, term_mapping)
    logger.debug(f'Applied @ubiquitous_language decorator to {cls.__name__}')
    return cls

def stateless_setattr(self, name: str, value: Any):
    if hasattr(self, '_initializing') or name.startswith('_'):
        original_setattr(self, name, value)
    else:
        raise DomainException(f"Cannot modify attribute '{name}' on stateless domain service", error_code='STATELESS_VIOLATION')

@functools.wraps(original_init)
def stateless_init(self, *args, **kwargs):
    self._initializing = True
    original_init(self, *args, **kwargs)
    del self._initializing

def immutable_setattr(self, name: str, value: Any):
    if not hasattr(self, '_initialized') or name.startswith('_'):
        original_setattr(self, name, value)
    else:
        raise DomainException(f"Cannot modify attribute '{name}' on immutable value object", error_code='IMMUTABILITY_VIOLATION')

@functools.wraps(original_init)
def immutable_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    self._initialized = True

@functools.wraps(original_init)
def validating_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if hasattr(self, 'validate'):
        validation_result = self.validate()
        if not validation_result.is_valid:
            raise ValidationException(validation_result.errors, context={'class': cls.__name__, 'args': args, 'kwargs': kwargs})

@functools.wraps(original_init)
def timestamping_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if not hasattr(self, 'timestamp') or not self.timestamp:
        from datetime import datetime
        self.timestamp = datetime.now()

@functools.wraps(original_init)
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

@functools.wraps(original_init)
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

@functools.wraps(original_init)
def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)

@functools.wraps(original_init)
def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)

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

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, AggregateRoot):
        raise TypeError(f'@aggregate_root can only be applied to AggregateRoot subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._max_aggregate_size = max_size
    cls._max_complexity = max_complexity
    cls._validate_boundaries = validate_boundaries
    cls._auto_register = auto_register
    cls._is_aggregate_root = True
    _wrap_aggregate_methods(cls, max_size)
    if validate_boundaries:
        _add_boundary_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    if auto_register:
        original_init = cls.__init__

        @functools.wraps(original_init)
        def enhanced_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            _auto_register_aggregate(self, domain_context)
        cls.__init__ = enhanced_init
    logger.debug(f'Applied @aggregate_root decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, DomainService):
        raise TypeError(f'@domain_service can only be applied to DomainService subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._is_stateless = stateless
    cls._max_complexity = max_complexity
    cls._validate_purity = validate_purity
    cls._is_domain_service = True
    if stateless:
        _enforce_statelessness(cls)
    if validate_purity:
        _add_purity_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @domain_service decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, ValueObject):
        raise TypeError(f'@value_object can only be applied to ValueObject subclasses, got {cls}')
    cls._is_immutable = immutable
    cls._validate_on_creation = validate_on_creation
    cls._max_complexity = max_complexity
    cls._is_value_object = True
    if immutable:
        _enforce_immutability(cls)
    if validate_on_creation:
        _add_creation_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @value_object decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, DomainEvent):
        raise TypeError(f'@domain_event can only be applied to DomainEvent subclasses, got {cls}')
    cls._event_version = event_version
    cls._validate_significance = validate_significance
    cls._auto_timestamp = auto_timestamp
    cls._is_domain_event = True
    if validate_significance:
        _add_significance_validation(cls)
    if auto_timestamp:
        _add_auto_timestamping(cls)
    logger.debug(f'Applied @domain_event decorator to {cls.__name__}')
    return cls

def decorator(cls: Type[T]) -> Type[T]:
    cls._ubiquitous_language_mapping = term_mapping
    cls._enforce_naming = enforce_naming
    cls._validate_consistency = validate_consistency
    cls._has_ubiquitous_language = True
    if enforce_naming:
        _validate_ubiquitous_language_naming(cls, term_mapping)
    if validate_consistency:
        _add_language_consistency_validation(cls, term_mapping)
    logger.debug(f'Applied @ubiquitous_language decorator to {cls.__name__}')
    return cls

def stateless_setattr(self, name: str, value: Any):
    if hasattr(self, '_initializing') or name.startswith('_'):
        original_setattr(self, name, value)
    else:
        raise DomainException(f"Cannot modify attribute '{name}' on stateless domain service", error_code='STATELESS_VIOLATION')

@functools.wraps(original_init)
def stateless_init(self, *args, **kwargs):
    self._initializing = True
    original_init(self, *args, **kwargs)
    del self._initializing

def immutable_setattr(self, name: str, value: Any):
    if not hasattr(self, '_initialized') or name.startswith('_'):
        original_setattr(self, name, value)
    else:
        raise DomainException(f"Cannot modify attribute '{name}' on immutable value object", error_code='IMMUTABILITY_VIOLATION')

@functools.wraps(original_init)
def immutable_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    self._initialized = True

@functools.wraps(original_init)
def validating_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if hasattr(self, 'validate'):
        validation_result = self.validate()
        if not validation_result.is_valid:
            raise ValidationException(validation_result.errors, context={'class': cls.__name__, 'args': args, 'kwargs': kwargs})

@functools.wraps(original_init)
def timestamping_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if not hasattr(self, 'timestamp') or not self.timestamp:
        from datetime import datetime
        self.timestamp = datetime.now()

@functools.wraps(original_init)
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

@functools.wraps(original_init)
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

@functools.wraps(original_init)
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

@functools.wraps(original_init)
def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)

@functools.wraps(original_init)
def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)

@functools.wraps(original_init)
def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)
