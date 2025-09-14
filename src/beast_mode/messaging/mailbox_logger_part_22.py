from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class GetlogfilesClass:
    """Auto-generated class for functions."""

    def get_log_files(self) -> List[Dict[str, Any]]:
    """Get information about all log files"""
    log_files = []
    try:
    for file_path in self.log_directory.glob('mailbox_*.log'):
    if file_path.is_file():
    stat = file_path.stat()
    log_files.append({'path': str(file_path), 'size_bytes': stat.st_size, 'size_mb': round(stat.st_size / (1024 * 1024), 2), 'created': datetime.fromtimestamp(stat.st_ctime).isoformat(), 'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(), 'is_current': file_path == self.current_log_file})
    log_files.sort(key=lambda x: x['created'], reverse=True)
    except Exception as e:
    logger.error(f'Error getting log file information: {e}')
    return log_files

    async def check_mail(self, since: Optional[datetime]=None, message_types: Optional[List[MessageType]]=None, source_agents: Optional[List[str]]=None, limit: Optional[int]=None) -> List[Dict[str, Any]]:
    """
    Check mail by scanning log files for messages.

    Args:
    since: Only return messages after this timestamp
    message_types: Filter by message types
    source_agents: Filter by source agent IDs
    limit: Maximum number of messages to return

    Returns:
    List of matching messages
    """
    messages = []
    try:
    log_files = self.get_log_files()
    for log_file_info in log_files:
    file_path = Path(log_file_info['path'])
    if since:
    file_modified = datetime.fromisoformat(log_file_info['modified'])
    if file_modified < since:
    continue
    try:
    with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
    line = line.strip()
    if not line:
    continue
    try:
    log_entry = json.loads(line)
    if since:
    entry_time = datetime.fromisoformat(log_entry['timestamp'])
    if entry_time < since:
    continue
    if log_entry.get('parsed_message'):
    message_data = log_entry['parsed_message']
    if message_types and message_data.get('type') not in message_types:
    continue
    if source_agents and message_data.get('source') not in source_agents:
    continue
    messages.append({'log_timestamp': log_entry['timestamp'], 'message': message_data, 'log_file': str(file_path)})
    if limit and len(messages) >= limit:
    break
    except json.JSONDecodeError:
    continue
    except Exception as e:
    logger.error(f'Error reading log file {file_path}: {e}')
    continue
    if limit and len(messages) >= limit:
    break
    messages.sort(key=lambda x: x['log_timestamp'], reverse=True)
    if limit:
    messages = messages[:limit]
    except Exception as e:
    logger.error(f'Error checking mail: {e}')
    return messages

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

