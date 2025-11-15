"""
updater.py

Main orchestrator for the auto-update system.
Provides a simple one-function interface: check_and_apply_updates()

This module coordinates all update operations:
- Checking for updates
- Downloading updates
- Installing updates
- Error handling

Author: Auto-Update System
Date: 2025
"""

import os
import sys
import logging
from typing import Optional, Tuple, Callable

# Import our update modules
from update_checker import UpdateChecker
from update_downloader import UpdateDownloader
from update_installer import UpdateInstaller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Updater:
    """
    Main auto-update orchestrator.
    
    This class brings together all update components and provides
    a simple interface for checking and applying updates.
    """
    
    # GitHub repository information
    REPO_OWNER = "Sabeeh1996"
    REPO_NAME = "FBR-INVOICE-Search-Match"
    
    def __init__(self, app_dir: Optional[str] = None):
        """
        Initialize the Updater.
        
        Args:
            app_dir (str, optional): Application directory. Defaults to current directory.
        """
        self.app_dir = app_dir or os.getcwd()
        self.version_file = os.path.join(self.app_dir, "version.txt")
        
        # Initialize update components
        self.checker = UpdateChecker(self.REPO_OWNER, self.REPO_NAME)
        self.downloader = UpdateDownloader(self.app_dir)
        self.installer = UpdateInstaller(self.app_dir)
        
        logger.info("Updater initialized")
    
    def get_current_version(self) -> str:
        """
        Read current version from version.txt file.
        
        Returns:
            str: Current version (e.g., "1.0")
                 Returns "0.0" if file not found or error occurs
        """
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    version = f.read().strip()
                    logger.info(f"Current version: {version}")
                    return version
            else:
                logger.warning("version.txt not found, assuming version 0.0")
                return "0.0"
                
        except Exception as e:
            logger.error(f"Error reading version file: {str(e)}")
            return "0.0"
    
    def check_for_updates(self) -> Tuple[bool, Optional[dict]]:
        """
        Check if a new version is available.
        
        Returns:
            tuple: (update_available: bool, release_data: dict or None)
            
        Example:
            updater = Updater()
            available, release_info = updater.check_for_updates()
            if available:
                print(f"New version: {release_info['tag_name']}")
        """
        try:
            current_version = self.get_current_version()
            logger.info(f"Checking for updates (current: v{current_version})...")
            
            release_data = self.checker.check_for_updates(current_version)
            
            if release_data:
                logger.info(f"Update found: {release_data['tag_name']}")
                return True, release_data
            else:
                logger.info("No updates available")
                return False, None
                
        except Exception as e:
            logger.error(f"Error checking for updates: {str(e)}")
            return False, None
    
    def download_update(
        self,
        release_data: dict,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Optional[str]:
        """
        Download update from GitHub release.
        
        Args:
            release_data (dict): Release information from check_for_updates()
            progress_callback (callable, optional): Progress tracking function
            
        Returns:
            str: Path to downloaded update file
            None: If download failed
        """
        try:
            logger.info("Starting download...")
            
            # Check if release has assets
            assets = release_data.get('assets', [])
            if not assets:
                logger.error("Release has no downloadable assets")
                return None
            
            # Download the update
            if progress_callback:
                update_file = self.downloader.download_file(
                    assets[0]['browser_download_url'],
                    progress_callback=progress_callback
                )
            else:
                update_file = self.downloader.download_from_release(release_data)
            
            if update_file:
                logger.info(f"Download completed: {update_file}")
            else:
                logger.error("Download failed")
            
            return update_file
            
        except Exception as e:
            logger.error(f"Error downloading update: {str(e)}")
            return None
    
    def install_update(self, update_file: str, new_version: str) -> bool:
        """
        Install downloaded update.
        
        Args:
            update_file (str): Path to downloaded update ZIP
            new_version (str): Version to update to
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        try:
            logger.info("Starting installation...")
            
            success = self.installer.install_update(update_file, new_version)
            
            if success:
                logger.info("Installation completed successfully")
            else:
                logger.error("Installation failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error installing update: {str(e)}")
            return False
    
    def check_and_apply_updates(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        interactive: bool = True,
        force_update: bool = True
    ) -> Tuple[bool, str]:
        """
        Complete auto-update process: check, download, and install.
        
        This is the main function you'll use in your application!
        
        Args:
            progress_callback (callable, optional): Function to track download progress
            interactive (bool): If True, returns status for user interaction.
                               If False, applies update silently.
            force_update (bool): If True, users MUST update before continuing.
                                If False, update is optional.
        
        Returns:
            tuple: (success: bool, message: str)
                   success: True if update was applied or no update needed
                   message: Description of what happened
        
        Example Usage:
            # Mandatory update on startup
            updater = Updater()
            success, message = updater.check_and_apply_updates(force_update=True)
            if not success:
                print(message)
                sys.exit(1)  # Exit app if update failed
        """
        try:
            logger.info("=" * 70)
            logger.info("STARTING AUTO-UPDATE CHECK")
            logger.info("=" * 70)
            
            # Step 1: Check for updates
            logger.info("Step 1: Checking for updates...")
            update_available, release_data = self.check_for_updates()
            
            if not update_available:
                message = "Your application is up to date!"
                logger.info(message)
                return True, message
            
            # Get version info
            current_version = self.get_current_version()
            new_version = release_data['tag_name']
            
            logger.info(f"Update available: v{current_version} -> {new_version}")
            
            # Step 2: Download update
            logger.info("Step 2: Downloading update...")
            update_file = self.download_update(release_data, progress_callback)
            
            if not update_file:
                message = "Failed to download update. Please check your internet connection."
                logger.error(message)
                return False, message
            
            # Step 3: Install update
            logger.info("Step 3: Installing update...")
            installation_success = self.install_update(update_file, new_version)
            
            if installation_success:
                message = (
                    f"✓ Successfully updated to version {new_version}!\n"
                    f"⚠ Please restart the application to use the new version."
                )
                logger.info("Update completed successfully!")
                return True, message
            else:
                if force_update:
                    message = (
                        f"❌ CRITICAL: Update to version {new_version} is required!\n"
                        f"Installation failed. Please check your internet connection and try again.\n"
                        f"The application cannot continue without this update."
                    )
                    logger.error("Mandatory update failed - blocking application start")
                    return False, message
                else:
                    message = "Update installation failed. Your application was not modified."
                    logger.error(message)
                    return False, message
            
        except Exception as e:
            message = f"Update process error: {str(e)}"
            logger.error(message)
            return False, message


def check_and_apply_updates(
    progress_callback: Optional[Callable[[int, int], None]] = None,
    force_update: bool = True
) -> Tuple[bool, str]:
    """
    Simple convenience function for auto-update.
    
    This is the easiest way to add auto-update to your application!
    Just call this function on startup.
    
    Args:
        progress_callback (callable, optional): Function to show download progress
        force_update (bool): If True, users MUST update (app exits if they don't).
                            If False, update is optional.
        
    Returns:
        tuple: (success: bool, message: str)
        
    Example:
        # In your main.py - MANDATORY UPDATE:
        from updater import check_and_apply_updates
        import sys
        
        success, message = check_and_apply_updates(force_update=True)
        print(message)
        
        if not success:
            # Update required but failed - block app
            input("Press Enter to exit...")
            sys.exit(1)
        
        if "restart" in message.lower():
            # Update successful - restart required
            input("Press Enter to exit and restart...")
            sys.exit(0)
        
        # No update needed - continue normally
    """
    updater = Updater()
    return updater.check_and_apply_updates(
        progress_callback=progress_callback,
        force_update=force_update
    )


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("FBR INVOICE CHECKER - AUTO-UPDATE SYSTEM")
    print("=" * 70)
    print()
    
    # Example 1: Simple update check (recommended for most cases)
    print("Running auto-update check...")
    print("-" * 70)
    
    def show_progress(downloaded, total):
        """Simple progress display."""
        if total > 0:
            percent = (downloaded / total) * 100
            bar_length = 40
            filled = int(bar_length * downloaded / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\rDownloading: [{bar}] {percent:.1f}%", end='')
    
    # Run the update
    success, message = check_and_apply_updates(progress_callback=show_progress)
    
    print("\n")
    print("-" * 70)
    print("Result:", message)
    print("-" * 70)
    
    # Example 2: Manual update check with more control
    print("\n\nExample 2: Manual Update Check")
    print("-" * 70)
    
    updater = Updater()
    
    # Check if update is available
    available, release_info = updater.check_for_updates()
    
    if available:
        print(f"\n✓ Update Available!")
        print(f"  Current Version: v{updater.get_current_version()}")
        print(f"  Latest Version: {release_info['tag_name']}")
        print(f"  Release Name: {release_info.get('name', 'N/A')}")
        print(f"  Published: {release_info.get('published_at', 'N/A')}")
        
        # Ask user if they want to update
        response = input("\nWould you like to install this update? (y/n): ")
        
        if response.lower() == 'y':
            success, message = updater.check_and_apply_updates(
                progress_callback=show_progress
            )
            print("\n" + message)
            
            if success and "restart" in message.lower():
                input("\nPress Enter to exit...")
                sys.exit(0)
        else:
            print("Update skipped")
    else:
        print("\n✓ Your application is up to date!")
    
    print("\n" + "=" * 70)
