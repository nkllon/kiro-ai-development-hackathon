
    def process_output(self, output_data: Any, format_type: str='json') -> bytes:
        """Process output data for stdout"""
        processor = self.formats.get(format_type, self.output_json)
        return processor(output_data)
