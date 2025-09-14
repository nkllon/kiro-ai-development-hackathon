from src.rm_ddd.core.health import ModuleHealth

    def process_binary_input(self, input_data: bytes) -> ProcessedInput:
        """Process binary input from stdin"""
        return ProcessedInput(format='binary', data=input_data, success=True)
