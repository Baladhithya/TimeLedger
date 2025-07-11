import psutil
import subprocess
import time
from datetime import datetime
from plyer import notification

class AppBlocker:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.blocked_apps = set()
        self.blocking_active = True
        
    def block_app(self, app_name):
        """Add app to blocked list"""
        self.blocked_apps.add(app_name.lower())
        print(f"Blocked app: {app_name}")
        
        # Send notification
        try:
            notification.notify(
                title="TimeLedger - App Blocked",
                message=f"{app_name} has been blocked due to time limit",
                timeout=10
            )
        except:
            pass
    
    def unblock_app(self, app_name):
        """Remove app from blocked list"""
        self.blocked_apps.discard(app_name.lower())
        print(f"Unblocked app: {app_name}")
    
    def is_app_blocked(self, app_name):
        """Check if app is currently blocked"""
        return app_name.lower() in self.blocked_apps
    
    def kill_process_by_name(self, process_name):
        """Kill all processes with given name"""
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    killed_count += 1
                    print(f"Terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return killed_count
    
    def enforce_app_blocks(self):
        """Continuously monitor and kill blocked apps"""
        while self.blocking_active:
            try:
                for blocked_app in self.blocked_apps.copy():
                    killed = self.kill_process_by_name(blocked_app)
                    if killed > 0:
                        print(f"Enforced block on {blocked_app}: killed {killed} processes")
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"App blocking error: {e}")
                time.sleep(5)
    
    def start_blocking_monitor(self):
        """Start background thread to monitor blocked apps"""
        import threading
        monitor_thread = threading.Thread(target=self.enforce_app_blocks, daemon=True)
        monitor_thread.start()
    
    def stop_blocking(self):
        """Stop app blocking"""
        self.blocking_active = False
        self.blocked_apps.clear()
    
    def get_blocked_apps_list(self):
        """Get list of currently blocked apps"""
        return list(self.blocked_apps)
