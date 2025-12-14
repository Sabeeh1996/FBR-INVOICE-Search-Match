# Quick Deployment Guide - Different Networks

## For Installations on Different Client Networks

Since each client is on a **different network**, deployment is very simple!

### ✅ Recommended Deployment Method

**1. Package Your Application**
```
FBR-Invoice-Checker/
├── main.py
├── gui.py
├── fbr_checker.py
├── excel_handler.py
├── license_manager.py
├── version_manager.py
├── single_instance.py
├── mac_auth.py
├── license_config.json  (with expiry date)
├── version.txt
└── assets/
```

**2. Deploy to Each Client**
- Copy entire folder to client's computer
- No need to pre-configure MAC addresses
- No need to modify mac_config.json

**3. First Run (Auto-Authorization)**
- Client runs the application
- MAC address automatically authorized
- `mac_config.json` created with client's MAC
- Application locked to that device

**4. Done!**
- Each client has independent configuration
- No MAC conflicts between clients
- No central management needed

---

## Deployment Scenarios

### Scenario 1: Simple Copy & Run (Auto-Auth)
```bash
# On your computer: Package the app
zip -r FBR-Invoice-Checker.zip FBR-Invoice-Checker/

# Send to client
# Client extracts and runs
python main.py
```
✅ **Auto-authorizes on first run**

---

### Scenario 2: Pre-Configure Binding Mode
If you want to lock to first device permanently:

**Before deployment:**
1. Create/edit `mac_config.json`:
```json
{
    "mode": "binding",
    "authorized_macs": [],
    "bound_mac": null,
    "allow_first_run": true,
    "show_mac_info": true
}
```

2. Deploy to client
3. First run binds to their device permanently
4. Cannot be transferred to another device

---

### Scenario 3: Disable MAC Check (Testing)
For testing or trial period:

**mac_config.json:**
```json
{
    "mode": "disabled",
    "authorized_macs": [],
    "bound_mac": null,
    "allow_first_run": true,
    "show_mac_info": true
}
```

---

## Key Benefits for Different Networks

✅ **No MAC Conflicts**
- Each network has unique MAC addresses
- No coordination needed between clients

✅ **Independent Configurations**
- Each client has their own `mac_config.json`
- No central database required

✅ **Simple Deployment**
- Just copy and run
- Auto-authorization works perfectly

✅ **Secure by Default**
- First run locks to device
- Cannot be copied within client's network

---

## What Happens on First Run?

```
1. Application starts
2. Detects MAC address: AA:BB:CC:DD:EE:FF
3. Checks mac_config.json (empty or doesn't exist)
4. Auto-authorizes this MAC address
5. Saves to mac_config.json:
   {
       "authorized_macs": ["hash_of_AA:BB:CC:DD:EE:FF"],
       ...
   }
6. Application runs normally
```

**On subsequent runs:**
```
1. Application starts
2. Detects MAC address: AA:BB:CC:DD:EE:FF
3. Checks mac_config.json
4. Finds authorized hash
5. ✅ Access granted
```

**If copied to different computer in same network:**
```
1. Application starts
2. Detects MAC address: 11:22:33:44:55:66
3. Checks mac_config.json
4. MAC not in authorized list
5. ❌ "Device Not Authorized" error
```

---

## Client Instructions

Send this to your clients:

### Installation Steps

1. **Extract Files**
   - Extract all files to a folder (e.g., `C:\FBR-Invoice-Checker\`)

2. **Run Application**
   - Double-click `main.py` or run the executable
   - On first run, application will authorize your device

3. **Done!**
   - Application is now ready to use
   - It will only work on this computer

### Important Notes
- Application is licensed to THIS computer only
- Do not copy to other computers
- MAC address authorization protects the license
- Contact support if you need to change computers

---

## Troubleshooting

### Client Reports "Device Not Authorized"

**Cause:** They copied application from another computer

**Solution:**
```bash
# On their computer, run:
python manage_mac.py
# Select option 3 (Authorize New MAC Address)
# Enter "current"
```

### Need to Transfer License to New Computer

**Option 1: Reset Configuration**
- Delete `mac_config.json` on new computer
- Run application (will auto-authorize)

**Option 2: Pre-authorize New MAC**
- Get new computer's MAC address
- Use `manage_mac.py` to authorize it
- Transfer `mac_config.json` to new computer

---

## Configuration Files Per Client

Each client should have:
```
license_config.json  → Their license expiry
mac_config.json      → Their MAC authorization
version.txt          → Application version
```

**Do NOT share mac_config.json between clients!**
Each client gets their own independent configuration.

---

## Security Features

✅ Each client's MAC address is hashed (SHA256)
✅ Config file is specific to their device
✅ Cannot be copied to unauthorized devices
✅ Works offline (no internet check needed)
✅ No central server required

---

## Summary

**For Different Networks:**
1. ✅ Copy entire application folder to client
2. ✅ Client runs application
3. ✅ Auto-authorization happens
4. ✅ Application locked to that device
5. ✅ No manual configuration needed!

**It's that simple!**
