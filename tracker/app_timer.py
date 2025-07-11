import time
from datetime import datetime, timedelta
from plyer import notification
import threading

class AppTimer:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.app_limits = {}  # app_name: limit_seconds
        self.app_usage_today = {}  # app_name: seconds_used
        self.warnings_sent = set()  # Track which apps have been warned
        self.monitoring = True
        
    def set_app_limit(self, app_name, limit_hours):
        """Set time limit for an application"""
        self.app_limits[app_name] = limit_hours * 3600  # Convert to seconds
        print(f"Set limit for {app_name}: {limit_hours} hours")
    
    def remove_app_limit(self, app_name):
        """Remove time limit for an application"""
        if app_name in self.app_limits:
            del self.app_limits[app_name]
            print(f"Removed limit for {app_name}")
    
    def get_app_usage_today(self, app_name):
        """Get total usage time for app today"""
        app_sessions = self.data_manager.app_sessions
        total_time = 0
        
        today = datetime.now().date()
        for session in app_sessions:
            if session['app_name'] == app_name:
                session_date = datetime.fromisoformat(session['start_time']).date()
                if session_date == today:
                    total_time += session['duration_seconds']
        
        return total_time
    
    def check_app_limits(self):
        """Check if any apps have exceeded their limits"""
        alerts = []
        
        for app_name, limit_seconds in self.app_limits.items():
            usage_seconds = self.get_app_usage_today(app_name)
            
            if usage_seconds >= limit_seconds:
                # Limit exceeded
                alerts.append({
                    "type": "limit_exceeded",
                    "app_name": app_name,
                    "usage_hours": usage_seconds / 3600,
                    "limit_hours": limit_seconds / 3600,
                    "message": f"⚠️ Time limit exceeded for {app_name}!"
                })
                
            elif usage_seconds >= limit_seconds * 0.8:  # 80% warning
                warning_key = f"{app_name}_80"
                if warning_key not in self.warnings_sent:
                    alerts.append({
                        "type": "warning",
                        "app_name": app_name,
                        "usage_hours": usage_seconds / 3600,
                        "limit_hours": limit_seconds / 3600,
                        "message": f"⚠️ 80% time limit reached for {app_name}"
                    })
                    self.warnings_sent.add(warning_key)
                    
            elif usage_seconds >= limit_seconds * 0.5:  # 50% warning
                warning_key = f"{app_name}_50"
                if warning_key not in self.warnings_sent:
                    alerts.append({
                        "type": "info",
                        "app_name": app_name,
                        "usage_hours": usage_seconds / 3600,
                        "limit_hours": limit_seconds / 3600,
                        "message": f"ℹ️ 50% time limit reached for {app_name}"
                    })
                    self.warnings_sent.add(warning_key)
        
        return alerts
    
    def send_notification(self, alert):
        """Send system notification"""
        try:
            notification.notify(
                title="TimeLedger - App Timer",
                message=alert["message"],
                timeout=10
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def monitor_app_timers(self):
        """Monitor app usage and send alerts"""
        while self.monitoring:
            try:
                alerts = self.check_app_limits()
                
                for alert in alerts:
                    self.send_notification(alert)
                    
                    # Log the alert
                    self.data_manager.add_app_alert(alert)
                
                # Reset daily warnings at midnight
                current_time = datetime.now()
                if current_time.hour == 0 and current_time.minute == 0:
                    self.warnings_sent.clear()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"App timer monitoring error: {e}")
                time.sleep(60)
    
    def get_app_limits_status(self):
        """Get current status of all app limits"""
        status = {}
        
        for app_name, limit_seconds in self.app_limits.items():
            usage_seconds = self.get_app_usage_today(app_name)
            
            status[app_name] = {
                "limit_hours": limit_seconds / 3600,
                "usage_hours": usage_seconds / 3600,
                "remaining_hours": max(0, (limit_seconds - usage_seconds) / 3600),
                "percentage_used": min(100, (usage_seconds / limit_seconds) * 100),
                "status": "exceeded" if usage_seconds >= limit_seconds else "active"
            }
        
        return status
    
    def stop_monitoring(self):
        """Stop app timer monitoring"""
        self.monitoring = False
