"""
Auto-sync GitHub Whitelist
Automatically commits and pushes mac_whitelist.json changes to GitHub
"""

import subprocess
import sys
import os
# GitHub Personal Access Token for authentication
GITHUB_TOKEN = "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"

def check_git_changes():
    """Check if mac_whitelist.json has changes"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain', 'mac_whitelist.json'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return bool(result.stdout.strip())
    except Exception as e:
        print(f"Error checking git status: {e}")
        return False


def sync_whitelist():
    """Sync mac_whitelist.json to GitHub"""
    try:
        if not check_git_changes():
            print("✓ No changes to sync")
            return True
        
        print("📤 Syncing mac_whitelist.json to GitHub...")
        
        # Add file
        subprocess.run(['git', 'add', 'mac_whitelist.json'], check=True)
        print("  ✓ File staged")
        
        # Commit
        subprocess.run(
            ['git', 'commit', '-m', 'Auto-authorize new device'],
            check=True
        )
        print("  ✓ Changes committed")
        
        # Configure git credential helper for this session
        repo_url = f"https://{GITHUB_TOKEN}@github.com/Sabeeh1996/FBR-INVOICE-Search-Match.git"
        
        # Push with authentication
        subprocess.run(['git', 'push', repo_url, 'develop'], check=True)
        print("  ✓ Pushed to GitHub")
        
        print("\n✅ Whitelist synced successfully!")
        print("   Changes are now live for all devices\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Sync failed: {e}")
        print("\nManual sync command:")
        print("  git add mac_whitelist.json")
        print("  git commit -m \"Auto-authorize device\"")
        print("  git push origin develop")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    sync_whitelist()
