# 🔐 Simple MAC Control Guide - For Non-Technical Users

**Control your application access remotely using GitHub - NO coding required!**

---

## 📋 Quick Overview

When someone runs your application for the first time on their computer:
1. ✅ The application auto-authorizes their device
2. 📧 You receive a notification with their device details
3. 🔑 You can later revoke access if needed using GitHub

---

## 🎯 Two Easy Ways to Control Access

### **Method 1: Using Your Computer (Easiest)**

Run the control panel on your computer:

```bash
python mac_control_panel.py
```

**What you can do:**
- ✅ View all authorized devices
- 📱 See new device notifications
- ➕ Manually add devices
- ❌ Remove/revoke device access
- 🗑️ Clear all devices

**Example Workflow:**
1. Someone runs the app → you get notification
2. Open control panel → see their device info
3. If they shouldn't have access → remove their device
4. Commit and push to GitHub (see Method 2)

---

### **Method 2: Using GitHub Website (Most Powerful)**

**You can control access from ANYWHERE using just a web browser!**

#### Step 1: Go to GitHub File

Open this URL in your browser:
```
https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match/blob/develop/mac_whitelist.json
```

#### Step 2: Edit the File

1. Click the **pencil icon** (✏️) in top-right corner
2. You'll see something like this:

```json
{
  "mode": "github_whitelist",
  "authorized_macs": [
    "abc123def456...",
    "xyz789uvw012..."
  ],
  "last_updated": "2025-12-14T10:30:00Z"
}
```

#### Step 3: Make Changes

**To REMOVE access (revoke a device):**
- Just **delete the line** with their MAC hash
- Remove the comma if needed

**Before:**
```json
"authorized_macs": [
  "abc123def456...",
  "xyz789uvw012..."
]
```

**After (removed first device):**
```json
"authorized_macs": [
  "xyz789uvw012..."
]
```

**To ADD a device manually:**
- Get their MAC hash from notification email/Telegram
- Add it to the list with a comma

```json
"authorized_macs": [
  "xyz789uvw012...",
  "new123device456..."
]
```

**To BLOCK ALL devices:**
- Clear the list to empty

```json
"authorized_macs": []
```

#### Step 4: Save Changes

1. Scroll down to bottom of page
2. In "Commit changes" box, type: `Revoke access for device X`
3. Click **"Commit changes"** button

**That's it!** ✅

---

## 🚀 How It Works

```
┌─────────────────────────────────────────────────────────┐
│  User runs app on their computer                        │
│  ↓                                                       │
│  App checks MAC address                                 │
│  ↓                                                       │
│  App fetches mac_whitelist.json from GitHub             │
│  ↓                                                       │
│  If MAC not in list → Auto-authorize + Notify you       │
│  If MAC in list → Allow access                          │
│  If MAC removed from list → Block access                │
└─────────────────────────────────────────────────────────┘
```

**Changes take effect IMMEDIATELY** on next app startup!

---

## 📬 Finding Device Information

### Where to Find MAC Hashes

**Option 1: Check Notifications Folder**
- On your computer, go to: `first_run_notifications/`
- Each file contains device details
- Copy the `mac_address_hash` value

**Option 2: Use Control Panel**
```bash
python mac_control_panel.py
# Choose option 4: View Notifications
```

**Option 3: Telegram/Email** (if configured)
- You'll receive instant notification with MAC hash
- Just copy-paste the hash into GitHub

---

## 🛡️ Common Scenarios

### Scenario 1: Temporary Access
**Someone needs to use it for a week, then you want to revoke:**

1. They run app → auto-authorized → you get notification ✅
2. After 1 week → go to GitHub → remove their MAC hash
3. Next time they try to run → **BLOCKED** ❌

### Scenario 2: Pre-Approve Multiple Devices
**You want to setup 5 computers before giving them the app:**

1. Run app on each computer → get 5 notifications
2. Go to GitHub → verify all 5 MACs are in the list
3. Distribute app to users → all work immediately ✅

### Scenario 3: Emergency Lockdown
**You need to block EVERYONE immediately:**

1. Go to GitHub → edit `mac_whitelist.json`
2. Clear `authorized_macs` to: `[]`
3. Commit → **ALL devices blocked** 🚫

### Scenario 4: Stolen/Lost Device
**A laptop with your app was stolen:**

1. Check notifications → find the device MAC hash
2. Go to GitHub → remove that specific hash
3. Stolen device can no longer run app ✅

---

## 🎨 Visual Guide

### GitHub Edit Process (Screenshots Guide)

**Step 1: Navigate to file**
```
GitHub.com → Your Repo → develop branch → mac_whitelist.json
```

**Step 2: Click edit (pencil icon)**
```
┌─────────────────────────────────────────┐
│  mac_whitelist.json              [✏️]   │
└─────────────────────────────────────────┘
```

**Step 3: Make changes**
```json
{
  "authorized_macs": [
    "keep_this_device",
    "remove_this_device",  ← DELETE THIS LINE
    "keep_this_one_too"
  ]
}
```

**Step 4: Commit**
```
┌─────────────────────────────────────────┐
│ Commit changes                           │
│ ─────────────────────────────────────── │
│ Removed unauthorized device              │
│                                          │
│ [Commit changes] button                  │
└─────────────────────────────────────────┘
```

---

## ⚡ Quick Reference Card

| **Action** | **Method** | **Time** |
|------------|------------|----------|
| View authorized devices | Control panel or GitHub | 10 sec |
| Remove one device | Edit GitHub, delete line | 30 sec |
| Block all devices | Edit GitHub, clear array | 30 sec |
| Add device manually | Copy hash, add to GitHub | 60 sec |
| Emergency lockdown | Edit GitHub, empty array | 20 sec |

---

## 💡 Pro Tips

1. **Bookmark the GitHub edit URL** for quick access
2. **Use Telegram bot** for instant notifications (easier than email)
3. **Keep notifications folder** as backup record of all devices
4. **Test on your own device first** before distributing
5. **Use descriptive commit messages** like "Removed John's laptop"

---

## 🔥 Advanced: Blocking by Default

If you want **manual approval** for every device (instead of auto-authorize):

Edit `mac_config.json` in your build:
```json
{
  "mode": "whitelist",
  "authorized_macs": [],
  "allow_first_run": false  ← Change this to false
}
```

Now users MUST be pre-approved in GitHub before they can run the app.

---

## 📞 Support

**Common Issues:**

**Q: Changes in GitHub not working?**  
A: User needs to restart the application. Changes fetch on startup.

**Q: Can't edit GitHub file?**  
A: Make sure you're logged into GitHub and have write access to the repo.

**Q: Lost all MAC hashes?**  
A: Check `first_run_notifications/` folder for backup records.

**Q: Want to change GitHub URL?**  
A: Edit the URL in `mac_auth.py` line 30 (or use custom URL in code).

---

## ✅ Checklist

- [ ] I know how to edit `mac_whitelist.json` on GitHub
- [ ] I can find device MAC hashes from notifications
- [ ] I tested blocking and unblocking a device
- [ ] I have Telegram/Email notifications configured (optional)
- [ ] I bookmarked the GitHub file URL for quick access

---

**You're all set!** 🎉

You now have complete remote control over who can use your application, 
without writing a single line of code. Just edit a file on GitHub!
