import ctypes
from ctypes import wintypes, windll
import time
from datetime import datetime
import threading

class WindowsActivityTracker:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.last_input_time = 0
        self.mouse_pos = (0, 0)
        self.key_count = 0
        self.mouse_count = 0
        
        # Windows API structures
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', wintypes.UINT),
                ('dwTime', wintypes.DWORD),
            ]
        
        self.POINT = POINT
        self.LASTINPUTINFO = LASTINPUTINFO
        
    def get_idle_time(self):
        """Get system idle time in seconds using Windows API"""
        try:
            lii = self.LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(self.LASTINPUTINFO)
            windll.user32.GetLastInputInfo(ctypes.byref(lii))
            millis = windll.kernel32.GetTickCount() - lii.dwTime
            return millis / 1000.0
        except Exception as e:
            print(f"Error getting idle time: {e}")
            return 0
    
    def get_cursor_position(self):
        """Get current cursor position"""
        try:
            point = self.POINT()
            windll.user32.GetCursorPos(ctypes.byref(point))
            return (point.x, point.y)
        except Exception:
            return (0, 0)
    
    def detect_user_activity(self):
        """Enhanced user activity detection"""
        current_time = time.time()
        idle_seconds = self.get_idle_time()
        cursor_pos = self.get_cursor_position()
        
        # Detect mouse movement
        mouse_moved = cursor_pos != self.mouse_pos
        if mouse_moved:
            self.mouse_count += 1
            self.mouse_pos = cursor_pos
        
        activity_data = {
            "timestamp": datetime.now().isoformat(),
            "idle_seconds": idle_seconds,
            "is_idle": idle_seconds > 300,  # 5 minutes
            "cursor_position": cursor_pos,
            "mouse_moved": mouse_moved,
            "total_mouse_movements": self.mouse_count,
            "activity_level": "high" if idle_seconds < 30 else "medium" if idle_seconds < 180 else "low"
        }
        
        return activity_data

class KeyboardMouseHook:
    """Low-level keyboard and mouse hook for detailed activity tracking"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.key_presses = 0
        self.mouse_clicks = 0
        self.start_time = time.time()
        
    def get_activity_stats(self):
        """Get keyboard and mouse activity statistics"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        return {
            "session_duration": elapsed_time,
            "key_presses": self.key_presses,
            "mouse_clicks": self.mouse_clicks,
            "keys_per_minute": (self.key_presses / elapsed_time) * 60 if elapsed_time > 0 else 0,
            "clicks_per_minute": (self.mouse_clicks / elapsed_time) * 60 if elapsed_time > 0 else 0,
            "last_updated": datetime.now().isoformat()
        }
