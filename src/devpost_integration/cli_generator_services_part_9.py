from src.rm_ddd.core.health import ModuleHealth

    def process_json_input(self, input_data: bytes) -> ProcessedInput:
        """Process JSON input from stdin"""
        try:
            data = json.loads(input_data.decode('utf-8'))
            return ProcessedInput(format='json', data=data, success=True)
        except json.JSONDecodeError as e:
            return ProcessedInput(format='json', data=None, success=False, error=str(e))
