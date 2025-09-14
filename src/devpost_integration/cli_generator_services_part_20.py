
    def output_text(self, data: Any) -> bytes:
        """Output data as text"""
        if isinstance(data, list):
            return '\n'.join((str(item) for item in data)).encode('utf-8')
        else:
            return str(data).encode('utf-8')
