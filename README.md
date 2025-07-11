# TimeLedger - Desktop Activity Tracker

TimeLedger is a comprehensive desktop activity tracking application designed to help users monitor their computer usage, manage app time, and gain insights into their productivity. Built with Python and CustomTkinter, it provides a user-friendly graphical interface, runs silently in the background via a system tray icon, and offers various tracking and reporting features.

## 🚀 Features

* **Activity Tracking**: Monitors active applications and window titles, distinguishing between active and idle time.
* **Resource Monitoring**: Tracks CPU, memory, disk, and network usage.
* **App Timers & Blocking**: Set daily time limits for specific apps and automatically block them.
* **Data Visualization**: Charts for app usage, daily activity timeline, and resource consumption.
* **Detailed Timeline View**: Minute-by-minute view of app usage.
* **Storage Analysis**: Estimates disk space used by applications.
* **Location Tracking**: IP-based approximate location data.
* **Daily Reports**: HTML reports with activity, app usage, and productivity stats.
* **Data Export**: Export activity data as CSV or JSON.
* **System Tray Integration**: Runs in the background and accessible via tray icon.
* **Startup Integration**: Option to auto-start with Windows.
* **Privacy Mode**: Toggle tracking on/off.

---

## 📦 Installation

### Requirements

* **Python 3.10+** (for development)
* **Windows 10/11** (recommended)

### Run from Source

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/timeledger-desktop-tracker.git
   cd timeledger-desktop-tracker
   ```

2. **Create virtual environment & install dependencies**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the app**

   ```bash
   python main.py
   ```

---

## 🖥️ Packaging the App (Executable)

The app is packaged using `pyinstaller`:

```bash
pyinstaller --noconfirm --windowed --icon=icon.ico main.py
```

The `.exe` file will be found inside `dist/`.

---

## 📂 Installer Creation (NSIS)

1. Create a folder like:

```
AppInstaller/
├── TimeLedger.exe         # Your EXE from dist/
├── assets/                # Icons, images, etc.
├── installer.nsi          # NSIS script
```

2. Run the installer script via NSIS to generate an `.exe` installer.

---

## 🔄 Auto-start on Windows

TimeLedger has a built-in option to enable auto-start at login via the GUI:

* Navigate to **Settings Tab** → **Enable "Start with Windows"**

---

## 📁 File Structure

```
.
├── gui/
├── tracker/
├── utils/
├── data/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
```

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

* Developed by Baladhithya T
* [GitHub](https://github.com/baladhithya)

---

## 📸 Screenshots

