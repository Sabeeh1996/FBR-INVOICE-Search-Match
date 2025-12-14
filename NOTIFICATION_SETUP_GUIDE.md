# First Run Notification Setup Guide

## Overview
When a user opens the application for the first time on a new device, you will automatically receive the MAC address and device information through your chosen notification method.

## Notification Methods

### 1. Local File (Default - Always Enabled)
**Easiest method - No setup required!**

- All first-run notifications are automatically saved to:
  ```
  logs/first_run_notifications.txt
  ```
- You can check this file anytime to see all new device activations
- Each entry includes: MAC address, computer name, username, timestamp, OS info

**To view notifications:**
```bash
cat logs/first_run_notifications.txt
# or open the file in any text editor
```

---

### 2. Telegram Bot (Recommended for Remote Monitoring)
**Get instant notifications on your phone!**

#### Setup Steps:

1. **Create Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow instructions to create bot
   - Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID:**
   - Search for `@userinfobot` in Telegram
   - Start chat and it will show your **Chat ID** (looks like: `123456789`)

3. **Configure notification_config.json:**
   ```json
   {
       "enabled": true,
       "methods": {
           "telegram": {
               "enabled": true,
               "bot_token": "YOUR_BOT_TOKEN_HERE",
               "chat_id": "YOUR_CHAT_ID_HERE"
           }
       }
   }
   ```

4. **Install requests library:**
   ```bash
   pip install requests
   ```

5. **Done!** You'll get instant Telegram messages when new devices activate.

---

### 3. Email Notification

#### For Gmail:

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Create App Password:**
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and "Windows Computer"
   - Copy the generated 16-character password

3. **Configure notification_config.json:**
   ```json
   {
       "enabled": true,
       "methods": {
           "email": {
               "enabled": true,
               "smtp_server": "smtp.gmail.com",
               "smtp_port": 587,
               "sender_email": "your-email@gmail.com",
               "sender_password": "your-16-char-app-password",
               "recipient_email": "admin@example.com"
           }
       }
   }
   ```

#### For Other Email Providers:
Update SMTP settings accordingly:
- **Outlook:** smtp-mail.outlook.com, port 587
- **Yahoo:** smtp.mail.yahoo.com, port 587
- **Custom SMTP:** Use your provider's settings

---

### 4. HTTP Webhook (For Custom Integration)

**Use if you have your own server/webhook:**

1. **Create API endpoint** that accepts POST requests

2. **Configure notification_config.json:**
   ```json
   {
       "enabled": true,
       "methods": {
           "http": {
               "enabled": true,
               "url": "https://your-server.com/api/notify",
               "api_key": "your-api-key-here"
           }
       }
   }
   ```

3. **Install requests library:**
   ```bash
   pip install requests
   ```

**Expected POST body:**
```json
{
    "event": "first_run",
    "device_info": {
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "computer_name": "CLIENT-PC",
        "username": "john.doe",
        "timestamp": "2025-12-14 15:30:45",
        "os": "Windows",
        "os_version": "10.0.19045",
        "machine": "AMD64"
    }
}
```

---

## Configuration File

The `notification_config.json` file controls all notification settings:

```json
{
    "enabled": true,
    "methods": {
        "http": {
            "enabled": false,
            "url": "https://your-server.com/api/notify",
            "api_key": "your-api-key-here"
        },
        "email": {
            "enabled": false,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your-email@gmail.com",
            "sender_password": "your-app-password",
            "recipient_email": "admin@example.com"
        },
        "telegram": {
            "enabled": false,
            "bot_token": "your-telegram-bot-token",
            "chat_id": "your-chat-id"
        },
        "local_file": {
            "enabled": true,
            "file_path": "logs/first_run_notifications.txt"
        }
    },
    "include_info": {
        "mac_address": true,
        "computer_name": true,
        "username": true,
        "timestamp": true,
        "os_info": true
    }
}
```

### Configuration Options:

- **enabled**: Master switch for all notifications
- **methods**: Enable/disable specific notification channels
- **include_info**: Choose what information to collect

---

## What Information is Collected?

On first run, the following information is collected and sent:

