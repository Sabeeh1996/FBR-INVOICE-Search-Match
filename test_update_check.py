from update_checker import UpdateChecker
import json
import os

# Load GitHub token from config
config_path = os.path.join(os.path.dirname(__file__), 'github_update_config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
        github_token = config.get('github_token')
        repo_owner = config.get('repo_owner', 'Sabeeh1996')
        repo_name = config.get('repo_name', 'FBR-INVOICE-Search-Match')
except Exception as e:
    print(f"⚠️  Warning: Could not load github_update_config.json: {e}")
    print("   Using defaults without authentication (won't work for private repos)")
    github_token = None
    repo_owner = 'Sabeeh1996'
    repo_name = 'FBR-INVOICE-Search-Match'

# Initialize checker with token for private repo access
checker = UpdateChecker(repo_owner, repo_name, github_token=github_token)
release = checker.get_latest_release()

if release:
    print(f"✓ Latest version detected: {release.get('tag_name')}")
    print(f"  Name: {release.get('name')}")
    print(f"  Published: {release.get('published_at')}")
    
    # Check for assets
    assets = release.get('assets', [])
    if assets:
        print(f"  Assets: {len(assets)} file(s)")
        for asset in assets:
            print(f"    - {asset.get('name')} ({asset.get('size')} bytes)")
    else:
        print("  No assets attached to this release")
else:
    print("✗ No release found or API error")
    print("   Make sure:")
    print("   1. The repository has at least one release")
    print("   2. The release is not marked as 'draft'")
    print("   3. For private repos: github_update_config.json has valid token")
