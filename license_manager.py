"""
License Manager Module
Handles software expiry management with GitHub-based central control.
Fetches license from GitHub (authoritative) with local fallback.
"""

import json
import os
import sys
import logging
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path


class LicenseManager:
    """
    Manages software license/expiry system with GitHub-based control.
    Fetches license status from GitHub (authoritative source).
    """
    
    # GitHub Personal Access Token for authentication
    GITHUB_TOKEN = "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"
    
    # GitHub URL for license config
    GITHUB_LICENSE_URL = "https://raw.githubusercontent.com/Sabeeh1996/FBR-INVOICE-Search-Match/develop/license_config.json"
    
    # Local cache file for offline fallback
    GITHUB_CACHE_FILE = "github_license_config.json"
    
    # Legacy local config file
    CONFIG_FILE = "license_config.json"
    
    # Default expiry date - can be set to any future date
    DEFAULT_EXPIRY_DATE = "2026-12-31"  # YYYY-MM-DD format
    
    # Days before expiry to show warning
    EARLY_WARNING_DAYS = 15
    
    # Days before expiry to show critical warning
    CRITICAL_WARNING_DAYS = 7
    
    def __init__(self):
        """Initialize the license manager."""
        self.expiry_date = None
        self.license_config = None
        self.license_status = "unknown"
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
    
    def _fetch_github_license(self):
        """
        Fetch license configuration from GitHub repository.
        Uses GitHub API for real-time access (no cache delays).
        
        Returns:
            dict: GitHub license config or None if fetch fails
        """
        import base64
        
        try:
            # Convert raw URL to API URL for no-cache access
            if 'raw.githubusercontent.com' in self.GITHUB_LICENSE_URL:
                parts = self.GITHUB_LICENSE_URL.replace('https://raw.githubusercontent.com/', '').split('/')
                if len(parts) >= 4:
                    user, repo, branch = parts[0], parts[1], parts[2]
                    file_path = '/'.join(parts[3:])
                    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}?ref={branch}"
                    
                    logging.info(f"Fetching license from GitHub API...")
                    
                    req = urllib.request.Request(
                        api_url,
                        headers={
                            'User-Agent': 'FBR-Invoice-Checker',
                            'Accept': 'application/vnd.github.v3+json',
                            'Authorization': f'token {self.GITHUB_TOKEN}'
                        }
                    )
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        api_response = json.loads(response.read().decode())
                        # Decode base64 content
                        content = base64.b64decode(api_response['content']).decode('utf-8')
                        data = json.loads(content)
                        logging.info(f"✓ License fetched from GitHub (mode: {data.get('mode', 'unknown')})")
                        return data
            
            # Fallback to raw URL
            logging.info(f"Fetching license from GitHub raw URL...")
            req = urllib.request.Request(
                self.GITHUB_LICENSE_URL,
                headers={'User-Agent': 'FBR-Invoice-Checker'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                logging.info(f"✓ License fetched from GitHub")
                return data
                
        except urllib.error.URLError as e:
            logging.warning(f"Failed to fetch GitHub license (network error): {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse GitHub license JSON: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching GitHub license: {str(e)}")
            return None
    
    def _get_writable_cache_path(self):
        """Get writable path for license cache (AppData when running as exe)."""
        if self._is_running_as_exe():
            from app_data_manager import get_writable_file_path
            return get_writable_file_path(self.GITHUB_CACHE_FILE)
        else:
            return self.GITHUB_CACHE_FILE
    
    def load_or_create_config(self):
        """
        Load license config from GitHub (authoritative source).
        Falls back to local cached file if GitHub is unavailable.
        Updates local cache for offline use.
        """
        # Try to fetch from GitHub first (AUTHORITATIVE)
        github_license = self._fetch_github_license()
        
        if github_license:
            # GitHub is available - use it and update local cache
            self._apply_github_license(github_license)
            logging.info("✓ Using GitHub license (authoritative - online)")
            
            # Save GitHub version locally for offline fallback
            try:
                cache_path = self._get_writable_cache_path()
                with open(cache_path, 'w') as f:
                    json.dump(github_license, f, indent=2)
                logging.info("  → Saved GitHub license locally for offline use")
            except Exception as e:
                logging.warning(f"Could not save GitHub license cache: {e}")
        else:
            # GitHub unavailable - try local cache file
            cache_path = self._get_writable_cache_path()
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r') as f:
                        cached_license = json.load(f)
                    
                    if cached_license.get('mode') == 'github_license':
                        logging.warning("⚠️  GitHub unavailable - using CACHED license")
                        logging.warning("   License status may be outdated - check connectivity")
                        self._apply_github_license(cached_license)
                    else:
                        logging.info("Using local license config (GitHub unavailable)")
                        self._load_local_config()
                except Exception as e:
                    logging.error(f"Error loading cached license: {e}")
                    self._load_local_config()
            else:
                # No GitHub and no cache - use local config file
                logging.info("Using local license config (GitHub unavailable)")
                self._load_local_config()
    
    def _apply_github_license(self, github_license):
        """
        Apply license configuration from GitHub.
        
        Args:
            github_license (dict): License configuration from GitHub
        """
        if github_license.get('mode') == 'github_license':
            self.license_config = github_license
            license_info = github_license.get('license_info', {})
            
            # Get license status
            self.license_status = license_info.get('status', 'unknown')
            
            # Get expiry date
            expiry_str = license_info.get('expiry_date', self.DEFAULT_EXPIRY_DATE)
            try:
                self.expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
            except:
                logging.warning(f"Invalid expiry date format: {expiry_str}")
                self.expiry_date = datetime.strptime(self.DEFAULT_EXPIRY_DATE, '%Y-%m-%d').date()
            
            # Update warning thresholds from GitHub config
            self.EARLY_WARNING_DAYS = github_license.get('warning_days', self.EARLY_WARNING_DAYS)
            self.CRITICAL_WARNING_DAYS = github_license.get('critical_days', self.CRITICAL_WARNING_DAYS)
            
            logging.info(f"  Status: {self.license_status}")
            logging.info(f"  Expiry: {self.expiry_date}")
            logging.info(f"  Type: {license_info.get('license_type', 'standard')}")
        else:
            logging.warning(f"Unknown license mode: {github_license.get('mode')}")
            self._load_local_config()
    
    def _load_local_config(self):
        """
        Load license from local config file (fallback).
        When running as exe, loads from bundled resource.
        """
        try:
            # When running as exe, load from bundled resource
            if self._is_running_as_exe():
                config_path = self._get_resource_path(self.CONFIG_FILE)
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.license_config = json.load(f)
                    self.expiry_date = datetime.strptime(
                        self.license_config.get('expiry_date', self.DEFAULT_EXPIRY_DATE),
                        '%Y-%m-%d'
                    ).date()
                    self.license_status = "active"  # Assume active for local config
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
                        self.license_status = "active"  # Assume active for local config
                        logging.info(f"License loaded from local config. Expiry date: {self.expiry_date}")
                else:
                    # Create new config with default expiry (development only)
                    self.expiry_date = datetime.strptime(self.DEFAULT_EXPIRY_DATE, '%Y-%m-%d').date()
                    self.license_status = "active"
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
            self.license_status = "active"
    
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
        Checks both status (from GitHub) and expiry date.
        
        Returns:
            bool: True if expired, False otherwise
        """
        # Check if status is revoked or expired (GitHub control)
        if self.license_status in ['revoked', 'expired']:
            return True
        
        # Check date-based expiry
        return self.get_days_until_expiry() < 0
    
    def get_expiry_status(self):
        """
        Get detailed expiry status with warning levels.
        Checks both GitHub status and expiry date.
        
        Returns:
            dict: Status information with keys:
                - is_expired: bool
                - days_remaining: int
                - status_level: str ('OK', 'WARNING', 'CRITICAL', 'EXPIRED', 'REVOKED')
                - message: str
                - expiry_date: str
                - license_status: str
        """
        days_remaining = self.get_days_until_expiry()
        today = datetime.now().date()
        
        # Check GitHub status first (takes precedence)
        if self.license_status == 'revoked':
            status_level = 'REVOKED'
            message = f"🔴 LICENSE REVOKED! Contact administrator."
            is_expired = True
        elif self.license_status == 'expired':
            status_level = 'EXPIRED'
            message = f"🔴 LICENSE EXPIRED! Marked as expired by administrator."
            is_expired = True
        elif days_remaining < 0:
            status_level = 'EXPIRED'
            message = f"🔴 SOFTWARE EXPIRED! Expired on {self.expiry_date}"
            is_expired = True
        elif days_remaining <= self.CRITICAL_WARNING_DAYS:
            status_level = 'CRITICAL'
            message = f"🔴 CRITICAL: Software expires in {days_remaining} days ({self.expiry_date})"
            is_expired = False
        elif days_remaining <= self.EARLY_WARNING_DAYS:
            status_level = 'WARNING'
            message = f"🟡 WARNING: Software expires in {days_remaining} days ({self.expiry_date})"
            is_expired = False
        else:
            status_level = 'OK'
            message = f"✓ Software active. Expires in {days_remaining} days ({self.expiry_date})"
            is_expired = False
        
        # Show notification only for WARNING, CRITICAL, EXPIRED, and REVOKED statuses
        should_show_warning = status_level in ['WARNING', 'CRITICAL', 'EXPIRED', 'REVOKED']
        
        return {
            'is_expired': is_expired,
            'days_remaining': days_remaining,
            'status_level': status_level,
            'message': message,
            'expiry_date': str(self.expiry_date),
            'license_status': self.license_status,
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
        Handles both GitHub status and date-based expiry.
        
        Args:
            parent_window: Parent Tkinter window (optional)
            
        Returns:
            bool: True if user wants to continue, False to quit
        """
        from tkinter import messagebox
        
        status = self.get_expiry_status()
        
        # Handle revoked status (GitHub control)
        if status['status_level'] == 'REVOKED':
            messagebox.showerror(
                "License Revoked",
                f"🔴 This software license has been REVOKED.\n\n"
                f"License Status: {status['license_status']}\n"
                f"Expiry Date: {status['expiry_date']}\n\n"
                f"Please contact the software provider.\n"
                f"The administrator has disabled this license.",
                parent=parent_window
            )
            return False
        
        # Handle expired status
        if status['is_expired']:
            expired_reason = "marked as expired" if status['license_status'] == 'expired' else "date expired"
            messagebox.showerror(
                "Software Expired",
                f"❌ This software has expired.\n\n"
                f"Expiry Date: {status['expiry_date']}\n"
                f"Days Since Expiry: {abs(status['days_remaining'])} days\n"
                f"Reason: {expired_reason}\n\n"
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
