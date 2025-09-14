
    def __init__(self, entity_id: TEntityId, domain_context: str, module_id: Optional[str]=None):
        """
        Initialize domain entity with systematic compliance.
        
        Args:
            entity_id: Unique identifier for this entity
            domain_context: The bounded context this entity belongs to
            module_id: Optional RM module identifier
        """
        self.id = entity_id
        self._version = 1
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._domain_events: List['DomainEvent'] = []
        super().__init__(domain_context, module_id)
        logger.debug(f'Entity created: {self.__class__.__name__}({entity_id}) in context: {domain_context}')
