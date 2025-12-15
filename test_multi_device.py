"""
Test Multi-Device MAC Authentication
Demonstrates multiple device support
"""

from mac_auth import MACAuthenticator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    print("=" * 70)
    print("Testing Multi-Device MAC Authentication")
    print("=" * 70)
    print()
    
    # Initialize authenticator
    auth = MACAuthenticator()
    
    print("📱 CURRENT DEVICE INFORMATION")
    print("-" * 70)
    print(f"MAC Address: {auth.current_mac}")
    print(f"MAC Hash: {auth.current_mac_hash[:20]}...")
    print()
    
    # Check authorization
    print("🔐 AUTHORIZATION CHECK")
    print("-" * 70)
    is_authorized, message = auth.is_authorized()
    print(f"Status: {'✅ AUTHORIZED' if is_authorized else '❌ DENIED'}")
    print(f"Message: {message}")
    print()
    
    # Get authentication info
    print("📊 AUTHENTICATION STATISTICS")
    print("-" * 70)
    auth_info = auth.get_auth_info()
    print(f"Mode: {auth_info['mode']}")
    print(f"Total Authorized Devices: {auth_info['total_devices']}")
    print(f"Multi-Device Mode: {'Yes' if auth_info['is_multi_device'] else 'No'}")
    print()
    
    # Get device list
    print("💻 AUTHORIZED DEVICES")
    print("-" * 70)
    devices = auth.get_device_list()
    
    if devices:
        for idx, device in enumerate(devices, 1):
            status_icon = "✅" if device['status'] == 'active' else "❌"
            print(f"\nDevice #{device['device_id']}: {status_icon} {device['status'].upper()}")
            print(f"  Name: {device['device_name']}")
            print(f"  MAC: {device['mac_address']}")
            print(f"  User: {device['username']}")
            print(f"  Computer: {device['computer_name']}")
            print(f"  Authorized: {device['authorized_date'][:10]}")
            print(f"  Last Seen: {device['last_updated'][:10]}")
    else:
        print("No devices found in whitelist")
    
    print()
    print("=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
