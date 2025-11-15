"""
License Manager Module
Handles software expiry management with early notifications and license validation.
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path


class LicenseManager:
    """
    Manages software license/expiry system with notifications.
    """
    
    # Default expiry date - can be set to any future date
    DEFAULT_EXPIRY_DATE = "2025-11-30"  # YYYY-MM-DD format
    
    # Days before expiry to show warning
    EARLY_WARNING_DAYS = 15
    
    # Days before expiry to show critical warning
    CRITICAL_WARNING_DAYS = 7
    
    # Config file location
    CONFIG_FILE = "license_config.json"
    
    def __init__(self):
        """Initialize the license manager."""
        self.expiry_date = None
        self.license_config = None
        self.load_or_create_config()
    
    def _get_resource_path(self, relative_path):
        """
        Get absolute path to resource, works for dev and for PyInstaller.
        When running as exe, PyInstaller extracts files to sys._MEIPASS.
        """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # Running in normal Python environment
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def _is_running_as_exe(self):
        """Check if running as PyInstaller bundled executable."""
        return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    
    def load_or_create_config(self):
        """
        Load license config from bundled file.
        When running as exe, license is bundled inside and cannot be modified.
        """
        try:
            # When running as exe, always load from bundled resource
            if self._is_running_as_exe():
                config_path = self._get_resource_path(self.CONFIG_FILE)
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.license_config = json.load(f)
                    self.expiry_date = datetime.strptime(
                        self.license_config.get('expiry_date', self.DEFAULT_EXPIRY_DATE),
                        '%Y-%m-%d'
                    ).date()
                    logging.info(f"License loaded from bundled config. Expiry date: {self.expiry_date}")
            else:
                # Development mode: load or create local config file
                if os.path.exists(self.CONFIG_FILE):
                    with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                        self.license_config = json.load(f)
                        self.expiry_date = datetime.strptime(
                            self.license_config.get('expiry_date', self.DEFAULT_EXPIRY_DATE),
                            '%Y-%m-%d'
                        ).date()
                        logging.info(f"License loaded from config. Expiry date: {self.expiry_date}")
                else:
                    # Create new config with default expiry (development only)
                    self.expiry_date = datetime.strptime(self.DEFAULT_EXPIRY_DATE, '%Y-%m-%d').date()
                    self.license_config = {
                        'expiry_date': self.DEFAULT_EXPIRY_DATE,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'software_version': '1.0.0'
                    }
                    self.save_config()
                    logging.info(f"New license created with expiry date: {self.expiry_date}")
        except Exception as e:
            logging.error(f"Error loading license config: {str(e)}")
            # Fallback to default
            self.expiry_date = datetime.strptime(self.DEFAULT_EXPIRY_DATE, '%Y-%m-%d').date()
    
    def save_config(self):
        """
        Save license config to file.
        Only works in development mode - bundled exe cannot modify license.
        """
        # Prevent saving when running as bundled exe
        if self._is_running_as_exe():
            logging.warning("Cannot save license config when running as bundled executable")
            return
            
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.license_config, f, indent=4)
            logging.info("License config saved successfully")
        except Exception as e:
            logging.error(f"Error saving license config: {str(e)}")
    
    def set_expiry_date(self, expiry_date_str):
        """
        Set a new expiry date for the software.
        Only works in development mode - bundled exe cannot modify license.
        
        Args:
            expiry_date_str (str): Expiry date in YYYY-MM-DD format
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Prevent modification when running as bundled exe
        if self._is_running_as_exe():
            logging.warning("Cannot modify expiry date when running as bundled executable")
            return False
            
        try:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            self.expiry_date = expiry_date
            self.license_config['expiry_date'] = expiry_date_str
            self.license_config['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save_config()
            logging.info(f"Expiry date updated to: {expiry_date}")
            return True
        except ValueError as e:
            logging.error(f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
            return False
    
    def get_days_until_expiry(self):
        """
        Get number of days until software expires.
        
        Returns:
            int: Number of days remaining (negative if already expired)
        """
        today = datetime.now().date()
        remaining_days = (self.expiry_date - today).days
        return remaining_days
    
    def is_expired(self):
        """
        Check if software license has expired.
        
        Returns:
            bool: True if expired, False otherwise
        """
        return self.get_days_until_expiry() < 0
    
    def get_expiry_status(self):
        """
        Get detailed expiry status with warning levels.
        
        Returns:
            dict: Status information with keys:
                - is_expired: bool
                - days_remaining: int
                - status_level: str ('OK', 'WARNING', 'CRITICAL', 'EXPIRED')
                - message: str
                - expiry_date: str
        """
        days_remaining = self.get_days_until_expiry()
        today = datetime.now().date()
        
        if days_remaining < 0:
            status_level = 'EXPIRED'
            message = f"🔴 SOFTWARE EXPIRED! Expired on {self.expiry_date}"
        elif days_remaining <= self.CRITICAL_WARNING_DAYS:
            status_level = 'CRITICAL'
            message = f"🔴 CRITICAL: Software expires in {days_remaining} days ({self.expiry_date})"
        elif days_remaining <= self.EARLY_WARNING_DAYS:
            status_level = 'WARNING'
            message = f"🟡 WARNING: Software expires in {days_remaining} days ({self.expiry_date})"
        else:
            status_level = 'OK'
            message = f"✓ Software active. Expires in {days_remaining} days ({self.expiry_date})"
        
        # Show notification only for WARNING, CRITICAL, and EXPIRED statuses
        should_show_warning = status_level in ['WARNING', 'CRITICAL', 'EXPIRED']
        
        return {
            'is_expired': days_remaining < 0,
            'days_remaining': days_remaining,
            'status_level': status_level,
            'message': message,
            'expiry_date': str(self.expiry_date),
            'should_show_warning': should_show_warning
        }
    
    def get_expiry_info_text(self):
        """
        Get formatted expiry information for display.
        
        Returns:
            str: Formatted expiry information
        """
        status = self.get_expiry_status()
        
        info_lines = [
            "=" * 60,
            "📋 SOFTWARE LICENSE INFORMATION",
            "=" * 60,
            f"Expiry Date:        {status['expiry_date']}",
            f"Days Remaining:     {status['days_remaining']} days",
            f"Status:             {status['status_level']}",
            f"Message:            {status['message']}",
            "=" * 60
        ]
        
        return "\n".join(info_lines)
    
    def show_expiry_warning(self, parent_window=None):
        """
        Show expiry warning dialog.
        
        Args:
            parent_window: Parent Tkinter window (optional)
            
        Returns:
            bool: True if user wants to continue, False to quit
        """
        from tkinter import messagebox
        
        status = self.get_expiry_status()
        
        if status['is_expired']:
            messagebox.showerror(
                "Software Expired",
                f"❌ This software has expired.\n\n"
                f"Expiry Date: {status['expiry_date']}\n"
                f"Days Since Expiry: {abs(status['days_remaining'])} days\n\n"
                f"Please contact the software provider to renew your license.",
                parent=parent_window
            )
            return False
        
        elif status['status_level'] == 'CRITICAL':
            result = messagebox.showwarning(
                "Critical: Software Expiring Soon",
                f"⚠️  Your software will expire very soon!\n\n"
                f"Expiry Date: {status['expiry_date']}\n"
                f"Days Remaining: {status['days_remaining']} days\n\n"
                f"Please renew your license soon to avoid interruption.\n\n"
                f"Click OK to continue, or Cancel to exit.",
                parent=parent_window
            )
            return result is not None
        
        elif status['status_level'] == 'WARNING':
            result = messagebox.showinfo(
                "Notice: Software Expiring",
                f"ℹ️  Your software will expire soon.\n\n"
                f"Expiry Date: {status['expiry_date']}\n"
                f"Days Remaining: {status['days_remaining']} days\n\n"
                f"Please plan to renew your license.\n\n"
                f"Click OK to continue.",
                parent=parent_window
            )
            return True
        
        return True
    
    def validate_license(self):
        """
        Validate license on startup.
        
        Returns:
            bool: True if software can run, False if expired
        """
        return not self.is_expired()


# Convenience function for easy access
def get_license_manager():
    """Get the license manager instance."""
    return LicenseManager()
