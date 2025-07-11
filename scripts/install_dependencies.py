import subprocess
import sys

def install_packages():
    """Install required packages for TimeLedger"""
    packages = [
        'psutil',
        'customtkinter',
        'matplotlib',
        'requests',
        'plyer',
        'Pillow',
        'pandas',
        'pystray',
        'pywin32'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

if __name__ == "__main__":
    install_packages()
