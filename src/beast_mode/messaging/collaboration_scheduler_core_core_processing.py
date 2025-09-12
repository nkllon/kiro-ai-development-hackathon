"""
Collaboration Scheduler Core Core Processing

This module was extracted from collaboration_scheduler_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import uuid
from .models import BeastModeMessage, MessageType, AgentCapabilities

def process_offline_collaboration_queue(self, agent_id: str) -> List[Dict[str, Any]]:
    """
        Process queued collaboration requests for an agent that came online.
        
        Args:
            agent_id: Agent that came online
            
        Returns:
            List of collaboration requests for the agent
        """
    agent_requests = []
    remaining_queue = []
    for item in self.offline_collaboration_queue:
        if item['target_agent'] == agent_id:
            agent_requests.append(item)
        else:
            remaining_queue.append(item)
    self.offline_collaboration_queue = remaining_queue
    if agent_requests:
        logger.info(f'Processing {len(agent_requests)} queued collaborations for {agent_id}')
    return agent_requests
