# Auto-Update System - Quick Reference

## ⚡ Quick Start (30 seconds)

### Add to your main.py:
```python
from updater import check_and_apply_updates

# At app startup:
success, message = check_and_apply_updates()
print(message)
if "restart" in message.lower():
    input("Press Enter to restart...")
    sys.exit(0)
```

---

## 📦 Files Created

| File | Purpose |
|------|---------|
| `version.txt` | Stores current version (e.g., "1.0") |
| `update_checker.py` | Checks GitHub for new releases |
| `update_downloader.py` | Downloads update files |
| `update_installer.py` | Installs updates safely |
| `updater.py` | Main orchestrator (use this!) |

---

## 🚀 Common Use Cases

### 1. Automatic Startup Check
```python
from updater import check_and_apply_updates
success, msg = check_and_apply_updates()
```

### 2. Manual Button
```python
from updater import Updater
updater = Updater()
available, release = updater.check_for_updates()
if available:
    print(f"New: {release['tag_name']}")
```

### 3. With Progress
```python
def progress(down, total):
    print(f"{(down/total)*100:.0f}%", end='\r')

check_and_apply_updates(progress_callback=progress)
```

---

## 🔧 GitHub Release Setup

1. Go to: https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match/releases/new

2. **Tag:** `v1.0`, `v1.1`, `v1.2` (must start with 'v')

3. **Attach ZIP** containing your app files

4. **Publish!**

---

## 📝 Version Management

**Current version** is stored in `version.txt`:
```
1.0
```

**GitHub tags** should be: `v1.0`, `v1.1`, `v1.2`

The updater automatically compares them!

---

## ✅ Testing Checklist

- [ ] Created `version.txt` with current version
- [ ] Created GitHub release with higher version (e.g., v1.1)
- [ ] Attached ZIP file to release
- [ ] ZIP contains app files (not in subfolder)
- [ ] Run `python updater.py` to test
- [ ] Check logs for errors

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No updates" but new release exists | Check version.txt format (no 'v', no spaces) |
| Download timeout | Check internet connection |
| ZIP extraction fails | Ensure files are at ZIP root, not in folder |
| Permission denied | Run as administrator or check folder permissions |

---

## 📚 Documentation

For detailed docs, see: `AUTO_UPDATE_DOCUMENTATION.md`

For examples, run: `python example_integration.py`

---

## 🔑 Key Functions

```python
# Simple (recommended)
from updater import check_and_apply_updates
success, message = check_and_apply_updates()

# Advanced
from updater import Updater
updater = Updater()
available, release = updater.check_for_updates()
if available:
    file = updater.download_update(release)
    success = updater.install_update(file, release['tag_name'])
```

---

## ⚠️ Important Notes

- ✅ **No GitHub token required** - uses public API
- ✅ **Automatic backup** - creates backup before updating
- ✅ **Automatic rollback** - restores on failure
- ✅ **PyInstaller compatible** - works with EXE files
- ⚠️ **Restart required** - app must restart after update
- ⚠️ **Internet required** - for checking and downloading

---

## 📞 Support

Check logs: `logs/fbr_check_log.txt`

Test manually: `python updater.py`

---

Made for FBR Invoice Checker | Version 1.0
