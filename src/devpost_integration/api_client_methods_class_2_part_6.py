from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, api_key: str, base_url: str = "https://devpost.com"):
        super().__init__(module_id="api_client", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)
        
        self.api_key = api_key
        self.base_url = base_url
        self._error_count = 0
        self._command_count = 0
    