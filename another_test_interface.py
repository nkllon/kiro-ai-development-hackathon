
from src.beast_mode.core.interfaces import ReflectiveModule

class AnotherTestInterface(ReflectiveModule):
    def get_health_status(self):
        return {"status": "healthy"}
    
    def get_metrics(self):
        return {"test": "metrics"}

