"""
MAC Address Authentication Module
Restricts application usage to authorized MAC addresses only.
"""

import uuid
import json
import os
import logging
import hashlib
import urllib.request
import urllib.error
import subprocess
import threading
from datetime import datetime
from typing import List, Optional, Tuple


class MACAuthenticator:
    """
    Handles MAC address-based authentication for the application.
    Supports both whitelist mode and license binding mode.
    """
    
    def __init__(self, config_file="mac_config.json", github_url=None, whitelist_file="mac_whitelist.json", auto_sync_github=True):
        """
        Initialize MAC authenticator.
        
        Args:
            config_file (str): Path to MAC address configuration file
            github_url (str): GitHub raw URL for mac_whitelist.json (optional)
            whitelist_file (str): Path to local GitHub whitelist file
            auto_sync_github (bool): Automatically push whitelist to GitHub on authorization
        """
        self.config_file = config_file
        self.whitelist_file = whitelist_file
        self.auto_sync_github = auto_sync_github
        self.config_existed_before = os.path.exists(config_file)  # Track if config existed
        self.github_url = github_url or "https://raw.githubusercontent.com/Sabeeh1996/FBR-INVOICE-Search-Match/develop/mac_whitelist.json"
        self.config = self._load_config()
        self.current_mac = self.get_mac_address()
        self.current_mac_hash = self._hash_mac(self.current_mac) if self.current_mac else None
        self.is_first_run = False  # Will be set to True if this is first authorization
        
    def get_mac_address(self) -> Optional[str]:
        """
        Get the MAC address of the primary network interface.
        
        Returns:
            str: MAC address in format XX:XX:XX:XX:XX:XX or None if unavailable
        """
        try:
            # Get MAC address using uuid.getnode()
            mac_num = uuid.getnode()
            
            # Convert to standard MAC format
            mac_hex = ':'.join(['{:02x}'.format((mac_num >> elements) & 0xff)
                               for elements in range(0, 8*6, 8)][::-1])
            
            # Validate it's not a fake MAC (all zeros or all Fs)
            if mac_hex == '00:00:00:00:00:00' or mac_hex == 'ff:ff:ff:ff:ff:ff':
                logging.warning("Invalid MAC address detected")
                return self._get_mac_fallback()
            
            return mac_hex.upper()
            
        except Exception as e:
            logging.error(f"Error getting MAC address: {str(e)}")
            return self._get_mac_fallback()
    
    def _get_mac_fallback(self) -> Optional[str]:
        """
        Fallback method to get MAC address using alternative methods.
        
        Returns:
            str: MAC address or None
        """
        try:
            import subprocess
            import re
            
            if os.name == 'nt':  # Windows
                # Use getmac command
                output = subprocess.check_output("getmac", shell=True).decode()
                # Extract first MAC address
                mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
                if mac_match:
                    return mac_match.group(0).upper().replace('-', ':')
            else:  # Linux/Mac
                # Use ifconfig or ip command
                try:
                    output = subprocess.check_output("ifconfig", shell=True).decode()
                except:
                    output = subprocess.check_output("ip link", shell=True).decode()
                
                mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
                if mac_match:
                    return mac_match.group(0).upper().replace('-', ':')
                    
        except Exception as e:
            logging.error(f"Fallback MAC address retrieval failed: {str(e)}")
        
        return None
    
    def _hash_mac(self, mac_address: str) -> str:
        """
        Create a hash of MAC address for secure storage.
        
        Args:
            mac_address (str): MAC address to hash
            
        Returns:
            str: SHA256 hash of MAC address
        """
        return hashlib.sha256(mac_address.encode()).hexdigest()
    
    def _load_config(self) -> dict:
        """
        Load MAC address configuration from file.
        
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            "mode": "whitelist",  # Options: "whitelist", "binding", "disabled"
            "authorized_macs": [],  # List of authorized MAC address hashes
            "bound_mac": None,  # MAC address bound to license (if binding mode)
            "allow_first_run": True,  # Auto-authorize first MAC address
            "show_mac_info": True  # Show MAC address in error messages for admin
        }
        
        if not os.path.exists(self.config_file):
            # Create default config
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            logging.error(f"Error loading MAC config: {str(e)}")
            return default_config
    
    def _save_config(self, config: dict = None):
        """
        Save MAC address configuration to file.
        
        Args:
            config (dict): Configuration to save. If None, saves current config.
        """
        try:
            config_to_save = config if config else self.config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving MAC config: {str(e)}")
    
    def _update_github_whitelist_file(self, mac_hash: str) -> bool:
        """
        Update local GitHub whitelist file with new device entry.
        Uses status-based authorization (active/revoked).
        
        Args:
            mac_hash (str): MAC address hash to add
            
        Returns:
            bool: True if successful
        """
        try:
            # Load existing whitelist
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r') as f:
                    whitelist = json.load(f)
            else:
                whitelist = {
                    "_comment": "GitHub-hosted MAC Address Whitelist - Edit this file to control device access",
                    "_instructions": [
                        "To AUTHORIZE: Set status to 'active'",
                        "To REVOKE: Set status to 'revoked'",
                        "Empty devices array = first-time use (auto-authorization enabled)",
                        "Status values: 'active' = authorized, 'revoked' = blocked",
                        "mac_address field is for admin reference (readable MAC address)",
                        "mac_hash field is used for device matching (do not edit)"
                    ],
                    "mode": "github_whitelist",
                    "devices": [],
                    "last_updated": "",
                    "updated_by": "auto-authorize"
                }
            
            # Migrate old format to new format if needed
            if 'authorized_macs' in whitelist and 'devices' not in whitelist:
                whitelist['devices'] = [
                    {
                        "mac_address": "[Hash only - MAC unknown]",
                        "mac_hash": mac,
                        "status": "active",
                        "authorized_date": whitelist.get('last_updated', ''),
                        "notes": "Migrated from old format"
                    }
                    for mac in whitelist.get('authorized_macs', [])
                ]
                del whitelist['authorized_macs']
            
            # Check if MAC already exists
            devices = whitelist.get('devices', [])
            existing_device = next((d for d in devices if d.get('mac_hash') == mac_hash), None)
            
            if existing_device:
                # Update existing device
                if existing_device.get('status') == 'revoked':
                    logging.warning(f"Device was previously revoked, re-activating: {self.current_mac}")
                existing_device['status'] = 'active'
                existing_device['last_updated'] = datetime.now().isoformat()
            else:
                # Add new device
                devices.append({
                    "mac_address": self.current_mac,  # Actual MAC for admin visibility
                    "mac_hash": mac_hash,  # Hash for comparison
                    "status": "active",
                    "authorized_date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "notes": "Auto-authorized on first run"
                })
                whitelist['devices'] = devices
            
            whitelist['last_updated'] = datetime.now().isoformat()
            whitelist['updated_by'] = 'auto-authorize'
            
            # Save updated whitelist
            with open(self.whitelist_file, 'w') as f:
                json.dump(whitelist, f, indent=2)
            
            logging.info(f"Added MAC to GitHub whitelist file: {self.whitelist_file}")
            
            # Auto-sync to GitHub if enabled
            if self.auto_sync_github:
                self._sync_to_github_async()
            else:
                logging.info(f"→ Run 'python sync_whitelist.py' to sync to GitHub")
            
            return True
            
        except Exception as e:
            logging.error(f"Error updating GitHub whitelist file: {str(e)}")
            return False
    
    def _sync_to_github_async(self):
        """
        Asynchronously sync whitelist to GitHub in background.
        Runs git commands in separate thread to avoid blocking app startup.
        Handles pull/merge automatically before pushing.
        """
        def sync_task():
            try:
                logging.info("🔄 Starting automatic GitHub sync...")
                
                # Check if git is available
                subprocess.run(['git', '--version'], capture_output=True, check=True)
                
                cwd = os.path.dirname(os.path.abspath(__file__))
                
                # Pull latest changes first to avoid conflicts
                logging.info("   Pulling latest changes from GitHub...")
                pull_result = subprocess.run(
                    ['git', 'pull', 'origin', 'develop'],
                    capture_output=True,
                    text=True,
                    cwd=cwd
                )
                
                if pull_result.returncode != 0 and 'Already up to date' not in pull_result.stdout:
                    logging.warning(f"   Pull had issues (continuing anyway): {pull_result.stderr}")
                
                # Add file
                subprocess.run(
                    ['git', 'add', self.whitelist_file],
                    capture_output=True,
                    check=True,
                    cwd=cwd
                )
                
                # Commit (may fail if no changes after pull - that's OK)
                commit_result = subprocess.run(
                    ['git', 'commit', '-m', 'Auto-authorize new device [automated]'],
                    capture_output=True,
                    text=True,
                    cwd=cwd
                )
                
                # Check if there's anything to push
                if 'nothing to commit' in commit_result.stdout or commit_result.returncode != 0:
                    # Check if already committed but not pushed
                    status_result = subprocess.run(
                        ['git', 'status', '-sb'],
                        capture_output=True,
                        text=True,
                        cwd=cwd
                    )
                    
                    if 'ahead' not in status_result.stdout:
                        logging.info("✅ Whitelist already synced to GitHub (no changes needed)")
                        return
                
                # Push
                result = subprocess.run(
                    ['git', 'push', 'origin', 'develop'],
                    capture_output=True,
                    text=True,
                    cwd=cwd
                )
                
                if result.returncode == 0:
                    logging.info("✅ Whitelist automatically synced to GitHub!")
                    logging.info("   All devices will see this authorization on next startup")
                else:
                    logging.warning(f"⚠️ Auto-sync push failed: {result.stderr.split('error:')[0] if 'error:' in result.stderr else result.stderr[:100]}")
                    logging.info("   Run 'python sync_whitelist.py' manually to sync")
                    
            except subprocess.CalledProcessError as e:
                logging.warning(f"⚠️ Auto-sync to GitHub failed: {e}")
                logging.info("   This is normal if git is not configured or network unavailable")
                logging.info("   Run 'python sync_whitelist.py' manually when ready")
            except FileNotFoundError:
                logging.warning("⚠️ Git not found - cannot auto-sync to GitHub")
                logging.info("   Run 'python sync_whitelist.py' manually after installing git")
            except Exception as e:
                logging.warning(f"⚠️ Unexpected error during auto-sync: {e}")
        
        # Run sync in background thread
        sync_thread = threading.Thread(target=sync_task, daemon=True)
        sync_thread.start()
    
    def _fetch_github_whitelist(self) -> Optional[dict]:
        """
        Fetch MAC whitelist from GitHub repository.
        
        Returns:
            dict: GitHub whitelist config or None if fetch fails
        """
        try:
            logging.info(f"Fetching MAC whitelist from GitHub...")
            
            # Add timeout and user agent
            req = urllib.request.Request(
                self.github_url,
                headers={'User-Agent': 'FBR-Invoice-Checker'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                logging.info(f"Successfully fetched GitHub whitelist (mode: {data.get('mode', 'unknown')})")
                return data
                
        except urllib.error.URLError as e:
            logging.warning(f"Failed to fetch GitHub whitelist (network error): {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse GitHub whitelist JSON: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching GitHub whitelist: {str(e)}")
            return None
    
    def _merge_github_config(self, github_config: dict):
        """
        Merge GitHub whitelist with local config.
        GitHub settings take ABSOLUTE precedence for authorization.
        Uses status-based authorization (active/revoked).
        
        Args:
            github_config (dict): Configuration from GitHub
        """
        if github_config.get('mode') == 'github_whitelist':
            # Use GitHub whitelist mode - GitHub has absolute control
            self.config['mode'] = 'whitelist'
            
            # Extract devices and build authorized MAC list (only active devices)
            devices = github_config.get('devices', [])
            
            # If devices array is empty, allow first-run auto-authorization
            if not devices:
                self.config['authorized_macs'] = []
                self.config['allow_first_run'] = True
                logging.info(f"✓ GitHub whitelist is empty - first-run auto-authorization enabled")
                return
            
            # Build list of active MACs only
            active_macs = [
                device['mac_hash'] 
                for device in devices 
                if device.get('status') == 'active'
            ]
            
            self.config['authorized_macs'] = active_macs
            self.config['allow_first_run'] = False  # Disable auto-auth when GitHub has devices
            
            total_devices = len(devices)
            active_count = len(active_macs)
            revoked_count = total_devices - active_count
            
            logging.info(f"✓ Using GitHub whitelist (authoritative): {active_count} active, {revoked_count} revoked")
            
            # Check if current MAC is revoked
            current_device = next((d for d in devices if d.get('mac_hash') == self.current_mac_hash), None)
            if current_device:
                if current_device.get('status') == 'revoked':
                    logging.error(f"❌ Device status: REVOKED by administrator")
                    logging.error(f"   Device was explicitly revoked on GitHub")
                elif current_device.get('status') != 'active':
                    logging.warning(f"⚠️  Device status: {current_device.get('status')} (unknown status)")
            elif total_devices > 0:
                logging.warning(f"⚠️  Device MAC not found in GitHub whitelist - access will be denied")
                
        elif github_config.get('mode') in ['whitelist', 'binding', 'disabled']:
            # Direct mode override (backward compatibility)
            self.config['mode'] = github_config['mode']
            if 'authorized_macs' in github_config:
                self.config['authorized_macs'] = github_config['authorized_macs']
            if 'bound_mac' in github_config:
                self.config['bound_mac'] = github_config['bound_mac']
    
    def is_authorized(self) -> Tuple[bool, str]:
        """
        Check if current MAC address is authorized to run the application.
        ALWAYS fetches latest whitelist from GitHub first (authoritative source).
        Only falls back to local file if GitHub is completely unavailable.
        
        Returns:
            tuple: (is_authorized: bool, message: str)
        """
        if not self.current_mac:
            return False, "Unable to detect MAC address"
        
        # Try to fetch GitHub whitelist first (AUTHORITATIVE)
        github_config = self._fetch_github_whitelist()
        
        if github_config:
            # GitHub is available - use it and save locally for offline use
            self._merge_github_config(github_config)
            logging.info("✓ Using GitHub whitelist (authoritative - online)")
            
            # Save GitHub version locally for offline fallback
            try:
                with open(self.whitelist_file, 'w') as f:
                    json.dump(github_config, f, indent=2)
                logging.info("  → Saved GitHub whitelist locally for offline use")
            except Exception as e:
                logging.warning(f"Could not save GitHub whitelist locally: {e}")
                
        else:
            # GitHub unavailable - try local whitelist file as backup
            if os.path.exists(self.whitelist_file):
                try:
                    with open(self.whitelist_file, 'r') as f:
                        local_whitelist = json.load(f)
                    
                    if local_whitelist.get('mode') == 'github_whitelist':
                        logging.warning("⚠️  GitHub unavailable - using CACHED local whitelist")
                        logging.warning("   Status may be outdated - check GitHub connectivity")
                        self._merge_github_config(local_whitelist)
                    else:
                        logging.info("Using local MAC configuration (GitHub unavailable)")
                except Exception as e:
                    logging.error(f"Error loading local whitelist: {e}")
                    logging.info("Using local MAC configuration (GitHub unavailable)")
            else:
                logging.info("Using local MAC configuration (GitHub unavailable)")
        
        mode = self.config.get("mode", "whitelist")
        
        # If disabled, allow all
        if mode == "disabled":
            logging.info("MAC authentication is disabled")
            return True, "MAC authentication disabled"
        
        # Whitelist mode
        if mode == "whitelist":
            return self._check_whitelist()
        
        # Binding mode
        elif mode == "binding":
            return self._check_binding()
        
        else:
            logging.error(f"Unknown MAC authentication mode: {mode}")
            return False, "Invalid authentication mode"
    
    def _check_whitelist(self) -> Tuple[bool, str]:
        """
        Check if MAC address is in whitelist.
        GitHub whitelist has absolute authority - overrides local authorization.
        
        Returns:
            tuple: (is_authorized: bool, message: str)
        """
        authorized_macs = self.config.get("authorized_macs", [])
        
        # If whitelist is empty and allow_first_run is True, auto-authorize
        # Note: allow_first_run is disabled when GitHub whitelist is active
        if not authorized_macs and self.config.get("allow_first_run", True):
            logging.info(f"First run detected - auto-authorizing MAC: {self.current_mac}")
            self.is_first_run = True  # Mark as first run
            self.authorize_current_mac()
            return True, "Auto-authorized (first run)"
        
        # Check if current MAC is in whitelist
        if self.current_mac_hash in authorized_macs:
            logging.info(f"✓ MAC address authorized: {self.current_mac}")
            return True, "MAC address authorized"
        
        # Not authorized - could be never authorized or revoked by admin
        mac_info = f" (MAC: {self.current_mac})" if self.config.get("show_mac_info", True) else ""
        logging.error(f"❌ ACCESS DENIED: {self.current_mac}")
        logging.error(f"   Device not in active whitelist - may be revoked or never authorized")
        return False, f"⚠️  Access Denied\n\nThis device is not authorized{mac_info}\n\nReason: Device not in active whitelist\n(Status may be 'revoked' or never authorized)\n\nContact administrator for access."
    
    def _check_binding(self) -> Tuple[bool, str]:
        """
        Check if MAC address matches bound MAC.
        
        Returns:
            tuple: (is_authorized: bool, message: str)
        """
        bound_mac = self.config.get("bound_mac")
        
        # If no MAC is bound yet, bind current MAC
        if not bound_mac:
            loggiis_first_run = True  # Mark as first run
            self.ng.info(f"Binding license to MAC: {self.current_mac}")
            self.config["bound_mac"] = self.current_mac_hash
            self._save_config()
            return True, "License bound to this device"
        
        # Check if current MAC matches bound MAC
        if self.current_mac_hash == bound_mac:
            logging.info(f"MAC address matches bound license: {self.current_mac}")
            return True, "Device authorized (license bound)"
        
        # Not authorized
        mac_info = f" (MAC: {self.current_mac})" if self.config.get("show_mac_info", True) else ""
        logging.warning(f"MAC address does not match bound license: {self.current_mac}")
        return False, f"License is bound to a different device{mac_info}"
    
    def authorize_current_mac(self) -> bool:
        """
        Add current MAC address to authorized list.
        Also updates local GitHub whitelist file for easy syncing.
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.current_mac_hash:
                return False
            
            if self.current_mac_hash not in self.config["authorized_macs"]:
                self.config["authorized_macs"].append(self.current_mac_hash)
                self._save_config()
                logging.info(f"Authorized MAC address: {self.current_mac}")
                
                # Also update GitHub whitelist file (will auto-sync if enabled)
                self._update_github_whitelist_file(self.current_mac_hash)
            
            return True
        except Exception as e:
            logging.error(f"Error authorizing MAC: {str(e)}")
            return False
    
    def authorize_mac(self, mac_address: str) -> bool:
        """
        Add specific MAC address to authorized list.
        
        Args:
            mac_address (str): MAC address to authorize
            
        Returns:
            bool: True if successful
        """
        try:
            mac_hash = self._hash_mac(mac_address.upper())
            
            if mac_hash not in self.config["authorized_macs"]:
                self.config["authorized_macs"].append(mac_hash)
                self._save_config()
                logging.info(f"Authorized MAC address: {mac_address}")
            
            return True
        except Exception as e:
            logging.error(f"Error authorizing MAC: {str(e)}")
            return False
    
    def revoke_mac(self, mac_address: str) -> bool:
        """
        Remove specific MAC address from authorized list.
        
        Args:
            mac_address (str): MAC address to revoke
            
        Returns:
            bool: True if successful
        """
        try:
            mac_hash = self._hash_mac(mac_address.upper())
            
            if mac_hash in self.config["authorized_macs"]:
                self.config["authorized_macs"].remove(mac_hash)
                self._save_config()
                logging.info(f"Revoked MAC address: {mac_address}")
                return True
            
            return False
        except Exception as e:
            logging.error(f"Error revoking MAC: {str(e)}")
            return False
    
    def get_auth_info(self) -> dict:
        """
        Get authentication information for display.
        
        Returns:
            dict: Authentication info
        """
        return {
            "current_mac": self.current_mac,
            "mode": self.config.get("mode", "unknown"),
            "is_authorized": self.is_authorized()[0],
            "authorized_count": len(self.config.get("authorized_macs", []))
        }
    
    def set_mode(self, mode: str):
        """
        Set authentication mode.
        
        Args:
            mode (str): Authentication mode ("whitelist", "binding", "disabled")
        """
        if mode in ["whitelist", "binding", "disabled"]:
            self.config["mode"] = mode
            self._save_config()
            logging.info(f"MAC authentication mode set to: {mode}")
        else:
            logging.error(f"Invalid MAC authentication mode: {mode}")


# Convenience function for quick check
def check_mac_authorization(config_file="mac_config.json") -> Tuple[bool, str, str]:
    """
    Quick check if current device is authorized.
    
    Args:
        config_file (str): Path to configuration file
        
    Returns:
        tuple: (is_authorized: bool, message: str, mac_address: str)
    """
    auth = MACAuthenticator(config_file)
    is_auth, message = auth.is_authorized()
    return is_auth, message, auth.current_mac
