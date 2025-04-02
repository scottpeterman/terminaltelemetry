# backend/message_router.py
import asyncio
import traceback

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget
import json
import logging
from termtel.termtelng.backend.sessions import SSHSession, TelemetrySession, UISession

logger = logging.getLogger(__name__)


class MessageRouter(QObject):
    """
    Central message routing system that manages all sessions and message dispatch
    """
    message_to_frontend = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # Initialize our sessions
        self.sessions = {
            "terminal": SSHSession("terminal"),
            "telemetry": TelemetrySession("telemetry"),
            "ui_state": UISession("ui_state")
        }

        # Set router reference in each session
        for session in self.sessions.values():
            if hasattr(session, 'message_router'):
                session.message_router = self

        # Connect each session's message_ready signal to our frontend relay
        for session in self.sessions.values():
            session.message_ready.connect(self._relay_to_frontend)

        logger.info("MessageRouter initialized with sessions")

    @pyqtSlot(str)
    def handle_frontend_message(self, message_json: str):
        """Entry point for all messages from frontend"""
        try:
            message = json.loads(message_json)
            session_id = message.get("session_id")

            if session_id not in self.sessions:
                logger.error(f"Unknown session ID: {session_id}")
                return

            session = self.sessions[session_id]
            action = message.get("action")
            payload = message.get("payload", {})

            # Check if we're in a widget context
            is_widget = isinstance(self.parent, QWidget)

            if is_widget:
                # Handle synchronously for widgets
                self._handle_message_sync(session, action, payload)
            else:
                # Use async for regular windows
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(self._handle_message_async(session, action, payload))
                except RuntimeError as e:
                    logger.error(f"Asyncio error: {e}")
                    # Fallback to sync handling
                    self._handle_message_sync(session, action, payload)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message_json}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self._send_error("system", str(e))

    def _handle_message_sync(self, session, action, payload):
        """Synchronous version of message handling for widget context"""
        print(f"session: {session} action: {action} payload: {payload}")
        try:
            # Handle basic UI actions synchronously
            if action == "zoom_in":
                if hasattr(self.parent, 'web_view'):
                    current_factor = self.parent.web_view.zoomFactor()
                    self.parent.web_view.setZoomFactor(min(current_factor + 0.1, 5.0))
            elif action == "zoom_out":
                if hasattr(self.parent, 'web_view'):
                    current_factor = self.parent.web_view.zoomFactor()
                    self.parent.web_view.setZoomFactor(max(current_factor - 0.1, 0.25))
            elif action == "set_theme":
                # Update widget theme if available
                if hasattr(self.parent, 'update_theme'):
                    self.parent.update_theme(payload.get("theme"))

            # For other actions, we'll need to create and run a temporary event loop
            # to execute the async methods synchronously
            else:
                # Get the method to call
                method_name = f"handle_{action}" if action not in ["connect", "disconnect", "data", "resize",
                                                                   "get_device_info", "get_environment"] else action

                if hasattr(session, method_name):
                    method = getattr(session, method_name)

                    # Only try to run async methods
                    if asyncio.iscoroutinefunction(method):
                        # Create a new event loop
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            # Run the async method in this temporary loop
                            if action == "connect":
                                loop.run_until_complete(method(**payload))
                            elif action == "disconnect":
                                # Special case for disconnect which doesn't take parameters
                                loop.run_until_complete(method())
                            elif action == "data" or action == "resize":
                                loop.run_until_complete(method(payload))
                            elif action == "set_theme":
                                loop.run_until_complete(method(payload.get("theme")))
                            else:
                                loop.run_until_complete(method(payload))

                            # Clean up
                            loop.close()
                        except Exception as e:
                            print(f"Error running async method in temp loop: {e}")
                            traceback.print_exc()
                    else:
                        # If it's a sync method, just call it directly
                        if action == "connect":
                            method(**payload)
                        elif action == "disconnect":
                            # Special case for disconnect which doesn't take parameters
                            method(payload=None)
                        elif action == "data" or action == "resize":
                            method(payload)
                        elif action == "set_theme":
                            method(payload.get("theme"))
                        else:
                            method(payload)
                else:
                    logger.warning(f"Unknown action {action} for session {session.session_id}")

        except Exception as e:
            logger.error(f"Error in sync message handling: {e}")
            traceback.print_exc()
            self._send_error(session.session_id, str(e))
    async def _handle_message_async(self, session, action, payload):
        """Handle async message processing"""
        print(f"session: {session} action: {action} payload: {payload}")
        try:
            if action == "connect":
                await session.connect(**payload)
            elif action == "disconnect":
                await session.disconnect()
            elif action == "data":
                await session.handle_data(payload)
            elif action == "resize":
                await session.handle_resize(payload)
            elif action == "set_theme":
                await session.set_theme(payload.get("theme"))
            elif action == "get_device_info":
                try:
                    await session.get_device_info()
                except:
                    pass  # will retry
            elif action == "get_environment":
                try:
                    await session.get_environment_data()
                except:
                    traceback.print_exc()
                    pass
            elif action == "start_monitoring" and isinstance(session, SSHSession):
                print("start_monitoring not yet implemented")
            elif action == "zoom_in":
                # Access the main window through the view
                view = self.parent
                if hasattr(view, 'page'):
                    current_factor = view.zoomFactor()
                    view.setZoomFactor(min(current_factor + 0.1, 5.0))
            elif action == "zoom_out":
                view = self.parent
                if hasattr(view, 'page'):
                    current_factor = view.zoomFactor()
                    view.setZoomFactor(max(current_factor - 0.1, 0.25))
            else:
                if hasattr(session, f"handle_{action}"):
                    method = getattr(session, f"handle_{action}")
                    await method(payload)
                else:
                    logger.warning(f"Unknown action {action} for session {session.session_id}")
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in async message handling: {e}")
            self._send_error(session.session_id, str(e))

    def _relay_to_frontend(self, message: str):
        """Relay messages from sessions to frontend"""
        print(f"Sending telemetry update directly through message router")
        print(f"Payload: \n{message}")
        self.message_to_frontend.emit(message)

    def _send_error(self, session_id: str, error_message: str):
        """Utility method to send error messages to frontend"""
        error = {
            "session_id": session_id,
            "action": "error",
            "payload": {"message": error_message}
        }
        self.message_to_frontend.emit(json.dumps(error))

    def _handle_message_sync(self, session, action, payload):
        """Synchronous version of message handling for widget context"""
        print(f"session: {session} action: {action} payload: {payload}")
        try:
            # Handle basic UI actions synchronously
            if action == "zoom_in":
                if hasattr(self.parent, 'web_view'):
                    current_factor = self.parent.web_view.zoomFactor()
                    self.parent.web_view.setZoomFactor(min(current_factor + 0.1, 5.0))
            elif action == "zoom_out":
                if hasattr(self.parent, 'web_view'):
                    current_factor = self.parent.web_view.zoomFactor()
                    self.parent.web_view.setZoomFactor(max(current_factor - 0.1, 0.25))
            elif action == "set_theme":
                # Update widget theme if available
                if hasattr(self.parent, 'update_theme'):
                    self.parent.update_theme(payload.get("theme"))

            # For other actions, we'll need to create and run a temporary event loop
            # to execute the async methods synchronously
            else:
                # Get the method to call
                method_name = f"handle_{action}" if action not in ["connect", "disconnect", "data", "resize",
                                                                   "get_device_info", "get_environment"] else action

                if hasattr(session, method_name):
                    method = getattr(session, method_name)

                    # Only try to run async methods
                    if asyncio.iscoroutinefunction(method):
                        # Create a new event loop
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            # Run the async method in this temporary loop
                            if action in ["connect", "data", "resize"]:
                                loop.run_until_complete(method(**payload))
                            elif action in ["set_theme"]:
                                loop.run_until_complete(method(payload.get("theme")))
                            else:
                                try:
                                    loop.run_until_complete(method(payload))
                                except Exception as e:
                                    print(e)
                                    traceback.print_exc()

                            # Clean up
                            loop.close()
                        except Exception as e:
                            print(f"Error running async method in temp loop: {e}")
                            traceback.print_exc()
                    else:
                        # If it's a sync method, just call it directly
                        if action in ["connect", "data", "resize"]:
                            method(**payload)
                        elif action in ["set_theme"]:
                            method(payload.get("theme"))
                        else:
                            method(payload)
                else:
                    logger.warning(f"Unknown action {action} for session {session.session_id}")

        except Exception as e:
            logger.error(f"Error in sync message handling: {e}")
            traceback.print_exc()
            self._send_error(session.session_id, str(e))

    async def cleanup(self):
        """Async cleanup all sessions"""
        for session in self.sessions.values():
            try:
                if hasattr(session, 'stop'):
                    await session.stop()
            except Exception as e:
                logger.error(f"Error stopping session: {e}")

    def cleanup_sync(self):
        """Synchronous cleanup for widget usage"""
        print("Running MessageRouter cleanup_sync")
        for session_id, session in list(self.sessions.items()):
            try:
                # Special handling for TelemetrySession
                if isinstance(session, TelemetrySession):
                    print(f"Cleaning up telemetry session: {session_id}")
                    # Stop the collector if it exists
                    if hasattr(session, 'collector') and session.collector:
                        if hasattr(session.collector, 'isRunning') and session.collector.isRunning():
                            print(f"Stopping collector thread")
                            session.collector._is_running = False
                            session.collector.quit()
                            session.collector.wait(1000)  # Wait with timeout

                    # Mark session as inactive
                    session._active = False

                    # Create and run a temporary event loop to synchronously disconnect
                    try:
                        temp_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(temp_loop)
                        temp_loop.run_until_complete(session.disconnect())
                        temp_loop.close()
                    except Exception as e:
                        print(f"Error in sync disconnect: {e}")

                # For other session types
                elif hasattr(session, 'stop_sync'):
                    session.stop_sync()
                # Fallback to async if needed
                elif hasattr(session, 'stop'):
                    try:
                        temp_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(temp_loop)
                        temp_loop.run_until_complete(session.stop())
                        temp_loop.close()
                    except Exception as e:
                        print(f"Error in fallback async stop: {e}")

            except Exception as e:
                print(f"Error stopping session {session_id}: {e}")
                traceback.print_exc()