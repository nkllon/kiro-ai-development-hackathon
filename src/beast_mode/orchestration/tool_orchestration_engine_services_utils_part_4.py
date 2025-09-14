from src.rm_ddd.core.health import ModuleHealth

def _execute_single_tool(self, tool_id: str, context: DecisionContext, operation_id: str) -> ToolExecutionResult:
    """
        Execute a single tool with comprehensive monitoring
        """
    tool_def = self.tools_registry[tool_id]
    start_time = time.time()
    try:
        command = tool_def.command
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=tool_def.timeout_seconds, cwd=self.project_root)
        execution_time = int((time.time() - start_time) * 1000)
        success = result.returncode == 0
        self.tool_health_cache[tool_id] = ToolStatus.HEALTHY if success else ToolStatus.DEGRADED
        return ToolExecutionResult(tool_id=tool_id, success=success, output=result.stdout, error=result.stderr if result.stderr else None, execution_time_ms=execution_time, exit_code=result.returncode, health_status=self.tool_health_cache[tool_id])
    except subprocess.TimeoutExpired:
        execution_time = int((time.time() - start_time) * 1000)
        self.tool_health_cache[tool_id] = ToolStatus.FAILED
        return ToolExecutionResult(tool_id=tool_id, success=False, output='', error=f'Tool execution timed out after {tool_def.timeout_seconds} seconds', execution_time_ms=execution_time, health_status=ToolStatus.FAILED)
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        self.tool_health_cache[tool_id] = ToolStatus.FAILED
        return ToolExecutionResult(tool_id=tool_id, success=False, output='', error=f'Tool execution failed: {str(e)}', execution_time_ms=execution_time, health_status=ToolStatus.FAILED)
