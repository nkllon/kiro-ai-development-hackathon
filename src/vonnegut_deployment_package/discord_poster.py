#!/usr/bin/env python3
"""Discord integration for posting completed specifications and coordination results."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests

class DiscordPoster:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv('DISCORD_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError("Discord webhook URL not provided")
    
    def post_spec_completion(self, spec_path: str) -> bool:
        """Post a completed specification to Discord."""
        spec_name = Path(spec_path).name
        
        # Read spec files
        requirements_file = Path(spec_path) / "requirements.md"
        design_file = Path(spec_path) / "design.md" 
        tasks_file = Path(spec_path) / "tasks.md"
        
        files_completed = []
        if requirements_file.exists():
            files_completed.append("📋 Requirements")
        if design_file.exists():
            files_completed.append("🏗️ Design")
        if tasks_file.exists():
            files_completed.append("✅ Tasks")
        
        # Create Discord embed
        embed = {
            "title": f"📚 Spec Completed: {spec_name}",
            "description": f"New specification completed with {len(files_completed)} documents",
            "color": 0x00ff00,  # Green
            "fields": [
                {
                    "name": "Completed Documents",
                    "value": "\n".join(files_completed),
                    "inline": False
                },
                {
                    "name": "Timestamp",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "AI Coordination Framework"
            }
        }
        
        return self._send_message({"embeds": [embed]})
    
    def post_coordination_results(self, results: Dict) -> bool:
        """Post coordination experiment results to Discord."""
        embed = {
            "title": "🤖 AI Coordination Results",
            "description": "Latest coordination experiment completed",
            "color": 0x0099ff,  # Blue
            "fields": [
                {
                    "name": "Tasks Completed",
                    "value": f"{results.get('completed_tasks', 0)}/{results.get('total_tasks', 0)}",
                    "inline": True
                },
                {
                    "name": "Success Rate",
                    "value": f"{results.get('success_rate', 0):.1%}",
                    "inline": True
                },
                {
                    "name": "Duration",
                    "value": results.get('duration', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "LLM Providers Used",
                    "value": ", ".join(results.get('llm_providers', [])),
                    "inline": False
                },
                {
                    "name": "Key Insights",
                    "value": results.get('insights', 'No insights provided'),
                    "inline": False
                }
            ]
        }
        
        return self._send_message({"embeds": [embed]})
    
    def post_experiment_findings(self, findings: Dict) -> bool:
        """Post experimental findings and comparisons."""
        color = 0xff9900 if findings.get('status') == 'partial' else 0x00ff00
        
        embed = {
            "title": "🔬 Experiment Findings",
            "description": findings.get('summary', 'Experimental results available'),
            "color": color,
            "fields": []
        }
        
        # Add findings as fields
        for key, value in findings.items():
            if key not in ['summary', 'status']:
                embed["fields"].append({
                    "name": key.replace('_', ' ').title(),
                    "value": str(value),
                    "inline": len(str(value)) < 50
                })
        
        return self._send_message({"embeds": [embed]})
    
    def post_status_update(self, status: Dict) -> bool:
        """Post a status update."""
        embed = {
            "title": "📊 Status Update",
            "description": status.get('message', 'System status update'),
            "color": 0x808080,  # Gray
            "fields": [
                {
                    "name": "Active Workers",
                    "value": str(status.get('active_workers', 0)),
                    "inline": True
                },
                {
                    "name": "Completed Tasks",
                    "value": str(status.get('completed_tasks', 0)),
                    "inline": True
                },
                {
                    "name": "System Health",
                    "value": status.get('health', 'Unknown'),
                    "inline": True
                }
            ]
        }
        
        return self._send_message({"embeds": [embed]})
    
    def _send_message(self, payload: Dict) -> bool:
        """Send message to Discord webhook."""
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send Discord message: {e}")
            return False

def main():
    """CLI interface for Discord posting."""
    if len(sys.argv) < 3:
        print("Usage: discord_poster.py <action> <data>")
        print("Actions: spec_completion, coordination_results, experiment_findings, status_update")
        sys.exit(1)
    
    action = sys.argv[1]
    data_arg = sys.argv[2]
    
    poster = DiscordPoster()
    
    if action == "spec_completion":
        success = poster.post_spec_completion(data_arg)
    elif action == "coordination_results":
        data = json.loads(data_arg)
        success = poster.post_coordination_results(data)
    elif action == "experiment_findings":
        data = json.loads(data_arg)
        success = poster.post_experiment_findings(data)
    elif action == "status_update":
        data = json.loads(data_arg)
        success = poster.post_status_update(data)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
    
    if success:
        print("Message posted successfully")
    else:
        print("Failed to post message")
        sys.exit(1)

if __name__ == "__main__":
    main()