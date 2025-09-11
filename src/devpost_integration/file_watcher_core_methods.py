class FileWatcherCore(ReflectiveModule):
    """
    Core file system monitoring functionality.
    
    Provides essential file watching capabilities with debouncing
    and event handling infrastructure.
    """
    
    def __init__(
        self,
        project_path: Path,
        config: Optional[DevpostConfig] = None
    ):
        """Initialize core file watcher."""
        self.project_path = Path(project_path).resolve()
        self.config = config or DevpostConfig()
        
        # File tracking
        self.file_hashes: Dict[str, str] = {}
        self.file_timestamps: Dict[str, float] = {}
        self.ignored_patterns: Set[str] = self._get_ignored_patterns()
        
        # Debouncing
        self.debounce_delay = 2.0
        self.pending_changes: Dict[str, FileChangeEvent] = {}
        self.debounce_timer: Optional[threading.Timer] = None
        
        # Event handling
        self.change_callbacks: List[Callable[[FileChangeEvent], None]] = []
        self.event_queue: deque = deque(maxlen=1000)
        
        # Monitoring state
        self.is_monitoring = False
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[ProjectFileEventHandler] = None
        
        # Statistics
        self.stats = {
            'files_monitored': 0,
            'changes_detected': 0,
            'changes_processed': 0,
            'last_scan': None
        }
    
    def _get_ignored_patterns(self) -> Set[str]:
        """Get patterns to ignore during file monitoring."""
        return {
            '*.pyc', '*.pyo', '__pycache__', '.git', '.DS_Store',
            '*.log', '*.tmp', '*.swp', '*.swo', 'node_modules',
            '.venv', 'venv', 'env', '.env', '*.egg-info'
        }
    
    def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Add callback for file change events."""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Remove callback for file change events."""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def start_monitoring(self) -> bool:
        """Start file system monitoring."""
        if self.is_monitoring:
            logger.warning("File monitoring already active")
            return False
        
        try:
            self.event_handler = ProjectFileEventHandler(self)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.project_path),
                recursive=True
            )
            self.observer.start()
            self.is_monitoring = True
            self._perform_initial_scan()
            logger.info(f"Started monitoring {self.project_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop file system monitoring."""
        if not self.is_monitoring:
            return False
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            if self.debounce_timer:
                self.debounce_timer.cancel()
                self.debounce_timer = None
            
            self.is_monitoring = False
            logger.info("Stopped file monitoring")
            return True
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def _perform_initial_scan(self) -> None:
        """Perform initial scan of project files."""
        logger.info("Performing initial file scan...")
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                self._track_file(file_path)
        
        self.stats['files_monitored'] = len(self.file_hashes)
        self.stats['last_scan'] = datetime.now()
        logger.info(f"Initial scan complete: {self.stats['files_monitored']} files tracked")
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        for pattern in self.ignored_patterns:
            if file_path.match(pattern) or pattern in str(file_path):
                return True
        return False
    
    def _track_file(self, file_path: Path) -> None:
        """Track file for changes."""
        try:
            file_str = str(file_path)
            stat = file_path.stat()
            self.file_timestamps[file_str] = stat.st_mtime
            
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()
                    self.file_hashes[file_str] = file_hash
            except (IOError, OSError):
                pass
                
        except Exception as e:
            logger.debug(f"Error tracking file {file_path}: {e}")
    
    def _handle_file_change(self, file_path: Path, change_type: ChangeType) -> None:
        """Handle file change event."""
        if self._should_ignore_file(file_path):
            return
        
        file_str = str(file_path)
        event = FileChangeEvent(
            file_path=file_path,
            change_type=change_type,
            timestamp=datetime.now(),
            content_type=self._detect_content_type(file_path)
        )
        
        self.pending_changes[file_str] = event
        self.stats['changes_detected'] += 1
        self._start_debounce_timer()
    
    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Detect content type of file."""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.py']:
            return ContentType.CODE
        elif suffix in ['.md', '.txt', '.rst']:
            return ContentType.DOCUMENTATION
        elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
            return ContentType.IMAGE
        elif suffix in ['.mp4', '.avi', '.mov', '.webm']:
            return ContentType.VIDEO
        elif suffix in ['.zip', '.tar', '.gz']:
            return ContentType.ARCHIVE
        else:
            return ContentType.OTHER
    
    def _start_debounce_timer(self) -> None:
        """Start debounce timer for processing changes."""
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        self.debounce_timer = threading.Timer(
            self.debounce_delay,
            self._process_pending_changes
        )
        self.debounce_timer.start()
    
    def _process_pending_changes(self) -> None:
        """Process all pending file changes."""
        if not self.pending_changes:
            return
        
        logger.info(f"Processing {len(self.pending_changes)} pending changes")
        
        for event in self.pending_changes.values():
            self._notify_change_callbacks(event)
            self.stats['changes_processed'] += 1
        
        self.pending_changes.clear()
        self._update_file_tracking()
    
    def _notify_change_callbacks(self, event: FileChangeEvent) -> None:
        """Notify all registered callbacks of file change."""
        for callback in self.change_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in change callback: {e}")
    
    def _update_file_tracking(self) -> None:
        """Update file tracking information."""
        for file_path in list(self.file_hashes.keys()):
            path = Path(file_path)
            if not path.exists():
                del self.file_hashes[file_path]
                if file_path in self.file_timestamps:
                    del self.file_timestamps[file_path]
            else:
                self._track_file(path)
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            **self.stats,
            'is_monitoring': self.is_monitoring,
            'pending_changes': len(self.pending_changes),
            'files_tracked': len(self.file_hashes)
        }

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'File Watcher Core',
            'description': 'file_watcher_core module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")