"""
First Run Notification System
Sends MAC address information to administrator on first application run.
"""

import os
import json
import logging
import threading
from datetime import datetime
from typing import Optional


class FirstRunNotifier:
    """
    Handles notifications when application runs for first time on a new device.
    Supports multiple notification methods: HTTP, Email, Telegram, Local File.
    """
    
    def __init__(self, config_file="notification_config.json"):
        """
        Initialize notifier with configuration.
        
        Args:
            config_file (str): Path to notification configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.notification_log = "logs/first_run_notifications.txt"
        
    def _load_config(self) -> dict:
        """
        Load notification configuration.
        
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            "enabled": True,
            "methods": {
                "http": {
                    "enabled": False,
                    "url": "https://your-server.com/api/notify",
                    "api_key": "your-api-key-here"
                },
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your-email@gmail.com",
                    "sender_password": "your-app-password",
                    "recipient_email": "admin@example.com"
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": "your-telegram-bot-token",
                    "chat_id": "your-chat-id"
                },
                "local_file": {
                    "enabled": True,
                    "file_path": "logs/first_run_notifications.txt"
                }
            },
            "include_info": {
                "mac_address": True,
                "computer_name": True,
                "username": True,
                "timestamp": True,
                "os_info": True
            }
        }
        
        if not os.path.exists(self.config_file):
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except Exception as e:
            logging.error(f"Error loading notification config: {str(e)}")
            return default_config
    
    def _save_config(self, config: dict = None):
        """Save notification configuration."""
        try:
            config_to_save = config if config else self.config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving notification config: {str(e)}")
    
    def collect_device_info(self, mac_address: str) -> dict:
        """
        Collect device information for notification.
        
        Args:
            mac_address (str): MAC address of the device
            
        Returns:
            dict: Device information
        """
        import platform
        import socket
        
        info = {}
        include = self.config.get("include_info", {})
        
        if include.get("mac_address", True):
            info["mac_address"] = mac_address
        
        if include.get("computer_name", True):
            try:
                info["computer_name"] = socket.gethostname()
            except:
                info["computer_name"] = "Unknown"
        
        if include.get("username", True):
            try:
                info["username"] = os.getlogin()
            except:
                info["username"] = os.environ.get('USERNAME', 'Unknown')
        
        if include.get("timestamp", True):
            info["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if include.get("os_info", True):
            try:
                info["os"] = platform.system()
                info["os_version"] = platform.version()
                info["machine"] = platform.machine()
            except:
                info["os"] = "Unknown"
        
        return info
    
    def notify_first_run(self, mac_address: str) -> bool:
        """
        Send first run notification using all enabled methods.
        
        Args:
            mac_address (str): MAC address of the device
            
        Returns:
            bool: True if at least one notification succeeded
        """
        if not self.config.get("enabled", True):
            logging.info("First run notifications are disabled")
            return False
        
        device_info = self.collect_device_info(mac_address)
        success = False
        
        # Try all enabled notification methods
        methods = self.config.get("methods", {})
        
        # Local file (always try this as fallback)
        if methods.get("local_file", {}).get("enabled", True):
            if self._notify_local_file(device_info):
                success = True
        
        # HTTP notification
        if methods.get("http", {}).get("enabled", False):
            # Run in background thread to not block startup
            threading.Thread(target=self._notify_http, args=(device_info,), daemon=True).start()
            success = True
        
        # Email notification
        if methods.get("email", {}).get("enabled", False):
            threading.Thread(target=self._notify_email, args=(device_info,), daemon=True).start()
            success = True
        
        # Telegram notification
        if methods.get("telegram", {}).get("enabled", False):
            threading.Thread(target=self._notify_telegram, args=(device_info,), daemon=True).start()
            success = True
        
        return success
    
    def _notify_local_file(self, device_info: dict) -> bool:
        """
        Write notification to local file.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            bool: True if successful
        """
        try:
            file_path = self.config.get("methods", {}).get("local_file", {}).get("file_path", self.notification_log)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write notification
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*80 + "\n")
                f.write(f"NEW DEVICE FIRST RUN - {device_info.get('timestamp', 'Unknown')}\n")
                f.write("="*80 + "\n")
                for key, value in device_info.items():
                    f.write(f"{key.upper()}: {value}\n")
                f.write("="*80 + "\n\n")
            
            logging.info(f"First run notification saved to: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error writing first run notification to file: {str(e)}")
            return False
    
    def _notify_http(self, device_info: dict) -> bool:
        """
        Send notification via HTTP POST request.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            bool: True if successful
        """
        try:
            import requests
            
            http_config = self.config.get("methods", {}).get("http", {})
            url = http_config.get("url")
            api_key = http_config.get("api_key")
            
            if not url:
                logging.warning("HTTP notification URL not configured")
                return False
            
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            payload = {
                "event": "first_run",
                "device_info": device_info
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                logging.info("First run notification sent via HTTP")
                return True
            else:
                logging.warning(f"HTTP notification failed with status: {response.status_code}")
                return False
                
        except ImportError:
            logging.warning("requests library not installed. Install with: pip install requests")
            return False
        except Exception as e:
            logging.error(f"Error sending HTTP notification: {str(e)}")
            return False
    
    def _notify_email(self, device_info: dict) -> bool:
        """
        Send notification via email.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            bool: True if successful
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            email_config = self.config.get("methods", {}).get("email", {})
            
            # Email content
            subject = f"FBR Invoice Checker - New Device Activation"
            
            body = "A new device has activated the FBR Invoice Checker application.\n\n"
            body += "Device Information:\n"
            body += "-" * 50 + "\n"
            for key, value in device_info.items():
                body += f"{key.upper()}: {value}\n"
            body += "-" * 50 + "\n\n"
            body += "Please verify this activation is authorized.\n"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config.get("sender_email")
            msg['To'] = email_config.get("recipient_email")
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port"))
            server.starttls()
            server.login(email_config.get("sender_email"), email_config.get("sender_password"))
            server.send_message(msg)
            server.quit()
            
            logging.info("First run notification sent via email")
            return True
            
        except Exception as e:
            logging.error(f"Error sending email notification: {str(e)}")
            return False
    
    def _notify_telegram(self, device_info: dict) -> bool:
        """
        Send notification via Telegram bot.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            bool: True if successful
        """
        try:
            import requests
            
            telegram_config = self.config.get("methods", {}).get("telegram", {})
            bot_token = telegram_config.get("bot_token")
            chat_id = telegram_config.get("chat_id")
            
            if not bot_token or not chat_id:
                logging.warning("Telegram bot token or chat ID not configured")
                return False
            
            # Format message
            message = "🆕 *FBR Invoice Checker - New Device*\n\n"
            for key, value in device_info.items():
                message += f"*{key.upper()}:* `{value}`\n"
            
            # Send via Telegram API
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logging.info("First run notification sent via Telegram")
                return True
            else:
                logging.warning(f"Telegram notification failed with status: {response.status_code}")
                return False
                
        except ImportError:
            logging.warning("requests library not installed. Install with: pip install requests")
            return False
        except Exception as e:
            logging.error(f"Error sending Telegram notification: {str(e)}")
            return False
    
    def get_notification_display_text(self, mac_address: str) -> str:
        """
        Get formatted text to display to user on first run.
        
        Args:
            mac_address (str): MAC address
            
        Returns:
            str: Formatted display text
        """
        device_info = self.collect_device_info(mac_address)
        
        text = "="*60 + "\n"
        text += "  FIRST TIME ACTIVATION\n"
        text += "="*60 + "\n\n"
        text += "This device has been authorized to run the application.\n\n"
        text += "Device Information:\n"
        text += "-"*60 + "\n"
        text += f"MAC Address:    {device_info.get('mac_address', 'Unknown')}\n"
        text += f"Computer Name:  {device_info.get('computer_name', 'Unknown')}\n"
        text += f"User:           {device_info.get('username', 'Unknown')}\n"
        text += f"Date/Time:      {device_info.get('timestamp', 'Unknown')}\n"
        text += "-"*60 + "\n\n"
        text += "This information has been logged for security purposes.\n"
        text += "="*60 + "\n"
        
        return text


def check_and_notify_first_run(mac_address: str, mac_config_existed: bool) -> bool:
    """
    Check if this is first run and send notification if needed.
    
    Args:
        mac_address (str): MAC address of device
        mac_config_existed (bool): Whether mac_config.json existed before
        
    Returns:
        bool: True if this was first run
    """
    # If mac_config didn't exist before, this is first run
    if not mac_config_existed:
        notifier = FirstRunNotifier()
        
        # Send notifications
        notifier.notify_first_run(mac_address)
        
        # Log the first run
        logging.info("="*80)
        logging.info("FIRST RUN DETECTED - Device authorized and notification sent")
        logging.info(notifier.get_notification_display_text(mac_address))
        logging.info("="*80)
        
        return True
    
    return False
