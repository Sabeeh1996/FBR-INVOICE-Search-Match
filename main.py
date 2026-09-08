"""
Main Entry Point
FBR Invoice Checker Bot - Automated invoice verification with GUI
"""

import tkinter as tk
from tkinter import messagebox, ttk
import logging
import os
import sys
import threading
import multiprocessing
from datetime import datetime
from gui import FBRInvoiceCheckerGUI
from license_manager import LicenseManager
from version_manager import read_version, is_version_tampered, get_version_info
from single_instance import SingleInstance
from mac_auth import MACAuthenticator
from first_run_notifier import FirstRunNotifier
from updater import Updater


def setup_logging():
    """
    Setup logging configuration for the application.
    Creates logs directory and configures logging format.
    When running as exe, logs are stored in AppData.
    """
    # Determine logs directory based on execution mode
    if getattr(sys, 'frozen', False):
        # Running as exe - use AppData
        from app_data_manager import get_app_data_dir
        logs_dir = os.path.join(get_app_data_dir(), 'logs')
        print(f"Exe mode: Using AppData for logs: {logs_dir}")
    else:
        # Running as script - use local logs folder
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Created logs directory: {logs_dir}")
    
    # Generate log filename with timestamp
    log_filename = os.path.join(logs_dir, 'fbr_check_log.txt')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=" * 80)
    logging.info("FBR Invoice Checker Bot Started")
    logging.info(f"Log file: {log_filename}")
    logging.info("=" * 80)


def check_version_integrity():
    """
    Check if version.txt was manually edited by user (tampered with).
    
    If tampering is detected, show warning and attempt auto-fix.
    
    Returns:
        bool: True if version is valid, False if tampered (but continuing anyway)
    """
    if is_version_tampered():
        logging.warning("[SECURITY] Version file was tampered with!")
        version_info = get_version_info()
        logging.warning(f"Version info: {version_info}")
        
        # Show warning to user
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Security Notice",
            "⚠️ VERSION FILE WAS MODIFIED\n\n"
            "The version.txt file was manually edited.\n"
            "For security reasons, only the update system should change versions.\n\n"
            "The application will continue with the locked/secure version."
        )
        root.destroy()
        return False
    
    return True


def check_for_app_update_async(root):
    """
    Check GitHub Releases for a newer version in the background so it
    never delays application startup. If one is found, prompt the user.
    """
    def worker():
        try:
            updater = Updater()
            available, release_data = updater.check_for_updates()
            if available:
                latest_version = release_data.get('tag_name', 'unknown')
                root.after(0, lambda: prompt_update(root, updater, latest_version))
        except Exception as e:
            logging.warning(f"Update check failed: {e}")

    threading.Thread(target=worker, daemon=True).start()


def prompt_update(root, updater, latest_version):
    """Ask the user whether to install the newly detected update."""
    current_version = updater.get_current_version()
    answer = messagebox.askyesno(
        "Update Available",
        f"A new version is available.\n\n"
        f"Current version: {current_version}\n"
        f"Latest version: {latest_version}\n\n"
        "Update now? The application will close and reopen automatically."
    )
    if not answer:
        return

    progress_win = tk.Toplevel(root)
    progress_win.title("Updating...")
    progress_win.geometry("350x110")
    progress_win.resizable(False, False)
    progress_win.transient(root)
    progress_win.attributes('-topmost', True)

    tk.Label(progress_win, text=f"Downloading update {latest_version}...").pack(pady=(15, 5))
    progress_bar = ttk.Progressbar(progress_win, length=300, mode='determinate')
    progress_bar.pack(pady=5)

    def progress_cb(downloaded, total):
        if total > 0:
            percent = (downloaded / total) * 100
            progress_win.after(0, lambda: progress_bar.config(value=percent))

    def do_update():
        success, message = updater.check_and_apply_updates(
            progress_callback=progress_cb, force_update=True
        )
        root.after(0, lambda: finish_update(root, progress_win, success, message))

    threading.Thread(target=do_update, daemon=True).start()


def finish_update(root, progress_win, success, message):
    """Handle the outcome of a download/launch-installer attempt."""
    progress_win.destroy()
    if success and "restart" in message.lower():
        messagebox.showinfo(
            "Update Ready",
            "The update has been downloaded. The application will now close and restart."
        )
        root.destroy()
        sys.exit(0)
    else:
        messagebox.showerror("Update Failed", message)


