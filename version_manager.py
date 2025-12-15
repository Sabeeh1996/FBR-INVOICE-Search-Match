"""
Secure Version Management Module
Prevents users from manually editing version.txt to downgrade or change versions.
Only the updater module (with a secret token) can change versions.
"""

import os
import sys
import hashlib
import json
import logging
from datetime import datetimefrom app_data_manager import get_app_data_dir
logger = logging.getLogger(__name__)


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


def get_app_dir():
    """Return application directory (works for both .py and .exe)"""
    if getattr(sys, "frozen", False):
        # PyInstaller bundled executable - use the exe's directory
        return os.path.dirname(sys.executable)
    else:
        # Python script
        return os.path.dirname(os.path.abspath(__file__))


def get_version_file():
    """
    Return path to version.txt.
    When running as exe, reads from bundled resource (read-only).
    """
    if getattr(sys, "frozen", False):
        # Read from bundled resource inside exe
        return get_resource_path("version.txt")
    else:
        # Development mode: read from local file
        return os.path.join(get_app_dir(), "version.txt")


def get_version_lock_file():
    """
    Return path to version.lock (tamper-proof lock file).
    When running as exe, stores in AppData (hidden from user).
    """
    if getattr(sys, "frozen", False):
        # Running as exe - use AppData directory
        return os.path.join(get_app_data_dir(), "version.lock")
    else:
        # Development mode - use app directory
        return os.path.join(get_app_dir(), "version.lock")


def calculate_checksum(version_str):
    """
    Generate a checksum to validate version hasn't been tampered with.
    
    Args:
        version_str: Version string (e.g., "1.1")
    
    Returns:
        str: SHA256 checksum (first 16 chars)
    """
    return hashlib.sha256(version_str.encode()).hexdigest()[:16]


def read_version():
    """
    Read version from file with integrity check.
    
    If version.txt was manually edited by user, this detects it
    and returns the locked version instead.
    
    Returns:
        tuple: (version_string, is_valid_checksum)
               is_valid_checksum = False means file was tampered
    """
    version_file = get_version_file()
    lock_file = get_version_lock_file()
    
    try:
        # Read version file
        if not os.path.exists(version_file):
            logger.warning(f"Version file not found: {version_file}")
            return "1.0", False
        
        with open(version_file, "r", encoding="utf-8") as f:
            version = f.read().strip()
        
        # Check if lock file exists and validate integrity
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)
                
                stored_checksum = lock_data.get("checksum", "")
                expected_checksum = calculate_checksum(version)
                
                # If checksum doesn't match, user tampered with version.txt
                if stored_checksum != expected_checksum:
                    logger.warning(
                        f"[SECURITY] version.txt was tampered! "
                        f"Expected checksum: {stored_checksum}, Got: {expected_checksum}. "
                        f"Reverting to locked version."
                    )
                    locked_version = lock_data.get("version", "1.0")
                    return locked_version, False
                
                return version, True
            
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading version lock: {e}")
                return version, False
        else:
            # No lock file yet, create one (first run or fresh install)
            logger.info("First run: creating version lock file")
            create_version_lock(version)
            return version, True
    
    except Exception as e:
        logger.error(f"Error reading version: {e}")
        return "1.0", False


def create_version_lock(version):
    """
    Create a tamper-proof lock file that stores version + checksum.
    
    ONLY the updater module should call this after a successful update.
    This prevents users from manually downgrading versions.
    
    Args:
        version: Version string (e.g., "1.1")
    
    Returns:
        bool: True if lock created successfully
    """
    lock_file = get_version_lock_file()
    checksum = calculate_checksum(version)
    
    lock_data = {
        "version": version,
        "checksum": checksum,
        "locked_at": datetime.now().isoformat(),
        "locked_by": "system_updater"
    }
    
    try:
        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump(lock_data, f, indent=2)
        logger.info(f"Version lock created: {version} (checksum: {checksum})")
        return True
    except Exception as e:
        logger.error(f"Error creating version lock: {e}")
        return False


def update_version_secure(new_version, updater_token=None):
    """
    Securely update version (only updater module can call this).
    
    This prevents accidental or malicious version changes by requiring
    a secret token that only the updater module should have.
    
    Args:
        new_version: The new version string (e.g., "1.1")
        updater_token: Secret token that only updater.py should have
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # This token should match the one in updater.py
    UPDATER_TOKEN = "updater_secure_token_2025_fbr_invoice"
    
    if updater_token != UPDATER_TOKEN:
        logger.error(f"Unauthorized version update attempt (invalid token)")
        return False, "Unauthorized: Only updater can change version"
    
    version_file = get_version_file()
    
    try:
        # Write new version to file
        with open(version_file, "w", encoding="utf-8") as f:
            f.write(new_version.strip())
        
        # Create integrity lock to prevent tampering
        if not create_version_lock(new_version):
            return False, "Failed to create version lock"
        
        logger.info(f"Version securely updated to {new_version}")
        return True, f"Version updated to {new_version}"
    
    except Exception as e:
        logger.error(f"Failed to update version: {e}")
        return False, f"Failed to update version: {e}"


def is_version_tampered():
    """
    Check if version.txt was manually edited by user.
    
    Returns:
        bool: True if tampering detected, False if version is valid
    """
    version, is_valid = read_version()
    return not is_valid


def get_version_info():
    """
    Get detailed version information for logging/debugging.
    
    Returns:
        dict: Version info including status, checksum, locked time
    """
    version_file = get_version_file()
    lock_file = get_version_lock_file()
    
    version, is_valid = read_version()
    
    info = {
        "version": version,
        "is_valid": is_valid,
        "version_file_exists": os.path.exists(version_file),
        "lock_file_exists": os.path.exists(lock_file),
        "app_dir": get_app_dir()
    }
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
            info["locked_at"] = lock_data.get("locked_at")
            info["checksum"] = lock_data.get("checksum")
        except Exception:
            pass
    
    return info
