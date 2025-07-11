import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

class DataVisualization:
    def __init__(self, parent_frame, data_manager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        
        # Set matplotlib style
        plt.style.use('dark_background')
        
    def create_app_usage_pie_chart(self):
        """Create pie chart of app usage"""
        app_usage = self.data_manager.get_app_usage_summary()
        
        if not app_usage:
            return None
        
        # Prepare data
        apps = list(app_usage.keys())[:10]  # Top 10 apps
        times = [app_usage[app]['total_time'] / 3600 for app in apps]  # Convert to hours
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(apps)))
        wedges, texts, autotexts = ax.pie(times, labels=apps, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        ax.set_title('App Usage Distribution (Today)', fontsize=14, fontweight='bold')
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        return fig
    
    def create_timeline_chart(self):
        """Create timeline chart of daily activity"""
        sessions = self.data_manager.app_sessions
        
        if not sessions:
            return None
        
        # Group sessions by hour
        hourly_usage = {}
        for session in sessions:
            start_time = datetime.fromisoformat(session['start_time'])
            hour = start_time.hour
            
            if hour not in hourly_usage:
                hourly_usage[hour] = 0
            hourly_usage[hour] += session['duration_seconds'] / 3600  # Convert to hours
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        hours = list(range(24))
        usage = [hourly_usage.get(hour, 0) for hour in hours]
        
        # Create bar chart
        bars = ax.bar(hours, usage, color='skyblue', alpha=0.7)
        
        # Highlight current hour
        current_hour = datetime.now().hour
        if current_hour < len(bars):
            bars[current_hour].set_color('orange')
        
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Usage (Hours)')
        ax.set_title('Daily Activity Timeline', fontsize=14, fontweight='bold')
        ax.set_xticks(hours[::2])  # Show every 2 hours
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_resource_usage_chart(self):
        """Create resource usage chart"""
        resource_data = getattr(self.data_manager, 'resource_data', {})
        
        if not resource_data or 'system' not in resource_data:
            return None
        
        system_data = resource_data['system']
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # CPU Usage
        ax1.bar(['CPU'], [system_data.get('cpu_percent', 0)], color='red', alpha=0.7)
        ax1.set_ylabel('Percentage')
        ax1.set_title('CPU Usage')
        ax1.set_ylim(0, 100)
        
        # Memory Usage
        ax2.bar(['Memory'], [system_data.get('memory_percent', 0)], color='blue', alpha=0.7)
        ax2.set_ylabel('Percentage')
        ax2.set_title('Memory Usage')
        ax2.set_ylim(0, 100)
        
        # Disk Usage
        ax3.bar(['Disk'], [system_data.get('disk_percent', 0)], color='green', alpha=0.7)
        ax3.set_ylabel('Percentage')
        ax3.set_title('Disk Usage')
        ax3.set_ylim(0, 100)
        
        # Top Processes (CPU)
        if 'processes' in resource_data:
            processes = resource_data['processes'][:5]  # Top 5
            proc_names = [p['name'][:10] for p in processes]  # Truncate names
            proc_cpu = [p.get('cpu_percent', 0) for p in processes]
            
            ax4.barh(proc_names, proc_cpu, color='orange', alpha=0.7)
            ax4.set_xlabel('CPU %')
            ax4.set_title('Top Processes (CPU)')
        
        plt.tight_layout()
        return fig
    
    def create_storage_usage_chart(self):
        """Create storage usage visualization"""
        storage_data = self.data_manager.storage_data
        
        if not storage_data or 'app_storage' not in storage_data:
            return None
        
        app_storage = storage_data['app_storage']
        
        # Get top 10 apps by storage
        sorted_apps = sorted(app_storage.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if not sorted_apps:
            return None
        
        apps, sizes = zip(*sorted_apps)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create horizontal bar chart
        bars = ax.barh(apps, sizes, color='purple', alpha=0.7)
        
        ax.set_xlabel('Storage (MB)')
        ax.set_title('App Storage Usage', fontsize=14, fontweight='bold')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + max(sizes) * 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{width:.1f} MB', ha='left', va='center')
        
        plt.tight_layout()
        return fig
    
    def embed_chart_in_frame(self, fig, frame):
        """Embed matplotlib figure in tkinter frame"""
        if fig is None:
            return None
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        return canvas
