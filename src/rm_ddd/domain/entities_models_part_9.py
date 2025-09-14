
    def __repr__(self) -> str:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """String representation of entity."""
        return f'{self.__class__.__name__}(id={self.id}, version={self._version})'

    @abstractmethod