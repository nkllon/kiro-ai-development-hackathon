from src.rm_ddd.core.health import ModuleHealth

    def get_message_history(self, limit: Optional[int]=None) -> Dict[str, List[BeastModeMessage]]:
        """
        Get message history from the router.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Message history
        """
        if self.message_router:
            return self.message_router.get_message_history(limit)
        recent_messages = self.received_messages[-limit:] if limit else self.received_messages
        return {'sent': [], 'received': recent_messages}

    async def announce_office_hours(self, pattern: OfficeHoursPattern, start_time: time, end_time: time, timezone: str='UTC', days_of_week: Optional[Set[int]]=None, description: str='', capabilities_focus: Optional[List[str]]=None) -> None:
        """
        Announce office hours to the network.
        
        Args:
            pattern: Scheduling pattern
            start_time: Start time for office hours
            end_time: End time for office hours
            timezone: Timezone for the schedule
            days_of_week: Days of week for custom patterns
            description: Description of office hours focus
            capabilities_focus: Specific capabilities to focus on
        """
        office_hours = self.collaboration_scheduler.set_office_hours(pattern=pattern, start_time=start_time, end_time=end_time, timezone=timezone, days_of_week=days_of_week, description=description, capabilities_focus=capabilities_focus or [])
        message = BeastModeMessage(type=MessageType.OFFICE_HOURS_ANNOUNCEMENT, source=self.agent_id, target=None, payload={'office_hours': {'pattern': office_hours.pattern.value, 'start_time': office_hours.start_time.isoformat(), 'end_time': office_hours.end_time.isoformat(), 'timezone': office_hours.timezone, 'days_of_week': list(office_hours.days_of_week), 'description': office_hours.description, 'capabilities_focus': office_hours.capabilities_focus, 'max_concurrent_sessions': office_hours.max_concurrent_sessions, 'session_duration_minutes': office_hours.session_duration_minutes}, 'announcement': f'Agent {self.agent_id} office hours: {pattern.value} {start_time}-{end_time}'}, priority=4)
        await self.send_message(message)
        logger.info(f'Announced office hours: {pattern.value} {start_time}-{end_time}')

    async def request_collaboration(self, target_agents: List[str], topic: str, collaboration_type: CollaborationType=CollaborationType.AD_HOC, scheduled_start: Optional[datetime]=None, duration_minutes: int=30, description: str='', required_capabilities: Optional[List[str]]=None) -> str:
        """
        Request collaboration with other agents.
        
        Args:
            target_agents: List of agents to collaborate with
            topic: Collaboration topic
            collaboration_type: Type of collaboration
            scheduled_start: When to start (None for immediate)
            duration_minutes: Session duration
            description: Session description
            required_capabilities: Required capabilities
            
        Returns:
            str: Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        session = self.collaboration_scheduler.schedule_collaboration(participants=[self.agent_id] + target_agents, topic=topic, session_type=collaboration_type, scheduled_start=scheduled_start, duration_minutes=duration_minutes, description=description, required_capabilities=required_capabilities)
        if not session:
            raise RuntimeError('Failed to schedule collaboration session')
        for target_agent in target_agents:
            message = BeastModeMessage(type=MessageType.COLLABORATION_REQUEST, source=self.agent_id, target=target_agent, payload={'request_id': request_id, 'session_id': session.session_id, 'topic': topic, 'collaboration_type': collaboration_type.value, 'scheduled_start': scheduled_start.isoformat() if scheduled_start else None, 'duration_minutes': duration_minutes, 'description': description, 'required_capabilities': required_capabilities or [], 'organizer_capabilities': self.capabilities}, correlation_id=request_id, priority=3)
            await self.send_message(message)
        logger.info(f'Requested collaboration with {len(target_agents)} agents: {topic}')
        return request_id

    async def start_collaboration_session(self, session_id: str) -> bool:
        """
        Start a collaboration session and notify participants.
        
        Args:
            session_id: Session to start
            
        Returns:
            bool: True if session was started successfully
        """
        session = self.collaboration_scheduler.get_session(session_id)
        if not session:
            return False
        success = self.collaboration_scheduler.start_collaboration_session(session_id)
        if not success:
            return False
        for participant in session.participants:
            if participant != self.agent_id:
                message = BeastModeMessage(type=MessageType.COLLABORATION_START, source=self.agent_id, target=participant, payload={'session_id': session_id, 'topic': session.topic, 'organizer': self.agent_id, 'participants': session.participants, 'started_at': datetime.now().isoformat()}, priority=2)
                await self.send_message(message)
        logger.info(f'Started collaboration session {session_id}')
        return True

    async def end_collaboration_session(self, session_id: str, success: bool=True, success_metrics: Optional[Dict[str, Any]]=None) -> bool:
        """
        End a collaboration session and notify participants.
        
        Args:
            session_id: Session to end
            success: Whether the session was successful
            success_metrics: Success metrics and outcomes
            
        Returns:
            bool: True if session was ended successfully
        """
        session = self.collaboration_scheduler.get_session(session_id)
        if not session:
            return False
        ended = self.collaboration_scheduler.end_collaboration_session(session_id, success, success_metrics)
        if not ended:
            return False
        for participant in session.participants:
            if participant != self.agent_id:
                message = BeastModeMessage(type=MessageType.COLLABORATION_END, source=self.agent_id, target=participant, payload={'session_id': session_id, 'success': success, 'success_metrics': success_metrics or {}, 'ended_at': datetime.now().isoformat(), 'organizer': self.agent_id}, priority=2)
                await self.send_message(message)
        logger.info(f'Ended collaboration session {session_id} (success: {success})')
        return True
