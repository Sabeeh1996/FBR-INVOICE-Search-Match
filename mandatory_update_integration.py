"""
mandatory_update_integration.py

This file shows how to integrate MANDATORY updates into your application.
Users MUST update before they can use the app.
"""

import sys
import os


# ==============================================================================
# EXAMPLE 1: Simple Mandatory Update (Recommended)
# ==============================================================================

def example_1_mandatory_simple():
    """
    Simplest mandatory update implementation.
    App exits if update is required but fails.
    """
    print("=" * 70)
    print("FBR INVOICE CHECKER - Starting with MANDATORY UPDATE CHECK")
    print("=" * 70)
    
    from updater import check_and_apply_updates
    
    print("\nChecking for mandatory updates...")
    success, message = check_and_apply_updates(force_update=True)
    
    print("\n" + message)
    
    if not success:
        # Update is mandatory but failed
        print("\n" + "=" * 70)
        print("⛔ APPLICATION CANNOT START")
        print("=" * 70)
        print("\nThis application requires an update to continue.")
        print("Please check your internet connection and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)  # Exit with error code
    
    if "restart" in message.lower():
        # Update was successful, restart required
        print("\n" + "=" * 70)
        print("✓ UPDATE COMPLETE - RESTART REQUIRED")
        print("=" * 70)
        input("\nPress Enter to exit and restart...")
        sys.exit(0)  # Exit successfully
    
    # No update needed, continue normally
    print("\n✓ Starting application...")
    print("Your application code runs here...")
    # run_your_app()


# ==============================================================================
# EXAMPLE 2: Mandatory Update with Progress Bar
# ==============================================================================

def example_2_mandatory_with_progress():
    """
    Mandatory update with visual progress display.
    """
    from updater import check_and_apply_updates
    
    print("=" * 70)
    print("FBR INVOICE CHECKER")
    print("=" * 70)
    
    def show_progress(downloaded, total):
        """Display download progress."""
        if total > 0:
            percent = (downloaded / total) * 100
            bar_length = 50
            filled = int(bar_length * downloaded / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            
            print(f"\r[{bar}] {percent:.0f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='')
    
    print("\nChecking for updates...")
    success, message = check_and_apply_updates(
        progress_callback=show_progress,
        force_update=True
    )
    
    print("\n\n" + message)
    
    if not success:
        print("\n⛔ Cannot start application without update")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if "restart" in message.lower():
        input("\nPress Enter to restart...")
        sys.exit(0)
    
    print("\n✓ Starting application...")


# ==============================================================================
# EXAMPLE 3: Mandatory Update with Retry Option
# ==============================================================================

def example_3_mandatory_with_retry():
    """
    Mandatory update with retry attempts if it fails.
    """
    from updater import check_and_apply_updates
    import time
    
    print("=" * 70)
    print("FBR INVOICE CHECKER - Secure Update System")
    print("=" * 70)
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        if retry_count > 0:
            print(f"\nRetry attempt {retry_count}/{max_retries-1}...")
            time.sleep(2)  # Wait before retry
        
        print("\nChecking for updates...")
        success, message = check_and_apply_updates(force_update=True)
        
        print(message)
        
        if success:
            if "restart" in message.lower():
                print("\n✓ Update complete!")
                input("Press Enter to restart...")
                sys.exit(0)
            else:
                # No update needed
                print("\n✓ Starting application...")
                return
        else:
            # Update failed
            retry_count += 1
            if retry_count < max_retries:
                response = input(f"\nUpdate failed. Retry? (y/n): ")
                if response.lower() != 'y':
                    break
    
    # All retries failed
    print("\n" + "=" * 70)
    print("⛔ UNABLE TO UPDATE APPLICATION")
    print("=" * 70)
    print("\nPossible solutions:")
    print("1. Check your internet connection")
    print("2. Disable firewall/antivirus temporarily")
    print("3. Contact support")
    print(f"\nGitHub Releases: https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match/releases")
    input("\nPress Enter to exit...")
    sys.exit(1)


# ==============================================================================
# EXAMPLE 4: GUI Integration with Mandatory Update
# ==============================================================================

def example_4_gui_mandatory():
    """
    How to integrate mandatory updates in a tkinter GUI.
    """
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
        from updater import Updater
        import threading
        
        class MandatoryUpdateGUI:
            def __init__(self):
                self.root = tk.Tk()
                self.root.title("FBR Invoice Checker - Update Required")
                self.root.geometry("500x300")
                self.root.resizable(False, False)
                
                # Prevent window closing during update
                self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
                
                self.updater = Updater()
                self.update_required = False
                self.update_in_progress = False
                
                self.create_widgets()
                
                # Check for updates immediately
                self.root.after(500, self.check_updates)
            
            def create_widgets(self):
                """Create UI elements."""
                # Title
                title = tk.Label(
                    self.root,
                    text="FBR Invoice Checker",
                    font=("Arial", 18, "bold")
                )
                title.pack(pady=20)
                
                # Status label
                self.status_label = tk.Label(
                    self.root,
                    text="Checking for updates...",
                    font=("Arial", 12)
                )
                self.status_label.pack(pady=20)
                
                # Progress bar
                self.progress = ttk.Progressbar(
                    self.root,
                    length=400,
                    mode='indeterminate'
                )
                self.progress.pack(pady=10)
                self.progress.start()
                
                # Details label
                self.details_label = tk.Label(
                    self.root,
                    text="",
                    font=("Arial", 9),
                    fg="gray"
                )
                self.details_label.pack(pady=10)
                
                # Button frame
                self.button_frame = tk.Frame(self.root)
                self.button_frame.pack(pady=20)
            
            def check_updates(self):
                """Check for updates in background."""
                def check_thread():
                    available, release = self.updater.check_for_updates()
                    
                    if available:
                        # Update required
                        self.update_required = True
                        new_version = release['tag_name']
                        current = self.updater.get_current_version()
                        
                        self.root.after(0, lambda: self.show_update_required(
                            current, new_version
                        ))
                    else:
                        # No update, start app
                        self.root.after(0, self.start_application)
                
                threading.Thread(target=check_thread, daemon=True).start()
            
            def show_update_required(self, current, new_version):
                """Show mandatory update message."""
                self.progress.stop()
                self.progress['mode'] = 'determinate'
                self.progress['value'] = 0
                
                self.status_label.config(
                    text=f"⚠ UPDATE REQUIRED",
                    fg="red",
                    font=("Arial", 14, "bold")
                )
                
                self.details_label.config(
                    text=f"Current: v{current} → Required: {new_version}",
                    font=("Arial", 10, "bold")
                )
                
                # Add update button
                update_btn = tk.Button(
                    self.button_frame,
                    text="Update Now (Required)",
                    command=self.start_update,
                    bg="#4CAF50",
                    fg="white",
                    font=("Arial", 12, "bold"),
                    width=20,
                    height=2
                )
                update_btn.pack()
            
            def start_update(self):
                """Start the update process."""
                if self.update_in_progress:
                    return
                
                self.update_in_progress = True
                self.status_label.config(text="Downloading update...", fg="blue")
                
                # Clear button
                for widget in self.button_frame.winfo_children():
                    widget.destroy()
                
                def update_thread():
                    def progress_callback(downloaded, total):
                        if total > 0:
                            percent = (downloaded / total) * 100
                            self.root.after(0, lambda: self.progress.config(value=percent))
                    
                    success, message = self.updater.check_and_apply_updates(
                        progress_callback=progress_callback,
                        force_update=True
                    )
                    
                    self.root.after(0, lambda: self.update_complete(success, message))
                
                threading.Thread(target=update_thread, daemon=True).start()
            
            def update_complete(self, success, message):
                """Handle update completion."""
                self.update_in_progress = False
                
                if success and "restart" in message.lower():
                    self.status_label.config(
                        text="✓ Update Complete!",
                        fg="green"
                    )
                    self.details_label.config(text="Application will now restart")
                    
                    restart_btn = tk.Button(
                        self.button_frame,
                        text="Restart Now",
                        command=self.root.quit,
                        bg="#2196F3",
                        fg="white",
                        font=("Arial", 12, "bold"),
                        width=15
                    )
                    restart_btn.pack()
                    
                    # Auto-restart after 5 seconds
                    self.root.after(5000, self.root.quit)
                
                elif not success:
                    self.status_label.config(
                        text="✗ Update Failed",
                        fg="red"
                    )
                    self.details_label.config(text=message)
                    
                    retry_btn = tk.Button(
                        self.button_frame,
                        text="Retry Update",
                        command=self.start_update,
                        bg="#FF9800",
                        fg="white",
                        font=("Arial", 12, "bold"),
                        width=15
                    )
                    retry_btn.pack(pady=5)
                    
                    exit_btn = tk.Button(
                        self.button_frame,
                        text="Exit Application",
                        command=lambda: sys.exit(1),
                        bg="#f44336",
                        fg="white",
                        font=("Arial", 10),
                        width=15
                    )
                    exit_btn.pack(pady=5)
                else:
                    # No update needed
                    self.start_application()
            
            def start_application(self):
                """Start the main application."""
                self.status_label.config(text="✓ Up to date!", fg="green")
                self.details_label.config(text="Starting application...")
                self.progress.stop()
                
                # Close update window and start main app
                self.root.after(1000, self.launch_main_app)
            
            def launch_main_app(self):
                """Launch the main application."""
                self.root.destroy()
                print("Main application would start here...")
                # import gui
                # gui.start()
            
            def on_closing(self):
                """Handle window close attempt."""
                if self.update_in_progress:
                    messagebox.showwarning(
                        "Update in Progress",
                        "Please wait for the update to complete."
                    )
                elif self.update_required:
                    response = messagebox.askyesno(
                        "Exit Application",
                        "Update is required to use this application.\n\n"
                        "Are you sure you want to exit?"
                    )
                    if response:
                        sys.exit(1)
                else:
                    self.root.destroy()
            
            def run(self):
                """Start the GUI."""
                self.root.mainloop()
        
        # Run the GUI
        app = MandatoryUpdateGUI()
        app.run()
        
    except ImportError:
        print("Tkinter not available - skipping GUI example")


# ==============================================================================
# MAIN - Choose Example
# ==============================================================================

if __name__ == "__main__":
    print("\nMANDATORY UPDATE INTEGRATION EXAMPLES")
    print("=" * 70)
    print("\nThese examples show how to FORCE users to update.")
    print("Users cannot use the app without updating to the latest version.\n")
    print("Choose an example:")
    print()
    print("1. Simple mandatory update (recommended)")
    print("2. Mandatory update with progress bar")
    print("3. Mandatory update with retry option")
    print("4. GUI with mandatory update")
    print()
    
    choice = input("Enter choice (1-4): ")
    print()
    
    if choice == "1":
        example_1_mandatory_simple()
    elif choice == "2":
        example_2_mandatory_with_progress()
    elif choice == "3":
        example_3_mandatory_with_retry()
    elif choice == "4":
        example_4_gui_mandatory()
    else:
        print("Invalid choice")
