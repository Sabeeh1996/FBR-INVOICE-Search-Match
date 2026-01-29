# Configuration Repository Setup

## Overview
MAC address authentication and license expiration controls have been moved to a **separate private repository** for better security and management.

## Repository Structure

### Main Repository
- **Name**: `FBR-INVOICE-Search-Match`
- **Branch**: `develop`
- **Purpose**: Application source code
- **URL**: https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match

### Config Repository
- **Name**: `fbr-inv-check-expiry-mac-ogdcl`
- **Branch**: `main`
- **Purpose**: MAC whitelist and license configuration
- **URL**: https://github.com/Sabeeh1996/fbr-inv-check-expiry-mac-ogdcl
- **Security**: Must be kept **PRIVATE**

## Configuration Files

### 1. license_config.json
Located in config repository: `fbr-inv-check-expiry-mac-ogdcl/license_config.json`

```json
{
    "mode": "github_license",
    "license_info": {
        "status": "active",
        "expiry_date": "2026-12-31",
        "license_type": "full",
        "software_version": "1.1.0",
        "last_updated": "2025-12-16T00:00:00",
        "updated_by": "admin",
        "notes": "Full license - all features enabled"
    },
    "warning_days": 400,
    "critical_days": 7
}
```

**Fields**:
- `status`: "active" | "expired" | "revoked"
- `expiry_date`: YYYY-MM-DD format
- `license_type`: "full" | "trial" | "limited"

### 2. mac_whitelist.json
Located in config repository: `fbr-inv-check-expiry-mac-ogdcl/mac_whitelist.json`

```json
{
  "mode": "github_whitelist",
  "devices": [
    {
      "device_id": 1,
      "device_name": "DESKTOP-46BDVA7-sabeeh bhai 1995",
      "mac_address": "95:11:BD:A6:21:5B",
      "mac_hash": "65158b05d949d8d5afb6472965bcefcde59a8671ef106d3150886e6e7b0e493a",
      "status": "active",
      "authorized_date": "2025-12-15T20:08:03.201312",
      "notes": "Auto-authorized device #1"
    }
  ]
}
```

**Fields**:
- `status`: "active" | "revoked"
- `device_id`: Unique numeric identifier
- `mac_hash`: SHA256 hash of MAC address

## How It Works

### License Control
1. Application fetches `license_config.json` from GitHub on startup
2. Checks license status and expiry date
3. Caches locally in `github_license_config.json` for offline fallback
4. Shows warnings based on `warning_days` and `critical_days` thresholds
5. Blocks application if:
   - Status is "revoked"
   - Expiry date has passed
   - Cannot reach GitHub and local cache is expired

### MAC Address Control
1. Application calculates MAC address hash on startup
2. Fetches `mac_whitelist.json` from GitHub
3. Checks if device exists in whitelist:
   - **First run (empty whitelist)**: Auto-authorize and add to GitHub
   - **Existing device**: Check status field
     - "active" → Allow access
     - "revoked" → Block with error message
4. Caches locally in `mac_whitelist.json` for offline fallback

## Managing Devices

### To Authorize a New Device
1. First run will auto-authorize if whitelist is empty
2. Device info will be automatically pushed to GitHub repository

### To Revoke a Device
1. Open `mac_whitelist.json` in config repository
2. Find the device entry
3. Change `"status": "active"` to `"status": "revoked"`
4. Add reason in `"notes"` field
5. Commit and push changes

**Example**:
```json
{
  "device_id": 3,
  "status": "revoked",
  "notes": "Device lost - revoked on 2025-12-16"
}
```

## Managing License

### To Extend License
1. Open `license_config.json` in config repository
2. Update `"expiry_date"` to new date (YYYY-MM-DD)
3. Update `"last_updated"` to current timestamp
4. Commit and push changes

### To Revoke License
1. Open `license_config.json` in config repository
2. Change `"status": "active"` to `"status": "revoked"`
3. Add reason in `"notes"` field
4. Commit and push changes

**Example**:
```json
{
    "license_info": {
        "status": "revoked",
        "expiry_date": "2026-12-31",
        "notes": "License revoked - payment issue"
    }
}
```

## Technical Details

### GitHub Integration
- **Authentication**: Personal Access Token (configured in code)
- **URL Pattern**: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file}`
- **Cache**: GitHub CDN may cache files for a few minutes
- **Fallback**: Local cached files used if GitHub is unreachable

### Code Files
- `mac_auth.py`: MAC authentication logic
  - GitHub URL: Line 76
- `license_manager.py`: License validation logic
  - GitHub URL: Line 28

### Local Files (.gitignore)
These files are excluded from main repository:
- `license_config.json`
- `mac_whitelist.json`
- `github_license_config.json`

## Build Process

When building .exe:
```bash
python build_exe_complete.py
```

The executable will:
- Fetch config files from GitHub on each run
- Store local cache in AppData
- Use bundled fallback configs if both GitHub and cache fail

## Security Notes

1. **Keep Config Repository Private**
   - Contains sensitive device information
   - Controls application access

2. **Personal Access Token**
   - Required for GitHub API access
   - Configure with `repo` scope
   - Keep token secure

3. **MAC Address Hashing**
   - MAC addresses are hashed with SHA256
   - Original MAC stored for admin reference only

4. **Offline Support**
   - Local cache allows limited offline operation
   - Prevents GitHub outages from blocking users
   - Cache automatically updates when online

## Troubleshooting

### Application Not Fetching from GitHub
1. Check GitHub repository is accessible
2. Verify Personal Access Token is valid
3. Check file exists at expected URL
4. Wait 2-3 minutes for GitHub cache to clear

### Device Auto-Authorization Not Working
1. Ensure `devices` array is empty in GitHub whitelist
2. Check application has write access to GitHub
3. Verify GitHub token has `repo` scope

### License Changes Not Reflecting
1. Wait 2-3 minutes for GitHub cache
2. Delete local `github_license_config.json`
3. Restart application to force refresh

## Repository URLs

### Config Repository
- **Repository**: https://github.com/Sabeeh1996/fbr-inv-check-expiry-mac-ogdcl
- **License Config**: https://raw.githubusercontent.com/Sabeeh1996/fbr-inv-check-expiry-mac-ogdcl/main/license_config.json
- **MAC Whitelist**: https://raw.githubusercontent.com/Sabeeh1996/fbr-inv-check-expiry-mac-ogdcl/main/mac_whitelist.json

### Main Repository
- **Repository**: https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match
- **Branch**: develop

## Updates Complete
- ✅ Config files moved to separate repository
- ✅ URLs updated in mac_auth.py and license_manager.py
- ✅ .gitignore updated to exclude config files
- ✅ .exe rebuilt with new repository URLs
- ✅ License system tested (expires 2026-12-31, 380 days remaining)
