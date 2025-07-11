import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

class TimelineView:
    def __init__(self, parent_frame, data_manager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.current_view = "hourly"  # hourly, detailed, apps
        
        self.create_widgets()
        self.update_timeline()
    
    def create_widgets(self):
        """Create timeline view widgets"""
        # Control frame
        control_frame = ttk.Frame(self.parent_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # View selection
        ttk.Label(control_frame, text="View:").pack(side=tk.LEFT, padx=5)
        
        self.view_var = tk.StringVar(value=self.current_view)
        view_combo = ttk.Combobox(control_frame, textvariable=self.view_var, 
                                 values=["hourly", "detailed", "apps"], state="readonly")
        view_combo.pack(side=tk.LEFT, padx=5)
        view_combo.bind("<<ComboboxSelected>>", self.on_view_changed)
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh", command=self.update_timeline).pack(side=tk.LEFT, padx=10)
        
        # Timeline frame
        self.timeline_frame = ttk.Frame(self.parent_frame)
        self.timeline_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def on_view_changed(self, event=None):
        """Handle view selection change"""
        self.current_view = self.view_var.get()
        self.update_timeline()
    
    def create_hourly_timeline(self):
        """Create hourly activity timeline"""
        sessions = self.data_manager.app_sessions
        
        if not sessions:
            return self.create_empty_chart("No activity data available")
        
        # Group sessions by hour
        hourly_data = {}
        for hour in range(24):
            hourly_data[hour] = {"total": 0, "active": 0, "apps": set()}
        
        for session in sessions:
            start_time = datetime.fromisoformat(session['start_time'])
            if start_time.date() == datetime.now().date():  # Today only
                hour = start_time.hour
                duration = session['duration_seconds'] / 3600  # Convert to hours
                
                hourly_data[hour]["total"] += duration
                if session['was_active']:
                    hourly_data[hour]["active"] += duration
                hourly_data[hour]["apps"].add(session['app_name'])
        
        # Create chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        hours = list(range(24))
        total_times = [hourly_data[h]["total"] for h in hours]
        active_times = [hourly_data[h]["active"] for h in hours]
        
        # Total activity chart
        ax1.bar(hours, total_times, alpha=0.7, color='skyblue', label='Total Time')
        ax1.bar(hours, active_times, alpha=0.9, color='orange', label='Active Time')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Time (Hours)')
        ax1.set_title('Hourly Activity Timeline - Today')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(0, 24, 2))
        
        # App count chart
        app_counts = [len(hourly_data[h]["apps"]) for h in hours]
        ax2.plot(hours, app_counts, marker='o', color='green', linewidth=2)
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Number of Apps Used')
        ax2.set_title('Apps Used Per Hour')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(0, 24, 2))
        
        plt.tight_layout()
        return fig
    
    def create_detailed_timeline(self):
        """Create detailed minute-by-minute timeline"""
        sessions = self.data_manager.app_sessions
        
        if not sessions:
            return self.create_empty_chart("No activity data available")
        
        # Filter today's sessions
        today_sessions = []
        today = datetime.now().date()
        
        for session in sessions:
            start_time = datetime.fromisoformat(session['start_time'])
            if start_time.date() == today:
                today_sessions.append(session)
        
        if not today_sessions:
            return self.create_empty_chart("No activity data for today")
        
        # Create timeline chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Color map for different apps
        apps = list(set(s['app_name'] for s in today_sessions))
        colors = plt.cm.Set3(np.linspace(0, 1, len(apps)))
        app_colors = dict(zip(apps, colors))
        
        y_pos = 0
        for session in sorted(today_sessions, key=lambda x: x['start_time']):
            start_time = datetime.fromisoformat(session['start_time'])
            end_time = datetime.fromisoformat(session['end_time'])
            
            # Convert to hours from start of day
            start_hour = start_time.hour + start_time.minute/60 + start_time.second/3600
            end_hour = end_time.hour + end_time.minute/60 + end_time.second/3600
            
            color = app_colors[session['app_name']]
            alpha = 0.8 if session['was_active'] else 0.4
            
            ax.barh(y_pos, end_hour - start_hour, left=start_hour, 
                   color=color, alpha=alpha, height=0.8,
                   label=session['app_name'] if session['app_name'] not in ax.get_legend_handles_labels()[1] else "")
            
            y_pos += 1
        
        ax.set_xlabel('Time of Day (Hours)')
        ax.set_ylabel('Activity Sessions')
        ax.set_title('Detailed Activity Timeline - Today')
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 2))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 25, 2)])
        
        # Add legend (limit to 10 apps)
        handles, labels = ax.get_legend_handles_labels()
        if len(handles) > 10:
            handles, labels = handles[:10], labels[:10]
        ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        return fig
    
    def create_apps_timeline(self):
        """Create app-focused timeline"""
        sessions = self.data_manager.app_sessions
        
        if not sessions:
            return self.create_empty_chart("No activity data available")
        
        # Get app usage data
        app_usage = {}
        today = datetime.now().date()
        
        for session in sessions:
            start_time = datetime.fromisoformat(session['start_time'])
            if start_time.date() == today:
                app_name = session['app_name']
                if app_name not in app_usage:
                    app_usage[app_name] = {"total": 0, "active": 0, "sessions": []}
                
                app_usage[app_name]["total"] += session['duration_seconds']
                if session['was_active']:
                    app_usage[app_name]["active"] += session['duration_seconds']
                app_usage[app_name]["sessions"].append(session)
        
        if not app_usage:
            return self.create_empty_chart("No activity data for today")
        
        # Sort apps by usage time
        sorted_apps = sorted(app_usage.items(), key=lambda x: x[1]["total"], reverse=True)[:10]
        
        # Create chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
        
        # App usage pie chart
        app_names = [app[0] for app in sorted_apps]
        app_times = [app[1]["total"] / 3600 for app in sorted_apps]  # Convert to hours
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(app_names)))
        wedges, texts, autotexts = ax1.pie(app_times, labels=app_names, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        ax1.set_title('App Usage Distribution - Today')
        
        # App activity bar chart
        active_times = [app[1]["active"] / 3600 for app in sorted_apps]
        total_times = [app[1]["total"] / 3600 for app in sorted_apps]
        
        x_pos = np.arange(len(app_names))
        ax2.bar(x_pos, total_times, alpha=0.7, color='lightblue', label='Total Time')
        ax2.bar(x_pos, active_times, alpha=0.9, color='orange', label='Active Time')
        
        ax2.set_xlabel('Applications')
        ax2.set_ylabel('Time (Hours)')
        ax2.set_title('App Usage Comparison')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in app_names], 
                           rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_empty_chart(self, message):
        """Create empty chart with message"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=16, 
                transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return fig
    
    def update_timeline(self):
        """Update timeline based on current view"""
        # Clear existing widgets
        for widget in self.timeline_frame.winfo_children():
            widget.destroy()
        
        # Create appropriate timeline
        if self.current_view == "hourly":
            fig = self.create_hourly_timeline()
        elif self.current_view == "detailed":
            fig = self.create_detailed_timeline()
        elif self.current_view == "apps":
            fig = self.create_apps_timeline()
        else:
            fig = self.create_empty_chart("Invalid view selected")
        
        # Embed chart
        if fig:
            canvas = FigureCanvasTkAgg(fig, self.timeline_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            plt.close(fig)  # Free memory
