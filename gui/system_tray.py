import pystray
from PIL import Image, ImageDraw
import threading
from plyer import notification

class SystemTrayManager:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.running = True
        
    def create_icon_image(self):
        """Create a simple icon image"""
        # Create a simple clock icon
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)
        
        # Draw clock face
        draw.ellipse([8, 8, 56, 56], fill='white', outline='black', width=2)
        
        # Draw clock hands
        draw.line([32, 32, 32, 20], fill='black', width=3)  # Hour hand
        draw.line([32, 32, 44, 32], fill='black', width=2)  # Minute hand
        
        # Draw center dot
        draw.ellipse([30, 30, 34, 34], fill='black')
        
        return image
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def on_quit(self, icon, item):
        """Handle quit action from system tray. Triggers main window shutdown."""
        self.running = False # Signal this thread to stop
        if hasattr(self.app, 'main_window') and self.app.main_window.root:
            # Schedule the main window's closing protocol on the main thread
            self.app.main_window.root.after(0, self.app.main_window.on_closing)
        else:
            # Fallback if main window is already closed or not initialized
            self.app.stop_tracking()
            icon.stop() # Stop the tray icon itself
    
    def on_show_hide(self, icon, item):
        """Toggle main window visibility, scheduled on main thread."""
        if hasattr(self.app, 'main_window') and self.app.main_window.root:
            # Schedule the actual GUI operation on the main Tkinter thread
            self.app.main_window.root.after(0, self._toggle_main_window_visibility)
    
    def _toggle_main_window_visibility(self):
        """Actual GUI operation for toggling visibility, called from main thread."""
        try:
            if self.app.main_window.root.winfo_viewable():
                self.app.main_window.root.withdraw()
            else:
                self.app.main_window.root.deiconify()
                self.app.main_window.root.lift()
        except Exception as e:
            print(f"Error toggling main window visibility: {e}")
    
    def on_privacy_mode(self, icon, item):
        """Toggle privacy mode"""
        self.app.toggle_privacy_mode()
        status = "disabled" if self.app.tracking_enabled else "enabled"
        self.show_notification("TimeLedger", f"Privacy mode {status}")
    
    def on_generate_report(self, icon, item):
        """Generate quick report"""
        try:
            from utils.report_generator import ReportGenerator
            report_gen = ReportGenerator(self.app.data_manager)
            report_path = report_gen.generate_daily_report()
            self.show_notification("TimeLedger", f"Report generated: {report_path}")
        except Exception as e:
            self.show_notification("TimeLedger", f"Report error: {str(e)}")
    
    def create_menu(self):
        """Create system tray menu"""
        return pystray.Menu(
            pystray.MenuItem("Show/Hide Window", self.on_show_hide),
            pystray.MenuItem("Privacy Mode", self.on_privacy_mode),
            pystray.MenuItem("Generate Report", self.on_generate_report),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )
    
    def run_tray(self):
        """Run system tray"""
        try:
            image = self.create_icon_image()
            menu = self.create_menu()
            
            self.icon = pystray.Icon(
                "TimeLedger",
                image,
                "TimeLedger - Desktop Activity Tracker",
                menu
            )
            
            self.icon.run() # This call is blocking until icon.stop() is called
        except Exception as e:
            print(f"System tray error: {e}")
    
    def start(self):
        """Start system tray in background thread"""
        tray_thread = threading.Thread(target=self.run_tray, daemon=True)
        tray_thread.start()
