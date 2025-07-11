import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AppTimerManager:
    def __init__(self, parent_frame, data_manager, app_timer, app_blocker):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.app_timer = app_timer
        self.app_blocker = app_blocker
        
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        """Create app timer management widgets"""
        # Main container
        main_frame = ttk.Frame(self.parent_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add new timer section
        add_frame = ttk.LabelFrame(main_frame, text="Add App Timer", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # App name entry
        ttk.Label(add_frame, text="App Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.app_name_var = tk.StringVar()
        app_entry = ttk.Entry(add_frame, textvariable=self.app_name_var, width=30)
        app_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Time limit entry
        ttk.Label(add_frame, text="Time Limit (hours):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.time_limit_var = tk.StringVar()
        time_entry = ttk.Entry(add_frame, textvariable=self.time_limit_var, width=10)
        time_entry.grid(row=0, column=3, padx=5, pady=2)
        
        # Add button
        ttk.Button(add_frame, text="Add Timer", command=self.add_timer).grid(row=0, column=4, padx=10)
        
        # Help text
        help_text = "Enter app name (e.g., 'chrome.exe', 'notepad.exe') and time limit in hours"
        ttk.Label(add_frame, text=help_text, font=('Arial', 8), foreground='gray').grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=5)
        
        # Current timers section
        timers_frame = ttk.LabelFrame(main_frame, text="Active App Timers", padding=10)
        timers_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for displaying timers
        columns = ("App", "Limit", "Used", "Remaining", "Status", "Progress")
        self.timer_tree = ttk.Treeview(timers_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.timer_tree.heading("App", text="Application")
        self.timer_tree.heading("Limit", text="Limit (h)")
        self.timer_tree.heading("Used", text="Used (h)")
        self.timer_tree.heading("Remaining", text="Remaining (h)")
        self.timer_tree.heading("Status", text="Status")
        self.timer_tree.heading("Progress", text="Progress %")
        
        self.timer_tree.column("App", width=150)
        self.timer_tree.column("Limit", width=80)
        self.timer_tree.column("Used", width=80)
        self.timer_tree.column("Remaining", width=100)
        self.timer_tree.column("Status", width=100)
        self.timer_tree.column("Progress", width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(timers_frame, orient=tk.VERTICAL, command=self.timer_tree.yview)
        self.timer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.timer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_timer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Unblock App", command=self.unblock_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.update_display).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Blocked Apps", padding=10)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.blocked_apps_var = tk.StringVar()
        self.blocked_apps_label = ttk.Label(status_frame, textvariable=self.blocked_apps_var, 
                                           font=('Arial', 9), foreground='red')
        self.blocked_apps_label.pack(anchor=tk.W)
    
    def add_timer(self):
        """Add new app timer"""
        app_name = self.app_name_var.get().strip()
        time_limit_str = self.time_limit_var.get().strip()
        
        if not app_name or not time_limit_str:
            messagebox.showerror("Error", "Please enter both app name and time limit")
            return
        
        try:
            time_limit = float(time_limit_str)
            if time_limit <= 0:
                raise ValueError("Time limit must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid time limit (positive number)")
            return
        
        # Add timer
        self.app_timer.set_app_limit(app_name, time_limit)
        
        # Clear entries
        self.app_name_var.set("")
        self.time_limit_var.set("")
        
        # Update display
        self.update_display()
        
        messagebox.showinfo("Success", f"Timer added for {app_name}: {time_limit} hours")
    
    def remove_timer(self):
        """Remove selected timer"""
        selection = self.timer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a timer to remove")
            return
        
        item = self.timer_tree.item(selection[0])
        app_name = item['values'][0]
        
        # Confirm removal
        if messagebox.askyesno("Confirm", f"Remove timer for {app_name}?"):
            self.app_timer.remove_app_limit(app_name)
            self.app_blocker.unblock_app(app_name)
            self.update_display()
            messagebox.showinfo("Success", f"Timer removed for {app_name}")
    
    def unblock_app(self):
        """Unblock selected app"""
        selection = self.timer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an app to unblock")
            return
        
        item = self.timer_tree.item(selection[0])
        app_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Unblock {app_name}? (Timer will remain active)"):
            self.app_blocker.unblock_app(app_name)
            self.update_display()
            messagebox.showinfo("Success", f"{app_name} has been unblocked")
    
    def update_display(self):
        """Update the timer display"""
        # Clear existing items
        for item in self.timer_tree.get_children():
            self.timer_tree.delete(item)
        
        # Get timer status
        timer_status = self.app_timer.get_app_limits_status()
        
        # Populate treeview
        for app_name, status in timer_status.items():
            # Determine status color and text
            if status['status'] == 'exceeded':
                status_text = "BLOCKED"
                # Check if app should be blocked
                if not self.app_blocker.is_app_blocked(app_name):
                    self.app_blocker.block_app(app_name)
            else:
                status_text = "ACTIVE"
            
            # Insert row
            item_id = self.timer_tree.insert("", tk.END, values=(
                app_name,
                f"{status['limit_hours']:.1f}",
                f"{status['usage_hours']:.1f}",
                f"{status['remaining_hours']:.1f}",
                status_text,
                f"{status['percentage_used']:.1f}%"
            ))
            
            # Color code based on status
            if status['status'] == 'exceeded':
                self.timer_tree.set(item_id, "Status", "🚫 BLOCKED")
            elif status['percentage_used'] > 80:
                self.timer_tree.set(item_id, "Status", "⚠️ WARNING")
            else:
                self.timer_tree.set(item_id, "Status", "✅ ACTIVE")
        
        # Update blocked apps display
        blocked_apps = self.app_blocker.get_blocked_apps_list()
        if blocked_apps:
            blocked_text = f"Currently blocked: {', '.join(blocked_apps)}"
        else:
            blocked_text = "No apps currently blocked"
        self.blocked_apps_var.set(blocked_text)
        
        # Schedule next update
        self.parent_frame.after(5000, self.update_display)  # Update every 5 seconds
