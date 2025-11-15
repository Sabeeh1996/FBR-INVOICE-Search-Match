# Auto-Update System Documentation

## Overview

This auto-update system allows your FBR Invoice Checker application to automatically check for and install updates from GitHub Releases.

## Features

✅ **Automatic Update Detection** - Checks GitHub for new releases  
✅ **Safe Installation** - Creates backups before updating  
✅ **Rollback Support** - Restores previous version if update fails  
✅ **Progress Tracking** - Shows download progress to users  
✅ **Error Handling** - Gracefully handles network issues, corrupt files  
✅ **No Authentication Required** - Uses public GitHub API  
✅ **PyInstaller Compatible** - Works with both Python scripts and EXE files  

---

## Quick Start

### 1. Basic Integration (Automatic on Startup)

Add this to your `main.py` or startup script:

```python
from updater import check_and_apply_updates

# Check for updates when app starts
success, message = check_and_apply_updates()
print(message)

if "restart" in message.lower():
    input("Update installed! Press Enter to exit and restart...")
    sys.exit(0)
```

### 2. With Progress Bar

```python
from updater import check_and_apply_updates

def show_progress(downloaded, total):
    """Display download progress."""
    if total > 0:
        percent = (downloaded / total) * 100
        print(f"\rDownloading: {percent:.1f}%", end='')

success, message = check_and_apply_updates(progress_callback=show_progress)
print("\n" + message)
```

### 3. Manual "Check for Updates" Button

```python
from updater import Updater

def check_updates_button_clicked():
    """Called when user clicks 'Check for Updates' button."""
    updater = Updater()
    
    # Check if update is available
    available, release_info = updater.check_for_updates()
    
    if available:
        new_version = release_info['tag_name']
        current = updater.get_current_version()
        
        # Show dialog to user
        response = messagebox.askyesno(
            "Update Available",
            f"Version {new_version} is available!\n"
            f"Current: v{current}\n\n"
            f"Download and install?"
        )
        
        if response:
            # Apply update with progress
            success, message = updater.check_and_apply_updates(
                progress_callback=show_download_progress
            )
            
            if success:
                messagebox.showinfo("Success", message)
                if "restart" in message.lower():
                    sys.exit(0)  # Exit to allow restart
            else:
                messagebox.showerror("Update Failed", message)
    else:
        messagebox.showinfo("Up to Date", "You have the latest version!")
```

---

## Module Documentation

### 1. `updater.py` - Main Orchestrator

**Main Function:**
```python
check_and_apply_updates(progress_callback=None) -> (bool, str)
```

**Returns:**
- `success` (bool): True if update applied or no update needed
- `message` (str): Status message for user

**Example:**
```python
from updater import check_and_apply_updates

success, message = check_and_apply_updates()
print(message)
```

---

### 2. `update_checker.py` - Version Checking

**Purpose:** Checks GitHub Releases API for new versions

**Key Methods:**

```python
from update_checker import UpdateChecker

checker = UpdateChecker("Sabeeh1996", "FBR-INVOICE-Search-Match")

# Check for updates
release_data = checker.check_for_updates("1.0")

if release_data:
    print(f"New version: {release_data['tag_name']}")
```

**Compare Versions:**
```python
is_newer = checker.compare_versions("1.0", "v1.2")  # Returns: True
```

---

### 3. `update_downloader.py` - File Downloading

**Purpose:** Downloads update files from GitHub

**Key Methods:**

```python
from update_downloader import UpdateDownloader

downloader = UpdateDownloader()

# Download from release data
file_path = downloader.download_from_release(release_data)

# Or download from direct URL
file_path = downloader.download_file(
    "https://github.com/.../update.zip",
    filename="update.zip",
    progress_callback=my_progress_function
)
```

**Progress Callback Example:**
```python
def show_progress(downloaded_bytes, total_bytes):
    percent = (downloaded_bytes / total_bytes) * 100
    print(f"Progress: {percent:.1f}%")
```

---

### 4. `update_installer.py` - Installation & Backup

**Purpose:** Safely installs updates with backup/rollback

**Key Methods:**

```python
from update_installer import UpdateInstaller

installer = UpdateInstaller()

# Install update (creates backup automatically)
success = installer.install_update("update.zip", "1.2")

if success:
    print("Update installed!")
else:
    print("Installation failed - rolled back")
```

**Manual Operations:**
```python
# Validate ZIP before installing
is_valid = installer.validate_zip("update.zip")

# Create backup manually
installer.create_backup()

# Rollback if needed
installer.rollback()
```

---

## File Structure

```
FBR-INVOICE-STATUS-MATCHING/
├── version.txt                # Current version (e.g., "1.0")
├── updater.py                 # Main orchestrator
├── update_checker.py          # Version checking
├── update_downloader.py       # File downloading
├── update_installer.py        # Installation & backup
├── update.zip                 # Downloaded update (temporary)
└── backup_before_update/      # Backup folder (temporary)
```

---

## GitHub Release Setup

### Creating a Release

1. Go to your repository: https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match

2. Click "Releases" → "Create a new release"

3. **Tag version:** Use format `v1.0`, `v1.1`, `v1.2`, etc.

4. **Release title:** Version 1.2

5. **Attach files:** Upload your ZIP file containing:
   ```
   update.zip contents:
   ├── main.py
   ├── fbr_checker.py
   ├── gui.py
   ├── excel_handler.py
   └── assets/
       └── (all assets)
   ```

6. Click "Publish release"

### Release Checklist

✅ Tag follows `v1.0`, `v1.1` format  
✅ At least one ZIP file attached as asset  
✅ ZIP contains all necessary application files  
✅ ZIP does NOT contain backup folders or logs  
✅ Release is marked as "Latest release"  

---

## Integration Examples

