import requests
from datetime import datetime
import threading

class LocationTracker:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_location = None
        self.last_update = None
        
    def get_ip_location(self):
        """Get location based on IP address"""
        try:
            # Using ip-api.com (free tier)
            response = requests.get("http://ip-api.com/json/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    return {
                        "ip": data.get("query"),
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "country": data.get("country"),
                        "timezone": data.get("timezone"),
                        "lat": data.get("lat"),
                        "lon": data.get("lon"),
                        "isp": data.get("isp"),
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"Location tracking error: {e}")
            
        return None
    
    def update_location(self):
        """Update current location"""
        location = self.get_ip_location()
        if location:
            self.current_location = location
            self.last_update = datetime.now()
            self.data_manager.update_location_data(location)
            
    def get_current_location(self):
        """Get current cached location"""
        return self.current_location
