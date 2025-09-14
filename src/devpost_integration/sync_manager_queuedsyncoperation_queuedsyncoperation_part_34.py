
    def __init__(self) -> Any:
        super().__init__(module_id="sync_manager", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        self.config_path = Path('.devpost/config.json')
    