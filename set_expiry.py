"""
Admin Tool - Set Software Expiry Date
This utility allows administrators to set the software expiry date.
"""

import sys
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime, timedelta
from license_manager import LicenseManager


def set_expiry_via_gui():
    """Set expiry date using a GUI dialog."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.title("Software License Manager")
    
    # Get current license info
    license_mgr = LicenseManager()
    current_status = license_mgr.get_expiry_status()
    
    # Show current status
    current_info = (
        f"Current Expiry Date: {current_status['expiry_date']}\n"
        f"Days Remaining: {current_status['days_remaining']} days\n"
        f"\nEnter new expiry date (YYYY-MM-DD format):"
    )
    
    # Prompt for new date
    new_date = simpledialog.askstring(
        "Set Software Expiry Date",
        current_info,
        parent=root
    )
    
    if new_date is None:  # User cancelled
        root.destroy()
        return False
    
    # Validate and set the date
    if license_mgr.set_expiry_date(new_date):
        messagebox.showinfo(
            "Success",
            f"✓ Expiry date updated successfully!\n\n"
            f"New Expiry Date: {new_date}\n\n"
            f"License Information:\n"
            f"{license_mgr.get_expiry_info_text()}",
            parent=root
        )
        root.destroy()
        return True
    else:
        messagebox.showerror(
            "Error",
            f"❌ Failed to set expiry date.\n\n"
            f"Please use YYYY-MM-DD format.\n"
            f"Example: 2025-12-31",
            parent=root
        )
        root.destroy()
        return False


def set_expiry_via_cli():
    """Set expiry date using command line arguments."""
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("SOFTWARE LICENSE MANAGER - Command Line Tool")
        print("="*60)
        print("\nUsage:")
        print("  python set_expiry.py <YYYY-MM-DD>    Set new expiry date")
        print("  python set_expiry.py info             Show current license info")
        print("  python set_expiry.py gui              Open GUI tool")
        print("\nExample:")
        print("  python set_expiry.py 2025-12-31")
        print("  python set_expiry.py 2026-03-15")
        print("\n" + "="*60)
        return
    
    license_mgr = LicenseManager()
    command = sys.argv[1].lower()
    
    if command == "info":
        print("\n" + license_mgr.get_expiry_info_text())
    
    elif command == "gui":
        set_expiry_via_gui()
    
    else:
        # Try to set the date
        if license_mgr.set_expiry_date(command):
            print("\n" + "="*60)
            print("✓ EXPIRY DATE UPDATED SUCCESSFULLY")
            print("="*60)
            print(license_mgr.get_expiry_info_text())
            print("="*60 + "\n")
        else:
            print("\n" + "="*60)
            print("❌ FAILED TO UPDATE EXPIRY DATE")
            print("="*60)
            print(f"Invalid date format: {command}")
            print("Please use YYYY-MM-DD format (Example: 2025-12-31)")
            print("="*60 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1].lower() != "gui":
        # Use CLI mode if arguments provided (except for 'gui')
        set_expiry_via_cli()
    else:
        # Use GUI mode
        set_expiry_via_gui()


if __name__ == "__main__":
    main()
