from datetime import datetime
from typing import Dict, List, Any

    def load_metrics(self):
        """Load interface metrics from storage"""
        metrics_file = self.registry_file.replace('.json', '_metrics.json')
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                for interface_id, metrics_data in data.items():
                    self.metrics[interface_id] = InterfaceMetrics(**metrics_data)
            except Exception as e:
                print(f"Warning: Could not load metrics: {e}")
    