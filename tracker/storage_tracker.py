import os
import psutil
from pathlib import Path
import threading
from datetime import datetime

class StorageTracker:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.scan_in_progress = False
        
    def get_disk_usage(self):
        """Get overall disk usage statistics"""
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                }
            except PermissionError:
                continue
        return disk_usage
    
    def scan_folder_sizes(self, path, max_depth=2, current_depth=0):
        """Recursively scan folder sizes"""
        if current_depth > max_depth:
            return {}
            
        folder_sizes = {}
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {}
                
            for item in path_obj.iterdir():
                if item.is_dir():
                    try:
                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        folder_sizes[str(item)] = {
                            "size_bytes": size,
                            "size_mb": size / 1024 / 1024,
                            "size_gb": size / 1024 / 1024 / 1024,
                            "last_scanned": datetime.now().isoformat()
                        }
                        
                        # Recursively scan subdirectories
                        if current_depth < max_depth:
                            subfolder_sizes = self.scan_folder_sizes(item, max_depth, current_depth + 1)
                            folder_sizes.update(subfolder_sizes)
                            
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
            
        return folder_sizes
    
    def get_app_storage_usage(self):
        """Estimate storage usage by applications"""
        app_storage = {}
        
        # Common application directories
        app_dirs = [
            os.path.expanduser("~/AppData/Local"),
            os.path.expanduser("~/AppData/Roaming"),
            "C:/Program Files",
            "C:/Program Files (x86)",
        ]
        
        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                folder_sizes = self.scan_folder_sizes(app_dir, max_depth=1)
                for folder, info in folder_sizes.items():
                    app_name = os.path.basename(folder)
                    if app_name not in app_storage:
                        app_storage[app_name] = 0
                    app_storage[app_name] += info["size_mb"]
                    
        return app_storage
    
    def scan_storage_usage(self):
        """Perform full storage scan"""
        if self.scan_in_progress:
            return
            
        self.scan_in_progress = True
        
        try:
            # Get disk usage
            disk_usage = self.get_disk_usage()
            
            # Get app storage usage
            app_storage = self.get_app_storage_usage()
            
            # Update data manager
            self.data_manager.update_storage_data({
                "disk_usage": disk_usage,
                "app_storage": app_storage,
                "last_scan": datetime.now().isoformat()
            })
            
        finally:
            self.scan_in_progress = False
