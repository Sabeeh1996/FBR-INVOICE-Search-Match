# MAC Address Authentication System

## Overview
The MAC address authentication system restricts the FBR Invoice Checker application to run only on authorized devices. This provides an additional layer of security and license control.

## How It Works

The system identifies each computer by its unique MAC (Media Access Control) address and maintains a list of authorized devices.

### Authentication Modes

1. **Whitelist Mode** (Default)
   - Maintains a list of authorized MAC addresses
   - Supports multiple devices
   - Best for teams or multiple installations

2. **Binding Mode**
   - License is bound to a single device on first use
   - Cannot be transferred to another device
   - Best for single-user licenses

3. **Disabled Mode**
   - MAC authentication is turned off
   - No device restrictions

## Setup Instructions

### Deployment to Client (Different Networks)

**Simple Deployment (Recommended for different networks):**

1. **Copy entire application folder** to client's computer
2. Client runs `python main.py` (or the executable)
3. Application automatically authorizes their device on first run
4. `mac_config.json` is created and saved
5. ✅ Done! Application is now locked to that device

**Important:** Each client on different network gets fresh installation with auto-authorization. No manual MAC address management needed!

### First Installation (Same Network - Multiple Devices)

1. Install the application on the target device
2. Run the application once - it will auto-authorize the first device
3. Configuration file `mac_config.json` will be created

### Adding More Devices (Same Network Only)

#### Option 1: Using Management Utility (Recommended)

```bash
python manage_mac.py
```

Then select:
- Option 1: View current device MAC address
- Option 3: Authorize a new MAC address

#### Option 2: Manual Authorization

1. On the new device, run the application
2. Note the MAC address from the error message
3. On an authorized device, run `python manage_mac.py`
4. Choose "Authorize New MAC Address"
5. Enter the MAC address (format: XX:XX:XX:XX:XX:XX)

### Getting Device MAC Address

**Method 1: Run the application**
- The error message will display the MAC address if not authorized

**Method 2: Use management utility**
```bash
python manage_mac.py
```
Select option 1 to view current device MAC address

**Method 3: System commands**

Windows:
```cmd
getmac
```

Linux/Mac:
```bash
ifconfig
# or
ip link show
```

## Configuration File

The `mac_config.json` file stores the MAC authentication settings:

```json
{
    "mode": "whitelist",
    "authorized_macs": [
        "hash1...",
        "hash2..."
    ],
    "bound_mac": null,
    "allow_first_run": true,
    "show_mac_info": true
}
```

### Configuration Options

- **mode**: Authentication mode (`whitelist`, `binding`, `disabled`)
- **authorized_macs**: List of authorized MAC address hashes (encrypted for security)
- **bound_mac**: MAC address hash for binding mode
- **allow_first_run**: Auto-authorize first device (true/false)
- **show_mac_info**: Show MAC address in error messages (true/false)

## Management Commands

### View Current Device Info
```bash
python manage_mac.py
# Select option 1
```

### Authorize Current Device
```bash
python manage_mac.py
# Select option 3, then enter "current"
```

### Authorize Another Device
```bash
python manage_mac.py
# Select option 3, then enter MAC address
```

### Revoke Device Access
```bash
python manage_mac.py
# Select option 4, then enter MAC address
```

### Change Authentication Mode
```bash
python manage_mac.py
# Select option 6
```

### Disable MAC Authentication
```bash
python manage_mac.py
# Select option 7
```

## Distribution Strategy

### For Installations on Different Networks (Recommended)

Since each client is on a different network, each installation gets its own unique configuration:

**Method 1: Auto-Authorization (Simplest)**
1. Copy application to client's computer
2. Client runs application first time
3. Application auto-authorizes that device
4. Client's `mac_config.json` is created automatically
5. Application is now locked to that device

**Method 2: Pre-Authorization**
1. Get client's MAC address beforehand
2. Create `mac_config.json` with their MAC authorized
3. Set `"allow_first_run": false` to prevent auto-auth
4. Deploy with pre-configured file

**Method 3: Binding Mode (Most Secure)**
1. Set mode to "binding" in config
2. Application binds to first device permanently
3. Cannot be transferred or copied

### For Multiple Devices (Same Client, Same Network)

1. **Whitelist Mode**
   - Keep default whitelist mode
   - Pre-authorize all client MAC addresses
   - Share `mac_config.json` with the installation

### Important: Network Isolation Benefits

✅ **Each network = Separate installation**
- No MAC address conflicts between clients
- Each client has independent configuration
- MAC addresses don't need to be globally unique
- Simple deployment: just copy application folder

## Security Features

✅ **MAC addresses are hashed** - Not stored in plain text
✅ **Stale MAC detection** - Automatically handles changed network adapters
✅ **Process validation** - Verifies running processes
✅ **Tamper protection** - Detects config file modifications

## Troubleshooting

### "Device Not Authorized" Error

**Solution:**
1. Note the MAC address from error message
2. Run `python manage_mac.py` on authorized device
3. Add the MAC address to authorized list

### Application Works on One Computer but Not Another

**Cause:** Different MAC addresses
**Solution:** Authorize the new device's MAC address

### MAC Address Changed After Network Adapter Change

**Solution:**
1. Get new MAC address
2. Authorize it using management utility
3. Optionally revoke old MAC address

### "Unable to Detect MAC Address" Error

**Solution:**
1. Check network adapter is enabled
2. Ensure network drivers are installed
3. Try running as administrator
4. Temporarily disable MAC authentication if needed

## Best Practices

1. **Backup Configuration**
   - Keep backup of `mac_config.json`
   - Store authorized MAC addresses list separately

2. **Document Installations**
   - Maintain list of client MAC addresses
   - Record which devices are authorized

3. **Regular Audits**
   - Periodically review authorized devices
   - Remove unused MAC addresses

4. **Test Before Distribution**
   - Test on target device before deploying
   - Verify MAC authentication works correctly

## Integration with License System

The MAC authentication works alongside the existing license system:

1. License expiry check runs first
2. MAC address check runs second
3. Both must pass for application to run

## Support

For issues or questions:
- Check the management utility for current status
- Review logs in `logs/fbr_check_log.txt`
- Contact administrator with MAC address information
