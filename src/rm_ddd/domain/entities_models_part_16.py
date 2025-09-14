
    def get_entity_info(self) -> Dict[str, Any]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get comprehensive entity information."""
        return {'entity_id': str(self.id), 'entity_type': self.__class__.__name__, 'domain_context': self.domain_context, 'version': self._version, 'created_at': self._created_at.isoformat(), 'updated_at': self._updated_at.isoformat(), 'pending_events': len(self._domain_events), 'module_id': self.module_id}

    async def get_module_status(self) -> 'ModuleHealth':
        """Get entity health status."""
        from ..core.health import ModuleHealth
        validation_result = self.validate_domain_invariants()
        status = ModuleStatus.AVAILABLE if validation_result.is_valid else ModuleStatus.DEGRADED
        message = f'Entity {self.__class__.__name__}({self.id})'
        if not validation_result.is_valid:
            message += f' - {len(validation_result.errors)} validation errors'
        return ModuleHealth(status=status, message=message, capabilities=await self.get_module_capabilities(), domain_health=await self.get_domain_health())

    async def get_module_capabilities(self) -> List[ModuleCapability]:
        """Get entity capabilities."""
        return [ModuleCapability(name=f'entity_{self.__class__.__name__.lower()}', description=f'Domain entity: {self.__class__.__name__}', available=await self.is_healthy(), version=str(self._version))]

    async def is_healthy(self) -> bool:
        """Check if entity is healthy."""
        try:
            validation_result = self.validate_domain_invariants()
            return validation_result.is_valid
        except Exception as e:
            logger.error(f'Health check failed for entity {self.__class__.__name__}({self.id}): {e}')
            return False

    async def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators."""
        validation_result = self.validate_domain_invariants()
        return {'entity_id': str(self.id), 'entity_type': self.__class__.__name__, 'version': self._version, 'domain_valid': validation_result.is_valid, 'validation_errors': len(validation_result.errors), 'validation_warnings': len(validation_result.warnings), 'pending_events': len(self._domain_events), 'last_updated': self._updated_at.isoformat()}
