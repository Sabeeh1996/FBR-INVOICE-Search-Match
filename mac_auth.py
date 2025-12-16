"""
MAC Address Authentication Module
Restricts application usage to authorized MAC addresses only.
"""

import uuid
import json
import os
import sys
import logging
import hashlib
import urllib.request
import urllib.error
import subprocess
import threading
from datetime import datetime
from typing import List, Optional, Tuple
from app_data_manager import get_app_data_dir, ensure_writable_copy


def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller.
    When bundled as exe, files are extracted to sys._MEIPASS temp folder.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running in normal Python environment
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def is_running_as_exe():
    """Check if running as PyInstaller bundled executable."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


class MACAuthenticator:
    """
    Handles MAC address-based authentication for the application.
    Supports both whitelist mode and license binding mode.
    """
    
    # GitHub Personal Access Token for authentication
    GITHUB_TOKEN = "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"
    
    def __init__(self, config_file="mac_config.json", github_url=None, whitelist_file="mac_whitelist.json", auto_sync_github=True):
        """
        Initialize MAC authenticator.
        
        Args:
            config_file (str): Path to MAC address configuration file
            github_url (str): GitHub raw URL for mac_whitelist.json (optional)
            whitelist_file (str): Path to local GitHub whitelist file
            auto_sync_github (bool): Automatically push whitelist to GitHub on authorization
        """
        # When running as exe, store ALL writable files in AppData to prevent files appearing in exe directory
        if is_running_as_exe():
            from app_data_manager import get_writable_file_path
            self.config_file = get_writable_file_path(config_file)
            self.whitelist_file = get_writable_file_path(whitelist_file)
            logging.info(f"Exe mode: Using AppData for MAC files")
            logging.info(f"Config: {self.config_file}")
            logging.info(f"Whitelist: {self.whitelist_file}")
        else:
            self.config_file = config_file
            self.whitelist_file = whitelist_file
        
        self.auto_sync_github = auto_sync_github
        self.config_existed_before = os.path.exists(self.config_file)  # Track if config existed
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
    
    def _get_device_info(self) -> dict:
        """
        Collect comprehensive device information for authorization.
        
        Returns:
            dict: Device information including username and location
        """
        import platform
        import socket
        
        info = {}
        
        # Get PC username
        try:
            info['username'] = os.getlogin()
        except:
            info['username'] = os.environ.get('USERNAME', os.environ.get('USER', 'Unknown'))
        
        # Get computer name
        try:
            info['computer_name'] = socket.gethostname()
        except:
            info['computer_name'] = 'Unknown'
        
        # Get OS information
        try:
            info['os'] = platform.system()
            info['os_version'] = platform.version()
        except:
            info['os'] = 'Unknown'
        
        # === NETWORK DETAILS ===
        try:
            # Get local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info['local_ip'] = s.getsockname()[0]
            s.close()
        except:
            info['local_ip'] = 'Unknown'
        
        # Get all network interfaces
        try:
            import subprocess
            if os.name == 'nt':  # Windows
                # Get network adapter info
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, shell=True)
                output = result.stdout
                
                # Extract DNS servers
                dns_lines = [line.strip() for line in output.split('\n') if 'DNS Servers' in line or 'DNS Server' in line]
                if dns_lines:
                    info['dns_servers'] = dns_lines[0].split(':')[-1].strip()
                
                # Extract default gateway
                gateway_lines = [line.strip() for line in output.split('\n') if 'Default Gateway' in line]
                if gateway_lines:
                    gateway = gateway_lines[0].split(':')[-1].strip()
                    if gateway and gateway != '':
                        info['default_gateway'] = gateway
                
                # Get network adapter names
                adapter_lines = [line for line in output.split('\n') if 'adapter' in line.lower() and ':' in line]
                info['network_adapters'] = [line.split(':')[0].strip() for line in adapter_lines[:3]]
            else:  # Linux/Mac
                # Get network info
                try:
                    result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
                    if 'default via' in result.stdout:
                        info['default_gateway'] = result.stdout.split('default via')[1].split()[0]
                except:
                    pass
        except Exception as e:
            logging.debug(f"Could not get network adapter info: {e}")
        
        # Get FQDN
        try:
            info['fqdn'] = socket.getfqdn()
        except:
            info['fqdn'] = 'Unknown'
        
        # Get geolocation (lat/long) using IP - high precision
        try:
            import urllib.request
            import json
            
            # Try ipapi.co first (higher precision, 6 decimal places)
            try:
                req = urllib.request.Request(
                    'https://ipapi.co/json/',
                    headers={'User-Agent': 'FBR-Invoice-Checker'}
                )
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    geo_data = json.loads(response.read().decode())
                    if 'latitude' in geo_data and 'longitude' in geo_data:
                        # Store with high precision (6-8 decimal places)
                        info['public_ip'] = geo_data.get('ip', 'Unknown')
                        info['latitude'] = round(float(geo_data['latitude']), 8)
                        info['longitude'] = round(float(geo_data['longitude']), 8)
                        info['city'] = geo_data.get('city', 'Unknown')
                        info['country'] = geo_data.get('country_name', 'Unknown')
                        info['isp'] = geo_data.get('org', 'Unknown')
                        info['postal_code'] = geo_data.get('postal', 'Unknown')
                        info['region'] = geo_data.get('region', 'Unknown')
                        info['asn'] = geo_data.get('asn', 'Unknown')
                        info['timezone'] = geo_data.get('timezone', 'Unknown')
                        return info
            except Exception as e:
                logging.debug(f"ipapi.co failed, trying fallback: {str(e)}")
            
            # Fallback to ip-api.com
            req = urllib.request.Request(
                'http://ip-api.com/json/',
                headers={'User-Agent': 'FBR-Invoice-Checker'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                geo_data = json.loads(response.read().decode())
                if geo_data.get('status') == 'success':
                    # Store with maximum available precision
                    info['public_ip'] = geo_data.get('query', 'Unknown')
                    info['latitude'] = round(float(geo_data.get('lat', 0)), 8)
                    info['longitude'] = round(float(geo_data.get('lon', 0)), 8)
                    info['city'] = geo_data.get('city', 'Unknown')
                    info['country'] = geo_data.get('country', 'Unknown')
                    info['isp'] = geo_data.get('isp', 'Unknown')
                    info['postal_code'] = geo_data.get('zip', 'Unknown')
                    info['region'] = geo_data.get('regionName', 'Unknown')
                    info['asn'] = geo_data.get('as', 'Unknown')
                    info['timezone'] = geo_data.get('timezone', 'Unknown')
                else:
                    info['latitude'] = 'Unknown'
                    info['longitude'] = 'Unknown'
        except Exception as e:
            logging.warning(f"Could not fetch geolocation: {str(e)}")
            info['latitude'] = 'Unknown'
            info['longitude'] = 'Unknown'
        
        return info
    
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
        When running as exe, loads from bundled resource (read-only).
        
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
        
        # When running as exe, read from bundled resource
        if is_running_as_exe():
            config_path = get_resource_path(self.config_file)
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    logging.info(f"MAC config loaded from bundled resource")
                    return config
            except Exception as e:
                logging.error(f"Error loading bundled MAC config: {str(e)}")
                return default_config
        else:
            # Development mode: load or create local config file
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
        When running as exe, stores in AppData (hidden from user).
        
        Args:
            mac_hash (str): MAC address hash to add
            
        Returns:
            bool: True if successful
        """
        try:
            # Default whitelist structure
            default_whitelist = {
                "_comment": "GitHub-hosted MAC Address Whitelist - Unlimited Multi-Device Support",
                "_instructions": [
                    "UNLIMITED AUTO-AUTHORIZATION: All new devices are automatically approved",
                    "To BLOCK a device: Set status to 'revoked'",
                    "To ALLOW a device: Set status to 'active' (or just delete the revoked entry)",
                    "Empty devices array = first-time use (unlimited auto-authorization enabled)",
                    "Status values: 'active' = authorized, 'revoked' = blocked",
                    "device_name: Identifies the device (computer-username)",
                    "mac_address: For admin reference (readable MAC address)",
                    "mac_hash: Used for device matching (do not edit)"
                ],
                "mode": "github_whitelist",
                "max_devices": 0,
                "devices": [],
                "last_updated": "",
                "updated_by": "auto-authorize"
            }
            
            # Load existing whitelist
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r') as f:
                    whitelist = json.load(f)
            else:
                whitelist = default_whitelist
            
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
                # Update device info
                device_info = self._get_device_info()
                existing_device.update(device_info)
                logging.info(f"Updated existing device: {existing_device.get('device_name', 'Unnamed Device')}")
            else:
                # Collect device information
                device_info = self._get_device_info()
                
                # Generate device name (computer name + user)
                device_name = f"{device_info.get('computer_name', 'Unknown')}-{device_info.get('username', 'User')}"
                device_count = len(devices) + 1
                
                # Add new device with full information
                new_device = {
                    "device_id": device_count,
                    "device_name": device_name,
                    "mac_address": self.current_mac,  # Actual MAC for admin visibility
                    "mac_hash": mac_hash,  # Hash for comparison
                    "status": "active",
                    "authorized_date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "notes": f"Auto-authorized device #{device_count}"
                }
                new_device.update(device_info)
                devices.append(new_device)
                whitelist['devices'] = devices
                logging.info(f"Added new device #{device_count}: {device_name}")
            
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
        Uses GitHub API directly - works without git installation.
        Perfect for exe distribution on any PC.
        """
        def sync_task():
            try:
                logging.info("🔄 Starting automatic GitHub sync via API...")
                
                # Read the local whitelist file
                if not os.path.exists(self.whitelist_file):
                    logging.warning("⚠️  Local whitelist file not found, skipping sync")
                    return
                
                with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                    whitelist_content = f.read()
                
                # GitHub API endpoint
                api_url = "https://api.github.com/repos/Sabeeh1996/FBR-INVOICE-Search-Match/contents/mac_whitelist.json"
                
                # Get current file SHA (required for update)
                logging.info("   Fetching current file info from GitHub...")
                get_req = urllib.request.Request(
                    api_url + "?ref=develop",
                    headers={
                        'Authorization': f'token {self.GITHUB_TOKEN}',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                )
                
                try:
                    with urllib.request.urlopen(get_req, timeout=10) as response:
                        file_info = json.loads(response.read().decode())
                        current_sha = file_info['sha']
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        # File doesn't exist, create it
                        current_sha = None
                        logging.info("   File doesn't exist, will create new")
                    else:
                        raise
                
                # Encode content to base64
                import base64
                content_base64 = base64.b64encode(whitelist_content.encode('utf-8')).decode('utf-8')
                
                # Prepare update data
                update_data = {
                    "message": "Auto-authorize new device [automated]",
                    "content": content_base64,
                    "branch": "develop"
                }
                
                if current_sha:
                    update_data["sha"] = current_sha
                
                # Push to GitHub
                logging.info("   Uploading to GitHub...")
                put_req = urllib.request.Request(
                    api_url,
                    data=json.dumps(update_data).encode('utf-8'),
                    headers={
                        'Authorization': f'token {self.GITHUB_TOKEN}',
                        'Accept': 'application/vnd.github.v3+json',
                        'Content-Type': 'application/json'
                    },
                    method='PUT'
                )
                
                with urllib.request.urlopen(put_req, timeout=15) as response:
                    result = json.loads(response.read().decode())
                    logging.info("✅ Whitelist automatically synced to GitHub!")
                    logging.info("   All devices will see this authorization on next startup")
                    return
                    
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                logging.warning(f"⚠️ GitHub API sync failed (HTTP {e.code}): {error_body[:200]}")
                logging.info("   Device is authorized locally. Sync will retry on next run.")
            except urllib.error.URLError as e:
                logging.warning(f"⚠️ Network error during GitHub sync: {str(e)}")
                logging.info("   Device is authorized locally. Check internet connection.")
            except Exception as e:
                logging.warning(f"⚠️ Unexpected error during GitHub sync: {str(e)}")
                logging.info("   Device is authorized locally. Sync will retry later.")
        
        # Run sync in background thread
        sync_thread = threading.Thread(target=sync_task, daemon=True)
        sync_thread.start()
    
    def _fetch_github_whitelist(self) -> Optional[dict]:
        """
        Fetch MAC whitelist from GitHub repository.
        Uses GitHub API for real-time access (no cache delays).
        Falls back to raw URL if API fails.
        
        Returns:
            dict: GitHub whitelist config or None if fetch fails
        """
        import base64
        
        # Try GitHub API first (no cache delays)
        try:
            # Convert raw URL to API URL
            # https://raw.githubusercontent.com/USER/REPO/BRANCH/FILE
            # to https://api.github.com/repos/USER/REPO/contents/FILE?ref=BRANCH
            if 'raw.githubusercontent.com' in self.github_url:
                parts = self.github_url.replace('https://raw.githubusercontent.com/', '').split('/')
                if len(parts) >= 4:
                    user, repo, branch = parts[0], parts[1], parts[2]
                    file_path = '/'.join(parts[3:])
                    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}?ref={branch}"
                    
                    logging.info(f"Fetching MAC whitelist from GitHub API...")
                    
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
                        logging.info(f"✓ Successfully fetched from GitHub API (mode: {data.get('mode', 'unknown')})")
                        return data
        except Exception as e:
            logging.warning(f"GitHub API fetch failed: {str(e)}, trying raw URL...")
        
        # Fallback to raw URL
        try:
            logging.info(f"Fetching MAC whitelist from GitHub raw URL...")
            
            req = urllib.request.Request(
                self.github_url,
                headers={
                    'User-Agent': 'FBR-Invoice-Checker',
                    'Authorization': f'token {self.GITHUB_TOKEN}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                logging.info(f"✓ Successfully fetched from GitHub raw URL (mode: {data.get('mode', 'unknown')})")
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
            # Keep allow_first_run=True for unlimited auto-authorization
            # Only devices with status='revoked' will be blocked
            self.config['allow_first_run'] = True
            
            total_devices = len(devices)
            active_count = len(active_macs)
            revoked_count = total_devices - active_count
            
            logging.info(f"✓ Using GitHub whitelist (authoritative): {active_count} active, {revoked_count} revoked")
            if active_count > 0:
                logging.info(f"  → Multi-device mode: {active_count} authorized device(s)")
                # Log device names if available
                for idx, device in enumerate(devices, 1):
                    if device.get('status') == 'active':
                        device_name = device.get('device_name', device.get('computer_name', 'Unknown'))
                        logging.info(f"     Device #{idx}: {device_name}")
            
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
        Supports multiple devices per installation.
        Checks device status from GitHub whitelist to enforce revoked status.
        
        Returns:
            tuple: (is_authorized: bool, message: str)
        """
        authorized_macs = self.config.get("authorized_macs", [])
        
        # Load GitHub whitelist to check actual device status
        github_devices = []
        if os.path.exists(self.whitelist_file):
            try:
                with open(self.whitelist_file, 'r') as f:
                    github_whitelist = json.load(f)
                    github_devices = github_whitelist.get('devices', [])
            except Exception as e:
                logging.warning(f"Could not load GitHub whitelist for status check: {e}")
        
        # Check if current MAC is in whitelist
        if self.current_mac_hash in authorized_macs:
            # CRITICAL: Check if device status is 'revoked' in GitHub whitelist
            current_device = next((d for d in github_devices if d.get('mac_hash') == self.current_mac_hash), None)
            
            if current_device:
                device_status = current_device.get('status', 'unknown')
                device_name = current_device.get('device_name', current_device.get('computer_name', 'Unknown Device'))
                
                # Deny access if status is 'revoked'
                if device_status == 'revoked':
                    logging.error(f"❌ ACCESS DENIED: Device status is REVOKED")
                    logging.error(f"   Device: {device_name}")
                    logging.error(f"   MAC: {self.current_mac}")
                    logging.error(f"   This device was explicitly revoked by administrator")
                    revoked_date = current_device.get('last_updated', 'Unknown')
                    notes = current_device.get('notes', 'No notes available')
                    return False, (f"⚠️  Access Denied - Device Revoked\n\n"
                                 f"Device: {device_name}\n"
                                 f"Status: REVOKED by administrator\n"
                                 f"Date: {revoked_date}\n"
                                 f"Notes: {notes}\n\n"
                                 f"Contact administrator to restore access.")
                
                # Warn if status is not 'active' (unknown status)
                elif device_status != 'active':
                    logging.warning(f"⚠️  Device has unknown status: {device_status}")
                    logging.warning(f"   Allowing access, but status should be 'active' or 'revoked'")
            
            # Count total authorized devices
            device_count = len(authorized_macs)
            logging.info(f"✓ MAC address authorized: {self.current_mac}")
            logging.info(f"✓ Total authorized devices: {device_count}")
            return True, f"MAC address authorized ({device_count} device(s) total)"
        
        # NEW DEVICE - Check if it was previously revoked before auto-authorizing
        current_device = next((d for d in github_devices if d.get('mac_hash') == self.current_mac_hash), None)
        if current_device and current_device.get('status') == 'revoked':
            # Device exists in GitHub whitelist but with 'revoked' status
            device_name = current_device.get('device_name', current_device.get('computer_name', 'Unknown Device'))
            logging.error(f"❌ ACCESS DENIED: Device exists but is REVOKED")
            logging.error(f"   Device: {device_name}")
            logging.error(f"   MAC: {self.current_mac}")
            revoked_date = current_device.get('last_updated', 'Unknown')
            notes = current_device.get('notes', 'No notes available')
            return False, (f"⚠️  Access Denied - Device Revoked\n\n"
                         f"Device: {device_name}\n"
                         f"Status: REVOKED by administrator\n"
                         f"Date: {revoked_date}\n"
                         f"Notes: {notes}\n\n"
                         f"Contact administrator to restore access.")
        
        # NEW DEVICE - Auto-authorize if allow_first_run is True (default)
        # This enables unlimited multi-device support with automatic authorization
        if self.config.get("allow_first_run", True):
            device_count = len(authorized_macs) + 1
            logging.info(f"🆕 New device detected - auto-authorizing MAC: {self.current_mac}")
            logging.info(f"   This will be device #{device_count}")
            self.is_first_run = True  # Mark as first run
            self.authorize_current_mac()
            return True, f"Auto-authorized (device #{device_count})"
        
        # Only deny if allow_first_run is explicitly disabled (admin-controlled mode)
        mac_info = f" (MAC: {self.current_mac})" if self.config.get("show_mac_info", True) else ""
        device_count = len(authorized_macs)
        logging.error(f"❌ ACCESS DENIED: {self.current_mac}")
        logging.error(f"   {device_count} device(s) already authorized - this device is not in the list")
        logging.error(f"   Auto-authorization is disabled - contact administrator")
        return False, f"⚠️  Access Denied\n\n{device_count} device(s) already authorized.\nAuto-authorization disabled.\nContact administrator to authorize this device.\n\nMac Address:{mac_info}"

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
        Includes multi-device statistics.
        
        Returns:
            dict: Authentication info with device counts
        """
        authorized_macs = self.config.get("authorized_macs", [])
        is_auth, msg = self.is_authorized()
        
        return {
            "current_mac": self.current_mac,
            "mode": self.config.get("mode", "unknown"),
            "is_authorized": is_auth,
            "auth_message": msg,
            "total_devices": len(authorized_macs),
            "authorized_count": len(authorized_macs),
            "is_multi_device": len(authorized_macs) > 1
        }
    
    def get_device_list(self) -> list:
        """
        Get list of all authorized devices from whitelist.
        
        Returns:
            list: List of device dictionaries
        """
        try:
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r') as f:
                    whitelist = json.load(f)
                    devices = whitelist.get('devices', [])
                    return [
                        {
                            'device_id': d.get('device_id', 'N/A'),
                            'device_name': d.get('device_name', d.get('computer_name', 'Unknown')),
                            'mac_address': d.get('mac_address', 'N/A'),
                            'status': d.get('status', 'unknown'),
                            'authorized_date': d.get('authorized_date', 'N/A'),
                            'last_updated': d.get('last_updated', 'N/A'),
                            'username': d.get('username', 'N/A'),
                            'computer_name': d.get('computer_name', 'N/A')
                        }
                        for d in devices
                    ]
            return []
        except Exception as e:
            logging.error(f"Error getting device list: {e}")
            return []
    
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
