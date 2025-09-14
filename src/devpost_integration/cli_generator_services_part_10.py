from src.rm_ddd.core.health import ModuleHealth

    def process_text_input(self, input_data: bytes) -> ProcessedInput:
        """Process text input from stdin"""
        try:
            text = input_data.decode('utf-8')
            lines = text.strip().split('\n') if text.strip() else []
            return ProcessedInput(format='text', data=lines, success=True)
        except UnicodeDecodeError as e:
            return ProcessedInput(format='text', data=None, success=False, error=str(e))
