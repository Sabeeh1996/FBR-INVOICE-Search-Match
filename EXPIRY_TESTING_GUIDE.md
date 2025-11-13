# EXPIRY SYSTEM - TESTING GUIDE

## How to Test the Expiry System

This guide shows you how to verify the expiry/license system is working correctly.

---

## Test 1: Verify Current License Status

**Command:**
```bash
python set_expiry.py info
```

**Expected Output:**
```
============================================================
📋 SOFTWARE LICENSE INFORMATION
============================================================
Expiry Date:        2025-12-31
Days Remaining:     365 days
Status:             OK
Message:            ✓ Software active. Expires in 365 days
============================================================
```

**What to Check:**
- ✓ Shows a valid date
- ✓ Shows correct number of days
- ✓ Status should be OK (if more than 30 days remain)

---

## Test 2: Set Future Expiry Date (OK Status)

Test that the "OK" status displays correctly.

**Command:**
```bash
python set_expiry.py 2026-12-31
```

**Expected Output:**
```
✓ EXPIRY DATE UPDATED SUCCESSFULLY
============================================================
...Days Remaining: 365 days
Status: OK
Message: ✓ Software active. Expires in 365 days
```

**What to Check:**
- ✓ Shows status as "OK"
- ✓ Message is positive (green)
- ✓ license_config.json is updated

**Start the application:**
```bash
python main.py
```

**Expected GUI display:**
- Green status bar at top showing "Software active. Expires in 365 days"
- No warning dialogs appear
- Welcome message includes license info

---

## Test 3: Set Warning Expiry Date (WARNING Status)

Test 7-30 day warning range.

**Command:**
```bash
python set_expiry.py 2024-11-25
# Sets expiry to approximately 12 days from now
```

**Expected Output:**
```
Status: WARNING
Message: 🟡 WARNING: Software expires in 12 days
```

**Start the application:**
```bash
python main.py
```

**Expected Behavior:**
- Orange status bar at top
- Pop-up dialog appears: "Notice: Software Expiring"
- Shows warning about approaching expiry
- Allows user to click OK to continue

---

## Test 4: Set Critical Expiry Date (CRITICAL Status)

Test 0-7 day critical range.

**Command:**
```bash
python set_expiry.py 2024-11-17
# Sets expiry to approximately 4 days from now
```

**Expected Output:**
```
Status: CRITICAL
Message: 🔴 CRITICAL: Software expires in 4 days
```

**Start the application:**
```bash
python main.py
```

**Expected Behavior:**
- Red status bar at top
- Pop-up dialog appears: "Critical: Software Expiring Soon"
- Shows urgent warning with red indicator
- Suggests planning for license renewal
- Allows user to click OK to continue (for testing)

---

## Test 5: Set Past Expiry Date (EXPIRED Status)

Test that expired software blocks access.

**Command:**
```bash
python set_expiry.py 2024-11-10
# Sets expiry to past date
```

**Expected Output:**
```
Status: EXPIRED
Message: 🔴 SOFTWARE EXPIRED! Expired on 2024-11-10
```

**Start the application:**
```bash
python main.py
```

**Expected Behavior:**
- Red error dialog appears: "Software Expired"
- Shows expiry date clearly
- States "cannot start"
- Application closes without showing main GUI
- Error logged in logs/fbr_check_log.txt

---

## Test 6: GUI Features

### Status Bar Display

1. Set OK status:
   ```bash
   python set_expiry.py 2026-12-31
   ```
   
   **Check:**
   - Green bar at top ✓
   - Shows message "Software active..."
   - "Details" button visible

2. Click "Details" button
   
   **Check:**
   - Dialog shows full license information
   - Displays all status fields
   - Shows timestamps

---

## Test 7: License Config File

Check that configuration is saved correctly.

**File Location:**
```
license_config.json
```

**Check the file content:**
```bash
cat license_config.json
```

**Expected Content After Setting Date:**
```json
{
    "expiry_date": "2026-12-31",
    "created_date": "2024-11-13 10:30:00",
    "last_updated": "2024-11-13 12:00:00",
    "software_version": "1.0.0"
}
```

**What to Check:**
- ✓ expiry_date field matches what you set
- ✓ last_updated shows recent timestamp
- ✓ JSON is valid (no formatting errors)

---

## Test 8: Persistence Test

Verify settings persist across restarts.

**Steps:**
1. Set expiry date:
   ```bash
   python set_expiry.py 2025-06-30
   ```

2. Check status:
   ```bash
   python set_expiry.py info
   # Should show 2025-06-30
   ```

3. Close application and restart computer

4. Check status again:
   ```bash
   python set_expiry.py info
   # Should still show 2025-06-30
   ```

