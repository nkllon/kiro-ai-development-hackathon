from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, domain_context: str, external_system_name: str, translator: ContextTranslator[ExternalType, DomainType]):
        super().__init__(domain_context)
        self.external_system_name = external_system_name
        self.translator = translator
        self._adaptation_metrics = {'successful_adaptations': 0, 'failed_adaptations': 0, 'last_adaptation': None}

    async def adapt_from_external(self, external_data: ExternalType) -> DomainType:
        """
        Adapt external data to domain model.
        
        Args:
            external_data: Data from external system
            
        Returns:
            DomainType: Adapted domain model
            
        Raises:
            DomainException: If adaptation fails
        """
        try:
            domain_model = self.translator.translate_to_domain(external_data)
            validation_result = self.translator.validate_translation(external_data, domain_model)
            if not validation_result.is_valid:
                raise DomainException(f'Translation validation failed: {validation_result.errors}', error_code='TRANSLATION_VALIDATION_FAILED')
            self._adaptation_metrics['successful_adaptations'] += 1
            self._adaptation_metrics['last_adaptation'] = datetime.now()
            logger.info(f'Successfully adapted data from {self.external_system_name}')
            return domain_model
        except Exception as e:
            self._adaptation_metrics['failed_adaptations'] += 1
            logger.error(f'Failed to adapt data from {self.external_system_name}: {e}')
            raise DomainException(f'Adaptation failed: {str(e)}', error_code='ADAPTATION_FAILED', context={'external_system': self.external_system_name})

    async def adapt_to_external(self, domain_model: DomainType) -> ExternalType:
        """
        Adapt domain model to external format.
        
        Args:
            domain_model: Domain model to adapt
            
        Returns:
            ExternalType: Adapted external format
            
        Raises:
            DomainException: If adaptation fails
        """
        try:
            external_data = self.translator.translate_from_domain(domain_model)
            self._adaptation_metrics['successful_adaptations'] += 1
            self._adaptation_metrics['last_adaptation'] = datetime.now()
            logger.info(f'Successfully adapted data to {self.external_system_name}')
            return external_data
        except Exception as e:
            self._adaptation_metrics['failed_adaptations'] += 1
            logger.error(f'Failed to adapt data to {self.external_system_name}: {e}')
            raise DomainException(f'Adaptation failed: {str(e)}', error_code='ADAPTATION_FAILED', context={'external_system': self.external_system_name})

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

