"""
Application Data Manager
Manages writable app data files in hidden/system folders
Keeps the exe directory clean
"""

import os
import sys
import json
import logging
from pathlib import Path


def get_app_data_dir():
    """
    Get application data directory for storing writable files.
    Uses AppData on Windows, hidden folder on other OS.
    
    Returns:
        str: Path to app data directory
    """
    if os.name == 'nt':  # Windows
        # Use AppData/Local folder
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(appdata, 'FBR_Invoice_Checker')
    else:  # Linux/Mac
        # Use hidden folder in home directory
        app_dir = os.path.expanduser('~/.fbr_invoice_checker')
    
    # Create directory if it doesn't exist
    os.makedirs(app_dir, exist_ok=True)
    
    return app_dir


def get_writable_file_path(filename):
    """
    Get path for a writable data file in app data directory.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        str: Full path to the file in app data directory
    """
    return os.path.join(get_app_data_dir(), filename)


def copy_bundled_to_appdata(bundled_path, filename):
    """
    Copy bundled resource to app data directory if it doesn't exist.
    
    Args:
        bundled_path (str): Path to bundled resource file
        filename (str): Target filename in app data
        
    Returns:
        str: Path to the copied file in app data
    """
    target_path = get_writable_file_path(filename)
    
    # If target doesn't exist, copy from bundled resource
    if not os.path.exists(target_path):
        try:
            with open(bundled_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Copied bundled resource to: {target_path}")
        except Exception as e:
            logging.error(f"Error copying bundled resource: {e}")
            return None
    
    return target_path


def ensure_writable_copy(bundled_path, filename, default_content=None):
    """
    Ensure a writable copy of a file exists in app data directory.
    
    Args:
        bundled_path (str): Path to bundled resource (may not exist)
        filename (str): Target filename in app data
        default_content (dict): Default content if no bundled file exists
        
    Returns:
        str: Path to writable file
    """
    target_path = get_writable_file_path(filename)
    
    if not os.path.exists(target_path):
        # Try to copy from bundled resource first
        if os.path.exists(bundled_path):
            try:
                with open(bundled_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                logging.info(f"Created writable copy from bundled: {filename}")
            except Exception as e:
                logging.warning(f"Could not copy from bundled: {e}")
                # Fall through to create with default content
        
        # Create with default content if bundled copy failed or doesn't exist
        if not os.path.exists(target_path) and default_content:
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    if isinstance(default_content, dict):
                        json.dump(default_content, f, indent=2)
                    else:
                        f.write(str(default_content))
                logging.info(f"Created new file with defaults: {filename}")
            except Exception as e:
                logging.error(f"Could not create default file: {e}")
    
    return target_path
