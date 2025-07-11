import os
import sys
import winreg
from pathlib import Path

class StartupManager:
    def __init__(self):
        self.app_name = "TimeLedger"
        self.registry_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
    def add_to_startup(self):
        """Add TimeLedger to Windows startup"""
        try:
            # Get the path to the current Python executable and script
            python_exe = sys.executable
            script_path = Path(__file__).parent.parent / "main.py"
            
            # Create the command to run
            command = f'"{python_exe}" "{script_path}"'
            
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_SET_VALUE)
            
            # Set the value
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, command)
            
            # Close the key
            winreg.CloseKey(key)
            
            print("✅ TimeLedger added to startup")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add to startup: {e}")
            return False
    
    def remove_from_startup(self):
        """Remove TimeLedger from Windows startup"""
        try:
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_SET_VALUE)
            
            # Delete the value
            winreg.DeleteValue(key, self.app_name)
            
            # Close the key
            winreg.CloseKey(key)
            
            print("✅ TimeLedger removed from startup")
            return True
            
        except FileNotFoundError:
            print("ℹ️ TimeLedger was not in startup")
            return True
        except Exception as e:
            print(f"❌ Failed to remove from startup: {e}")
            return False
    
    def is_in_startup(self):
        """Check if TimeLedger is in startup"""
        try:
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_READ)
            
            # Try to read the value
            value, _ = winreg.QueryValueEx(key, self.app_name)
            
            # Close the key
            winreg.CloseKey(key)
            
            return True
            
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking startup status: {e}")
            return False
    
    def toggle_startup(self):
        """Toggle startup status"""
        if self.is_in_startup():
            return self.remove_from_startup()
        else:
            return self.add_to_startup()
