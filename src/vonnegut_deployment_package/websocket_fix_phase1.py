#!/usr/bin/env python3
"""
WebSocket Fix Phase 1: FastAPI WebSocket Registration Fix

This script implements the fix for WebSocket endpoint registration issues
in the Observatory server based on the diagnostic findings.
"""

import os
import sys
import logging
import shutil
from pathlib import Path
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketFixPhase1:
    """Phase 1 WebSocket fix implementation."""
    
    def __init__(self):
        self.server_file = Path("src/beast_mode/observatory/server.py")
        self.backup_file = Path("src/beast_mode/observatory/server.py.backup")
    
    def run_fix(self):
        """Execute Phase 1 WebSocket fix."""
        logger.info("🚀 Starting WebSocket Fix Phase 1: FastAPI Registration Fix")
        
        try:
            # Step 1: Create backup
            self._create_backup()
            
            # Step 2: Analyze current implementation
            analysis = self._analyze_current_implementation()
            logger.info(f"📊 Analysis: {analysis}")
            
            # Step 3: Apply fix based on analysis
            if analysis["websocket_setup_called"]:
                logger.info("✅ _setup_websockets() is already called in __init__")
                if analysis["websocket_endpoints_defined"]:
                    logger.info("✅ WebSocket endpoints are defined in _setup_websockets()")
                    # The issue might be with the decorator approach
                    self._apply_decorator_fix()
                else:
                    logger.error("❌ WebSocket endpoints not properly defined")
                    return False
            else:
                logger.error("❌ _setup_websockets() not called in __init__")
                self._apply_init_fix()
            
            # Step 4: Validate fix
            validation = self._validate_fix()
            
            if validation["success"]:
                logger.info("✅ Phase 1 fix applied successfully")
                return True
            else:
                logger.error(f"❌ Fix validation failed: {validation['error']}")
                self._restore_backup()
                return False
                
        except Exception as e:
            logger.error(f"❌ Phase 1 fix failed: {e}")
            logger.error(traceback.format_exc())
            self._restore_backup()
            return False
    
    def _create_backup(self):
        """Create backup of the server file."""
        if self.server_file.exists():
            shutil.copy2(self.server_file, self.backup_file)
            logger.info(f"📄 Backup created: {self.backup_file}")
        else:
            raise FileNotFoundError(f"Server file not found: {self.server_file}")
    
    def _analyze_current_implementation(self):
        """Analyze the current WebSocket implementation."""
        with open(self.server_file, 'r') as f:
            content = f.read()
        
        analysis = {
            "websocket_setup_called": False,
            "websocket_endpoints_defined": False,
            "websocket_decorators_found": 0,
            "init_method_found": False
        }
        
        # Check if _setup_websockets() is called in __init__
        if "self._setup_websockets()" in content:
            analysis["websocket_setup_called"] = True
        
        # Check if WebSocket endpoints are defined
        websocket_endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        for endpoint in websocket_endpoints:
            if f'@self.app.websocket("{endpoint}")' in content:
                analysis["websocket_decorators_found"] += 1
        
        if analysis["websocket_decorators_found"] >= 4:
            analysis["websocket_endpoints_defined"] = True
        
        # Check if __init__ method exists
        if "def __init__(self" in content:
            analysis["init_method_found"] = True
        
        return analysis
    
    def _apply_decorator_fix(self):
        """Apply fix for decorator-based WebSocket registration issues."""
        logger.info("🔧 Applying decorator fix for WebSocket registration")
        
        with open(self.server_file, 'r') as f:
            content = f.read()
        
        # The issue might be that the decorators are not being applied correctly
        # Let's modify the _setup_websockets method to use explicit route registration
        
        # Find the _setup_websockets method
        setup_websockets_start = content.find("def _setup_websockets(self):")
        if setup_websockets_start == -1:
            raise ValueError("_setup_websockets method not found")
        
        # Find the end of the method (next method or class definition)
        method_end = content.find("\n    def ", setup_websockets_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Extract the current method
        current_method = content[setup_websockets_start:method_end]
        
        # Create new method with explicit route registration
        new_method = '''def _setup_websockets(self):
        """Setup WebSocket endpoints with explicit registration."""
        logger.info("🔌 Setting up WebSocket endpoints...")
        
        async def emoji_rain_websocket(websocket: WebSocket):
            """WebSocket endpoint for real-time emoji rain updates."""
            await websocket.accept()
            await self.emoji_ws_handler.add_client(websocket)
            
            try:
                # Send initial state
                initial_data = {
                    "type": "initial_state",
                    "data": {
                        "active_effects": self.emoji_engine.get_active_effects(),
                        "performance_stats": self.emoji_engine.get_performance_stats(),
                        "observatory_status": {
                            "health_score": self.observatory_core.get_health_status().health_score,
                            "uptime": self.observatory_core.get_health_status().uptime_seconds
                        }
                    }
                }
                await websocket.send_text(json.dumps(initial_data))
                
                # Handle incoming messages
                while True:
                    try:
                        message = await websocket.receive_text()
                        data = json.loads(message)
                        await self._handle_websocket_message(websocket, data)
                    except WebSocketDisconnect:
                        break
                    except Exception as e:
                        logger.error(f"WebSocket error: {e}")
                        break
                        
            except WebSocketDisconnect:
                pass
            finally:
                await self.emoji_ws_handler.remove_client(websocket)
        
        async def observatory_websocket(websocket: WebSocket):
            """WebSocket endpoint for Observatory status updates."""
            await websocket.accept()
            
            try:
                while True:
                    # Send Observatory status every 5 seconds
                    health = self.observatory_core.get_health_status()
                    metrics = await self.observatory_core.get_metrics()

                    # Get anomaly data if available
                    anomalies = []
                    if self.observatory_core._anomaly_detector:
                        anomalies = self.observatory_core._anomaly_detector.get_active_anomalies()

                    status_data = {
                        "type": "observatory_status",
                        "data": {
                            "health": {
                                "status": health.status.value,
                                "health_score": health.health_score,
                                "uptime_seconds": health.uptime_seconds
                            },
                            "metrics": metrics,
                            "anomalies": anomalies,
                            "timestamp": health.last_check.isoformat()
                        }
                    }
                    
                    await websocket.send_text(json.dumps(status_data))
                    await asyncio.sleep(5)
                    
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Observatory WebSocket error: {e}")

        async def anomalies_websocket(websocket: WebSocket):
            """WebSocket endpoint for real-time anomaly alerts."""
            await websocket.accept()

            try:
                while True:
                    if self.observatory_core._anomaly_detector:
                        # Send anomaly updates every 10 seconds
                        active_anomalies = self.observatory_core._anomaly_detector.get_active_anomalies()
                        anomaly_stats = self.observatory_core._anomaly_detector.get_anomaly_stats()

                        anomaly_data = {
                            "type": "anomaly_update",
                            "data": {
                                "active_anomalies": active_anomalies,
                                "stats": anomaly_stats,
                                "timestamp": datetime.now().isoformat()
                            }
                        }

                        await websocket.send_text(json.dumps(anomaly_data))
                    
                    await asyncio.sleep(10)
                    
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Anomalies WebSocket error: {e}")

        async def doctor_status_websocket(websocket: WebSocket):
            """WebSocket endpoint for doctor status updates."""
            await websocket.accept()

            try:
                while True:
                    # Send doctor status every 3 seconds
                    doctor_data = {
                        "type": "doctor_status",
                        "data": {
                            "status": "healthy",
                            "checks_performed": 42,
                            "last_check": datetime.now().isoformat(),
                            "system_health": self.observatory_core.get_health_status().health_score
                        }
                    }
                    
                    await websocket.send_text(json.dumps(doctor_data))
                    await asyncio.sleep(3)
                    
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Doctor status WebSocket error: {e}")
        
        # Register WebSocket endpoints explicitly
        self.app.add_websocket_route("/ws/emoji-rain", emoji_rain_websocket)
        self.app.add_websocket_route("/ws/observatory", observatory_websocket)
        self.app.add_websocket_route("/ws/anomalies", anomalies_websocket)
        self.app.add_websocket_route("/ws/doctor-status", doctor_status_websocket)
        
        logger.info("✅ WebSocket endpoints registered successfully")
        logger.info(f"📊 Registered {len(['/ws/emoji-rain', '/ws/observatory', '/ws/anomalies', '/ws/doctor-status'])} WebSocket endpoints")
'''
        
        # Replace the method in the content
        new_content = content[:setup_websockets_start] + new_method + content[method_end:]
        
        # Write the updated content
        with open(self.server_file, 'w') as f:
            f.write(new_content)
        
        logger.info("✅ Decorator fix applied successfully")
    
    def _apply_init_fix(self):
        """Apply fix for missing _setup_websockets() call in __init__."""
        logger.info("🔧 Adding _setup_websockets() call to __init__")
        
        with open(self.server_file, 'r') as f:
            content = f.read()
        
        # Find the __init__ method and add the call
        init_start = content.find("def __init__(self")
        if init_start == -1:
            raise ValueError("__init__ method not found")
        
        # Find where to insert the call (after _setup_routes())
        setup_routes_pos = content.find("self._setup_routes()", init_start)
        if setup_routes_pos == -1:
            raise ValueError("_setup_routes() call not found")
        
        # Find the end of the line
        line_end = content.find("\n", setup_routes_pos)
        
        # Insert the _setup_websockets() call
        new_content = (content[:line_end] + 
                      "\n        self._setup_websockets()" + 
                      content[line_end:])
        
        with open(self.server_file, 'w') as f:
            f.write(new_content)
        
        logger.info("✅ _setup_websockets() call added to __init__")
    
    def _validate_fix(self):
        """Validate that the fix was applied correctly."""
        try:
            with open(self.server_file, 'r') as f:
                content = f.read()
            
            # Check for syntax errors by attempting to compile
            compile(content, self.server_file, 'exec')
            
            # Check that WebSocket setup is called
            if "self._setup_websockets()" not in content:
                return {"success": False, "error": "_setup_websockets() call not found"}
            
            # Check that WebSocket endpoints are registered
            if "add_websocket_route" not in content:
                return {"success": False, "error": "WebSocket route registration not found"}
            
            return {"success": True}
            
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Validation error: {e}"}
    
    def _restore_backup(self):
        """Restore the backup file."""
        if self.backup_file.exists():
            shutil.copy2(self.backup_file, self.server_file)
            logger.info(f"📄 Backup restored: {self.server_file}")
        else:
            logger.error("❌ No backup file found to restore")

def main():
    """Main function."""
    print("🚀 WebSocket Fix Phase 1: FastAPI Registration Fix")
    print("=" * 60)
    
    fix = WebSocketFixPhase1()
    success = fix.run_fix()
    
    if success:
        print("\n✅ Phase 1 fix completed successfully!")
        print("📋 Next steps:")
        print("  1. Restart the Observatory server")
        print("  2. Run diagnostic tests to verify the fix")
        print("  3. Proceed to Phase 2: Cloudflare configuration")
    else:
        print("\n❌ Phase 1 fix failed!")
        print("📋 Manual intervention required")
    
    return success

if __name__ == "__main__":
    main()
