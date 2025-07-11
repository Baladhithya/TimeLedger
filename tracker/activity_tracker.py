import psutil
import time
from datetime import datetime
import threading

try:
    import win32gui
    import win32process
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

class ActivityTracker:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_app = None
        self.app_start_time = None
        self.idle_threshold = 300  # 5 minutes
        self.last_activity_time = time.time()
        
    def get_active_window_info(self):
        """Get information about the currently active window"""
        if not WINDOWS_AVAILABLE:
            return {"app_name": "Unknown", "window_title": "Unknown"}
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                app_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                app_name = "Unknown"
                
            return {
                "app_name": app_name,
                "window_title": window_title,
                "pid": pid,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"app_name": "Unknown", "window_title": "Unknown", "error": str(e)}
    
    def detect_user_activity(self):
        """Detect if user is active or idle"""
        # This is a simplified version - in a full implementation,
        # you'd use system APIs to detect mouse/keyboard activity
        current_time = time.time()
        
        # For now, assume user is active if window changes
        window_info = self.get_active_window_info()
        if window_info["app_name"] != "Unknown":
            self.last_activity_time = current_time
            
        idle_time = current_time - self.last_activity_time
        return {
            "is_idle": idle_time > self.idle_threshold,
            "idle_time": idle_time,
            "last_activity": datetime.fromtimestamp(self.last_activity_time).isoformat()
        }
    
    def track_current_activity(self):
        """Track current activity and update data"""
        window_info = self.get_active_window_info()
        activity_info = self.detect_user_activity()
        
        current_time = datetime.now()
        app_name = window_info["app_name"]
        
        # If app changed, save previous app's session
        if self.current_app and self.current_app != app_name and self.app_start_time:
            session_duration = (current_time - self.app_start_time).total_seconds()
            self.data_manager.add_app_session(
                self.current_app,
                self.app_start_time,
                current_time,
                session_duration,
                not activity_info["is_idle"]
            )
        
        # Update current app tracking
        if app_name != self.current_app:
            self.current_app = app_name
            self.app_start_time = current_time
            
        # Update real-time data
        self.data_manager.update_current_activity({
            **window_info,
            **activity_info,
            "session_start": self.app_start_time.isoformat() if self.app_start_time else None
        })
        
    def get_running_processes(self):
        """Get list of all running processes with resource usage"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                proc_info = proc.info
                proc_info['memory_mb'] = proc_info['memory_info'].rss / 1024 / 1024
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
