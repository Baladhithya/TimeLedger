import psutil
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque

class ResourceMonitor:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.process_history = defaultdict(lambda: deque(maxlen=60))  # Keep 60 samples (5 minutes at 5s intervals)
        self.network_baseline = self.get_network_stats()
        self.monitoring = True
        
    def get_system_resources(self):
        """Get overall system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_total_gb": memory.total / (1024**3),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / (1024**3),
                "disk_total_gb": disk.total / (1024**3)
            }
        except Exception as e:
            print(f"Error getting system resources: {e}")
            return {}
    
    def get_network_stats(self):
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "timestamp": time.time()
            }
        except Exception as e:
            print(f"Error getting network stats: {e}")
            return {}
    
    def get_process_resources(self):
        """Get detailed resource usage per process"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'io_counters', 'create_time']):
            try:
                proc_info = proc.info
                
                # Calculate memory usage in MB
                if proc_info['memory_info']:
                    proc_info['memory_mb'] = proc_info['memory_info'].rss / (1024 * 1024)
                else:
                    proc_info['memory_mb'] = 0
                
                # Get I/O stats if available
                if proc_info['io_counters']:
                    proc_info['disk_read_mb'] = proc_info['io_counters'].read_bytes / (1024 * 1024)
                    proc_info['disk_write_mb'] = proc_info['io_counters'].write_bytes / (1024 * 1024)
                else:
                    proc_info['disk_read_mb'] = 0
                    proc_info['disk_write_mb'] = 0
                
                # Calculate uptime
                if proc_info['create_time']:
                    uptime = time.time() - proc_info['create_time']
                    proc_info['uptime_hours'] = uptime / 3600
                else:
                    proc_info['uptime_hours'] = 0
                
                processes.append(proc_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    
    def identify_resource_hogs(self, processes):
        """Identify processes using excessive resources"""
        resource_hogs = {
            "cpu_hogs": [],
            "memory_hogs": [],
            "disk_hogs": []
        }
        
        # Sort by different resource metrics
        cpu_sorted = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)
        memory_sorted = sorted(processes, key=lambda x: x.get('memory_mb', 0), reverse=True)
        disk_sorted = sorted(processes, key=lambda x: x.get('disk_read_mb', 0) + x.get('disk_write_mb', 0), reverse=True)
        
        # Identify top resource consumers
        for proc in cpu_sorted[:5]:
            if proc.get('cpu_percent', 0) > 10:  # More than 10% CPU
                resource_hogs["cpu_hogs"].append({
                    "name": proc['name'],
                    "pid": proc['pid'],
                    "cpu_percent": proc['cpu_percent'],
                    "severity": "high" if proc['cpu_percent'] > 50 else "medium"
                })
        
        for proc in memory_sorted[:5]:
            if proc.get('memory_mb', 0) > 100:  # More than 100MB RAM
                resource_hogs["memory_hogs"].append({
                    "name": proc['name'],
                    "pid": proc['pid'],
                    "memory_mb": proc['memory_mb'],
                    "severity": "high" if proc['memory_mb'] > 1000 else "medium"
                })
        
        for proc in disk_sorted[:5]:
            total_disk = proc.get('disk_read_mb', 0) + proc.get('disk_write_mb', 0)
            if total_disk > 10:  # More than 10MB disk I/O
                resource_hogs["disk_hogs"].append({
                    "name": proc['name'],
                    "pid": proc['pid'],
                    "disk_io_mb": total_disk,
                    "severity": "high" if total_disk > 100 else "medium"
                })
        
        return resource_hogs
    
    def monitor_resources(self):
        """Continuous resource monitoring"""
        while self.monitoring:
            try:
                # Get system resources
                system_resources = self.get_system_resources()
                
                # Get process resources
                processes = self.get_process_resources()
                
                # Identify resource hogs
                resource_hogs = self.identify_resource_hogs(processes)
                
                # Get network stats
                network_stats = self.get_network_stats()
                
                # Update data manager
                resource_data = {
                    "system": system_resources,
                    "processes": processes[:20],  # Top 20 processes
                    "resource_hogs": resource_hogs,
                    "network": network_stats,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.data_manager.update_resource_data(resource_data)
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                print(f"Resource monitoring error: {e}")
                time.sleep(10)  # Wait longer on error
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
