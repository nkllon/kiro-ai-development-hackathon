#!/usr/bin/env python3
"""
Neo4j Visualizer

Creates interactive visualizations of the project model graph from Neo4j database.
Uses 1Password item pointers from project model for secure credential access.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class Neo4jVisualizer:
    """Creates interactive visualizations of Neo4j project model"""

    def __init__(self, model_file: str = "project_model_registry.json"):
        self.model_file = Path(model_file)
        self.model_data = None
        self.visualizations_dir = Path("data/visualizations")
        self.neo4j_uri = "neo4j://localhost:7687"

    def load_model(self) -> None:
        """Load the project model with credential mappings"""
        if not self.model_file.exists():
            msg = f"Model file not found: {self.model_file}"
            raise FileNotFoundError(msg)

        with open(self.model_file) as f:
            self.model_data = json.load(f)
        print(f"✅ Loaded model: {self.model_file}")

    def get_credentials(self) -> dict[str, str]:
        """Get Neo4j credentials using 1Password item pointers"""
        credential_mappings = self.model_data.get("credential_mappings", {})

        if not credential_mappings:
            msg = "No credential mappings found in project model"
            raise ValueError(msg)

        # Use 1Password CLI to get actual values
        credentials = {}
        for key, op_pointer in credential_mappings.items():
            if key.startswith("neo4j_"):
                try:
                    # Extract the actual value from 1Password
                    result = subprocess.run(
                        ["op", "read", op_pointer],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    credentials[key] = result.stdout.strip()
                    print(f"✅ Retrieved {key} from 1Password")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Could not retrieve {key}: {e}")
                    # Fallback to environment variable
                    env_key = key.upper()
                    credentials[key] = os.getenv(env_key, "")
                    if credentials[key]:
                        print(f"✅ Retrieved {key} from environment variable {env_key}")

        return credentials


def main():
    """Main execution function"""
    visualizer = Neo4jVisualizer()

    try:
        visualizer.load_model()
        print("✅ Neo4j Visualizer initialized")

    except Exception as e:
        print(f"❌ Initialization failed: {e}")


if __name__ == "__main__":
    main()
