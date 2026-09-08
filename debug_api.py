import requests
import json
import os

# Load GitHub token
config_path = os.path.join(os.path.dirname(__file__), 'github_update_config.json')
with open(config_path, 'r') as f:
    config = json.load(f)
    github_token = config.get('github_token')

headers = {'Authorization': f'token {github_token}'}

api_url = "https://api.github.com/repos/Sabeeh1996/FBR-INVOICE-Search-Match/releases/latest"

print(f"Calling: {api_url}")
print(f"With authentication: {github_token[:20]}...")
response = requests.get(api_url, headers=headers)

print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {response.headers.get('X-RateLimit-Remaining')} API calls remaining")

if response.status_code == 200:
    data = response.json()
    print(f"\n✓ Release Found!")
    print(f"  Tag: {data.get('tag_name')}")
    print(f"  Name: {data.get('name')}")
    print(f"  Draft: {data.get('draft')}")
    print(f"  Prerelease: {data.get('prerelease')}")
    print(f"  Published: {data.get('published_at')}")
    print(f"  Assets: {len(data.get('assets', []))}")
elif response.status_code == 404:
    print("\n✗ No releases found (404)")
    print("\nTrying all releases endpoint...")
    all_releases_url = "https://api.github.com/repos/Sabeeh1996/FBR-INVOICE-Search-Match/releases"
    all_response = requests.get(all_releases_url, headers=headers)
    if all_response.status_code == 200:
        releases = all_response.json()
        print(f"\nFound {len(releases)} total releases:")
        for r in releases[:5]:  # Show first 5
            print(f"  - Tag: {r.get('tag_name')} | Name: {r.get('name')} | Draft: {r.get('draft')} | Prerelease: {r.get('prerelease')}")
    else:
        print(f"All releases also returned: {all_response.status_code}")
else:
    print(f"\n✗ Error: {response.status_code}")
    print(response.text[:500])
