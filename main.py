import customtkinter as ctk
import threading
import json
import os
from datetime import datetime, timedelta
from tracker.activity_tracker import ActivityTracker
from tracker.storage_tracker import StorageTracker
from tracker.location_tracker import LocationTracker
from gui.main_window import MainWindow
from utils.data_manager import DataManager
from tracker.windows_activity_tracker import WindowsActivityTracker
from tracker.resource_monitor import ResourceMonitor
from tracker.app_timer import AppTimer
from tracker.app_blocker import AppBlocker
from gui.system_tray import SystemTrayManager

class TimeLedgerApp:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Initialize trackers
        self.activity_tracker = ActivityTracker(self.data_manager)
        self.storage_tracker = StorageTracker(self.data_manager)
        self.location_tracker = LocationTracker(self.data_manager)
        
        # Initialize enhanced trackers
        self.windows_tracker = WindowsActivityTracker(self.data_manager)
        self.resource_monitor = ResourceMonitor(self.data_manager)
        self.app_timer = AppTimer(self.data_manager)
        self.app_blocker = AppBlocker(self.data_manager)
        
        # Tracking state - MOVED HERE
        self.tracking_enabled = True
        self.tracking_thread = None
        
        # Initialize GUI
        self.root = ctk.CTk()
        self.main_window = MainWindow(self.root, self, self.data_manager)
        
        # Initialize system tray
        self.system_tray = SystemTrayManager(self)
        
    def start_tracking(self):
        """Start background tracking"""
        if not self.tracking_enabled:
            return
            
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        # Start resource monitoring
        self.resource_thread = threading.Thread(target=self.resource_monitor.monitor_resources, daemon=True)
        self.resource_thread.start()
        
        # Start app timer monitoring
        self.timer_thread = threading.Thread(target=self.app_timer.monitor_app_timers, daemon=True)
        self.timer_thread.start()
        
        # Start app blocking enforcement
        self.app_blocker.start_blocking_monitor()
        
    def stop_tracking(self):
        """Stop background tracking"""
        self.tracking_enabled = False
        self.resource_monitor.stop_monitoring()
        self.app_timer.stop_monitoring()
        self.app_blocker.stop_blocking()
            
    def toggle_privacy_mode(self):
        """Toggle privacy mode on/off"""
        self.tracking_enabled = not self.tracking_enabled
        if self.tracking_enabled:
            self.start_tracking()
        else:
            self.stop_tracking()
            
    def _tracking_loop(self):
        """Main tracking loop running in background"""
        while self.tracking_enabled:
            try:
                # Track active window and app usage (every 2 seconds)
                self.activity_tracker.track_current_activity()
                
                # Update location (every 30 minutes)
                if datetime.now().minute % 30 == 0:
                    self.location_tracker.update_location()
                
                # Update storage usage (every hour)
                if datetime.now().minute == 0:
                    self.storage_tracker.scan_storage_usage()
                    
                # Save data periodically
                self.data_manager.save_daily_data()
                
                threading.Event().wait(2)  # Wait 2 seconds
                
            except Exception as e:
                print(f"Tracking error: {e}")
                threading.Event().wait(5)  # Wait longer on error
                
    def run(self):
        """Start the application"""
        # Start system tray
        self.system_tray.start()
        
        # Start background tracking
        self.start_tracking()
        
        # Start GUI
        self.root.mainloop()

if __name__ == "__main__":
    app = TimeLedgerApp()
    app.run()
import customtkinter as ctk
import threading
import json
import os
from datetime import datetime, timedelta
from tracker.activity_tracker import ActivityTracker
from tracker.storage_tracker import StorageTracker
from tracker.location_tracker import LocationTracker
from gui.main_window import MainWindow
from utils.data_manager import DataManager
from tracker.windows_activity_tracker import WindowsActivityTracker
from tracker.resource_monitor import ResourceMonitor
from tracker.app_timer import AppTimer
from tracker.app_blocker import AppBlocker
from gui.system_tray import SystemTrayManager

class TimeLedgerApp:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Initialize trackers
        self.activity_tracker = ActivityTracker(self.data_manager)
        self.storage_tracker = StorageTracker(self.data_manager)
        self.location_tracker = LocationTracker(self.data_manager)
        
        # Initialize enhanced trackers
        self.windows_tracker = WindowsActivityTracker(self.data_manager)
        self.resource_monitor = ResourceMonitor(self.data_manager)
        self.app_timer = AppTimer(self.data_manager)
        self.app_blocker = AppBlocker(self.data_manager)
        
        # Tracking state - MOVED HERE
        self.tracking_enabled = True
        self.tracking_thread = None
        
        # Initialize GUI
        self.root = ctk.CTk()
        self.main_window = MainWindow(self.root, self, self.data_manager)
        
        # Initialize system tray
        self.system_tray = SystemTrayManager(self)
        
    def start_tracking(self):
        """Start background tracking"""
        if not self.tracking_enabled:
            return
            
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        # Start resource monitoring
        self.resource_thread = threading.Thread(target=self.resource_monitor.monitor_resources, daemon=True)
        self.resource_thread.start()
        
        # Start app timer monitoring
        self.timer_thread = threading.Thread(target=self.app_timer.monitor_app_timers, daemon=True)
        self.timer_thread.start()
        
        # Start app blocking enforcement
        self.app_blocker.start_blocking_monitor()
        
    def stop_tracking(self):
        """Stop background tracking"""
        self.tracking_enabled = False
        self.resource_monitor.stop_monitoring()
        self.app_timer.stop_monitoring()
        self.app_blocker.stop_blocking()
            
    def toggle_privacy_mode(self):
        """Toggle privacy mode on/off"""
        self.tracking_enabled = not self.tracking_enabled
        if self.tracking_enabled:
            self.start_tracking()
        else:
            self.stop_tracking()
            
    def _tracking_loop(self):
        """Main tracking loop running in background"""
        while self.tracking_enabled:
            try:
                # Track active window and app usage (every 2 seconds)
                self.activity_tracker.track_current_activity()
                
                # Update location (every 30 minutes)
                if datetime.now().minute % 30 == 0:
                    self.location_tracker.update_location()
                
                # Update storage usage (every hour)
                if datetime.now().minute == 0:
                    self.storage_tracker.scan_storage_usage()
                    
                # Save data periodically
                self.data_manager.save_daily_data()
                
                threading.Event().wait(2)  # Wait 2 seconds
                
            except Exception as e:
                print(f"Tracking error: {e}")
                threading.Event().wait(5)  # Wait longer on error
                
    def run(self):
        """Start the application"""
        # Start system tray
        self.system_tray.start()
        
        # Start background tracking
        self.start_tracking()
        
        # Start GUI
        self.root.mainloop()

if __name__ == "__main__":
    app = TimeLedgerApp()
    app.run()
