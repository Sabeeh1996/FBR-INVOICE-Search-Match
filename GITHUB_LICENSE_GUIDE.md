# GitHub-Based License Management System

## Overview
The license management system now fetches license configuration from GitHub as the authoritative source, with local file fallback for offline use. This mirrors the MAC address whitelist system.

## Architecture

### 1. **GitHub as Authoritative Source**
   - Primary source: `https://raw.githubusercontent.com/Sabeeh1996/FBR-INVOICE-Search-Match/develop/github_license_config.json`
   - Fetched on every application startup
   - Real-time control over license status

### 2. **Local Cache for Offline Fallback**
   - File: `github_license_config.json`
   - Updated whenever GitHub is available
   - Used when GitHub is unreachable
   - Stored in AppData when running as .exe

### 3. **Legacy Local Config**
   - File: `license_config.json`
   - Used only if both GitHub and cache unavailable
   - Bundled in .exe as final fallback

## GitHub License Configuration Format

```json
{
  "_comment": "GitHub-hosted License Configuration - Central Control",
  "_instructions": [
    "ACTIVE LICENSE: Set status to 'active' and expiry_date to future date",
    "EXPIRED LICENSE: Set status to 'expired' OR set expiry_date to past date",
    "REVOKED LICENSE: Set status to 'revoked' to immediately block access",
    "Status values: 'active' = working, 'expired' = time-based block, 'revoked' = admin block"
  ],
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
  "warning_days": 15,
  "critical_days": 7
}
```

## License Status Values

| Status | Effect | Use Case |
|--------|--------|----------|
| `active` | License is valid | Normal operation |
| `expired` | License blocked by admin | Admin-controlled expiry |
| `revoked` | License immediately revoked | Emergency shutdown |

## How It Works

### Startup Flow:
```
1. Application starts
   ↓
2. Try to fetch from GitHub (AUTHORITATIVE)
   ↓
   ├─ Success → Use GitHub config & save to local cache
   │             ↓
   │          Check status & expiry date
   │
   └─ Failed → Load from local cache
               ↓
            ├─ Cache exists → Use cached config (show warning)
            │
            └─ No cache → Use bundled license_config.json
```

### Status Check Priority:
```
1. GitHub status (if 'revoked' or 'expired') → Block immediately
   ↓
2. Expiry date check → Block if past expiry
   ↓
3. Warning days → Show warnings before expiry
```

## Control Methods

### 1. **Immediate Revoke** (Emergency)
Edit `github_license_config.json` on GitHub:
```json
"license_info": {
  "status": "revoked",
  ...
}
```
Effect: All devices blocked on next startup

### 2. **Mark as Expired** (Admin Control)
```json
"license_info": {
  "status": "expired",
  ...
}
```
Effect: License blocked regardless of date

### 3. **Date-Based Expiry** (Time-Based)
```json
"license_info": {
  "status": "active",
  "expiry_date": "2025-01-01",
  ...
}
```
Effect: License expires on specified date

### 4. **Extend License**
```json
"license_info": {
  "status": "active",
  "expiry_date": "2027-12-31",
  ...
}
```
Effect: License extended, all devices updated on next startup

## Features

### ✅ Implemented
- [x] GitHub-based license control
- [x] Local cache for offline use
- [x] Status-based blocking (active/expired/revoked)
- [x] Date-based expiry
- [x] Warning notifications (15 days, 7 days)
- [x] Fallback to local config
- [x] Works with bundled .exe

### 🎯 Key Benefits
- **Centralized control** - Update license from GitHub
- **No exe rebuild** - Change license without recompiling
- **Offline support** - Works without internet (uses cache)
- **Multi-level fallback** - GitHub → Cache → Bundled config
- **Granular control** - Status + date-based expiry

## Usage for Administrators

### To Revoke All Access:
1. Edit `github_license_config.json` on GitHub
2. Set `"status": "revoked"`
3. Commit changes
4. All devices will be blocked on next startup

### To Extend License:
1. Edit `github_license_config.json` on GitHub
2. Update `"expiry_date": "2027-12-31"`
3. Keep `"status": "active"`
4. Commit changes

### To Check Current Status:
View the GitHub file:
`https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match/blob/develop/github_license_config.json`

## Files to Upload to GitHub

1. **`github_license_config.json`** - License configuration (required)
2. Keep the file public or use GitHub token for private repos

## Testing

Test the license system:
```powershell
python -c "from license_manager import LicenseManager; lm = LicenseManager(); print('Status:', lm.license_status); print('Expiry:', lm.expiry_date)"
```

## Integration with Existing Code

No changes needed to existing code. The `LicenseManager` class maintains backward compatibility:
- `is_expired()` - Now checks both status and date
- `get_expiry_status()` - Returns extended status info
- `validate_license()` - Works as before

## Next Steps

1. **Upload `github_license_config.json` to GitHub repo**
   - Path: `FBR-INVOICE-Search-Match/github_license_config.json`
   - Branch: `develop`

2. **Test with different statuses:**
   - Set to 'revoked' and test
   - Set to 'expired' and test
   - Set past date and test

3. **Rebuild .exe** with new license manager
