# ⚡ EXPIRY SYSTEM - QUICK REFERENCE CARD

## 🎯 TL;DR (Too Long; Didn't Read)

Your software now expires on **2025-12-31** by default.

### To Change It:
```bash
python set_expiry.py gui              # GUI (easiest)
python set_expiry.py 2025-12-31       # CLI
python set_expiry.py info             # Check status
```

### To Use It:
```bash
python main.py                        # Run normally
```

---

## 📋 Quick Commands

| What You Want | Command |
|--------------|---------|
| Check current status | `python set_expiry.py info` |
| Open GUI tool | `python set_expiry.py gui` |
| Set expiry to 2025-12-31 | `python set_expiry.py 2025-12-31` |
| Run the app | `python main.py` |
| Help/usage | `python set_expiry.py` |

---

## 🎨 What You'll See

### Green Status (OK)
```
🟢 ✓ Software active. Expires in 365 days (2026-12-31)
```
→ Everything fine, continue normally

### Orange Status (WARNING)
```
🟡 WARNING: Software expires in 15 days (2024-11-28)
```
→ Warning dialog appears, but you can continue

### Red Status (CRITICAL)
```
🔴 CRITICAL: Software expires in 5 days (2024-11-18)
```
→ Urgent warning dialog appears

### Red Status (EXPIRED)
```
🔴 SOFTWARE EXPIRED! Expired on 2024-11-10
```
→ Software won't start, must renew

---

## 📅 Date Format

### ✅ CORRECT: `YYYY-MM-DD`
```
2025-12-31    ✓
2026-01-15    ✓
2024-06-30    ✓
```

### ❌ WRONG: Everything Else
```
12/31/2025    ✗
31-12-2025    ✗
2025/12/31    ✗
December 31   ✗
```

---

## 🚨 Common Issues

| Problem | Solution |
|---------|----------|
| "Software Expired" | `python set_expiry.py 2026-12-31` |
| Invalid date error | Use format: `YYYY-MM-DD` |
| Can't find set_expiry.py | Make sure you're in app root directory |
| License file missing | Restart app - auto-creates |

---

## 📞 Get Help

| Need | File to Read |
|------|--------------|
| Super quick start | This file (you're reading it!) |
| Quick reference | `EXPIRY_QUICK_START.md` |
| Complete guide | `LICENSE_GUIDE.md` |
| Testing procedures | `EXPIRY_TESTING_GUIDE.md` |
| Diagrams | `EXPIRY_VISUAL_GUIDE.md` |

---

## ⏰ Timeline Example

```
Today (Nov 13)      Oct 13          Oct 21          Oct 30
├─────────────────────┬──────────────┬─────────────┤
│                     │              │             │
🟢 OK (130 days)     🟢 OK (100d)   🟡 WARNING   🔴 CRITICAL
                                    (30 days)     (7 days)
                     Oct 31
                     ├────────────────────────┤
                     🔴 EXPIRED (software blocked)
```

---

## 🛠️ For Admins Only

### Create 90-Day Trial
```bash
# Today: Nov 13, 2024
# 90 days later: Feb 11, 2025
python set_expiry.py 2025-02-11
```

### Renew Annual License
```bash
# Extend for 1 more year
python set_expiry.py 2025-11-13
```

### Emergency Block
```bash
# Need to stop usage immediately
python set_expiry.py 2024-11-13
```

### Check Current License
```bash
python set_expiry.py info
```

---

## 💡 Pro Tips

1. **Plan ahead**: Set expiry before trial ends
2. **Monitor logs**: Check `logs/fbr_check_log.txt` for expiry events
3. **Test before production**: Try a test date first
4. **Schedule renewal**: Mark calendar 30 days before expiry
5. **Backup config**: Keep copy of `license_config.json`

---

## 🎓 Examples

### Example 1: Setting Trial to Expire in 30 Days
```bash
# Calculate: Today + 30 days
# If today is Nov 13, 2024, then 30 days = Dec 13, 2024

python set_expiry.py 2024-12-13
```

### Example 2: Setting Annual License
```bash
python set_expiry.py 2025-11-13
```

### Example 3: Checking Before Expiry
```bash
python set_expiry.py info
# Output shows: "365 days remaining"
```

### Example 4: Renewing at Last Minute
```bash
# Software showing red CRITICAL warning
python set_expiry.py 2026-11-13
# Problem solved!
```

---

## 🎯 Responsibility Matrix

| Role | Command | When |
|------|---------|------|
| **User** | `python main.py` | Daily use |
| **Admin** | `python set_expiry.py gui` | When setting up |
| **Admin** | `python set_expiry.py info` | Before expiry |
| **Admin** | `python set_expiry.py 2025-12-31` | When renewing |

---

## 📊 Reference Table

| Days Until Expiry | Status | Color | Dialog | Can Use? |
|------------------|--------|-------|--------|----------|
| > 30 | OK | 🟢 | None | ✅ Yes |
| 7-30 | WARNING | 🟡 | Info | ✅ Yes |
| 0-6 | CRITICAL | 🔴 | Warning | ✅ Yes |
| < 0 | EXPIRED | 🔴 | Error | ❌ No |

---

## ✨ Magic Shortcuts

### View Everything at Once
```bash
python set_expiry.py info
```

### Set & Done
```bash
python set_expiry.py 2025-12-31
```

### GUI Wizard
```bash
python set_expiry.py gui
```

### Run App
```bash
python main.py
```

---

## 🔍 Finding Your Expiry Date

### In GUI
Look at top of window - color-coded status bar shows date

### In Terminal
```bash
python set_expiry.py info
# Shows "Expiry Date: 2025-12-31"
```

### In File
```bash
# Open license_config.json
# Look for: "expiry_date": "2025-12-31"
```

---

## 🚀 Get Started Right Now

```bash
# Step 1: Check what you have
python set_expiry.py info

# Step 2: Set your expiry date (use your own date!)
python set_expiry.py 2025-12-31

# Step 3: Run the app
python main.py

# Done! 🎉
```

---

## 🎯 One-Page Summary

```
╔════════════════════════════════════════════════════════╗
║         EXPIRY SYSTEM - ONE-PAGE GUIDE                 ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  CHECK STATUS:  python set_expiry.py info            ║
║  SET DATE:      python set_expiry.py 2025-12-31      ║
║  OPEN GUI:      python set_expiry.py gui             ║
║  RUN APP:       python main.py                       ║
║                                                        ║
║  DATE FORMAT: YYYY-MM-DD (not MM/DD/YYYY)            ║
║  EXAMPLE: 2025-12-31 (not 12/31/2025)                ║
║                                                        ║
║  GREEN:   OK (> 30 days)     → Continue              ║
║  ORANGE:  WARNING (7-30d)    → Heads up              ║
║  RED:     CRITICAL (< 7d)    → Urgent!               ║
║  RED:     EXPIRED (past)     → BLOCKED               ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

---

## 🆘 Emergency Support

**Software won't start?**
```bash
python set_expiry.py 2025-12-31
```

**Don't know the date?**
```bash
python set_expiry.py info
```

**Need help?**
→ Read: `LICENSE_GUIDE.md`

**Still stuck?**
→ Check: `EXPIRY_QUICK_START.md`

---

## ✅ Verification

After setting expiry, verify it worked:
```bash
python set_expiry.py info
# Should show your new date
```

---

**That's it! You're all set.** 🎉

For more information, see the detailed guides in the documentation folder.