✅ **MAC Address** - Device's network adapter MAC
✅ **Computer Name** - Hostname of the device
✅ **Username** - Logged-in user
✅ **Timestamp** - Date and time of first run
✅ **OS Information** - Operating system and version

---

## Example Notifications

### Telegram Message:
```
🆕 FBR Invoice Checker - New Device

MAC_ADDRESS: AA:BB:CC:DD:EE:FF
COMPUTER_NAME: CLIENT-PC-01
USERNAME: john.doe
TIMESTAMP: 2025-12-14 15:30:45
OS: Windows
OS_VERSION: 10.0.19045
MACHINE: AMD64
```

### Email:
```
Subject: FBR Invoice Checker - New Device Activation

A new device has activated the FBR Invoice Checker application.

Device Information:
--------------------------------------------------
MAC_ADDRESS: AA:BB:CC:DD:EE:FF
COMPUTER_NAME: CLIENT-PC-01
USERNAME: john.doe
TIMESTAMP: 2025-12-14 15:30:45
OS: Windows
OS_VERSION: 10.0.19045
MACHINE: AMD64
--------------------------------------------------

Please verify this activation is authorized.
```

### Local File Entry:
```
================================================================================
NEW DEVICE FIRST RUN - 2025-12-14 15:30:45
================================================================================
MAC_ADDRESS: AA:BB:CC:DD:EE:FF
COMPUTER_NAME: CLIENT-PC-01
USERNAME: john.doe
TIMESTAMP: 2025-12-14 15:30:45
OS: Windows
OS_VERSION: 10.0.19045
MACHINE: AMD64
================================================================================
```

---

## Multiple Notification Methods

You can enable multiple methods simultaneously!

**Example: Get both Telegram AND Email notifications:**
```json
{
    "enabled": true,
    "methods": {
        "telegram": {
            "enabled": true,
            "bot_token": "...",
            "chat_id": "..."
        },
        "email": {
            "enabled": true,
            "smtp_server": "smtp.gmail.com",
            ...
        },
        "local_file": {
            "enabled": true
        }
    }
}
```

---

## Deployment Workflow

### Before Distribution:

1. **Choose notification method(s)**
2. **Configure notification_config.json**
3. **Test on your computer first**
4. **Include config file with application**

### When Client Installs:

1. Client extracts application
2. Client runs application first time
3. Application auto-authorizes device
4. **You receive notification automatically!**
5. You can verify MAC address and approve

---

## Troubleshooting

### Not Receiving Notifications?

**Check:**
1. Is `notification_config.json` present?
2. Is `"enabled": true` in config?
3. Are credentials correct (bot token, email password)?
4. Check `logs/fbr_check_log.txt` for errors
5. Verify `logs/first_run_notifications.txt` has entries (local file always works)

### Telegram Not Working?

- Verify bot token is correct
- Verify chat ID is correct
- Start chat with your bot first (send `/start`)
- Check internet connection
- Install requests: `pip install requests`

### Email Not Working?

- Verify SMTP settings
- Use App Password (not regular password) for Gmail
- Enable "Less secure app access" if required
- Check firewall settings
- Install required libraries (already in Python)

---

## Security Notes

✅ **MAC addresses are hashed** in storage
✅ **Notifications sent in background** - Don't block startup
✅ **Local file always works** - Even if remote methods fail
✅ **No internet required** - Local file method works offline

---

## Best Practices

1. **Enable Local File** - Always keep this as backup
2. **Use Telegram** - Best for instant remote monitoring
3. **Test First** - Run on your computer before distributing
4. **Check Regularly** - Review `logs/first_run_notifications.txt`
5. **Keep Config Secure** - Don't share credentials publicly

---

## Quick Start (Telegram - Recommended)

```bash
# 1. Create bot with @BotFather
# 2. Get chat ID from @userinfobot
# 3. Edit notification_config.json:
{
    "enabled": true,
    "methods": {
        "telegram": {
            "enabled": true,
            "bot_token": "YOUR_BOT_TOKEN",
            "chat_id": "YOUR_CHAT_ID"
        }
    }
}
# 4. pip install requests
# 5. Done!
```

Now you'll get instant notifications when new devices activate! 🎉
