# 🔒 Mandatory Update System - Quick Guide

## What Changed?

Your update system now **FORCES users to update** before they can use the application.

---

## 🚀 Quick Integration

### Add this to your `main.py` startup:

```python
from updater import check_and_apply_updates
import sys

# Check for MANDATORY updates
success, message = check_and_apply_updates(force_update=True)
print(message)

if not success:
    # Update required but failed - BLOCK APP
    print("\n⛔ This application requires an update to continue.")
    input("Press Enter to exit...")
    sys.exit(1)

if "restart" in message.lower():
    # Update successful - restart required
    input("Press Enter to restart...")
    sys.exit(0)

# No update needed - continue normally
print("Starting application...")
# Your app code here
```

---

## 📋 How It Works

```
User starts app
      │
      ▼
Check GitHub for updates
      │
      ├─► No update found
      │   └─► ✓ App starts normally
      │
      └─► Update available
          │
          ▼
      Download & Install
          │
          ├─► ✓ Success → User must restart
          │
          └─► ✗ Failed → ⛔ APP BLOCKED
                          User cannot continue!
```

---

## ⚙️ Configuration

### Force Update (Default - Recommended)
```python
check_and_apply_updates(force_update=True)  # Users MUST update
```

### Optional Update
```python
check_and_apply_updates(force_update=False)  # Users can skip
```

---

## 🎯 Example Scenarios

### Scenario 1: Critical Security Update
```python
# When you push v1.1 with security fixes
# All v1.0 users will be FORCED to update

from updater import check_and_apply_updates
success, message = check_and_apply_updates(force_update=True)

if not success:
    print("⛔ Security update required!")
    sys.exit(1)
```

### Scenario 2: Optional Feature Update
```python
# When you push v1.1 with new features
# Users can choose to update or skip

from updater import check_and_apply_updates
success, message = check_and_apply_updates(force_update=False)

if not success:
    print("Update available but failed. Continuing with current version...")
# App continues normally
```

---

## 📝 User Experience

### When Update is Available (Mandatory):

```
================================
FBR INVOICE CHECKER - Starting
================================

Checking for mandatory updates...

Update available: v1.1
Downloading: [████████████] 100%

✓ Successfully updated to version 1.1!
⚠ Please restart the application to use the new version.

Press Enter to restart...
```

### If Update Fails:

```
Checking for mandatory updates...

✗ CRITICAL: Update to version 1.1 is required!
Installation failed. Please check your internet connection and try again.
The application cannot continue without this update.

⛔ APPLICATION CANNOT START

This application requires an update to continue.
Please check your internet connection and try again.

Press Enter to exit...
```

---

## 🎨 Integration Examples

### Example 1: Simple (Recommended)
```python
from updater import check_and_apply_updates
import sys

success, message = check_and_apply_updates(force_update=True)
print(message)

if not success:
    input("Press Enter to exit...")
    sys.exit(1)

if "restart" in message.lower():
    sys.exit(0)
```

### Example 2: With Progress Bar
```python
def show_progress(downloaded, total):
    percent = (downloaded / total) * 100
    print(f"\rProgress: {percent:.0f}%", end='')

success, message = check_and_apply_updates(
    progress_callback=show_progress,
    force_update=True
)
```

### Example 3: With Retry Logic
```python
max_retries = 3
for attempt in range(max_retries):
    success, message = check_and_apply_updates(force_update=True)
    
    if success:
        break
    
    if attempt < max_retries - 1:
        print("Retrying...")
else:
    print("⛔ Cannot start without update")
    sys.exit(1)
```

---

## 🔧 Publishing Updates

### Step 1: Update Your Code
Make your changes to the application

### Step 2: Increment Version
Edit `version.txt`:
```
1.1
```

### Step 3: Create GitHub Release
- Tag: `v1.1`
- Attach ZIP file
- Publish

### Step 4: All Users Will Be Forced to Update!
When users start the app, they will:
1. See "Update required" message
2. Automatically download v1.1
3. Install and restart
4. **Cannot skip or ignore**

---

## ⚠️ Important Notes

### ✅ DO This:
- Test updates thoroughly before publishing
- Ensure ZIP file is correct
- Keep version numbers incrementing
- Have a backup plan

### ❌ DON'T Do This:
- Publish untested updates (users will be forced to install)
- Break the ZIP structure (users will be blocked from app)
- Skip version numbers (can cause confusion)

---

## 🛡️ Safety Features

Even with mandatory updates:
- ✅ **Backup created** before update
- ✅ **Automatic rollback** if update fails
- ✅ **Retry option** for users
- ✅ **Clear error messages**
- ✅ **No data loss**

---

## 📞 Testing

### Test Mandatory Update:
```bash
python mandatory_update_integration.py
```

Choose example 1-4 to see how mandatory updates work.

---

## 🎯 When to Use

### Use Mandatory Updates (force_update=True) for:
- ✅ Security patches
- ✅ Critical bug fixes
- ✅ Breaking changes
- ✅ License/compliance updates
- ✅ Database schema changes

### Use Optional Updates (force_update=False) for:
- ⚪ Minor features
- ⚪ UI improvements
- ⚪ Performance tweaks
- ⚪ Non-critical fixes

---

## 💡 Pro Tips

1. **Communicate Early**: Tell users about upcoming mandatory updates

2. **Test Thoroughly**: Mandatory updates block users if they fail

3. **Monitor Releases**: Watch for issues after publishing

4. **Provide Support**: Have a manual download option as backup

5. **Version Strategy**: 
   - Major versions (2.0) = Mandatory
   - Minor versions (1.1) = Optional
   - Patches (1.0.1) = Mandatory for security

---

## 🔗 Related Files

- `updater.py` - Main update system (now with force_update)
- `mandatory_update_integration.py` - Integration examples
- `AUTO_UPDATE_DOCUMENTATION.md` - Complete docs

---

## ✅ Summary

**Before:** Users could skip updates  
**After:** Users MUST update to continue

**Default behavior:** Mandatory updates (`force_update=True`)  
**To make optional:** Set `force_update=False`

**Your integration:**
```python
from updater import check_and_apply_updates
success, msg = check_and_apply_updates(force_update=True)
if not success:
    sys.exit(1)  # Block app
```

---

**✨ Your users will always be on the latest version!**
