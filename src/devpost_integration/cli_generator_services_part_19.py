
    def output_json(self, data: Any) -> bytes:
        """Output data as JSON"""
        try:
            json_str = json.dumps(data, indent=2, default=str)
            return json_str.encode('utf-8')
        except (TypeError, ValueError) as e:
            error_data = {'error': str(e), 'data': str(data)}
            return json.dumps(error_data).encode('utf-8')
