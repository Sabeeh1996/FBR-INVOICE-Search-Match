"""
MAC Address Authentication Module
Restricts application usage to authorized MAC addresses only.
"""

import uuid
import json
import os
import logging
import hashlib
from typing import List, Optional, Tuple


class MACAuthenticator:
    """
    Handles MAC address-based authentication for the application.
    Supports both whitelist mode and license binding mode.
    """
    
    def __init__(self, config_file="mac_config.json"):
        """
        Initialize MAC authenticator.
        
        Args:
            config_file (str): Path to MAC address configuration file
        """
        self.config_file = config_file
        self.config_existed_before = os.path.exists(config_file)  # Track if config existed
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
    
    def is_authorized(self) -> Tuple[bool, str]:
        """
        Check if current MAC address is authorized to run the application.
        
        Returns:
            tuple: (is_authorized: bool, message: str)
        """
        if not self.current_mac:
            return False, "Unable to detect MAC address"
        
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
        
        Returns:
            tuple: (is_authorized: bool, message: str)
        """
        authorized_macs = self.config.get("authorized_macs", [])
        
        # If whitelist is empty and allow_first_run is True, auto-authorize
        if not authorized_macs and self.config.get("allow_first_run", True):
            logging.info(f"First run detected - auto-authorizing MAC: {self.current_mac}")
            self.is_first_run = True  # Mark as first run
            self.authorize_current_mac()
            return True, "Auto-authorized (first run)"
        
        # Check if current MAC is in whitelist
        if self.current_mac_hash in authorized_macs:
            logging.info(f"MAC address authorized: {self.current_mac}")
            return True, "MAC address authorized"
        
        # Not authorized
        mac_info = f" (MAC: {self.current_mac})" if self.config.get("show_mac_info", True) else ""
        logging.warning(f"Unauthorized MAC address: {self.current_mac}")
        return False, f"This device is not authorized to run the application{mac_info}"
    
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
