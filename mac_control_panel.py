"""
Simple MAC Address Control Panel
Easy-to-use interface for authorizing/revoking devices
"""

import json
import os
import sys
from datetime import datetime


class MACControlPanel:
    """Simple control panel for managing MAC addresses"""
    
    def __init__(self, whitelist_file="mac_whitelist.json"):
        self.whitelist_file = whitelist_file
        
    def load_whitelist(self):
        """Load current whitelist"""
        if not os.path.exists(self.whitelist_file):
            return {
                "mode": "github_whitelist",
                "authorized_macs": [],
                "last_updated": datetime.now().isoformat(),
                "updated_by": "admin"
            }
        
        with open(self.whitelist_file, 'r') as f:
            return json.load(f)
    
    def save_whitelist(self, data):
        """Save whitelist"""
        data['last_updated'] = datetime.now().isoformat()
        with open(self.whitelist_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✓ Whitelist saved to {self.whitelist_file}")
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("MAC ADDRESS CONTROL PANEL")
        print("="*60)
        print("\n1. View Authorized Devices")
        print("2. Add Device (Authorize)")
        print("3. Remove Device (Revoke Access)")
        print("4. View Notifications (New Devices)")
        print("5. Clear All Devices")
        print("6. Exit")
        print("\n" + "="*60)
    
    def view_devices(self):
        """Show all authorized devices"""
        data = self.load_whitelist()
        macs = data.get('authorized_macs', [])
        
        print("\n" + "="*60)
        print(f"AUTHORIZED DEVICES: {len(macs)}")
        print("="*60)
        
        if not macs:
            print("\n⚠ No devices authorized yet")
            print("\nDevices will auto-authorize on first run.")
            print("Check 'first_run_notifications' folder for new device details.")
        else:
            for i, mac_hash in enumerate(macs, 1):
                print(f"{i}. {mac_hash[:16]}...{mac_hash[-8:]}")
        
        print("="*60)
    
    def add_device(self):
        """Add a device to whitelist"""
        print("\n" + "="*60)
        print("ADD DEVICE")
        print("="*60)
        
        # First show notifications to help user find MAC hash
        self.show_notifications_brief()
        
        print("\nEnter the MAC address hash to authorize:")
        print("(Copy from notification above or full hash)")
        mac_hash = input("\nMAC Hash: ").strip()
        
        if not mac_hash:
            print("\n✗ Empty input. Cancelled.")
            return
        
        if len(mac_hash) < 16:
            print("\n✗ Invalid MAC hash (too short)")
            return
        
        data = self.load_whitelist()
        
        if mac_hash in data['authorized_macs']:
            print(f"\n⚠ Device already authorized")
            return
        
        data['authorized_macs'].append(mac_hash)
        self.save_whitelist(data)
        
        print(f"\n✓ Device authorized successfully!")
        print(f"Total authorized devices: {len(data['authorized_macs'])}")
    
    def remove_device(self):
        """Remove a device from whitelist"""
        data = self.load_whitelist()
        macs = data.get('authorized_macs', [])
        
        if not macs:
            print("\n⚠ No devices to remove")
            return
        
        print("\n" + "="*60)
        print("REMOVE DEVICE")
        print("="*60)
        
        for i, mac_hash in enumerate(macs, 1):
            print(f"{i}. {mac_hash[:16]}...{mac_hash[-8:]}")
        
        try:
            choice = input("\nEnter device number to remove (or 0 to cancel): ").strip()
            choice = int(choice)
            
            if choice == 0:
                print("\nCancelled.")
                return
            
            if 1 <= choice <= len(macs):
                removed_mac = macs.pop(choice - 1)
                data['authorized_macs'] = macs
                self.save_whitelist(data)
                
                print(f"\n✓ Device removed: {removed_mac[:16]}...{removed_mac[-8:]}")
                print(f"Remaining devices: {len(macs)}")
            else:
                print("\n✗ Invalid choice")
        
        except ValueError:
            print("\n✗ Invalid input")
    
    def show_notifications_brief(self):
        """Show brief list of notifications"""
        notif_dir = "first_run_notifications"
        
        if not os.path.exists(notif_dir):
            return
        
        files = [f for f in os.listdir(notif_dir) if f.endswith('.json')]
        
        if not files:
            return
        
        print("\nRecent Device Notifications:")
        print("-" * 60)
        
        # Show last 5 notifications
        for filename in sorted(files, reverse=True)[:5]:
            filepath = os.path.join(notif_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    notif = json.load(f)
                    mac_hash = notif.get('mac_address_hash', 'unknown')
                    computer = notif.get('computer_name', 'unknown')
                    user = notif.get('username', 'unknown')
                    
                    print(f"\n📱 {computer} ({user})")
                    print(f"   Hash: {mac_hash}")
            except:
                pass
        
        print("-" * 60)
    
    def view_notifications(self):
        """View all first-run notifications"""
        notif_dir = "first_run_notifications"
        
        print("\n" + "="*60)
        print("FIRST-RUN NOTIFICATIONS")
        print("="*60)
        
        if not os.path.exists(notif_dir):
            print("\n⚠ No notifications yet")
            return
        
        files = [f for f in os.listdir(notif_dir) if f.endswith('.json')]
        
        if not files:
            print("\n⚠ No notifications yet")
            return
        
        print(f"\nTotal notifications: {len(files)}\n")
        
        for i, filename in enumerate(sorted(files, reverse=True), 1):
            filepath = os.path.join(notif_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    notif = json.load(f)
                
                print(f"\n[{i}] Notification from: {filename}")
                print("-" * 60)
                print(f"Computer Name : {notif.get('computer_name', 'N/A')}")
                print(f"Username      : {notif.get('username', 'N/A')}")
                print(f"MAC Address   : {notif.get('mac_address', 'N/A')}")
                print(f"MAC Hash      : {notif.get('mac_address_hash', 'N/A')}")
                print(f"OS            : {notif.get('os_info', 'N/A')}")
                print(f"Timestamp     : {notif.get('timestamp', 'N/A')}")
                
            except Exception as e:
                print(f"\n✗ Error reading {filename}: {str(e)}")
        
        print("\n" + "="*60)
    
    def clear_all(self):
        """Clear all authorized devices"""
        print("\n" + "="*60)
        print("⚠️  CLEAR ALL DEVICES")
        print("="*60)
        
        data = self.load_whitelist()
        count = len(data.get('authorized_macs', []))
        
        if count == 0:
            print("\n⚠ No devices to clear")
            return
        
        print(f"\nThis will remove ALL {count} authorized device(s).")
        confirm = input("\nType 'YES' to confirm: ").strip()
        
        if confirm == 'YES':
            data['authorized_macs'] = []
            self.save_whitelist(data)
            print(f"\n✓ All devices cleared")
        else:
            print("\nCancelled.")
    
    def run(self):
        """Run the control panel"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\nChoose an option (1-6): ").strip()
                
                if choice == '1':
                    self.view_devices()
                elif choice == '2':
                    self.add_device()
                elif choice == '3':
                    self.remove_device()
                elif choice == '4':
                    self.view_notifications()
                elif choice == '5':
                    self.clear_all()
                elif choice == '6':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("\n✗ Invalid choice")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n✗ Error: {str(e)}")
                input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("FBR Invoice Checker - MAC Control Panel")
    print("="*60)
    
    panel = MACControlPanel()
    panel.run()


if __name__ == "__main__":
    main()
