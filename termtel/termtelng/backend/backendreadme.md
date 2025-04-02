
```markdown
# Multi-Session Architecture

## Session Types & Channels

### SSH Sessions
1. **Primary Terminal (SSH1)**
   ```javascript
   {
       "session_id": "ssh1",
       "type": "terminal",
       "action": "connect|data|disconnect"
   }
   ```
   - Main interactive terminal
   - Full PTY support
   - Command input/output

2. **Telemetry Terminal (SSH2)**
   ```javascript
   {
       "session_id": "ssh2",
       "type": "telemetry",
       "action": "connect|monitor|disconnect"
   }
   ```
   - Dedicated to device monitoring
   - Runs telemetry commands
   - Periodic data collection

3. **UI State Channel**
   ```javascript
   {
       "session_id": "ui_state",
       "type": "system",
       "action": "set_theme|update_layout"
   }
   ```
   - Theme management
   - Layout preferences
   - Panel visibility

## Message Flow Diagram
```plaintext
Frontend                        Backend
   |                              |
   |        WebChannel           |
   |---------------------------→ | MessageRouter
   |         [channel]           |
   |                            |
   |                            |─→ SSH1 Session
   |   Terminal Window          |   - Interactive shell
   |←---------------------------| 
   |      [terminal data]       |
   |                            |
   |                            |─→ SSH2 Session
   |   Telemetry Panels         |   - Device info
   |←---------------------------| 
   |    [monitoring data]       |
   |                            |
   |                            |─→ UI State
   |   Theme/Layout             |   - Theme updates
   |←---------------------------| 
   |     [state changes]        |
```

## Session Management

### Backend Implementation
```python
class MessageRouter(QObject):
    def __init__(self):
        self.sessions = {
            "ssh1": SSHSession("ssh1", session_type="terminal"),
            "ssh2": SSHSession("ssh2", session_type="telemetry"),
            "ui_state": UISession("ui_state")
        }
```

### Frontend Implementation
```javascript
class SessionManager {
    constructor() {
        this.sessions = {
            ssh1: new TerminalSession("ssh1"),
            ssh2: new TelemetrySession("ssh2"),
            ui_state: new UISession("ui_state")
        };
    }
}
```

## Channel Separation

### Terminal Channel (SSH1)
- Full interactive terminal
- Command history
- PTY size management
```python
class SSHSession:
    async def handle_pty_resize(self, cols, rows):
        if self.session_type == "terminal":
            self.channel.resize_pty(width=cols, height=rows)
```

### Telemetry Channel (SSH2)
- Automated commands
- Periodic updates
- Data parsing
```python
class TelemetrySession:
    async def start_monitoring(self):
        while self._active:
            await self.execute_command("show device-info")
            await self.execute_command("show ip route")
            await asyncio.sleep(self.refresh_rate)
```

### UI State Channel
- Theme management
- Panel state
- Layout preferences
```python
class UISession:
    async def handle_panel_visibility(self, panel_id, visible):
        self.panel_states[panel_id] = visible
        self.send_message("panel_updated", {
            "panel": panel_id,
            "visible": visible
        })
```

## Example: Complete Message Flow

1. **Terminal Input**
```javascript
// Frontend sends command
this.sessions.ssh1.sendToBackend("data", {
    text: "show interface"
});

// Backend processes and responds
this.send_message("data", {
    "text": "GigabitEthernet1/0/1 is up..."
});
```

2. **Telemetry Update**
```javascript
// Backend sends update
this.send_message("telemetry_update", {
    "device_info": {...},
    "routing_table": [...],
    "neighbors": [...]
});

// Frontend updates UI
this.sessions.ssh2.updatePanels(data);
```

3. **Theme Change**
```javascript
// Frontend initiates theme change
this.sessions.ui_state.setTheme("crt-amber");

// Backend confirms and broadcasts
this.send_message("theme_changed", {
    "theme": "crt-amber"
});
```

Would you like me to expand on any particular aspect of the multi-session architecture or channel management?