**Expected:**
- ✓ Date persists across restarts
- ✓ Timestamp updated only when changed

---

## Test 9: Date Format Validation

Test that invalid formats are rejected.

**Invalid Format Tests:**

```bash
# Test 1: MM/DD/YYYY format
python set_expiry.py 12/31/2025
# Expected: ❌ FAILED - Invalid date format

# Test 2: DD-MM-YYYY format
python set_expiry.py 31-12-2025
# Expected: ❌ FAILED - Invalid date format

# Test 3: Wrong delimiters
python set_expiry.py 2025/12/31
# Expected: ❌ FAILED - Invalid date format
```

**Valid Format Tests:**

```bash
# All valid:
python set_expiry.py 2025-12-31  ✓
python set_expiry.py 2026-01-01  ✓
python set_expiry.py 2024-06-15  ✓
```

---

## Test 10: GUI Refresh Test

Verify license status updates in real-time.

**Steps:**
1. Start application:
   ```bash
   python main.py
   ```

2. Note the expiry date in status bar

3. Without closing the app, open another terminal:
   ```bash
   python set_expiry.py 2026-12-31
   ```

4. Back in main application, note that status bar may not update immediately (application needs restart to reflect changes)

5. Restart the application:
   ```bash
   python main.py
   ```

**Expected:**
- ✓ Status bar updates with new date
- ✓ Color changes appropriately

---

## Test 11: Logging Test

Verify expiry events are logged.

**Check logs:**
```bash
cat logs/fbr_check_log.txt
```

**Expected entries:**
```
INFO - ==============================================================
INFO - SOFTWARE LICENSE INFORMATION
INFO - ==============================================================
INFO - Expiry Date: 2025-12-31
INFO - Days Remaining: 365 days
INFO - Status: OK
```

**When setting expiry:**
```
INFO - License loaded from config. Expiry date: 2025-12-31
```

**When setting new expiry:**
```
INFO - Expiry date updated to: 2025-12-31
INFO - License config saved successfully
```

---

## Test 12: End-to-End Workflow

Complete workflow simulation:

**Step 1: Initial Setup**
```bash
python set_expiry.py 2026-12-31
# New software with 1+ year expiry
```

**Step 2: Run Application**
```bash
python main.py
# Should show green status, no warnings
```

**Step 3: Simulate 1 Year Later (Approach Warning)**
```bash
python set_expiry.py 2024-11-25
# Now 12 days until expiry
```

**Step 4: Run Application Again**
```bash
python main.py
# Should show orange status, warning dialog
```

**Step 5: Admin Renews License**
```bash
python set_expiry.py 2026-12-31
# Renewed for another year
```

**Step 6: Verify Renewal**
```bash
python set_expiry.py info
# Should show updated date and "OK" status
```

---

## Troubleshooting Tests

### Test: Missing Config File

1. Delete `license_config.json`
2. Run:
   ```bash
   python set_expiry.py info
   ```

**Expected:**
- New config file is created
- Shows default expiry: 2025-12-31

### Test: Corrupted Config File

1. Open `license_config.json` and break the JSON formatting
2. Run:
   ```bash
   python set_expiry.py info
   ```

**Expected:**
- Error is logged
- Fallback to default date
- Application still runs with default

### Test: Invalid Date in Config

1. Manually edit license_config.json with invalid date
2. Run:
   ```bash
   python main.py
   ```

**Expected:**
- Error is caught
- Default date used as fallback
- Application still starts

---

## Performance Test

Test that license checks don't slow down startup.

**Steps:**
1. Check startup time without license system
2. Check startup time with license system
3. Note the time difference

**Expected:**
- Minimal startup delay (< 100ms)
- License check should be nearly instantaneous

---

## Summary Checklist

- [ ] Status info command works
- [ ] Setting future date works (OK status)
- [ ] Setting near-term date works (WARNING status)
- [ ] Setting very near date works (CRITICAL status)
- [ ] Setting past date blocks application (EXPIRED)
- [ ] GUI shows status bar correctly
- [ ] Details button shows information
- [ ] License config file is created and updated
- [ ] Settings persist across restarts
- [ ] Invalid date formats are rejected
- [ ] Events are logged correctly
- [ ] No performance impact on startup

---

## Test Data Reference

| Scenario | Date to Set | Expected Status | Days Left | Color |
|----------|------------|-----------------|-----------|-------|
| Test Normal | 2026-12-31 | OK | 365+ | 🟢 Green |
| Test Warning | 2024-11-25 | WARNING | 12 | 🟡 Orange |
| Test Critical | 2024-11-17 | CRITICAL | 4 | 🔴 Red |
| Test Expired | 2024-11-10 | EXPIRED | -3 | 🔴 Red |

---

All tests complete! Your expiry system is working correctly. 🎉