def main():
    """
    Main function to initialize and run the application.
    """
    # Setup logging
    setup_logging()
    
    # Check for single instance - prevent multiple instances from running
    instance_lock = SingleInstance("FBR_Invoice_Checker_App")
    if not instance_lock.acquire_lock():
        logging.warning("Another instance detected")
        
        # Get PID of running instance
        old_pid = instance_lock.get_lock_pid()
        
        if old_pid:
            # Check if old instance has visible window (foreground vs background)
            is_foreground = instance_lock.has_visible_window(old_pid)
            
            if is_foreground:
                # OLD INSTANCE IS FOREGROUND - Don't allow new instance
                logging.info("Old instance has visible window - blocking new instance")
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                root.lift()
                root.focus_force()
                messagebox.showwarning(
                    "Application Already Running",
                    "⚠️ FBR INVOICE CHECKER IS ALREADY OPEN\n\n"
                    "The application is already running with a visible window.\n\n"
                    "Please use the existing window or close it first.\n\n"
                    "💡 Tip: Check your taskbar for the running instance."
                )
                root.destroy()
                logging.info("User notified - exiting second instance")
                sys.exit(0)
            else:
                # OLD INSTANCE IS BACKGROUND/STUCK - Auto-close it
                logging.info(f"Old instance (PID {old_pid}) is background/stuck - auto-closing")
                if instance_lock.kill_process(old_pid):
                    # Wait a moment for process to die
                    import time
                    time.sleep(1)
                    
                    # Try to acquire lock again
                    if instance_lock.acquire_lock():
                        logging.info("✓ Successfully auto-closed background instance and acquired lock")
                        # Continue with normal startup - no dialog needed
                    else:
                        logging.error("Failed to acquire lock after terminating background instance")
                        root = tk.Tk()
                        root.withdraw()
                        root.attributes('-topmost', True)
                        messagebox.showerror(
                            "Startup Error",
                            "❌ Failed to start after closing background instance.\n\n"
                            "Please restart your computer if this persists."
                        )
                        root.destroy()
                        sys.exit(1)
                else:
                    logging.error(f"Failed to terminate background instance (PID: {old_pid})")
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    messagebox.showerror(
                        "Startup Error",
                        "❌ Cannot close the background instance.\n\n"
                        "Please close 'FBR Invoice Checker' from Task Manager."
                    )
                    root.destroy()
                    sys.exit(1)
        else:
            logging.error("Cannot determine old instance PID")
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showerror(
                "Startup Error",
                "❌ Another instance is running but cannot be detected.\n\n"
                "Please close all FBR Invoice Checker windows and try again."
            )
            root.destroy()
            sys.exit(1)
    
    logging.info("✓ Single instance lock acquired - application starting")
    
    # Check MAC address authorization
    mac_auth = MACAuthenticator()
    is_authorized, auth_message = mac_auth.is_authorized()
    
    if not is_authorized:
        logging.error(f"MAC address not authorized: {auth_message}")
        
        # Show error message to user
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()
        
        auth_info = mac_auth.get_auth_info()
        mac_display = auth_info['current_mac'] if auth_info['current_mac'] else "Unable to detect"
        
        messagebox.showerror(
            "Device Not Authorized",
            "⚠️ DEVICE NOT AUTHORIZED\n\n"
            f"{auth_message}\n\n"
            f"Device MAC Address: {mac_display}\n\n"
            "Please contact the administrator to authorize this device."
        )
        root.destroy()
        instance_lock.release_lock()
        sys.exit(1)
    
    logging.info(f"✓ MAC address authorized - {auth_message}")
    
    # Check if this is first run and send notification
    if mac_auth.is_first_run:
        notifier = FirstRunNotifier()
        notifier.notify_first_run(mac_auth.current_mac)
        
        # Device authorization popup disabled - silently authorize
        # root = tk.Tk()
        # root.withdraw()
        # messagebox.showinfo(
        #     "Device Authorized",
        #     "✅ DEVICE SUCCESSFULLY AUTHORIZED\n\n"
        #     f"MAC Address: {mac_auth.current_mac}\n\n"
        #     "This device is now authorized to run the application.\n"
        #     "Authorization has been automatically synced to GitHub.\n\n"
        #     "💡 All other devices will see this authorization\n"
        #     "   on their next startup."
        # )
        # root.destroy()
    
    # Check version integrity (detect tampering)
    check_version_integrity()
    
    # Log version info
    current_version, is_valid = read_version()
    logging.info(f"Current version: {current_version} (Valid: {is_valid})")
    
    # Initialize and validate license
    license_manager = LicenseManager()
    logging.info(license_manager.get_expiry_info_text())
    
    # Check if software is expired
    if not license_manager.validate_license():
        logging.error("SOFTWARE LICENSE EXPIRED - Application cannot start")
        # Show expiry error to user
        root = tk.Tk()
        root.withdraw()  # Hide root window
        license_manager.show_expiry_warning(root)
        root.destroy()
        return
    
    # Create Tkinter root window
    root = tk.Tk()
    
    # Set window icon (optional - can add custom icon later)
    # root.iconbitmap('icon.ico')
    
    # Center window on screen
    window_width = 800
    window_height = 650
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Create and run GUI
    app = FBRInvoiceCheckerGUI(root, license_manager)

    # Check for updates in the background - never blocks startup
    check_for_app_update_async(root)

    # Start the Tkinter event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error in main loop: {str(e)}")
    finally:
        # Release single instance lock
        instance_lock.release_lock()
        logging.info("=" * 80)
        logging.info("FBR Invoice Checker Bot Closed")
        logging.info("=" * 80)


if __name__ == "__main__":
    # CRITICAL: Prevent spawning new processes in PyInstaller .exe
    # Required for undetected-chromedriver to work in frozen executables
    multiprocessing.freeze_support()
    main()
