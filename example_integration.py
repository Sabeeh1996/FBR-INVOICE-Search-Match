"""
example_integration.py

This file demonstrates how to integrate the auto-update system
into your FBR Invoice Checker application.

Choose one of the examples below based on your needs.
"""

import sys
import os

# ==============================================================================
# EXAMPLE 1: Automatic Update Check on Startup (Recommended)
# ==============================================================================

def example_1_automatic_startup():
    """
    Check for updates automatically when the application starts.
    This is the simplest and most recommended approach.
    """
    print("=" * 70)
    print("FBR INVOICE CHECKER - Starting...")
    print("=" * 70)
    
    # Import the updater
    from updater import check_and_apply_updates
    
    # Check for updates
    print("\nChecking for updates...")
    success, message = check_and_apply_updates()
    
    # Show result to user
    print(message)
    
    # If update was installed, ask user to restart
    if success and "restart" in message.lower():
        input("\nPress Enter to exit and restart the application...")
        sys.exit(0)
    
    # Continue with normal application startup
    print("\nStarting FBR Invoice Checker...")
    # Your normal app code here
    # import gui
    # gui.start()


# ==============================================================================
# EXAMPLE 2: Update Check with Progress Bar
# ==============================================================================

def example_2_with_progress():
    """
    Check for updates with a visual progress bar during download.
    """
    from updater import check_and_apply_updates
    
    def show_progress(downloaded, total):
        """Display a nice progress bar."""
        if total > 0:
            percent = (downloaded / total) * 100
            bar_length = 50
            filled = int(bar_length * downloaded / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # Format file sizes
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            
            print(f"\rDownloading: [{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='')
    
    print("Checking for updates...")
    success, message = check_and_apply_updates(progress_callback=show_progress)
    
    print("\n" + message)
    
    if success and "restart" in message.lower():
        input("\nPress Enter to restart...")
        sys.exit(0)


# ==============================================================================
# EXAMPLE 3: Manual "Check for Updates" Button (For GUI)
# ==============================================================================

def example_3_manual_check():
    """
    Manual update check - useful for a menu button in GUI.
    This gives users control over when to update.
    """
    from updater import Updater
    
    updater = Updater()
    
    print("Checking for updates...")
    available, release_info = updater.check_for_updates()
    
    if available:
        new_version = release_info['tag_name']
        current_version = updater.get_current_version()
        
        print(f"\n{'='*60}")
        print("UPDATE AVAILABLE!")
        print(f"{'='*60}")
        print(f"Current Version: v{current_version}")
        print(f"Latest Version:  {new_version}")
        print(f"Release Date:    {release_info.get('published_at', 'N/A')}")
        print(f"{'='*60}")
        
        # Ask user if they want to update
        response = input("\nWould you like to install this update? (y/n): ")
        
        if response.lower() == 'y':
            print("\nDownloading and installing update...")
            
            def show_progress(downloaded, total):
                if total > 0:
                    percent = (downloaded / total) * 100
                    print(f"\rProgress: {percent:.0f}%", end='')
            
            success, message = updater.check_and_apply_updates(
                progress_callback=show_progress
            )
            
            print("\n" + message)
            
            if success and "restart" in message.lower():
                input("\nPress Enter to exit...")
                sys.exit(0)
        else:
            print("Update cancelled by user")
    else:
        print("\n✓ Your application is up to date!")


# ==============================================================================
# EXAMPLE 4: Silent Background Check
# ==============================================================================

def example_4_background_check():
    """
    Check for updates silently in the background.
    Notify user later without interrupting their work.
    """
    import threading
    from updater import Updater
    
    update_available_flag = {"available": False, "version": None}
    
    def background_check():
        """Run in background thread."""
        updater = Updater()
        available, release = updater.check_for_updates()
        
        if available:
            update_available_flag["available"] = True
            update_available_flag["version"] = release['tag_name']
            print(f"\n[Background] Update available: {release['tag_name']}")
    
    # Start background check
    print("Starting background update check...")
    thread = threading.Thread(target=background_check, daemon=True)
    thread.start()
    
    # Continue with app...
    print("Application running...")
    
    # Later, check if update was found
    thread.join(timeout=10)  # Wait max 10 seconds
    
    if update_available_flag["available"]:
        print(f"\n⚠ Update available: {update_available_flag['version']}")
        print("You can update from the Help menu.")


# ==============================================================================
# EXAMPLE 5: Integration with Tkinter GUI
# ==============================================================================

def example_5_tkinter_integration():
    """
    How to integrate auto-update into a tkinter GUI application.
    """
    try:
        import tkinter as tk
        from tkinter import messagebox
        from updater import Updater
        import threading
        
        class UpdaterGUI:
            def __init__(self):
                self.root = tk.Tk()
                self.root.title("FBR Invoice Checker")
                self.root.geometry("400x300")
                
                self.updater = Updater()
                
                # Create menu
                menubar = tk.Menu(self.root)
                help_menu = tk.Menu(menubar, tearoff=0)
                help_menu.add_command(
                    label="Check for Updates",
                    command=self.manual_update_check
                )
                help_menu.add_separator()
                help_menu.add_command(label="About", command=self.show_about)
                menubar.add_cascade(label="Help", menu=help_menu)
                self.root.config(menu=menubar)
                
                # Add content
                label = tk.Label(
                    self.root,
                    text="FBR Invoice Checker",
                    font=("Arial", 16, "bold")
                )
                label.pack(pady=50)
                
                # Check for updates on startup (in background)
                self.root.after(1000, self.startup_update_check)
            
            def startup_update_check(self):
                """Check for updates when app starts (non-blocking)."""
                def check():
                    available, release = self.updater.check_for_updates()
                    if available:
                        self.root.after(0, lambda: self.show_update_dialog(release))
                
                threading.Thread(target=check, daemon=True).start()
            
            def manual_update_check(self):
                """Called when user clicks Check for Updates menu."""
                def check():
                    available, release = self.updater.check_for_updates()
                    
                    if available:
                        self.root.after(0, lambda: self.show_update_dialog(release))
                    else:
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Up to Date",
                            "You have the latest version!"
                        ))
                
                threading.Thread(target=check, daemon=True).start()
            
            def show_update_dialog(self, release):
                """Show update available dialog."""
                new_version = release['tag_name']
                current = self.updater.get_current_version()
                
                response = messagebox.askyesno(
                    "Update Available",
                    f"Version {new_version} is available!\n\n"
                    f"Current version: v{current}\n"
                    f"Latest version: {new_version}\n\n"
                    f"Download and install now?\n"
                    f"(Application will restart after update)"
                )
                
                if response:
                    self.apply_update()
            
            def apply_update(self):
                """Download and install update."""
                # Show progress window
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Updating...")
                progress_window.geometry("400x150")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                status_label = tk.Label(
                    progress_window,
                    text="Downloading update...",
                    font=("Arial", 10)
                )
                status_label.pack(pady=20)
                
                progress_label = tk.Label(
                    progress_window,
                    text="0%",
                    font=("Arial", 12, "bold")
                )
                progress_label.pack(pady=10)
                
                def update_progress(downloaded, total):
                    if total > 0:
                        percent = (downloaded / total) * 100
                        progress_window.after(0, lambda: progress_label.config(
                            text=f"{percent:.0f}%"
                        ))
                
                def do_update():
                    success, message = self.updater.check_and_apply_updates(
                        progress_callback=update_progress
                    )
                    
                    progress_window.after(0, progress_window.destroy)
                    
                    if success and "restart" in message.lower():
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Update Complete",
                            message
                        ))
                        self.root.after(100, self.root.quit)
                    elif not success:
                        self.root.after(0, lambda: messagebox.showerror(
                            "Update Failed",
                            message
                        ))
                
                threading.Thread(target=do_update, daemon=True).start()
            
            def show_about(self):
                """Show about dialog."""
                version = self.updater.get_current_version()
                messagebox.showinfo(
                    "About",
                    f"FBR Invoice Checker\nVersion {version}\n\n"
                    f"Auto-update system enabled"
                )
            
            def run(self):
                """Start the GUI."""
                self.root.mainloop()
        
        # Run the GUI
        app = UpdaterGUI()
        app.run()
        
    except ImportError:
        print("Tkinter not available - skipping GUI example")


# ==============================================================================
# MAIN - Choose which example to run
# ==============================================================================

if __name__ == "__main__":
    print("AUTO-UPDATE SYSTEM INTEGRATION EXAMPLES")
    print("=" * 70)
    print()
    print("Choose an example to run:")
    print()
    print("1. Automatic update check on startup (Recommended)")
    print("2. Update check with progress bar")
    print("3. Manual update check (for menu button)")
    print("4. Silent background check")
    print("5. Tkinter GUI integration")
    print()
    
    choice = input("Enter choice (1-5): ")
    print()
    
    if choice == "1":
        example_1_automatic_startup()
    elif choice == "2":
        example_2_with_progress()
    elif choice == "3":
        example_3_manual_check()
    elif choice == "4":
        example_4_background_check()
    elif choice == "5":
        example_5_tkinter_integration()
    else:
        print("Invalid choice")
