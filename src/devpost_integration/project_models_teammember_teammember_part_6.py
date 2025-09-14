
    def __init__(self, member_data: Dict[str, Any]=None):
        """Initialize team member."""
        super().__init__()
        self.module_id = 'team_member'
        self.version = '1.0.0'
        self.member_data = member_data or {}
        self.member_id = self.member_data.get('id', '')
        self.name = self.member_data.get('name', '')
        self.email = self.member_data.get('email', '')
        self.role = self.member_data.get('role', 'member')
        self.permissions = self.member_data.get('permissions', [])
        self._operation_count = 0
        self._errors = 0
        register_module(self)
