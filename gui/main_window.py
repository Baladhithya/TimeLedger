import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import threading
from datetime import datetime
from gui.visualization import DataVisualization
from gui.timeline_view import TimelineView
from gui.app_timer_manager import AppTimerManager
from utils.report_generator import ReportGenerator
from utils.startup_manager import StartupManager

class MainWindow:
    def __init__(self, root, app, data_manager):
        self.root = root
        self.app = app
        self.data_manager = data_manager
        
        self.setup_window()
        self.create_widgets()
        self.start_updates()
        
        # Bind the window closing protocol to our custom handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("TimeLedger - Desktop Activity Tracker")
        self.root.geometry("1400x900")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def create_widgets(self):
        """Create main window widgets"""
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_charts_tab()
        self.create_timeline_tab()
        self.create_app_timers_tab()
        self.create_storage_tab()
        self.create_location_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
    def _create_segmented_progress_bar(self, parent_frame, app_usage_data, total_time_seconds):
        """Creates a segmented progress bar based on app usage."""
        # Clear existing widgets in the progress bar frame
        for widget in parent_frame.winfo_children():
            widget.destroy()

        if not app_usage_data or total_time_seconds == 0:
            ctk.CTkLabel(parent_frame, text="No app usage data yet.", text_color="gray").pack(fill="x", pady=5)
            return

        # Sort apps by total time descending
        sorted_apps = sorted(app_usage_data.items(), key=lambda item: item[1]['total_time'], reverse=True)

        # Define a set of colors for the segments
        colors = ["#2ECC71", "#3498DB", "#9B59B6", "#F1C40F", "#E67E22", "#E74C3C", "#1ABC9C", "#2C3E50"]
        color_index = 0

        # Create a frame to hold the segments, ensuring it has rounded corners
        progress_bar_container = ctk.CTkFrame(parent_frame, fg_color="gray20", corner_radius=10, height=20)
        progress_bar_container.pack(fill="x", pady=10, padx=10)
        progress_bar_container.pack_propagate(False) # Prevent it from resizing based on children

        # Use a grid layout for segments to ensure they fill the height
        progress_bar_container.grid_rowconfigure(0, weight=1)

        current_width_percentage = 0
        for i, (app_name, data) in enumerate(sorted_apps):
            segment_percentage = (data['total_time'] / total_time_seconds) * 100
            
            # Only show segments that are at least 1% to avoid tiny slivers
            if segment_percentage < 1 and i < len(sorted_apps) - 1:
                continue # Skip small segments unless it's the last one (for "Other")

            # Assign color
            segment_color = colors[color_index % len(colors)]
            color_index += 1

            # Create a frame for each segment
            segment_frame = ctk.CTkFrame(progress_bar_container, fg_color=segment_color, corner_radius=0)
            segment_frame.pack(side="left", fill="y", expand=True, ipadx=0, ipady=0)
            
            # Set width based on percentage. CustomTkinter pack doesn't directly support percentage width,
            # so we'll rely on expand=True and the order of packing.
            # For a more precise visual, we'd need to calculate exact pixel widths or use a canvas.
            # For simplicity and visual effect, we'll use `pack` with `fill="y"` and `side="left"`.
            # The `ipadx` and `ipady` are set to 0 to ensure no internal padding.
            
            # Store app name and color for the legend below
            self.app_colors[app_name] = segment_color
            
            current_width_percentage += segment_percentage
            if current_width_percentage >= 100:
                break # Stop if we've filled the bar

        # Add a small "remainder" segment if total is less than 100%
        if current_width_percentage < 100:
            remainder_frame = ctk.CTkFrame(progress_bar_container, fg_color="gray30", corner_radius=0)
            remainder_frame.pack(side="left", fill="y", expand=True)

        # Create a legend for the apps below the bar
        legend_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        legend_frame.pack(fill="x", pady=(5, 0), padx=10)
        
        # Clear existing legend items
        for widget in legend_frame.winfo_children():
            widget.destroy()

        # Display top 3 apps with their colors and times
        for i, (app_name, data) in enumerate(sorted_apps[:3]):
            color = self.app_colors.get(app_name, "gray") # Get color from stored map
            time_str = f"{int(data['total_time'] // 3600)}h {int((data['total_time'] % 3600) // 60)}m"
            
            app_row_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            app_row_frame.pack(fill="x", pady=2)

            # Fix: Use ctk.ThemeManager.get_color to get a valid background color for CTkCanvas
            # This ensures it's not "transparent" which CTkCanvas doesn't understand.
            canvas_bg_color = "gray20"  # Safe default background
            color_dot = ctk.CTkCanvas(app_row_frame, width=10, height=10, bg=canvas_bg_color, highlightthickness=0)
            color_dot.create_oval(0, 0, 10, 10, fill=color, outline="")
            color_dot.pack(side="left", padx=(0, 5))
            
            ctk.CTkLabel(app_row_frame, text=app_name, font=ctk.CTkFont(size=12)).pack(side="left", anchor="w")
            ctk.CTkLabel(app_row_frame, text=time_str, font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", anchor="e")

    def create_dashboard_tab(self):
        """Create dashboard tab"""
        tab = self.notebook.add("📊 Dashboard")
        
        # Initialize app_colors dictionary
        self.app_colors = {}

        # Current activity frame
        activity_frame = ctk.CTkFrame(tab)
        activity_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(activity_frame, text="Current Activity", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.current_activity_text = ctk.CTkTextbox(activity_frame, height=100)
        self.current_activity_text.pack(fill="x", padx=10, pady=5)
        
        # Total time and progress bar section
        total_time_frame = ctk.CTkFrame(tab)
        total_time_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.total_time_label = ctk.CTkLabel(total_time_frame, text="4 h 40 m", font=ctk.CTkFont(size=24, weight="bold"))
        self.total_time_label.pack(anchor="w", padx=10, pady=(5, 0))

        self.progress_bar_frame = ctk.CTkFrame(total_time_frame, fg_color="transparent")
        self.progress_bar_frame.pack(fill="x", pady=(0, 10)) # This frame will hold the segmented bar and legend

        # Stats frames (moved to row 2)
        stats_frame = ctk.CTkFrame(tab)
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.stats_labels = {}
        stats_data = [
            ("Total Time", "total_time"),
            ("Active Time", "active_time"),
            ("Apps Used", "apps_used"),
            ("Most Used App", "most_used_app")
        ]
        
        for i, (label, key) in enumerate(stats_data):
            frame = ctk.CTkFrame(stats_frame)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12)).pack(pady=2)
            self.stats_labels[key] = ctk.CTkLabel(frame, text="--", font=ctk.CTkFont(size=14, weight="bold"))
            self.stats_labels[key].pack(pady=2)
        
        # Configure grid weights
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Recent activity (moved to row 3)
        recent_frame = ctk.CTkFrame(tab)
        recent_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkLabel(recent_frame, text="Recent Activity", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.recent_activity_text = ctk.CTkTextbox(recent_frame, height=200)
        self.recent_activity_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Configure grid weights
        tab.grid_rowconfigure(3, weight=1) # Changed from 2 to 3
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        
    def create_charts_tab(self):
        """Create charts tab"""
        tab = self.notebook.add("📈 Charts")
        
        # Create visualization component
        self.visualization = DataVisualization(tab, self.data_manager)
        
        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(control_frame, text="App Usage Pie Chart", 
                     command=self.show_app_usage_chart).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Timeline Chart", 
                     command=self.show_timeline_chart).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Resource Usage", 
                     command=self.show_resource_chart).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Storage Usage", 
                     command=self.show_storage_chart).pack(side="left", padx=5)
        
        # Chart frame
        self.chart_frame = ctk.CTkFrame(tab)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_timeline_tab(self):
        """Create timeline tab"""
        tab = self.notebook.add("⏰ Timeline")
        
        # Create timeline view
        self.timeline_view = TimelineView(tab, self.data_manager)
        
    def create_app_timers_tab(self):
        """Create app timers tab"""
        tab = self.notebook.add("⏱️ App Timers")
        
        # Create app timer manager
        self.app_timer_manager = AppTimerManager(tab, self.data_manager, 
                                            self.app.app_timer, self.app.app_blocker)
        
    def create_storage_tab(self):
        """Create storage tab"""
        tab = self.notebook.add("💾 Storage")
        
        # Storage info frame
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(info_frame, text="Storage Analysis", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        ctk.CTkButton(info_frame, text="Scan Storage", command=self.scan_storage).pack(side="left", padx=5)
        ctk.CTkButton(info_frame, text="Refresh", command=self.update_storage_display).pack(side="left", padx=5)
        
        # Storage display
        self.storage_text = ctk.CTkTextbox(tab, height=400)
        self.storage_text.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_location_tab(self):
        """Create location tab"""
        tab = self.notebook.add("🌍 Location")
        
        # Location info frame
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(info_frame, text="Location Tracking", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        ctk.CTkButton(info_frame, text="Update Location", command=self.update_location).pack(side="left", padx=5)
        
        # Location display
        self.location_text = ctk.CTkTextbox(tab, height=400)
        self.location_text.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_reports_tab(self):
        """Create reports tab"""
        tab = self.notebook.add("📊 Reports")
        
        # Report controls
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(control_frame, text="Generate Reports", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_frame, text="Daily Report", command=self.generate_daily_report).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Export JSON", command=self.export_json).pack(side="left", padx=5)
        
        # Report display
        self.report_text = ctk.CTkTextbox(tab, height=400)
        self.report_text.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_settings_tab(self):
        """Create settings tab"""
        tab = self.notebook.add("⚙️ Settings")
        
        # Privacy settings
        privacy_frame = ctk.CTkFrame(tab)
        privacy_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(privacy_frame, text="Privacy Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.privacy_var = ctk.BooleanVar(value=self.app.tracking_enabled)
        ctk.CTkCheckBox(privacy_frame, text="Enable Activity Tracking", 
                       variable=self.privacy_var, command=self.toggle_tracking).pack(anchor="w", padx=10, pady=2)
        
        # Startup settings
        startup_frame = ctk.CTkFrame(tab)
        startup_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(startup_frame, text="Startup Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.startup_manager = StartupManager()
        self.startup_var = ctk.BooleanVar(value=self.startup_manager.is_in_startup())
        ctk.CTkCheckBox(startup_frame, text="Start with Windows", 
                       variable=self.startup_var, command=self.toggle_startup).pack(anchor="w", padx=10, pady=2)
        
        # Data management
        data_frame = ctk.CTkFrame(tab)
        data_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(data_frame, text="Data Management", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        ctk.CTkButton(data_frame, text="Clear All Data", command=self.clear_data).pack(side="left", padx=5)
        ctk.CTkButton(data_frame, text="Open Data Folder", command=self.open_data_folder).pack(side="left", padx=5)
        
    def show_app_usage_chart(self):
        """Show app usage pie chart"""
        self.clear_chart_frame()
        fig = self.visualization.create_app_usage_pie_chart()
        if fig:
            self.visualization.embed_chart_in_frame(fig, self.chart_frame)
        
    def show_timeline_chart(self):
        """Show timeline chart"""
        self.clear_chart_frame()
        fig = self.visualization.create_timeline_chart()
        if fig:
            self.visualization.embed_chart_in_frame(fig, self.chart_frame)
        
    def show_resource_chart(self):
        """Show resource usage chart"""
        self.clear_chart_frame()
        fig = self.visualization.create_resource_usage_chart()
        if fig:
            self.visualization.embed_chart_in_frame(fig, self.chart_frame)
        
    def show_storage_chart(self):
        """Show storage usage chart"""
        self.clear_chart_frame()
        fig = self.visualization.create_storage_usage_chart()
        if fig:
            self.visualization.embed_chart_in_frame(fig, self.chart_frame)
        
    def clear_chart_frame(self):
        """Clear chart frame"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
    
    def scan_storage(self):
        """Start storage scan in background"""
        def scan_thread():
            self.app.storage_tracker.scan_storage_usage()
            self.root.after(0, self.update_storage_display)
        
        threading.Thread(target=scan_thread, daemon=True).start()
        messagebox.showinfo("Storage Scan", "Storage scan started in background...")
    
    def update_storage_display(self):
        """Update storage display"""
        storage_data = self.data_manager.storage_data
        
        if not storage_data:
            self.storage_text.delete("1.0", "end")
            self.storage_text.insert("1.0", "No storage data available. Click 'Scan Storage' to analyze disk usage.")
            return
        
        display_text = "Storage Analysis Results:\n\n"
        
        # Disk usage
        if 'disk_usage' in storage_data:
            display_text += "=== Disk Usage ===\n"
            for device, usage in storage_data['disk_usage'].items():
                display_text += f"{device}: {usage['percent']:.1f}% used ({usage['used']/(1024**3):.1f} GB / {usage['total']/(1024**3):.1f} GB)\n"
            display_text += "\n"
        
        # App storage
        if 'app_storage' in storage_data:
            display_text += "=== Top Applications by Storage ===\n"
            sorted_apps = sorted(storage_data['app_storage'].items(), key=lambda x: x[1], reverse=True)[:20]
            for app, size_mb in sorted_apps:
                if size_mb > 1:  # Only show apps using more than 1MB
                    display_text += f"{app}: {size_mb:.1f} MB\n"
        
        self.storage_text.delete("1.0", "end")
        self.storage_text.insert("1.0", display_text)
    
    def update_location(self):
        """Update location in background"""
        def location_thread():
            self.app.location_tracker.update_location()
            self.root.after(0, self.update_location_display)
        
        threading.Thread(target=location_thread, daemon=True).start()
    
    def update_location_display(self):
        """Update location display"""
        location_data = self.data_manager.location_data
        
        if not location_data:
            self.location_text.delete("1.0", "end")
            self.location_text.insert("1.0", "No location data available. Click 'Update Location' to get current location.")
            return
        
        display_text = "Current Location Information:\n\n"
        display_text += f"IP Address: {location_data.get('ip', 'Unknown')}\n"
        display_text += f"City: {location_data.get('city', 'Unknown')}\n"
        display_text += f"Region: {location_data.get('region', 'Unknown')}\n"
        display_text += f"Country: {location_data.get('country', 'Unknown')}\n"
        display_text += f"Timezone: {location_data.get('timezone', 'Unknown')}\n"
        display_text += f"ISP: {location_data.get('isp', 'Unknown')}\n"
        display_text += f"Last Updated: {location_data.get('timestamp', 'Unknown')}\n"
        
        if location_data.get('lat') and location_data.get('lon'):
            display_text += f"Coordinates: {location_data['lat']}, {location_data['lon']}\n"
        
        self.location_text.delete("1.0", "end")
        self.location_text.insert("1.0", display_text)
    
    def generate_daily_report(self):
        """Generate daily report"""
        try:
            report_generator = ReportGenerator(self.data_manager)
            report_path = report_generator.generate_daily_report()
            
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", f"Daily report generated successfully!\n\nReport saved to: {report_path}\n\nThe report contains:\n- Daily activity summary\n- App usage analysis\n- Productivity insights\n- Resource usage statistics\n- Timeline visualization\n\nOpen the HTML file in your browser to view the full report.")
            
            messagebox.showinfo("Report Generated", f"Daily report saved to:\n{report_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def export_csv(self):
        """Export data to CSV"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.data_manager.export_data_csv(file_path):
                messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
            else:
                messagebox.showerror("Export Failed", "Failed to export data to CSV")
    
    def export_json(self):
        """Export data to JSON"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.data_manager.export_data_json(file_path):
                messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
            else:
                messagebox.showerror("Export Failed", "Failed to export data to JSON")
    
    def toggle_tracking(self):
        """Toggle activity tracking"""
        self.app.toggle_privacy_mode()
        
    def toggle_startup(self):
        """Toggle startup with Windows"""
        if self.startup_var.get():
            success = self.startup_manager.add_to_startup()
        else:
            success = self.startup_manager.remove_from_startup()
        
        if not success:
            # Revert checkbox if operation failed
            self.startup_var.set(not self.startup_var.get())
    
    def clear_data(self):
        """Clear all data"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data? This cannot be undone."):
            try:
                # Clear current session data
                self.data_manager.app_sessions = []
                self.data_manager.storage_data = {}
                self.data_manager.location_data = {}
                
                # Save empty data
                self.data_manager.save_daily_data()
                
                messagebox.showinfo("Success", "All data has been cleared.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
    
    def open_data_folder(self):
        """Open data folder in file explorer"""
        import subprocess
        import os
        
        data_path = self.data_manager.data_dir
        if os.path.exists(data_path):
            subprocess.Popen(f'explorer "{data_path}"')
        else:
            messagebox.showerror("Error", "Data folder not found")
    
    def update_dashboard(self):
        """Update dashboard display"""
        try:
            # Update current activity
            current_activity = self.data_manager.current_activity
            if current_activity:
                activity_text = f"Current App: {current_activity.get('app_name', 'Unknown')}\n"
                activity_text += f"Window: {current_activity.get('window_title', 'Unknown')}\n"
                activity_text += f"Status: {'Active' if not current_activity.get('is_idle', True) else 'Idle'}\n"
                activity_text += f"Last Update: {current_activity.get('timestamp', 'Unknown')}"
            else:
                activity_text = "No current activity data available"
            
            self.current_activity_text.delete("1.0", "end")
            self.current_activity_text.insert("1.0", activity_text)
            
            # Update stats
            app_usage = self.data_manager.get_app_usage_summary()
            
            total_time_seconds = sum(data['total_time'] for data in app_usage.values()) if app_usage else 0
            active_time = sum(data['active_time'] for data in app_usage.values()) if app_usage else 0
            apps_used = len(app_usage) if app_usage else 0
            
            if app_usage:
                most_used_app = max(app_usage.items(), key=lambda x: x[1]['total_time'])[0]
            else:
                most_used_app = "None"
            
            # Update total time label
            total_hours = int(total_time_seconds // 3600)
            total_minutes = int((total_time_seconds % 3600) // 60)
            self.total_time_label.configure(text=f"{total_hours} h {total_minutes} m")

            # Update segmented progress bar
            self._create_segmented_progress_bar(self.progress_bar_frame, app_usage, total_time_seconds)

            self.stats_labels['total_time'].configure(text=f"{total_time_seconds/3600:.1f}h")
            self.stats_labels['active_time'].configure(text=f"{active_time/3600:.1f}h")
            self.stats_labels['apps_used'].configure(text=str(apps_used))
            self.stats_labels['most_used_app'].configure(text=most_used_app[:15] + "..." if len(most_used_app) > 15 else most_used_app)
            
            # Update recent activity
            recent_sessions = self.data_manager.app_sessions[-10:] if self.data_manager.app_sessions else []
            recent_text = "Recent Activity:\n\n"
            
            for session in reversed(recent_sessions):
                start_time = datetime.fromisoformat(session['start_time'])
                duration = session['duration_seconds']
                recent_text += f"{start_time.strftime('%H:%M')} - {session['app_name']} ({duration:.0f}s)\n"
            
            if not recent_sessions:
                recent_text += "No recent activity"
            
            self.recent_activity_text.delete("1.0", "end")
            self.recent_activity_text.insert("1.0", recent_text)
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
    
    def start_updates(self):
        """Start periodic updates"""
        self.update_dashboard()
        self.root.after(5000, self.start_updates)  # Update every 5 seconds

    def on_closing(self):
        """Handles the main window closing event for graceful shutdown."""
        if messagebox.askokcancel("Quit", "Do you want to quit TimeLedger?"):
            # Signal all background threads to stop
            self.app.stop_tracking()
            
            # Stop the system tray icon gracefully
            if self.app.system_tray.icon:
                self.app.system_tray.running = False # Signal the tray thread to stop its loop
                self.app.system_tray.icon.stop() # This will unblock icon.run()
            
            # Give a tiny moment for the tray thread to react and exit its loop
            import time
            time.sleep(0.1) 
            
            # Destroy the main window
            self.root.destroy()
