
    def __init__(self, project_data: Dict[str, Any]=None):
        """Initialize DevPost project."""
        super().__init__()
        self.module_id = 'devpost_project'
        self.version = '1.0.0'
        self.project_data = project_data or {}
        self.project_id = self.project_data.get('project_id', '')
        self.title = self.project_data.get('title', '')
        self.description = self.project_data.get('description', '')
        self.status = self.project_data.get('status', SubmissionStatus.DRAFT)
        self.team_members = self.project_data.get('team_members', [])
        self.submission_deadline = self.project_data.get('submission_deadline', None)
        self._operation_count = 0
        self._errors = 0
        register_module(self)
