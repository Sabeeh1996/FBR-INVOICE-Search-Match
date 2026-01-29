"""
Single Instance Lock Manager
DISABLED - Allows multiple instances to run simultaneously.
"""

import os
import sys
import tempfile
import atexit
import logging


class SingleInstance:
    """
    Single instance checking DISABLED.
    Multiple instances of the application can now run simultaneously.
    """
    
    def __init__(self, app_name="FBR_Invoice_Checker"):
        """
        Initialize the single instance lock (DISABLED).
        
        Args:
            app_name (str): Unique application identifier (unused)
        """
        self.app_name = app_name
        self.lockfile = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
        self.fp = None
        self.is_locked = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def acquire_lock(self):
        """
        DISABLED - Always returns True to allow multiple instances.
        
        Returns:
            bool: Always True (multiple instances allowed)
        """
        logging.info("Single instance checking DISABLED - multiple instances allowed")
        self.is_locked = True
        return True
    
    def release_lock(self):
        """
        DISABLED - Does nothing.
        """
        self.is_locked = False
    
    def cleanup(self):
        """
        Cleanup function called on exit (DISABLED).
        """
        pass
    
    def get_lock_pid(self):
        """
        DISABLED - Returns None.
        
        Returns:
            None: Always None
        """
        return None
    
    def has_visible_window(self, pid):
        """
        DISABLED - Always returns True.
        
        Args:
            pid (int): Process ID (unused)
            
        Returns:
            bool: Always True
        """
        return True
    
    def kill_process(self, pid):
        """
        DISABLED - Does nothing.
        
        Args:
            pid (int): Process ID (unused)
            
        Returns:
            bool: Always False
        """
        return False
    
    def __enter__(self):
        """Context manager entry."""
        return self.acquire_lock()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release_lock()
        return False


# Convenience function for simple usage
def check_single_instance(app_name="FBR_Invoice_Checker"):
    """
    DISABLED - Always returns instance (multiple instances allowed).
    
    Args:
        app_name (str): Unique application identifier
        
    Returns:
        SingleInstance: Instance manager object
    """
    instance = SingleInstance(app_name)
    instance.acquire_lock()
    return instance


