# EXPIRY & LICENSE QUICK START

## What's New? 🎯

Your software now has an **automatic expiry/license system** that:
- ✅ Blocks software from running after expiry date
- ✅ Shows warnings 15 days before expiry
- ✅ Shows critical alerts 7 days before expiry
- ✅ Provides easy admin tool to set expiry dates

---

## For Users 👥

### What You'll See

**When Software is Active:**
```
✓ Software active. Expires in 45 days (2025-12-31)
```
Status bar at top shows in **GREEN** ✅

**When Expiry is Approaching:**
```
🟡 WARNING: Software expires in 15 days (2025-12-31)
```
Status bar at top shows in **ORANGE** ⚠️
You'll see a popup notification.

**When Expiry is Very Soon:**
```
🔴 CRITICAL: Software expires in 5 days (2025-12-31)
```
Status bar at top shows in **RED** 🔴
You'll see a critical warning dialog.

**When Software is Expired:**
```
🔴 SOFTWARE EXPIRED! Expired on 2025-12-31
```
Application cannot start. Shows error message.

### View License Details

Click the **"Details"** button in the status bar to see:
- Current expiry date
- Days remaining
- Current status
- License info

---

## For Administrators 🔧

### Setting Expiry Date

#### Option 1: GUI Tool (Easiest)

```bash
python set_expiry.py gui
```

A window opens. Enter date in `YYYY-MM-DD` format:
```
2025-12-31
```

Click OK. Done! ✓

#### Option 2: Command Line

```bash
python set_expiry.py 2025-12-31
```

Response:
```
✓ EXPIRY DATE UPDATED SUCCESSFULLY
==============================================================
📋 SOFTWARE LICENSE INFORMATION
==============================================================
Expiry Date:        2025-12-31
Days Remaining:     365 days
Status:             OK
Message:            ✓ Software active. Expires in 365 days
==============================================================
```

#### Option 3: Check Current Status

```bash
python set_expiry.py info
```

Shows current license information without making changes.

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `python set_expiry.py gui` | Open GUI tool to set date |
| `python set_expiry.py 2025-12-31` | Set expiry to Dec 31, 2025 |
| `python set_expiry.py info` | View current license info |
| `python set_expiry.py` | Show help/usage |

---

## Date Format Rules ⚠️

**CORRECT:**
- ✅ `2025-12-31` (December 31, 2025)
- ✅ `2026-01-15` (January 15, 2026)
- ✅ `2024-06-30` (June 30, 2024)

**WRONG:**
- ❌ `12/31/2025` (American format)
- ❌ `31-12-2025` (European format)
- ❌ `2025/12/31` (Slash format)
- ❌ `December 31, 2025` (Written format)

Always use: `YYYY-MM-DD` (Year-Month-Day with dashes)

---

## Typical Workflow

### 1. Install/First Run
Software comes with default expiry: **2025-12-31**

### 2. Set Custom Expiry
```bash
python set_expiry.py 2026-06-30
# Now expires June 30, 2026
```

### 3. Monitor
Users see status in GUI. Warnings appear at 30 and 7 days.

### 4. Renew Before Expiry
```bash
python set_expiry.py 2027-06-30
# Extended another year
```

### 5. After Expiry
If not renewed, software won't start. Error message explains.

---

## Where is License Stored?

File: `license_config.json` (in application root directory)

Example:
```json
{
    "expiry_date": "2025-12-31",
    "created_date": "2024-11-13 10:30:00",
    "last_updated": "2024-11-13 11:45:00",
    "software_version": "1.0.0"
}
```

**This file is created automatically** - you don't need to create it.

---

## Troubleshooting

### "Software Expired" Error on Startup
→ Expiry date has passed
→ Solution: `python set_expiry.py 2026-12-31`

### Invalid Date Format Error
→ Using wrong date format
→ Solution: Use `YYYY-MM-DD` format only

### License file not found?
→ Restart application - it will be created automatically with default date

### Can't find set_expiry.py?
→ Make sure you're in the application root directory
→ Use: `cd path/to/FBR-INVOICE-STATUS-MATCHING`

---

## Key Features Summary

| Feature | Details |
|---------|---------|
| **Validation** | Checked automatically on startup |
| **Early Warning** | Shows at 30 days before expiry |
| **Critical Alert** | Shows at 7 days before expiry |
| **Visual Indicator** | Color-coded status bar (Green/Orange/Red) |
| **GUI Integration** | License status always visible |
| **Admin Control** | Easy-to-use admin tool |
| **Logs** | All expiry events logged in logs/fbr_check_log.txt |

---

## For Complete Details

See: `LICENSE_GUIDE.md` for comprehensive documentation

---

## Support

**Questions?** Check:
1. License status: `python set_expiry.py info`
2. Current date format is YYYY-MM-DD
3. Check logs: `logs/fbr_check_log.txt`
4. See LICENSE_GUIDE.md for advanced options

**Example Issue Solving:**
```
Problem: "Invalid date format"
Solution: Use python set_expiry.py 2025-12-31 (not 12/31/2025)
```

---

Happy automating! 🎉
