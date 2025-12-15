"""
Single Instance Lock Manager
Prevents multiple instances of the application from running simultaneously.
"""

import os
import sys
import tempfile
import atexit
import logging


class SingleInstance:
    """
    Ensures only one instance of the application can run at a time.
    Uses a lock file mechanism that works across platforms.
    """
    
    def __init__(self, app_name="FBR_Invoice_Checker"):
        """
        Initialize the single instance lock.
        
        Args:
            app_name (str): Unique application identifier
        """
        self.app_name = app_name
        self.lockfile = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
        self.fp = None
        self.is_locked = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def acquire_lock(self):
        """
        Try to acquire the single instance lock.
        Automatically cleans up stale locks from previous crashes.
        
        Returns:
            bool: True if lock acquired successfully, False if another instance is running
        """
        try:
            # First, check for and remove any stale lock files
            self._cleanup_stale_lock()
            
            # Try to open the lock file exclusively
            if os.name == 'nt':  # Windows
                # On Windows, we use file locking
                import msvcrt
                
                # Create new lock file
                self.fp = open(self.lockfile, 'w')
                try:
                    msvcrt.locking(self.fp.fileno(), msvcrt.LK_NBLCK, 1)
                    self.fp.write(str(os.getpid()))
                    self.fp.flush()
                    self.is_locked = True
                    logging.info(f"Single instance lock acquired (PID: {os.getpid()})")
                    return True
                except IOError:
                    self.fp.close()
                    self.fp = None
                    logging.warning("Another instance is already running")
                    return False
                    
            else:  # Unix/Linux/Mac
                import fcntl
                
                self.fp = open(self.lockfile, 'w')
                try:
                    fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.fp.write(str(os.getpid()))
                    self.fp.flush()
                    self.is_locked = True
                    logging.info(f"Single instance lock acquired (PID: {os.getpid()})")
                    return True
                except IOError:
                    self.fp.close()
                    self.fp = None
                    logging.warning("Another instance is already running")
                    return False
                    
        except Exception as e:
            logging.error(f"Error acquiring single instance lock: {str(e)}")
            return False
    
    def _cleanup_stale_lock(self):
        """
        Check for and remove stale lock files from previous crashes or force closes.
        This ensures users can always restart the app even if it was terminated abnormally.
        """
        if not os.path.exists(self.lockfile):
            return
        
        try:
            # Try to read the PID from lock file
            with open(self.lockfile, 'r') as f:
                pid_str = f.read().strip()
                if not pid_str:
                    # Empty lock file, remove it
                    logging.info("Removing empty lock file")
                    os.remove(self.lockfile)
                    return
                
                pid = int(pid_str)
                
            # Check if process is still running
            if not self._is_process_running(pid):
                # Stale lock file from crashed/killed process, remove it
                logging.info(f"Removing stale lock file (PID {pid} is not running)")
                os.remove(self.lockfile)
            else:
                logging.debug(f"Lock file is valid (PID {pid} is running)")
                
        except (ValueError, IOError, OSError) as e:
            # Invalid lock file, remove it
            logging.info(f"Removing invalid lock file: {e}")
            try:
                os.remove(self.lockfile)
            except:
                pass
    
    def _is_process_running(self, pid):
        """
        Check if a process with given PID is running.
        
        Args:
            pid (int): Process ID to check
            
        Returns:
            bool: True if process is running, False otherwise
        """
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                kernel32 = ctypes.windll.kernel32
                PROCESS_QUERY_INFORMATION = 0x0400
                SYNCHRONIZE = 0x00100000
                
                handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | SYNCHRONIZE, 0, pid)
                if handle:
                    kernel32.CloseHandle(handle)
                    return True
                return False
            else:  # Unix/Linux/Mac
                import signal
                try:
                    os.kill(pid, 0)
                    return True
                except OSError:
                    return False
        except:
            return False
    
    def release_lock(self):
        """
        Release the single instance lock.
        """
        if self.fp:
            try:
                if os.name == 'nt':  # Windows
                    import msvcrt
                    msvcrt.locking(self.fp.fileno(), msvcrt.LK_UNLCK, 1)
                else:  # Unix/Linux/Mac
                    import fcntl
                    fcntl.lockf(self.fp, fcntl.LOCK_UN)
                
                self.fp.close()
                self.fp = None
                
                # Remove lock file
                if os.path.exists(self.lockfile):
                    os.remove(self.lockfile)
                    
                self.is_locked = False
                logging.info("Single instance lock released")
                
            except Exception as e:
                logging.error(f"Error releasing single instance lock: {str(e)}")
    
    def cleanup(self):
        """
        Cleanup function called on exit.
        """
        if self.is_locked:
            self.release_lock()
    
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
    Check if application is already running.
    
    Args:
        app_name (str): Unique application identifier
        
    Returns:
        SingleInstance: Instance manager object if lock acquired, None otherwise
    """
    instance = SingleInstance(app_name)
    if instance.acquire_lock():
        return instance
    return None
