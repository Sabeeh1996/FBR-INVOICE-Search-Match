# SOFTWARE LICENSE & EXPIRY SYSTEM

## Overview

The FBR Invoice Checker Bot now includes an integrated license/expiry management system that allows you to:

- ✅ Set software expiry dates
- ✅ Display early warnings (30 days before expiry)
- ✅ Show critical warnings (7 days before expiry)
- ✅ Block usage after expiry date
- ✅ Provide user-friendly notifications

---

## Features

### 1. **Automatic License Validation**
- License is automatically checked when the software starts
- Software will NOT run if license has expired
- Clear error message displayed to user

### 2. **Early Warning System**
Three levels of warnings:
- **OK** (Green): Software active, more than 30 days remaining
- **WARNING** (Orange): 7-30 days until expiry
- **CRITICAL** (Red): Less than 7 days until expiry
- **EXPIRED** (Red): Software has expired

### 3. **Visual Indicators**
- License status displayed at the top of the application in color-coded bar
- Green = Normal operation
- Orange = Warning - expiry approaching
- Red = Critical - expiry very soon or already expired

### 4. **User Notifications**
- Welcome message includes license status
- License details available via "Details" button in GUI
- Pop-up warnings appear on startup if expiry is approaching

---

## Setting Expiry Date

There are three ways to set the software expiry date:

### Method 1: GUI Tool (Recommended for Users)

```bash
python set_expiry.py gui
```

A window will open showing:
- Current expiry date
- Days remaining
- Prompt to enter new expiry date

Enter the date in `YYYY-MM-DD` format (Example: `2025-12-31`)

### Method 2: Command Line (For Administrators)

**Set specific date:**
```bash
python set_expiry.py 2025-12-31
```

**View current license info:**
```bash
python set_expiry.py info
```

**Show help:**
```bash
python set_expiry.py
```

### Method 3: Python Script (For Developers)

```python
from license_manager import LicenseManager

# Create or load license
license_mgr = LicenseManager()

# Set new expiry date
license_mgr.set_expiry_date("2025-12-31")

# View status
status = license_mgr.get_expiry_status()
print(status['message'])
```

---

## License Configuration File

The license information is stored in `license_config.json`:

```json
{
    "expiry_date": "2025-12-31",
    "created_date": "2024-11-13 10:30:00",
    "last_updated": "2024-11-13 11:45:00",
    "software_version": "1.0.0"
}
```

**Location:** Root directory of the application

**Note:** This file is created automatically with default expiry date if it doesn't exist.

---

## Default Expiry Date

Default expiry date: **2025-12-31**

You can change the default by editing `license_manager.py`:

```python
DEFAULT_EXPIRY_DATE = "2025-12-31"  # Change this date
```

---

## Warning Thresholds

You can customize warning thresholds in `license_manager.py`:

```python
# Days before expiry to show early warning
EARLY_WARNING_DAYS = 30

# Days before expiry to show critical warning
CRITICAL_WARNING_DAYS = 7
```

---

## Behavior When Software Expires

1. **On Startup:**
   - License is validated before GUI appears
   - If expired, error dialog is shown
   - Application terminates gracefully

2. **During Usage:**
   - License status is always visible in GUI
   - If expiry is approaching, warning dialogs appear
   - User can view full license details by clicking "Details" button

3. **After Expiry:**
   - Software cannot be run
   - Clear message explains why
   - Instructions provided to contact administrator

---

## Expiry Date Format

**Always use this format:** `YYYY-MM-DD`

**Examples:**
- ✅ `2025-12-31` (Valid)
- ✅ `2026-01-15` (Valid)
- ❌ `12/31/2025` (Invalid)
- ❌ `31-12-2025` (Invalid)
- ❌ `2025/12/31` (Invalid)

---

## Status Levels & Actions

| Status | Days Remaining | Color | Action | Message |
|--------|---------------|-------|--------|---------|
| OK | > 30 | 🟢 Green | Continue normally | Software active |
| WARNING | 7-30 | 🟡 Orange | Show info dialog | Approaching expiry |
| CRITICAL | 0-6 | 🔴 Red | Show warning dialog | Expiry very soon |
| EXPIRED | < 0 | 🔴 Red | Block & exit | Expired - cannot run |

---

## Example Scenarios

### Scenario 1: Setting Up Software

```bash
# Initial setup with 90-day trial
python set_expiry.py 2025-02-13

# Or use GUI
python set_expiry.py gui
# Enter: 2025-02-13
```

### Scenario 2: Renewing License

User sees warning that software expires in 10 days. Administrator sets new date:

```bash
python set_expiry.py 2026-02-13
# Confirms: ✓ Expiry date updated successfully!
```

Software continues running with new expiry date.

### Scenario 3: Emergency Expiry

Testing scenario - set expiry to tomorrow:

```bash
python set_expiry.py 2024-11-14
```

On next startup, user sees critical warning. After that date, software won't run.

---

## Troubleshooting

### Problem: Invalid Date Format Error

```
❌ FAILED TO UPDATE EXPIRY DATE
Invalid date format: 12/31/2025
```

**Solution:** Use `YYYY-MM-DD` format:
```bash
python set_expiry.py 2025-12-31
```

### Problem: License File Missing

**Solution:** Restart the application - it will create `license_config.json` automatically with default date.

### Problem: Software Won't Start

**Reason:** License has expired

**Solution:** 
1. Set new expiry date:
   ```bash
   python set_expiry.py 2026-12-31
   ```
2. Restart the application

### Problem: Can't Find license_config.json

**Location:** Check the root directory of the application (same folder as `main.py`)

---

## Security Notes

- License file is stored in plain JSON (not encrypted)
- This is suitable for internal use
- For production with sensitive licensing, consider using encrypted storage
- The timestamp fields help track when licenses were issued/updated

---

## Support

For license-related issues:
1. Check current status: `python set_expiry.py info`
2. View GUI tool: `python set_expiry.py gui`
3. Check `license_config.json` file
4. Check application logs in `logs/fbr_check_log.txt`

---

## Quick Reference

```bash
# View current license info
python set_expiry.py info

# Open GUI tool to set date
python set_expiry.py gui

# Set expiry to specific date
python set_expiry.py 2025-12-31

# Set expiry to 90 days from now
python set_expiry.py $(date -d "+90 days" +%Y-%m-%d)
```

---

## Integration Points

The license system is integrated at:

1. **main.py** - Initial validation on startup
2. **gui.py** - Status display in main window
3. **license_manager.py** - Core license logic
4. **set_expiry.py** - Administrator tool

All warnings and status messages use standard Tkinter message boxes for user-friendly interaction.

---

## Version History

- **v1.0.0** - Initial license system implementation (Nov 2024)
