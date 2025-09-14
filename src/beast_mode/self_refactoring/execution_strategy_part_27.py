from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def register(self, name: str, interface_type: InterfaceType, 
                file_path: str, line_number: int, methods: List[str]) -> bool:
        """Register an interface"""
        try:
            metadata = InterfaceMetadata(
                name=name,
                type=interface_type,
                status=InterfaceStatus.ACTIVE,
                file_path=file_path,
                line_number=line_number,
                methods=methods,
                created_at=datetime.now(),
                compliance_score=0.0
            )
            self.interfaces[name] = metadata
            self.save_registry()
            return True
        except Exception as e:
            print(f"Error registering interface {name}: {e}")
            return False
    