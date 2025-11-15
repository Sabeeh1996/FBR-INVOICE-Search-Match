"""
INTEGRATE_INTO_YOUR_APP.py

Copy this code to your main.py or gui.py to enable MANDATORY updates.
Users will be FORCED to update before using the application.
"""

# ==============================================================================
# STEP 1: Add this to the TOP of your main.py or gui.py
# ==============================================================================

import sys
import os

# Import the updater
from updater import check_and_apply_updates


# ==============================================================================
# STEP 2: Add this function (or use directly in main)
# ==============================================================================

def enforce_mandatory_update():
    """
    Check for updates and BLOCK app if update is required but fails.
    
    Returns:
        bool: True if app can continue, False otherwise
    """
    print("=" * 70)
    print("FBR INVOICE CHECKER - Update Check")
    print("=" * 70)
    print()
    
    # Optional: Add progress bar
    def show_progress(downloaded, total):
        if total > 0:
            percent = (downloaded / total) * 100
            bar_length = 50
            filled = int(bar_length * downloaded / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percent:.0f}%", end='')
    
    # Check for mandatory updates
    print("Checking for updates...")
    success, message = check_and_apply_updates(
        progress_callback=show_progress,
        force_update=True  # ← This makes it MANDATORY
    )
    
    print("\n\n" + message)
    print()
    
    # Handle result
    if not success:
        # Update is required but failed - BLOCK APP
        print("=" * 70)
        print("⛔ APPLICATION CANNOT START")
        print("=" * 70)
        print()
        print("This application requires an update to continue.")
        print("Please check your internet connection and try again.")
        print()
        print("If the problem persists:")
        print("1. Check your firewall/antivirus settings")
        print("2. Download manually from:")
        print("   https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match/releases")
        print()
        input("Press Enter to exit...")
        return False
    
    if "restart" in message.lower():
        # Update was successful - restart required
        print("=" * 70)
        print("✓ UPDATE COMPLETE")
        print("=" * 70)
        print()
        print("The application will now restart.")
        print()
        input("Press Enter to exit...")
        return False
    
    # No update needed - continue
    print("✓ Application is up to date!")
    print()
    return True


# ==============================================================================
# STEP 3: Modify your main() function like this
# ==============================================================================

def main():
    """
    Main application entry point with mandatory update check.
    """
    # Check for mandatory updates FIRST
    if not enforce_mandatory_update():
        # Update failed or restart needed - exit
        sys.exit(0 if "restart" in str(sys.argv) else 1)
    
    # Continue with normal application startup
    print("Starting FBR Invoice Checker...")
    print("-" * 70)
    
    # Your existing application code goes here
    # For example:
    # import gui
    # gui.start_application()
    
    # Or if you have a function that starts your app:
    # run_invoice_checker()
    
    # Placeholder for demonstration
    print("Your application is now running!")
    print("This is where your normal app code would execute.")
    input("\nPress Enter to exit...")


# ==============================================================================
# STEP 4: Call main() at the bottom of your file
# ==============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nApplication error: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


# ==============================================================================
# ALTERNATIVE: Simple One-Liner Integration
# ==============================================================================

"""
If you want the SIMPLEST possible integration, just add these 3 lines
at the very start of your main.py:

    from updater import check_and_apply_updates
    import sys
    
    success, msg = check_and_apply_updates(force_update=True)
    print(msg)
    if not success or "restart" in msg.lower():
        sys.exit(0 if "restart" in msg.lower() else 1)
    
    # Your app code continues here...

That's it! Your app now has mandatory updates.
"""


# ==============================================================================
# GUI INTEGRATION EXAMPLE (for tkinter applications)
# ==============================================================================

"""
If you're using tkinter, add this to your GUI startup:

    def __init__(self):
        # Before creating your main window:
        if not self.check_mandatory_update():
            sys.exit(0)
        
        # Now create your GUI
        self.root = tk.Tk()
        # ... rest of your GUI code
    
    def check_mandatory_update(self):
        '''Check for mandatory updates before showing GUI.'''
        from updater import check_and_apply_updates
        
        success, message = check_and_apply_updates(force_update=True)
        
        if not success:
            messagebox.showerror(
                "Update Required",
                "This application requires an update.\\n\\n" + message
            )
            return False
        
        if "restart" in message.lower():
            messagebox.showinfo(
                "Update Complete",
                "Update installed successfully.\\nPlease restart the application."
            )
            return False
        
        return True
"""


# ==============================================================================
# TESTING
# ==============================================================================

"""
To test this integration:

1. Run this file directly:
   python INTEGRATE_INTO_YOUR_APP.py

2. Test with a GitHub release:
   - Create a release with tag v1.1
   - Run again and it will force update

3. Test update failure:
   - Disconnect internet
   - Run again and it will block the app

4. Test normal operation:
   - If no update available, app starts normally
"""
