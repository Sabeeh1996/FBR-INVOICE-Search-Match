"""
Main Entry Point
FBR Invoice Checker Bot - Automated invoice verification with GUI
"""

import tkinter as tk
import logging
import os
from datetime import datetime
from gui import FBRInvoiceCheckerGUI


def setup_logging():
    """
    Setup logging configuration for the application.
    Creates logs directory and configures logging format.
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Created logs directory: {logs_dir}")
    
    # Generate log filename with timestamp
    log_filename = os.path.join(logs_dir, 'fbr_check_log.txt')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=" * 80)
    logging.info("FBR Invoice Checker Bot Started")
    logging.info(f"Log file: {log_filename}")
    logging.info("=" * 80)


def main():
    """
    Main function to initialize and run the application.
    """
    # Setup logging
    setup_logging()
    
    # Create Tkinter root window
    root = tk.Tk()
    
    # Set window icon (optional - can add custom icon later)
    # root.iconbitmap('icon.ico')
    
    # Center window on screen
    window_width = 800
    window_height = 650
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Create and run GUI
    app = FBRInvoiceCheckerGUI(root)
    
    # Start the Tkinter event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error in main loop: {str(e)}")
    finally:
        logging.info("=" * 80)
        logging.info("FBR Invoice Checker Bot Closed")
        logging.info("=" * 80)


if __name__ == "__main__":
    main()
