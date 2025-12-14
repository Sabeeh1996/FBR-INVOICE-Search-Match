"""
Main Entry Point
FBR Invoice Checker Bot - Automated invoice verification with GUI
"""

import tkinter as tk
from tkinter import messagebox
import logging
import os
import sys
from datetime import datetime
from gui import FBRInvoiceCheckerGUI
from license_manager import LicenseManager
from version_manager import read_version, is_version_tampered, get_version_info
from single_instance import SingleInstance
from mac_auth import MACAuthenticator
from first_run_notifier import FirstRunNotifier


def setup_logging():
    """
    Setup logging configuration for the application.
    Creates logs directory and configures logging format.
    """
    # Create logs directory if it doesn't exist
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


def main():
    """
    Main function to initialize and run the application.
    """
    # Setup logging
    setup_logging()
    
    # Check for single instance - prevent multiple instances from running
    instance_lock = SingleInstance("FBR_Invoice_Checker_App")
    if not instance_lock.acquire_lock():
        logging.error("Another instance of the application is already running")
        
        # Show error message to user
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Already Running",
            "⚠️ ANOTHER INSTANCE IS ALREADY RUNNING\n\n"
            "Only one instance of FBR Invoice Checker can run at a time.\n\n"
            "Please close the existing instance before starting a new one."
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
        
        # Show first run message to user
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Device Authorized",
            "✅ DEVICE SUCCESSFULLY AUTHORIZED\n\n"
            f"MAC Address: {mac_auth.current_mac}\n\n"
            "This device is now authorized to run the application.\n"
            "The administrator has been notified of this activation."
        )
        root.destroy()
    
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
    main()
