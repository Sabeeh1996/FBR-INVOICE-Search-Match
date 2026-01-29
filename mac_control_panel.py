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
        print("\n1. View All Devices (Active & Revoked)")
        print("2. Authorize Device (Set status: active)")
        print("3. Revoke Device Access (Set status: revoked)")
        print("4. View Notifications (New Devices)")
        print("5. Remove Device Completely (Delete from list)")
        print("6. Exit")
        print("\n" + "="*60)
    
    def view_devices(self):
        """Show all devices with their status"""
        data = self.load_whitelist()
        devices = data.get('devices', [])
        
        print("\n" + "="*60)
        print(f"ALL DEVICES: {len(devices)}")
        print("="*60)
        
        if not devices:
            print("\n⚠ No devices yet")
            print("\nDevices will auto-authorize on first run.")
            print("Check 'first_run_notifications' folder for new device details.")
        else:
            active = [d for d in devices if d.get('status') == 'active']
            revoked = [d for d in devices if d.get('status') == 'revoked']
            
            print(f"\n✅ Active: {len(active)} | ❌ Revoked: {len(revoked)}")
            print("\n" + "-"*60)
            
            for i, device in enumerate(devices, 1):
                mac_address = device.get('mac_address', 'N/A')
                mac_hash = device.get('mac_hash', 'unknown')
                status = device.get('status', 'unknown')
                status_icon = "✅" if status == 'active' else "❌" if status == 'revoked' else "⚠️"
                notes = device.get('notes', '')
                auth_date = device.get('authorized_date', 'N/A')[:10]
                
                print(f"{i}. {status_icon} [{status.upper()}] {mac_address}")
                print(f"   Hash: {mac_hash[:16]}...{mac_hash[-8:]}")
                print(f"   Authorized: {auth_date}")
                if notes:
                    print(f"   Notes: {notes}")
                print()
        
        print("="*60)
    
    def add_device(self):
        """Authorize a device (set status to active)"""
        print("\n" + "="*60)
        print("AUTHORIZE DEVICE")
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
        devices = data.get('devices', [])
        
        # Check if device already exists
        existing = next((d for d in devices if d.get('mac_hash') == mac_hash), None)
        
        if existing:
            if existing.get('status') == 'active':
                print(f"\n⚠ Device already authorized (status: active)")
            else:
                existing['status'] = 'active'
                existing['last_updated'] = datetime.now().isoformat()
                self.save_whitelist(data)
                print(f"\n✓ Device status changed to: ACTIVE")
                print(f"   Device is now authorized")
        else:
            # Add new device - need to ask for MAC address
            mac_address = input("\nEnter actual MAC address (e.g., AA:BB:CC:DD:EE:FF): ").strip().upper()
            
            if not mac_address or len(mac_address) < 17:
                print("\n✗ Invalid MAC address format")
                return
            
            devices.append({
                'mac_address': mac_address,
                'mac_hash': mac_hash,
                'status': 'active',
                'authorized_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'notes': 'Manually authorized by admin'
            })
            data['devices'] = devices
            self.save_whitelist(data)
            print(f"\n✓ Device authorized successfully!")
        
        print(f"Total devices: {len(devices)}")
    
    def remove_device(self):
        """Revoke device access (set status to revoked)"""
        data = self.load_whitelist()
        devices = data.get('devices', [])
        
        if not devices:
            print("\n⚠ No devices to revoke")
            return
        
        print("\n" + "="*60)
        print("REVOKE DEVICE ACCESS")
        print("="*60)
        
        for i, device in enumerate(devices, 1):
            mac_address = device.get('mac_address', 'unknown')
            status = device.get('status', 'unknown')
            status_icon = "✅" if status == 'active' else "❌"
            print(f"{i}. {status_icon} [{status.upper()}] {mac_address}")
        
        try:
            choice = input("\nEnter device number to REVOKE (or 0 to cancel): ").strip()
            choice = int(choice)
            
            if choice == 0:
                print("\nCancelled.")
                return
            
            if 1 <= choice <= len(devices):
                device = devices[choice - 1]
                mac_address = device.get('mac_address', '')
                
                if device.get('status') == 'revoked':
                    print(f"\n⚠ Device already revoked")
                else:
                    device['status'] = 'revoked'
                    device['last_updated'] = datetime.now().isoformat()
                    if 'notes' in device:
                        device['notes'] += ' | Revoked by admin'
                    else:
                        device['notes'] = 'Revoked by admin'
                    
                    self.save_whitelist(data)
                    
                    print(f"\n✓ Device access REVOKED: {mac_address}")
                    print(f"   Status changed to: REVOKED")
                    print(f"   Device will be blocked on next app startup")
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
                    mac_address = notif.get('mac_address', 'unknown')
                    computer = notif.get('computer_name', 'unknown')
                    user = notif.get('username', 'unknown')
                    
                    print(f"\n📱 {computer} ({user})")
                    print(f"   MAC: {mac_address}")
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
        """Delete a device completely from the list"""
        data = self.load_whitelist()
        devices = data.get('devices', [])
        
        if not devices:
            print("\n⚠ No devices to delete")
            return
        
        print("\n" + "="*60)
        print("⚠️  DELETE DEVICE COMPLETELY")
        print("="*60)
        print("\nThis will PERMANENTLY DELETE the device from the list.")
        print("To temporarily block access, use option 3 (Revoke) instead.\n")
        
        for i, device in enumerate(devices, 1):
            mac_address = device.get('mac_address', 'unknown')
            status = device.get('status', 'unknown')
            print(f"{i}. [{status.upper()}] {mac_address}")
        
        try:
            choice = input("\nEnter device number to DELETE (or 0 to cancel): ").strip()
            choice = int(choice)
            
            if choice == 0:
                print("\nCancelled.")
                return
            
            if 1 <= choice <= len(devices):
                confirm = input("\nType 'DELETE' to confirm: ").strip()
                
                if confirm == 'DELETE':
                    device = devices.pop(choice - 1)
                    data['devices'] = devices
                    self.save_whitelist(data)
                    
                    mac_address = device.get('mac_address', '')
                    print(f"\n✓ Device deleted: {mac_address}")
                    print(f"Remaining devices: {len(devices)}")
                else:
                    print("\nCancelled (confirmation failed)")
            else:
                print("\n✗ Invalid choice")
        
        except ValueError:
            print("\n✗ Invalid input")
    
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
