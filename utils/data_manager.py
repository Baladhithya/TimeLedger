import json
import os
from datetime import datetime, date
import pandas as pd
from pathlib import Path

class DataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Current session data
        self.current_activity = {}
        self.app_sessions = []
        self.storage_data = {}
        self.location_data = {}
        
        # Load today's data if exists
        self.load_daily_data()
        
    def get_daily_file_path(self, target_date=None):
        """Get file path for daily data"""
        if target_date is None:
            target_date = date.today()
        return self.data_dir / f"{target_date.isoformat()}.json"
    
    def load_daily_data(self, target_date=None):
        """Load data for a specific day"""
        file_path = self.get_daily_file_path(target_date)
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.app_sessions = data.get("app_sessions", [])
                    self.storage_data = data.get("storage_data", {})
                    self.location_data = data.get("location_data", {})
            except Exception as e:
                print(f"Error loading daily data: {e}")
    
    def save_daily_data(self, target_date=None):
        """Save current data to daily file"""
        file_path = self.get_daily_file_path(target_date)
        data = {
            "date": date.today().isoformat(),
            "app_sessions": self.app_sessions,
            "storage_data": self.storage_data,
            "location_data": self.location_data,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving daily data: {e}")
    
    def add_app_session(self, app_name, start_time, end_time, duration, was_active):
        """Add an app usage session"""
        session = {
            "app_name": app_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "was_active": was_active,
            "date": date.today().isoformat()
        }
        self.app_sessions.append(session)
    
    def update_current_activity(self, activity_data):
        """Update current activity data"""
        self.current_activity = activity_data
    
    def update_storage_data(self, storage_data):
        """Update storage usage data"""
        self.storage_data = storage_data
    
    def update_location_data(self, location_data):
        """Update location data"""
        self.location_data = location_data

    def update_resource_data(self, resource_data):
        """Update resource usage data"""
        self.resource_data = resource_data

    def add_app_alert(self, alert):
        """Add app timer alert to log"""
        if not hasattr(self, 'app_alerts'):
            self.app_alerts = []
        
        alert['timestamp'] = datetime.now().isoformat()
        self.app_alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.app_alerts) > 100:
            self.app_alerts = self.app_alerts[-100:]

    def get_resource_summary(self):
        """Get resource usage summary"""
        if not hasattr(self, 'resource_data') or not self.resource_data:
            return {}
        
        return {
            "system": self.resource_data.get('system', {}),
            "resource_hogs": self.resource_data.get('resource_hogs', {}),
            "last_updated": self.resource_data.get('timestamp', '')
        }
    
    def get_app_usage_summary(self, days=1):
        """Get app usage summary for specified days"""
        app_usage = {}
        
        for session in self.app_sessions:
            app_name = session["app_name"]
            duration = session["duration_seconds"]
            
            if app_name not in app_usage:
                app_usage[app_name] = {
                    "total_time": 0,
                    "active_time": 0,
                    "sessions": 0
                }
            
            app_usage[app_name]["total_time"] += duration
            app_usage[app_name]["sessions"] += 1
            
            if session["was_active"]:
                app_usage[app_name]["active_time"] += duration
        
        return app_usage
    
    def export_data_csv(self, file_path):
        """Export data to CSV"""
        try:
            df = pd.DataFrame(self.app_sessions)
            df.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def export_data_json(self, file_path):
        """Export data to JSON"""
        try:
            data = {
                "app_sessions": self.app_sessions,
                "storage_data": self.storage_data,
                "location_data": self.location_data,
                "exported_at": datetime.now().isoformat()
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
