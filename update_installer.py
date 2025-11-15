"""
update_installer.py

This module handles extracting and installing updates safely.
It includes ZIP validation, backup creation, and rollback capabilities.

Author: Auto-Update System
Date: 2025
"""

import os
import sys
import shutil
import zipfile
import logging
from typing import Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UpdateInstaller:
    """
    Extracts and installs updates with safety mechanisms.
    
    This class handles:
    - ZIP file validation
    - Backup creation before updating
    - Safe file replacement
    - Rollback on failure
    - Version file updates
    """
    
    def __init__(self, app_dir: Optional[str] = None):
        """
        Initialize the UpdateInstaller.
        
        Args:
            app_dir (str, optional): Application directory to update.
                                     Defaults to current directory.
        """
        self.app_dir = app_dir or os.getcwd()
        self.backup_dir = os.path.join(self.app_dir, "backup_before_update")
        self.version_file = os.path.join(self.app_dir, "version.txt")
        
        logger.info(f"UpdateInstaller initialized for: {self.app_dir}")
    
    def validate_zip(self, zip_path: str) -> bool:
        """
        Validate that a ZIP file is not corrupted.
        
        Args:
            zip_path (str): Path to ZIP file
            
        Returns:
            bool: True if ZIP is valid, False otherwise
        """
        try:
            if not os.path.exists(zip_path):
                logger.error(f"ZIP file not found: {zip_path}")
                return False
            
            if os.path.getsize(zip_path) == 0:
                logger.error("ZIP file is empty")
                return False
            
            # Try to open and test the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Test ZIP integrity
                corrupt_file = zip_ref.testzip()
                if corrupt_file:
                    logger.error(f"Corrupt file in ZIP: {corrupt_file}")
                    return False
                
                # List contents for logging
                file_list = zip_ref.namelist()
                logger.info(f"ZIP contains {len(file_list)} files")
                
                return True
                
        except zipfile.BadZipFile:
            logger.error("Invalid or corrupt ZIP file")
            return False
        except Exception as e:
            logger.error(f"Error validating ZIP: {str(e)}")
            return False
    
    def create_backup(self) -> bool:
        """
        Create a backup of current application files.
        
        This is a safety measure - if update fails, we can restore from backup.
        
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            # Remove old backup if it exists
            if os.path.exists(self.backup_dir):
                logger.info("Removing old backup...")
                shutil.rmtree(self.backup_dir)
            
            # Create backup directory
            os.makedirs(self.backup_dir)
            logger.info(f"Creating backup at: {self.backup_dir}")
            
            # List of important files to backup
            important_files = [
                'version.txt',
                'license_config.json',
                'main.py',
                'fbr_checker.py',
                'gui.py',
                'excel_handler.py',
                'license_manager.py'
            ]
            
            backup_count = 0
            
            # Backup specific important files
            for filename in important_files:
                file_path = os.path.join(self.app_dir, filename)
                if os.path.exists(file_path):
                    dest_path = os.path.join(self.backup_dir, filename)
                    shutil.copy2(file_path, dest_path)
                    backup_count += 1
                    logger.debug(f"Backed up: {filename}")
            
            # Backup entire assets directory if it exists
            assets_dir = os.path.join(self.app_dir, 'assets')
            if os.path.exists(assets_dir):
                backup_assets = os.path.join(self.backup_dir, 'assets')
                shutil.copytree(assets_dir, backup_assets)
                logger.debug("Backed up assets directory")
                backup_count += 1
            
            logger.info(f"Backup completed: {backup_count} items backed up")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return False
    
    def extract_update(self, zip_path: str) -> bool:
        """
        Extract update ZIP to application directory.
        
        Args:
            zip_path (str): Path to update ZIP file
            
        Returns:
            bool: True if extraction successful, False otherwise
        """
        try:
            logger.info(f"Extracting update from: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of files to extract
                file_list = zip_ref.namelist()
                
                # Extract all files
                for file_name in file_list:
                    try:
                        # Skip directory entries
                        if file_name.endswith('/'):
                            continue
                        
                        # Extract file
                        zip_ref.extract(file_name, self.app_dir)
                        logger.debug(f"Extracted: {file_name}")
                        
                    except Exception as e:
                        logger.warning(f"Could not extract {file_name}: {str(e)}")
                        continue
                
                logger.info(f"Successfully extracted {len(file_list)} files")
                return True
                
        except Exception as e:
            logger.error(f"Error extracting update: {str(e)}")
            return False
    
    def update_version_file(self, new_version: str) -> bool:
        """
        Update the version.txt file with new version number.
        
        Args:
            new_version (str): New version string (e.g., "v1.2" or "1.2")
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Clean version string (remove 'v' prefix if present)
            clean_version = new_version.strip().lower().replace('v', '')
            
            # Write new version to file
            with open(self.version_file, 'w') as f:
                f.write(clean_version)
            
            logger.info(f"Updated version file to: {clean_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating version file: {str(e)}")
            return False
    
    def rollback(self) -> bool:
        """
        Restore files from backup if update fails.
        
        Returns:
            bool: True if rollback successful, False otherwise
        """
        try:
            if not os.path.exists(self.backup_dir):
                logger.error("No backup found to restore")
                return False
            
            logger.info("Rolling back to previous version...")
            
            # Restore all files from backup
            for item in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, item)
                dest_path = os.path.join(self.app_dir, item)
                
                if os.path.isfile(backup_path):
                    shutil.copy2(backup_path, dest_path)
                    logger.debug(f"Restored: {item}")
                elif os.path.isdir(backup_path):
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(backup_path, dest_path)
                    logger.debug(f"Restored directory: {item}")
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during rollback: {str(e)}")
            return False
    
    def cleanup_backup(self):
        """
        Remove backup directory after successful update.
        """
        try:
            if os.path.exists(self.backup_dir):
                shutil.rmtree(self.backup_dir)
                logger.info("Backup cleaned up")
        except Exception as e:
            logger.warning(f"Could not clean up backup: {str(e)}")
    
    def cleanup_update_file(self, zip_path: str):
        """
        Remove downloaded update ZIP after installation.
        
        Args:
            zip_path (str): Path to update ZIP file
        """
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
                logger.info(f"Removed update file: {zip_path}")
        except Exception as e:
            logger.warning(f"Could not remove update file: {str(e)}")
    
    def install_update(self, zip_path: str, new_version: str) -> bool:
        """
        Complete update installation process.
        
        This is the main method that orchestrates the entire installation:
        1. Validate ZIP
        2. Create backup
        3. Extract update
        4. Update version file
        5. Cleanup
        
        If any step fails, it rolls back to the previous version.
        
        Args:
            zip_path (str): Path to update ZIP file
            new_version (str): New version string
            
        Returns:
            bool: True if installation successful, False otherwise
            
        Example:
            installer = UpdateInstaller()
            success = installer.install_update("update.zip", "1.2")
            if success:
                print("Update installed! Please restart.")
        """
        try:
            logger.info("=" * 60)
            logger.info("STARTING UPDATE INSTALLATION")
            logger.info("=" * 60)
            
            # Step 1: Validate ZIP
            logger.info("[1/5] Validating update file...")
            if not self.validate_zip(zip_path):
                logger.error("Update file validation failed")
                return False
            logger.info("✓ Update file is valid")
            
            # Step 2: Create backup
            logger.info("[2/5] Creating backup...")
            if not self.create_backup():
                logger.error("Backup creation failed - aborting update")
                return False
            logger.info("✓ Backup created")
            
            # Step 3: Extract update
            logger.info("[3/5] Extracting update files...")
            if not self.extract_update(zip_path):
                logger.error("Extraction failed - rolling back")
                self.rollback()
                return False
            logger.info("✓ Files extracted")
            
            # Step 4: Update version file
            logger.info("[4/5] Updating version information...")
            if not self.update_version_file(new_version):
                logger.error("Version update failed - rolling back")
                self.rollback()
                return False
            logger.info(f"✓ Version updated to {new_version}")
            
            # Step 5: Cleanup
            logger.info("[5/5] Cleaning up...")
            self.cleanup_update_file(zip_path)
            self.cleanup_backup()
            logger.info("✓ Cleanup completed")
            
            logger.info("=" * 60)
            logger.info("UPDATE INSTALLATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error during installation: {str(e)}")
            logger.info("Attempting rollback...")
            self.rollback()
            return False


# Example usage (for testing purposes)
if __name__ == "__main__":
    print("UpdateInstaller Test")
    print("=" * 60)
    
    # Create installer instance
    installer = UpdateInstaller()
    
    # Example 1: Validate a ZIP file
    print("\nExample 1: Validate ZIP")
    print("-" * 60)
    test_zip = "update.zip"
    if os.path.exists(test_zip):
        is_valid = installer.validate_zip(test_zip)
        print(f"ZIP validation result: {is_valid}")
    else:
        print(f"Test file '{test_zip}' not found")
    
    # Example 2: Create backup
    print("\nExample 2: Create Backup")
    print("-" * 60)
    backup_success = installer.create_backup()
    print(f"Backup creation result: {backup_success}")
    
    # Example 3: Full installation (requires valid update.zip)
    print("\nExample 3: Full Installation")
    print("-" * 60)
    if os.path.exists(test_zip):
        success = installer.install_update(test_zip, "1.2")
        if success:
            print("\n✓ Update installed successfully!")
            print("⚠ Application restart required")
        else:
            print("\n✗ Update installation failed")
    else:
        print("No update.zip file found for installation test")
    
    print("\n" + "=" * 60)
