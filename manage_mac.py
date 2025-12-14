"""
MAC Address Management Utility
Tool for administrators to manage authorized MAC addresses.
"""

import sys
from mac_auth import MACAuthenticator


def display_menu():
    """Display the management menu."""
    print("\n" + "="*60)
    print("  FBR Invoice Checker - MAC Address Management")
    print("="*60)
    print("\n1. Show Current Device MAC Address")
    print("2. Show All Authorized MAC Addresses")
    print("3. Authorize a New MAC Address")
    print("4. Revoke a MAC Address")
    print("5. Show Authentication Status")
    print("6. Change Authentication Mode")
    print("7. Disable MAC Authentication")
    print("8. Enable MAC Authentication (Whitelist Mode)")
    print("9. Exit")
    print("\n" + "-"*60)


def show_current_mac(auth):
    """Show current device MAC address."""
    print("\n" + "="*60)
    print("  Current Device Information")
    print("="*60)
    print(f"\nMAC Address: {auth.current_mac}")
    print(f"Status: {'✓ Authorized' if auth.is_authorized()[0] else '✗ NOT Authorized'}")
    print("\nNote: Share this MAC address with administrator to authorize this device.")


def show_authorized_macs(auth):
    """Show all authorized MAC addresses (hashed for security)."""
    print("\n" + "="*60)
    print("  Authorized MAC Addresses")
    print("="*60)
    
    macs = auth.config.get("authorized_macs", [])
    if not macs:
        print("\n  No MAC addresses authorized yet.")
    else:
        print(f"\n  Total Authorized Devices: {len(macs)}")
        print("\n  MAC Address Hashes (for security, actual MACs are hashed):")
        for i, mac_hash in enumerate(macs, 1):
            print(f"  {i}. {mac_hash[:16]}...{mac_hash[-16:]}")


def authorize_mac(auth):
    """Authorize a new MAC address."""
    print("\n" + "="*60)
    print("  Authorize New MAC Address")
    print("="*60)
    print("\nEnter MAC address in format XX:XX:XX:XX:XX:XX")
    print("(or 'current' to authorize current device)")
    
    mac_input = input("\nMAC Address: ").strip()
    
    if mac_input.lower() == 'current':
        if auth.authorize_current_mac():
            print("\n✓ Current device authorized successfully!")
        else:
            print("\n✗ Failed to authorize current device.")
    else:
        # Validate MAC address format
        import re
        if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac_input):
            print("\n✗ Invalid MAC address format. Use XX:XX:XX:XX:XX:XX")
            return
        
        if auth.authorize_mac(mac_input):
            print(f"\n✓ MAC address {mac_input} authorized successfully!")
        else:
            print(f"\n✗ Failed to authorize MAC address {mac_input}")


def revoke_mac(auth):
    """Revoke a MAC address."""
    print("\n" + "="*60)
    print("  Revoke MAC Address")
    print("="*60)
    print("\nEnter MAC address to revoke (format XX:XX:XX:XX:XX:XX)")
    
    mac_input = input("\nMAC Address: ").strip()
    
    # Validate MAC address format
    import re
    if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac_input):
        print("\n✗ Invalid MAC address format. Use XX:XX:XX:XX:XX:XX")
        return
    
    confirm = input(f"\nAre you sure you want to revoke {mac_input}? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        if auth.revoke_mac(mac_input):
            print(f"\n✓ MAC address {mac_input} revoked successfully!")
        else:
            print(f"\n✗ MAC address {mac_input} not found in authorized list.")
    else:
        print("\n  Revocation cancelled.")


def show_auth_status(auth):
    """Show authentication status."""
    print("\n" + "="*60)
    print("  Authentication Status")
    print("="*60)
    
    auth_info = auth.get_auth_info()
    is_auth, message = auth.is_authorized()
    
    print(f"\nCurrent Device MAC: {auth_info['current_mac']}")
    print(f"Authentication Mode: {auth_info['mode'].upper()}")
    print(f"Authorized Devices: {auth_info['authorized_count']}")
    print(f"Status: {'✓ AUTHORIZED' if is_auth else '✗ NOT AUTHORIZED'}")
    print(f"Message: {message}")


def change_mode(auth):
    """Change authentication mode."""
    print("\n" + "="*60)
    print("  Change Authentication Mode")
    print("="*60)
    print("\n1. Whitelist Mode (Multiple authorized devices)")
    print("2. Binding Mode (One device only)")
    print("3. Disabled (No MAC authentication)")
    
    choice = input("\nSelect mode (1-3): ").strip()
    
    mode_map = {
        '1': 'whitelist',
        '2': 'binding',
        '3': 'disabled'
    }
    
    if choice in mode_map:
        mode = mode_map[choice]
        auth.set_mode(mode)
        print(f"\n✓ Authentication mode changed to: {mode.upper()}")
        
        if mode == 'binding' and not auth.config.get('bound_mac'):
            print("\nNote: License will be bound to the first device that runs the application.")
    else:
        print("\n✗ Invalid choice.")


def main():
    """Main function."""
    auth = MACAuthenticator()
    
    while True:
        display_menu()
        choice = input("Select option (1-9): ").strip()
        
        if choice == '1':
            show_current_mac(auth)
        elif choice == '2':
            show_authorized_macs(auth)
        elif choice == '3':
            authorize_mac(auth)
        elif choice == '4':
            revoke_mac(auth)
        elif choice == '5':
            show_auth_status(auth)
        elif choice == '6':
            change_mode(auth)
        elif choice == '7':
            auth.set_mode('disabled')
            print("\n✓ MAC authentication disabled.")
        elif choice == '8':
            auth.set_mode('whitelist')
            print("\n✓ MAC authentication enabled (Whitelist mode).")
        elif choice == '9':
            print("\n  Exiting...\n")
            sys.exit(0)
        else:
            print("\n✗ Invalid option. Please select 1-9.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
