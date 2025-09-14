
    def __init__(self, connected: bool = False):
        super().__init__(module_id="project_status", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)
        
        self.connected = connected
        self.project_id = None
        self.project_name = None
        self.local_path = None
        self.last_sync = None
        self.pending_changes = []
        self.validation_errors = []
    