
    def process_input(self, input_data: bytes, format_type: str='auto') -> ProcessedInput:
        """Process stdin input based on format"""
        if format_type == 'auto':
            format_type = self.detect_format(input_data)
        processor = self.formats.get(format_type, self.process_text_input)
        return processor(input_data)
