from datetime import datetime
from typing import Dict, List, Any

    def _serialize_registry(self) -> Dict[str, Any]:
        """Serialize registry for JSON storage"""
        return {
            name: {
                'name': metadata.name,
                'type': metadata.type.value,
                'status': metadata.status.value,
                'file_path': metadata.file_path,
                'line_number': metadata.line_number,
                'methods': metadata.methods,
                'created_at': metadata.created_at.isoformat(),
                'compliance_score': metadata.compliance_score
            }
            for name, metadata in self.interfaces.items()
        }

# Global registry instance
registry = InterfaceRegistry()