### Example 1: Simple Startup Check

```python
# main.py
import sys
from updater import check_and_apply_updates

def main():
    # Check for updates on startup
    print("Checking for updates...")
    success, message = check_and_apply_updates()
    print(message)
    
    if "restart" in message.lower():
        input("Press Enter to restart...")
        sys.exit(0)
    
    # Continue with normal app startup
    run_application()

if __name__ == "__main__":
    main()
```

### Example 2: GUI Integration (tkinter)

```python
# gui.py
import tkinter as tk
from tkinter import messagebox
from updater import Updater
import threading

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.updater = Updater()
        
        # Add "Check for Updates" menu item
        menu = tk.Menu(self.root)
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(
            label="Check for Updates",
            command=self.check_updates
        )
        menu.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu)
    
    def check_updates(self):
        """Check for updates in background thread."""
        def update_thread():
            available, release = self.updater.check_for_updates()
            
            if available:
                response = messagebox.askyesno(
                    "Update Available",
                    f"Version {release['tag_name']} is available!\n"
                    "Download and install now?"
                )
                
                if response:
                    self.apply_update()
            else:
                messagebox.showinfo(
                    "Up to Date",
                    "You have the latest version!"
                )
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def apply_update(self):
        """Download and install update."""
        success, message = self.updater.check_and_apply_updates()
        
        if success and "restart" in message.lower():
            messagebox.showinfo("Update Complete", message)
            self.root.quit()
        elif not success:
            messagebox.showerror("Update Failed", message)
```

### Example 3: Silent Background Check

```python
# Check for updates silently without user prompt
import threading
from updater import Updater

def background_update_check():
    """Run in background thread."""
    updater = Updater()
    available, release = updater.check_for_updates()
    
    if available:
        # Store flag for later user notification
        with open("update_available.flag", "w") as f:
            f.write(release['tag_name'])

# Start background check
thread = threading.Thread(target=background_update_check, daemon=True)
thread.start()

# Later, check if update was found
import os
if os.path.exists("update_available.flag"):
    # Show notification to user
    pass
```

---

## Troubleshooting

### Issue: "No updates available" but new version exists

**Solution:** Check version.txt format
- Should contain only version number: `1.0`
- No extra spaces or characters
- No 'v' prefix

### Issue: Download fails with timeout

**Solution:** Increase timeout in update_downloader.py:
```python
response = requests.get(url, stream=True, timeout=60)  # Increase to 60s
```

### Issue: ZIP extraction fails

**Solution:** Ensure ZIP file structure is correct:
```
update.zip/
├── main.py          ✓ Correct (files at root)
├── gui.py
└── assets/

NOT:
update.zip/
└── MyApp/           ✗ Wrong (nested folder)
    ├── main.py
    └── gui.py
```

### Issue: Update works but app won't restart

**Solution:** Add explicit restart logic:
```python
import os
import sys

success, message = check_and_apply_updates()
if "restart" in message.lower():
    # Restart application
    os.execv(sys.executable, ['python'] + sys.argv)
```

### Issue: Permission denied during update

**Solution:** Run application with administrator privileges or ensure write access to application directory.

---

## Testing the Update System

### 1. Test Version Comparison

```python
from update_checker import UpdateChecker

checker = UpdateChecker("Sabeeh1996", "FBR-INVOICE-Search-Match")

# Test comparisons
print(checker.compare_versions("1.0", "v1.2"))   # True
print(checker.compare_versions("1.5", "v1.2"))   # False
print(checker.compare_versions("1.2", "v1.2"))   # False
```

### 2. Test with Mock Release

Create a test release on GitHub:
- Tag: `v1.1` (higher than your current version)
- Upload a test ZIP file
- Run updater to test full process

### 3. Test Rollback

```python
from update_installer import UpdateInstaller

installer = UpdateInstaller()

# Create backup
installer.create_backup()

# Simulate failed update
print("Testing rollback...")
installer.rollback()
```

---

## Security Considerations

✅ **No Authentication Tokens** - Uses public API only  
✅ **ZIP Validation** - Checks file integrity before extraction  
✅ **Backup Before Update** - Always creates backup first  
✅ **Rollback on Failure** - Automatically restores on error  
✅ **HTTPS Only** - All downloads use secure connections  

⚠ **Important:** Only install updates from trusted sources (your own GitHub repository)

---

## Advanced Configuration

### Custom Repository

```python
from updater import Updater

# Override repository in updater.py
Updater.REPO_OWNER = "YourUsername"
Updater.REPO_NAME = "YourRepo"

updater = Updater()
```

### Custom Download Directory

```python
from update_downloader import UpdateDownloader

downloader = UpdateDownloader(download_dir="C:/Temp/Updates")
```

### Custom Backup Location

```python
from update_installer import UpdateInstaller

installer = UpdateInstaller(app_dir="C:/MyApp")
```

---

## PyInstaller Integration

The update system works with PyInstaller EXE files:

```python
# In your main.py before PyInstaller build:
import sys
import os

# Get application directory (works for both .py and .exe)
if getattr(sys, 'frozen', False):
    # Running as EXE
    app_dir = os.path.dirname(sys.executable)
else:
    # Running as Python script
    app_dir = os.path.dirname(os.path.abspath(__file__))

# Use app_dir for updater
from updater import Updater
updater = Updater(app_dir=app_dir)
```

---

## Support

For issues or questions:
1. Check the logs in `logs/fbr_check_log.txt`
2. Verify GitHub release structure
3. Test network connectivity
4. Review error messages in console

---

## Changelog

**Version 1.0** - Initial auto-update system
- GitHub integration
- Automatic version checking
- Safe installation with backup
- Rollback support
- Progress tracking

---

Made with ❤️ for FBR Invoice Checker
