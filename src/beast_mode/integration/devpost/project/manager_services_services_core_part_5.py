from src.rm_ddd.core.health import ModuleHealth

def get_project_metadata(self) -> ProjectMetadata:
    """Extract metadata from local project files.
        
        Returns:
            ProjectMetadata instance with extracted information
        """
    metadata = ProjectMetadata(title='Untitled Project')
    package_data = self._extract_package_json_metadata()
    if package_data:
        if package_data.get('name'):
            metadata.title = package_data.get('name', '')
        if package_data.get('description'):
            metadata.description = package_data.get('description', '')
        metadata.repository_url = self._extract_repository_url(package_data)
        metadata.package_info.update(package_data)
    readme_data = self._extract_readme_metadata()
    if readme_data:
        if not metadata.title or metadata.title == 'Untitled Project':
            metadata.title = readme_data.get('title', metadata.title)
        if not metadata.tagline:
            metadata.tagline = readme_data.get('tagline', metadata.tagline)
        if not metadata.description:
            metadata.description = readme_data.get('description', metadata.description)
        metadata.readme_path = readme_data.get('path')
    pyproject_data = self._extract_pyproject_metadata()
    if pyproject_data:
        if pyproject_data.get('name'):
            metadata.title = pyproject_data.get('name', '')
        if pyproject_data.get('description'):
            metadata.description = pyproject_data.get('description', '')
        metadata.repository_url = metadata.repository_url or self._extract_repository_url(pyproject_data)
        metadata.package_info.update(pyproject_data)
    git_data = self._extract_git_metadata()
    if git_data:
        metadata.repository_url = metadata.repository_url or git_data.get('repository_url')
        metadata.team_members.extend(git_data.get('contributors', []))
    metadata.title = metadata.title.strip() if metadata.title != 'Untitled Project' else ''
    metadata.tagline = metadata.tagline.strip()
    metadata.description = metadata.description.strip()
    metadata.team_members = list(set(metadata.team_members))
    if not metadata.title or metadata.title == 'Untitled Project':
        metadata.title = self.project_root.name.replace('-', ' ').replace('_', ' ').title()
    return metadata

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

